# -*- coding: utf-8 -*-
"""
模板带背视频生成器（大作文骨架篇，竖屏 1080x1920）

链路：writing_templates.json 取句 -> edge-tts 逐句合成（慢读 + 原速）
      -> 词边界对齐 -> Pillow 按块渲染帧 -> ffmpeg 拼帧 + 混音 -> mp4

用法：python tools/make_recite_video.py [--only=0,1]
"""
import os, sys, json, re, asyncio, subprocess, shutil, hashlib
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')
BUILD = os.path.join(ROOT, 'build_video')
OUT_DIR = os.path.join(ROOT, 'output')
# Trae 自带的 ffmpeg 是精简构建（无 mp3/wav/aac），改用 imageio-ffmpeg 的完整版
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1080, 1920
FPS = 25

VOICE_EN = 'en-US-EmmaNeural'
VOICE_CN = 'zh-CN-XiaoxiaoNeural'
RATE_SLOW = '-15%'
RATE_FAST = '-2%'

FONT_EN = 'C:/Windows/Fonts/georgia.ttf'
FONT_EN_I = 'C:/Windows/Fonts/georgiai.ttf'
FONT_CN = 'C:/Windows/Fonts/msyh.ttc'
FONT_CN_B = 'C:/Windows/Fonts/msyhbd.ttc'

# ---------------- 配色（深色，与站点一致） ----------------
BG_TOP = (12, 17, 30)
BG_BOT = (24, 33, 53)
T_CUR = (255, 255, 255)      # 正在读的块
T_DONE = (176, 188, 212)     # 已读过
T_NEXT = (128, 142, 168)     # 还没读到
SLOT_CUR = (255, 208, 110)
SLOT_DONE = (196, 158, 84)
SLOT_NEXT = (118, 98, 58)
CN_COL = (146, 161, 187)
ACCENT = (110, 168, 254)
LINE = (44, 56, 84)
WHITE = (246, 249, 255)


# ---------------- 内容清单 ----------------
def load_tpl():
    with open(TPL, encoding='utf-8') as f:
        return json.load(f)


TPL_DATA = load_tpl()
SEC = {s['id']: s for s in TPL_DATA['sections']}


def skel(sid):
    return {'en': SEC[sid]['en'], 'cn': SEC[sid]['cn'], 'note': SEC[sid].get('note') or ''}


def pool(sid, idx):
    s = SEC[sid]['sentences'][idx]
    return {'en': s['en'], 'cn': s['cn'], 'note': ''}


PARTS = [
    {
        'tag': 'PART 1 · 动态图第一段',
        'title': '趋势描述 · 三句话',
        'sub': '英二最常考的一段。十年里有八年是动态图，骨架先背死。',
        'items': [
            dict(skel('chart_dynamic'), note='{{chart}} 填 line / bar；{{topic}} 是题眼；两个时间写年份'),
            pool('chart_dynamic', 0),
            pool('chart_dynamic', 1),
            pool('chart_dynamic', 6),
            pool('chart_dynamic', 7),
        ],
    },
    {
        'tag': 'PART 2 · 静态图第一段',
        'title': '占比分布 · 两句骨架',
        'sub': '饼图、柱状图只比占比时用这套。一出现年份就换回动态。',
        'items': [
            dict(skel('chart_static'), note='前半句报总量，后半句由大到小排；{{percent total}} 可写 the first three'),
            pool('chart_static', 0),
            pool('chart_static', 1),
        ],
    },
    {
        'tag': 'PART 3 · 第二段归因',
        'title': '原因段 · 一句骨架 + 四个机制',
        'sub': '骨架只给一句，剩下全靠机制句。挑两个能说通的，别贪多。',
        'items': [
            dict(skel('para2_why'), note='这句是段首，背下来整段就立住了'),
            pool('para2_why', 4),
            pool('para2_why', 1),
            pool('para2_why', 3),
            pool('para2_why', 0),
            pool('para2_why', 2),
        ],
    },
    {
        'tag': 'PART 4 · 第三段正面版',
        'title': '立场 + 建议 · 四类主体',
        'sub': '先表态，再挑两个主体各一句。政府、学校、家庭、个人覆盖绝大多数题目。',
        'items': [
            dict(skel('para3_positive'), note='正面版开场：先把趋势定性为好事，再给一个推论'),
            pool('para3_positive', 1),
            pool('para3_positive', 2),
            pool('para3_positive', 3),
            pool('para3_positive', 6),
        ],
    },
    {
        'tag': 'PART 5 · 第三段负面版',
        'title': '立场 + 对策 · 三句话',
        'sub': '题目指向问题时用这版。语气要硬，动词用 should / must。',
        'items': [
            dict(skel('para3_negative'), note='负面版开场：定性为问题，再用 unless 逼出对策'),
            pool('para3_negative', 0),
            pool('para3_negative', 1),
            pool('para3_negative', 5),
        ],
    },
]

