# -*- coding: utf-8 -*-
"""
熟词僻义 v2 合池 + 判义工作流

  python tools/wn2.py pool             # 建合池工作表（deck 池 + 大纲词扩展池）
  python tools/wn2.py show 0 60        # 打印第 0~60 个词供判义
  python tools/wn2.py show 60 60
  python tools/wn2.py build            # 读 decisions -> 生成板块数据
  python tools/wn2.py stat             # 进度统计
"""
import json
import os
import re
import sys
import csv
import glob
import collections

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
TOOLS = os.path.join(ROOT, 'tools')

STOP = set('''a an the of to in on at for with by from about as is are was were be been being do does did have has had
it its this that these those their them they we you he she his her our your i not no nor or and but so if then than
most more some any all both each other another such which who whom whose when where why how what while because
can could will would should may might must shall into over under between among against during before after above
through out off up down again once here there just very only also too quite rather'''.split())

# 纯功能词/基础词：在真题里不可能有"僻义"，直接排除（省判义工时）
FUNC = set('''say says said one ones people person make makes made making new newer newest news time times
year years need needs needed many us our we you they them their it its he she his her him i me my mine
think thinks thought way ways much more most less least life lives go goes went gone get gets got gotten
come comes came become becomes became better best good well now then here there also too very only just
even still yet again once ever never always often sometimes soon later early late today tomorrow yesterday
first second third last next other others another same different such own very quite rather almost about
do does did done doing have has had having be is am are was were been being will would shall should can
could may might must not no nor yes ok okay thing things something anything nothing everything someone
anyone everyone nobody somebody kind sort lot lots bit bits piece pieces part parts side sides end ends
number numbers amount amounts type types form forms name names call called case cases point points
help helps helped helping give gives gave given take takes took taken taking put puts putting keep keeps
kept let lets letting seem seems seemed look looks looked looking find finds found finding tell tells told
ask asks asked answer answers use uses used using work works worked show shows showed shown try tries
tried need want wants wanted like likes liked love loves hated hate start starts started stop stops
play plays played run runs ran move moves moved turn turns turned bring brings brought hold holds held
write writes wrote written read reads speak speaks spoke meet meets met lose loses lost pay pays paid
buy buys bought sell sells sold send sends sent build builds built grow grows grew find open opens opened
close closes closed learn learns learned study studies studied live lives lived die dies died change
changes changed happen happens happened appear appears appeared feel feels felt hear hears heard watch
watches watched sit sits sat stand stands stood walk walks walked'''.split())

SKIP_FILES = ('deck', 'index', 'chain', 'mindmap', 'freq', 'hard', 'phrase', 'dict', 'tc_', 'wordnotes', 'pilot')
TYPE_CN = {'text1': '阅读', 'text2': '阅读', 'text3': '阅读', 'text4': '阅读',
           'cloze': '完形', 'newtype': '新题型', 'translation': '翻译', 'writing': '写作'}
KYK = ('zk', 'gk', 'cet4', 'cet6', 'ky')
POOL_FP = os.path.join(TOOLS, 'wn2_all_worklist.json')
DEC_FP = os.path.join(TOOLS, 'wn2_decisions.json')


# ------------------------------------------------------------------ 语料
def load_corpus():
    sents = []
    for p in sorted(glob.glob(os.path.join(DATA, '*.json'))) + sorted(glob.glob(os.path.join(DATA, 'en1', '*.json'))):
        b = os.path.basename(p)
        if any(k in b for k in SKIP_FILES):
            continue
        try:
            dd = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(dd, dict):
            continue
        en1 = 'en1' in p.replace('\\', '/')
        m = re.search(r'(\d{4})', b)
        year = m.group(1) if m else ''
        for a in dd.get('articles', []):
            if not isinstance(a, dict):
                continue
            for s in a.get('sentences', []) or []:
                en = s.get('en') or ''
                if not en:
                    continue
                sents.append({'sid': s.get('id', ''), 'en': en, 'cn': s.get('cn') or '',
                              'year': year, 'book': '英语一' if en1 else '英语二',
                              'type': a.get('type', ''), 'topic': a.get('topic', '')})
    return sents


