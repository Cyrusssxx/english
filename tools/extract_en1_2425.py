import os, sys, re, json

SYS = "C:/Users/cjx/.workbuddy/binaries/python/envs/default/Lib/site-packages"
if SYS not in sys.path:
    sys.path.insert(0, SYS)
import pymupdf as fitz

BASE = "D:/ai code/英语考研试题和答案/【2】2010-2025年考研英语一真题及解析/01、英一真题部分"
OUT = "tools"

QNUM = re.compile(r"(2[1-9]|3[0-9]|40)")  # 阅读题号 21-40
QHEAD = re.compile(r"^\s*(2[1-9]|3[0-9]|40)\s*[\.．]\s*")
OPTION = re.compile(r"[\\[［]\s*([A-D])\s*[\]］]?\s*(.*?)(?=[\\[［]\s*[A-D]\s*[\]］]?|\Z)", re.S)
TEXTMARK = re.compile(r"Text\s+[1-4]\b")


def load_text(y):
    p = os.path.join(BASE, f"{y}年考研英语一真题【可复制搜索查词】.pdf")
    doc = fitz.open(p)
    return "\n".join(pg.get_text() for pg in doc)


def clean_paragraphs(text):
    raw = text.split("\n")
    paras, cur = [], []
    for line in raw:
        s = line.rstrip()
        if s.strip() == "":
            if cur:
                paras.append(cur)
                cur = []
            continue
        cur.append(s)
    if cur:
        paras.append(cur)
    out = []
    for para in paras:
        joined = ""
        for i, ln in enumerate(para):
            if joined.endswith("-") and i > 0:
                joined = joined[:-1] + ln.strip()
            else:
                joined = (joined + " " + ln.strip()) if joined else ln.strip()
        joined = re.sub(r"\s+", " ", joined).strip()
        # 过滤页码/噪声行
        if len(joined) < 3:
            continue
        if re.match(r"^\d{2,4}[-–]\d{1,2}$", joined):
            continue
        if re.match(r"^\d{1,3}$", joined):
            continue
        out.append(joined)
    return out


def split_sentences(para):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z])", para)
    res = []
    for p in parts:
        p = p.strip()
        if p:
            res.append(p)
    return res


def find_passages(txt, pa, pb, q_positions):
    marks = [(m.start(), int(m.group(1))) for m in re.finditer(r"Text\s+([1-4])\b", txt)
             if pa < m.start() < pb]
    marks = sorted(marks)[:4]
    # 每篇首题题号 -> 在全文的位置
    first_q_pos = {}
    for t in (1, 2, 3, 4):
        qn = 21 + (t - 1) * 5
        first_q_pos[t] = q_positions.get(qn)
    bounds = []
    for idx, (pos, num) in enumerate(marks):
        nl = txt.find("\n", pos)
        start = nl + 1 if nl > 0 else pos + 8
        nxt_text = marks[idx + 1][0] if idx + 1 < len(marks) else pb
        fq = first_q_pos.get(num)
        # 正文结束于：下一篇标记 或 本篇首题 的较早者
        candidates = [nxt_text]
        if fq is not None and fq > pos:
            candidates.append(fq)
        end = min(candidates)
        bounds.append((num, start, end))
    passages = {}
    for num, start, end in bounds:
        body = txt[start:end]
        passages[num] = clean_paragraphs(body)
    return passages


def find_questions(txt, pa, pb):
    q21 = txt.find("\n21", pa)
    if q21 < 0:
        q21 = txt.find("21.", pa)
    qregion = txt[q21:pb]
    qanchors = [(m.start(), int(m.group(1)), "q") for m in re.finditer(r"\n\s*(2[1-9]|3[0-9]|40)\s*[\.．]\s*", qregion)]
    tanchors = [(m.start(), None, "t") for m in TEXTMARK.finditer(qregion)]
    allanchors = sorted(qanchors + tanchors)
    questions = {}
    for idx, (pos, num, kind) in enumerate(qanchors):
        nxt = None
        for a in allanchors:
            if a[0] > pos:
                nxt = a[0]
                break
        end = nxt if nxt is not None else len(qregion)
        block = qregion[pos:end]
        block = QHEAD.sub("", block, count=1)
        opts = {}
        # 风格1: [A] 括号
        for om2 in OPTION.finditer(block):
            letter = om2.group(1)
            otxt = re.sub(r"\s+", " ", om2.group(2)).strip()
            opts[letter] = otxt
        # 风格2: A. 字母+句号
        if len(opts) < 4:
            opts = {}
            first = re.search(r"\n\s*([A-D])\s*[\.．]", block)
            stem = block[:first.start()].strip() if first else block.strip()
            stem = re.sub(r"\s+", " ", stem).strip().rstrip(".").strip()
            for om2 in re.finditer(r"\n\s*([A-D])\s*[\.．]\s*(.*?)(?=\n\s*[A-D]\s*[\.．]|\Z)", block, re.S):
                letter = om2.group(1)
                otxt = re.sub(r"\s+", " ", om2.group(2)).strip()
                opts[letter] = otxt
        else:
            first = re.search(r"[\\[［]\s*[A-D]\s*[\]］]?", block)
            stem = block[:first.start()].strip() if first else block.strip()
        questions[num] = {"stem": re.sub(r"\s+", " ", stem).strip(), "options": opts}
    return questions


