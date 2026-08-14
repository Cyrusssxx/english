#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""考研英语真题 -> 结构化 JSON 抽取管线（英语二 2007-2009 / 英语一 2010-2025 阅读）。

设计：
- 英文篇章 + 题目（题干/选项）从「真题 PDF」抽取（文本层干净）。
- 中文译文 + 答案 + 解析从「解析 PDF」抽取（译文区中文干净，按句序与英文配对）。
- 仅取阅读 Text1-4（英语一阅读专项；英语二 2007-2009 也先以阅读为主）。

用法：
  python import_exam.py --exam en2 --year 2007 --dry
  python import_exam.py --exam en1 --year 2010 --out pwa/data/en1/2010.json --dry
  python import_exam.py --exam en1 --all          # 2010-2025 全量
"""
import os
import re
import sys
import json
import glob
import argparse
import pymupdf

SRC = r"D:\ai code\英语考研试题和答案"

# ---------- 选项字母括号（兼容 ASCII / 全角 / 方圆括号 / OCR 乱码 J） ----------
OPT_LEAD = r"[\[【［「『]"
OPT_TRAIL = r"[\]\】」J』］]"
OPT_BR = re.compile(OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?")

def seg_answer(seg):
    """段内找「正确选项」标记，返回字母。兼容 [C]正确 / ［DJ 为正确答案 / C 正确 / A 项正确。"""
    # 模式1：[X]正确（字母紧贴正确）
    m = re.search(OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?\s*正确", seg)
    if m:
        return m.group(1)
    # 模式2：[X]...为正确答案
    m = re.search(OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?[\s\S]{0,50}?为正确答案", seg)
    if m:
        return m.group(1)
    # 模式3：裸字母 + 正确（如 "C 正确。" / "A 项正确。"）
    m = re.search(r"(?<![A-Za-z])([A-D])\s*项正确|(?<![A-Za-z])([A-D])\s*正确", seg)
    if m:
        return m.group(1) or m.group(2)
    # 模式4：符合文义 / 符合文意
    m = re.search(OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?\s*符合文[义意]", seg)
    if m:
        return m.group(1)
    # 模式5：正确项[X] / 正确项 [X]
    m = re.search(r"正确项\s*" + OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?", seg)
    if m:
        return m.group(1)
    # 模式6：[X]...正确项
    m = re.search(OPT_LEAD + r"\s*([A-D])\s*" + OPT_TRAIL + r"?[\s\S]{0,30}?正确项", seg)
    if m:
        return m.group(1)
    return None

# ---------- 文本清洗 ----------
FOOTER_RE = re.compile(r"英语试题\s*\.\s*\d+\s*\.\s*\(共\s*\d+\s*页\)")
NOISE_RE = re.compile(r"^\s*〔?[\d一二三四五六七八九十]+[〕)．.]\s*$")  # 孤立页码/标记

CJK = re.compile(r"[一-鿿]")


def pdf_full_text(path):
    d = pymupdf.open(path)
    return "\n".join(pg.get_text() for pg in d)


def clean(t):
    t = FOOTER_RE.sub("\n", t)
    return t


def cjk_ratio(s):
    if not s.strip():
        return 0
    c = len(CJK.findall(s))
    return c / max(1, len(re.findall(r"[一-鿿A-Za-z0-9]", s)))


# ---------- 真题：阅读篇章 + 题目 ----------
def split_paragraphs(passage):
    """按空行/孤立换行切段落，返回 [{para, text}]。"""
    blocks = re.split(r"\n\s*\n", passage.strip())
    out = []
    for i, b in enumerate(blocks):
        b = b.strip()
        if not b:
            continue
        out.append((len(out) + 1, b))
    return out


def split_sentences(para_text):
    """段内断句：以 .?! 后接空白+大写 为边界；保留原顺序。"""
    # 保护常见缩写，避免误断
    txt = para_text.strip()
    # 先按标点断（句末标点后跟空格+大写字母）
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", txt)
    sents = []
    for p in parts:
        p = p.strip()
        if p:
            sents.append(p)
    return sents


def parse_reading_from_real(real_text):
    """real_text: 真题 PDF 全文。返回 {textN: {en_passage, questions:[...]}}"""
    # 定位所有 Text N 起点（去重：跳过连续同号的重复标记）
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r"(?<![A-Za-z])Text\s*(\d)", real_text, re.I)]
    starts = []
    for pos, n in marks:
        if starts and starts[-1][1] == n:
            continue
        starts.append((pos, n))
    if not starts:
        return {}
    blocks = {}
    for idx, (pos, n) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(real_text)
        blk = real_text[pos:end]
        blk = re.sub(r"^.*?Text\s*\d\s*", "", blk, count=1, flags=re.S | re.I).strip()
        blocks[n] = blk
    result = {}
    # 选项括号兼容：ASCII [ ] / 全角 ［ ］ / 方圆 【 】 / OCR 乱码 J；括号与字母间允许空格
    OPT_OPEN = r"[\[【［「『]"
    OPT_CLOSE = r"[\]\】」J』』\]]"
    O = lambda L: OPT_OPEN + r"\s*" + L + r"\s*" + OPT_CLOSE
    qpat = re.compile(
        r"(\d{1,2})\.\s+(?P<stem>.+?)\s*"
        + O("A") + r"\s*(?P<A>.+?)\s*"
        + O("B") + r"\s*(?P<B>.+?)\s*"
        + O("C") + r"\s*(?P<C>.+?)\s*"
        + O("D") + r"\s*(?P<D>.+?)(?=\n\s*\d{1,2}\.\s|\Z)",
        re.S,
    )
    for n, blk in blocks.items():
        # 第一个阅读题号（21-40）之前是篇章
        mq = re.search(r"\n\s*(?:2[1-9]|3[0-9]|40)\.\s", blk)
        if mq:
            passage = blk[: mq.start()]
            qblock = blk[mq.start():]
        else:
            passage = blk
            qblock = ""
        # 篇章断句
        sents = []
        sid = 0
        for para, ptxt in split_paragraphs(passage):
            for s in split_sentences(ptxt):
                sid += 1
                sents.append({"para": para, "en": s})
        # 题目
        qs = []
        for qm in qpat.finditer(qblock):
            opts = {
                "A": re.sub(r"\s+", " ", qm.group("A").strip()),
                "B": re.sub(r"\s+", " ", qm.group("B").strip()),
                "C": re.sub(r"\s+", " ", qm.group("C").strip()),
                "D": re.sub(r"\s+", " ", qm.group("D").strip()),
            }
            qs.append(
                {
                    "number": int(qm.group(1)),
                    "stem": re.sub(r"\s+", " ", qm.group("stem").strip()),
                    "options": opts,
                }
            )
        result[n] = {"sents": sents, "questions": qs}
    return result


def parse_questions_global(real_text):
    """从整本真题抽取全部阅读题（题号 21-40），按题号范围归到 Text1-4。
    与篇章切块解耦，避免部分年份题目集中在文末导致漏抽。"""
    OPT_OPEN = r"[\[【［「『]"
    OPT_CLOSE = r"[\]\】」J』』\]]"
    O = lambda L: OPT_OPEN + r"\s*" + L + r"\s*" + OPT_CLOSE
    qpat = re.compile(
        r"(\d{1,2})\.\s+(?P<stem>.+?)\s*"
        + O("A") + r"\s*(?P<A>.+?)\s*"
        + O("B") + r"\s*(?P<B>.+?)\s*"
        + O("C") + r"\s*(?P<C>.+?)\s*"
        + O("D") + r"\s*(?P<D>.+?)(?=\n\s*\d{1,2}\.\s|\Z)",
        re.S,
    )
    out = {1: [], 2: [], 3: [], 4: []}
    for m in qpat.finditer(real_text):
        num = int(m.group(1))
        if 21 <= num <= 40:
            tno = (num - 21) // 5 + 1
            out[tno].append({
                "number": num,
                "stem": re.sub(r"\s+", " ", m.group("stem").strip()),
                "options": {
                    "A": re.sub(r"\s+", " ", m.group("A").strip()),
                    "B": re.sub(r"\s+", " ", m.group("B").strip()),
                    "C": re.sub(r"\s+", " ", m.group("C").strip()),
                    "D": re.sub(r"\s+", " ", m.group("D").strip()),
                },
            })
    return out


# ---------- 解析：中文译文 + 答案 ----------
def cn_norm(s):
    """去掉 CJK 之间被 OCR 插入的空格，提升译文可读性。"""
    return re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", s)


ANALYSIS_KW = ["总体分析", "本文", "文章", "段落", "关键词", "①", "②", "③", "④", "⑤",
               "【", "】", "深层", "解读", "考点", "思路", "定位", "命题", "选项",
               "正确", "搭配", "注释", "语篇", "分析", "—", "―", "◇", "◆",
               "★", "※", "译文", "参考", "✓", "✘"]


def _clean_cn_lines(gap):
    out = []
    for line in gap.split("\n"):
        line = cn_norm(line.strip())
        if not line:
            continue
        if any(k in line for k in ANALYSIS_KW):
            continue
        if re.search(r"【[^】]*[A-Za-z]{2,}[^】]*】", line):  # 注音括号（含拉丁字母）
            continue
        if cjk_ratio(line) < 0.5:
            continue
        out.append(line)
    return out


def extract_translation_cn(region, en_sents):
    """逐句锚定：用真题每句英文在解析里定位，句与句之间的干净中文即该句译文。
    词汇表（注音括号/项目符号）与语篇评注被自然过滤。返回与 en_sents 等长的译文列表。"""
    positions = []
    cursor = 0
    for s in en_sents:
        words = re.findall(r"[A-Za-z]+", s)[:8]
        pos = None
        if words:
            pat = r"\s*".join(re.escape(w) for w in words)
            m = re.search(pat, region[cursor:], re.I)
            if m:
                pos = cursor + m.start()
        positions.append(pos)
        if pos is not None:
            cursor = pos + 1
    cn_per = []
    n = len(en_sents)
    for i, pos in enumerate(positions):
        if pos is None:
            cn_per.append("")
            continue
        if i + 1 < n and positions[i + 1] is not None:
            end = positions[i + 1]
        else:
            sub = region[pos:]
            em = re.search(r"真题精解|语篇分析|试题精解", sub)
            end = pos + em.start() if em else len(region)
        gap = region[pos:end]
        cn_per.append("".join(_clean_cn_lines(gap)))
    return cn_per


# 译文区之后的『词汇/难句』小节标题：一定出现在译文之后（不会出现在篇章前的小标题里），
# 用作译文区的终点分隔。
TRANS_END_KW = ["词汇注释", "难句分析"]
# 兜底分隔词：仅当找不到上述词汇小节时，取出现在英文篇章【之后】的分析章节词。
TRANS_END_KW_FALLBACK = ["试题精解", "真题精解", "深层解读", "答案解析", "语篇分析"]

# 广告/水印垃圾关键词，出现在译文里需剔除
AD_KW = ["淘宝", "店铺", "公众号", "微信", "光速考研", "赠送", "客服", "加微信",
         "唯一正版", "正版", "盗版", "百度", "网盘", "二维码", "关注", "店铺名"]

def _strip_ads(line):
    for k in AD_KW:
        if k in line:
            return ""
    return line

def _find_first_passage_start(region):
    """定位英文篇章起点：取『译文/词汇小节之前最后一个英文簇』的起点。
    篇章与译文逐段（或交错）紧随，译文之后才是词汇/语篇分析；开头的『总体分析』英文标题
    属于更早的簇，因此『词汇小节之前的最后一个英文簇』稳健命中所需篇章。"""
    # 词汇小节位置（第一个即可，必在译文之后）
    vocab_pos = len(region)
    for kw in TRANS_END_KW:
        p = region.find(kw)
        if p != -1 and p < vocab_pos:
            vocab_pos = p
    if vocab_pos == len(region):
        vocab_pos = int(len(region) * 0.7)  # 兜底：无词汇小节时用前 70% 作为界
    # 收集英文连续块
    runs = []
    i, n = 0, len(region)
    while i < n:
        if region[i].isascii() and region[i].isalpha():
            j = i
            letters = 0
            while j < n and (region[j].isascii() and (region[j].isalpha() or region[j] in " .,'\"()/-")):
                if region[j].isalpha():
                    letters += 1
                j += 1
            if letters >= 15:
                runs.append((i, j))
            i = j
        else:
            i += 1
    if not runs:
        return None
    # 聚簇：相邻块间隔 < 300 视为同一英文簇
    clusters = []
    for (s, e) in runs:
        if clusters and s - clusters[-1][1] < 300:
            clusters[-1] = (clusters[-1][0], e)
        else:
            clusters.append((s, e))
    # 篇章判定：篇章之后的片段是『中文译文』（中文占比最高），而『总体分析』之后是英文篇章、
    # 『语篇分析』之后是词汇/分析。因此取「尾随片段中文占比最高」的簇为篇章起点。
    best = None
    best_ratio = -1.0
    for idx, (s, e) in enumerate(clusters):
        nxt_start = clusters[idx + 1][0] if idx + 1 < len(clusters) else vocab_pos
        seg = region[e: nxt_start]
        if not seg.strip():
            continue
        cjk = len(CJK.findall(seg))
        ratio = cjk / max(1, len(seg))
        if ratio > best_ratio:
            best_ratio = ratio
            best = (s, e)
    if best and best_ratio > 0.2:
        return best[0]
    # 兜底：词汇小节之前的最后一个簇
    cand = [c for c in clusters if c[1] <= vocab_pos]
    if cand:
        return cand[-1][0]
    return clusters[0][0]

# 译文截断信号：出现这些词说明已进入「语篇分析/试题精解」等章节，需从译文里切掉。
# 注意：不用裸字「分析」（译文里偶现「分析」属正常语义），只用无歧义的章节标题词。
ANALYSIS_SIGNALS = ["语篇分析", "试题精解", "真题精解", "深层解读", "答案解析",
                    "考点", "命题", "思路", "结构切分", "功能注释", "句子主干",
                    "难句分析", "词汇注释", "经典搭配", "总体分析", "参考答案"]

def _truncate_ref_cn(text):
    """去掉译文里可能混入的分析/词汇章节内容。若开头即是分析信号，则整段判为污染，置空。"""
    for sig in ANALYSIS_SIGNALS:
        p = text.find(sig)
        if p != -1:
            if p == 0:
                return ""  # 整段以分析信号开头 => 实为分析章节，非译文
            text = text[:p]
    return text.strip()

def extract_full_translation(region, anchor_word_lists=None):
    """解析某 Text region 中，英文篇章区域（含可能的『英中交错』译文）里的全部中文译文。
    兼容两种版式：
      - 顺序版（英语二 2007-2009 等）：英文整段 -> 中文整段；
      - 交错版（英语一 多数年份）：英文分句/子句 与 中文译文 逐行交错。
    做法：优先用真题干净首句（及备用句）在 region 中定位『英文篇章起点』（篇章中的句子只出现在
    篇章内，不出现在总体分析或语篇分析引文中，且篇章必在分析之前），再取篇章起点到词汇/难句小节
    之间的区块，保留其中中文占比高的行。返回清洗后的整段译文（用于 article.ref_cn 全文参考译文）。"""
    ps = None
    if anchor_word_lists:
        for aw in anchor_word_lists:
            if not aw:
                continue
            pat = r"\s*".join(re.escape(w) for w in aw[:8])
            m = re.search(pat, region, re.I)
            if m:
                ps = m.start()
                break
    if ps is None:
        ps = _find_first_passage_start(region)
    if ps is None:
        ps = 0
    # 译文终点：必须在『英文篇章起点』之后找，避免误命中篇章之前的小标题/前文词汇
    cut = len(region)
    for kw in TRANS_END_KW:
        p = region.find(kw, ps)
        if p != -1 and p < cut:
            cut = p
    if cut == len(region):
        for kw in TRANS_END_KW_FALLBACK:
            p = region.find(kw, ps)
            if p != -1 and p < cut:
                cut = p
    block = region[ps: cut]
    out = []
    for line in block.split("\n"):
        line = re.sub(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])", "", line.strip())
        if not line:
            continue
        line = _strip_ads(line)
        if not line:
            continue
        if cjk_ratio(line) < 0.5:
            continue
        if re.search(r"【[^】]*[A-Za-z]{2,}[^】]*】", line):
            continue
        out.append(line)
    text = "".join(out)
    return _truncate_ref_cn(text)


def parse_analysis_for_text(analysis_text, text_no, en_sents):
    """从解析全文抽取某 Text 的：标题/主题、逐句中文译文（与 en_sents 对齐）、答案 {number: letter}。"""
    marks = [(m.start(), m.end(), int(m.group(1))) for m in re.finditer(r"Text\s+(\d)", analysis_text)]
    cur = next((mk for mk in marks if mk[2] == text_no), None)
    if not cur:
        return None
    cstart = cur[1]
    nxt = next((mk[0] for mk in marks if mk[0] > cur[0] and mk[2] != text_no), len(analysis_text))
    region = analysis_text[cstart: nxt]

    # 主题：首句锚点之前的首行干净中文
    topic = ""
    first_pos = None
    if en_sents:
        for s in en_sents:
            words = re.findall(r"[A-Za-z]+", s["en"])[:8]
            if not words:
                continue
            m = re.search(r"\s*".join(re.escape(w) for w in words), region, re.I)
            if m:
                first_pos = m.start()
                break
    head_region = region[:first_pos] if first_pos else region
    for line in head_region.split("\n"):
        line = line.strip()
        if 4 <= len(line) <= 60 and cjk_ratio(line) > 0.6 and not any(k in line for k in ANALYSIS_KW):
            topic = line
            break

    # 逐句译文（沿用旧英文锚定法，对英语一多数年份有效）
    cn = extract_translation_cn(region, [s["en"] for s in en_sents]) if en_sents else []

    # 全文参考译文：英文篇章之后、分析章节之前的整段中文（稳健，覆盖所有年份）
    anchor_lists = []
    for s in en_sents[:3]:
        w = re.findall(r"[A-Za-z]+", s["en"])
        if w:
            anchor_lists.append(w)
    ref_cn = extract_full_translation(region, anchor_lists)

    # 答案：在整个解析文中，按题号切段（同一题号可能有多个片段，取含正确标记的），段内用 seg_answer 取字母
    answers = answers_by_number(analysis_text)
    return {"topic": topic, "cn": cn, "ref_cn": ref_cn, "answers": answers}


def answers_by_number(text):
    """按题号切段，段内用 seg_answer 取正确字母，返回 {题号: 字母}。
    同一题号可能有多个片段（题干/译文重复），取含正确标记的片段。"""
    qsplit = list(re.finditer(r"\n\s*(\d{1,2})\.\s", text))
    ans = {}
    for i, qm in enumerate(qsplit):
        num = int(qm.group(1))
        if num < 1 or num > 60:
            continue
        seg_end = qsplit[i + 1].start() if i + 1 < len(qsplit) else len(text)
        a = seg_answer(text[qm.end(): seg_end])
        if a:
            ans[num] = a  # 后写覆盖：真题精解片段通常在译文片段之后
    return ans


def extract_all_answers(text):
    """兼容旧调用：返回 {题号: 字母}。"""
    return answers_by_number(text)


# ---------- 组装 ----------
def build_article(year, exam, text_no, real_blk, ans_info, all_answers=None, questions=None):
    sents = real_blk["sents"]
    qs = questions if questions is not None else real_blk.get("questions", [])
    cn = ans_info["cn"] if ans_info else []
    ref_cn = ans_info.get("ref_cn", "") if ans_info else ""
    # 译文策略：解析版式多变（顺序版/英中交错版），逐句精确对齐不可靠且易混入「语篇分析」等内容。
    # 统一采用『全文参考译文 ref_cn』（已截断分析章节、去广告），挂到每句 cn 上，保证点击即可见干净译文。
    # 若 ref_cn 为空（如扫描图解析年份），则回退到旧逐句结果（可能为空）。
    for i, s in enumerate(sents):
        if ref_cn:
            s_cn = ref_cn
        else:
            s_cn = cn[i] if i < len(cn) else ""
        s["cn"] = s_cn
        s["id"] = (f"en1_{year}" if exam == "en1" else f"{year}") + f"_text{text_no}_s{str(i+1).zfill(2)}"
        s["words"] = []  # 预标注词留空（运行时靠离线词典兜底高亮）
    # 题目补充答案/解析（优先用全局题号映射，更稳）
    ans_map = all_answers if all_answers is not None else (ans_info["answers"] if ans_info else {})
    for q in qs:
        qid = (f"en1_{year}" if exam == "en1" else f"{year}") + f"_text{text_no}_q{q['number']}"
        q["id"] = qid
        q["type"] = "reading"
        q["answer"] = ans_map.get(q["number"], "")
        q["explanation"] = ""
        q["related_sentences"] = []
    topic = (ans_info or {}).get("topic", "")
    # 标题：用真题首句摘要 or 主题
    title = topic or (sents[0]["en"][:60] if sents else f"Text {text_no}")
    return {
        "id": f"{year}_text{text_no}" if exam == "en2" else f"en1_{year}_text{text_no}",
        "type": f"text{text_no}",
        "title": title,
        "topic": topic,
        "ref_cn": ref_cn,
        "source": f"{year} 年考研{'英语一' if exam=='en1' else '英语二'} Text {text_no} · 真题与解析 PDF 自动抽取",
        "sentences": sents,
        "questions": qs,
        "sentence_count": len(sents),
        "question_count": len(qs),
    }


def find_pdfs(exam, year):
    if exam == "en2":
        real = os.path.join(SRC, "真题", f"{year}年考研英语真题（可复制、可搜索）.pdf")
        ans = os.path.join(SRC, "答案", f"{year}年考研英语真题解析.pdf")
    else:
        real = os.path.join(SRC, "【2】2010-2025年考研英语一真题及解析", "01、英一真题部分",
                            f"{year}年考研英语一真题【可复制搜索查词】.pdf")
        ans = os.path.join(SRC, "【2】2010-2025年考研英语一真题及解析", "02、解析部分", "详细版",
                           f"{year}年考研英语一真题解析.pdf")
    return real, ans


def process_year(exam, year, dry=False, out=None):
    real_p, ans_p = find_pdfs(exam, year)
    if not (os.path.isfile(real_p) and os.path.isfile(ans_p)):
        print(f"  ⚠️ {year} {exam} 缺少 PDF：\n    {real_p}\n    {ans_p}")
        return None
    real_txt = clean(pdf_full_text(real_p))
    ans_txt = pdf_full_text(ans_p)
    real_blocks = parse_reading_from_real(real_txt)
    # 全局抽取阅读题（按题号归到 Text），与篇章切块解耦
    global_qs = parse_questions_global(real_txt)
    # 全局按题号提取正确字母 {题号: 字母}
    all_answers = answers_by_number(ans_txt)
    articles = []
    for tno in (1, 2, 3, 4):
        if tno not in real_blocks:
            print(f"  ⚠️ {year} Text{tno} 未在真题中解析到（PDF 缺该篇文本层）")
            continue
        qs = global_qs.get(tno, [])
        blk_answers = {q["number"]: all_answers[q["number"]]
                       for q in qs if q["number"] in all_answers}
        ans_info = parse_analysis_for_text(ans_txt, tno, real_blocks[tno]["sents"])
        art = build_article(year, exam, tno, real_blocks[tno], ans_info, blk_answers, questions=qs)
        articles.append(art)
        hit = sum(1 for q in art["questions"] if q["answer"])
        print(f"  Text{tno}: {art['sentence_count']} 句 / {art['question_count']} 题 / 译文 {len(ans_info['cn']) if ans_info else 0} 句 / 答案命中 {hit}")
    data = {
        "schema_version": 1,
        "exam": exam,
        "year": year,
        "articles": articles,
    }
    if dry:
        return data
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f"  ✅ 写出 {out}")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", choices=["en1", "en2"], required=True)
    ap.add_argument("--year", type=int)
    ap.add_argument("--all", action="store_true", help="en1: 2010-2025; en2: 2007-2009")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--out", help="输出 json 路径（单年）")
    args = ap.parse_args()

    if args.all:
        years = list(range(2010, 2026)) if args.exam == "en1" else [2007, 2008, 2009]
    else:
        years = [args.year]

    root = os.path.dirname(os.path.abspath(__file__))
    pwa = os.path.normpath(os.path.join(root, "..", "pwa"))
    for y in years:
        print(f"--- {args.exam} {y} ---")
        if args.all:
            sub = "en1" if args.exam == "en1" else ""
            out = os.path.join(pwa, "data", sub, f"{y}.json") if sub else os.path.join(pwa, "data", f"{y}.json")
            process_year(args.exam, y, dry=args.dry, out=out if not args.dry else None)
        else:
            process_year(args.exam, y, dry=args.dry, out=args.out)


if __name__ == "__main__":
    main()
