"""en1 数据修复 · 补充解析(explanation)

针对审计剩余的解析缺口(2010-2023 部分题)。解析 PDF 的"精准定位/命题解密/技巧总结"
段是完整中文，但原 fix_en1_questions.py 的 SECTION_CUT / 噪声过滤会截断。
本脚本: 从题号块里，取"最后一个选项中文行之后"到"下一道题号之前"的全部中文解析行，
不做 SECTION_CUT 硬截断(改由下题号自然边界)，保留完整解析。

用法:
  python tools/fix_en1_expl.py            # 真写回
  python tools/fix_en1_expl.py --dry      # 仅报告
"""
import json, os, glob, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN1_DIR = os.path.join(ROOT, "pwa", "data", "en1")
SRC = "D:/ai code/英语考研试题和答案/【2】2010-2025年考研英语一真题及解析/02、解析部分/详细版"

SYS = "C:/Users/cjx/.workbuddy/binaries/python/envs/default/Lib/site-packages"
if SYS not in sys.path:
    sys.path.insert(0, SYS)

NUM_RE = re.compile(r"(?:^|\n)\s*(\d)\s*(\d)\s*[\.．]")
OPT_RE = re.compile(r"[\[｜［【]?\s*([A-D])\s*[\]］J】]?\s*([\u4e00-\u9fff][^\n]*)")


def load_pdf_text(path):
    import pymupdf as fitz
    doc = fitz.open(path)
    return "\n".join(p.get_text() for p in doc)


def find_blocks(text):
    spans = []
    for m in NUM_RE.finditer(text):
        num = int(m.group(1) + m.group(2))
        if 21 <= num <= 40:
            spans.append((m.start(), num))
    spans.sort()
    blocks = {}
    for idx, (pos, num) in enumerate(spans):
        end = spans[idx + 1][0] if idx + 1 < len(spans) else len(text)
        if num in blocks:
            blocks[num] = (blocks[num][0], max(blocks[num][1], end))
        else:
            blocks[num] = (pos, end)
    return blocks


def parse_expl(seg):
    # 选项中文行位置
    opt_ends = [m.end() for m in OPT_RE.finditer(seg)]
    start = max(opt_ends) if opt_ends else 0
    expl = seg[start:]
    # 自然边界: 下一道题号
    ne = NUM_RE.search(expl)
    if ne:
        expl = expl[:ne.start()]
    lines = []
    for ln in expl.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        cjk = sum(1 for c in ln if '一' <= c <= '鿿')
        lat = sum(1 for c in ln if c.isascii() and c.isalpha())
        # 保留中文解析行(中文占比高)，丢弃纯英文伪影长行
        if cjk == 0 and len(ln) > 6:
            continue
        if len(ln) > 600:
            continue
        if cjk < len(ln) * 0.3 and lat > 0:
            continue
        lines.append(ln)
    return "\n".join(lines).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(EN1_DIR, "*.json")),
                   key=lambda x: int(os.path.basename(x)[:-5]))
    total = 0
    for f in files:
        y = int(os.path.basename(f)[:-5])
        pdf = os.path.join(SRC, f"{y}年考研英语一真题解析.pdf")
        if not os.path.exists(pdf):
            continue
        text = load_pdf_text(pdf)
        blocks = find_blocks(text)
        parsed = {num: parse_expl(text[s:e]) for num, (s, e) in blocks.items()}

        d = json.load(open(f, encoding="utf-8"))
        changed = False
        for a in d.get("articles", []):
            for q in a.get("questions", []):
                num = q.get("number")
                p = parsed.get(num)
                if p and not (q.get("explanation") or "").strip():
                    q["explanation"] = p
                    total += 1
                    changed = True
        if changed and not args.dry:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if changed:
            print(f"{y}: 补解析 {total if False else sum(1 for a in d['articles'] for q in a['questions'] if q.get('explanation'))} (本回合+{total})")
    print(f"\n[dry={args.dry}] 本次补解析={total} 题")


if __name__ == "__main__":
    main()