def find_answers(txt):
    ans = {}
    # 格式A: "21. D 22.D 23.A ..."
    for m in re.finditer(r"(2[1-9]|3[0-9]|40)\s*[\.．]\s*([A-D])\b", txt):
        ans[int(m.group(1))] = m.group(2)
    # 格式B: "21-25 CAABA" -> 21=C 22=A ...
    for m in re.finditer(r"(2[1-9]|3[0-9]|40)\s*[-–]\s*(2[1-9]|3[0-9]|40)\s*([A-D]{1,5})", txt):
        start = int(m.group(1)); end = int(m.group(2)); letters = m.group(3)
        for i, ch in enumerate(letters):
            n = start + i
            if n <= end and n not in ans:
                ans[n] = ch
    return ans


def extract(y):
    txt = load_text(y)
    pa = txt.find("Part A")
    pb = txt.find("Part B")
    # 全文题号位置（用于正文边界）
    q_positions = {}
    for m in re.finditer(r"\n\s*(2[1-9]|3[0-9]|40)\s*[\.．]", txt):
        q_positions[int(m.group(1))] = m.start()
    passages = find_passages(txt, pa, pb, q_positions)
    questions = find_questions(txt, pa, pb)
    answers = find_answers(txt)
    art_q = {1: [], 2: [], 3: [], 4: []}
    for num in sorted(questions):
        t = (num - 21) // 5 + 1
        if t in art_q:
            art_q[t].append(num)
    articles = []
    for num in [1, 2, 3, 4]:
        paras = passages.get(num, [])
        sents, sid = [], 0
        for pi, para in enumerate(paras):
            for s in split_sentences(para):
                sid += 1
                sents.append({
                    "para": pi + 1, "en": s, "cn": "",
                    "id": f"en1_{y}_text{num}_s{sid:02d}", "words": []
                })
        qs = []
        for qn in art_q[num]:
            q = questions[qn]
            qs.append({
                "number": qn, "stem": q["stem"], "options": q["options"],
                "id": f"en1_{y}_text{num}_q{qn}", "type": "reading",
                "answer": answers.get(qn, ""), "explanation": "",
                "related_sentences": [], "stem_cn": "", "options_cn": {}
            })
        articles.append({
            "id": f"en1_{y}_text{num}", "type": f"text{num}", "title": "",
            "topic": "", "ref_cn": "",
            "source": f"{y} 年考研英语一 Text {num} · 真题 PDF 抽取 + 手工补译",
            "sentences": sents, "questions": qs,
            "sentence_count": len(sents), "question_count": len(qs)
        })
    out = {"schema_version": 1, "exam": "en1", "year": y, "articles": articles}
    path = os.path.join(OUT, f"en1_{y}_extracted.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 报告
    print(f"{y}: 文章={len(articles)} 句={'/'.join(str(len(a['sentences'])) for a in articles)} "
          f"题={'/'.join(str(len(a['questions'])) for a in articles)} "
          f"答案命中={sum(1 for a in articles for q in a['questions'] if q['answer'])}")
    for num in [1, 2, 3, 4]:
        a = articles[num - 1]
        print(f"  text{num}: {len(a['sentences'])}句, {len(a['questions'])}题, "
              f"选项完整={all(len(q['options'])==4 for q in a['questions'])}, "
              f"答案={[q['answer'] for q in a['questions']]}")


if __name__ == "__main__":
    for y in [2024, 2025]:
        extract(y)
