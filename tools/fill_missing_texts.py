#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补回 en1 缺失篇：2013/2014/2017 的 Text1、2020 的 Text2。
英文来源：真题 PDF（干净）优先；真题无文本层的年份（2014/2017/2020 缺篇）从解析 PDF 反抽英文。
译文/答案/主题：复用 import_exam 的 parse_analysis_for_text（从解析 PDF 抽，稳健）。
用法：
  python fill_missing_texts.py --dry
  python fill_missing_texts.py
"""
import os, re, sys, json, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import import_exam as IE

SRC = IE.SRC
LAT = re.compile(r"[A-Za-z]")

def en_ratio(s):
    if not s.strip():
        return 0
    return len(LAT.findall(s)) / max(1, len(s))

def extract_en_from_xf(region):
    """从解析某 Text region 抽英文（英中逐行交错 + 多遍重印版式）。
    收集全部英文候选行（截断行尾中文），排除题干/选项行（含[ABCD]或问号或提问句式），
    按序拼接后整体断句，再对相邻高度相似的句子去重，得到正文。"""
    lines = [ln.strip() for ln in region.split("\n") if ln.strip()]
    QUESTION_HEAD = re.compile(
        r"^(what|how|which|why|according to|it can be|the author|we can|in the|from the)\b", re.I)
    frags = []
    for ln in lines:
        if re.match(r"^[\u4e00-\u9fff]", ln):
            continue
        if re.search(r"[\[［][A-D][\]］]", ln):   # 选项行
            continue
        if "?" in ln:                              # 题干行
            continue
        if QUESTION_HEAD.match(ln):
            continue
        words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", ln)
        if len(words) < 4:
            continue
        m = re.search(r"[\u4e00-\u9fff]{2,}", ln)
        if m and m.start() >= 6:
            ln = ln[:m.start()]
        ln = re.sub(r"[\u4e00-\u9fff].*$", "", ln).strip()
        if len(re.findall(r"[A-Za-z]", ln)) >= 8:
            frags.append(ln)
    if not frags:
        return []
    txt = re.sub(r"\s+", " ", " ".join(frags)).strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", txt)
    seen = []
    sents = []
    for p in parts:
        p = p.strip()
        if len(LAT.findall(p)) < 8:
            continue
        wset = set(re.findall(r"[a-z]+", p.lower()))
        dup = any(len(wset & sw) / max(1, min(len(wset), len(sw))) >= 0.6 for sw in seen[-3:])
        if dup:
            continue
        seen.append(wset)
        sents.append(p)
    return sents

def split_to_sents(en_list, year, tno):
    """把英文句子列表转成 import_exam 风格 {para,en} 结构。"""
    out = []
    para = 1
    for i, s in enumerate(en_list):
        out.append({"para": para, "en": s})
        # 每 3-4 句算一段（按句数粗略分段）
        if (i + 1) % 4 == 0:
            para += 1
    return out

def get_en_sents(year, tno, ans_txt):
    """英文来源：真题优先，解析兜底。"""
    real_p, _ = IE.find_pdfs("en1", year)
    real_txt = IE.clean(IE.pdf_full_text(real_p))
    # 真题里定位该篇：Text tno 锚点
    marks = []
    for m in re.finditer(r"(?<![A-Za-z])Text\s*([\dl])", real_txt, re.I):
        g = m.group(1)
        n = 1 if g.lower() == "l" else int(g)
        marks.append((m.start(), n))
    starts = []
    for pos, n in marks:
        if starts and starts[-1][1] == n:
            continue
        starts.append((pos, n))
    blk = None
    for idx, (pos, n) in enumerate(starts):
        if n == tno:
            end = starts[idx + 1][0] if idx + 1 < len(starts) else len(real_txt)
            blk = real_txt[pos:end]
            break
    if blk:
        blk = re.sub(r"^.*?Text\s*[\dl]\s*", "", blk, count=1, flags=re.S | re.I).strip()
        mq = re.search(r"\n\s*(?:2[1-9]|3[0-9]|40)\.\s", blk)
        passage = blk[: mq.start()] if mq else blk
        en_lines = []
        for para, ptxt in IE.split_paragraphs(passage):
            for s in IE.split_sentences(ptxt):
                en_lines.append(s)
        if en_lines:
            sents = [{"para": p, "en": s} for p, s in
                     [( (i // 4) + 1, x) for i, x in enumerate(en_lines)]]
            return sents, "real"
    # 兜底：解析 PDF
    m = re.search(r"Text\s+" + str(tno) + r"\b", ans_txt)
    if not m:
        return None, "xf"
    nxt = re.search(r"Text\s+" + str(tno + 1) + r"\b", ans_txt[m.start():]) if tno < 4 else None
    end = m.start() + nxt.start() if nxt else len(ans_txt)
    region = ans_txt[m.start():end]
    en_list = extract_en_from_xf(region)
    if not en_list:
        return None, "xf"
    sents = split_to_sents(en_list, year, tno)
    return sents, "xf"

def build_missing(year, tno, dry):
    _, ans_p = IE.find_pdfs("en1", year)
    ans_txt = IE.pdf_full_text(ans_p)
    en_sents, src = get_en_sents(year, tno, ans_txt)
    if not en_sents:
        print(f"  ⚠️ {year} Text{tno} 英文抽不到（真题+解析均失败）")
        return None
    ans_info = IE.parse_analysis_for_text(ans_txt, tno, en_sents)
    qs = IE.parse_questions_global(IE.clean(IE.pdf_full_text(IE.find_pdfs("en1", year)[0])))
    qs = qs.get(tno, [])
    all_answers = IE.answers_by_number(ans_txt)
    art = IE.build_article(year, "en1", tno, {"sents": en_sents, "questions": qs},
                           ans_info, all_answers, questions=qs)
    hit = sum(1 for q in art["questions"] if q["answer"])
    cn_ok = sum(1 for s in art["sentences"] if s["cn"].strip())
    print(f"  Text{tno}: 来源={src} {art['sentence_count']}句/{art['question_count']}题 "
          f"译文={cn_ok}句 ref_cn={len(art['ref_cn'])}字 答案命中={hit}")
    if dry:
        return None
    # 译文/解析统一交 sub-agent 手工补：清空自动抽到的（可能污染的）译文与解析字段
    art["ref_cn"] = ""
    for s in art["sentences"]:
        s["cn"] = ""
    for q in art["questions"]:
        q["explanation"] = ""
        q["stem_cn"] = ""
        q["options_cn"] = {}
        q["related_sentences"] = []
    return art

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    targets = [(2013, 1), (2014, 1), (2017, 1), (2020, 2)]
    new_arts = {}
    for year, tno in targets:
        print(f"--- {year} Text{tno} ---")
        art = build_missing(year, tno, args.dry)
        if art:
            new_arts[(year, tno)] = art
    if args.dry:
        return
    # 合并进现有 json
    EN1 = os.path.normpath(os.path.join(HERE, "..", "pwa", "data", "en1"))
    for (year, tno), art in new_arts.items():
        fp = os.path.join(EN1, f"{year}.json")
        d = json.load(open(fp, encoding="utf-8"))
        # 去重（若已存在同 id）
        d["articles"] = [a for a in d["articles"] if a["id"] != art["id"]]
        d["articles"].append(art)
        order = {f"text{n}": n for n in range(1, 5)}
        d["articles"].sort(key=lambda x: order.get(x["type"], 9))
        json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  ✅ 合并 {year}.json (现 {len(d['articles'])} 篇)")

if __name__ == "__main__":
    main()