INTRO = [
    ('cover', '三段骨架 · 带背', '大作文不用整篇背，背骨架就够'),
    ('say', '每句话我读两遍。第一遍慢，你跟着念；第二遍正常速度，你先自己默背，再对一下答案。'),
    ('say', '句子里发黄的下划线是空位，考试的时候换成本题的具体词。现在跟着念占位名就行，知道那里该填什么。'),
    ('say', '全片二十多句，九分钟出头。现在开始，第一段。'),
]

RUN_PART = {
    'tag': 'PART 6 · 整段连背',
    'title': '五句骨架 · 连着过一遍',
    'sub': '不暂停、不解释，按考场上的速度连读一遍，找写作文的节奏。',
    'items': [skel('chart_dynamic'), skel('chart_static'), skel('para2_why'),
              skel('para3_positive'), skel('para3_negative')],
}

OUTRO = [
    ('say', '三段骨架过完了。最后提醒一句。'),
    ('say', '模板只是骨架，考场上必须换成本题的具体词和数据。骨架越熟，留给填词的时间越多。'),
    ('say', '再过一遍的方法：关掉声音，看着中文说英文。说得出来，才是真背下来了。'),
]


# ---------------- 文本工具 ----------------
CHIP_RE = re.compile(r'\{\{[^}]+\}\}')
PUNCT_ONLY = re.compile(r'^[,.;:!?%\)\]”"]+$')

CHIP_SPEAK = {}


def chip_name(raw):
    """{{item1}} -> item1"""
    return raw[2:-2].strip()


def chip_speak(raw):
    n = chip_name(raw)
    if n in CHIP_SPEAK:
        return CHIP_SPEAK[n]
    if n.lower() == 'chart':
        # {{chart}} 后紧跟 chart 名词，读作 bar 避免 "chart chart"
        CHIP_SPEAK[n] = 'bar'
        return 'bar'
    m = re.match(r'^([a-z]+?)\s*(\d*)$', n, re.I)
    if m:
        base, num = m.group(1).lower(), m.group(2)
        word = {'item': 'item', 'percent': 'percent', 'num': 'number',
                'time': 'time', 'topic': 'topic', 'chart': 'chart'}.get(base, base)
        out = (word + ' ' + num).strip() if num else word
    else:
        out = n
    CHIP_SPEAK[n] = out
    return out


def tokenize(en):
    """[(kind, text)]，芯片整体保留"""
    toks, i = [], 0
    for m in CHIP_RE.finditer(en):
        for w in en[i:m.start()].split():
            toks.append(('w', w))
        toks.append(('c', m.group(0)))
        i = m.end()
    for w in en[i:].split():
        toks.append(('w', w))
    # 把紧跟芯片的纯标点并进芯片 token
    out = []
    for k, t in toks:
        if out and k == 'w' and PUNCT_ONLY.match(t) and out[-1][0] == 'c':
            out[-1] = ('c', out[-1][1] + t)
        else:
            out.append((k, t))
    return out


