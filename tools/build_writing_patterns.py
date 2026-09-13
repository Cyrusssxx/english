# -*- coding: utf-8 -*-
'''交叉索引：把 2010-2026 大作文「套用示范」里的关键句型，反向挂进
   「近义词」板块（nearmap：写作句式·同义替换地图）
   「熟词短语」板块（phrasebook：新增「写作句式」类）。
生成物：
  1. pwa/data/writing_patterns.json  —— 规范句型 + 释义 + 例句 + 年份 + 出处链接
  2. pwa/data/phrasebook.json        —— 追加/刷新「写作句式」类（幂等）
  3. pwa/js/nearmap.js               —— 在标记之间插入写作句式地图（幂等，零 fetch）
用法：python tools/build_writing_patterns.py
'''
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
JSDIR = os.path.join(ROOT, 'pwa', 'js')
APPLY_FP = os.path.join(DATA, 'writing_apply.json')
OUT_FP = os.path.join(DATA, 'writing_patterns.json')
PH_FP = os.path.join(DATA, 'phrasebook.json')
NM_FP = os.path.join(JSDIR, 'nearmap.js')

CAT = '写作句式'

# 功能簇（顺序即展示顺序）：名称 / 颜色 / 说明
FUNCS = [
    ('图表引出', '#0d9488', '开篇点图：先说清图是什么、整体呈现什么分布'),
    ('上升趋势', '#ef4444', '描述上涨：rose / climbed / upward trend / momentum'),
    ('幅度·速度', '#f59e0b', '比快慢、比幅度、点出转折点与天花板'),
    ('占比·分布', '#8b5cf6', '静态图三板斧：largest share / middle group / small proportions'),
    ('升降对比·转折', '#10b981', '一升一降 / 被取代 / By contrast——转折表达集中放这里'),
    ('原因·背景', '#f97316', '第二段归因：时代、政策、观念、经济、心态'),
    ('意义·价值', '#eab308', '说好处：gain / facilitate / enrich / an ideal way'),
    ('建议·展望', '#06b6d4', '第三段收尾：pave the way / stay competitive / keep improving'),
    ('主题词·术语', '#64748b', '各话题的固定说法，换题时直接替换'),
]
FUNC_NAMES = [f[0] for f in FUNCS]

# 关键词归类规则（按顺序命中即停）
RULES = [
    ('图表引出', ['uneven distribution', 'uniform direction']),
    ('占比·分布', ['largest share', 'follows closely', 'middle group', 'small proportion',
                   'felt satisfied']),
    ('升降对比·转折', ['contrast', 'declined', 'displaced']),
    ('上升趋势', ['rose', 'climbed', 'upward trend', 'increase occurred', 'momentum']),
    ('幅度·速度', ['pace of growth', 'differed sharply', 'same margin', 'particularly striking',
                   'watershed', 'saturation', 'little room']),
    ('主题词·术语', ['disposable income', 'literacy rate', 'hands-on']),
    ('建议·展望', ['paves the way', 'strike a balance', 'channel more resources', 'to extremes',
                   'keep pace', 'secure an advantage', 'competitive', 'sports facilities',
                   'own initiative', 'give impetus', 'boosted the popularity',
                   'keep improving']),
    ('原因·背景', ['consequence', 'prosperity', 'endeavour', 'priorities', 'shift in',
                   'awareness', 'account of', 'takes off', 'powerlessness', 'plateau',
                   'technology gap', 'joint effects', 'parenting']),
]
DEFAULT_FUNC = '意义·价值'

STOP = {'a', 'an', 'the', 'and', 'or', 'respectively', 'them', 'their', 'that', 'which',
        'where', 'it', 'is', 'are', 'was', 'were', 'this'}

# 少数合并组的规范写法（默认取出现最多的原写法）
CANON_OVERRIDE = {
    'make up relatively small proportion of': 'make up relatively small proportions of …',
}


