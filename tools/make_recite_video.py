# -*- coding: utf-8 -*-
"""
模板带背视频生成器（大作文骨架篇 · 横屏 1920x1080）

链路：writing_templates.json 取句 -> edge-tts 逐句合成（慢读 + 原速）
      -> wav 精确拼接（无 aac 填充误差）-> WordBoundary 对齐行首
      -> Pillow 渲染帧 -> ffmpeg 按帧数精确编码 + 混音 -> mp4

音画同步要点：
  1. 中间产物一律 pcm wav（样本数即时长），不像 aac 每段有 priming/padding；
  2. 每段帧数用「累积时间取整」分配，误差不跨段累积；
  3. 编码时 -frames:v 精确截断到总帧数，音轨 apad 后 -t 裁到同一时长。

用法：python tools/make_recite_video.py [--only=0,1]
"""
import os, sys, json, re, asyncio, subprocess, shutil, hashlib, wave, array
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')
BUILD = os.path.join(ROOT, 'build_video')
OUT_DIR = os.path.join(ROOT, 'output')
# Trae 自带的 ffmpeg 是精简构建（无 mp3/wav/aac），改用 imageio-ffmpeg 的完整版
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

W, H = 1920, 1080          # 横屏 16:9
FPS = 25
SR = 24000                 # 统一采样率，wav 直接按样本拼
MX = 130                   # 左右页边距

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
DIM = (96, 112, 140)
DIM2 = (74, 86, 110)

# 版面（横屏）
TOP_BAR = 100              # 顶栏分隔线 y
EN_TOP = 150               # 英文区上边界
EN_AREA = 690              # 英文 + 中文可用高度
CN_LH = 48                 # 中文行高
CAP_Y = 884                # 底部胶囊 y
NOTE_Y = 954               # 底部提示 y

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

# 头尾只留画面，不配旁白（旁白属于「无意义音频」，全删）
HEAD = {'title': '三段骨架 · 带背', 'sub': '五段骨架拆开念 · 每句两遍', 'sec': 2.4}
TAIL = {'title': '背骨架 · 不背整篇', 'sub': '模板只是骨架，考场上换成本题的具体词', 'sec': 2.6}

RUN_PART = {
    'tag': 'PART 6 · 整段连背',
    'title': '五句骨架 · 连着过一遍',
    'sub': '不暂停、不解释，按考场上的速度连读一遍，找写作文的节奏。',
    'items': [skel('chart_dynamic'), skel('chart_static'), skel('para2_why'),
              skel('para3_positive'), skel('para3_negative')],
}

CARD_SEC = 2.2     # 分段卡片静默时长
GAP1 = 0.8         # 慢读 -> 原速 之间
GAP2 = 1.8         # 原速 -> 下一句 之间（留给自己背）
RUN_TAIL = 0.9


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
    gd.ellipse([W * 0.10, -H * 0.30, W * 0.90, H * 0.26], fill=44)
    glow = glow.filter(ImageFilter.GaussianBlur(200))
    return Image.composite(Image.new('RGB', (W, H), (44, 68, 112)), img, glow)


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
        lines = wrap_block(b, size, W - 2 * MX)
        widths = [sum(x[4] for x in ln) for ln in lines]
        out.append((lines, max(widths) if widths else 0))
    return out


def measure(laid, size, gap=34):
    n = sum(len(x[0]) for x in laid)
    return int(n * size * 1.42 + (len(laid) - 1) * gap)


def cn_rows(item):
    cn = item.get('cn') or ''
    if not cn:
        return []
    return wrap_cn(cn, font(FONT_CN, 32), font(FONT_EN_I, 30), W - 2 * MX)