def speak_text(toks):
    parts = []
    for k, t in toks:
        if k == 'c':
            m = CHIP_RE.match(t)
            parts.append(chip_speak(m.group(0)))
            if t[m.end():]:
                parts[-1] += t[m.end():]
        else:
            parts.append(t)
    return ' '.join(parts)


def split_blocks(toks):
    """按标点断块，token 带原索引 [(k, t, ti)]"""
    blocks, cur = [], []
    for ti, (k, t) in enumerate(toks):
        cur.append((k, t, ti))
        txt = t          # 芯片 token 已含尾随标点，不能只取 {{...}}
        if re.search(r'[,;:.!?]"?$', txt):
            plain = ''.join(CHIP_RE.match(x[1]).group(0) if x[0] == 'c' else x[1] for x in cur)
            if len(plain) >= 12:
                blocks.append(cur)
                cur = []
    if cur:
        blocks.append(cur)
    return blocks


def norm(w):
    return re.sub(r"[^A-Za-z0-9']", '', w).lower()


def align(toks, words):
    ts = [None] * len(toks)
    j = 0
    for i, (k, t) in enumerate(toks):
        if k == 'c':
            m = CHIP_RE.match(t)
            want = chip_speak(m.group(0))
        else:
            want = t
        wn = [norm(x) for x in want.split()]
        wn = [x for x in wn if x]
        if not wn:
            ts[i] = ts[i - 1] if i else 0.0
            continue
        for look in range(j, min(j + 5, len(words))):
            if norm(words[look][1]) == wn[0]:
                ts[i] = words[look][0]
                j = look + 1
                break
    last = 0.0
    for i in range(len(ts)):
        if ts[i] is None:
            ts[i] = last
        last = ts[i]
    return ts


