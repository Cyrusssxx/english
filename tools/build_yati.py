# -*- coding: utf-8 -*-
"""从两份押题 PDF 生成押题页数据：
- 27考研英语作文押题精选.pdf → 26 张题目图（每题 1 张嵌入 JPEG）
- ai归来版范文.pdf → 26 篇配套范文英文正文（重排段落 + 结构化块）

输出：
  pwa/data/yati/{NN}.jpg   26 张图
  pwa/data/yati.json       结构化数据（分组、顺序、图/文块）
分组顺序（用户要求）：单图表 → 小作文 → 其它图表（图画+图表/双图表）→ 图画（单图画/双图画）
每组默认收起由前端处理。
"""
import fitz, json, os, re, io
from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PWA = os.path.join(ROOT, 'pwa')
IMGDIR = os.path.join(PWA, 'data', 'yati')
os.makedirs(IMGDIR, exist_ok=True)

QPDF = r"E:\夸克\Download\27考研英语作文押题精选.pdf"
FPDF = r"E:\夸克\Download\ai归来版范文.pdf"

# ---------- 0) 英文题名 + 图内中文标注的英文写法（人工整理，写作时可直接套用） ----------
# 英文题名与写作词库 topics26 组保持一致口径（可作首段点题短语）。
TITLE_EN = {
    1: 'the use of AI tools',
    2: '"staying around" vs. "companionship"',
    3: 'stress and physical and mental health',
    4: 'over-packaging and green consumption',
    5: 'online information and rational judgement',
    6: 'purposes of continuing education among employees',
    7: 'domestic sales of fuel and new energy vehicles',
    8: "residents' daily travel choices",
    9: 'factors in college students\' career choices',
    10: 'the number of convenience stores nationwide',
    11: 'barrier-free passages in public places',
    12: 'the popularisation of first-aid knowledge',
    13: 'overseas returnees developing their careers at home',
    14: 'average life expectancy and population ageing',
    15: 'online and offline ice cream sales',
    16: 'the inheritance of traditional Chinese art',
    17: 'popularity vs. genuine passion',
    18: 'tourism development and environmental protection',
    19: 'a peer mentoring programme: introduction and reply',
    20: 'a lecture on Chinese culture: suggestions and arrangements',
    21: 'recommending a study tool: advice and explanation',
    22: 'a change of pick-up plan: apology and suggestion',
    23: 'help with overseas study: thanks and invitation',
    24: 'volunteer application to the cultural exchange centre',
    25: 'volunteers wanted: notice from the tourism association',
    26: 'minutes of a meeting on reducing food waste',
}

# 图内的中文标注（人物对白 / 图注 / 招牌），逐条给「能直接写进作文」的英文。
# 空白：图里没有中文标注（纯图表）。
NOTES = {
    1: [('AI 太好用了！', 'AI is such a great help!'),
        ('答案已生成', 'the answer has been generated'),
        ('作业「已完成」', 'homework already "finished"')],
    2: [('爸爸，你在听我说话吗？', 'Dad, are you listening to me?'),
        ('「陪着」不等于「陪伴」', '"Staying around" is not companionship.')],
    3: [('压力（墙上海报）', 'a poster reading "pressure"')],
    4: [('买个礼物需要这么多包装？', 'Does one gift really need all this packaging?')],
    5: [('网络信息', 'online information'),
        ('真 / 假（散落标签）', 'labels reading "true" and "false"'),
        ('诚信：网络信息真假难辨', 'Honesty: online information is hard to tell true from false.')],
    11: [('2021~2025 年某市公共场所设置无障碍通道的比例', 'the share of public places with barrier-free passages in a city, 2021–2025'),
         ('注：无障碍通道指坡道、升降设施等便于行动不便者进出的通道',
          'Barrier-free passages refer to ramps, lifts and other facilities that help people with mobility difficulties get in and out.')],
    16: [('中国传统艺术的传承', 'the inheritance of traditional Chinese art')],
    17: [('这个专业需求旺盛，前景广阔！', 'This major is in great demand and has bright prospects!'),
         ('我十分热爱这个专业。', 'I am truly passionate about this major.'),
         ('热门新兴岗位', 'popular emerging positions'),
         ('热门专业报考指南', 'a guide to popular majors'),
         ('热门 vs 热爱', 'popularity vs. genuine passion')],
    18: [('以前 / 现在', 'in the past / at present'),
         ('景区入口', 'the entrance to the scenic area')],
}

