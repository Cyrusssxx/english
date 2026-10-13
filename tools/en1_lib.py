# -*- coding: utf-8 -*-
"""英语一真题/解析 PDF 抽取库（2016-2025 完形 & 新题型补全用）。

真题 PDF：有文本层 → 官方英文原文 + 选项。
解析 PDF：2016-2023 有文本层，双栏排布（左英文/右中文）→ 逐句译文、选项中文、答案、解析。
          2024/2025 为扫描件（无文本层）→ 需另行补译文与解析。
"""
import re, os, glob
import pymupdf

EXAM_BASE = r'D:\ai code\英语考研试题和答案\【2】2010-2025年考研英语一真题及解析\01、英一真题部分'
KEY_BASE = r'D:\ai code\英语考研试题和答案\【2】2010-2025年考研英语一真题及解析\02、解析部分\详细版'

# ---- 页眉页脚噪声行 ----
NOISE_PATS = [
    re.compile(r'^英语（一）试题'),
    re.compile(r'^（共\s*\d+\s*页）$'),
    re.compile(r'^\d{4}\s*年英语（一）试题第\d+页共\d+页$'),
    re.compile(r'^\d{4}\s*年考研英语'),
    re.compile(r'^6HFWLRQ'),
    re.compile(r'^\.?\s*\d{1,2}\s*\.?$'),
    re.compile(r'^\s*\d{1,2}\s*$'),
    re.compile(r'^认准淘宝店铺'),
]

# ---- 括号变体（解析册里 [A] / 【A】/［A］/「A」/[A 都被用过，OCR 还会把 [ 认成 L） ----
OB = r'[\[【(（［「『L]'
CB = r'[\]】)）］」』J]'

OPT_LINE_A = re.compile(r'^\s*(\d{1,2})\s*[\.．、]\s*' + OB + r'\s*([A-D])\s*' + CB + r'?\s*(.*)$')
OPT_LINE_B = re.compile(r'^\s*' + OB + r'\s*([A-D])\s*' + CB + r'?\s*(.*)$')

BRACKET_MAP = {'「': '【', '『': '【', '［': '【', '(': '【',
               '」': '】', '』': '】', '］': '】', ')': '】'}


def norm_brackets(s):
    """把各种括号变体统一成【】/[]，便于后续答案/答案句的模式匹配。"""
    for a, b in BRACKET_MAP.items():
        s = s.replace(a, b)
    # OCR 常见：字母选项前的左中括号被识别成 L（如 "LA] acceptance"）
    s = re.sub(r'L\s*([A-D])\s*】', r'【\1】', s)
    s = re.sub(r'L\s*([A-D])\s*\]', r'[\1]', s)
    return s


# ---- 真题册末尾的「答案速查」表 ----
ANS_RANGE = re.compile(r'(?<![\d])(\d{1,2})\s*[-–—~]\s*(\d{1,2})\s*([A-G]{2,20})')
ANS_SEQ = re.compile(r'(?<![\d])(\d{1,2})\s*[.．、]\s*([A-G])(?![A-Za-z])')


def exam_answers(year):
    """从真题 PDF 的『答案速查』表取答案 → {题号: 字母}。

    2024/2025 的解析册是无文本层的扫描件，只能靠真题册末尾的答案表。
    注意：真题册里的"填涂说明/答题卡"页会产生一串假的 `1. A 2. A ...`，必须按
    「有答案表标题或区间写法 + 覆盖 41~45 + 答案不雷同」筛掉。
    """
    doc = exam_doc(year)
    best, best_score = {}, 0
    for pg in doc:
        t = re.sub(r'\s+', ' ', pg.get_text())
        cand = {}
        for a, _b, lets in ANS_RANGE.findall(t):
            a = int(a)
            for k, ch in enumerate(lets):
                cand.setdefault(a + k, ch)
        for n, ch in ANS_SEQ.findall(t):
            cand.setdefault(int(n), ch)
        cover = sum(1 for q in range(1, 21) if q in cand)
        if cover < 20:
            continue
        if len(set(cand[q] for q in range(1, 21))) <= 2:   # 全是同一个字母 = 假表
            continue
        strong = ('答案速查' in t) or bool(ANS_RANGE.search(t))
        score = cover + (sum(1 for q in range(41, 46) if q in cand) * 3 if strong else 0)
        if score > best_score:
            best, best_score = cand, score
    return best


