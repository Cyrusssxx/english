# -*- coding: utf-8 -*-
"""生成熟词僻义表格数据 pwa/data/wordnotes.json（按词频降序 · 原句取短句）

数据来源（全部为已有资料，无 AI 生成）：
  1) 单词 + 僻义：pwa/data/deck_tc_senses.json（唐迟·熟词僻义，OCR + 人工核对）
  2) 熟义：tools/ecdict.csv 的 translation 首义（取前 2 个义项）
  3) 原句：在题库（阅读/完形/新题型/翻译 全部题型）里找【含该词的短句】，优先长度 ≤ 110 字符；
     没有短句时，截取以该词为中心的片段。出处标注「年份 英语一/二 · 题型」。

词频 freq = 该词（含常见词形变化）在题库全部真题句中的出现次数，用于排序（最常出现的排前面）。

运行：python -X utf8 tools/build_wordnotes.py
"""
import csv
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')

SKIP_FILES = ['deck', 'index', 'chain', 'mindmap', 'freq', 'hard', 'phrases', 'dict', 'tc_', 'wordnotes']

TYPE_CN = {
    'text1': '阅读', 'text2': '阅读', 'text3': '阅读', 'text4': '阅读',
    'cloze': '完形', 'newtype': '新题型', 'translation': '翻译',
    'writing_a': '写作', 'writing_b': '写作',
}
SHORT_LIMIT = 130      # 短句阈值（字符）
SNIP_LIMIT = 110       # 截取片段目标长度


def load_sentences():
    """题库全部真题句（en + cn + 年份 + 英一/英二 + 题型）"""
    out = []
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.json'))) + \
            sorted(glob.glob(os.path.join(DATA_DIR, 'en1', '*.json')))
    for p in files:
        base = os.path.basename(p)
        if any(k in base for k in SKIP_FILES):
            continue
        try:
            dd = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(dd, dict):
            continue
        is_en1 = 'en1' in p.replace('\\', '/')
        m = re.search(r'(\d{4})', base)
        year = m.group(1) if m else ''
        for a in dd.get('articles', []):
            if not isinstance(a, dict):
                continue
            tcn = TYPE_CN.get(a.get('type', ''), a.get('type', ''))
            for s in a.get('sentences', []) or []:
                en = s.get('en') or ''
                if not en:
                    continue
                out.append({
                    'en': re.sub(r'\s+', ' ', en).strip(),
                    'cn': re.sub(r'\s+', ' ', s.get('cn') or '').strip(),
                    'year': year,
                    'book': '英语一' if is_en1 else '英语二',
                    'type': tcn,
                })
    return out


def load_common(path):
    trans = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if w and w not in trans:
                trans[w] = (row.get('translation') or '').strip()
    return trans


def clean_common(raw):
    """'n. 打击, 打, 冲撞, 讽刺\\nv. ...' → 'n. 打击；打'"""
    if not raw:
        return ''
    first = raw.split('\\n')[0].strip()
    m = re.match(r'^([a-z]+\.)\s*(.*)$', first, re.I)
    pos, body = (m.group(1), m.group(2)) if m else ('', first)
    items = [x.strip() for x in re.split(r'[,，;；]', body) if x.strip()][:2]
    return (pos + ' ' + '；'.join(items)).strip()


def clean_uncommon(raw):
    if not raw:
        return ''
    t = re.sub(r'\s+', '', raw)
    t = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫]', '；', t)
    t = t.replace('..', '.')
    return t.strip('；,，')


def variants(w):
    """精确词形变体集合（词频统计用，避免 see 误配 seem）"""
    vs = {w}
    if w.endswith('e'):
        vs |= {w + 'd', w[:-1] + 'ing'}
    else:
        vs |= {w + 'ed', w + 'ing'}
    vs |= {w + 's', w + 'es', w + 'ness', w + 'ment', w + 'tion'}
    if w.endswith('y'):
        vs |= {w[:-1] + 'ies', w[:-1] + 'ied'}
    return vs


def word_re(w):
    """词族匹配（例句候选用）：词根（去尾 e）+ 至多 6 字母后缀"""
    stem = w[:-1] if w.endswith('e') else w
    return re.compile(r'\b' + re.escape(stem) + r"[a-z]{0,6}\b", re.I)


def freq_re(w):
    """词频统计正则：仅精确变体"""
    return re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in sorted(variants(w), key=len, reverse=True)) + r')\b', re.I)


def clean_cn(cn):
    """清洗译文：截掉混入的讲义笔记（“记：/解析/技巧总结/精准定位”等分析文字）"""
    if not cn:
        return ''
    cn = re.sub(r'\s+', ' ', cn).strip()
    for sig in ['记：', '【', '［精准定位', '技巧总结', '精准定位', '定位到', '解析', '本题']:
        i = cn.find(sig)
        if i >= 0:
            cn = cn[:i]
    cn = cn.strip(' ，,；;')
    return cn[:180]


