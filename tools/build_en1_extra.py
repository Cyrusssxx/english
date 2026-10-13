# -*- coding: utf-8 -*-
"""构建英语一近十年（2016-2025）完形填空 + 新题型数据，并入 pwa/data/en1/{year}.json。

阶段一：完形（cloze）。新题型在阶段二补充。
产出先写入 tools/en1_stage/{year}.json 供人工审核，再由 --apply 并入正式数据。

用法：
  python tools/build_en1_extra.py --stage      # 生成/刷新 staging
  python tools/build_en1_extra.py --apply      # 并入 pwa/data/en1/
"""
import argparse, json, os, re, subprocess, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en1_lib import (ClozePassageParas, cloze_options, key_doc, key_sections,
                     passage_streams, norm_brackets, OB, CB, exam_answers)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STAGE = os.path.join(ROOT, 'tools', 'en1_stage')
EN1_DIR = os.path.join(ROOT, 'pwa', 'data', 'en1')

YEARS = list(range(2016, 2026))
# 与 index.html / article.js 的渲染顺序一致
RENDER_ORDER = ['text1', 'text2', 'text3', 'text4', 'newtype', 'cloze',
                'translation', 'writing_a', 'writing_b']

# ---- 每年正文文本的手工修正（OCR 残渣；按 (旧, 新) 顺序替换） ----
TEXT_FIX = {
    2016: [("spouse\" is a", "spouse is a"), ("G ", "")],
    2018: [("fu a Swiss study", "in a Swiss study"),
           ("ħ1Ĩ1ĩ", "Fortunately"),
           ("--=----", "")],
}

# 段落话题概要（写入 article.topic）
TOPIC_FIX = {}


def key_fulltext(year, sec):
    doc = key_doc(year)
    return '\n'.join(doc[i].get_text() for i in range(sec[0], sec[1]))


def cloze_fulltext(year, sec):
    """取完形解析文本；若 1~20 题头没凑齐，自动向后扩页最多 4 页。

    原因：部分年份的分章检测器会把最后一题（通常是第 20 题）的解析页划到下一章，
    导致该题既无选项块也无答案。
    """
    doc = key_doc(year)
    n = doc.page_count
    s, e = sec[0], sec[1]

    def _txt(a, b):
        return '\n'.join(doc[i].get_text() for i in range(a, min(b, n)))

    t = _txt(s, e)
    for _ in range(4):
        if e >= n:
            break
        b = key_blocks(t, 1, 20)
        miss = [q for q in range(1, 21) if q not in b]
        # 最后一题的块过短 = 解析被截在章外，继续向后扩页
        last_short = 20 in b and len(b[20]) < 300
        if not miss and not last_short:
            break
        e += 1
        t = _txt(s, e)
    return t


QBLOCK = re.compile(r'(?:^|\n)\s*(\d{1,2})\s*[.．、]\s*' + OB + r'\s*([A-D])\s*' + CB + '?')


def key_blocks(text, lo, hi):
    """把解析文本切成题块：返回 {题号: 块文本}。"""
    marks = []
    for m in QBLOCK.finditer(text):
        n = int(m.group(1))
        if lo <= n <= hi:
            marks.append((m.start(), n))
    # 去重（同题号取首个）
    seen, ms = set(), []
    for pos, n in marks:
        if n in seen:
            continue
        seen.add(n)
        ms.append((pos, n))
    ms.sort()
    out = {}
    for i, (pos, n) in enumerate(ms):
        end = ms[i + 1][0] if i + 1 < len(ms) else len(text)
        out[n] = text[pos:end]
    return out


ANS_KEYS = ('符合文意', '符合句意', '符合题意', '符合语境', '符合上下文', '符合逻辑',
            '契合文意', '契合句意', '契合', '入选', '为正确答案', '为最佳选项',
            '恰当', '准确', '正确')


