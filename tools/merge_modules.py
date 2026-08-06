"""合并 tools/extracted/modules/*_extra.json 到 pwa/data/{year}.json，并同步 index.json"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pwa' / 'data'
MODULES = Path(__file__).resolve().parent / 'extracted' / 'modules'

# 文章类型排序（与前端 index.html 一致）
ORDER = ['text1', 'text2', 'text3', 'text4', 'newtype', 'cloze', 'translation', 'writing_a', 'writing_b']

for mf in sorted(MODULES.glob('*_extra.json')):
    year = mf.stem.replace('_extra', '')
    d = json.loads(mf.read_text(encoding='utf-8'))
    year_path = DATA / f'{year}.json'
    data = json.loads(year_path.read_text(encoding='utf-8'))
    extra_ids = {a['id'] for a in d['articles']}
    # 移除旧的 extra 文章，追加新的
    data['articles'] = [a for a in data['articles'] if a['id'] not in extra_ids]
    data['articles'].extend(d['articles'])
    data['articles'].sort(key=lambda a: (ORDER.index(a['type']) if a['type'] in ORDER else 99, a['id']))
    year_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{year}.json -> {len(data["articles"])} 篇')

# index.json 同步
idx_path = DATA / 'index.json'
idx = json.loads(idx_path.read_text(encoding='utf-8'))
for y in idx['years']:
    year = str(y['year'])
    year_path = DATA / f'{year}.json'
    data = json.loads(year_path.read_text(encoding='utf-8'))
    arts = data['articles']
    y['articles'] = [
        {
            'id': a['id'], 'type': a['type'],
            'title': a.get('title', ''), 'topic': a.get('topic', ''),
            'sentence_count': len(a.get('sentences', [])),
            'question_count': len(a.get('questions', [])),
        }
        for a in arts
    ]
    y['articles'].sort(key=lambda a: (ORDER.index(a['type']) if a['type'] in ORDER else 99, a['id']))
idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding='utf-8')
print('index.json 同步完成')