def snippet(en, w, limit=SNIP_LIMIT):
    """原句过长时，截取以该词为中心的片段（在标点边界断开）"""
    m = word_re(w).search(en)
    if not m:
        return en if len(en) <= limit else en[:limit].strip() + ' …'

    start, end = m.start(), m.end()
    budget = max(limit - (end - start), 24)
    left, right = budget // 2, budget - budget // 2
    a = max(0, start - left)
    b = min(len(en), end + right)
    # 对齐单词边界，避免切断单词
    if a > 0 and en[a - 1].isalpha() and en[a].isalpha():
        sp = en.rfind(' ', 0, a)
        if sp > 0:
            a = sp + 1
    if b < len(en) and en[b - 1].isalpha() and en[b].isalpha():
        sp = en.find(' ', b)
        if sp > 0:
            b = sp
    frag = en[a:b].strip()
    if a > 0:
        cut = max(frag.rfind(', '), frag.rfind('; '), frag.rfind(': '))
        if 0 < cut < 40:
            frag = frag[cut + 2:]
        frag = '… ' + frag
    if b < len(en):
        cands = [x for x in [frag.find(', ', 10), frag.find('; ', 10)] if x > 0]
        cut = min(cands) if cands else len(frag)
        frag = frag[:cut].rstrip(' ,;') + ' …'
    return frag.strip()


def main():
    deck = json.load(open(os.path.join(DATA_DIR, 'deck_tc_senses.json'), encoding='utf-8'))
    sents = load_sentences()
    common_map = load_common(os.path.join(ROOT, 'tools', 'ecdict.csv'))
    print(f'题库句 {len(sents)} 条（阅读/完形/新题型/翻译），熟词僻义词条 {len(deck["words"])}')

    rows = []
    seen = set()
    stat = {'short': 0, 'snip': 0, 'fallback': 0, 'none': 0}
    for it in deck['words']:
        w = (it.get('word') or '').strip()
        if not w:
            continue
        wl = w.lower()
        if wl in seen:
            continue
        seen.add(wl)
        rx = word_re(wl)
        frx = freq_re(wl)
        freq = sum(len(frx.findall(s['en'])) for s in sents)

        cands = [s for s in sents if rx.search(s['en'])]
        # 指纹候选：与讲义例句实词有交集的句子（更可能用的是偏僻义），优先从中取短句
        ex_raw = re.sub(r'\s+', ' ', it.get('example_en') or '').strip()
        fp_words = [x for x in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", ex_raw.lower()) if x != wl]
        fingered = [s for s in cands if any(t in s['en'].lower() for t in fp_words)] if fp_words else []

        src = en = cn = ''
        picked = None
        for pool, tag in ((fingered, ''), (cands, '')):
            if not pool:
                continue
            shorts = [s for s in pool if len(s['en']) <= SHORT_LIMIT]
            if shorts:
                picked = (min(shorts, key=lambda s: (not s['cn'], len(s['en']))), False, tag)
                break
        if picked:
            pick, is_snip, tag = picked
            en, cn = pick['en'], clean_cn(pick['cn'])
            src = (f"{pick['year']} {pick['book']} · {pick['type']}" if pick['year'] else pick['type']) + tag
            stat['short'] += 1
        elif cands:
            # 指纹池与全池都没有短句 → 优先从指纹池截取，其次全池最短句截取
            pool2 = fingered or cands
            pick = min(pool2, key=lambda s: len(s['en']))
            en = snippet(pick['en'], wl)
            src = (f"{pick['year']} {pick['book']} · {pick['type']}（截取）" if pick['year'] else f"{pick['type']}（截取）")
            stat['snip'] += 1
        else:
            if ex_raw:
                en = snippet(ex_raw, wl) if len(ex_raw) > SHORT_LIMIT else ex_raw
                cn = clean_cn(it.get('example_cn') or '')
                src = '讲义例证'
                stat['fallback'] += 1
            else:
                stat['none'] += 1

        rows.append({
            'w': w,
            'freq': freq,
            'common': clean_common(common_map.get(wl, '')),
            'uncommon': clean_uncommon(it.get('meaning') or ''),
            'en': en, 'cn': cn, 'src': src,
        })

    rows.sort(key=lambda r: (-r['freq'], r['w'].lower()))
    out = {'name': '熟词僻义', 'count': len(rows), 'rows': rows}
    dst = os.path.join(DATA_DIR, 'wordnotes.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'写入 {dst}｜{len(rows)} 条，按词频降序')
    print('短句', stat['short'], '｜截取片段', stat['snip'], '｜讲义例证', stat['fallback'], '｜无例句', stat['none'])
    print('\nTop 10（词频降序）：')
    for r in rows[:10]:
        print(f"  {r['freq']:>3}  {r['w']:<12} {r['uncommon'][:12]:<14} {r['en'][:72]}")
    print('\n样例（用户点名的三条）：')
    for r in rows:
        if r['w'] in ('handsome', 'narrow', 'submit'):
            print(f"  {r['w']}: {r['en']}\n      译文: {r['cn'][:60]}  [{r['src']}]")


if __name__ == '__main__':
    main()