def _negated(scope, mm):
    """判断该命中是否处于否定语境（排除「…不符合文意」这类反例）。

    只看紧邻位置：选项标记前 2 字 + 判定关键词前 2 字。用整段/整句扫描会误杀
    「…和 不相上下」，正确。」这类正常表述。
    """
    if re.search(r'[不非难误]', scope[max(0, mm.start() - 2):mm.start()]):
        return True
    w = mm.group(0)
    pos = max(w.rfind(k) for k in ANS_KEYS)
    if pos >= 0 and re.search(r'[不非难误]', w[max(0, pos - 2):pos]):
        return True
    return False

NOTDOT = r'[^。；;]'          # 「这一过程：识别出 A  Carrie H 」——允许逗号，切断句号/分号
OK_WORDS = (r'(?:契合文意|契合句意|契合|符合文意|符合句意|符合题意|符合语境|符合上下文|'
            r'符合逻辑|入选|为正确答案|为最佳选项|恰当|准确)')

ANS_PATS = [
    # 【D】When 表示"当…时"，符合语义逻辑  /  [A] delay 正确
    re.compile(r'[【\[]\s*([A-D])\s*[】\]]' + NOTDOT + r'{0,150}?' + OK_WORDS),
    re.compile(r'[【\[]\s*([A-D])\s*[】\]]' + NOTDOT + r'{0,120}?正确'),
    re.compile(r'(?<![A-Za-z])([A-D])\s*项' + NOTDOT + r'{0,120}?'
               r'(?:' + OK_WORDS + r'|正确)'),
    re.compile(r'【\s*([A-D])\s*】\s*(?:意为' + r'[^，。;；]' + r'{0,30}?)?正确'),
    re.compile(r'(?:故选|应选|故答案为|因此选|综上)\s*[【\[]?\s*([A-D])\s*[】\]]?'),
    re.compile(r'(?<![A-Za-z])([A-D])\s*(?:符合|契合|正确|入选|为正确答案)'),
    re.compile(r'只有\s*[【\[]?\s*([A-D])\s*[】\]]?\s*[^。，；\n]{0,24}'),
]


SCOPE_RE = re.compile(r'[【\[]\s*解题思路\s*[】\]](.*?)'
                      r'(?=[【\[]\s*(?:错项排除|考点提炼)\s*[】\]]|\Z)', re.S)


def _scopes(blk):
    """一个题块里可能有多个【解题思路】（解析册加重影/跨栏，会把别题的内容卷进来），
    全部取出逐个尝试，而不是只认第一个。"""
    nb = re.sub(r'\s+', ' ', norm_brackets(blk))
    return [m.group(1) for m in SCOPE_RE.finditer(nb)] or [nb]


def _mentioned(scope, opts):
    """这一段里实际出现了哪些选项的英文原词。"""
    if not opts:
        return None
    out = []
    for k in 'ABCD':
        w = (opts.get(k) or '').strip(' ])》）.、,，;；')
        if len(w) < 2:
            continue
        if re.search(r'(?<![A-Za-z])' + re.escape(w), scope, re.I):
            out.append(k)
    return out


def _cand(scope):
    cands = []
    for pi, pat in enumerate(ANS_PATS):
        for mm in pat.finditer(scope):
            if _negated(scope, mm):
                continue
            cands.append((pi, mm.start(), mm.group(1)))
    cands.sort()
    return cands[0][2] if cands else None


def detect_answer(block, opts=None):
    """返回检出的答案，或 None。

    三级置信：
      1) 【解题思路】里模式命中的字母，其英文原词在同段也出现 → 最可靠，直接采纳
      2) 同段只出现了一个选项的原词 → 采纳
      3) 都没有 → 退回模式命中的首个结果
    """
    scopes = _scopes(block)
    first_c = None
    for sc in scopes:
        c = _cand(sc)
        if c is None:
            continue
        first_c = first_c or c
        men = _mentioned(sc, opts)
        if men is None:
            return c
        if c in men:
            return c
        if len(men) == 1:
            if first_c == men[0]:
                return men[0]
            continue
    if opts:
        for sc in scopes:
            men = _mentioned(sc, opts)
            if len(men) == 1:
                return men[0]
    return first_c


