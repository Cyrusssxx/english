"""en1 数据修复 · 阶段二：从"详细版解析"PDF 补全题目

对每题（按题号 21-40 锚定）提取：
  - answer        : 正确选项字母（从 "正确项为【X】" / "［X］正确" 等标记）
  - explanation   : 解题思路/错项排除（中文，去噪）
  - stem_cn       : 题干中文
  - options_cn    : 选项中文 {A,B,C,D}

英文 stem/options 沿用数据里已有的干净内容，不抽解析PDF的破损英文。

用法：
  python tools/fix_en1_questions.py            # 真写回
  python tools/fix_en1_questions.py --dry      # 报告+打印样例不写回
  python tools/fix_en1_questions.py --year 2010 # 只处理某年
"""
import json, os, glob, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN1_DIR = os.path.join(ROOT, "pwa", "data", "en1")
SRC = "D:/ai code/英语考研试题和答案/【2】2010-2025年考研英语一真题及解析/02、解析部分/详细版"

SYS = "C:/Users/cjx/.workbuddy/binaries/python/envs/default/Lib/site-packages"
if SYS not in sys.path:
    sys.path.insert(0, SYS)

OPT_RE = re.compile(r"[\[｜［【]?\s*([A-D])\s*[\]］J】]?\s*([\u4e00-\u9fff][^\n]*)")  # 兼容 ［A］ / 【A】 两种括号
NUM_RE = re.compile(r"(?:^|\n)\s*(\d)\s*(\d)\s*[\.．]")   # 兼容 "NN." / "N N ." / "NN．" / "N N ．" 拆分格式
STEM_CN_RE = re.compile(r"^\s*(\d{2})\.\s*([\u4e00-\u9fff][^\n]*)")
ANSWER_RES = [
    re.compile(r"([A-D])\s*项正确"),                       # 2022/2023：A 项正确。/故C 项正确。
    re.compile(r"确定答案为\s*[【｜]?([A-D])[】｜]?\s*项"),  # 2022/2023：确定答案为C 项
    re.compile(r"答案为\s*[【｜]?([A-D])[】｜]?\s*项"),       # 答案为C 项
    re.compile(r"本题答案为\s*[【｜]?([A-D])[】｜]?"),
    re.compile(r"答案应为\s*[【｜]?([A-D])[】｜]?"),
    re.compile(r"正确项[^\n]{0,6}?([A-D])"),
    re.compile(r"[\[｜［【]([A-D])[\]］J】]?\s*为正确"),
    re.compile(r"[\[｜［【]([A-D])[\]］J】]?\s*正确"),
    re.compile(r"故[\[｜［【]([A-D])[\]］J】]?正确"),
    re.compile(r"因此[\[｜［【]([A-D])[\]］J】]?正确"),
    re.compile(r"选[【｜]([A-D])[】｜]"),
    re.compile(r"答案[：:]\s*[【｜]?([A-D])[】｜]?"),
]
SECTION_CUT = ["Section III", "Part C", "PartC", "Part B", "翻译", "写作", "审题谋篇", "一、审题",
               "Text 1", "Text 2", "Text 3", "Text 4", "Section II",
               "Ⅰ①", "Ⅱ①", "Ⅲ①", "Ⅳ①",            # 下一篇/下一段真题正文起始，截断解析溢出
               "二、试题精解", "三、", "四、"]


def load_pdf_text(path):
    import pymupdf as fitz
    doc = fitz.open(path)
    return "\n".join(p.get_text() for p in doc)


def find_blocks(text):
    """返回 {num: (start, end)}，按题号 21-40 切块。"""
    blocks = {}
    spans = [(m.start(), int(m.group(1) + m.group(2))) for m in NUM_RE.finditer(text)
             if 21 <= int(m.group(1) + m.group(2)) <= 40]
    spans.sort()
    for idx, (pos, num) in enumerate(spans):
        end = spans[idx + 1][0] if idx + 1 < len(spans) else len(text)
        # 同一题号可能多次出现（英文stem + 中文stem），取最早起点、最晚终点
        if num in blocks:
            blocks[num] = (blocks[num][0], max(blocks[num][1], end))
        else:
            blocks[num] = (pos, end)
    return blocks


