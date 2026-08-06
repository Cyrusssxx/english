import re, os, json, glob

SRC = 'tools/extracted'

# 2025 无 exam.txt，手工整理自 notes_ocr.txt
DIRECTIONS_2025 = {
    'writing_a': (
        "Suppose you are planning a short play based on a classic Chinese novel. "
        "Write your friend John an email to 1) introduce the play, and 2) invite him to take part in it. "
        "Write your answer in about 100 words on the ANSWER SHEET. "
        'Do not sign your own name in your email; use "Li Ming" instead. (10 points)'
    ),
    'writing_b': (
        "Write an essay based on the chart below. In your essay, you should "
        "1) describe and interpret the chart, and 2) give your comments. "
        "Write your answer in about 150 words on the ANSWER SHEET. (15 points)"
    ),
}

def get_dirs(lines, idx, max_lines=11):
    """从 'NN. Directions:' 起截取，至含 points 的行或空行/页标记，最多 max_lines 行"""
    out = []
    for i in range(idx + 1, min(idx + 1 + max_lines, len(lines))):
        l = lines[i]
        if not l.strip():
            break
        if re.match(r'^\s*\[?page|^\s*Part [AB]\s*$|^\s*Section|^[-\d.]+\s*$|^\s*\(?\s*\d+\s*\)?\s*$', l):
            break
        out.append(l.strip())
        if 'points' in l:
            break
    return ' '.join(out)

def find_dirs(lines, num):
    """定位 'NN. Directions' 或 'N N. Directions'（OCR 空格）"""
    pat = re.compile(r'^\s*' + str(num) + r'\s*\.\s*Directions', re.I)
    for i, l in enumerate(lines):
        if pat.search(l):
            return i
    pat2 = re.compile(r'^' + str(num)[0] + r'\s+' + str(num)[1] + r'\s*\.\s*Directions', re.I)
    for i, l in enumerate(lines):
        if pat2.search(l):
            return i
    return None

for y in range(2010, 2026):
    fn = os.path.join(SRC, f'{y}_exam.txt')
    if not os.path.exists(fn):
        print(y, 'SKIP (no exam.txt)')
        continue
    lines = open(fn, encoding='utf-8').read().split('\n')
    got = {}
    for num, key in ((47, 'writing_a'), (48, 'writing_b')):
        i = find_dirs(lines, num)
        if i is None:
            print(y, f'{key}: NOT FOUND')
            continue
        d = get_dirs(lines, i)
        # 过滤图表数字行噪音
        d = re.sub(r'\s{2,}', ' ', d)
        got[key] = d
    if y == 2025:
        got = dict(DIRECTIONS_2025)
    # 写入 extra JSON
    extra_fn = os.path.join(SRC, 'modules', f'{y}_extra.json')
    extra = json.load(open(extra_fn, encoding='utf-8'))
    for a in extra.get('articles', []):
        if a.get('type') in got and got[a['type']]:
            a['directions'] = got[a['type']]
    json.dump(extra, open(extra_fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in got.items():
        print(f'{y} {k}: {len(v)}字 | {v[:60]}...')
