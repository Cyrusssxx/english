import json, io, os

for y in range(2010, 2026):
    rfn = f'tools/extracted/modules/_reserve_{y}.json'
    extra_fn = f'tools/extracted/modules/{y}_extra.json'
    if not os.path.exists(rfn):
        continue
    reserve = json.load(io.open(rfn, encoding='utf-8'))
    extra = json.load(io.open(extra_fn, encoding='utf-8'))
    for a in extra.get('articles', []):
        t = a['type']
        if t in reserve:
            # 只保留 reserve 中非空键
            data = {k: v for k, v in reserve[t].items() if v}
            if data:
                a['reserve'] = data
    json.dump(extra, io.open(extra_fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(y, 'merged')
