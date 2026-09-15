# -*- coding: utf-8 -*-
"""
把「套用示范」同步进题库文章（pwa/data/{year}.json）

文章页（article.html）读的是文章对象里的 apply 字段，而生成器写的是
  pwa/data/writing_apply.json       大作文（writingb）
  pwa/data/small_apply.json         小作文（writinga）
本脚本把两者同步进每年的 year.json —— 改完示范**必须跑它**，否则文章页看到的还是旧版。

用法：python tools/sync_apply.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')

BIG_SRC = os.path.join(DATA, 'writing_apply.json')
SMALL_SRC = os.path.join(DATA, 'small_apply.json')
SMALL_AID = {}       # year -> aid（小作文 id 有两种命名：2010_writinga / 2026_writing_a）

try:
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import apply_small_plan as P
    SMALL_AID = {y: c['aid'] for y, c in P.PLAN.items()}
except Exception:      # noqa: BLE001
    pass


def load(fp):
    return json.load(io.open(fp, encoding='utf-8')) if os.path.exists(fp) else {}


def main():
    big, small = load(BIG_SRC), load(SMALL_SRC)
    years = sorted(set(big) | set(small))
    n = 0
    for y in years:
        fp = os.path.join(DATA, '%s.json' % y)
        if not os.path.exists(fp):
            print('  ⚠ %s.json 不存在，跳过' % y)
            continue
        d = json.load(io.open(fp, encoding='utf-8'))
        changed = False
        for a in d.get('articles', []):
            if y in big and a.get('id', '').endswith('writingb'):
                ap = big[y]
                a['apply'] = {
                    'apply_en': ap['apply_en'], 'apply_cn': ap['apply_cn'],
                    'tips': ap['tips'], 'title': ap.get('title', ''),
                    'slot_phrases': ap.get('slot_phrases') or [],
                    'key_phrases': ap.get('key_phrases') or [],
                }
                changed = True
            aid = SMALL_AID.get(y)
            if y in small and aid and a.get('id') == aid:
                ap = small[y]
                a['apply'] = {
                    'apply_en': ap['apply_en'], 'apply_cn': ap['apply_cn'],
                    'tips': ap['tips'], 'title': ap.get('title', ''),
                    'slot_phrases': ap.get('slot_phrases') or [],
                    'key_phrases': ap.get('key_phrases') or [],
                }
                changed = True
        if changed:
            json.dump(d, io.open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            n += 1
    print('同步 %d 年；大作文 %d 篇 / 小作文 %d 篇' % (n, len(big), len(small)))


if __name__ == '__main__':
    main()
