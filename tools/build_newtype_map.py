# -*- coding: utf-8 -*-
"""英二新题型类型分类（Part B）→ pwa/data/newtype_map.json

首页「新题型」chip 行用它做筛选（仅英二，2010-2025 共 16 篇）。
类型从各年 newtype 文章的 qtype 归纳：
  小标题 → 小标题对应（给段落配小标题）
  匹配   → 多项对应（左 5 项 ↔ 右 7 项）
  判断   → 判断正误（T/F，2010 仅 1 次）
数据源 = pwa/data/{year}.json，改年份数据后重跑本脚本即可。
"""
import io
import json
import os
import sys
from collections import OrderedDict

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'pwa', 'data')

# qtype → (首页 chip 名, 一句话说明)
QTYPE_MAP = OrderedDict([
    ('小标题', ('小标题对应', '给每段配小标题（7 选 5）——答案=段落主旨，干扰项=局部细节')),
    ('匹配', ('多项对应', '左 5 项 ↔ 右 7 项信息匹配——「只提到但没做这件事」是高频陷阱')),
    ('判断', ('判断正误', 'True / False 逐条回原文比对（2010 年后未再考）')),
])
ORDER = ['小标题对应', '多项对应', '判断正误']

# 年份缺 newtype 的说明（数据现状，供 hint 用）
def main():
    types = OrderedDict()          # label -> {'years': [...], 'qtypes': set()}
    amap = {}
    for y in range(2007, 2027):
        fp = os.path.join(DATA, '%d.json' % y)
        if not os.path.exists(fp):
            continue
        d = json.load(io.open(fp, encoding='utf-8'))
        for a in d.get('articles') or []:
            if a.get('type') != 'newtype':
                continue
            qs = a.get('questions') or []
            qt = None
            for q in qs:
                if q.get('qtype'):
                    qt = q['qtype']
                    break
            label = QTYPE_MAP.get(qt, (qt or '未分类', ''))[0]
            types.setdefault(label, {'years': [], 'qtypes': set()})
            types[label]['years'].append(y)
            types[label]['qtypes'].add(qt)
            amap[a['id']] = label

    out_types = []
    for label in ORDER + [k for k in types if k not in ORDER]:
        if label not in types:
            continue
        v = types[label]
        desc = next((d for q, (l, d) in QTYPE_MAP.items() if l == label), '')
        ys = sorted(v['years'], reverse=True)
        out_types.append({
            'id': label,
            'count': len(ys),
            'years': ys,
            'desc': desc,
            'qtypes': sorted(x for x in v['qtypes'] if x),
        })

    out = {
        'note': '英二新题型（Part B）类型分类，由 tools/build_newtype_map.py 生成',
        'years': sorted(set(y for t in out_types for y in t['years'])),
        'types': out_types,
        'map': amap,
    }
    fp = os.path.join(DATA, 'newtype_map.json')
    io.open(fp, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print('生成 %s' % fp)
    for t in out_types:
        print('  %-6s %d 篇 | %s | %s' % (t['id'], t['count'],
                                        '·'.join(str(y) for y in t['years']), t['desc'][:30]))
    print('总篇数:', len(amap), '| 年份:', out['years'][0], '-', out['years'][-1])


if __name__ == '__main__':
    main()
