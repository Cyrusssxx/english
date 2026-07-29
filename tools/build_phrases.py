# -*- coding: utf-8 -*-
"""
从「英（二）2014-2024 真题词组-背诵版.pdf」构建：
  1) pwa/data/phrases.json    —— 精读页词组自动高亮用（扁平映射 + maxWords）
  2) pwa/data/deck_phrases.json —— 内置「真题词组」词书（含例句，供背诵）

PDF 为窄多列表格（序号 | 短语 | 中文含义 | 例句）。三大解析难点：
  - 短语/含义/例句常跨行折断；
  - 含义首行的 y 常略高于行首序号（内容顶对齐）；
  - 例句较长，会“溢出”到下一行序号的 y 带以下。
故采用【文本块 block + 按 x 分列 + 按序号锚点就近归属】重建：
  * PyMuPDF 把每条例句、每块含义分别归为独立 block，block 整体不跨条错位；
  * 按 x 把词分到 短语(<190) / 含义(190~259) / 例句(>=259) 三列，
    即便“含义”与“例句”在同一基线被粘连成一个 token，也按字符脚本(中/英)拆开；
  * 每个 block 以其最小 y 就近归属到“行首序号”锚点（允许内容比序号高出 TOL 像素），
    跨页续行则归属到上一页最后一条 —— 从而修复溢出与跨页错位。

释义/例句 100% 照抄 PDF，无 AI 生成。对高亮词典(phrases.json)额外做严格校验：
凡含义夹带英文单词、为空或过长者一律丢弃（宁可漏收，绝不展示错误释义）。
年份题库里的人工词组随后在合并步骤并入。

运行：python -X utf8 tools/build_phrases.py
"""
import glob
import json
import os
import re

import fitz  # PyMuPDF

PDF_PATH = r"e:\夸克\Download\英（二）2014-2024年真题词组-背诵版.pdf"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')
PHRASES_OUT = os.path.join(DATA_DIR, 'phrases.json')
DECK_OUT = os.path.join(DATA_DIR, 'deck_phrases.json')
VERSION = 'en2-v9'

NUM_X = 92        # 行首序号列右界（序号 x0≈74~86，短语从 97 起）
MID_X = 190       # 短语列 / 含义列 分界（短语 x0≤177，含义 x0≥196）
RIGHT_X = 259     # 含义列 / 例句列 分界（含义 x0≤256，例句 x0≥261）
HEADER_Y = 62     # 页眉（公众号/页码）以上丢弃
FOOTER_Y = 775    # 页脚页码（y≈781）以下丢弃；末行词条 y1≈762 须保留
CONT_GAP = 22     # 页顶“续行”判定：比首个序号高出超过此值者归上一页最后一条
BLOCK_GAP = 20    # 列内聚块阈值：同条相邻行间距≈15.6px，跨条间距≥25px，取 20 可分

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
NUM_RE = re.compile(r'^\d{1,2}$')
LATIN_WORD_RE = re.compile(r'[A-Za-z]{3,}')
PLACEHOLDERS = {'A', 'B', 'sb', 'sth', 'sb.', 'sth.', 'sth,', 'o.s.'}
HEADER_TOKENS = {'编', '号', '短语', '含义', '例句', '编号'}


def has_cjk(s):
    return bool(CJK_RE.search(s))


def is_cjk_char(ch):
    return bool(CJK_RE.match(ch)) or ('\u3000' <= ch <= '\u303f') or ('\uff00' <= ch <= '\uffef')


def split_runs(text):
    """把一个 token 拆成 (kind, substr) 序列，kind ∈ {'cjk','latin'}；
    标点/空格/数字并入当前 run（无当前 run 时并入下一个字母 run）。"""
    runs = []
    cur_kind = None
    buf = ''
    for ch in text:
        if is_cjk_char(ch):
            k = 'cjk'
        elif ch.isascii() and ch.isalpha():
            k = 'latin'
        else:
            k = None  # 标点/数字/空格
        if k is None:
            buf += ch
            continue
        if cur_kind is None:
            cur_kind = k
            buf += ch
        elif k == cur_kind:
            buf += ch
        else:
            runs.append((cur_kind, buf))
            buf = ch
            cur_kind = k
    if buf:
        runs.append((cur_kind or 'latin', buf))
    return runs


def new_entry(num):
    return {'num': num, 'phrase_words': [], 'meaning_parts': [],
            'en_words': [], 'cn_parts': []}