def nkey(pat):
    s = pat.lower().replace('\u2019', "'")
    out = []
    for t in re.findall(r"[a-z']+", s):
        if t in STOP:
            continue
        if len(t) > 3 and t.endswith('s') and not t.endswith('ss'):
            t = t[:-1]
        out.append(t)
    return ' '.join(out)


def segs(pat):
    parts = [p.strip(' ,.;') for p in re.split(r'\u2026+', pat)]
    return [p for p in parts if len(p) > 2]


def pick_func(canon):
    low = canon.lower()
    for name, kws in RULES:
        for kw in kws:
            if kw in low:
                return name
    return DEFAULT_FUNC


def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', (text or '').replace('\n', ' ')) if s.strip()]


def cn_sentences(text):
    return [s.strip() for s in re.split(r'(?<=[\u3002\uff01\uff1f])', text or '') if s.strip()]


def match_sentence(pat, sents):
    ss = segs(pat)
    if not ss:
        return None
    for s in sents:
        low = s.lower()
        if all(x.lower() in low for x in ss):
            return s
    longest = max(ss, key=len)
    for s in sents:
        if longest.lower() in s.lower():
            return s
    # 再退一级：用句型里最长的特征词定位（如 were displaced → displaced）
    words = [w for w in re.findall(r"[A-Za-z]{6,}", longest)]
    words.sort(key=len, reverse=True)
    for w in words:
        for s in sents:
            if w.lower() in s.lower():
                return s
    return None


def aid_of(year):
    return '%s_writingb' % year


