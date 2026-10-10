# -*- coding: utf-8 -*-
"""完形·翻译词库 一期数据管线（完形部分）v2
产出 pwa/data/wnlex.json：
  1) 完形选项单词（词形归并去重，分类：逻辑衔接 / 核心实词）
  2) 完形选项词组（首词归并，cat=搭配）
  3) 纯介词选项 → 介词搭配还原（v/n + prep，语料=完形正文+题干，须命中 ECDICT/手写表），cat=搭配
  4) 完形来源熟词僻义（wordnotes.json，cat=僻义）
每条字段：id/w/part/cat/cn/common/uncommon/freq/freq_note/diff/diff_val/score/sent/sent_cn/src/year
综合分 score = cat内freq_norm*60 + diff_norm*40（生成端算好，前端直接用）
"""
import csv, io, json, re, sys, glob
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
ECDICT = 'tools/ecdict.csv'
OUT = 'pwa/data/wnlex.json'
WORDNOTES = 'pwa/data/wordnotes.json'

# ---------------- ECDICT 加载 ----------------
EC = {}
with io.open(ECDICT, encoding='utf-8', newline='') as f:
    for row in csv.DictReader(f):
        w = (row.get('word') or '').strip().lower()
        if not w or w in EC:
            continue
        raw = row.get('translation') or ''
        # 关键：ECDICT translation 内含字面 "\n"（反斜杠+n），统一替换为中文分号
        tr = raw.replace('\\n', '；').replace('\n', '；')
        def _rank(x):
            try:
                v = int(x or 0)
                return v if v > 0 else 10 ** 9
            except Exception:
                return 10 ** 9
        EC[w] = {'tr': tr, 'tag': row.get('tag') or '', 'ex': row.get('exchange') or '',
                 'rank': min(_rank(row.get('bnc')), _rank(row.get('frq')))}
print('ECDICT 载入', len(EC))

POS_RE = re.compile(r'\b(n|v|adj|adv|prep|conj|pron|art|num|aux|int|vi|vt|abbr)\.')

def poses(w):
    return set(POS_RE.findall(EC.get(w, {}).get('tr', '')))

def lemma(w):
    ex = EC.get(w, {}).get('ex', '')
    m = re.search(r'0:([a-z\'\-]+)', ex)
    return m.group(1) if m else w

def diff_of(w):
    """难度按 BNC/FRQ 词频排名：≤3000 易 / ≤15000 中 / 其余或无数据 难"""
    rank = EC.get(w, {}).get('rank', 10 ** 9)
    if rank <= 3000:
        return '易', 1
    if rank <= 15000:
        return '中', 2
    return '难', 3

def brief_cn(w, limit=3, width=64):
    tr = EC.get(w, {}).get('tr', '')
    if not tr:
        return ''
    items = []
    for it in tr.split('；'):
        it = it.strip()
        if it and not it.startswith('[法]'):      # 滤掉法律标签义项噪音
            items.append(it)
    out, total = [], 0
    for it in items[:limit]:
        if len(it) > 28:
            it = it[:28] + '…'
        out.append(it)
        total += len(it)
        if total >= width:
            break
    return '；'.join(out)

