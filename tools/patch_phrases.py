# -*- coding: utf-8 -*-
"""
增量补充词组词典：从 ECDICT 抓真题语料中出现的多词搭配并入 phrases.json。

背景：现有词组词典仅覆盖 PDF 词组书 + 题库人工词组（1581 条），用户反馈
精翻中「puts in / draws out / in which / supposed to」等常见搭配无法连续翻译。

方案：
- 扫描 16 年真题正文全部相邻 2-3 词组合
- 在 ECDICT 中查这些组合（ECDICT 收录常用短语/搭配）
- 释义纯净（中文、无英文泄漏、长度合理）则并入 phrases.json
- 保留原词典条目；新词组低优先级（不覆盖）

运行：python -X utf8 tools/patch_phrases.py
"""
import csv
import json
import glob
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
CSV_PATH = os.path.join(ROOT, 'tools', 'ecdict.csv')
PHRASES_PATH = os.path.join(DATA_DIR, 'phrases.json')

TOK = re.compile(r"[A-Za-z][A-Za-z'\-]*")

FUNCTION = set("""the a an of to in on for with at from by about out off up down over under
as than so then but and or nor if yet while when where why how what which who whom whose
this that these those there here all any both each few more most other some such no not
only own same very can will just should is are was were be been being have has had do does
did i you he she it we they them his her its our your their me my mine ours yours us""".split())


def corpus_vocab():
    """真题语料中出现过的全部单词（小写），用于界定「常见词」。"""
    words = set()
    for f in sorted(glob.glob(os.path.join(DATA_DIR, '20*.json'))):
        with open(f, encoding='utf-8') as fp:
            d = json.load(fp)
        for art in d.get('articles', []):
            for s in art.get('sentences', []):
                words.update(m.group(0).lower() for m in TOK.finditer(s.get('en', '') or ''))
    return words


def clean_meaning(m):
    m = (m or '').replace('\\n', '\n').split('\n')[0].strip()
    if not re.search(r'[\u4e00-\u9fff]', m):
        return None
    if re.search(r'[A-Za-z]', m):
        return None
    if len(m) > 40:
        return None
    return m


def main():
    common = corpus_vocab() | FUNCTION
    print(f'常见词表：{len(common)}')

    cur = json.load(open(PHRASES_PATH, encoding='utf-8'))
    phrases = cur['phrases']
    added = {}
    with open(CSV_PATH, encoding='utf-8', newline='') as fp:
        for row in csv.DictReader(fp):
            w = (row.get('word') or '').strip().lower()
            if ' ' not in w or w in phrases:
                continue
            toks = w.split()
            if not (2 <= len(toks) <= 4):
                continue
            if not all(t in common for t in toks):
                continue
            if toks[0] in FUNCTION and toks[-1] in FUNCTION:
                continue
            m = clean_meaning(row.get('translation'))
            if m:
                added[w] = m
    phrases.update(added)
    cur['maxWords'] = max(cur.get('maxWords') or 0, 4)
    with open(PHRASES_PATH, 'w', encoding='utf-8') as fp:
        json.dump(cur, fp, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(PHRASES_PATH)
    print(f'新增 {len(added)} 条，词组总数 {len(phrases)} → phrases.json {size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
