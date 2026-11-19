# -*- coding: utf-8 -*-
"""从两份押题 PDF 生成押题页数据：
- 27考研英语作文押题精选.pdf → 26 张题目图（每题 1 张嵌入 JPEG）
- ai归来版范文.pdf → 26 篇配套范文英文正文
输出：
  pwa/data/yati/{NN}.jpg   26 张图
  pwa/data/yati.json       结构化数据（分组、顺序、图/文路径）
分组顺序（用户要求）：单图表 → 小作文 → 其它图表（图画+图表/双图表）→ 图画（单图画/双图画）
每组默认收起由前端处理。
"""
import fitz, json, os, re, io
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), '..')
PWA = os.path.join(ROOT, 'pwa')
IMGDIR = os.path.join(PWA, 'data', 'yati')
os.makedirs(IMGDIR, exist_ok=True)

QPDF = r"E:\夸克\Download\27考研英语作文押题精选.pdf"
FPDF = r"E:\夸克\Download\ai归来版范文.pdf"

# ---------- 1) 从题目 PDF 提取 26 题：题号、中文名、类型、来源、图 ----------
qdoc = fitz.open(QPDF)
questions = {}
type_order = {'单图表': 0, '小作文': 1, '图画+图表': 2, '双图表': 3, '单图画': 4, '双图画': 5}
for i in range(len(qdoc)):
    pg = qdoc[i]
    txt = pg.get_text()
    m = re.search(r'\n(\d{2})\n([^\n]+)\n对应精选第|^\s*(\d{2})\s*\n([^\n]+)', txt, re.M)
    # 更稳：在文本里找 "NN\n标题"，标题后跟"来源"或换行
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    # 找题号行（两位数字，后一行是标题）
    num, title = None, None
    for j, l in enumerate(lines):
        if re.fullmatch(r'\d{2}', l) and j + 1 < len(lines):
            cand = lines[j + 1]
            if cand and not re.fullmatch(r'\d{2}', cand) and '来源' not in cand:
                num, title = int(l), cand
                break
    if num is None:
        continue
    # 类型：文本里出现的已知类型词
    typ = next((t for t in type_order if t in txt), None)
    if not typ:
        continue
    imgs = pg.get_images(full=True)
    if not imgs:
        continue
    xref = imgs[0][0]
    info = qdoc.extract_image(xref)
    ext = info['ext']
    imgname = f"{num:02d}.jpg"
    # 压缩：原图 1601px → 宽 900 / quality 80（约 90KB）。
    # 页面显示再由 CSS 限高，避免图太大撑满屏；点击大图仍看 900px 清晰版。
    im = Image.open(io.BytesIO(info['image'])).convert('RGB')
    if im.width > 900:
        im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=80, optimize=True)
    with open(os.path.join(IMGDIR, imgname), 'wb') as f:
        f.write(buf.getvalue())
    questions[num] = {
        'no': num, 'title': title, 'type': typ,
        'img': f"data/yati/{imgname}",
        'typeRank': type_order[typ],
    }

# ---------- 2) 从范文 PDF 提取 26 篇正文 ----------
fdoc = fitz.open(FPDF)
for i in range(len(fdoc)):
    lines = [l.strip() for l in fdoc[i].get_text().splitlines() if l.strip()]
    num = None
    joined = '\n'.join(lines)
    # 直接找 "对应精选第NN题"（最稳）
    mm = re.search(r'对应精选第(\d+)题', joined)
    if mm:
        num = int(mm.group(1))
    if num is None or num not in questions:
        continue
    txt = fdoc[i].get_text()
    # 正文起点：'正文 NNN 词' 或 '全文 NNN 词' 之后
    body = re.split(r'(?:正文|全文)\s*\d+\s*词', txt, maxsplit=1)
    essay = body[1].strip() if len(body) > 1 else ''
    # 去掉页眉页脚
    essay = re.sub(r'27考研英语作文押题精选.*?by不会微分算子\s*\n?', '', essay).strip()
    questions[num]['essay'] = essay

# ---------- 3) 校验 + 组装 ----------
missing_img = [n for n in range(1, 27) if n not in questions or not questions[n].get('img')]
missing_essay = [n for n in range(1, 27) if n not in questions or not questions[n].get('essay')]
print('题目数', len(questions), '缺图', missing_img, '缺范文', missing_essay)
if missing_img or missing_essay:
    print('⚠️  有缺失，请检查提取逻辑')

# 按用户要求排序：typeRank 升序（单图表0→小作文1→图画+图表2→双图表3→单图画4→双图画5），同类按题号
ordered = sorted(questions.values(), key=lambda q: (q['typeRank'], q['no']))
out = {
    'meta': {'title': '27 考研作文押题 · 26 题', 'desc': '押题精选 26 道题目原图 + 配套范文，按「单图表 → 小作文 → 其它图表 → 图画」排列，可展开看范文。'},
    'groups': [],
}
# 按类型分组，保序
seen = []
for q in ordered:
    if q['type'] not in seen:
        seen.append(q['type'])
for t in seen:
    items = [q for q in ordered if q['type'] == t]
    out['groups'].append({
        'id': 't' + str(type_order[t]), 'name': t, 'type': t,
        'items': [{k: q[k] for k in ('no', 'title', 'img', 'essay')} for q in items],
    })

with open(os.path.join(PWA, 'data', 'yati.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('写出 yati.json:', [(g['name'], len(g['items'])) for g in out['groups']])