def _opt_cluster(text, opts, win=320):
    """用「四个选项英文词同时出现」定位该题在解析册里的位置，返回起始下标或 None。

    为什么需要它：个别年份（如 2021）解析册的文本层顺序被打乱，`3. [A]` 这类题头
    根本找不到，但选项行本身必然存在——四个英文选项挤在一起就是最硬的锚点。
    """
    events = []
    for i, k in enumerate('ABCD'):
        w = (opts.get(k) or '').strip()
        if len(w) < 2:
            continue
        for m in re.finditer(r'\b' + re.escape(w), text, re.I):
            events.append((m.start(), i))
    events.sort()
    for i, (p, _i) in enumerate(events):
        seen = {}
        j = i
        while j < len(events) and events[j][0] - p <= win:
            seen.setdefault(events[j][1], events[j][0])
            j += 1
        if len(seen) < 3:
            continue
        tail = max(seen.values()) + 120
        seg = text[p:min(len(text), tail)]
        # 必须同时出现 ≥2 个选项标记（【A】【B】…）才能确认这是选项行而不是正文巧合
        if len(re.findall(r'[【\[]\s*[A-D]\s*[】\]]', seg)) >= 2:
            return p
    return None


def answer_by_options(text, opts):
    """兜底：先按选项行定位，再在其后 3000 字内做常规答案检出。"""
    p = _opt_cluster(text, opts)
    if p is None:
        return None
    return detect_answer(text[p:p + 3000])


def answer_by_unique_option(text, opts):
    """最后的兜底：若解析段里只提到了一个选项的英文原词，那它就是答案。

    用于 OCR 把选项字母打烂的情况（如 2020 第 5 题的「故【八】正」）。
    """
    seg = text
    hit = [k for k in 'ABCD'
           if (opts.get(k) or '').strip()
           and re.search(re.escape(opts[k].strip()), seg, re.I)]
    return hit[0] if len(hit) == 1 else None


def split_opt_cn(rest, en):
    """选项行剩余文本 → 中文释义（剥掉与官方选项重复的英文部分）。"""
    rest = re.sub(r'\s+', ' ', rest).strip()
    en_n = re.sub(r'\s+', ' ', en).strip()
    if rest.lower().startswith(en_n.lower()):
        return rest[len(en_n):].strip(' 　;；,，.。')
    m = re.search(r'[一-鿿]', rest)
    if m:
        return rest[m.start():].strip(' 　;；,，.。')
    return ''


ABBREV = {'mr', 'mrs', 'ms', 'dr', 'prof', 'st', 'vs', 'etc', 'e.g', 'i.e',
          'no', 'fig', 'u.s', 'u.k', 'a.m', 'p.m', 'jr', 'sr', 'inc', 'ltd',
          'co', 'corp', 'approx', 'dept', 'univ'}
SENT_SPLIT = re.compile(r'(?<=[.!?])["”’)\]]?\s+(?=["“(\[]?[A-Z0-9])')

# 真题册为扫描件的年份：文本层会在空位前插入伪句点（"invented six years. [4] by"）
SCANNED_YEARS = {2024, 2025}
FAKE_DOT = re.compile(r'\.\s*\[(\d+)\]\s+(?=[a-z])')
# 盗版解析册水印：乱码汉字 + VX/微信号 + 字母数字串
WM_RE = re.compile(r'[^。；\s]{0,10}(?:VX|vx|微信)[・·\-—:：]?[A-Za-z0-9]{4,}')


