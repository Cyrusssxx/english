"""从 OCR 解析文本中抽取每题答案（依据官方解析中的“X项正确”判定）。

原理：官方解析每题含一个“[精准定位]”块，块内明确写出“X项正确”。
向前回溯取题号，向后扫描取答案字母，从而得到答案键。

用法:
    python -X utf8 tools/extract_answers.py 2023
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "tools", "extracted")

# 答案判定表述（按可靠性排序）
ANS_PATTERNS = [
    r"([A-D])\s*项正确",
    r"故\s*([A-D])\s*项",
    r"([A-D])\s*项为正确",
    r"正确答案为\s*([A-D])",
    r"答案为\s*([A-D])",
]


def extract(year):
    path = os.path.join(EXT, "%d_notes_ocr.txt" % year)
    if not os.path.exists(path):
        path = os.path.join(EXT, "%d_notes.txt" % year)
    if not os.path.exists(path):
        print("MISSING notes for", year)
        return {}

    text = open(path, encoding="utf-8").read()
    # 去掉换行便于跨行匹配（OCR 会把一句拆多行）
    flat = re.sub(r"\s+", "", text)

    results = {}
    for m in re.finditer(r"\[精准定位[\]］]", flat):
        start = m.start()
        # 向前回溯 400 字符找题号（形如 21. / 21．）
        back = flat[max(0, start - 400):start]
        nums = re.findall(r"(?<!\d)(2[1-9]|3[0-9]|40)[.．]", back)
        if not nums:
            continue
        qno = int(nums[-1])
        # 向后扫描 2500 字符找答案判定
        fwd = flat[start:start + 2500]
        ans = None
        for pat in ANS_PATTERNS:
            mm = re.search(pat, fwd)
            if mm:
                ans = mm.group(1)
                break
        if ans and qno not in results:
            results[qno] = ans
    return results


def main():
    years = [int(a) for a in sys.argv[1:] if a.isdigit()] or [2023]
    for year in years:
        res = extract(year)
        print("=" * 60)
        print(year, "extracted", len(res), "answers")
        missing = [n for n in range(21, 41) if n not in res]
        line = []
        for n in range(21, 41):
            line.append("%d%s" % (n, res.get(n, "?")))
            if n % 5 == 0:
                print("   " + " ".join(line))
                line = []
        if missing:
            print("   MISSING:", missing)


if __name__ == "__main__":
    main()
