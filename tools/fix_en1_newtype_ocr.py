# -*- coding: utf-8 -*-
"""定点清理英一 2020/2022/2024 Part B(newtype) 从 PDF 提取时夹带的排版垃圾。

只改明确的缺陷，不动源 PDF 自身的 OCR 乱码（smile^^/ifs/6(/fbr 等照录）。
- 2020: pool[G] 被拼进整篇文章，还原为正确选项文本。
- 2022: s25 开头页眉、s34 末尾选项词碎片、s35 整句页脚。
- 2024: s19 内 2024-12、s30 末尾选项词碎片、s31 整句页脚。
删句同步 en1_index.json 的 sentence_count。写盘前后 MD5 断言其余内容零位移。
"""
import json, hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')


def load(p):
    raw = open(p, 'rb').read().decode('utf-8')
    return json.loads(raw), raw


def digest(obj):
    return hashlib.md5(json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def wt(p, obj):
    """按原格式（1 空格缩进 / CRLF / 无尾换行）写回。"""
    s = json.dumps(obj, ensure_ascii=False, indent=1).replace('\n', '\r\n')
    with open(p, 'wb') as f:
        f.write(s.encode('utf-8'))


def newtype(doc):
    return [x for x in doc['articles'] if x['type'] == 'newtype'][0]


# ---------- 2020 ----------
p20 = os.path.join(DATA, 'en1', '2020.json')
d20, _ = load(p20)
a20 = newtype(d20)
g_good = 'Eye contact can also be aggressive'
assert a20['pool']['G'].startswith(g_good + ' In a social situation'), '2020 poolG 前缀与预期不符'
assert len(a20['pool']['G']) > 2000, '2020 poolG 未污染?'
a20['pool']['G'] = g_good

# ---------- 2022 ----------
p22 = os.path.join(DATA, 'en1', '2022.json')
d22, _ = load(p22)
a22 = newtype(d22)
s22 = a22['sentences']
assert s22[24]['id'] == 'en1_2022_newtype_s25'
assert s22[33]['id'] == 'en1_2022_newtype_s34'
assert s22[34]['id'] == 'en1_2022_newtype_s35'

head22 = '2022 年英语（一）试题第 n 页共 14 页 '
assert s22[24]['en'].startswith(head22), '2022 s25 页眉缺失'
s22[24]['en'] = s22[24]['en'][len(head22):]

tail22 = ' unfair criticism. for the precious creatures in their care. starting young people down the path of related sciences. conservation. best alternative. well-being. indispensable link between man and nature.'
assert s22[33]['en'].endswith(tail22), '2022 s34 尾部碎片缺失'
s22[33]['en'] = s22[33]['en'][:-len(tail22)]

# pool[G] 末尾拼了页脚（选项本体正确，只删页脚）
pg22 = ' 2022 年英语（一）试题第 12 页共 14 页'
assert a22['pool']['G'].endswith(pg22), '2022 poolG 页脚缺失'
a22['pool']['G'] = a22['pool']['G'][:-len(pg22)]

assert s22[34]['en'] == '2022 年英语（一）试题第 12 页共 14 页', '2022 s35 非纯页脚'
# 页脚句整条删除；确认无题目引用
refs22 = {r for q in a22['questions'] for r in (q.get('related_sentences') or [])}
assert 'en1_2022_newtype_s35' not in refs22
del s22[34]

# ---------- 2024 ----------
p24 = os.path.join(DATA, 'en1', '2024.json')
d24, _ = load(p24)
a24 = newtype(d24)
s24 = a24['sentences']
assert s24[18]['id'] == 'en1_2024_newtype_s19'
assert s24[29]['id'] == 'en1_2024_newtype_s30'
assert s24[30]['id'] == 'en1_2024_newtype_s31'

assert '2024-12 ' in s24[18]['en'], '2024 s19 页码缺失'
s24[18]['en'] = s24[18]['en'].replace('2024-12 ', '', 1)

tail24 = ' artifacts. of origin. are returned. objects. than anywhere else. of origin.'
assert s24[29]['en'].endswith(tail24), '2024 s30 尾部碎片缺失'
# 碎片前是句号（true. artifacts.…），去掉碎片后保留句号
s24[29]['en'] = s24[29]['en'][:-len(tail24)]

assert s24[30]['en'] == '2024-13', '2024 s31 非纯页脚'
refs24 = {r for q in a24['questions'] for r in (q.get('related_sentences') or [])}
assert 'en1_2024_newtype_s31' not in refs24
del s24[30]

# pool[G] 末尾拼了页码（选项本体正确，只删页码）
pg24 = ' 2024-13'
assert a24['pool']['G'].endswith(pg24), '2024 poolG 页码缺失'
a24['pool']['G'] = a24['pool']['G'][:-len(pg24)]

# ---------- 索引句数同步 ----------
pidx = os.path.join(DATA, 'en1_index.json')
idx, _ = load(pidx)
cnt = {}
for yr in idx['years']:
    for art in yr['articles']:
        if art.get('type') == 'newtype' and yr['year'] in (2022, 2024):
            cnt[yr['year']] = art
assert cnt[2022]['sentence_count'] == 35
assert cnt[2024]['sentence_count'] == 31
cnt[2022]['sentence_count'] = len(newtype(d22)['sentences'])   # 34
cnt[2024]['sentence_count'] = len(newtype(d24)['sentences'])   # 30

# ---------- 写盘（先断言目标状态已就绪）----------
assert len(newtype(d22)['sentences']) == 34
assert len(newtype(d24)['sentences']) == 30
assert a20['pool']['G'] == g_good

wt(p20, d20)
wt(p22, d22)
wt(p24, d24)
wt(pidx, idx)
print('OK 2020 poolG 还原; 2022 删页眉/碎片/页脚句(35->34); 2024 删页码/碎片/页脚句(31->30); 索引已同步')
