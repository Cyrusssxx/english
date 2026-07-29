"""OCR 提取扫描版解析 PDF（2023/2024/2025）。

用途：2023/2024/2025 的《考研英语二真题解析》PDF 为扫描图片版，无文本层，
无法用 PyMuPDF 直接取字。此脚本用 RapidOCR 逐页识别，输出纯文本供人工核对与建库。

用法:
    python -X utf8 tools/ocr_notes.py 2023
    python -X utf8 tools/ocr_notes.py 2023 2024 2025
    python -X utf8 tools/ocr_notes.py 2025 --exam     # OCR 真题而非解析

输出: tools/extracted/{year}_notes_ocr.txt / {year}_exam_ocr.txt
"""
import os
import sys
import time

import numpy as np
from PIL import Image
import fitz
from rapidocr_onnxruntime import RapidOCR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "tools", "extracted")
SRC_BASE = r"D:\ai code\英语二考研试题和答案"

NOTES_DIR = os.path.join(SRC_BASE, "答案")
EXAM_DIR = os.path.join(SRC_BASE, "真题")

EXAM_NAMES = {
    2023: "2023年考研英语二真题【可复制搜索查词】.pdf",
    2024: "2024年考研英语二真题.pdf",
    2025: "2025年考研英语二真题【后续更新正式版】.pdf",
}

DPI = 200

# 水印页判定：2023 等扫描版解析的“有文本层”其实是满页水印
# （“配套/音频/VX/KZ”重复堆叠），整页仅十余种不同字符；
# 而真实解析正文页含中英文混排，不同字符数通常数百。
MIN_NATIVE_CHARS = 400
MIN_UNIQUE_CHARS = 80


def is_watermark(text):
    """判断文本层内容是否为无意义水印（字符多样性极低）。"""
    return len(set(text)) < MIN_UNIQUE_CHARS


def notes_path(year):
    return os.path.join(NOTES_DIR, str(year) + "年考研英语二真题解析.pdf")


def exam_path(year):
    name = EXAM_NAMES.get(year)
    if not name:
        return None
    return os.path.join(EXAM_DIR, name)


def ocr_pdf(pdf_path, out_path, ocr):
    """逐页渲染 + OCR，写出带页标记的文本。"""
    doc = fitz.open(pdf_path)
    total = len(doc)
    mat = fitz.Matrix(DPI / 72, DPI / 72)
    chunks = []
    t0 = time.time()

    for i, page in enumerate(doc):
        # 若该页本身有文本层，直接用（更准，且保留英文空格）
        native = page.get_text("text").strip()
        # 仅当文本层内容足够长且字符多样（非水印）时才直接采用
        if len(native) > MIN_NATIVE_CHARS and not is_watermark(native):
            body = native
            tag = "native"
        else:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            result, _ = ocr(np.array(img))
            body = "\n".join(r[1] for r in result) if result else ""
            tag = "ocr"

        chunks.append("\n===== [page %d] (%s) =====\n%s" % (i + 1, tag, body))
        print("  page %d/%d  %s  chars=%d  (%.1fs)"
              % (i + 1, total, tag, len(body), time.time() - t0), flush=True)

    doc.close()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chunks))
    print("  -> %s (%d bytes, %.1fs)"
          % (out_path, os.path.getsize(out_path), time.time() - t0))


def main():
    args = [a for a in sys.argv[1:]]
    want_exam = "--exam" in args
    years = [int(a) for a in args if a.isdigit()]
    if not years:
        years = [2023, 2024, 2025]

    ocr = RapidOCR()
    for year in years:
        if want_exam:
            src = exam_path(year)
            out = os.path.join(OUT_DIR, "%d_exam_ocr.txt" % year)
        else:
            src = notes_path(year)
            out = os.path.join(OUT_DIR, "%d_notes_ocr.txt" % year)

        if not src or not os.path.exists(src):
            print("MISSING:", src)
            continue
        print("=" * 70)
        print("OCR", year, "exam" if want_exam else "notes", ":", os.path.basename(src))
        ocr_pdf(src, out, ocr)


if __name__ == "__main__":
    main()