# ---------- 1) 从题目 PDF 提取 26 题：题号、中文名、类型、图 ----------
qdoc = fitz.open(QPDF)
questions = {}
type_order = {'单图表': 0, '小作文': 1, '图画+图表': 2, '双图表': 3, '单图画': 4, '双图画': 5}
for i in range(len(qdoc)):
    pg = qdoc[i]
    txt = pg.get_text()
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    num, title = None, None
    for j, l in enumerate(lines):
        if re.fullmatch(r'\d{2}', l) and j + 1 < len(lines):
            cand = lines[j + 1]
            if cand and not re.fullmatch(r'\d{2}', cand) and '来源' not in cand:
                num, title = int(l), cand
                break
    if num is None:
        continue
    typ = next((t for t in type_order if t in txt), None)
    if not typ:
        continue
    imgs = pg.get_images(full=True)
    if not imgs:
        continue
    xref = imgs[0][0]
    info = qdoc.extract_image(xref)
    imgname = f"{num:02d}.jpg"
    # 压缩：原图 1601px → 宽 900 / quality 80（约 90KB）。页面里只当缩略图与弹层大图用。
    im = Image.open(io.BytesIO(info['image'])).convert('RGB')
    if im.width > 900:
        im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=80, optimize=True)
    with open(os.path.join(IMGDIR, imgname), 'wb') as f:
        f.write(buf.getvalue())
    questions[num] = {
        'no': num, 'title': title, 'type': typ,
        'en': TITLE_EN.get(num, ''),
        'notes': [{'zh': z, 'en': e} for z, e in NOTES.get(num, [])],
        'img': f"data/yati/{imgname}",
        'typeRank': type_order[typ],
    }

# ---------- 2) 范文重排：PDF 是硬换行，这里还原成段落 + 结构块 ----------
SAL = re.compile(r'^Dear\b[^.!?]{0,40},$')
CLOSE = re.compile(r'^(Yours (?:sincerely|faithfully)|Sincerely yours|Best (?:regards|wishes)|Yours),?$', re.I)
TITLE = re.compile(r'^(Notice|Announcement|Minutes of Meeting|Minutes)$', re.I)
DATELINE = re.compile(r'^(?:[A-Z][a-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})$')
LABEL = re.compile(r'^(Date|Time|Location|Objective|Attendees|Subject|Topic|Agenda|Place|Purpose|Organizer)\s*:')
# 大作文段首套语：命中且上一段已收句 → 起新段
OPENERS = re.compile(
    r'^(A variety of reasons|Various (?:reasons|factors)|Several (?:factors|reasons)|'
    r'There (?:are (?:several|many|a number of)|is (?:no doubt|no denying)|is a growing)|'
    r'We should bear in mind|It is (?:not difficult|highly necessary|important|worth noting|widely)|'
    r'In my (?:opinion|view)|From my (?:perspective|point of view)|As far as I am concerned|'
    r'To (?:sum up|conclude)|In conclusion|In a word|All things considered|'
    r'What is more|Nobody can (?:deny|ignore)|No one can (?:deny|ignore)|'
    r'Only through|As is (?:shown|depicted|illustrated)|According to the (?:chart|graph|picture))', re.I)
WRAP = 72   # 排版折行宽度（实测中位数 74），短于此的行视为段尾


