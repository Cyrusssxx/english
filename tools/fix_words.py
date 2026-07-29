"""fix_words.py — 将 words[].w 修正为英文原句中实际出现的词形/短语跨度
用法: python -X utf8 tools\\fix_words.py 2023 [--apply]
默认仅打印建议；加 --apply 才写回文件（按句内定位替换，保留原有行格式）。
"""
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
DATA_DIR = TOOLS.parent / 'pwa' / 'data'

PLACEHOLDERS = {
    'sth', 'sb', 'sb/sth', 'sth/sb', 'one', "one's", 'ones', 'a', 'an', 'the',
    'be', 'do', 'sth.', 'oneself', 'yourself',
}


def find_word(text, w):
    start = 0
    while True:
        pos = text.find(w, start)
        if pos < 0:
            return -1
        before = text[pos - 1] if pos > 0 else ''
        after = text[pos + len(w)] if pos + len(w) < len(text) else ''
        if not before.isalpha() and not after.isalpha():
            return pos
        start = pos + 1


def stem_match(a, b):
    a, b = a.lower(), b.lower()
    if a == b:
        return True
    n = 0
    for x, y in zip(a, b):
        if x == y:
            n += 1
        else:
            break
    m = min(len(a), len(b))
    return n >= 3 and n >= m - 3


def tokens(en):
    return [(mo.group(0), mo.start(), mo.end())
            for mo in re.finditer(r"[A-Za-z][A-Za-z'\-]*", en)]


def suggest(en, w):
    toks = tokens(en)
    parts = w.split()
    content = [p for p in parts if p.lower() not in PLACEHOLDERS
               and p not in ('A', 'B')]
    if not content:
        return None
    # 逐个内容词按词干顺序匹配，取覆盖跨度
    idx = 0
    matched = []
    for cw in content:
        found = None
        for j in range(idx, len(toks)):
            if stem_match(toks[j][0], cw):
                found = j
                break
        if found is None:
            return None
        matched.append(found)
        idx = found + 1
    lo = toks[matched[0]][1]
    hi = toks[matched[-1]][2]
    cand = en[lo:hi]
    if find_word(en, cand) < 0:
        return None
    return cand


def main():
    if len(sys.argv) < 2:
        print('need year')
        sys.exit(1)
    year = sys.argv[1]
    apply = '--apply' in sys.argv
    path = DATA_DIR / f'{year}.json'
    raw = path.read_text(encoding='utf-8')
    data = json.loads(raw)

    fixes = []  # (sid, old, new)
    fail = []
    for art in data.get('articles', []):
        for s in art.get('sentences', []):
            en = s.get('en', '')
            sid = s.get('id')
            for w in s.get('words', []):
                ww = w.get('w')
                if not ww:
                    continue
                if find_word(en, ww) >= 0:
                    continue
                new = suggest(en, ww)
                if new and new != ww:
                    fixes.append((sid, ww, new))
                else:
                    fail.append((sid, ww, en))

    print('=== 建议替换 ===')
    for sid, old, new in fixes:
        print(f'{sid}: "{old}"  ->  "{new}"')
    if fail:
        print('\n=== 无法自动确定（需人工）===')
        for sid, ww, en in fail:
            print(f'{sid}: "{ww}"')
            print(f'    en: {en}')
    print(f'\n共 {len(fixes)} 条可自动修正, {len(fail)} 条需人工')

    if apply and not fail:
        lines = raw.split('\n')
        for sid, old, new in fixes:
            key = f'"id": "{sid}"'
            for i, ln in enumerate(lines):
                if key in ln:
                    lines[i] = ln.replace(f'"w": "{old}"', f'"w": "{new}"', 1)
                    break
        path.write_text('\n'.join(lines), encoding='utf-8')
        print('\n已写回', path)
    elif apply and fail:
        print('\n存在无法自动修正的条目，未写回。')


if __name__ == '__main__':
    main()
