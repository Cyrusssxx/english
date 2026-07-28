# -*- coding: utf-8 -*-
"""
真题/解析 PDF 文本提取（仅供制作 data JSON 时人工对照，不自动生成数据）

用法:
    python -X utf8 tools\extract_pdf.py 2010          # 提取单年
    python -X utf8 tools\extract_pdf.py 2010 2014     # 提取区间

输出:
    tools/extracted/{year}_exam.txt    真题全文
    tools/extracted/{year}_notes.txt   解析全文（体量大，检索定位用）
"""
import sys
import glob
from pathlib import Path

import fitz  # PyMuPDF

SRC = Path(r"D:\ai code\英语二考研试题和答案")
OUT = Path(__file__).resolve().parent / "extracted"


def extract(pdf_path: Path, out_path: Path):
    doc = fitz.open(pdf_path)
    parts = []
    for i, page in enumerate(doc):
        parts.append(f"\n===== [page {i + 1}] =====\n")
        parts.append(page.get_text())
    text = "".join(parts)
    out_path.write_text(text, encoding="utf-8")
    print(f"  {pdf_path.name} -> {out_path.name}  ({doc.page_count} 页 / {len(text)} 字符)")


def find_pdf(folder: str, year: int) -> Path | None:
    hits = sorted((SRC / folder).glob(f"{year}年考研英语二真题*.pdf"))
    return hits[0] if hits else None


def main():
    args = [int(a) for a in sys.argv[1:]] or [2010]
    years = range(args[0], (args[1] if len(args) > 1 else args[0]) + 1)
    OUT.mkdir(exist_ok=True)
    for y in years:
        print(f"[{y}]")
        exam = find_pdf("真题", y)
        notes = find_pdf("答案", y)
        if exam:
            extract(exam, OUT / f"{y}_exam.txt")
        else:
            print(f"  !! 找不到 {y} 真题 PDF")
        if notes:
            extract(notes, OUT / f"{y}_notes.txt")
        else:
            print(f"  !! 找不到 {y} 解析 PDF")


if __name__ == "__main__":
    main()
