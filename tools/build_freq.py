# -*- coding: utf-8 -*-
"""
统计真题考频，产出 pwa/data/freq.json：{ "词/词组key": {"c": 出现次数, "a": 出现文章数}, ... }。

数据源：pwa/data/20*.json 的 articles[].sentences[].en（16 年真题正文）。
- 单词：小写归一 + 用 dict.json 的 forms 变形还原到原形，使 economist/economists 归并统计；
        key 与 dict.js 的 dictLookup 归一后一致，运行时 freqLookup 可命中。
- 词组：复用 pwa/data/phrases.json 的 key 做最长优先、非重叠匹配（与精读页 annotatePhrases 同口径）。
仅统计真题实际出现，绝不编造；无出现的词/词组不写入。

运行：python -X utf8 tools/build_freq.py
"""
import json
import glob
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
DICT_PATH = os.path.join(DATA_DIR, 'dict.json')
PHRASES_PATH = os.path.join(DATA_DIR, 'phrases.json')
OUT_PATH = os.path.join(DATA_DIR, 'freq.json')

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")


def norm_word(tok):
    """与 dict.js normWord 一致：小写 + 去首尾非字母。"""
    w = tok.lower()
    w = re.sub(r"^[^a-z]+", '', w)
    w = re.sub(r"[^a-z]+$", '', w)
    return w


def load_forms():
    """从 dict.json 读变形→原形映射；缺失则返回空映射。"""
    if not os.path.exists(DICT_PATH):
        print('⚠ 未找到 dict.json，单词不做变形归并。')
        return {}
    with open(DICT_PATH, encoding='utf-8') as fp:
        d = json.load(fp)
    return d.get('forms', {}) or {}


def load_phrase_index():
    """从 phrases.json 构建 首词→[(tokens, key)] 按 token 数降序，供最长优先匹配。"""
    if not os.path.exists(PHRASES_PATH):
        print('⚠ 未找到 phrases.json，跳过词组考频。')
        return {}
    with open(PHRASES_PATH, encoding='utf-8') as fp:
        data = json.load(fp)
    phrases = data.get('phrases', {}) or {}
    index = {}
    for key in phrases:
        toks = key.split(' ')
        index.setdefault(toks[0], []).append((toks, key))
    for lst in index.values():
        lst.sort(key=lambda x: len(x[0]), reverse=True)
    return index


def match_phrases(text, index):
    """左→右逐 token 最长优先、非重叠匹配，返回命中的 key 列表（可重复）。"""
    hits = []
    toks = [(m.start(), m.end(), m.group(0).lower()) for m in WORD_RE.finditer(text)]
    i = 0
    while i < len(toks):
        cands = index.get(toks[i][2])
        matched = None
        if cands:
            for tk, key in cands:
                n = len(tk)
                if i + n > len(toks):
                    continue
                ok = True
                for k in range(1, n):
                    if toks[i + k][2] != tk[k]:
                        ok = False
                        break
                    gap = text[toks[i + k - 1][1]:toks[i + k][0]]
                    if not re.fullmatch(r"[\s\-]*", gap):
                        ok = False
                        break
                if ok:
                    matched = (tk, key)
                    break
        if matched:
            hits.append(matched[1])
            i += len(matched[0])
        else:
            i += 1
    return hits


def main():
    forms = load_forms()
    pindex = load_phrase_index()

    word_c = {}   # base -> 次数
    word_a = {}   # base -> set(article_id)
    phr_c = {}
    phr_a = {}

    files = sorted(glob.glob(os.path.join(DATA_DIR, '20*.json')))
    art_count = 0
    for f in files:
        with open(f, encoding='utf-8') as fp:
            d = json.load(fp)
        for art in d.get('articles', []):
            art_count += 1
            aid = art.get('id', '')
            for s in art.get('sentences', []):
                en = s.get('en', '') or ''
                # 单词
                for tok in WORD_RE.findall(en):
                    w = norm_word(tok)
                    if len(w) < 2:
                        continue
                    base = forms.get(w, w)
                    word_c[base] = word_c.get(base, 0) + 1
                    word_a.setdefault(base, set()).add(aid)
                # 词组
                for key in match_phrases(en, pindex):
                    phr_c[key] = phr_c.get(key, 0) + 1
                    phr_a.setdefault(key, set()).add(aid)

    out = {}
    for w, c in word_c.items():
        out[w] = {'c': c, 'a': len(word_a[w])}
    for key, c in phr_c.items():
        out[key] = {'c': c, 'a': len(phr_a[key])}

    with open(OUT_PATH, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))

    size = os.path.getsize(OUT_PATH)
    print(f'文章：{art_count} 篇（{len(files)} 个题库文件）')
    print(f'考频条目：单词 {len(word_c)} · 词组 {len(phr_c)}')
    print(f'输出：{OUT_PATH}  体积：{size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