def src_label(s):
    return '%s %s · %s' % (s['year'], s['book'], TYPE_CN.get(s['type'], s['type']))


def cn_ok(s):
    """译文可靠性：只有英语二 2010+ 可信"""
    return s['book'] == '英语二' and s['year'] >= '2010'


# ------------------------------------------------------------------ ECDICT
def load_ecdict(needed=None):
    out = {}
    with open(os.path.join(TOOLS, 'ecdict.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if not w or (needed is not None and w not in needed):
                continue
            out.setdefault(w, {'trans': (row.get('translation') or '').strip(),
                               'ex': (row.get('exchange') or '').strip(),
                               'collins': (row.get('collins') or '').strip(),
                               'tag': (row.get('tag') or '').strip()})
    return out


def variants(word, ec, other_bases=None):
    w = word.lower()
    vs = {w}
    other_bases = other_bases or set()
    for part in (ec or {}).get('ex', '').split('/'):
        if ':' in part:
            k, v = part.split(':', 1)
            if k in ('d', 'p', 'i', 's', '3', '0', '1') and v and ' ' not in v:
                vs.add(v.lower())
    if w.endswith('e'):
        vs |= {w + 'd', w[:-1] + 'ing', w + 's'}
    elif w.endswith('y') and len(w) > 2 and w[-2] not in 'aeiou':
        vs |= {w[:-1] + 'ies', w[:-1] + 'ied', w + 's'}
    else:
        vs |= {w + 'ed', w + 'ing', w + 's', w + 'es'}
    if w.endswith('s'):
        vs.add(w[:-1])
    # 变体若是另一个池内词的基形，说明是那个词的屈折形式，剔除以免重复
    return {v for v in vs if v and (v == w or v not in other_bases)}


def clean_common(trans):
    if not trans:
        return ''
    lines = [l.strip() for l in trans.split('\n') if l.strip() and not l.strip().startswith('[')]
    out = []
    for ln in lines[:2]:
        m = re.match(r'^([a-z]+\.)\s*(.+)$', ln)
        if m:
            ss = [x.strip() for x in re.split(r'[,，;；]', m.group(2)) if x.strip()][:2]
            if ss:
                out.append(m.group(1) + ' ' + '；'.join(ss))
        else:
            ss = [x.strip() for x in re.split(r'[,，;；]', ln) if x.strip()][:2]
            if ss:
                out.append('；'.join(ss))
    return ' / '.join(out)


def familiarity(ec):
    if not ec:
        return 0
    try:
        sc = int(ec.get('collins') or 0) * 2
    except ValueError:
        sc = 0
    tags = set((ec.get('tag') or '').split())
    for t, v in (('zk', 5), ('gk', 4), ('cet4', 3), ('cet6', 3), ('ky', 4)):
        if t in tags:
            sc += v
    return sc


# ------------------------------------------------------------------ pool
def cmd_pool():
    sents = load_corpus()
    print('语料 %d 句' % len(sents))
    idx = collections.defaultdict(list)
    for i, s in enumerate(sents):
        for w in set(re.findall(r"[a-z][a-z'-]{1,}", s['en'].lower())):
            idx[w].append(i)
    freq = {w: len(v) for w, v in idx.items()}

    pool = {}

    def add(word, tip, kind):
        w = word.strip()
        if not w or ' ' in w:
            return
        e = pool.setdefault(w.lower(), {'w': w, 'tips': [], 'kinds': []})
        if tip:
            e['tips'].append(tip)
        e['kinds'].append(kind)

    rex = json.load(open(os.path.join(DATA, 'deck_realexam.json'), encoding='utf-8'))
    for w in rex.get('words', []):
        add(w.get('word', ''), w.get('meaning'), '真题词汇')
    tc = json.load(open(os.path.join(DATA, 'deck_tc_senses.json'), encoding='utf-8'))
    for w in tc.get('words', []):
        add(w.get('word', ''), w.get('meaning'), '唐迟')
    nt = json.load(open(os.path.join(DATA, 'wordnotes_notes.json'), encoding='utf-8'))
    for r in nt.get('rows', []):
        add(r.get('word', ''), r.get('uncommon'), '大白笔记')

    # 扩展池：大纲词 且 语料出现 >=3
    need = set(pool)
    ext_words = set()
    with open(os.path.join(TOOLS, 'ecdict.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if not w or ' ' in w or w in STOP or w in pool:
                continue
            if not (set((row.get('tag') or '').split()) & set(KYK)):
                continue
            if freq.get(w, 0) >= 3:
                ext_words.add(w)
    for w in ext_words:
        add(w, '', '大纲词')
    for k in list(pool):
        if k in FUNC and not pool[k]['tips']:
            del pool[k]
    print('  合池 %d 词（deck 池 %d + 大纲扩展 %d）' % (len(pool), len(need), len(ext_words)))

    ec = load_ecdict(needed=set(pool))
    base_forms = set(pool)
    rows = []
    for k, v in pool.items():
        tgt = {k}
        for x in variants(k, ec.get(k), base_forms - {k}):
            tgt.add(x)
        hits = sorted({i for x in tgt for i in idx.get(x, [])})
        if not hits:
            continue
        occ = []
        for i in hits:
            s = sents[i]
            en = re.sub(r'\s+', ' ', s['en']).strip()
            occ.append({'sid': s['sid'], 'en': en, 'cn': re.sub(r'\s+', ' ', s['cn']).strip() if cn_ok(s) else '',
                        'year': s['year'], 'src': src_label(s), 'ok': cn_ok(s)})
        # 干净句在前，短句优先
        occ.sort(key=lambda o: (not o['ok'], len(o['en'])))
        e = ec.get(k, {})
        rows.append({'w': v['w'], 'common': clean_common(e.get('trans', '')),
                     'tips': [t for t in v['tips'] if t], 'kinds': sorted(set(v['kinds'])),
                     'fam': familiarity(e), 'tag': e.get('tag', ''), 'collins': e.get('collins', ''),
                     'n': len(occ), 'occ': occ})
    # 排序：语料频次高 → 熟悉度高（先判最有价值的）
    rows.sort(key=lambda r: (not bool(r['tips']), -r['n'], -r['fam'], r['w'].lower()))
    json.dump({'total': len(rows), 'rows': rows}, open(POOL_FP, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('写入', POOL_FP)
    print('  有真题句 %d ｜出现 >=10 次 %d ｜5-9 次 %d ｜3-4 次 %d ｜<=2 次 %d' % (
        len(rows), sum(1 for r in rows if r['n'] >= 10), sum(1 for r in rows if 5 <= r['n'] < 10),
        sum(1 for r in rows if 3 <= r['n'] < 5), sum(1 for r in rows if r['n'] < 3)))


def cmd_show(start=0, count=50, occ=3, wlen=140):
    d = json.load(open(POOL_FP, encoding='utf-8'))
    dec = json.load(open(DEC_FP, encoding='utf-8')) if os.path.exists(DEC_FP) else {'words': [], 'phrases': []}
    done = {x['w'].lower() for x in dec['words']} | {w.lower() for w in dec.get('dropped', [])}
    todo = [r for r in d['rows'] if r['w'].lower() not in done]
    print('# 剩余 %d 词（已判 %d）｜本批 %d-%d' % (len(todo), len(done), start, start + count))
    for r in todo[start:start + count]:
        print('=' * 78)
        print('%s ┃频%d ┃fam%s ┃熟义: %s' % (r['w'], r['n'], r['fam'], r['common']))
        if r['tips']:
            print('  deck提示:', ' / '.join(r['tips'])[:110])
        for o in r['occ'][:occ]:
            print('  [%s] %s | %s' % ('✓' if o['ok'] else '✗', o['sid'], o['en'][:wlen]))


def cmd_stat():
    d = json.load(open(POOL_FP, encoding='utf-8'))
    dec = json.load(open(DEC_FP, encoding='utf-8')) if os.path.exists(DEC_FP) else {'words': [], 'phrases': []}
    done = {x['w'].lower() for x in dec['words']} | {w.lower() for w in dec.get('dropped', [])}
    print('合池 %d ｜已判 %d（其中丢弃 %d）｜剩余 %d' % (len(d['rows']), len(done), len(dec.get('dropped', [])), len(d['rows']) - len(done)))
    print('入库档位分布:', collections.Counter(x['tier'] for x in dec['words']))
    print('丢弃(真题无僻义):', len(dec.get('dropped', [])))


# ------------------------------------------------------------------ build
TIER_ORDER = {'高': 0, '中': 1, '低': 2}


def cmd_build():
    d = json.load(open(POOL_FP, encoding='utf-8'))
    by = {r['w'].lower(): r for r in d['rows']}
    dec = json.load(open(DEC_FP, encoding='utf-8'))
    out = []
    dropped = []
    for x in dec['words']:
        r = by.get(x['w'].lower())
        if not r:
            dropped.append(x['w'])
            continue
        sid = x.get('sid') or ''
        o = next((q for q in r['occ'] if q['sid'] == sid), None) or r['occ'][0]
        en, cn = o['en'], o['cn']
        if cn and len(cn) > 110:
            cn = cn[:108].rstrip() + '…'
        if len(en) > 135:
            i = en.find(x['w'].split()[0])
            en = ('…' + en[max(0, i - 20):]) if i > 25 else en
            if len(en) > 135:
                en = en[:133].rstrip() + '…'
        # 年份标签：该僻义已验证的句子（sids）+ 所有同类出现年份
        years = sorted({q['year'] for q in r['occ'] if q['sid'] in x.get('sids', [sid]) and q['year']},
                       reverse=True) or [o['year']]
        out.append({'w': r['w'], 'common': x.get('common') or r['common'],
                    'uncommon': x['uncommon'], 'tier': x['tier'],
                    'en': en, 'cn': cn, 'src': o['src'], 'year': o['year'],
                    'years': years, 'n': r['n']})
    out.sort(key=lambda r: (TIER_ORDER.get(r['tier'], 9), -r['n'], r['w'].lower()))
    payload = {'count': len(out), 'rows': out}
    json.dump(payload, open(os.path.join(DATA, 'wordnotes.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('写入 pwa/data/wordnotes.json：%d 条（高 %d / 中 %d / 低 %d）' % (
        len(out), sum(1 for r in out if r['tier'] == '高'), sum(1 for r in out if r['tier'] == '中'),
        sum(1 for r in out if r['tier'] == '低')))
    print('  无真题句而丢弃:', dropped)

    # —— 短语板块 ——
    ph_fp = os.path.join(TOOLS, 'wn2_phrases_worklist.json')
    if os.path.exists(ph_fp) and dec.get('phrases'):
        ph = {r['w'].strip().lower(): r for r in json.load(open(ph_fp, encoding='utf-8'))['rows']}
        cats = ['政法', '商业经济', '科学科技', '教育文化历史', '社会生活']
        groups = {c: [] for c in cats}
        miss = []
        for x in dec['phrases']:
            r = ph.get(x['w'].strip().lower())
            if not r:
                miss.append(x['w'])
                continue
            en = re.sub(r'\s+', ' ', r['en']).strip()
            if len(en) > 190:
                en = en[:188].rstrip() + '…'
            cn = re.sub(r'\s+', ' ', r['cn'] or '').strip()
            if len(cn) > 150:
                cn = cn[:148].rstrip() + '…'
            cat = x.get('cat') or r['cat'] or '社会生活'
            groups.setdefault(cat, []).append({
                'w': r['w'], 'meaning': x.get('meaning') or ' | '.join(r['meanings'])[:40],
                'en': en, 'cn': cn, 'src': r['src'], 'year': r['year']})
        for c in groups:
            groups[c].sort(key=lambda a: a['w'].lower())
        json.dump({'count': sum(len(v) for v in groups.values()), 'cats': cats, 'groups': groups},
                  open(os.path.join(DATA, 'phrasebook.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('写入 pwa/data/phrasebook.json：%d 条 / %d 类（缺失 %s）' % (
            sum(len(v) for v in groups.values()), len(cats), miss))


def _remaining_rows():
    d = json.load(open(POOL_FP, encoding='utf-8'))
    dec = json.load(open(DEC_FP, encoding='utf-8')) if os.path.exists(DEC_FP) else {'words': [], 'dropped': []}
    done = {x['w'].lower() for x in dec['words']} | {w.lower() for w in dec.get('dropped', [])}
    return [r for r in d['rows'] if r['w'].lower() not in done]


def cmd_word(w, occ=8, wlen=115):
    """打印某个词在全语料中的全部出现句（判义/复核用）"""
    d = json.load(open(POOL_FP, encoding='utf-8'))
    r = next((x for x in d['rows'] if x['w'].lower() == w.strip().lower()), None)
    if not r:
        print('词池中没有:', w)
        return
    print('%s ┃频%d ┃熟义: %s' % (r['w'], r['n'], r['common']))
    if r['tips']:
        print('deck提示:', ' / '.join(r['tips'])[:110])
    for o in r['occ'][:occ]:
        print('  [%s] %s | %s' % ('✓' if o['ok'] else '✗', o['sid'], o['en'][:wlen]))
        if o['ok'] and o['cn']:
            print('      译:', o['cn'][:80])


def cmd_remaining():
    rows = _remaining_rows()
    fp = os.path.join(TOOLS, 'wn2_remaining.json')
    json.dump({'total': len(rows), 'rows': rows}, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('待判 %d 词 →' % len(rows), fp)


def cmd_rslice(a, b, occ=2, wlen=100):
    rows = _remaining_rows()
    for r in rows[a:b]:
        print('=' * 74)
        print('%s ┃频%d ┃熟义: %s' % (r['w'], r['n'], r['common']))
        if r['tips']:
            print('  deck提示:', ' / '.join(r['tips'])[:100])
        for o in r['occ'][:occ]:
            print('  [%s] %s | %s' % ('✓' if o['ok'] else '✗', o['sid'], o['en'][:wlen]))


def cmd_skip(n):
    d = json.load(open(POOL_FP, encoding='utf-8'))
    dec = json.load(open(DEC_FP, encoding='utf-8'))
    done = {x['w'].lower() for x in dec['words']} | {w.lower() for w in dec.get('dropped', [])}
    todo = [r for r in d['rows'] if r['w'].lower() not in done]
    dropped = dec.setdefault('dropped', [])
    for r in todo[:n]:
        dropped.append(r['w'])
    json.dump(dec, open(DEC_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('已标记丢弃 %d 个（累计丢弃 %d）' % (min(n, len(todo)), len(dropped)))
    print('本批丢弃:', [r['w'] for r in todo[:n]])


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else 'stat'
    if c == 'pool':
        cmd_pool()
    elif c == 'show':
        cmd_show(int(sys.argv[2]) if len(sys.argv) > 2 else 0,
                 int(sys.argv[3]) if len(sys.argv) > 3 else 50,
                 int(sys.argv[4]) if len(sys.argv) > 4 else 3,
                 int(sys.argv[5]) if len(sys.argv) > 5 else 140)
    elif c == 'word':
        cmd_word(sys.argv[2])
    elif c == 'remaining':
        cmd_remaining()
    elif c == 'rslice':
        cmd_rslice(int(sys.argv[2]), int(sys.argv[3]),
                   int(sys.argv[4]) if len(sys.argv) > 4 else 2,
                   int(sys.argv[5]) if len(sys.argv) > 5 else 100)
    elif c == 'skip':
        cmd_skip(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
    elif c == 'build':
        cmd_build()
    else:
        cmd_stat()
