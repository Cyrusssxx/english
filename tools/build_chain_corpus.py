"""Build pwa/data/chain_corpus.json — a consolidated, dependency-free sentence corpus
used by chain.html (串联词汇). Covers EN2 reading (2007-2025) + EN1 reading (2010-2025).

Each entry: {"id": sentence id, "aid": article id, "exam": "en1"/"en2",
             "year": int, "en": english sentence text}

Translation (ref_cn) is intentionally NOT embedded here (it's whole-passage and heavy);
chain.html lazy-loads an article's ref_cn on demand via storage getArticle.
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
        for s in a.get('sentences', []):
            en = (s.get('en') or '').replace('\n', ' ').strip()
            if not en:
                continue
            sentences.append({
                'id': s['id'],
                'aid': aid,
                'exam': exam,
                'year': year,
                'en': en,
            })

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