def bucket_word(e, w):
    """把一个词按所在列与字符脚本归入 短语/含义/例句(英)/例句(中)。"""
    x0 = w[0]
    text = w[4]
    if x0 < MID_X:                     # 短语列（含左侧非序号残留）
        e['phrase_words'].append(text)
        return
    if x0 < RIGHT_X:                   # 含义列（纯中文；夹带的拉丁文为例句起始被粘连到同一 token，归例句）
        for kind, run in split_runs(text):
            if kind == 'cjk':
                e['meaning_parts'].append(run)
            else:
                s = run.strip()
                if s:
                    e['en_words'].append(s)
        return
    # 例句列
    for kind, run in split_runs(text):
        if kind == 'cjk':
            e['cn_parts'].append(run)
        else:
            s = run.strip()
            if s:
                e['en_words'].append(s)


def is_noise_token(t):
    """页眉/年份标题/表头列名等噪声词，直接丢弃。"""
    if '公众号' in t or '晶婷' in t:
        return True
    if t in HEADER_TOKENS:
        return True
    if re.fullmatch(r'20\d\d', t):            # 年份标题 2014/2015...
        return True
    if '英语二' in t or '——' in t or '年—' in t:
        return True
    return False


def parse_pdf():
    doc = fitz.open(PDF_PATH)
    entries = []
    prev_entry = None
    for page in doc:
        words = [w for w in page.get_text('words')
                 if HEADER_Y <= w[1] and w[3] <= FOOTER_Y and not is_noise_token(w[4])]
        if not words:
            continue
        anchors = sorted([w for w in words if w[0] < NUM_X and NUM_RE.match(w[4])],
                         key=lambda w: w[1])
        if not anchors:
            # 整页皆为上一条的续行（极少见）
            if prev_entry is not None:
                for w in sorted(words, key=lambda w: (round(w[1]), w[0])):
                    bucket_word(prev_entry, w)
            continue
        page_entries = [new_entry(int(a[4])) for a in anchors]
        # 序号在变高行内大致居中；同一条的多行内容(含义/例句)整体也居中于该行，
        # 故其“块中心”与序号中心对齐。逐词就近会把多行含义切碎到相邻条目，
        # 因此改为：列内先按行距聚块，再以块中心就近归属到序号锚点。
        anchor_cy = [(a[1] + a[3]) / 2.0 for a in anchors]
        anchor_ids = {id(a) for a in anchors}
        first_ay = anchors[0][1]

        def nearest_entry(cy):
            best_i = 0
            best_d = abs(cy - anchor_cy[0])
            for i in range(1, len(anchor_cy)):
                d = abs(cy - anchor_cy[i])
                if d < best_d:
                    best_d = d
                    best_i = i
            return page_entries[best_i]

        content = [w for w in words if id(w) not in anchor_ids]
        refs = []  # (cy, target_entry)：已正确归属的短语/含义块，供例句就近参照
        # 短语/含义列：列内按行距聚块，以块中心就近归属（避免多行含义被逐词切碎）。
        for col_lo, col_hi in ((-1, MID_X), (MID_X, RIGHT_X)):
            col = sorted([w for w in content if col_lo <= w[0] < col_hi],
                         key=lambda w: (w[1], w[0]))
            if not col:
                continue
            blocks = [[col[0]]]
            for w in col[1:]:
                if w[1] - blocks[-1][-1][1] > BLOCK_GAP:
                    blocks.append([w])
                else:
                    blocks[-1].append(w)
            for blk in blocks:
                cy = sum((w[1] + w[3]) / 2.0 for w in blk) / len(blk)
                if cy < first_ay - CONT_GAP and prev_entry is not None:
                    target = prev_entry        # 页顶跨页续行
                else:
                    target = nearest_entry(cy)
                refs.append((cy, target))
                for w in sorted(blk, key=lambda w: (round(w[1]), w[0])):
                    bucket_word(target, w)
        # 例句列：多行连续、跨条无垂直间隔，聚块会把多条例句并成一块；
        # 且序号垂直居中会使本条例句高于其序号。故将例句逐词归属到
        # “最近的已定位短语/含义块”所属条目（短语/含义已正确归属，比就近序号可靠）。
        refs.sort()
        for w in sorted([x for x in content if x[0] >= RIGHT_X],
                        key=lambda w: (round(w[1]), w[0])):
            ecy = (w[1] + w[3]) / 2.0
            if refs:
                target = min(refs, key=lambda r: abs(r[0] - ecy))[1]
            else:
                target = nearest_entry(ecy)
            bucket_word(target, w)
        entries.extend(page_entries)
        prev_entry = page_entries[-1]

    # 收尾成 {phrase, meaning, ex_en, ex_cn}
    out = []
    for e in entries:
        phrase = re.sub(r'\s+', ' ', ' '.join(e['phrase_words'])).strip()
        meaning = ''.join(e['meaning_parts']).strip()
        ex_en = re.sub(r'\s+', ' ', ' '.join(e['en_words'])).strip()
        ex_cn = ''.join(e['cn_parts']).strip()
        if phrase:
            out.append({'phrase': phrase, 'meaning': meaning,
                        'ex_en': ex_en, 'ex_cn': ex_cn})
    return out