def split_sentences(para):
    """按英文句界切句；保护缩写、人名首字母与 [n] 空标记，避免误切。

    2024/2025 的真题 PDF 是扫描件，文本层会在空位前插入伪句点（"invented six
    years. [4] by Americans"），切完后再按「下一句以小写词开头」把它们接回去。
    """
    parts = SENT_SPLIT.split(para)
    out, buf = [], ''
    for p in parts:
        buf = (buf + ' ' + p).strip() if buf else p
        if not buf:
            continue
        tail = re.split(r'\s+', buf)[-1].strip('.,;:!?').lower()
        if tail in ABBREV or (len(tail) == 1 and tail.isalpha()):
            continue
        if re.search(r'\[\d+\]$', buf):
            continue
        out.append(buf)
        buf = ''
    if buf:
        out.append(buf)
    out = [re.sub(r'\s+', ' ', s).strip() for s in out if s.strip()]
    return _merge_fragments(out)


def _merge_fragments(sents):
    """修掉扫描件文本层造成的碎片。

    2024/2025 真题册是扫描件，空位前会被插入伪句点，切出 "They." / "chosen to."
    这类 1~4 词的残句。判据：真完形句子几乎不可能这么短 → 向前合并并去掉伪句点。
    """
    out = []
    i = 0
    while i < len(sents):
        s = sents[i]
        nxt = sents[i + 1] if i + 1 < len(sents) else None
        if nxt is not None and len(s.split()) <= 4:
            body = re.sub(r'[.]+$', '', s).strip()
            sents[i + 1] = (body + ' ' + nxt).strip()
            i += 1
            continue
        if out and not re.match(r'^[\["“(\[]?[A-Z0-9]', s) and not s.startswith('['):
            out[-1] = out[-1] + ' ' + s              # 以小写词开头 = 上一句被伪句点截断
            i += 1
            continue
        out.append(s)
        i += 1
    return out


def extract_expl(blk, full='', opts=None):
    """从题块里取「考点提炼 + 解题思路 + 错项排除」整段解析。

    截断条件：下一题的题头（QBLOCK）或「词汇注释」小节。
    起点优先【考点提炼】，缺失时退回【解题思路】；两种括号风格都要认。
    """
    blk = norm_brackets(blk) if blk else ''   # ［考点提炼］/（考点提炼）等变体统一成【】式
    m = re.search(r'[【\[]\s*(?:考点提炼|解题思路)\s*[】\]]', blk) if blk else None
    if m:
        rest = blk[m.end():]
        end = None
        mm = QBLOCK.search(rest)
        if mm:
            end = mm.start()
        m2 = re.search(r'[【\[]\s*词汇注释\s*[】\]]', rest)
        if m2 and (end is None or m2.start() < end):
            end = m2.start()
        seg = rest[:end] if end is not None else rest
    else:
        seg = ''
    # 兜底：题块缺失（解析册文本层顺序错乱）时，用「四个选项词同时出现」定位
    if not seg.strip() and opts:
        p = _opt_cluster(full, opts)
        if p is not None:
            seg = full[p:p + 3000]
            m3 = re.search(r'[【\[]\s*(?:考点提炼|解题思路)\s*[】\]]', seg)
            if m3:
                seg = seg[m3.end():]
    return seg[:EXPL_MAX]


EXPL_MAX = 2200