# ---------------- 完形语料收集 ----------------
opt_words, opt_phrases = Counter(), Counter()
corpus_sents = []          # 完形句子 dict + aid（介词搭配还原 + 原句回填）
sent_of_num = {}           # (aid, qnum) -> sentence
aids = []
PHRASE_FIX = {             # 选项词形 → 规范词条词形
    'concerned with': 'be concerned with',
    'did away': 'do away (with)',
    'do away': 'do away (with)',
}
for f in sorted(glob.glob('pwa/data/20*.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    for a in d.get('articles', []):
        if a.get('type') != 'cloze':
            continue
        aid = a['id']
        aids.append(aid)
        year = aid[:4]
        for s in a.get('sentences', []):
            corpus_sents.append({'aid': aid, 'year': year, 's': s})
            for m in re.finditer(r'\[(\d+)\]', s.get('en', '')):   # 一句可含多个空位
                sent_of_num[(aid, int(m.group(1)))] = s
        for q in a.get('questions', []):
            for o in (q.get('options') or {}).values():
                o = str(o).strip().lower()
                if not o:
                    continue
                if ' ' in o:
                    o = re.sub(r"[()]", '', o)
                    opt_phrases[o] += 1
                else:
                    opt_words[o] += 1
print('完形', len(aids), '篇 | 选项词', len(opt_words), '| 选项词组', len(opt_phrases))

# ---------------- 分类与归并 ----------------
CONJ_EXTRA = {'however', 'therefore', 'thus', 'instead', 'moreover', 'nevertheless',
              'otherwise', 'meanwhile', 'accordingly', 'consequently', 'hence',
              'likewise', 'furthermore', 'nonetheless', 'conversely'}

# 完形选项中作介词/限定词用的词（无独立实义，不成词条 → 还原为真题搭配）
PREP_ONLY = {'from', 'with', 'into', 'in', 'on', 'to', 'by', 'under', 'across',
             'around', 'without', 'among', 'against', 'unlike', 'another'}

rows = []
word_merged, word_src = Counter(), {}
for w, c in opt_words.items():
    L = lemma(w)
    word_merged[L] += c
    word_src.setdefault(L, (w, None))   # 占位，原句回填时用 opt_q 定位
print('归并后单词:', len(word_merged))

pure_preps = []
for w, freq in word_merged.items():
    ps = poses(w)
    if 'conj' in ps or w in CONJ_EXTRA:
        cat = '衔接'
    elif w in PREP_ONLY:
        pure_preps.append(w)
        continue                  # 孤立介词/限定词：走搭配还原，不单独成条
    else:
        cat = '实词'
    diff, dv = diff_of(w)
    rows.append({
        'id': 'cloze:' + w, 'w': w, 'part': 'cloze', 'cat': cat,
        'cn': brief_cn(w), 'freq': freq, 'freq_note': '完形选项×%d' % freq,
        'diff': diff, 'diff_val': dv,
    })
print('纯介词(进搭配还原):', sorted(pure_preps))

# —— 词组：首词归并 + 词形修正 ——
ph_merged, ph_src = Counter(), {}
for p, c in opt_phrases.items():
    toks = p.split()
    toks[0] = lemma(toks[0])
    P = ' '.join(toks)
    P = PHRASE_FIX.get(P, P)
    ph_merged[P] += c
    ph_src.setdefault(P, p)
print('归并后词组:', len(ph_merged))

PHRASE_CN = {
    'be concerned with': '与…有关；涉及',
    'do away (with)': '废除；去掉；消灭',
    'by this means': '通过这种方式',
    'at that point': '在那个时刻；到那一步',
    'in the height of': '在…的鼎盛时期（如盛夏）',
    "throw one's weight behind": '全力支持；动用影响力支持',
    'in respects of': '在…方面',
    'need to': '需要；有必要',
    'focus on': '聚焦于；集中于',
    'base on': '基于；以…为基础',
    'communicate with': '与…交流；沟通',
    'come across': '偶然遇到；被理解',
    'grow into': '成长为；逐渐适应',
    'divide into': '把…分成；划分为',
}

def phrase_cn(p):
    if p in PHRASE_CN:
        return PHRASE_CN[p]
    return brief_cn(p, limit=2, width=48)

miss_cn = []
for p, freq in ph_merged.items():
    cn = phrase_cn(p)
    if not cn:
        miss_cn.append(p)
        continue
    rows.append({
        'id': 'cloze:' + p, 'w': p, 'part': 'cloze', 'cat': '搭配',
        'cn': cn, 'freq': freq, 'freq_note': '完形选项×%d' % freq,
        'diff': '中', 'diff_val': 2,
    })
print('词组缺释义(丢弃):', miss_cn)

# —— 纯介词 → 搭配还原（须命中 ECDICT/手写表） ——
STOP_L = set('the a an and or of to in on at by for with as is are was were be been being '
             'that this these those it its his her their our your my not no so if then '
             'than when which who whom whose what where how will would can could shall '
             'should may might must do does did have has had from into onto about after '
             'before under over between among through during since until while because '
             'although though unless whether there here they we you he she i'.split())
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
prep_pairs = defaultdict(Counter)
prep_loc = {}                  # 搭配 -> 首个含它的句子 dict
for item in corpus_sents:
    text = item['s'].get('en', '')
    low = text.lower()
    for p in pure_preps:
        for m in re.finditer(r"([A-Za-z][A-Za-z'-]{2,})\s+" + p + r"\b", low):
            L = lemma(m.group(1))
            if L in STOP_L or len(L) < 3 or L in pure_preps:
                continue
            if not (poses(L) & {'n', 'v', 'vi', 'vt', 'adj'}):
                continue
            key = L + ' ' + p
            prep_pairs[p][L] += 1
            prep_loc.setdefault(key, item['s'])

prep_cand = Counter()
for p, cnts in prep_pairs.items():
    for L, c in cnts.most_common(2):
        prep_cand[L + ' ' + p] += c
_ = prep_loc

existing = {r['w'] for r in rows}
added_prep = 0
prep_src = {}
for p, freq in prep_cand.most_common():
    if p in existing:
        continue
    cn = phrase_cn(p)
    if not cn:
        continue                 # 未命中 ECDICT/手写表 → 不收（宁可缺不滥）
    _s = prep_loc.get(p)
    rows.append({
        'id': 'cloze:' + p, 'w': p, 'part': 'cloze', 'cat': '搭配',
        'cn': cn, 'freq': 1, 'freq_note': '正文搭配',
        'diff': '中', 'diff_val': 2,
        'sent': (_s or {}).get('en', ''), 'sent_cn': (_s or {}).get('cn', ''),
        'src': ((_s or {}).get('en', '') and '完形正文搭配'),
        'year': '',
    })
    prep_src[p] = True
    existing.add(p)
    added_prep += 1
print('介词搭配还原收录:', added_prep, [p for p in prep_src])

# —— 完形来源熟词僻义 ——
wn = json.load(io.open(WORDNOTES, encoding='utf-8'))
TIER_DV = {'高': ('难', 3), '中': ('中', 2), '低': ('易', 1)}
n_wn = 0
for r in wn.get('rows', []):
    if '完形' not in (r.get('src') or ''):
        continue
    diff, dv = TIER_DV.get(r.get('tier', '中'), ('中', 2))
    rows.append({
        'id': 'cloze:pz:' + r['w'], 'w': r['w'], 'part': 'cloze', 'cat': '僻义',
        'cn': r.get('uncommon', ''), 'common': r.get('common', ''),
        'uncommon': r.get('uncommon', ''),
        'freq': r.get('n', 1), 'freq_note': '全库×%d' % r.get('n', 1),
        'diff': diff, 'diff_val': dv,
        'sent': r.get('en', ''), 'sent_cn': r.get('cn', ''), 'src': r.get('src', ''),
        'year': r.get('year', ''),
    })
    n_wn += 1
print('熟词僻义(完形来源):', n_wn)

# ---------------- 原句回填 ----------------
# 选项（归并后）-> (aid, qnum)：收集阶段重扫一遍建立映射
opt_q = {}                 # (aid, merged_key) -> qnum
for f in sorted(glob.glob('pwa/data/20*.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    for a in d.get('articles', []):
        if a.get('type') != 'cloze':
            continue
        for q in a.get('questions', []):
            n = int(q.get('number') or 0)
            for o in (q.get('options') or {}).values():
                o = str(o).strip().lower()
                if not o:
                    continue
                o = re.sub(r"[()]", '', o)
                toks = o.split()
                if toks:
                    toks[0] = lemma(toks[0])
                key = PHRASE_FIX.get(' '.join(toks), ' '.join(toks))
                opt_q.setdefault((a['id'], key), n)

no_sent = 0
for r in rows:
    if r['part'] != 'cloze' or r.get('sent'):
        continue
    w = r['w']
    # 1) 选项定位：该词首次出现的文章 + 题号 → 题干句
    aid_first = next((a for a in aids if opt_q.get((a, w))), None)
    n = opt_q.get((aid_first, w)) if aid_first else None
    s = sent_of_num.get((aid_first, n)) if aid_first and n else None
    if s:
        r['sent'] = s.get('en', '')
        r['sent_cn'] = s.get('cn', '')
        r['src'] = '%s 英语二 · 完形 第%d题选项' % (aid_first[:4], n)
        continue
    # 2) 介词搭配/其他：在完形正文找首个含该搭配的句子
    pat = re.compile(r"\b" + re.escape(w) + r"\b", re.I)
    for item in corpus_sents:
        if pat.search(item['s'].get('en', '')):
            r['sent'] = item['s'].get('en', '')
            r['sent_cn'] = item['s'].get('cn', '')
            r['src'] = item['year'] + ' 英语二 · 完形正文'
            break
    if not r.get('sent'):
        no_sent += 1
print('无原句条目:', no_sent, '/', len(rows))

# ---------------- 综合分 ----------------
cat_max = defaultdict(int)
for r in rows:
    cat_max[r['cat']] = max(cat_max[r['cat']], r['freq'])
for r in rows:
    fn = r['freq'] / max(cat_max[r['cat']], 1)
    dn = r['diff_val'] / 3.0
    r['score'] = round(fn * 60 + dn * 40, 1)

rows.sort(key=lambda r: -r['score'])
out = {'count': len(rows), 'rows': rows}
io.open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print()
print('== 产出', OUT, '| 共', len(rows), '条 ==')
from collections import Counter as C
print('按类别:', dict(C(r['cat'] for r in rows)))
print('按难度:', dict(C(r['diff'] for r in rows)))
print('Top12 预览:')
for r in rows[:12]:
    print(f"  [{r['cat']}] {r['w']}  {r['cn'][:34]}  {r['freq_note']} {r['diff']} s={r['score']}")
print('衔接类全量:', [r['w'] for r in rows if r['cat'] == '衔接'])