def _is_noise_line(ln):
    """丢弃纯英文伪影行（解析PDF英文被拆字，保留中文解析行）。"""
    if not ln:
        return True
    cjk = sum(1 for c in ln if '一' <= c <= '鿿')
    lat = sum(1 for c in ln if c.isascii() and c.isalpha())
    if cjk == 0 and len(ln) > 8:
        return True                      # 纯英文长行 = 噪声
    if len(ln) > 500:
        return True
    return False


def parse_question(num, block):
    seg = block
    # 题干中文
    stem_cn = ""
    for line in seg.split("\n"):
        m = STEM_CN_RE.match(line)
        if m and int(m.group(1)) == num:
            t = m.group(2).strip()
            if len(t) > 3:
                stem_cn = t
                break
    # 选项中文（兼容半角/全角括号）
    options_cn = {}
    for m in OPT_RE.finditer(seg):
        options_cn.setdefault(m.group(1), m.group(2).strip())
    # 答案
    answer = ""
    for r in ANSWER_RES:
        mm = r.search(seg)
        if mm:
            answer = mm.group(1)
            break
    # 解析：从最后一个选项位置到块末，砍掉后续 Section/Text 段，按中英文比清洗
    opt_ends = [m.end() for m in OPT_RE.finditer(seg)]     # 用同一 OPT_RE，兼容 [ BJ 噪声
    start = max(opt_ends) if opt_ends else 0
    expl = seg[start:]
    for cut in SECTION_CUT:
        ci = expl.find(cut)
        if ci > 0:
            expl = expl[:ci]
    lines = []
    for ln in expl.split("\n"):
        ln = ln.strip()
        if _is_noise_line(ln):
            continue
        lines.append(ln)
    explanation = "\n".join(lines).strip()
    # 若仍含下一题号残留，截断
    ne = NUM_RE.search(explanation)
    if ne:
        explanation = explanation[:ne.start()].strip()
    return {
        "answer": answer,
        "stem_cn": stem_cn,
        "options_cn": options_cn,
        "explanation": explanation,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--year", type=int, default=None)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(EN1_DIR, "*.json")),
                   key=lambda x: int(os.path.basename(x)[:-5]))
    for f in files:
        y = int(os.path.basename(f)[:-5])
        if args.year and y != args.year:
            continue
        pdf = os.path.join(SRC, f"{y}年考研英语一真题解析.pdf")
        if not os.path.exists(pdf):
            print(f"[skip] {y} 解析PDF不存在")
            continue
        text = load_pdf_text(pdf)
        blocks = find_blocks(text)
        parsed = {num: parse_question(num, text[s:e]) for num, (s, e) in blocks.items()}

        d = json.load(open(f, encoding="utf-8"))
        filled = 0
        for a in d.get("articles", []):
            for q in a.get("questions", []):
                num = q.get("number")
                p = parsed.get(num)
                if not p:
                    continue
                changed = False
                if p["answer"] and not q.get("answer"):
                    q["answer"] = p["answer"]; changed = True
                if p["stem_cn"] and not q.get("stem_cn"):
                    q["stem_cn"] = p["stem_cn"]; changed = True
                if p["options_cn"] and not q.get("options_cn"):
                    # 只补数据中缺失的选项中文
                    oc = dict(q.get("options_cn") or {})
                    for k, v in p["options_cn"].items():
                        oc.setdefault(k, v)
                    q["options_cn"] = oc; changed = True
                if p["explanation"] and not (q.get("explanation") or "").strip():
                    q["explanation"] = p["explanation"]; changed = True
                if changed:
                    filled += 1
        if args.dry:
            np = len(parsed)
            ca = sum(1 for p in parsed.values() if p["answer"])
            ce = sum(1 for p in parsed.values() if p["explanation"])
            cs = sum(1 for p in parsed.values() if p["stem_cn"])
            co = sum(1 for p in parsed.values() if len(p["options_cn"]) >= 4)
            print(f"\n===== {y} 解析出 {np} 题 | ans {ca}/{np} | expl {ce}/{np} | stem_cn {cs}/{np} | opt4 {co}/{np} | 可补全 {filled} =====")
            for num in sorted(parsed):
                p = parsed[num]
                print(f"  Q{num}: ans={p['answer'] or '-'} stem_cn={'Y' if p['stem_cn'] else '-'} opt_cn={list(p['options_cn'].keys())} expl={len(p['explanation'])}字")
        else:
            if filled:
                json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
                print(f"{y}: 补全 {filled} 题")
            else:
                print(f"{y}: 无变化，跳过")
    print("[done]")


if __name__ == "__main__":
    main()
