"""Append EN2 2007/2008/2009 reading (text1-4) entries to pwa/data/index.json,
matching the existing entry schema {id,type,title,topic,sentence_count,question_count}.

Strategy: load current index.json as text, build the three year blocks, and insert
them right before the final `  ]\n}` (the years-array closer) so the rest of the
file is preserved byte-for-byte. Blocks use 4-space base indent to nest under "years": [.
"""
import json

IDX = 'pwa/data/index.json'

text = open(IDX, encoding='utf-8').read()
idx = json.loads(text)

existing_years = {y['year'] for y in idx['years']}

def block_for(year):
    d = json.load(open(f'pwa/data/{year}.json', encoding='utf-8'))
    arts = []
    for a in d['articles']:
        arts.append({
            'id': a['id'],
            'type': a['type'],
            'title': a.get('title', ''),
            'topic': a.get('topic', ''),
            'sentence_count': len(a.get('sentences', [])),
            'question_count': len(a.get('questions', [])),
        })
    return {'year': year, 'articles': arts}

# descending order 2009,2008,2007 to keep a tidy block (UI sorts anyway)
new_blocks = [block_for(y) for y in (2009, 2008, 2007) if y not in existing_years]

# render each block with indent=2, then add 4 leading spaces to every line
def render_block(b):
    s = json.dumps(b, ensure_ascii=False, indent=2)
    return '\n'.join(('    ' + line if line else line) for line in s.split('\n'))

insert = ',\n'.join(render_block(b) for b in new_blocks)

marker = '  ]\n}'
pos = text.rfind(marker)
if pos < 0:
    raise SystemExit('years closer "  ]\\n}" not found')

head = text[:pos]          # ends with the last existing article "    }"
new_text = head + ',\n' + insert + '\n' + marker

open(IDX, 'w', encoding='utf-8').write(new_text)

# verify it still parses and the new years are present
chk = json.loads(new_text)
added = [y['year'] for y in chk['years'] if y['year'] in (2007, 2008, 2009)]
print('OK. index now has years:', sorted([y['year'] for y in chk['years']], reverse=True)[:6], '...')
print('added blocks for:', added)
for y in added:
    yy = next(x for x in chk['years'] if x['year'] == y)
    print(f'  {y}:', [(a["id"], a["type"], a["sentence_count"], a["question_count"]) for a in yy["articles"]])
