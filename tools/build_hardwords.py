# -*- coding: utf-8 -*-
"""
构建精选难词集合，产出 pwa/data/hardwords.json：{"version":1, "words":[...]}。

数据源：内置词书 deck_tc_senses.json（熟词僻义）+ deck_realexam.json（真题高频·较难词）。
- 词条统一小写归一；词组 key（含空格）原样小写保留，单词用 dict.json forms 展开到原形一并收录，
  使正文任意词形（如 hits→hit、accommodating→accommodate）都能命中精选集合。
- 输出 words 为普通数组，运行时 new Set() 快速检索。

运行：python -X utf8 tools/build_hardwords.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
OUT_PATH = os.path.join(DATA_DIR, 'hardwords.json')

SOURCES = ['deck_tc_senses.json', 'deck_realexam.json']


def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding='utf-8') as fp:
        return json.load(fp)


def main():
    forms = (load_json('dict.json').get('forms', {}) or {}) if os.path.exists(
        os.path.join(DATA_DIR, 'dict.json')) else {}

    hard = set()
    per_source = {}
    for fn in SOURCES:
        deck = load_json(fn)
        words = [w['word'] for w in deck.get('words', [])]
        per_source[fn] = len(words)
        for w in words:
            key = str(w or '').lower().strip()
            if not key:
                continue
            hard.add(key)
            # 单词（无空格）再补其 forms 原形，覆盖变形词命中
            if ' ' not in key and key in forms:
                hard.add(forms[key])

    words = sorted(hard)
    with open(OUT_PATH, 'w', encoding='utf-8') as fp:
        json.dump({'version': 1, 'words': words}, fp, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(OUT_PATH)
    print('数据源：' + ' + '.join(f'{k} ({v}词)' for k, v in per_source.items()))
    print(f'精选难词集合（去重+forms展开）：{len(words)} 个')
    print(f'输出：{OUT_PATH}  体积：{size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
