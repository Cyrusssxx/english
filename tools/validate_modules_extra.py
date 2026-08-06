# -*- coding: utf-8 -*-
"""校验 tools/extracted/modules/{year}_extra.json 的结构完整性。
用法：python -X utf8 tools/validate_modules_extra.py
"""
import json
import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent / 'extracted' / 'modules'

errors = []
warnings = []


def err(m):
    errors.append(m)


def warn(m):
    warnings.append(m)


def check_year(year):
    path = MOD / f'{year}_extra.json'
    if not path.exists():
        err(f'{year}: 文件不存在')
        return
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        err(f'{year}: JSON 解析失败 {e}')
        return
    if data.get('year') != year:
        err(f'{year}: 顶层 year={data.get("year")} 与预期不符')
    arts = data.get('articles')
    if not isinstance(arts, list):
        err(f'{year}: articles 缺失或非列表')
        return

    expected = {f'{year}_cloze', f'{year}_newtype', f'{year}_translation', f'{year}_writinga', f'{year}_writingb'}
    got = {a['id'] for a in arts}
    if expected != got:
        err(f'{year}: 文章 id 集合 {got} != 预期 {expected}')

    for a in arts:
        aid = a.get('id', '?')
        atype = a.get('type', '?')
        p = f'{year}/{aid}'
        for f in ('title', 'topic', 'source'):
            if not a.get(f):
                err(f'{p}: 缺字段 {f}')
        # words 为空数组
        for s in a.get('sentences', []):
            if s.get('words') != []:
                err(f'{p}: 句 {s.get("id")} words 非空数组')

        if atype == 'cloze':
            sents = a['sentences']
            for i, s in enumerate(sents, 1):
                if s['id'] != f'{aid}_s{i:02d}':
                    err(f'{p}: 句 id 顺序不符 {s["id"]}')
                if not s.get('cn'):
                    err(f'{p}: 句 {s["id"]} 缺 cn')
            blanks = sorted(int(n) for s in sents for n in re.findall(r'\[(\d+)\]', s['en']))
            qs = sorted(q['number'] for q in a['questions'])
            if blanks != list(range(1, 21)):
                err(f'{p}: 完形占位符 {blanks}')
            if qs != list(range(1, 21)):
                err(f'{p}: 题号 {qs}')
            if len(a['questions']) != 20:
                err(f'{p}: 题目数 {len(a["questions"])}')
            for q in a['questions']:
                if q['answer'] not in q.get('options', {}):
                    err(f'{p}: q{q["number"]} answer 不在 options')
                if not q.get('explanation'):
                    warn(f'{p}: q{q["number"]} 缺 explanation')

        elif atype == 'newtype':
            pool = a.get('pool', {})
            pool_cn = a.get('pool_cn', {})
            if not pool or set(pool) != set('ABCDEFG'):
                err(f'{p}: pool 必须为 A-G')
            if set(pool_cn) != set('ABCDEFG'):
                err(f'{p}: pool_cn 必须为 A-G')
            for i, s in enumerate(a['sentences'], 1):
                if s['id'] != f'{aid}_s{i:02d}':
                    err(f'{p}: 句 id 顺序不符 {s["id"]}')
                if not s.get('cn'):
                    err(f'{p}: 句 {s["id"]} 缺 cn')
            if len(a['questions']) != 5:
                err(f'{p}: 题目数 {len(a["questions"])}')
            for q in a['questions']:
                if not (41 <= q['number'] <= 45):
                    err(f'{p}: 题号 {q["number"]}')
                if q.get('qtype') not in ('匹配', '小标题', '判断'):
                    err(f'{p}: q{q["number"]} qtype={q.get("qtype")}')
                if q['answer'] not in pool:
                    err(f'{p}: q{q["number"]} answer 不在 pool')
                if not q.get('explanation'):
                    warn(f'{p}: q{q["number"]} 缺 explanation')
                for sid in q.get('related_sentences', []):
                    if sid not in {s['id'] for s in a['sentences']}:
                        err(f'{p}: q{q["number"]} related_sentences 引用不存在 {sid}')

        elif atype == 'translation':
            if not a.get('ref_cn'):
                err(f'{p}: 缺 ref_cn')
            sents = a['sentences']
            for i, s in enumerate(sents, 1):
                if s['id'] != f'{aid}_s{i:02d}':
                    err(f'{p}: 句 id 顺序不符 {s["id"]}')
                if not s.get('cn'):
                    err(f'{p}: 句 {s["id"]} 缺 cn')
            if a.get('questions') != []:
                err(f'{p}: translation questions 应为空')

        elif atype in ('writing_a', 'writing_b'):
            for f in ('sample_en', 'sample_cn'):
                if not a.get(f):
                    err(f'{p}: 缺字段 {f}')
            if a.get('sentences', []) not in ([], None):
                err(f'{p}: 作文 sentences 应为空')
            if atype == 'writing_b' and not a.get('chart_img'):
                warn(f'{p}: 缺 chart_img')

    # 打印摘要
    print(f'===== {year} =====')
    for a in arts:
        print(f"  {a['id']} [{a['type']}] 句 {len(a.get('sentences', []))} / 题 {len(a.get('questions', []))} / pool {list(a.get('pool', {}).keys())}")


for y in (2013, 2014, 2015):
    check_year(y)

print()
for w in warnings:
    print('WARN :', w)
for e in errors:
    print('ERROR:', e)
print(f'\n共 {len(errors)} 错误 · {len(warnings)} 警告')
sys.exit(1 if errors else 0)
