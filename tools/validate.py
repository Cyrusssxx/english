# -*- coding: utf-8 -*-
"""validate.py — 英语二精翻题库校验脚本
用法：python -X utf8 tools\\validate.py            校验 pwa/data 下全部年份 JSON
      python -X utf8 tools\\validate.py 2022       只校验指定年份

校验项：
- 顶层必填字段与年份一致性
- 文章 id/type 合法、句 id 唯一且前缀正确
- 词汇标注 w 必须能在句子 en 中全词匹配到（词组优先渲染的前提）
- 题目 answer 在 options（或文章 pool）内，related_sentences 引用存在
- 完形：正文 [n] 占位符与题号一一对应
- index.json 与年份文件的文章清单/句数/题数一致
"""
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DATA_DIR = TOOLS.parent / 'pwa' / 'data'

VALID_TYPES = {'text1', 'text2', 'text3', 'text4', 'cloze', 'newtype', 'translation', 'writing_a', 'writing_b'}

# 非逐句模块（翻译/作文）：不校验逐句结构与题目，改用模块专属校验
MODULE_TYPES = {'translation', 'writing_a', 'writing_b'}

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def find_word(text, w):
    """与前端 article.js findWord 同逻辑：全词匹配（前后均非字母）"""
    start = 0
    while True:
        pos = text.find(w, start)
        if pos < 0:
            return -1
        before = text[pos - 1] if pos > 0 else ''
        after = text[pos + len(w)] if pos + len(w) < len(text) else ''
        if not before.isalpha() and not after.isalpha():
            return pos
        start = pos + 1


def check_article(year, art):
    aid = art.get('id', '?')
    prefix = f'[{year}/{aid}]'

    if not re.match(rf'^{year}_[a-z0-9]+$', str(aid)):
        err(f'{prefix} 文章 id 不符合 {year}_xxx 规则')
    if art.get('type') not in VALID_TYPES:
        err(f'{prefix} type 非法: {art.get("type")}')

    # ---------- 翻译/作文等模块型文章：只校验展示字段 ----------
    if art.get('type') in MODULE_TYPES:
        if art.get('type') == 'translation':
            if not art.get('ref_cn'):
                err(f'{prefix} 翻译缺参考译文 ref_cn')
        if art.get('type') in ('writing_a', 'writing_b'):
            for field in ('directions', 'sample_en', 'sample_cn'):
                if not art.get(field):
                    err(f'{prefix} 作文缺字段 {field}')
        return {
            'id': aid, 'type': art.get('type'), 'title': art.get('title'),
            'topic': art.get('topic'),
            'sentence_count': len(art.get('sentences', [])),
            'question_count': len(art.get('questions', [])),
        }

    for field in ('title', 'topic', 'sentences', 'questions'):
        if field not in art:
            err(f'{prefix} 缺少字段 {field}')

    # ---------- 句子 ----------
    sent_ids = set()
    all_blanks = []
    for s in art.get('sentences', []):
        sid = s.get('id', '?')
        sp = f'{prefix} 句 {sid}'
        if sid in sent_ids:
            err(f'{sp} 句 id 重复')
        sent_ids.add(sid)
        if not str(sid).startswith(str(aid)):
            err(f'{sp} 句 id 未以文章 id 为前缀')
        if not s.get('en'):
            err(f'{sp} 缺少 en')
        if not s.get('cn'):
            err(f'{sp} 缺少 cn')
        # 词汇标注必须能在原句中全词匹配（词组整体标注）
        for w in s.get('words', []):
            if not w.get('w') or not w.get('meaning'):
                err(f'{sp} 词条缺少 w/meaning: {w}')
                continue
            if find_word(s.get('en', ''), w['w']) < 0:
                err(f'{sp} 词 "{w["w"]}" 无法在原句中全词匹配')
        all_blanks += [int(n) for n in re.findall(r'\[(\d+)\]', s.get('en', ''))]

    # ---------- 题目 ----------
    q_numbers = set()
    pool = art.get('pool')
    for q in art.get('questions', []):
        qid = q.get('id', '?')
        qp = f'{prefix} 题 {qid}'
        if not str(qid).startswith(str(aid)):
            err(f'{qp} 题 id 未以文章 id 为前缀')
        if q.get('number') in q_numbers:
            err(f'{qp} 题号重复: {q.get("number")}')
        q_numbers.add(q.get('number'))
        opts = q.get('options') or pool or {}
        if not opts:
            err(f'{qp} 无 options 且文章无 pool')
        if q.get('answer') not in opts:
            err(f'{qp} answer "{q.get("answer")}" 不在选项 {sorted(opts)} 内')
        if not q.get('explanation'):
            warn(f'{qp} 缺少 explanation')
        if q.get('options') and not q.get('options_cn'):
            warn(f'{qp} 缺少 options_cn（选项翻译）')
        for sid in q.get('related_sentences', []):
            if sid not in sent_ids:
                err(f'{qp} related_sentences 引用不存在的句 id: {sid}')

    # ---------- 完形：占位符与题号双射 ----------
    if art.get('type') == 'cloze':
        blanks = sorted(all_blanks)
        numbers = sorted(q_numbers)
        if blanks != numbers:
            err(f'{prefix} 完形占位符 {blanks} 与题号 {numbers} 不一致')
    elif all_blanks:
        warn(f'{prefix} 非完形文章正文出现 [n] 占位符: {all_blanks}')

    return {
        'id': aid, 'type': art.get('type'), 'title': art.get('title'),
        'topic': art.get('topic'),
        'sentence_count': len(art.get('sentences', [])),
        'question_count': len(art.get('questions', [])),
    }


