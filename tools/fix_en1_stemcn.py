"""en1 数据修复 · 补充题：从"详细版解析"PDF 补全题干中文(stem_cn)与选项中文(options_cn)

解析PDF的题干中文格式被拆字，形如:
  "2 1 .根据第一段内容，博物馆在______ 方面正面临困难。"
  "2 1 ．根据第一段内容..."
  "21. 根据第一段内容..."
  "21．根据第一段内容..."
选项中文: "［A］维护其塑料物品" / "[A]维护其塑料物品"

兼容上述所有题号拆分格式。只读缺失字段，不覆盖已有内容。幂等。

用法:
  python tools/fix_en1_stemcn.py            # 真写回
  python tools/fix_en1_stemcn.py --dry      # 仅报告
"""
import json, os, glob, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN1_DIR = os.path.join(ROOT, "pwa", "data", "en1")
SRC = "D:/ai code/英语考研试题和答案/【2】2010-2025年考研英语一真题及解析/02、解析部分/详细版"

SYS = "C:/Users/cjx/.workbuddy/binaries/python/envs/default/Lib/site-packages"
if SYS not in sys.path:
    sys.path.insert(0, SYS)

# 题号: 兼容 "21." / "2 1 ." / "21．" / "2 1 ．"
NUM_RE = re.compile(r"(?:^|\n)\s*(\d)\s*(\d)\s*[\.．]")
OPT_RE = re.compile(r"[\[｜［【]?\s*([A-D])\s*[\]］J】]?\s*([\u4e00-\u9fff][^\n]*)")


def load_pdf_text(path):
    import pymupdf as fitz
    doc = fitz.open(path)
    return "\n".join(p.get_text() for p in doc)


def find_blocks(text):
    """返回 {num: (start, end)}，按题号 21-40 切块。"""
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


def parse_block(seg):
    # 题干中文: 段首 "NN.中文" 紧跟在题干英文之后，取本块里第一个纯中文长行(>6字)
    stem_cn = ""
    for line in seg.split("\n"):
        line = line.strip()
        if not line:
            continue
        cjk = sum(1 for c in line if '一' <= c <= '鿿')
        # 题干中文行: 基本全是中文，长度>6，且不含英文字母(避免英文stem)
        if cjk >= len(line) * 0.8 and cjk > 6 and not any(c.isascii() and c.isalpha() for c in line):
            stem_cn = line
            break
    # 选项中文
    options_cn = {}
    for m in OPT_RE.finditer(seg):
        options_cn.setdefault(m.group(1), m.group(2).strip())
    return stem_cn, options_cn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(EN1_DIR, "*.json")),
                   key=lambda x: int(os.path.basename(x)[:-5]))
    total_stem = 0
    total_opt = 0
    for f in files:
        y = int(os.path.basename(f)[:-5])
        pdf = os.path.join(SRC, f"{y}年考研英语一真题解析.pdf")
        if not os.path.exists(pdf):
            continue
        text = load_pdf_text(pdf)
        blocks = find_blocks(text)
        parsed = {num: parse_block(text[s:e]) for num, (s, e) in blocks.items()}

        d = json.load(open(f, encoding="utf-8"))
        changed = False
        for a in d.get("articles", []):
            for q in a.get("questions", []):
                num = q.get("number")
                p = parsed.get(num)
                if not p:
                    continue
                stem_cn, options_cn = p
                if stem_cn and not q.get("stem_cn"):
                    q["stem_cn"] = stem_cn
                    total_stem += 1
                    changed = True
                if options_cn:
                    oc = dict(q.get("options_cn") or {})
                    before = len(oc)
                    for k, v in options_cn.items():
                        oc.setdefault(k, v)
                    if len(oc) > before or not q.get("options_cn"):
                        q["options_cn"] = oc
                        if len(oc) > before:
                            total_opt += 1
                        changed = True
        if changed and not args.dry:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{y}: stem_cn补 {sum(1 for a in d.get('articles',[]) for q in a.get('questions',[]) if q.get('stem_cn'))}/{sum(len(a.get('questions',[])) for a in d.get('articles',[]))} | 本轮回填 stem={total_stem if changed else 0} opt={total_opt if changed else 0}")
    print(f"\n[dry={args.dry}] 本次补 stem_cn={total_stem} 题, options_cn={total_opt} 题")


if __name__ == "__main__":
    main()