def reflow(essay):
    """硬换行 → [{k: h|meta|p|sign, v: 文本}]"""
    lines = [l.strip() for l in essay.splitlines() if l.strip()]
    blocks, cur, label = [], '', None
    after_close = False

    def flush():
        nonlocal cur
        if cur.strip():
            blocks.append({'k': 'p', 'v': cur.strip()})
        cur = ''

    for ln in lines:
        if label:                                   # 上一行是 "Date:" 这类标签，本行是它的值
            blocks.append({'k': 'meta', 'v': (label + ' ' + ln).strip()})
            label = None
            continue
        if SAL.match(ln):                           # 称呼
            flush()
            blocks.append({'k': 'p', 'v': ln})
            after_close = False
            continue
        if CLOSE.match(ln):                         # 结束语，后跟署名
            flush()
            blocks.append({'k': 'sign', 'v': ln})
            after_close = True
            continue
        if after_close and len(ln) <= 30 and not ln.endswith(('.', '!', '?')):
            blocks.append({'k': 'sign', 'v': ln})
            after_close = False
            continue
        if not cur and TITLE.match(ln):             # 通知 / 纪要标题
            blocks.append({'k': 'h', 'v': ln})
            continue
        if not cur and DATELINE.match(ln):
            blocks.append({'k': 'meta', 'v': ln})
            continue
        if LABEL.match(ln):                         # Date: / Time: / Attendees: ...
            flush()
            if ln.endswith(':'):
                label = ln
            else:
                blocks.append({'k': 'meta', 'v': ln})
            continue
        if cur and OPENERS.match(ln) and cur.rstrip().endswith(('.', '!', '?')):
            flush()                                 # 套语开头 → 新段
        cur = (cur + ' ' + ln).strip() if cur else ln
        if ln.endswith(('.', '!', '?')) and len(ln) < WRAP - 4:
            flush()                                 # 短尾行 → 段尾
    flush()
    # 通知/纪要末尾的机构名、落款：短行且不收句 → 署名
    if blocks and blocks[-1]['k'] == 'p':
        v = blocks[-1]['v']
        if len(v) <= 45 and not v.endswith(('.', '!', '?')):
            blocks[-1]['k'] = 'sign'
    return blocks


def word_count(blocks):
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", ' '.join(b['v'] for b in blocks)))


# ---------- 3) 从范文 PDF 提取正文 ----------
fdoc = fitz.open(FPDF)
for i in range(len(fdoc)):
    lines = [l.strip() for l in fdoc[i].get_text().splitlines() if l.strip()]
    joined = '\n'.join(lines)
    mm = re.search(r'对应精选第(\d+)题', joined)
    if not mm:
        continue
    num = int(mm.group(1))
    if num not in questions:
        continue
    txt = fdoc[i].get_text()
    body = re.split(r'(?:正文|全文)\s*\d+\s*词', txt, maxsplit=1)
    essay = body[1].strip() if len(body) > 1 else ''
    essay = re.sub(r'27考研英语作文押题精选.*?by不会微分算子\s*\n?', '', essay).strip()
    questions[num]['blocks'] = reflow(essay)
    questions[num]['words'] = word_count(questions[num]['blocks'])

# ---------- 4) 校验 + 组装 ----------
missing_img = [n for n in range(1, 27) if n not in questions or not questions[n].get('img')]
missing_essay = [n for n in range(1, 27) if n not in questions or not questions[n].get('blocks')]
missing_en = [n for n in range(1, 27) if n not in questions or not questions[n].get('en')]
print('题目数', len(questions), '缺图', missing_img, '缺范文', missing_essay, '缺英文题名', missing_en)
if missing_img or missing_essay:
    print('⚠️  有缺失，请检查提取逻辑')

# 大作文应还原成 3 段（小作文按书信/通知格式）
bad = [(q['no'], q['type'], sum(1 for b in q['blocks'] if b['k'] == 'p'))
       for q in questions.values() if q['type'] != '小作文' and sum(1 for b in q['blocks'] if b['k'] == 'p') != 3]
if bad:
    print('⚠️  大作文非 3 段：', bad)

ordered = sorted(questions.values(), key=lambda q: (q['typeRank'], q['no']))
out = {
    'meta': {'title': '作文押题 26 篇', 'desc': '押题精选 26 道原题 + 配套范文'},
    'groups': [],
}
seen = []
for q in ordered:
    if q['type'] not in seen:
        seen.append(q['type'])
for t in seen:
    items = [q for q in ordered if q['type'] == t]
    out['groups'].append({
        'id': 't' + str(type_order[t]), 'name': t, 'type': t,
        'items': [{k: q[k] for k in ('no', 'title', 'en', 'notes', 'img', 'blocks', 'words')} for q in items],
    })

with open(os.path.join(PWA, 'data', 'yati.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('写出 yati.json:', [(g['name'], len(g['items'])) for g in out['groups']])
print('段落分布:', [(q['no'], len([b for b in q['blocks'] if b['k'] == 'p']), q['words']) for q in ordered])
