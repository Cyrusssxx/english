# -*- coding: utf-8 -*-
"""
从 ECDICT (tools/ecdict.csv) + 题库 (pwa/data/20*.json) 构建精简离线词典 pwa/data/dict.json。

思路：
- 语料 = 16 年真题正文全部单词（去重、小写）。用户读到的词必在语料内。
- 只收录「语料内、词典可查、非简单词」的较难词，产出单文件全量 precache。
- 简单词判定单一数据源 is_simple()：带中/高考基础标签(zk/gk) 或 词频排名 <= 阈值 或 过短 或 停用词。
- 词形还原：利用 ECDICT exchange 的 0:lemma 字段把变形词收敛到原形，仅当变形也在语料内才写入 forms。

运行：python -X utf8 tools/build_dict.py
"""
import csv
import json
import glob
import re
import os
import sys

# ---- 可调常量 ----
SIMPLE_FRQ_RANK = 3000          # 词频排名 <= 此值视为简单词（松紧开关）
TRANS_MAX = 80                  # 中文释义截断长度
SIZE_WARN_KB = 800              # dict.json 体积告警阈值
VERSION = 'en2-v9'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
CSV_PATH = os.path.join(ROOT, 'tools', 'ecdict.csv')
OUT_PATH = os.path.join(DATA_DIR, 'dict.json')

# 考研词表（用于难度校准：重点词即便高频也保留为难词）
EXAM_LIB_DIR = r"d:\ai code\英语词库"
EXAM_LIB_FILES = [
    '考研真题核心词汇书.txt',
    '完全版考研考纲词汇（乱序）.txt',
    '考研形近易混词汇.txt',
]
EXAM_WORDS = set()              # 在 main 中加载：首个空白前 token 的小写

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")

# 高频功能词/停用词（这些即便命中词典也不做可点）
STOPWORDS = set("""
a an the and or but if then else when while of to in on at by for with about against
between into through during before after above below from up down out off over under
again further once here there all any both each few more most other some such no nor
not only own same so than too very can will just should now is are was were be been
being have has had do does did i you he she it we they them his her its our your their
this that these those as me my mine ours yours theirs who whom which what where why how
""".split())

csv.field_size_limit(10 * 1024 * 1024)


def load_exam_words():
    """加载 3 个考研词表的首 token（小写）为集合；文件缺失则静默跳过。"""
    words = set()
    for name in EXAM_LIB_FILES:
        path = os.path.join(EXAM_LIB_DIR, name)
        if not os.path.exists(path):
            print(f'⚠ 考研词表缺失，跳过：{path}')
            continue
        with open(path, encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                tok = re.split(r'\s+', line, maxsplit=1)[0].strip().lower()
                if tok:
                    words.add(tok)
    return words


def build_corpus():
    """扫描全部题库正文，返回小写去重词集。"""
    corpus = set()
    files = sorted(glob.glob(os.path.join(DATA_DIR, '20*.json')))
    for f in files:
        with open(f, encoding='utf-8') as fp:
            d = json.load(fp)
        for art in d.get('articles', []):
            for s in art.get('sentences', []):
                for tok in WORD_RE.findall(s.get('en', '') or ''):
                    w = tok.lower().strip("'-")
                    if len(w) >= 2:
                        corpus.add(w)
    return corpus, files


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


def rank_of(row):
    """取 frq / bnc 中较小的非零排名；都为 0 视为未收录（很生僻）。"""
    ranks = [r for r in (to_int(row.get('frq')), to_int(row.get('bnc'))) if r > 0]
    return min(ranks) if ranks else 10 ** 9


def is_simple(row, word):
    tag = row.get('tag') or ''
    if 'zk' in tag or 'gk' in tag:
        return True
    if len(word) <= 3:
        return True
    if word in STOPWORDS:
        return True
    # 考研重点词：过了基础闸门后，即便高频也保留为难词（置于词频闸门之前）
    if word in EXAM_WORDS:
        return False
    if rank_of(row) <= SIMPLE_FRQ_RANK:
        return True
    return False


def main():
    if not os.path.exists(CSV_PATH):
        print('ERROR: 未找到 tools/ecdict.csv，请先在联网环境下载 ECDICT 词典源。')
        sys.exit(1)

    corpus, files = build_corpus()
    print(f'语料：{len(files)} 个题库文件，去重后 {len(corpus)} 个词')

    global EXAM_WORDS
    EXAM_WORDS = load_exam_words()
    print(f'考研词表：{len(EXAM_WORDS)} 个重点词（高频也保留为难词）')

    # Pass 1：抓取语料词的直接条目
    entries = {}
    with open(CSV_PATH, encoding='utf-8', newline='') as fp:
        for row in csv.DictReader(fp):
            w = (row.get('word') or '').strip().lower()
            if w in corpus:
                entries[w] = row

    # 收集需要补抓的原形（变形词的 lemma 不在语料时也要拿到，用于判定与释义）
    need_lemmas = set()
    for w in list(entries.keys()):
        lem = parse_exchange(entries[w].get('exchange')).get('0')
        if lem:
            need_lemmas.add(lem.strip().lower())
    need_lemmas -= set(entries.keys())

    # Pass 2：补抓原形条目
    if need_lemmas:
        with open(CSV_PATH, encoding='utf-8', newline='') as fp:
            for row in csv.DictReader(fp):
                w = (row.get('word') or '').strip().lower()
                if w in need_lemmas:
                    entries[w] = row

    words = {}   # base -> {p, t, frq, tag}
    forms = {}   # 变形词 -> base（仅当变形也在语料内）
    for w in sorted(corpus):
        row = entries.get(w)
        if not row:
            continue  # 词典查不到：简单词或专有名词，天然不包 span
        # 收敛到原形
        base, base_row = w, row
        lem = parse_exchange(row.get('exchange')).get('0')
        if lem:
            lb = lem.strip().lower()
            if lb in entries and lb != w:
                base, base_row = lb, entries[lb]
        t = clean_trans(base_row.get('translation'))
        if not t:
            continue  # 无中文释义，跳过
        if is_simple(base_row, base):
            continue  # 简单词跳过
        if base not in words:
            r = rank_of(base_row)
            words[base] = {
                'p': (base_row.get('phonetic') or '').strip(),
                't': t,
                'frq': r if r < 10 ** 9 else 0,
                'tag': (base_row.get('tag') or '').strip(),
            }
        if w != base:
            forms[w] = base

    out = {'version': VERSION, 'words': words, 'forms': forms}
    with open(OUT_PATH, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(OUT_PATH)
    print(f'难词收录：{len(words)} 条，变形映射：{len(forms)} 条')
    print(f'输出：{OUT_PATH}  体积：{size / 1024:.1f} KB')
    if size > SIZE_WARN_KB * 1024:
        print(f'⚠ 警告：dict.json 超过 {SIZE_WARN_KB}KB，可去掉音标字段 p 压缩体积。')


if __name__ == '__main__':
    main()