def norm_key(phrase):
    return re.sub(r'\s+', ' ', phrase.lower()).strip()


def is_matchable(phrase):
    """可字面匹配：>=2 词、无省略号占位、无 A/B/sb/sth 占位、无中文。"""
    if '...' in phrase or '．' in phrase or '。' in phrase or '…' in phrase:
        return False
    toks = phrase.split()
    if len(toks) < 2:
        return False
    if any(t in PLACEHOLDERS for t in toks):
        return False
    if has_cjk(phrase):
        return False
    return True


def clean_meaning_for_highlight(meaning):
    """高亮词典释义严格校验：非空、含中文、不夹带英文单词、长度合理，否则返回 None。"""
    if not meaning or not has_cjk(meaning):
        return None
    if re.search(r'[A-Za-z]', meaning):  # 任何拉丁字母（含 In/A/B 泄漏）均判为脏数据
        return None
    if len(meaning) > 40:
        return None
    return meaning


def example_looks_clean(en, cn):
    """跨页/跨条续行会把相邻条目的残句、被拆散的数字掺进例句。
    检出这类污染信号则丢弃例句（宁缺勿错），该词条仍保留 word+meaning。"""
    if cn and cn[0] in '。，、；：！？）':      # 中文以句中标点开头 = 上一条残句
        return False
    if re.search(r'(?:^| )\d(?:$| )', en):     # 孤立数字 token（如被拆散的 "1 9"/"3"）
        return False
    return True


def collect_year_phrases():
    """从 16 年题库收集人工标注的多词词组（w 含空格），释义已去「词组：」前缀。"""
    out = {}
    for f in sorted(glob.glob(os.path.join(DATA_DIR, '20*.json'))):
        with open(f, encoding='utf-8') as fp:
            d = json.load(fp)
        for art in d.get('articles', []):
            for s in art.get('sentences', []):
                for w in s.get('words', []) or []:
                    ww = (w.get('w') or '').strip()
                    if ' ' not in ww:
                        continue
                    key = norm_key(ww)
                    mean = (w.get('meaning') or '').strip()
                    if key and mean and is_matchable(ww):
                        out[key] = mean  # 后出现覆盖，语境释义均可
    return out


def main():
    entries = parse_pdf()
    print(f'PDF 解析：{len(entries)} 条词条')

    # 词书（全部词条，含模板/单词，供背诵）；例句仅在看起来完整时保留
    seen = set()
    deck_words = []
    for e in entries:
        key = norm_key(e['phrase'])
        if not key or key in seen or not e['meaning']:
            continue
        seen.add(key)
        item = {'word': key, 'meaning': e['meaning']}
        if example_looks_clean(e['ex_en'], e['ex_cn']):
            if e['ex_en']:
                item['example_en'] = e['ex_en']
            if e['ex_cn']:
                item['example_cn'] = e['ex_cn']
        deck_words.append(item)
    deck = {'name': '真题词组（英语二2014-2024）', 'words': deck_words}
    with open(DECK_OUT, 'w', encoding='utf-8') as fp:
        json.dump(deck, fp, ensure_ascii=False)
    print(f'deck_phrases.json：{len(deck_words)} 词条')

    # 高亮词典：PDF 可匹配且释义纯净的词组 + 年份题库人工词组（题库优先）
    pdf_phrases = {}
    for e in entries:
        if not is_matchable(e['phrase']):
            continue
        m = clean_meaning_for_highlight(e['meaning'])
        if m:
            pdf_phrases[norm_key(e['phrase'])] = m
    phrases = dict(pdf_phrases)
    ymap = collect_year_phrases()
    phrases.update(ymap)  # 题库语境释义覆盖 PDF 通用释义
    pdf_only = len(set(pdf_phrases) - set(ymap))
    max_words = max((len(k.split()) for k in phrases), default=0)
    out = {'version': VERSION, 'maxWords': max_words, 'phrases': phrases}
    with open(PHRASES_OUT, 'w', encoding='utf-8') as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(PHRASES_OUT)
    print(f'phrases.json：{len(phrases)} 词组（PDF净收 {len(pdf_phrases)}，其中PDF独有 {pdf_only}；'
          f'题库 {len(ymap)}），maxWords={max_words}，体积 {size / 1024:.1f} KB')


if __name__ == '__main__':
    main()
