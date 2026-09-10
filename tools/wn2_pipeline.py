# -*- coding: utf-8 -*-
"""
熟词僻义 / 熟词短语 数据管道 v2

核心原则（用户确认）：
  A. 以真题例句为准，从例句反推僻义 —— 只保留「义项 ≠ 该词常用义」的句子，那个义项即僻义
     真题里没考过僻义的词 → 剔除

用法：
  python tools/wn2_pipeline.py worklist      # 生成待判义工作表
  python tools/wn2_pipeline.py build         # 读 decisions 构建最终数据
  python tools/wn2_pipeline.py phrases       # 生成短语工作表（按文章主题归类）
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
PWA = os.path.join(ROOT, 'pwa')
DATA = os.path.join(PWA, 'data')
TOOLS = os.path.join(ROOT, 'tools')

STOP = set('''a an the of to in on at for with by from about as is are was were be been being do does did have has had
it its this that these those their them they we you he she his her our your i not no nor or and but so if then than
most more some any all both each other another such which who whom whose when where why how what while because
can could will would should may might must shall into over under between among against during before after above
through out off up down again once here there just very only also too quite rather'''.split())

SKIP_FILES = ('deck', 'index', 'chain', 'mindmap', 'freq', 'hard', 'phrase', 'dict', 'tc_', 'wordnotes')


# ---------------------------------------------------------------- ECDICT
def load_ecdict(needed=None):
    """读 ECDICT，返回 word -> {trans, ex, collins, tag}；needed 非空时只保留这些词"""
    out = {}
    with open(os.path.join(TOOLS, 'ecdict.csv'), encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if not w:
                continue
            if needed is not None and w not in needed:
                continue
            out.setdefault(w, {
                'trans': (row.get('translation') or '').strip(),
                'ex': (row.get('exchange') or '').strip(),
                'collins': (row.get('collins') or '').strip(),
                'tag': (row.get('tag') or '').strip(),
            })
    return out


def variants(word, ec):
    """精确词形变体集合：ECDICT exchange 优先，启发式兜底"""
    w = word.lower()
    vs = {w}
    e = (ec or {}).get('ex', '')
    for part in e.split('/'):
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
    return {v for v in vs if v}


def clean_common(trans):
    """ECDICT translation -> 熟义（词性 + 前 2 义项）"""
    if not trans:
        return ''
    lines = [l.strip() for l in trans.split('\n') if l.strip() and not l.strip().startswith('[')]
    if not lines:
        return ''
    out = []
    for ln in lines[:2]:
        m = re.match(r'^([a-z]+\.)\s*(.+)$', ln)
        if m:
            senses = re.split(r'[,，;；]', m.group(2))
            senses = [s.strip() for s in senses if s.strip()][:2]
            if senses:
                out.append(m.group(1) + ' ' + '；'.join(senses))
        else:
            senses = re.split(r'[,，;；]', ln)
            senses = [s.strip() for s in senses if s.strip()][:2]
            if senses:
                out.append('；'.join(senses))
    return ' / '.join(out)


def familiarity(ec):
    """熟悉度分：collins 星级 + 考纲标签（越大越熟）"""
    if not ec:
        return 0
    score = 0
    try:
        score += int(ec.get('collins') or 0) * 2
    except ValueError:
        pass
    tags = set((ec.get('tag') or '').split())
    for t, v in (('zk', 5), ('gk', 4), ('cet4', 3), ('cet6', 3), ('ky', 4)):
        if t in tags:
            score += v
    return score


# ---------------------------------------------------------------- 语料
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
                sents.append({
                    'sid': s.get('id', ''),
                    'en': en,
                    'cn': s.get('cn') or '',
                    'year': year,
                    'book': '英语一' if en1 else '英语二',
                    'type': a.get('type', ''),
                    'aid': a.get('id', ''),
                    'topic': a.get('topic', ''),
                })
    return sents


TYPE_CN = {'text1': '阅读', 'text2': '阅读', 'text3': '阅读', 'text4': '阅读',
           'cloze': '完形', 'newtype': '新题型', 'translation': '翻译', 'writing': '写作'}


def src_label(s):
    return '%s %s · %s' % (s['year'], s['book'], TYPE_CN.get(s['type'], s['type']))


# ---------------------------------------------------------------- 词池
def load_pool():
    """单词池：真题词汇 deck（单词条）+ 唐迟熟词僻义 + 大白笔记"""
    pool = {}   # word -> {deck_meaning, src_kind}

    rex = json.load(open(os.path.join(DATA, 'deck_realexam.json'), encoding='utf-8'))
    for w in rex.get('words', []):
        word = (w.get('word') or '').strip()
        if not word or ' ' in word:
            continue
        pool.setdefault(word.lower(), {'w': word, 'tips': [], 'kinds': []})
        pool[word.lower()]['tips'].append(w.get('meaning') or '')
        pool[word.lower()]['kinds'].append('真题词汇')

    tc = json.load(open(os.path.join(DATA, 'deck_tc_senses.json'), encoding='utf-8'))
    for w in tc.get('words', []):
        word = (w.get('word') or '').strip()
        if not word or ' ' in word:
            continue
        pool.setdefault(word.lower(), {'w': word, 'tips': [], 'kinds': []})
        pool[word.lower()]['tips'].append(w.get('meaning') or '')
        pool[word.lower()]['kinds'].append('唐迟')

    nt = json.load(open(os.path.join(DATA, 'wordnotes_notes.json'), encoding='utf-8'))
    for r in nt.get('rows', []):
        word = (r.get('word') or '').strip()
        if not word or ' ' in word:
            continue
        pool.setdefault(word.lower(), {'w': word, 'tips': [], 'kinds': []})
        pool[word.lower()]['tips'].append(r.get('uncommon') or '')
        pool[word.lower()]['kinds'].append('大白笔记')
    return pool


def load_phrase_pool():
    ph = {}

    def add(word, meaning, en, cn, kind):
        k = re.sub(r'\s+', ' ', word.strip().lower())
        if not k:
            return
        e = ph.setdefault(k, {'w': word.strip(), 'meanings': [], 'en': '', 'cn': '', 'kinds': []})
        if meaning:
            e['meanings'].append(meaning.strip())
        if en and not e['en']:
            e['en'] = re.sub(r'\s+', ' ', en).strip()
            e['cn'] = re.sub(r'\s+', ' ', cn or '').strip()
        e['kinds'].append(kind)

    rex = json.load(open(os.path.join(DATA, 'deck_realexam.json'), encoding='utf-8'))
    for w in rex.get('words', []):
        word = (w.get('word') or '').strip()
        if ' ' not in word:
            continue
        add(word, w.get('meaning'), w.get('example_en'), w.get('example_cn'), '真题词汇')

    tcp = json.load(open(os.path.join(DATA, 'deck_tc_phrases.json'), encoding='utf-8'))
    for w in tcp.get('words', []):
        add(w.get('word', ''), w.get('meaning'), w.get('example_en'), w.get('example_cn'), '唐迟短语')

    nt = json.load(open(os.path.join(DATA, 'wordnotes_notes.json'), encoding='utf-8'))
    for r in nt.get('rows', []):
        if ' ' in (r.get('word') or ''):
            add(r['word'], r.get('uncommon'), r.get('en'), r.get('cn'), '大白笔记')
    return ph


# ---------------------------------------------------------------- 归类
CATS = [
    ('政法', ['政府', '法律', '立法', '法院', '司法', '政策', '监管', '税', '选举', '政治', '议会', '宪法',
             '移民', '警察', '犯罪', '国会', '总统', '权利', '诉', '联邦', '国家安全', '外交', '工会', '法案']),
    ('商业经济', ['公司', '经济', '市场', '商业', '企业', '金融', '银行', '投资', '消费', '贸易', '产业', '就业',
               '薪', '利润', '销售', '品牌', '广告', '管理', '创业', '股市', '竞争', '成本', '价格', '劳动']),
    ('科学科技', ['科学', '技术', '研究', '数据', '人工智能', 'AI', '网络', '互联网', '算法', '医学', '健康',
               '基因', '气候', '环境', '能源', '航天', '生物', '物理', '心理', '手机', '数字', '机器人']),
    ('教育文化历史', ['教育', '学校', '大学', '学生', '学习', '考试', '文化', '艺术', '历史', '文学', '新闻',
                 '媒体', '图书', '出版', '博物馆', '音乐', '语言', '写作', '知识', '宗教', '电影']),
    ('社会生活', ['社会', '生活', '家庭', '工作', '职业', '性别', '人口', '城市', '社区', '健康', '习惯',
               '旅行', '运动', '幸福', '焦虑', '婚姻', '育儿', '朋友', '慈善', '消费', '身份', '贫富']),
]


def classify(text):
    """按文章 topic 归类到 5 类；返回类别名或 ''"""
    if not text:
        return ''
    best, best_n = '', 0
    for name, kws in CATS:
        n = sum(1 for k in kws if k in text)
        if n > best_n:
            best, best_n = name, n
    return best


def norm(s):
    s = (s or '').lower()
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# ---------------------------------------------------------------- worklist
def cmd_worklist():
    print('加载语料…')
    sents = load_corpus()
    print('  句数', len(sents))
    # 建 inverted index：词 -> 句下标
    idx = collections.defaultdict(list)
    for i, s in enumerate(sents):
        for w in set(re.findall(r"[a-z][a-z'-]{1,}", s['en'].lower())):
            idx[w].append(i)

    print('加载词池…')
    pool = load_pool()
    print('  单词池', len(pool))
    ec = load_ecdict(needed=set(pool))
    print('  ECDICT 命中', len(ec))

    out = []
    nostr = 0
    for k, v in pool.items():
        vs = variants(k, ec.get(k))
        hits = sorted({i for x in vs for i in idx.get(x, [])})
        if not hits:
            nostr += 1
            continue
        occ = []
        for i in hits:
            s = sents[i]
            occ.append({'sid': s['sid'], 'en': s['en'], 'cn': s['cn'], 'year': s['year'],
                        'book': s['book'], 'type': TYPE_CN.get(s['type'], s['type']),
                        'src': src_label(s), 'topic': s['topic']})
        e = ec.get(k, {})
        out.append({
            'w': v['w'],
            'common': clean_common(e.get('trans', '')),
            'tips': [t for t in v['tips'] if t],
            'kinds': sorted(set(v['kinds'])),
            'fam': familiarity(e),
            'tag': e.get('tag', ''),
            'collins': e.get('collins', ''),
            'n': len(occ),
            'occ': occ,
        })
    out.sort(key=lambda r: (-r['fam'], r['w'].lower()))
    fp = os.path.join(TOOLS, 'wn2_words_worklist.json')
    json.dump({'total': len(out), 'rows': out}, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入', fp)
    print('  有真题句的词', len(out), '｜真题中未出现的词(剔除)', nostr)
    print('  出现句数分布: 1句 %d ｜2-3句 %d ｜4+句 %d' % (
        sum(1 for r in out if r['n'] == 1), sum(1 for r in out if 2 <= r['n'] <= 3), sum(1 for r in out if r['n'] >= 4)))


def cmd_phrases():
    print('加载语料…')
    sents = load_corpus()
    # 归一化例句 -> 文章
    smap = {}
    for s in sents:
        smap.setdefault(norm(s['en']), s)
    print('加载短语池…')
    ph = load_phrase_pool()
    print('  短语池', len(ph))

    rows = []
    unlocated = 0
    for k, v in ph.items():
        en = v['en']
        s = smap.get(norm(en))
        if not s:
            # 模糊：取例句前 60 字符归一化后前缀匹配
            pre = norm(en)[:60]
            cand = [x for key, x in smap.items() if pre and key.startswith(pre)]
            s = cand[0] if cand else None
        if not s:
            unlocated += 1
        cat = classify(s['topic']) if s else ''
        rows.append({
            'w': v['w'],
            'meanings': sorted(set(v['meanings'])),
            'en': s['en'] if s else en,
            'cn': s['cn'] if s else v['cn'],
            'src': src_label(s) if s else '',
            'year': s['year'] if s else '',
            'topic': s['topic'] if s else '',
            'cat': cat,
            'kinds': sorted(set(v['kinds'])),
        })
    fp = os.path.join(TOOLS, 'wn2_phrases_worklist.json')
    json.dump({'total': len(rows), 'rows': rows}, open(fp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入', fp)
    print('  未定位到文章', unlocated)
    print('  类别分布', collections.Counter(r['cat'] or '未分类' for r in rows))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'worklist'
    {'worklist': cmd_worklist, 'phrases': cmd_phrases}[cmd]()
