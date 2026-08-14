"""Build pwa/data/chain_corpus.json — a consolidated, dependency-free sentence corpus
used by chain.html (串联词汇). Covers EN2 reading (2007-2025) + EN1 reading (2010-2025).

Each entry: {"id": sentence id, "aid": article id, "exam": "en1"/"en2",
             "year": int, "en": english sentence text,
             "cn": per-sentence 中文译文 (可选, 仅当为真正的逐句译文时嵌入)}

嵌入策略：
- EN2 2010-2025 的句子级 cn 来自早期提取、质量好，且与整篇 ref_cn 不同 → 直接嵌入作为逐句译文。
- 2007-2009 / EN1 的句子 cn 等于整篇 ref_cn（重复整段）→ 不嵌入，交由 chain.html 按 aid 懒加载文章 ref_cn 整篇译文。
- 无 cn 的句子（如 EN1 扫描图年份）→ 不嵌入，回退为「暂无译文」。
"""
import json, glob, os
from datetime import datetime, timezone

OUT = 'pwa/data/chain_corpus.json'
sentences = []

def add_from(path, exam):
    d = json.load(open(path, encoding='utf-8'))
    year = d.get('year')
    for a in d.get('articles', []):
        if not a.get('type', '').startswith('text'):
            continue
        aid = a['id']
        art_ref_cn = a.get('ref_cn') or ''   # 整篇参考译文（2007-2009/EN1 有，EN2 2010-2025 无）
        for s in a.get('sentences', []):
            en = (s.get('en') or '').replace('\n', ' ').strip()
            if not en:
                continue
            sent = {
                'id': s['id'],
                'aid': aid,
                'exam': exam,
                'year': year,
                'en': en,
            }
            # 仅当该 cn 是真正的逐句译文（不等于整篇 ref_cn）时才嵌入
            cn = (s.get('cn') or '').strip()
            if cn and cn != art_ref_cn:
                sent['cn'] = cn
            sentences.append(sent)

# EN2 reading: 2007-2025
for y in range(2007, 2026):
    fp = f'pwa/data/{y}.json'
    if os.path.exists(fp):
        add_from(fp, 'en2')

# EN1 reading: 2010-2025
for fp in sorted(glob.glob('pwa/data/en1/*.json')):
    add_from(fp, 'en1')

out = {
    'built_at': datetime.now(timezone.utc).isoformat(),
    'count': len(sentences),
    'sentences': sentences,
}
open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))

# report size + a sanity check on uniqueness of ids
ids = [s['id'] for s in sentences]
dup = len(ids) - len(set(ids))
print(f'wrote {OUT}: {len(sentences)} sentences, '
      f'en2={sum(1 for s in sentences if s["exam"]=="en2")} '
      f'en1={sum(1 for s in sentences if s["exam"]=="en1")}, '
      f'dup_ids={dup}, size={os.path.getsize(OUT)//1024}KB')