def pick_layout(blocks, cn_h=0):
    """字号从 72 往下试：能压成一行就停下来；否则取满足高度约束的最大字号"""
    fallback = None
    size = 72
    while size >= 32:
        laid = layout_all(blocks, size)
        if measure(laid, size) + cn_h <= EN_AREA:
            if fallback is None:
                fallback = (size, laid)
            # 能压一行就一行；但别为了一行把字缩得太小
            if sum(len(ls) for ls, _ in laid) <= 1 and size >= 56:
                return size, laid
        size -= 2
    return fallback or (32, layout_all(blocks, 32))


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
            ly = y + size * 1.14
            d.line([(x, ly), (x + w - f_en.getlength(tail), ly)], fill=scol, width=max(2, size // 24))
        x += w


def render_sentence(path, part, idx, total, item, size, laid, lit, mode, progress):
    img = fade_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * progress), 4], fill=ACCENT)

    # 顶栏：左 PART 标签 / 右 序号
    d.text((MX, 46), part['tag'], font=font(FONT_CN, 27), fill=ACCENT)
    label = f'连背 {idx + 1} / {total}' if mode == 'run' else f'第 {idx + 1} / {total} 句'
    d.text((W - MX, 46), label, font=font(FONT_CN, 25), fill=DIM, anchor='ra')
    d.line([(MX, TOP_BAR), (W - MX, TOP_BAR)], fill=LINE, width=2)

    # 英文 + 中文整体垂直居中
    lines = flatten_lines(laid)
    he = measure(laid, size)
    rows_cn = cn_rows(item)
    hc = len(rows_cn) * CN_LH
    block_h = he + (40 + hc if rows_cn else 0)
    y = EN_TOP + max(0, (EN_AREA - block_h) // 2)

    li = 0
    for bl, bw in laid:
        for ln in bl:
            if mode == 'run':
                state = 'cur'      # 连背只读一遍，整段全亮，不搞逐行明暗
            else:
                state = 'done' if li < lit - 1 else ('cur' if li == lit - 1 else 'next')
            draw_word_line(d, ln, MX, y, size, state)
            y += int(size * 1.42)
            li += 1
        y += 34

    # 中文译文
    if rows_cn:
        cny = y + 6
        fcn2 = font(FONT_CN, 32)
        fsl2 = font(FONT_EN_I, 30)
        for ln in rows_cn:
            x = MX
            for u in ln:
                if u[0] == 'c':
                    if x > MX:
                        x += 6
                    d.text((x, cny), u[1], font=fsl2, fill=(176, 188, 210))
                    x += fsl2.getlength(u[1])
                    if u[2]:
                        d.text((x, cny), u[2], font=fcn2, fill=CN_COL)
                        x += fcn2.getlength(u[2])
                    x += 6
                else:
                    d.text((x, cny), u[1], font=fcn2, fill=CN_COL)
                    x += fcn2.getlength(u[1])
            cny += CN_LH

    # 底部跟读胶囊
    cap = {'slow': '第一遍 · 慢速跟读',
           'fast': '第二遍 · 自己先背，再对答案',
           'run': '连背 · 只读一遍，跟着走'}[mode]
    fp = font(FONT_CN, 26)
    pw = fp.getlength(cap)
    bx = (W - pw) / 2 - 34
    d.rounded_rectangle([bx, CAP_Y, bx + pw + 68, CAP_Y + 58], radius=29,
                        outline=(58, 82, 122), width=2)
    d.text((W / 2, CAP_Y + 29), cap, font=fp,
           fill=(130, 158, 198) if mode == 'slow' else (154, 182, 220), anchor='mm')

    # 底部提示（占位符说明等）
    note = re.sub(r'\{\{(.+?)\}\}', r'\1', item.get('note') or '')
    if note and mode != 'run':          # 连背段不摆长提示，只求跟得上
        fn = font(FONT_CN, 25)
        lim = W - 2 * MX - 40
        if fn.getlength(note) > lim:
            ell = fn.getlength('…')
            while note and fn.getlength(note) + ell > lim:
                note = note[:-1]
            note += '…'
        d.text((W / 2, NOTE_Y), note, font=fn, fill=(104, 118, 145), anchor='ma')

    img.save(path, compress_level=3)


def wrap_cn(text, f, fslot, maxw):
    """中文按字符折行；芯片整体不可拆；标点不落到行首（行尾悬挂）"""
    NO_HEAD = '，。、；：！？）》」』%…·'
    units = []
    for k, t in tokenize(text):
        if k == 'c':
            name, tail = chip_draw_text(t)
            units.append(('c', name, tail))
        else:
            for ch in t:
                units.append(('w', ch))

    rows, cur, curw = [], [], 0.0
    for u in units:
        if u[0] == 'c':
            w = fslot.getlength(u[1]) + f.getlength(u[2])
            head_punct = False
        else:
            w = f.getlength(u[1])
            head_punct = u[1] in NO_HEAD
        if cur and curw + w > maxw and not head_punct:
            rows.append(cur)
            cur, curw = [], 0.0
        cur.append(u)
        curw += w
    if cur:
        rows.append(cur)
    return rows


def render_card(path, kind, title, sub, progress, tag=None, meta=None):
    img = fade_bg()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * progress), 4], fill=ACCENT)
    if kind == 'cover':
        d.text((W / 2, 372), title, font=font(FONT_CN_B, 76), fill=WHITE, anchor='ma')
        d.line([(W / 2 - 60, 500), (W / 2 + 60, 500)], fill=(70, 106, 160), width=4)
        d.text((W / 2, 552), sub, font=font(FONT_CN, 34), fill=(158, 176, 204), anchor='ma')
        if meta:
            d.text((W / 2, 634), meta, font=font(FONT_CN, 26), fill=(108, 126, 156), anchor='ma')
        d.text((W / 2, 952), '英语二 · 大作文模板带背', font=font(FONT_CN, 25),
               fill=(86, 102, 132), anchor='ma')
    else:
        d.text((W / 2, 372), tag, font=font(FONT_CN, 28), fill=ACCENT, anchor='ma')
        d.text((W / 2, 424), title, font=font(FONT_CN_B, 66), fill=WHITE, anchor='ma')
        d.line([(W / 2 - 60, 534), (W / 2 + 60, 534)], fill=(70, 106, 160), width=4)
        d.text((W / 2, 584), sub, font=font(FONT_CN, 30), fill=(148, 164, 192), anchor='ma')
        if meta:
            d.text((W / 2, 660), meta, font=font(FONT_CN, 25), fill=(92, 108, 134), anchor='ma')
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