def build_cloze(year):
    opts = cloze_options(year)
    paras, _marks = ClozePassageParas(year)
    for a, b in TEXT_FIX.get(year, []):
        paras = [p.replace(a, b) for p in paras]
    sec = key_sections(year)['cloze']
    full = cloze_fulltext(year, sec)
    blocks = key_blocks(full, 1, 20)
    exam_ans = exam_answers(year)

    # ---- 句子切分：用普通英文句界切分，不再依赖解析册逐句对齐 ----
    if year in SCANNED_YEARS:
        paras = [FAKE_DOT.sub(r' [\1] ', p) for p in paras]
    sentences = []
    for pi, para in enumerate(paras, start=1):
        for s in split_sentences(para):
            sentences.append({'para': pi, 'en': s.strip()})
    sids = ['en1_%d_cloze_s%02d' % (year, i + 1) for i in range(len(sentences))]
    for i, s in enumerate(sentences):
        s['id'] = sids[i]
        s['cn'] = ''
        s['words'] = []
    # 每道题的定位句 = 含该空 [n] 的句子
    blank_of = {}
    for i, s in enumerate(sentences):
        for m in re.finditer(r'\[(\d+)\]', s['en']):
            blank_of.setdefault(int(m.group(1)), []).append(sids[i])
    warn = []

    questions = []
    for n in range(1, 21):
        o = opts.get(n)
        if not o or len(o) != 4:
            warn.append('q%d 选项缺失' % n)
            continue
        blk = norm_brackets(blocks.get(n, ''))
        oc = {}
        for k, v in o.items():
            mm = re.search(r'(?:【|\[)\s*%s\s*(?:】|\])\s*([^\n【\[]*)' % k, blk)
            oc[k] = split_opt_cn(mm.group(1), v) if mm else ''
        ans = detect_answer(blk, o)
        if not ans:                                   # 题块号错乱 / 解析册无文本层
            ans = answer_by_options(full, o) or exam_ans.get(n)
        if not ans:
            warn.append('q%d 答案未检出' % n)
        expl = extract_expl(blocks.get(n, ''), full, o)
        expl = re.sub(r'\s+', '', expl)
        # 盗版解析册混进来的水印文字（如 "空酉己查音学正VX・K7R72C11"）
        expl = WM_RE.sub('', expl)
        # 章节标签统一成【】式（解析册里 【】/[]/【】 三种混用）
        expl = re.sub(r'[【\[]\s*(考点提炼|解题思路|错项排除|词汇注释|难句分析)\s*[】\]]',
                      r'【\1】', expl)
        questions.append({
            'id': 'en1_%d_cloze_q%02d' % (year, n),
            'number': str(n),
            'qtype': '完形',
            'stem': '第 %d 空：选择最合适的词填入空白 [%d]' % (n, n),
            'stem_cn': '',
            'options': o,
            'options_cn': oc,
            'answer': ans,
            'explanation': expl,
            'related_sentences': blank_of.get(n) or sids[:1],
        })
    art = {
        'id': 'en1_%d_cloze' % year,
        'type': 'cloze',
        'title': '',
        'topic': TOPIC_FIX.get(year, ''),
        'source': 'Section I Use of English',
        'sentences': sentences,
        'questions': questions,
    }
    return art, warn


def apply_year(year, arts):
    """把 staging 里的 cloze/newtype 并入 pwa/data/en1/{year}.json。

    规则：保持 text1-4 原样不动，新条目按 render 顺序插入；已有同类型条目则替换。
    """
    fp = os.path.join(EN1_DIR, '%d.json' % year)
    d = json.load(open(fp, encoding='utf-8'))
    existing = {a['type']: a for a in d.get('articles', [])}
    for t, art in arts.items():
        existing[t] = art
    d['articles'] = sorted(existing.values(),
                           key=lambda a: RENDER_ORDER.index(a['type'])
                           if a['type'] in RENDER_ORDER else 99)
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return [a['type'] for a in d['articles']]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--years', type=str, default='')
    args = ap.parse_args()
    years = [int(x) for x in args.years.split(',')] if args.years else YEARS
    os.makedirs(STAGE, exist_ok=True)
    for y in years:
        art, warn = build_cloze(y)
        fp = os.path.join(STAGE, '%d.json' % y)
        data = {}
        if os.path.exists(fp):
            data = json.load(open(fp, encoding='utf-8'))
        data['cloze'] = art
        if args.apply:
            types = apply_year(y, {'cloze': art})
            print('%d APPLIED cloze: sents=%d questions=%d -> %s'
                  % (y, len(art['sentences']), len(art['questions']), types))
        else:
            json.dump(data, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print('%d cloze: sents=%d questions=%d ans_missing=%s %s'
                  % (y, len(art['sentences']), len(art['questions']),
                     [q['number'] for q in art['questions'] if not q['answer']], warn))
    if args.apply:
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build_en1_index.py')],
                       check=True)


if __name__ == '__main__':
    main()
