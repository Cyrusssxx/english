"""Patch EN1 data files: prefix sentence/question/related ids with 'en1_' so they
don't collide with EN2 ids of the same year (shared IndexedDB for favorites/answers,
and unambiguous chain-corpus lookup).

Idempotent: skips ids that already start with 'en1_'.
"""
import json, glob, os, re

PAT_S = re.compile(r'^\d{4}_text\d+_s\d+$')
PAT_Q = re.compile(r'^\d{4}_text\d+_q\d+$')

def pref(idv):
    if not isinstance(idv, str):
        return idv
    if idv.startswith('en1_'):
        return idv
    if PAT_S.match(idv) or PAT_Q.match(idv):
        return 'en1_' + idv
    return idv

files = sorted(glob.glob('pwa/data/en1/*.json'))
total_s = total_q = total_r = 0
for fp in files:
    d = json.load(open(fp, encoding='utf-8'))
    for a in d.get('articles', []):
        for s in a.get('sentences', []):
            if 'id' in s and s['id'] != pref(s['id']):
                s['id'] = pref(s['id']); total_s += 1
        for q in a.get('questions', []):
            if 'id' in q and q['id'] != pref(q['id']):
                q['id'] = pref(q['id']); total_q += 1
            rs = q.get('related_sentences')
            if isinstance(rs, list):
                new_rs = [pref(x) for x in rs]
                if new_rs != rs:
                    q['related_sentences'] = new_rs
                    total_r += sum(1 for a_, b_ in zip(new_rs, rs) if a_ != b_)
    json.dump(d, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('patched', os.path.basename(fp))

print(f'done: sentences={total_s} questions={total_q} related={total_r}')