# ---------------- 音频（wav 精确拼接） ----------------
def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if p.returncode != 0:
        raise RuntimeError('ffmpeg fail: ' + ' '.join(cmd[:10]) + '\n' + (p.stderr or '')[-1500:])
    return p


def wav_dur(p):
    with wave.open(p, 'rb') as w:
        return w.getnframes() / w.getframerate()


def akey(*parts):
    return hashlib.md5('|'.join(parts).encode('utf-8')).hexdigest()[:14]


def mp3_wav(mp3):
    """mp3 -> 24k mono wav，并裁掉开头固定静音（edge-tts 每句约 0.16s）

    返回 (wav, lead秒)。lead 用于把词边界时间戳整体前移，保证画面切换与开口严格对齐。
    """
    wav = os.path.splitext(mp3)[0] + '.wav'
    lp = wav + '.lead'
    if os.path.exists(wav) and os.path.exists(lp) and os.path.getmtime(wav) >= os.path.getmtime(mp3):
        with open(lp) as f:
            return wav, float(f.read().strip())

    p = subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', mp3,
                        '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_s16le', '-f', 's16le', '-'],
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError('decode fail: ' + mp3)
    a = array.array('h')
    a.frombytes(p.stdout)
    thr = 500           # ≈ -36 dBFS，低于此视为静音
    i = 0
    while i < len(a) and abs(a[i]) < thr:
        i += 1
    lead = max(0, i - int(0.03 * SR))      # 回退 30ms 保留起音
    with _wopen(wav) as o:
        o.writeframes(a[lead:].tobytes())
    with open(lp, 'w') as f:
        f.write('%.4f' % (lead / SR))
    return wav, lead / SR


def _wopen(path):
    o = wave.open(path, 'wb')
    o.setnchannels(1)
    o.setsampwidth(2)
    o.setframerate(SR)
    return o


def write_silence(out, sec):
    n = int(round(sec * SR))
    with _wopen(out) as o:
        chunk = b'\x00\x00' * SR
        left = n
        while left > 0:
            k = min(left, SR)
            o.writeframes(chunk[:k * 2])
            left -= k
    return n / SR


def mix_slow_fast(slow_wav, fast_wav, out, gap1=GAP1, gap2=GAP2):
    """慢读 + 静 + 原速 + 静，样本级精确"""
    with _wopen(out) as o:
        with wave.open(slow_wav, 'rb') as a:
            o.writeframes(a.readframes(a.getnframes()))
        o.writeframes(b'\x00\x00' * int(round(gap1 * SR)))
        with wave.open(fast_wav, 'rb') as b:
            o.writeframes(b.readframes(b.getnframes()))
        o.writeframes(b'\x00\x00' * int(round(gap2 * SR)))
    return wav_dur(out)