# ---------------------------------------------------------------- 基础读取
def exam_doc(year):
    fs = glob.glob(os.path.join(EXAM_BASE, f'{year}*.pdf'))
    if not fs:
        raise FileNotFoundError(f'exam pdf missing: {year}')
    return pymupdf.open(fs[0])


def key_doc(year):
    fs = glob.glob(os.path.join(KEY_BASE, f'{year}*.pdf'))
    if not fs:
        raise FileNotFoundError(f'key pdf missing: {year}')
    return pymupdf.open(fs[0])


def page_spans(page):
    """返回 [(y0, x0, text)]，按视觉行流已经扁平到 span 级。"""
    out = []
    d = page.get_text('dict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            y = round(l['bbox'][1], 1)
            for s in l['spans']:
                t = s['text']
                if t.strip():
                    out.append((y, round(s['bbox'][0], 1), t))
    return out


def _dedupe_spans(items):
    """剔除盗版解析 PDF 的重影/水印副本。

    现象：同一行文本在页面上出现两份 copy（相差极小偏移），导致按 x 排序后出现
    "In In the the choice choice" 式的重影，句子 token 数翻倍、对齐失败。
    判据：文本完全相同 且 |dy| <= 16 且 |dx| <= 60 → 保留一份。
    """
    seen = []
    out = []
    for y, x, t in items:
        dup = False
        for sy, sx, st in seen:
            if st == t and abs(y - sy) <= 16 and abs(x - sx) <= 60:
                dup = True
                break
        if dup:
            continue
        seen.append((y, x, t))
        out.append((y, x, t))
    return out


def page_rows(page, ytol=5.0):
    """同 page_lines，但额外保留 (最小 y, 最左 x) 用于判定首行缩进与段落间距。"""
    items = _dedupe_spans(page_spans(page))
    items.sort(key=lambda t: (t[0], t[1]))
    out, cur, cy, anchor = [], [], [], None

    def flush():
        if not cur:
            return
        row = sorted(cur, key=lambda v: v[0])
        out.append((min(cy), row[0][0],
                    re.sub(r'\s+', ' ', ' '.join(t for _, t in row)).strip()))

    for y, x, t in items:
        if anchor is None or abs(y - anchor) <= ytol:
            cur.append((x, t))
            cy.append(y)
            anchor = y if anchor is None else anchor
        else:
            flush()
            cur, cy, anchor = [(x, t)], [y], y
    flush()
    return out


def page_lines(page, ytol=5.0):
    """同一视觉行内按 x 升序拼接 span（挖空序号以独立 span 插在正确位置）。

    注意：同一视觉行内各 span 的 y 可能相差 1~3pt（上标序号、四栏选项表中的 A/B/C/D），
    必须先按 y 聚类再按 x 重排，否则会产生 "D C A B" 这类乱序。
    """
    return [t for _y, _x, t in page_rows(page, ytol)]


def clean_line(s):
    for p in NOISE_PATS:
        if p.match(s):
            return None
    return s


def exam_pages(year):
    doc = exam_doc(year)
    res = []
    for pg in doc:
        lns = [clean_line(x) for x in page_lines(pg)]
        res.append([x for x in lns if x])
    return res


def joined(year_pages):
    return ['\n'.join(p) for p in year_pages]


# ---------------------------------------------------------------- 完形：原文
BANK = re.compile(r'^\s*(?:\d{1,2})\s*[．.、]\s*[\[【(（]')


OPT_ROW = re.compile(r'^\s*(\d{1,2})\s*[.．、]\s*(?:[\[【(（]\s*[A-D]|A\s*[.．、])')


def locate_cloze(pages):
    """返回 (起始页, 选项开始的行下标所在页) 或 None。"""
    sp = None
    for i, lns in enumerate(pages):
        if any('Use of English' in x for x in lns):
            sp = i
            break
    if sp is None:
        return None
    # 选项表：形如 "1. [A] xxx" / "1. A. xxx"
    op = None
    for i in range(sp, min(sp + 3, len(pages))):
        if sum(1 for x in pages[i] if OPT_ROW.match(x)) >= 3:
            op = i
            break
    return sp, op


MARK_RE = re.compile(r'^[\W_]*$')
HEAD_SKIP = re.compile(r'^(Section\s+I\b|Use of English|Directions\s*[：:]?|Read the following|'
                       r'mark\s+A|B\s*,\s*C\s*or\s*D|.*ANSWER SHEET.*|20\d\d\s*年.*试题|'
                       r'.*年全国硕士研究生.*|.*入学考试.*)$')


HEAD_TAIL = re.compile(r'\(?\s*10\s*points\s*\)?')
MISSING_MARK_INSERT = {
    # 个别年份某个挖空序号在 PDF 文本层里彻底丢失 → 在已知锚点后补写
    2017: [('had less severe', 12)],
}


def ClozePassageText(year):
    """返回已规整为 [n] 的完形正文字符串。"""
    lns = cloze_passage_lines(year)
    raw = ' '.join(lns)
    for anchor, n in MISSING_MARK_INSERT.get(year, []):
        if anchor in raw and ('[%d]' % n) not in raw:
            raw = raw.replace(anchor, anchor + ' %d ' % n, 1)
    txt, cnt = insert_blank_marks(raw)
    return tidy_text(txt), cnt


PARA_GAP = 27.0      # 段内行距约 19~21pt，段间距 35~63pt


def exam_page_rows(year):
    return [[(y, x, t) for y, x, t in page_rows(pg) if clean_line(t)] for pg in exam_doc(year)]


def cloze_passage_rows(year):
    """完形正文的 (y, x0, text) 列表。逻辑与 cloze_passage_lines 完全一致，只是带上
    y/x0，这样才能按行距+首行缩进切出真实段落（纯文本列表做不到）。"""
    rows_pages = exam_page_rows(year)
    flat = [[t for _y, _x, t in p] for p in rows_pages]
    loc = locate_cloze(flat)
    if not loc:
        return []
    sp, op = loc
    op = op if op is not None else sp + 1
    raw = []
    for i in range(sp, op + 1):
        for y, x, txt in rows_pages[i]:
            if i == op and OPT_ROW.match(txt):
                break
            raw.append((y, x, txt))
    cut = 0
    for j, (y, x, txt) in enumerate(raw):
        if 'ANSWER SHEET' in txt or HEAD_TAIL.search(txt):
            m = HEAD_TAIL.search(txt)
            rest = txt[m.end():].strip() if m else ''
            cut = j + 1
            if rest:
                raw.insert(cut, (y, x, rest))
            break
    out = [(y, x, txt) for y, x, txt in raw[cut:] if not HEAD_SKIP.match(txt)]
    while out and re.match(r'^[\W\d]+$', out[-1][2]):
        out.pop()
    return out


def _split_paras(rows):
    """按 (首行缩进, 自适应行距) 把视觉行切成真实段落。

    两种排版都要兼容：
      - 段落间只靠首行缩进区分（行距一致，如 2016/2020 真题册）
      - 段落间只靠行距区分（无缩进，如 2021 解析册）
    所以阈值取「该页行距中位数 ×1.25」而不是写死的 pt 值。
    """
    gaps = [rows[i + 1][0] - rows[i][0] for i in range(len(rows) - 1)
            if rows[i + 1][0] > rows[i][0]]
    if not gaps:
        return [[r[2] for r in rows]]
    gaps.sort()
    med = gaps[len(gaps) // 2]
    left = min(r[1] for r in rows)
    paras, cur = [], []
    for i, (y, x, txt) in enumerate(rows):
        if cur:
            new_para = False
            if x - left > 16.0:                     # 首行缩进（实测真段首 18~33pt）
                new_para = True
            elif med > 0 and (y - rows[i - 1][0]) > med * 1.25:
                new_para = True                      # 段间额外空白
            if new_para:
                paras.append(cur)
                cur = []
        cur.append(txt)
    if cur:
        paras.append(cur)
    return paras


def ClozePassageParas(year):
    """完形正文按真实段落切分 → [para1, para2, ...]（已规整为 [n] 空标记）。"""
    paras = _split_paras(cloze_passage_rows(year))
    SEP = ' @@PARA@@ '
    all_raw = SEP.join(' '.join(p) for p in paras)
    for anchor, n in MISSING_MARK_INSERT.get(year, []):
        if anchor in all_raw and ('[%d]' % n) not in all_raw:
            all_raw = all_raw.replace(anchor, anchor + ' %d ' % n, 1)
    all_txt, cnt = insert_blank_marks(all_raw)
    out = [tidy_text(p) for p in all_txt.split(SEP)]
    out = [p for p in out if p.strip()]
    # 过短的段落多为版面噪声（残行/页眉零头），并入相邻段
    merged = []
    for p in out:
        if merged and len(p) < 100:
            merged[-1] = merged[-1] + ' ' + p
        elif merged and len(merged[-1]) < 100:
            merged[-1] = merged[-1] + ' ' + p
        else:
            merged.append(p)
    return [p for p in merged if p.strip()], cnt


def tidy_text(s):
    """通用排版整理：引号/句号前的空格、被 OCR 掉撇号的属格、连续空格。"""
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s+([,.;:!?])', r'\1', s)          # 标点前多余空格
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    s = re.sub(r'\[(\d+)\]\s*\.\s*', r'[\1]. ', s)  # [n] .  -> [n].
    s = re.sub(r'\s+\[(\d+)\]', r' [\1]', s)
    s = re.sub(r"\[(\d+)\]\s*'", r"[\1]'", s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def cloze_passage_lines(year):
    """完形正文清洗后的行列表（含形如 "... friends, 1 those ..." 的行内序号）。"""
    pages = exam_pages(year)
    loc = locate_cloze(pages)
    if not loc:
        return []
    sp, op = loc
    op = op if op is not None else sp + 1
    raw = []
    for i in range(sp, op + 1):
        for x in pages[i]:
            if not x:
                continue
            if i == op and OPT_ROW.match(x):
                break
            raw.append(x)
    # 先切掉 Directions 抬头（在过滤前做，防止含 ANSWER SHEET 的行被先滤掉）
    cut = 0
    for j, x in enumerate(raw):
        if 'ANSWER SHEET' in x or HEAD_TAIL.search(x):
            m = HEAD_TAIL.search(x)
            rest = x[m.end():].strip() if m else ''
            cut = j + 1
            if rest:
                raw.insert(cut, rest)
            break
    out = [x for x in raw[cut:] if not HEAD_SKIP.match(x)]
    # 尾部去噪：选项表前的零头
    while out and re.match(r'^[\W\d]+$', out[-1]):
        out.pop()
    return out


JUNK_OK = set(list('.,;:!?\'"') + list('’‘“”,，(（)）[—–-'))
REAL_NUM = re.compile(r'^[\d]{4,}')


def insert_blank_marks(text, expect=20):
    """把正文里的挖空序号 token（可能是 `1`、`_1_`、`----=5`、`]` 等杂形）规整为 [n]。"""
    toks = text.split()
    res, nxt = [], 1
    while toks:
        t = toks.pop(0)
        core = t.strip("'\"“”‘’`~")
        if nxt > expect or not core:
            res.append(t)
            continue
        letters = re.sub(r'[^A-Za-z]', '', core)
        digits = re.sub(r'\D', '', core)
        if letters and not digits:
            res.append(t)
            continue
        if core.isdigit():
            if int(core) == nxt:
                res.append('[%d]' % nxt)
                nxt += 1
            else:
                res.append(t)
            continue
        if letters and digits:
            # 序号被吞进相邻词（如 2024 的 "to12" / "15remain"）→ 就地拆成 [n] + 剩余词
            if digits == str(nxt) and len(letters) <= 10:
                i0 = core.index(str(nxt))
                head = core[:i0].strip('.,;:!?\'"')
                tail = core[i0 + len(str(nxt)):].strip('.,;:!?\'"')
                if head:
                    res.append(head)
                res.append('[%d]' % nxt)
                if tail:
                    res.append(tail)
                nxt += 1
                continue
            res.append(t)
            continue
        # 纯符号（可夹数字）
        if len(digits) > 3 or REAL_NUM.match(digits):
            res.append(t)                 # 真实数字，如 1650-1180
            continue
        if digits and int(digits) == nxt:
            res.append('[%d]' % nxt)
            nxt += 1
            continue
        if len(core) <= 6 and core not in JUNK_OK:
            res.append('[%d]' % nxt)      # 序号被 OCR 吃掉，按顺序补齐
            nxt += 1
            continue
        # 长杂符（----= 之类）当作噪声丢弃
    return ' '.join(res), nxt - 1


OPT_MARK = re.compile(r'(?:(?<=[\s\(\[（【])|^)([A-D])\s*[\]】）)J]\.?\s*|(?:(?<=[\s\(\[（【])|^)([A-D])[.．、]\s+')
OPT_QNUM = re.compile(r'(?:^|(?<=[\s\n]))(\d{1,2})\s*[.．、]\s*[：:]?\s*(?=[\[\(（【A-D])')


def _norm_area(text):
    """OCR 噪声归一化：`ED]`→`[D]`、`A]`→`[A]`、`1 7.`→`17.`、全角冒号。"""
    t = text
    t = re.sub(r'\bE\s*([A-D])\s*\]', r'[\1]', t)                 # ED] -> [D]
    t = re.sub(r'(?<![\w\[])([A-D])\s*\]\s', r'[\1] ', t)         # A] xxx -> [A] xxx
    t = re.sub(r'(?m)^\s*(\d)\s+(\d)\s*([.．、])', r'\1\2.', t)    # 1 7. -> 17.
    t = t.replace('：', ':')
    return t


def _norm_opt_text(s):
    return re.sub(r'\s+', ' ', s).strip(' 　;，,、')


# ================================================================ 解析册（双栏）
MID = 300.0
CIRCLED = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
CIRCLED += '❶❷❸❹❺❻❼❽❾❿'
CIRCLED += '⓵⓶⓷⓸⓹⓺⓻⓼⓽⓾'
CIRCLED += '⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽'
CIRC_RE = re.compile('[' + CIRCLED + '©]')


# OCR 误识别：部分解析册把圈号识别成相似符号（如 2022 的 ② → ©）
OCR_CIRC = {'©': 2, '®': None, '〇': None}


def _circ_val(ch):
    if ch in OCR_CIRC:
        return OCR_CIRC[ch]
    for grp in (CIRCLED[0:20], CIRCLED[20:30], CIRCLED[30:40], CIRCLED[40:50]):
        if ch in grp:
            return grp.index(ch) + 1
    return None


def key_cols(page, mid=MID):
    """解析页双栏切分：返回 (左栏文本, 右栏文本)。"""
    items = []
    d = page.get_text('dict')
    for b in d['blocks']:
        if b['type'] != 0:
            continue
        for l in b['lines']:
            y = round(l['bbox'][1], 1)
            for s in l['spans']:
                t = s['text']
                if not t.strip():
                    continue
                x0, x1 = s['bbox'][0], s['bbox'][2]
                if x1 <= mid:
                    side = 0
                elif x0 >= mid:
                    side = 1
                else:
                    side = 0 if (x0 + x1) / 2 < mid else 1
                items.append((side, y, x0, t))
    L = sorted([i for i in items if i[0] == 0], key=lambda t: (t[1], t[2]))
    R = sorted([i for i in items if i[0] == 1], key=lambda t: (t[1], t[2]))

    def join(seq):
        out, last = [], None
        for side, y, x, t in seq:
            out.append(('\n' if last is None or y - last > 2 else ' ') + t)
            last = y
        return re.sub(r'[ \t]+', ' ', ''.join(out)).strip()

    return join(L), join(R)


def key_pages(year):
    return [key_cols(p) for p in key_doc(year)]


CJK = re.compile(r'[一-鿿]')
ASCII_W = re.compile(r'[A-Za-z]')


def cjk_ratio(s):
    return len(CJK.findall(s)) / max(1, len(s))


PASSAGE_STOP = re.compile(r'真题精解|词汇注释|难句分析|语篇分析|文章总体分析|知识补充|技巧总结|【')


def passage_streams(pages, ytol=8.0):
    """从解析页提取语篇分析区的英文/中文行流（兼容双栏对排与单栏逐行夹注两种排版）。

    返回 (en_lines, cn_lines)。判定：进入语篇区（罗马段号/圈号开头的英文行），
    退出（真题精解/词汇注释/【 块）。行内先按 x 分左右组，再按文字占比归类。
    """
    ens, cns = [], []
    PAGE_ENTER = re.compile(r'^\s*(?:[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]{1,3}|I{1,3}|IV|V|VI{0,2}|IX|X)?\s*[^\w\s]*\s*[①-⑳❶-❿©]')
    for pg in pages:
        items = _dedupe_spans(page_spans(pg))
        items.sort(key=lambda t: (t[0], t[1]))
        rows, cur, anchor = [], [], None
        for y, x, t in items:
            if anchor is None or abs(y - anchor) <= ytol:
                cur.append((x, t))
                if anchor is None:
                    anchor = y
            else:
                rows.append(cur)
                cur, anchor = [(x, t)], y
        if cur:
            rows.append(cur)
        in_passage = False
        for row in rows:
            row.sort(key=lambda t: t[0])
            groups, g, lastx = [], [], None
            for x, t in row:
                if lastx is None or x - lastx <= 30:
                    g.append(t)
                else:
                    groups.append(g)
                    g = [t]
                lastx = x
            if g:
                groups.append(g)
            for gtxt in groups:
                txt = re.sub(r'\s+', ' ', ' '.join(gtxt)).strip()
                if not txt:
                    continue
                r = cjk_ratio(txt)
                is_en = r < 0.25
                if PASSAGE_STOP.search(txt):
                    in_passage = False
                    continue
                if not in_passage:
                    if is_en and (PAGE_ENTER.match(txt)
                                  or (CIRC_RE.search(txt) and len(txt) > 25)):
                        in_passage = True
                    else:
                        continue
                if not re.search(r'[A-Za-z一-鿿]', txt):
                    continue
                (ens if is_en else cns).append(txt)
    return ens, cns


def key_sections(year):
    """返回 {'cloze': (start,end), 'partb': (start,end)} 页区间（不含 end）。"""
    doc = key_doc(year)
    n = doc.page_count
    texts = [p.get_text() for p in doc]
    cloze_s = next((i for i, t in enumerate(texts)
                    if re.search(r'第一部分|Use of English', t)), 0)
    cloze_e = next((i for i in range(cloze_s + 1, n)
                    if re.search(r'第二部分|Text\s*1\b|Part\s*A\b', texts[i])), cloze_s + 1)
    # Part B：在后半本里找（排除写作 Part B——其后紧跟 Directions+essay 提示）
    pb_s = None
    for i in range(cloze_e, n):
        t = texts[i]
        if re.search(r'Part\s*B\b', t) and not re.search(r'essay|图画|作文', t[:2000]):
            pb_s = i
            break
    pb_e = next((i for i in range(pb_s + 1, n)
                 if re.search(r'Part\s*C\b|第三部分|写作|翻译', texts[i])), n) if pb_s is not None else None
    return {'cloze': (cloze_s, cloze_e), 'partb': (pb_s, pb_e)}


# 个别年份版面错位/标记丢失的手工兜底：【年份】【题号】= 完整选项表
OPT_FIX = {
    2023: {13: {'A': 'with regard to', 'B': 'in spite of', 'C': 'as well as', 'D': 'in line with'},
           12: {'A': 'heritage', 'B': 'revival', 'C': 'exchange', 'D': 'status'}},
}

TRAIL_JUNK = re.compile(r'(?:\s*[\[\(（【J]{1,2})+$')
TRAIL_QNUM = re.compile(r'\s*\d{1,2}\s*[.．、]?\s*$')


def _clean_opt_tail(s):
    s = TRAIL_JUNK.sub('', s)
    s = TRAIL_QNUM.sub('', s)
    return re.sub(r'\s+', ' ', s).strip(' 　;，,、')


def _split_options(chunk):
    """在一个题干块里按 A/B/C/D 标记切出四个选项。"""
    marks = []
    for m in OPT_MARK.finditer(chunk):
        k = m.group(1) or m.group(2)
        # 只接受 A→B→C→D 顺序推进，避免正文里的 A./B. 误判
        if marks and (ord(k) != ord(marks[-1][0]) + 1):
            continue
        if marks and marks[-1][0] == k:
            continue
        if not marks and k != 'A':
            continue
        marks.append((k, m.start(), m.end()))
    if len(marks) != 4:
        return None
    out = {}
    for i, (k, s, e) in enumerate(marks):
        end = marks[i + 1][1] if i + 1 < len(marks) else len(chunk)
        out[k] = _clean_opt_tail(chunk[e:end])
    return out


def cloze_options(year):
    """{题号: {A:.., B:.., C:.., D:..}}  支持 [A] / A. / (A) 等多种标记与四栏排版。"""
    pages = exam_pages(year)
    loc = locate_cloze(pages)
    if not loc:
        return {}
    sp, op = loc
    if op is None:
        return {}
    area = []
    for i in range(op, min(op + 2, len(pages))):
        for x in pages[i]:
            if re.match(r'^Section\s+I?I\b', x) or re.match(r'^Text\s+1\b', x):
                area.append('\n@@END@@\n')
                break
            area.append(x)
        if '\n@@END@@\n' in area:
            break
    text = _norm_area('\n'.join(a for a in area if a != '\n@@END@@\n'))
    chunks = []
    pos = []
    for m in OPT_QNUM.finditer(text):
        pos.append((int(m.group(1)), m.end()))
    pos = [(n, e) for i, (n, e) in enumerate(pos) if i == 0 or n != pos[i - 1][0]]
    for i, (n, e) in enumerate(pos):
        end = pos[i + 1][1] if i + 1 < len(pos) else len(text)
        seg = text[e:end]
        # 截到下一段起量（避免把下一题干吞进来）
        chunks.append((n, seg))
    res = {}
    for n, seg in chunks:
        # 去掉下一题号的干扰：块内不应再出现 "数字."；有则截断
        seg = re.split(r'(?:^|\s)\d{1,2}\s*[.．、]\s*(?=[\[\(（【A-D])', seg)[0]
        opts = _split_options(seg)
        if opts:
            res[n] = {k: v.strip().rstrip(' 　[(（【J') for k, v in opts.items()}
    for n, tbl in OPT_FIX.get(year, {}).items():
        res[n] = dict(tbl)
    return res


# ---------------------------------------------------------------- 句子切分与对齐
import difflib
import unicodedata

ROMAN_RE = re.compile(r'^(?:[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]+|I{1,3}|IV|V|VI{0,2}|IX|X)$')


CIRC_SPLIT = re.compile('([①-⑳❶-❿⓵-⓾⑴-⑽©])')
SENTINEL_S = chr(1)
SENTINEL_P = chr(2)


def _tokenize(s, line_mode=False):
    out = []
    for ln in s.split(chr(10)):
        toks = CIRC_SPLIT.sub(r' \1 ', ln).split()
        for j, tok in enumerate(toks):
            if line_mode and j == 0:
                core = tok.strip('.,;:!?()[]')
                if ROMAN_RE.match(core) and len(core) <= 4:
                    out.append(SENTINEL_P)
                    rest = tok[len(core):] if tok != core else ''
                    if rest:
                        out.append(rest)
                    continue
            m = re.fullmatch(r'([\W]*)([①-⑳❶-❿⓵-⓾⑴-⑽©])([\W]*)', tok)
            if m and (_circ_val(m.group(2)) or 0):
                out.append(SENTINEL_S + '%d' % (_circ_val(m.group(2)) or 0))
                if m.group(1):
                    out.append(m.group(1))
                if m.group(3):
                    out.append(m.group(3))
                continue
            out.append(tok)
    return out


def _tnorm(t):
    if t.startswith('\x01') or t.startswith('\x02'):
        return t
    return re.sub(r'[^a-z0-9]', '', t.lower())


def _repair_bounds(sents):
    """对齐切分可能把句尾词划到下一句：若前句无句末标点而后句开头带句号，则把边界右移。"""
    out = list(sents)
    k = 0
    while k < len(out) - 1:
        a, b = out[k], out[k + 1]
        if a and b and not re.search(r'[.!?]["”’)\]]*$', a) and re.match(r'^[^.!?]{1,40}?[.!?]["”’)\]]*\s', b + ' '):
            m = re.match(r'^(.*?[.!?]["”’)\]]*)\s', b + ' ')
            if m and len(m.group(1).split()) <= 6:
                out[k] = (a + ' ' + m.group(1)).strip()
                out[k + 1] = b[m.end(1):].strip()
                continue
        k += 1
    return out


def align_sentences(exam_text, key_text):
    """用解析左栏的圈号句号切真题正文。

    返回 (sents, para_of)：sents 为真题正文按句切分（保留 [n] 标记），para_of 为段号（1 起）。
    """
    A = _tokenize(key_text, line_mode=True)
    B = _tokenize(exam_text)
    an = [_tnorm(t) for t in A]
    bn = [_tnorm(t) for t in B]
    sm = difflib.SequenceMatcher(None, an, bn, autojunk=False)
    a2b = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            a2b[blk.a + k] = blk.b + k
    # 解析侧：句边界 = 圈号哨兵；段号 = 罗马段号或圈号==1 时重开
    cuts, para_of_cut = [], []
    p = 1
    for i, t in enumerate(A):
        if t.startswith(''):
            cuts.append(i)
            para_of_cut.append(p)
        elif t.startswith(''):
            p += 1 if cuts else 0
    bcuts, last = [], 0
    for a_idx in cuts:
        b_idx = None
        for d in range(0, 15):
            for cand in (a_idx + d, a_idx - d):
                if cand in a2b and a2b[cand] >= last:
                    b_idx = a2b[cand]
                    break
            if b_idx is not None:
                break
        if b_idx is None:
            b_idx = last
        bcuts.append(b_idx)
        last = b_idx
    sents, p_of, prev = [], [], 0
    for k, b in enumerate(bcuts):
        end = b if b > prev else prev
        seg = ' '.join(B[prev:end]).strip()
        if seg:
            sents.append(seg)
            p_of.append(para_of_cut[k])
        prev = max(prev, end)
    tail = ' '.join(B[prev:]).strip()
    if tail:
        sents.append(tail)
        p_of.append(para_of_cut[-1] if para_of_cut else 1)
    sents = _repair_bounds(sents)
    return sents, p_of


def split_cn_sentences(cn_text):
    """按圈号切解析中文列；返回 (sents, para_of)。段号以圈号==1 重开。"""
    toks = _tokenize(cn_text)
    sents, p_of, cur, p = [], [], [], 1
    for t in toks:
        if t.startswith('\x01'):
            v = int(t[1:])
            if cur:
                sents.append(''.join(cur))
                p_of.append(p)
            cur = []
            if v == 1:
                p += 1 if sents else 0
        else:
            cur.append(t)
    if cur:
        sents.append(''.join(cur))
        p_of.append(p)
    # 清理：去 CJK 间空格与噪声
    out = []
    for s in sents:
        s = re.sub(r'(?<=[一-鿿])\s+(?=[一-鿿])', '', s)
        s = re.sub(r'\s+', ' ', s).strip()
        out.append(s)
    return out, p_of