# ---------------- 渲染 ----------------
def fade_bg():
    img = Image.new('RGB', (W, H), BG_TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        r = y / (H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * r) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    glow = Image.new('L', (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.08, -H * 0.26, W * 0.92, H * 0.24], fill=46)
    glow = glow.filter(ImageFilter.GaussianBlur(190))
    return Image.composite(Image.new('RGB', (W, H), (46, 70, 116)), img, glow)


_FIT = {}


def font(path, size, idx=0):
    key = (path, size, idx)
    if key not in _FIT:
        _FIT[key] = ImageFont.truetype(path, size, index=idx) if path.lower().endswith('.ttc') \
            else ImageFont.truetype(path, size)
    return _FIT[key]


def chip_draw_text(t):
    """芯片 token -> (显示名, 尾随标点)"""
    m = CHIP_RE.match(t)
    return chip_name(m.group(0)), t[m.end():]


def wrap_block(block, size, maxw):
    """块内按词换行 -> [[(kind, text, tail, font, w, tok_idx)]]"""
    f_en = font(FONT_EN, size)
    f_slot = font(FONT_EN_I, int(size * 0.94))
    lines, cur, curw = [], [], 0.0
    for k, t, ti in block:
        if k == 'c':
            name, tail = chip_draw_text(t)
            f = f_slot
            dw = f.getlength(name) + f_en.getlength(tail)
            tk = ('c', name, tail, f, dw, ti)
        else:
            dw = f_en.getlength(t)
            tk = ('w', t, '', f_en, dw, ti)
        sp = f_en.getlength(' ') if cur else 0
        glue = cur and k == 'w' and PUNCT_ONLY.match(t)   # 标点不换行
        if cur and not glue and curw + sp + dw > maxw:
            lines.append(cur)
            cur, curw = [tk], dw
        else:
            if cur:
                cur.append(('sp', ' ', '', f_en, sp, ti))
                curw += sp
            cur.append(tk)
            curw += dw
    if cur:
        lines.append(cur)
    return lines


def layout_all(blocks, size):
    out = []
    for b in blocks:
        lines = wrap_block(b, size, 950)
        widths = [sum(x[4] for x in ln) for ln in lines]
        out.append((lines, max(widths) if widths else 0))
    return out


def measure(laid, size, gap=40):
    n = sum(len(x[0]) for x in laid)
    return int(n * size * 1.42 + (len(laid) - 1) * gap)


AREA = 940
TOP = 250


def cn_rows(item):
    cn = item.get('cn') or ''
    if not cn:
        return []
    return wrap_cn(cn, font(FONT_CN, 30), font(FONT_EN_I, 28), 900)


def pick_layout(blocks, cn_h=0):
    """字号从 68 往下试，英文 + 中文总高不超过 1100"""
    size = 68
    while size > 30:
        laid = layout_all(blocks, size)
        if measure(laid, size) + cn_h <= 1100:
            return size, laid
        size -= 2
    return size, layout_all(blocks, size)


def flatten_lines(laid):
    out = []
    for bi, (lines, bw) in enumerate(laid):
        for ln in lines:
            out.append(ln)
    return out


def line_ti(ln):
    for tk in ln:
        if tk[0] != 'sp':
            return tk[5]
    return 0


def draw_word_line(d, line, x0, y, size, state):
    """state: cur / done / next"""
    col = {'cur': T_CUR, 'done': T_DONE, 'next': T_NEXT}[state]
    scol = {'cur': SLOT_CUR, 'done': SLOT_DONE, 'next': SLOT_NEXT}[state]
    x = x0
    f_en = font(FONT_EN, size)
    for k, t, tail, f, w in [(a, b, c, dd, e) for a, b, c, dd, e, _ in line]:
        if k == 'sp':
            x += w
            continue
        if k == 'w':
            d.text((x, y), t, font=f_en, fill=col)
        else:
            d.text((x, y), t, font=f, fill=scol)
            if tail:
                d.text((x + f.getlength(t), y), tail, font=f_en, fill=col)
            ly = y + size * 1.16
            d.line([(x, ly), (x + w - f_en.getlength(tail), ly)], fill=scol, width=max(2, size // 22))
        x += w


def render_sentence(path, part, idx, total, item, size, laid, lit, mode, progress):
    img = fade_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * progress), 5], fill=ACCENT)

    d.text((W / 2, 92), part['tag'], font=font(FONT_CN, 26), fill=ACCENT, anchor='ma')
    d.text((W / 2, 136), part['title'], font=font(FONT_CN_B, 46), fill=WHITE, anchor='ma')
    d.line([(W / 2 - 46, 218), (W / 2 + 46, 218)], fill=LINE, width=3)

    lines = flatten_lines(laid)
    he = measure(laid, size)
    cn = item.get('cn') or ''
    fcn = font(FONT_CN, 30)
    fslot = font(FONT_EN_I, 28)
    rows_cn = cn_rows(item)
    hc = len(rows_cn) * 48
    total_h = he + (48 + hc if rows_cn else 0)
    y = 290 + max(0, (1140 - total_h) // 2)
    x0base = (W - max(bw for _, bw in laid)) / 2
    li = 0
    for bl, bw in laid:
        for ln in bl:
            state = 'done' if li < lit - 1 else ('cur' if li == lit - 1 else 'next')
            draw_word_line(d, ln, x0base, y, size, state)
            y += int(size * 1.42)
            li += 1
        y += 40

    # 中文
    cny = y + 8
    if rows_cn:
        widths = [sum(x[3] for x in r) for r in rows_cn]
        center_each = len(rows_cn) <= 2
        xc = (W - max(widths)) / 2
        for ln, lw in zip(rows_cn, widths):
            x = (W - lw) / 2 if center_each else xc
            for kind, txt, f, w in ln:
                if kind != 'sp':
                    d.text((x, cny), txt, font=f,
                           fill=(176, 188, 210) if kind == 'c' else CN_COL)
                x += w
            cny += 48

    # 底部跟读胶囊
    label = {'slow': '第一遍 · 慢速跟读',
             'fast': '第二遍 · 自己先背，再对答案',
             'run': '连背 · 只读一遍，跟着走'}[mode]
    fp = font(FONT_CN, 25)
    pw = fp.getlength(label)
    bx = (W - pw) / 2 - 30
    by = 1556
    d.rounded_rectangle([bx, by, bx + pw + 60, by + 56], radius=28,
                        outline=(60, 84, 124), width=2)
    d.text((W / 2, by + 27), label, font=fp,
           fill=(126, 154, 194) if mode == 'slow' else (150, 178, 216), anchor='mm')

    note = re.sub(r'\{\{(.+?)\}\}', r'\1', item.get('note') or '')
    if note:
        fn = font(FONT_CN, 24)
        nrows, cur = [], ''
        for ch in note:
            if fn.getlength(cur + ch) > 900:
                nrows.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            nrows.append(cur)
        if len(nrows) > 2:
            nrows = nrows[:2]
            nrows[1] = nrows[1][:-1] + '…'
        ny = 1636
        for ln in nrows:
            d.text((W / 2, ny), ln, font=fn, fill=(108, 122, 148), anchor='ma')
            ny += 36

    tag = '连背' if mode == 'run' else '第'
    d.text((W / 2, 1830), f'{tag} {idx + 1} / {total}' + ('' if mode == 'run' else ' 句'),
           font=font(FONT_CN, 23), fill=(74, 86, 110), anchor='ma')
    img.save(path, compress_level=3)


def wrap_cn(text, f, fslot, maxw):
    toks = tokenize(text)
    rows, cur, curw = [], [], 0.0
    for k, t in toks:
        glue = bool(cur) and k == 'w' and re.match(r'^[，。、；：！？）」』%]+$', t)
        tk_sp = None
        if k == 'c':
            name, tail = chip_draw_text(t)
            w = fslot.getlength(name) + f.getlength(tail) + 7
            tk = ('c', name, fslot, w)
            tk_sp = ('sp', '', f, 7)
        else:
            w = f.getlength(t + ' ')
            tk = ('w', t, f, w)
        if cur and not glue and curw + (7 if tk_sp else 0) + w > maxw:
            rows.append(cur)
            cur, curw = [], 0.0
        if tk_sp and cur:
            cur.append(tk_sp)
            curw += 7
        cur.append(tk)
        curw += w
    if cur:
        rows.append(cur)
    return rows


def render_card(path, kind, title, sub, progress, tag=None, meta=None):
    img = fade_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * progress), 5], fill=ACCENT)
    if kind == 'cover':
        d.text((W / 2, 690), title, font=font(FONT_CN_B, 66), fill=WHITE, anchor='ma')
        d.line([(W / 2 - 54, 806), (W / 2 + 54, 806), ], fill=(70, 106, 160), width=4)
        d.text((W / 2, 858), sub, font=font(FONT_CN, 32), fill=(154, 172, 200), anchor='ma')
        d.text((W / 2, 962), meta or '', font=font(FONT_CN, 25), fill=(110, 128, 158), anchor='ma')
        d.text((W / 2, 1042), '英语二 · 大作文模板带背', font=font(FONT_CN, 26),
               fill=(92, 110, 140), anchor='ma')
    else:
        d.text((W / 2, 660), tag, font=font(FONT_CN, 26), fill=ACCENT, anchor='ma')
        d.text((W / 2, 716), title, font=font(FONT_CN_B, 60), fill=WHITE, anchor='ma')
        d.line([(W / 2 - 54, 820), (W / 2 + 54, 820)], fill=(70, 106, 160), width=4)
        d.text((W / 2, 868), sub, font=font(FONT_CN, 29), fill=(148, 164, 192), anchor='ma')
        if meta:
            d.text((W / 2, 980), meta, font=font(FONT_CN, 24), fill=(92, 108, 134), anchor='ma')
    img.save(path, compress_level=3)


