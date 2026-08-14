"""Build pwa/data/en1_index.json — the article catalog for the EN1 (英语一) reading-only
entry. Mirrors index.json schema: {schema_version, exam:"en1", years:[{year, articles:[{id,type,title,topic,sentence_count,question_count}]}]}.
Reading only: type text1-4 from pwa/data/en1/YYYY.json (2010-2025)."""
import json, glob, os

years = []
for fp in sorted(glob.glob('pwa/data/en1/*.json'), reverse=True):
    d = json.load(open(fp, encoding='utf-8'))
    y = d.get('year')
    arts = []
    for a in d.get('articles', []):
        if not a.get('type', '').startswith('text'):
            continue
        arts.append({
            'id': a['id'],
            'type': a['type'],
            'title': a.get('title', ''),
            'topic': a.get('topic', ''),
            'sentence_count': len(a.get('sentences', [])),
            'question_count': len(a.get('questions', [])),
        })
    if arts:
        years.append({'year': y, 'articles': arts})

out = {
    'schema_version': 1,
    'exam': 'en1',
    'years': years,
}
open('pwa/data/en1_index.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=2))
print('wrote pwa/data/en1_index.json with', len(years), 'years,',
      sum(len(y['articles']) for y in years), 'reading articles')
