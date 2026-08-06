# -*- coding: utf-8 -*-
"""
增量补词典：把真题语料内、ECDICT 可查、但 dict.json 缺失的词补进去。

背景：dict.json 由一次性脚本（已丢失）从 ECDICT + 4 本内置词书扩充而来，
仍缺 919 个语料内词（含 optimism 等基础词），且用户查 quirky/quirk 也查不到。

策略：
- 语料 = 16 年真题正文全部词（去重、小写）
- 找出 dictLookup（words 直接/forms 映射）查不到的纯字母词
- 到 ECDICT 取条目，优先用 exchange 0:lemma 收敛原形（原形一并补）
- 补进 words（{p,t,frq,tag}），变形进 forms
- 不动已有词条；只新增
- 可选 EXTRA 词：非语料但用户可能手动查的基础词也补

运行：python -X utf8 tools/patch_dict.py
"""
import csv
import json
import glob
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
CSV_PATH = os.path.join(ROOT, 'tools', 'ecdict.csv')
DICT_PATH = os.path.join(DATA_DIR, 'dict.json')

TRANS_MAX = 80
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")

# 非语料但用户明确需要可查的基础词
EXTRA = [
    'optimism', 'optimist', 'optimistic', 'optimistically',
    'quirk', 'quirks', 'quirky', 'quirkier', 'quirkiest',
]


def parse_exchange(ex):
    d = {}
    for part in (ex or '').split('/'):
        if ':' in part:
            k, v = part.split(':', 1)
            d[k] = v.strip()
    return d


def clean_trans(t):
    t = (t or '').replace('\\n', '; ').replace('\n', '; ').strip()
    t = re.sub(r'\s+', ' ', t)
    if len(t) > TRANS_MAX:
        t = t[:TRANS_MAX].rstrip() + '…'
    return t


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def main():
    dict_data = json.load(open(DICT_PATH, encoding='utf-8'))
    words = dict_data['words']
    forms = dict_data['forms']
    old_count = len(words)

    # 语料
    corpus = set()
    for f in sorted(glob.glob(os.path.join(DATA_DIR, '20*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for art in d.get('articles', []):
            for s in art.get('sentences', []):
                for tok in WORD_RE.findall(s.get('en', '') or ''):
                    w = tok.lower().strip("'-")
                    if len(w) >= 2:
                        corpus.add(w)
    corpus |= set(EXTRA)

    def resolvable(w):
        if w in words:
            return True
        b = forms.get(w)
        return bool(b and b in words)

    need = set(w for w in corpus if not resolvable(w))
    print(f'待补词（查不到）：{len(need)}')

    # 抓 ECDICT 条目
    rows = {}
    with open(CSV_PATH, encoding='utf-8', newline='') as fp:
        for row in csv.DictReader(fp):
            w = (row.get('word') or '').strip().lower()
            if w in need:
                rows[w] = row

    # 第一轮：收集直接可补的词，并收集需补的原形
    to_add = {}   # base -> row
    form_map = {} # 变形 -> base
    for w in list(need):
        row = rows.get(w)
        if not row:
            continue
        lem = parse_exchange(row.get('exchange')).get('0')
        if lem:
            lb = lem.strip().lower()
            form_map[w] = lb
            need.add(lb)
        else:
            to_add[w] = row
    for lb in sorted(w for w in need if w not in rows):
        if lb in rows:
            pass

    # 第二轮：补抓原形条目
    with open(CSV_PATH, encoding='utf-8', newline='') as fp:
        for row in csv.DictReader(fp):
            w = (row.get('word') or '').strip().lower()
            if w in form_map.values() and w not in to_add:
                to_add[w] = row
            elif w in need and w not in to_add and not form_map.get(w):
                to_add[w] = row

    # 补原形表单：让 form_map 中指向的原形必然存在
    for b in set(form_map.values()):
        if b not in to_add and b in rows:
            to_add[b] = rows[b]

    added_words = 0
    for base, row in to_add.items():
        if base in words:
            continue
        t = clean_trans(row.get('translation'))
        if not t:
            continue
        r = [r2 for r2 in (to_int(row.get('frq')), to_int(row.get('bnc'))) if r2 > 0]
        words[base] = {
            'p': (row.get('phonetic') or '').strip(),
            't': t,
            'frq': min(r) if r else 0,
            'tag': (row.get('tag') or '').strip(),
        }
        added_words += 1

    added_forms = 0
    for w, b in form_map.items():
        if b in words and w not in words:
            if w not in forms:
                forms[w] = b
                added_forms += 1

    with open(DICT_PATH, 'w', encoding='utf-8') as fp:
        json.dump(dict_data, fp, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(DICT_PATH)
    print(f'新增词条：{added_words}（{old_count} → {len(words)}）')
    print(f'新增变形：{added_forms}')
    print(f'dict.json 体积：{size / 1024:.1f} KB')

    # 复查乐观主义/古怪
    for w in ['optimism', 'quirky', 'quirkier', 'optimistic']:
        hit = w in words or (forms.get(w) and forms[w] in words)
        print(f'  {w}: {"✓" if hit else "✗"}')


if __name__ == '__main__':
    main()
