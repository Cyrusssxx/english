# -*- coding: utf-8 -*-
"""补全 2010-2020 新题型「空位」映射：小标题题 para_no / 匹配题 person。
2010 是 T/F 判断题（空位=题目本身），无需映射，跳过。
"""
import json, re, sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'pwa/data/'

def load(y):
    return json.load(open(f'{BASE}{y}.json', encoding='utf-8'))

def save(y, d):
    json.dump(d, open(f'{BASE}{y}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
      '十': 10, '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15, '十六': 16}

def para_from_expl(ex):
    """从解释提取首个 '第X段'（中文/阿拉伯数字），支持 第四至六段 / 第十一、十二段 """
    m = re.search(r'第\s*([一二三四五六七八九十]{1,3})\s*段', ex)
    if not m:
        m = re.search(r'第\s*(\d{1,2})\s*段', ex)
    if not m:
        return None
    s = m.group(1)
    if s.isdigit():
        return int(s)
    return CN.get(s)

def person_from_stem(stem):
    """匹配/信息题：stem 里左栏标识（人名或作品名）。取第一个大写单词起始、到句末/动词前的连续段。"""
    m = re.search(r'^([A-Z][A-Za-z .\x27]+?)', stem)
    if not m:
        return None
    return m.group(1).strip()

def person_from_expl(ex):
    """从解释 '根据题干XXX定位' 提取人名，2014 作品名去字符间空格。"""
    m = re.search(r'根据题干([A-Za-z][A-Za-z .\x27]{2,}?)(?:定位|迅|，|。|与)', ex)
    if not m:
        m = re.search(r'根据题干([A-Za-z][A-Za-z .\x27]{2,}?)\s*(?:定|位)', ex)
    return m.group(1).strip() if m else None

# ---------------- 逐年份处理 ----------------
# 2011 人物观点匹配：person 从 stem（可手动核验）
P2011 = {41: 'Andrew Lansley', 42: 'Terence Stephenson', 43: 'Jamie Oliver',
         44: 'Dinesh Bhugra', 45: 'A Department of Health spokesperson'}
# 2012 信息匹配：stem 即人名
P2012 = {41: 'Petrarch', 42: 'Niccolò Machiavelli', 43: 'Samuel Smiles',
         44: 'Thomas Carlyle', 45: 'Marx and Engels'}
# 2014 作品匹配：stem 取左栏（去 expl 字符间距空格用）
P2014 = {41: 'Stone Circle', 42: 'Olaf Street Study', 43: 'Across the Park',
         44: 'Towards Avebury', 45: 'Seven Days'}

# 2013 小标题：重建段落结构 + para_no
PARA2013 = {  # sid_suffix: para
    's01_para': 1, 's02_para': 1, 's03_para': 1, 's04_para': 1, 's05_para': 1,
    's06_para': 1, 's07_para': 1, 's08_para': 1, 's09_para': 1, 's10_para': 1,
    's11_para': 2, 's12_para': 2, 's13_para': 2,
    's14_para': 3, 's15_para': 3, 's16_para': 3, 's17_para': 3,
    's18_para': 4, 's19_para': 4, 's20_para': 4,
    's21_para': 5, 's22_para': 5, 's23_para': 5,
    's24_para': 6, 's25_para': 6,
}
# 2015 小标题：重建段落结构 + para_no（原文第 3-7 段设题，前导段并入 para1，缺 para2 不连续）
PARA2015_START = {  # 段起始句序号（s 编号数字）: para
    1: 1, 8: 3, 17: 4, 23: 5, 26: 6, 30: 7,
}

def set_sentence_para(year, mapper):
    d = load(year)
    nt = [a for a in d['articles'] if 'new' in str(a.get('type', ''))][0]
    for s in nt['sentences']:
        n = int(s['id'].split('_s')[1])
        p = mapper(n)
        if p:
            s['para'] = p
    save(year, d)
    print(f'{year}: 段落重建 OK')

# 2013: 25 句直接映射
set_sentence_para(2013, lambda n: next((
    v for k, v in [('s%02d_para' % n, None)] ), None) if False else {
1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,11:2,12:2,13:2,14:3,15:3,16:3,17:3,
18:4,19:4,20:4,21:5,22:5,23:5,24:6,25:6}.get(n))

# 2015: 33 句，按起始点归段
def para2015(n):
    bounds = sorted(((8, 3), (17, 4), (23, 5), (26, 6), (30, 7)))
    cur = 1
    for start, p in bounds:
        if n < start:
            break
        cur = p
    return cur
set_sentence_para(2015, para2015)

# ---------------- person / para_no 写入 ----------------
def patch(y, person_map=None, para_map=None):
    d = load(y)
    nt = [a for a in d['articles'] if 'new' in str(a.get('type', ''))][0]
    for q in nt['questions']:
        n = q['number']
        if person_map and person_map.get(n):
            q['person'] = person_map[n]
        if para_map and para_map.get(n):
            q['para_no'] = para_map[n]
    save(y, d)
    persons = [q.get('person', '') for q in nt['questions']]
    para_nos = [q.get('para_no', '') for q in nt['questions']]
    print(f'{y}: person={persons}, para_no={para_nos}')

patch(2011, P2011)
patch(2012, P2012)
patch(2013, para_map={41: 2, 42: 3, 43: 4, 44: 5, 45: 6})
patch(2014, P2014)
patch(2015, para_map={41: 3, 42: 4, 43: 5, 44: 6, 45: 7})
patch(2016, para_map={41: 2, 42: 3, 43: 4, 44: 5, 45: 6})
# 2017/2019 人物观点匹配：从 expl 提取
for y in (2017, 2019):
    d = load(y)
    nt = [a for a in d['articles'] if 'new' in str(a.get('type', ''))][0]
    for q in nt['questions']:
        if 'person' not in q:
            q['person'] = person_from_expl(q.get('explanation', ''))
    save(y, d)
    print(y, [q.get('person') for q in nt['questions']])
patch(2018, para_map={41: 41, 42: 42, 43: 43, 44: 44, 45: 45})
patch(2020, para_map={41: 2, 42: 3, 43: 4, 44: 5, 45: 6})

print('\n全部写入完成')