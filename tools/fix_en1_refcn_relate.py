"""en1 数据修复 · 阶段一（可靠，不依赖解析 PDF）

1) ref_cn（全文参考译文）：用每篇文章句子级 cn 按段落拼装，
   修复原先截断/垃圾的 ref_cn（覆盖全部 16 年）。
2) related_sentences（定位原文依据）：题干+选项英文关键词与文章句子做
   重叠打分，取 top1-2 写入每题（修复全部为空的问题）。

用法：
    python tools/fix_en1_refcn_relate.py           # 真写回
    python tools/fix_en1_refcn_relate.py --dry      # 只报告不写回
"""
import json, os, glob, re, sys, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN1_DIR = os.path.join(ROOT, "pwa", "data", "en1")

STOP = set("""a an the and or but if while of to in on at by for with from into as is are was were be been being
this that these those it its their his her our your my we they he she you i them him us me
which who whom whose what when where why how not no nor so than then there here all any some
more most other another such same one two three first second can could may might will would
should shall must do does did done has have had having about over under between against through
they're we're you're it's that's he's she's i'm don't doesn't didn't won't can't cannot""".split())

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'\-]+")


def tokens(text):
    out = []
    for m in TOKEN_RE.findall(text or ""):
        w = m.lower()
        if len(w) <= 3 or w in STOP:
            continue
        out.append(w)
    return out


def build_ref_cn(article):
    """按 para 分组拼装全文译文。"""
    paras = {}
    for s in article.get("sentences", []):
        cn = (s.get("cn") or "").strip()
        if not cn:
            continue
        p = s.get("para") or 1
        paras.setdefault(p, []).append(cn)
    if not paras:
        return ""
    # 段落按数字顺序，段间空行
    parts = []
    for p in sorted(paras.keys()):
        parts.append("\n".join(paras[p]))
    return "\n\n".join(parts)


def build_related(article):
    """为每题找 top1-2 相关句（基于题干+选项英文关键词重叠）。"""
    sents = article.get("sentences", [])
    if not sents:
        return {}
    sent_text = {}
    sent_tokens = {}
    for s in sents:
        t = (s.get("en") or "")
        sent_text[s["id"]] = t.lower()
        sent_tokens[s["id"]] = set(tokens(t))
    result = {}
    for q in article.get("questions", []):
        qtext = (q.get("stem") or "") + " " + " ".join((q.get("options") or {}).values())
        qt = set(tokens(qtext))
        if not qt:
            continue
        scored = []
        for sid, stoks in sent_tokens.items():
            if not stoks:
                continue
            overlap = len(qt & stoks)
            if overlap > 0:
                scored.append((overlap, sid))
        scored.sort(key=lambda x: -x[0])
        picked = [sid for _, sid in scored[:2]]
        result[q.get("id")] = picked
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报告不写回")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(EN1_DIR, "*.json")),
                   key=lambda x: int(os.path.basename(x)[:-5]))
    total_ref = 0
    total_rel = 0
    for f in files:
        y = int(os.path.basename(f)[:-5])
        d = json.load(open(f, encoding="utf-8"))
        changed = False
        for a in d.get("articles", []):
            new_ref = build_ref_cn(a)
            old_ref = (a.get("ref_cn") or "").strip()
            if new_ref and new_ref != old_ref:
                a["ref_cn"] = new_ref
                total_ref += 1
                changed = True
            rel = build_related(a)
            for q in a.get("questions", []):
                picked = rel.get(q.get("id"), [])
                if picked and q.get("related_sentences") != picked:
                    q["related_sentences"] = picked
                    total_rel += 1
                    changed = True
        if changed and not args.dry:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        # 报告
        for a in d.get("articles", []):
            nrel = sum(1 for q in a.get("questions", []) if q.get("related_sentences"))
            rlen = len(a.get("ref_cn") or "")
            print(f"{a['id']:18s} ref_cn={rlen:4d}  q_with_rel={nrel}/{len(a.get('questions', []))}")
    print(f"\n[dry={args.dry}] ref_cn 更新 {total_ref} 篇, related_sentences 更新 {total_rel} 题")


if __name__ == "__main__":
    main()