def mix_run(fast_wav, out, tail=RUN_TAIL):
    with _wopen(out) as o:
        with wave.open(fast_wav, 'rb') as b:
            o.writeframes(b.readframes(b.getnframes()))
        o.writeframes(b'\x00\x00' * int(round(tail * SR)))
    return wav_dur(out)


def concat_wavs(paths, out):
    with _wopen(out) as o:
        for p in paths:
            with wave.open(p, 'rb') as w:
                o.writeframes(w.readframes(w.getnframes()))
    return wav_dur(out)


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
    seq = [{'kind': 'cover', 'title': HEAD['title'], 'sub': HEAD['sub'], 'sec': HEAD['sec']}]
    for pi, part in enumerate(PARTS):
        if only is not None and pi not in only:
            continue
        seq.append({'kind': 'card', 'part': part, 'pi': pi, 'sec': CARD_SEC})
        for si, item in enumerate(part['items']):
            seq.append({'kind': 'sent', 'part': part, 'pi': pi, 'si': si,
                        'item': item, 'toks': tokenize(item['en']),
                        'blocks': split_blocks(tokenize(item['en']))})
    if only is None:
        seq.append({'kind': 'card', 'part': RUN_PART, 'pi': 99, 'sec': CARD_SEC})
        for ri, item in enumerate(RUN_PART['items']):
            _t = tokenize(item['en'])
            seq.append({'kind': 'run', 'part': RUN_PART, 'pi': 99, 'si': ri,
                        'item': item, 'toks': _t, 'blocks': split_blocks(_t)})
    seq.append({'kind': 'cover', 'title': TAIL['title'], 'sub': TAIL['sub'],
                'sec': TAIL['sec'], 'tail': True})

    total_sent = len([x for x in seq if x['kind'] == 'sent'])
    print(f'共 {len(seq)} 个画面段，其中句子 {total_sent} 句（无旁白，仅英文朗读）')

    # ---- TTS 任务（只有句子 / 连背段有音频） ----
    jobs = []
    for i, s in enumerate(seq):
        if s['kind'] in ('sent', 'run'):
            st = speak_text(s['toks'])
            if s['kind'] == 'sent':
                s['slow_p'] = os.path.join(fa, akey(st, VOICE_EN, RATE_SLOW) + '_s.mp3')
                jobs.append((f'{i}_slow', st, VOICE_EN, RATE_SLOW, s['slow_p']))
            s['fast_p'] = os.path.join(fa, akey(st, VOICE_EN, RATE_FAST) + '_f.mp3')
            jobs.append((f'{i}_fast', st, VOICE_EN, RATE_FAST, s['fast_p']))
    print(f'TTS 任务 {len(jobs)} 条')
    words = await tts_all(jobs)
    print('TTS 完成')

    # ---- 逐段：音频 wav + 画面帧计划 ----
    seg_paths = []
    frame_plan = []      # [(png, seconds)]
    for i, s in enumerate(seq):
        segw = os.path.join(fa, f'seg_{i:04d}.wav')
        prog = (i + 1) / len(seq)
        png = os.path.join(ffr, f'f_{i:04d}.png')

        if s['kind'] in ('cover', 'card'):
            d0 = write_silence(segw, s['sec'])
            if s['kind'] == 'cover':
                meta = None if s.get('tail') else f'共 {total_sent} 句 · 每句念两遍'
                render_card(png, 'cover', s['title'], s['sub'], prog, meta=meta)
            else:
                p = s['part']
                render_card(png, 'part', p['title'], p['sub'], prog, tag=p['tag'],
                            meta=f'本段 {len(p["items"])} 句')
            frame_plan.append((png, d0))
            seg_paths.append(segw)
            print(f'  [{i+1}/{len(seq)}] {s["kind"]:<5} {d0:5.1f}s  静默  '
                  f'{s.get("title", s.get("part", {}).get("title", ""))[:26]}')
            continue

        part, item = s['part'], s['item']

        if s['kind'] == 'run':
            fastw, _ = mp3_wav(s['fast_p'])
            d0 = mix_run(fastw, segw)
            blocks = s['blocks']
            _nh = len(cn_rows(item))
            size, laid = pick_layout(blocks, 40 + _nh * CN_LH if _nh else 0)
            n = len(flatten_lines(laid))
            render_sentence(png, part, s['si'], len(part['items']), item,
                            size, laid, n, 'run', prog)
            frame_plan.append((png, d0))
            seg_paths.append(segw)
            print(f'  [{i+1}/{len(seq)}] run   {d0:5.1f}s  {item["en"][:34]}')
            continue

        sloww, lead_s = mp3_wav(s['slow_p'])
        fastw, _ = mp3_wav(s['fast_p'])
        d0 = mix_slow_fast(sloww, fastw, segw)
        slowd = wav_dur(sloww)
        blocks = s['blocks']
        _nh = len(cn_rows(item))
        size, laid = pick_layout(blocks, 40 + _nh * CN_LH if _nh else 0)
        lines = flatten_lines(laid)

        ts = [max(0.0, v - lead_s) for v in align(s['toks'], words.get(f'{i}_slow', []))]
        starts, prev = [], 0.0
        for li, ln in enumerate(lines):
            v = ts[line_ti(ln)] if ts else 0.0
            v = max(v, prev)
            if li == 0:
                v = 0.0            # 第一行从 0 起，避免开头多一截静止帧
            starts.append(v)
            prev = v
        bounds = starts + [slowd]

        for li in range(len(lines)):
            span = max(0.45, bounds[li + 1] - bounds[li])
            png = os.path.join(ffr, f'f_{i:04d}_{li}.png')
            render_sentence(png, part, s['si'], len(part['items']), item,
                            size, laid, li + 1, 'slow', prog)
            frame_plan.append((png, span))

        png = os.path.join(ffr, f'f_{i:04d}_f.png')
        render_sentence(png, part, s['si'], len(part['items']), item,
                        size, laid, len(lines), 'fast', prog)
        frame_plan.append((png, max(0.5, d0 - slowd)))
        seg_paths.append(segw)
        print(f'  [{i+1}/{len(seq)}] sent  {d0:5.1f}s  行{len(lines)} sz{size}  {item["en"][:32]}')

    # ---- 拼总音轨 ----
    audio_all = os.path.join(BUILD, 'audio_all.wav')
    a_dur = concat_wavs(seg_paths, audio_all)
    print(f'总音轨 {a_dur:.2f}s')

    # ---- 帧数分配：按累积时间取整，误差不跨段累积 ----
    plan = []
    acc_t, acc_f = 0.0, 0
    for png, dd in frame_plan:
        acc_t += dd
        nf = int(round(acc_t * FPS)) - acc_f
        if nf < 1:
            nf = 1
        acc_f += nf
        plan.append((png, nf))
    total_frames = acc_f
    v_dur = total_frames / FPS

    vlist = os.path.join(BUILD, 'video_list.txt')
    with open(vlist, 'w', encoding='utf-8') as f:
        f.write('ffconcat version 1.0\n')
        for png, nf in plan:
            f.write("file '%s'\n" % png.replace('\\', '/'))
            f.write('duration %.6f\n' % (nf / FPS))
        f.write("file '%s'\n" % plan[-1][0].replace('\\', '/'))

    silent = os.path.join(BUILD, 'video_silent.mp4')
    run([FFMPEG, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', vlist,
         '-r', str(FPS), '-frames:v', str(total_frames),
         '-pix_fmt', 'yuv420p', '-c:v', 'libx264', '-preset', 'medium',
         '-crf', '20', '-tune', 'stillimage', silent])

    name = '大作文模板带背_骨架篇.mp4' if only is None else 'preview_part.mp4'
    final = os.path.join(OUT_DIR, name)
    run([FFMPEG, '-y', '-loglevel', 'error', '-i', silent, '-i', audio_all,
         '-c:v', 'copy', '-af', 'apad', '-c:a', 'aac', '-b:a', '128k',
         '-t', '%.3f' % v_dur, '-movflags', '+faststart', final])
    print(f'帧 {total_frames} / 音轨 {a_dur:.2f}s / 成片 {v_dur:.2f}s')
    print(f'完成 -> {final}  {os.path.getsize(final)/1e6:.1f} MB  {v_dur/60:.2f} min')


if __name__ == '__main__':
    import edge_tts
    asyncio.run(main())