def render_say(path, text, progress):
    """中文讲解卡：纯旁白画面"""
    img = fade_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * progress), 5], fill=ACCENT)
    f = font(FONT_CN, 40)
    rows, cur, curw = [], [], 0.0
    for ch in text:
        w = f.getlength(ch)
        if cur and curw + w > 760:
            rows.append(''.join(cur))
            cur, curw = [], 0.0
        cur.append(ch)
        curw += w
    if cur:
        rows.append(''.join(cur))
    wmax = max((f.getlength(r) for r in rows), default=0)
    x0 = (W - wmax) / 2
    y = (H - len(rows) * 68) / 2
    for r in rows:
        d.text((x0, y), r, font=f, fill=(228, 236, 248))
        y += 68
    img.save(path, compress_level=3)


# ---------------- TTS ----------------
async def tts(text, voice, rate, path):
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary='WordBoundary')
    words = []
    with open(path, 'wb') as f:
        async for ch in comm.stream():
            if ch['type'] == 'audio':
                f.write(ch['data'])
            elif ch['type'] == 'WordBoundary':
                words.append((ch['offset'] / 1e7, ch['text']))
    return words


async def tts_all(jobs, conc=3):
    sem = asyncio.Semaphore(conc)
    res = {}

    async def one(key, text, voice, rate, path):
        jp = path + '.json'
        if os.path.exists(path) and os.path.exists(jp) and os.path.getsize(path) > 1000:
            with open(jp, encoding='utf-8') as f:
                res[key] = [tuple(x) for x in json.load(f)]
            return
        async with sem:
            for attempt in range(3):
                try:
                    w = await tts(text, voice, rate, path)
                    res[key] = w
                    with open(jp, 'w', encoding='utf-8') as f:
                        json.dump(w, f)
                    return
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(1.5)

    await asyncio.gather(*[one(*j) for j in jobs])
    return res