def build():
    apply_data = json.load(open(APPLY_FP, encoding='utf-8'))
    raw = defaultdict(list)   # nkey -> [(year, pat, cn)]
    for y in sorted(apply_data):
        for p in apply_data[y].get('key_phrases', []):
            raw[nkey(p['en'])].append((y, p['en'], p['cn']))

    groups = {f: [] for f in FUNC_NAMES}
    total_raw = 0
    for k, items in raw.items():
        total_raw += len(items)
        # 规范写法：出现次数最多的原写法；并列取最早年份
        cnt = defaultdict(int)
        for y, pat, _ in items:
            cnt[pat] += 1
        canon = CANON_OVERRIDE.get(k)
        if not canon:
            canon = sorted(cnt.items(), key=lambda kv: (-kv[1], items[0][0]))[0][0]
        years = sorted({y for y, _, _ in items})
        meaning = items[0][2]
        # 例句：优先取「中英句数对齐」的年份，保证译文不会错位
        en_ex = cn_ex = ''
        fallback = ''
        for y, _, _ in items:
            a = apply_data[y]
            sents = sentences(a.get('apply_en'))
            hit = match_sentence(canon, sents)
            if not hit:
                continue
            if not fallback:
                fallback = hit
            cns = cn_sentences(a.get('apply_cn'))
            if len(cns) == len(sents):
                en_ex, cn_ex = hit, cns[sents.index(hit)]
                break
        if not en_ex:
            en_ex = fallback
        variants = sorted(cnt.keys(), key=lambda p: (p != canon, p))
        func = pick_func(canon)
        groups[func].append({
            'w': canon,
            'meaning': meaning,
            'en': en_ex,
            'cn': cn_ex,
            'years': years,
            'freq': len(years),
            'aid': aid_of(years[-1]),
            'variants': variants if len(variants) > 1 else [],
        })

    for f in groups:
        groups[f].sort(key=lambda x: (-x['freq'], x['w'].lower()))
    payload = {
        'count': sum(len(v) for v in groups.values()),
        'raw_count': total_raw,
        'cat': CAT,
        'funcs': [{'name': n, 'color': c, 'desc': d} for n, c, d in FUNCS],
        'groups': groups,
    }
    json.dump(payload, open(OUT_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入 writing_patterns.json：原始 %d 条 → 规范 %d 条' % (total_raw, payload['count']))
    for f in FUNC_NAMES:
        print('  %-8s %d 条' % (f, len(groups[f])))
    return payload


def merge_phrasebook(payload=None):
    '''把「写作句式」类并入 phrasebook.json（幂等：先删同名类再追加）'''
    payload = payload or json.load(open(OUT_FP, encoding='utf-8'))
    ph = json.load(open(PH_FP, encoding='utf-8'))
    cats = [c for c in ph.get('cats', []) if c != CAT]
    groups = {k: v for k, v in ph.get('groups', {}).items() if k != CAT}
    rows = []
    for f in payload['funcs']:
        for e in payload['groups'].get(f['name'], []):
            rows.append({
                'w': e['w'],
                'meaning': e['meaning'],
                'en': e['en'],
                'cn': e['cn'],
                'src': '英语二大作文 · 套用示范（%s）' % ('/'.join(e['years'])),
                'year': e['years'][-1],
                'years': e['years'],
                'freq': e['freq'],
                'func': f['name'],
                'variants': e['variants'],
                'aid': e['aid'],
            })
    rows.sort(key=lambda r: (FUNC_NAMES.index(r['func']), -r['freq'], r['w'].lower()))
    cats.append(CAT)
    groups[CAT] = rows
    ph['cats'] = cats
    ph['groups'] = groups
    ph['count'] = sum(len(v) for v in groups.values())
    json.dump(ph, open(PH_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('并入 phrasebook.json：新增 / 刷新「%s」类 %d 条，总计 %d 条' % (CAT, len(rows), ph['count']))


NM_START = '  /* >>> 写作句式（tools/build_writing_patterns.py 自动生成，勿手改） >>> */'
NM_END = '  /* <<< 写作句式 <<< */'


def inject_nearmap(payload=None):
    '''把写作句式地图内联进 nearmap.js（零 fetch）'''
    payload = payload or json.load(open(OUT_FP, encoding='utf-8'))
    branches = []
    for f in payload['funcs']:
        items = payload['groups'].get(f['name'], [])
        if not items:
            continue
        children = []
        for e in items:
            tail = ('%d 年' % e['freq']) if e['freq'] > 1 else e['years'][-1]
            children.append({
                'name': '%s %s · %s' % (e['w'], e['meaning'], tail),
                'en': e['w'],
                'rest': '%s · %s' % (e['meaning'], tail),
            })
        branches.append({'name': '%s（%d）' % (f['name'], len(items)), 'color': f['color'],
                         'children': children})
    m = {
        'id': 'writing',
        'title': '写作句式 · 同义替换（大作文 2010-2026）',
        'root': '写作句式',
        'rootColor': '#0d9488',
        'intro': ('来源：2010-2026 英语二大作文「真题套用示范」里的关键句型，按写作功能成簇。'
                  '写大作文时同簇表达换着用（如「占比最大」有 3 种说法、「上升」有 5 种说法），'
                  '就不会通篇 rose / increase 重复。中文即该句型的用法，尾部数字为出现年份数——'
                  '数字越大越是高频万能句。'),
        'branches': branches,
    }
    block = NM_START + '\n  DATA.maps.push(' + json.dumps(m, ensure_ascii=False, indent=2) + ');\n' + NM_END
    src = open(NM_FP, encoding='utf-8').read()
    if NM_START in src and NM_END in src:
        src = re.sub(re.escape(NM_START) + r'.*?' + re.escape(NM_END), lambda _: block, src, flags=re.S)
    else:
        anchor = '  function esc(s) {'
        if anchor not in src:
            raise SystemExit('nearmap.js 找不到插入锚点')
        src = src.replace(anchor, block + '\n\n' + anchor, 1)
    open(NM_FP, 'w', encoding='utf-8', newline='\n').write(src)
    print('注入 nearmap.js：%d 个功能簇 / %d 条句型' % (len(branches), sum(len(b['children']) for b in branches)))


def main():
    payload = build()
    merge_phrasebook(payload)
    inject_nearmap(payload)


if __name__ == '__main__':
    main()