def check_year_file(path):
    year = int(path.stem)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        err(f'[{path.name}] JSON 解析失败: {e}')
        return None
    if data.get('year') != year:
        err(f'[{path.name}] 顶层 year={data.get("year")} 与文件名不一致')
    if data.get('exam') != 'en2':
        warn(f'[{path.name}] exam 字段非 en2: {data.get("exam")}')
    if 'schema_version' not in data:
        warn(f'[{path.name}] 缺少 schema_version')
    summary = []
    for art in data.get('articles', []):
        summary.append(check_article(year, art))
    return {'year': year, 'articles': summary}


def check_index(year_summaries):
    """index.json 与年份文件一致性"""
    idx_path = DATA_DIR / 'index.json'
    if not idx_path.exists():
        err('[index.json] 文件不存在')
        return
    try:
        idx = json.loads(idx_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        err(f'[index.json] JSON 解析失败: {e}')
        return
    idx_years = {y['year']: y for y in idx.get('years', [])}
    for ys in year_summaries:
        y = ys['year']
        if y not in idx_years:
            err(f'[index.json] 缺少年份 {y}')
            continue
        idx_arts = {a['id']: a for a in idx_years[y].get('articles', [])}
        for a in ys['articles']:
            ia = idx_arts.get(a['id'])
            if not ia:
                err(f'[index.json] {y} 缺少文章 {a["id"]}')
                continue
            for k in ('type', 'sentence_count', 'question_count'):
                if ia.get(k) != a[k]:
                    err(f'[index.json] {a["id"]} 的 {k}={ia.get(k)} 与题库 {a[k]} 不一致')
        for aid in idx_arts:
            if aid not in {a['id'] for a in ys['articles']}:
                err(f'[index.json] {y} 的文章 {aid} 在题库文件中不存在')


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    files = sorted(DATA_DIR.glob('[0-9][0-9][0-9][0-9].json'))
    if only:
        files = [f for f in files if f.stem == only]
    if not files:
        print('未找到年份题库文件', DATA_DIR)
        sys.exit(1)

    summaries = []
    for f in files:
        s = check_year_file(f)
        if s:
            summaries.append(s)
            for a in s['articles']:
                print(f"  {a['id']}: {a['sentence_count']} 句 / {a['question_count']} 题")
    if not only:
        check_index(summaries)

    print()
    for w in warnings:
        print('WARN :', w)
    for e in errors:
        print('ERROR:', e)
    print(f'\n共 {len(files)} 个年份文件 · {len(errors)} 错误 · {len(warnings)} 警告')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
