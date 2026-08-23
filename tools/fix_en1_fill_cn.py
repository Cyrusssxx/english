"""en1 数据修复 · 逐句 cn 兜底回填

en1 约定: 每句 cn 应 = 整篇 ref_cn (点击任意句可读整篇译文)。
部分篇(2018-2021)的 ref_cn 已抽好但句子级 cn 漏填 -> 把 ref_cn 回填到每句 cn。
ref_cn 本身残/空的篇不强行拼(源PDF无整篇译文), 仅回填已有 ref_cn。

用法:
  python tools/fix_en1_fill_cn.py            # 真写回
  python tools/fix_en1_fill_cn.py --dry      # 仅报告
"""
import json, os, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN1_DIR = os.path.join(ROOT, "pwa", "data", "en1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(EN1_DIR, "*.json")),
                   key=lambda x: int(os.path.basename(x)[:-5]))
    total = 0
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        changed = False
        for a in d.get("articles", []):
            rc = (a.get("ref_cn") or "").strip()
            if not rc:
                continue
            for s in a.get("sentences", []):
                if not s.get("cn"):
                    s["cn"] = rc
                    total += 1
                    changed = True
        if changed and not args.dry:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # 报告该篇剩余逐句cn缺口
        for a in d.get("articles", []):
            sents = a.get("sentences", [])
            ncn = sum(1 for s in sents if s.get("cn"))
            if ncn < len(sents):
                rclen = len(a.get("ref_cn") or "")
                print(f"{a['id']:18s} 仍缺逐句cn={len(sents)-ncn}/{len(sents)} (ref_cn={rclen}字)")
    print(f"\n[dry={args.dry}] 回填逐句cn={total} 句")


if __name__ == "__main__":
    main()
