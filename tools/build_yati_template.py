# -*- coding: utf-8 -*-
"""押题范文数据生成器（26 篇：大作文 18 + 小作文 8）。

规则（用户 2026-11-20 三次修订后定稿）：
  · 范文内容回退为 ai归来版范文.pdf 的原始英文（1fd2a10 版本），
    不再用模板句池按 tag 硬套——用户反馈机制句「太僵硬、套不进其他作文」。
  · 逐句中文来自 tools/yati_orig_cn.py，英文分句骨架来自 tools/yati_orig_en.json。
  · 保留呈现字段：title / en / notes / img / words 与分组、顺序不变。
  · 前端功能保留：词可点查释义、数字金底、逐句点开中文、整篇中文对照、
    图片不新标签打开——这些都由 yati.js / style.css 负责，不在本文件。

真源：tools/yati_orig_en.json + tools/yati_orig_cn.py + 现有 yati.json 的呈现字段。
数据只由本文件生成为 pwa/data/yati.json，不要手改 JSON。
幂等：重复运行得到相同结果。

用法：python tools/build_yati_template.py
"""
import json, os, io, re, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWA = os.path.join(ROOT, 'pwa')
YATI = os.path.join(PWA, 'data', 'yati.json')
EN_FILE = os.path.join(ROOT, 'tools', 'yati_orig_en.json')
CN_FILE = os.path.join(ROOT, 'tools', 'yati_orig_cn.py')

with io.open(EN_FILE, encoding='utf-8') as f:
    ORIG = json.load(f)
_spec = importlib.util.spec_from_file_location('yati_orig_cn', CN_FILE)
CN_MOD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(CN_MOD)
CN = CN_MOD.CN

with io.open(YATI, encoding='utf-8') as f:
    Y = json.load(f)

# ── 先对齐断言：骨架 / 译文 / 现有条目三方一致 ──────────────
cur = {it['no']: it for g in Y['groups'] for it in g['items']}
if set(cur) != {int(n) for n in ORIG} or set(cur) != set(CN):
    raise SystemExit('题号不齐: yati=%d orig=%d cn=%d' % (len(cur), len(ORIG), len(CN)))

for no_s, e in ORIG.items():
    no = int(no_s)
    cb = CN[no]
    if len(cb) != len(e['blocks']):
        raise SystemExit('NO%d 段数不符 en=%d cn=%d' % (no, len(e['blocks']), len(cb)))
    for bi, (b, csegs) in enumerate(zip(e['blocks'], cb)):
        if len(csegs) != len(b['sents']):
            raise SystemExit('NO%d B%d 句数不符 en=%d cn=%d' % (no, bi, len(b['sents']), len(csegs)))

# ── 替换 blocks：英文原句 + 逐句中文；保留 v（段落原文）与呈现字段 ──
wc_bad = []
for g in Y['groups']:
    for it in g['items']:
        no = it['no']
        e = ORIG[str(no)]
        cb = CN[no]
        it['blocks'] = [
            {
                'k': b['k'], 'v': b['v'],
                'sents': [{'en': en, 'cn': cn} for en, cn in zip(b['sents'], csegs)],
            }
            for b, csegs in zip(e['blocks'], cb)
        ]
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", ' '.join(b['v'] for b in it['blocks'])))
        it['words'] = words
        is_small = g['id'] == 't1'
        lo, hi = (85, 125) if is_small else (130, 200)
        if not (lo <= words <= hi):
            wc_bad.append((no, words, '小' if is_small else '大'))

with io.open(YATI, 'w', encoding='utf-8') as f:
    json.dump(Y, f, ensure_ascii=False, indent=1)

# ── 校验 ────────────────────────────────────────────────────
CJK = re.compile(r'[\u4e00-\u9fff]')
err = []
sent_n = 0
for g in Y['groups']:
    for it in g['items']:
        for b in it['blocks']:
            if not b.get('sents'):
                err.append('%d 缺 sents' % it['no'])
            for s in b.get('sents', []):
                sent_n += 1
                if not s.get('en') or not s.get('cn'):
                    err.append('%d 空 en/cn' % it['no'])
                    continue
                if '{{' in s['en'] or '{{' in s['cn'] or '}}' in s['en']:
                    err.append('%d 残留占位符 %s' % (it['no'], s['en']))
                if not CJK.search(s['cn']):
                    err.append('%d 中文缺失 %s' % (it['no'], s['cn'][:40]))
                if len(re.findall(r"[A-Za-z][A-Za-z'-]*", s['cn'])) >= 4:
                    err.append('%d 中文夹杂英文 %s' % (it['no'], s['cn'][:50]))

print('生成 26 篇，逐句 %d 条' % sent_n)
print('结构/译文错误:', err[:12] if err else '无')
print('词数越界:', wc_bad if wc_bad else '无')
if err or wc_bad:
    raise SystemExit(1)
