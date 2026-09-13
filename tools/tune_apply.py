# -*- coding: utf-8 -*-
'''把 17 篇大作文套用示范的词数配平到 165-180（考研英语二要求 150+，实测 170 上下最稳）。
从 tools/expand_apply.py 读候选补句，穷举「加哪几句」的组合，挑最接近 172 词的方案写回数据。
用法：git show HEAD:pwa/data/writing_apply.json > pwa/data/writing_apply.json && python tools/tune_apply.py
'''
import io
import itertools
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('tools/expand_apply.py', encoding='utf-8').read()
ns = {}
exec(compile(src.split('def main()')[0], 'x', 'exec'), ns)
PATCH, wc, paras = ns['PATCH'], ns['wc'], ns['paras']
FP = 'pwa/data/writing_apply.json'
orig = json.load(open(FP, encoding='utf-8'))
# 2010 原稿 181 词，删两处冗余（不动关键句型）
PATCH['2010'] = {'trim': [
    ('rose from 0.7 billion to 1 billion over the same span.', 'rose from 0.7 billion to 1 billion.'),
    ('and given the enormous population, the number of potential customers was huge',
     'and the number of potential customers was huge'),
]}
ADDKEYS = [('p1_add', 0), ('p1_add2', 0), ('p2_add', 1), ('p2_add2', 1), ('p3_add', 2), ('p3_add2', 2)]
LO, HI, TARGET = 165, 180, 172


def build(y, chosen):
    p = PATCH.get(y, {})
    en = paras(orig[y]['apply_en'])
    cn = paras(orig[y]['apply_cn'])
    if p.get('p1_new'):
        en[0] = p['p1_new']
        cn[0] = p['p1_new_cn']
    for old, new in list(p.get('fixes', [])) + list(p.get('trim', [])):
        if not new:
            continue
        for i, x in enumerate(en):
            if old in x:
                en[i] = x.replace(old, new)
                break
    for k, idx in ADDKEYS:
        if k in chosen:
            en[idx] = en[idx].rstrip() + ' ' + p[k].strip()
            if p.get(k + '_cn'):
                cn[idx] = cn[idx].rstrip() + p[k + '_cn'].strip()
    return '\n\n'.join(en), '\n\n'.join(cn)


data = json.load(open(FP, encoding='utf-8'))
print('%-6s %-5s %-6s %s' % ('年份', '原', '最终', '选中'))
tots = {}
for y in sorted(orig):
    p = PATCH.get(y, {})
    cands = [k for k, _ in ADDKEYS if p.get(k)]
    best = None
    for r in range(len(cands) + 1):
        for comb in itertools.combinations(cands, r):
            idxs = [i for k, i in ADDKEYS if k in comb]
            if len(idxs) != len(set(idxs)):
                continue
            en, cn = build(y, set(comb))
            n = wc(en)
            if LO <= n <= HI and (best is None or abs(n - TARGET) < best[0]):
                best = (abs(n - TARGET), n, comb, en, cn)
    if best is None:
        en, cn = build(y, set())
        best = (999, wc(en), (), en, cn)
        print('%-6s %-5d %-6d ★ 无候选命中区间' % (y, wc(orig[y]['apply_en']), best[1]))
    else:
        print('%-6s %-5d %-6d %s' % (y, wc(orig[y]['apply_en']), best[1], ' + '.join(best[2]) or '（不加）'))
    data[y]['apply_en'], data[y]['apply_cn'] = best[3], best[4]
    tots[y] = best[1]
json.dump(data, open(FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('词数: 最低 %d | 最高 %d | 平均 %.1f' % (min(tots.values()), max(tots.values()), sum(tots.values()) / len(tots)))
print('区间外:', [y for y, n in tots.items() if not (LO <= n <= HI)] or '无')
print('中英段落数不一致:', [y for y in data
      if len(paras(data[y]['apply_en'])) != len(paras(data[y]['apply_cn']))] or '无')