# ---------------- ffmpeg ----------------
def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode != 0:
        raise RuntimeError('ffmpeg fail: ' + ' '.join(cmd[:10]) + '\n' + (p.stderr or '')[-1500:])
    return p


def dur(path):
    p = subprocess.run([FFMPEG, '-v', 'error', '-i', path, '-ar', '24000', '-ac', '1',
                        '-f', 's16le', '-'], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('decode fail: ' + path)
    return len(p.stdout) / 2 / 24000


def akey(*parts):
    return hashlib.md5('|'.join(parts).encode('utf-8')).hexdigest()[:14]


def to_m4a(src, out):
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', src, '-ar', '24000', '-ac', '1',
         '-c:a', 'aac', '-b:a', '80k', out])
    return dur(out)


def pad_tail(src, out, tail=0.8):
    """音频 + 尾部静音"""
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', src,
         '-f', 'lavfi', '-t', str(tail), '-i', 'anullsrc=r=24000:cl=mono',
         '-filter_complex',
         '[0:a]aresample=24000,aformat=channel_layouts=mono[a0];'
         '[a0][1:a]concat=n=2:v=0:a=1[out]',
         '-map', '[out]', '-ar', '24000', '-ac', '1', '-c:a', 'aac', '-b:a', '80k', out])
    return dur(out)


def mix_slow_fast(slow, fast, out, gap1=1.0, gap2=2.6):
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', slow, '-i', fast,
         '-f', 'lavfi', '-t', str(gap1), '-i', 'anullsrc=r=24000:cl=mono',
         '-f', 'lavfi', '-t', str(gap2), '-i', 'anullsrc=r=24000:cl=mono',
         '-filter_complex',
         '[0:a]aresample=24000,aformat=channel_layouts=mono[a0];'
         '[1:a]aresample=24000,aformat=channel_layouts=mono[a1];'
         '[a0][2:a][a1][3:a]concat=n=4:v=0:a=1[out]',
         '-map', '[out]', '-ar', '24000', '-ac', '1', '-c:a', 'aac', '-b:a', '80k', out])
    return dur(out)


