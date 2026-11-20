# -*- coding: utf-8 -*-
"""核对：句池里的句子有多少是「从图表范文原句提取」的，覆盖了哪些原句、漏了哪些。
只读，不改任何文件。用法：python tools/_audit_pool_vs_essay.py [--all]
"""
import json
import re
import sys
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PWA = ROOT / 'pwa'

TARGET = ['6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
if '--all' in sys.argv:
    TARGET = [str(i) for i in range(1, 27)]

STOP = set('a an the of to in on at for and or but as by with from that this it its is are was were be been '
           'has have had do does did not no more most such than then there their they them we our us you your '
           'can could may might must should would will also only very much many some any each other'.split())


PREFIX = [
    r'^this phenomenon can be attributed to a combination of factors\.?\s*',
    r'^primary among these is (?:that )?',
    r'^equally important,?\s*',
    r'^a further driver is (?:that )?',
    r'^nevertheless,?\s*',
    r'^however,?\s*',
    r'^during this period,?\s*',
    r'^by contrast,?\s*',
    r'^in contrast,?\s*',
    r'^together,?\s*',
    r'^the figures? (?:thus |therefore )?(?:suggest|show|reflect)(?: that)?\s*',
    r'^the findings therefore suggest(?: that)?\s*',
    r'^we should bear in mind that\s*',
]


def strip_prefix(t):
    s = str(t)
    for p in PREFIX:
        s2 = re.sub(p, '', s, flags=re.I)
        if s2 != s:
            return s2
    return s


def norm(t):
    t = re.sub(r'\{\{[^}]+\}\}', ' ', str(t).lower())
    t = re.sub(r'[^a-z0-9%.\s]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def toks(t):
    return [w for w in norm(t).split() if w not in STOP]


def sim(a, b):
    ta, tb = toks(a), toks(b)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    jac = len(sa & sb) / len(sa | sb)
    r = difflib.SequenceMatcher(None, ta, tb).ratio()
    return max(jac, r)


def load():
    yati = json.loads((PWA / 'data/yati.json').read_text(encoding='utf-8'))
    flat = {}
    for g in yati.get('groups', []):
        for it in g.get('items', []):
            flat[str(it['no'])] = it
    tp = json.loads((PWA / 'data/writing_templates.json').read_text(encoding='utf-8'))
    secs = {s['id']: s for s in tp['sections']}
    p2 = [x['en'] for x in secs['para2_why']['sentences']]
    p3 = [x['en'] for x in (secs['para3_positive'].get('pool_all') or [])]
    return flat, p2, p3


def essay_paras(it, idx):
    blocks = it.get('blocks') or []
    if len(blocks) <= idx:
        return []
    b = blocks[idx]
    if b.get('sents'):
        return [s['en'] for s in b['sents']]
    return [b.get('v', '')]


def main():
    flat, p2, p3 = load()
    print(f'句池：第二段 {len(p2)} 条 / 第三段 {len(p3)} 条\n')
    stat = {'p2': [0, 0, 0], 'p3': [0, 0, 0]}   # 命中 高相似 未覆盖
    rows = []
    for no in TARGET:
        it = flat.get(no)
        if not it:
            continue
        for pidx, pool, key, label in ((1, p2, 'p2', '第二段'), (2, p3, 'p3', '第三段')):
            for s in essay_paras(it, pidx):
                best, hit = 0.0, ''
                for cand in pool:
                    v = sim(strip_prefix(s), cand)
                    if v > best:
                        best, hit = v, cand
                if best >= 0.985:
                    lvl = '原文'; stat[key][0] += 1
                elif best >= 0.62:
                    lvl = '改写'; stat[key][1] += 1
                else:
                    lvl = '未覆盖'; stat[key][2] += 1
                rows.append((no, label, lvl, round(best, 2), s, hit))
    for no, label, lvl, sc, s, hit in rows:
        icon = {'原文': '===', '改写': ' ~ ', '未覆盖': ' X '}[lvl]
        print(f'[{icon}] NO{no} {label} {sc:.2f}  {s[:110]}')
        if lvl == '改写':
            print(f'          ↳ 最接近池句: {hit[:110]}')
    print('\n汇总（原文命中 / 高相似改写 / 完全未覆盖）')
    for k, label in (('p2', '第二段'), ('p3', '第三段')):
        a, b, c = stat[k]
        print(f'  {label}: {a} / {b} / {c}   共 {a + b + c} 句，覆盖 {a + b} 句（{(a + b) / max(1, a + b + c) * 100:.0f}%）')


if __name__ == '__main__':
    main()
