"""清理真题 PDF 文本层提取结果，切分 Text 1-4 原文与题目。

真题 PDF（可复制版）的文本层存在字符级瑕疵：连字/引号被错编码、
撇号被识别成数字、单词字母被拆散跨行等。此脚本做规整化，输出便于建库的文本。

用法:
    python -X utf8 tools/clean_exam_text.py 2023
输出: tools/extracted/{year}_exam_clean.txt
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT = os.path.join(ROOT, "tools", "extracted")

# 通用字符级修正（按顺序应用）
FIXES = [
    # 页脚 / 页标记
    (r"英语（二）试题[\.\s]*\d[\s\d]*[\.\s]*（共\s*1?\s*4\s*页）", ""),
    (r"=====\s*\[page \d+\]\s*=====", ""),
    # 错编码的常见词
    (r"govemmenfs", "government's"),
    (r"govemment", "government"),
    (r"\bifs\b", "it's"),
    (r"\bThafs\b", "That's"),
    (r"\bthafs\b", "that's"),
    (r"\bHke\b", "like"),
    (r"1\s*汰e", "like"),
    (r"\bdoesn9t\b", "doesn't"),
    # 撇号被识别为数字：teenagers9 -> teenagers'
    (r"([A-Za-z]{3,})9(?=\s|[.,;:]|$)", r"\1'"),
    (r"([A-Za-z]{3,})5(?=\s|[.,;:]|$)", r"\1'"),
    # 引号规整
    (r",,", "\""),
    (r"/J", "\""),
    (r"\bU([A-Z])", r"\"\1"),          # UI personally -> "I personally
    (r"\bu\s+(?=[a-z])", "\""),         # u cognitive -> "cognitive
    (r"[“”]", "\""),
    (r"[‘’]", "'"),
]


def fix_spread_letters(text):
    """合并被拆散的单词：如 'g\nr a s s .' / 'o\nu\nt .' -> 'grass.' / 'out.'。

    真题 PDF 中题干末尾的单词常被逐字母拆开。仅当连续单字母
    序列（>=3 个）紧跟一个句点时才合并，避免误合“in a 2008”这类正常文本。
    必须在引号修正之前执行，否则 'o u t' 中的单个 u 会被误当成引号。
    """
    def merge(m):
        letters = re.sub(r"\s+", "", m.group(1))
        return " " + letters + "."

    # 左侧 (?<![A-Za-z']) 确保首个单字母真正独立，不吞掉前一词末字母
    # （含撇号情形：Crone's s t u d y . 中的 's 不得被当成序列起点）
    pattern = re.compile(r"(?<![A-Za-z'])((?:[A-Za-z]\s+){2,}[A-Za-z])\s*\.")
    return pattern.sub(merge, text)


def clean(text):
    # 统一换行
    text = text.replace("\r\n", "\n")
    # 先合并被拆散的字母（必须先于引号修正）
    text = fix_spread_letters(text)
    for pat, rep in FIXES:
        text = re.sub(pat, rep, text)
    # 压缩多余空白
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main():
    years = [int(a) for a in sys.argv[1:] if a.isdigit()] or [2023]
    for year in years:
        src = os.path.join(EXT, "%d_exam.txt" % year)
        if not os.path.exists(src):
            print("MISSING", src)
            continue
        raw = open(src, encoding="utf-8").read()
        out = clean(raw)
        dst = os.path.join(EXT, "%d_exam_clean.txt" % year)
        with open(dst, "w", encoding="utf-8") as f:
            f.write(out)
        print("%d -> %s (%d -> %d chars)" % (year, dst, len(raw), len(out)))


if __name__ == "__main__":
    main()