# ---------------- 主流程 ----------------
async def main():
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--only='):
            only = [int(x) for x in a.split('=')[1].split(',')]
        elif a == '--full':
            only = None

    fa = os.path.join(BUILD, 'audio')
    ffr = os.path.join(BUILD, 'frames')
    if os.path.isdir(ffr):
        shutil.rmtree(ffr)
    os.makedirs(fa, exist_ok=True)
    os.makedirs(ffr, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- 组装任务清单（order 即时间顺序） ----
    seq = []   # dict(kind=card|say|sent, ...)
    for i, (kind, *rest) in enumerate(INTRO):
        if kind == 'cover':
            seq.append({'kind': 'cover', 'title': rest[0], 'sub': rest[1], 'cn': '这套视频只做一件事：' + rest[1]})
        else:
            seq.append({'kind': 'say', 'text': rest[0]})
    for pi, part in enumerate(PARTS):
        if only is not None and pi not in only:
            continue
        seq.append({'kind': 'card', 'part': part, 'pi': pi})
        for si, item in enumerate(part['items']):
            seq.append({'kind': 'sent', 'part': part, 'pi': pi, 'si': si,
                        'item': item, 'toks': tokenize(item['en']),
                        'blocks': split_blocks(tokenize(item['en']))})
    if only is None:
        seq.append({'kind': 'card', 'part': RUN_PART, 'pi': 99})
        for ri, item in enumerate(RUN_PART['items']):
            _t = tokenize(item['en'])
            seq.append({'kind': 'run', 'part': RUN_PART, 'pi': 99, 'si': ri,
                        'item': item, 'toks': _t, 'blocks': split_blocks(_t)})
    for kind, *rest in OUTRO:
        seq.append({'kind': 'say', 'text': rest[0]})
    seq.append({'kind': 'cover', 'title': '背骨架 · 不背整篇',
                'sub': '下一集：小作文十类模板带你过一遍', 'cn': '背骨架，不背整篇。下一集，小作文。'})

    total_sent = len([x for x in seq if x['kind'] == 'sent'])
    print(f'共 {len(seq)} 个画面段，其中句子 {total_sent} 句')

    # ---- TTS 任务 ----
    jobs = []
    for i, s in enumerate(seq):
        if s['kind'] in ('sent', 'run'):
            st = speak_text(s['toks'])
            if s['kind'] == 'sent':
                s['slow_p'] = os.path.join(fa, akey(st, VOICE_EN, RATE_SLOW) + '_s.mp3')
                jobs.append((f'{i}_slow', st, VOICE_EN, RATE_SLOW, s['slow_p']))
            s['fast_p'] = os.path.join(fa, akey(st, VOICE_EN, RATE_FAST) + '_f.mp3')
            jobs.append((f'{i}_fast', st, VOICE_EN, RATE_FAST, s['fast_p']))
        else:
            txt = s.get('cn') or (s['part']['title'] + '。' + s['part']['sub'] if s['kind'] == 'card' else s['text'])
            s['cn_p'] = os.path.join(fa, akey(txt, VOICE_CN) + '_c.mp3')
            jobs.append((f'{i}_cn', txt, VOICE_CN, '-5%', s['cn_p']))
    print(f'TTS 任务 {len(jobs)} 条')
    words = await tts_all(jobs)
    print('TTS 完成')

    # ---- 逐段音频 + 帧 ----
    concat_lines = []
    audio_segs = []
    for i, s in enumerate(seq):
        seg = os.path.join(fa, f'seg_{i:04d}.m4a')
        if s['kind'] in ('cover', 'card', 'say'):
            d0 = to_m4a(s['cn_p'], seg)
            png = os.path.join(ffr, f'f_{i:04d}.png')
            prog = (i + 1) / len(seq)
            if s['kind'] == 'cover':
                render_card(png, 'cover', s['title'], s['sub'], prog,
                            meta=f'共 {total_sent} 句 · 每句读两遍')
            elif s['kind'] == 'card':
                p = s['part']
                render_card(png, 'part', p['title'], p['sub'], prog, tag=p['tag'],
                            meta=f'本段 {len(p["items"])} 句')
            else:
                render_say(png, s['text'], prog)
            concat_lines.append((png, d0 + 0.45))
            audio_segs.append(seg)
            print(f'  [{i+1}/{len(seq)}] {s["kind"]:<5} {d0:5.1f}s  {s.get("text", s.get("title", ""))[:26]}')
            continue

        part, item = s['part'], s['item']
        if s['kind'] == 'run':
            fast = s['fast_p']
            segd = pad_tail(fast, seg, 0.85)
            blocks = s['blocks']
            _nh = len(cn_rows(item))
            size, laid = pick_layout(blocks, 48 + _nh * 48 if _nh else 0)
            n = len(flatten_lines(laid))
            png = os.path.join(ffr, f'f_{i:04d}_run.png')
            render_sentence(png, part, s['si'], len(part['items']), item,
                            size, laid, n, 'run', (i + 1) / len(seq))
            concat_lines.append((png, segd))
            audio_segs.append(seg)
            print(f'  [{i+1}/{len(seq)}] run   {segd:5.1f}s  {item["en"][:34]}')
            continue

        slow, fast = s['slow_p'], s['fast_p']
        segd = mix_slow_fast(slow, fast, seg)
        slowd = dur(slow)
        blocks = s['blocks']

        _nh = len(cn_rows(item))
        size, laid = pick_layout(blocks, 48 + _nh * 48 if _nh else 0)
        lines = flatten_lines(laid)
        ts = align(s['toks'], words.get(f'{i}_slow', []))
        # 每行起点时间，保证单调
        starts, prev = [], 0.0
        for ln in lines:
            v = ts[line_ti(ln)] if ts else 0.0
            v = max(v, prev)
            starts.append(v)
            prev = v
        bounds = starts + [max(slowd, prev)]

        prog = (i + 1) / len(seq)
        for li in range(len(lines)):
            span = max(0.5, bounds[li + 1] - bounds[li])
            png = os.path.join(ffr, f'f_{i:04d}_{li}.png')
            render_sentence(png, part, s['si'], len(part['items']), item,
                            size, laid, li + 1, 'slow', prog)
            concat_lines.append((png, span))

        png = os.path.join(ffr, f'f_{i:04d}_f.png')
        render_sentence(png, part, s['si'], len(part['items']), item,
                        size, laid, len(lines), 'fast', prog)
        concat_lines.append((png, max(0.6, segd - slowd)))
        audio_segs.append(seg)
        print(f'  [{i+1}/{len(seq)}] sent  {segd:5.1f}s  行{len(lines)} sz{size}  {item["en"][:34]}')

    # ---- 拼音频 ----
    alist = os.path.join(BUILD, 'audio_list.txt')
    with open(alist, 'w', encoding='utf-8') as f:
        for p in audio_segs:
            f.write("file '%s'\n" % p.replace('\\', '/'))
    audio_all = os.path.join(BUILD, 'audio_all.m4a')
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', alist, '-c', 'copy', audio_all])
    total_d = dur(audio_all)

    # ---- 拼视频（等比缩放帧时长，与音轨严格等长） ----
    sum_d = sum(dd for _, dd in concat_lines)
    k = total_d / sum_d
    vlist = os.path.join(BUILD, 'video_list.txt')
    with open(vlist, 'w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n')
        for png, dd in concat_lines:
            f.write("file '%s'\n" % png.replace('\\', '/'))
            f.write('duration %.3f\n' % (dd * k))
        f.write("file '%s'\n" % concat_lines[-1][0].replace('\\', '/'))

    silent = os.path.join(BUILD, 'video_silent.mp4')
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', vlist,
         '-r', str(FPS), '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'medium',
         '-crf', '20', '-tune', 'stillimage', silent])

    name = '大作文模板带背_骨架篇.mp4' if only is None else 'preview_part.mp4'
    final = os.path.join(OUT_DIR, name)
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', silent, '-i', audio_all,
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-shortest',
         '-movflags', '+faststart', final])
    print(f'完成 -> {final}  {os.path.getsize(final)/1e6:.1f} MB  {total_d/60:.2f} min')


if __name__ == '__main__':
    import edge_tts
    asyncio.run(main())
