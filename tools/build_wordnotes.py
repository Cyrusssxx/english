# -*- coding: utf-8 -*-
"""生成熟词僻义表格数据 pwa/data/wordnotes.json
（按词频降序 · 原句只取含该词的短句 · 译文清洗掉讲义分析文字）

数据来源（全部为已有资料，无 AI 生成）：
  1) 单词 + 僻义：pwa/data/deck_tc_senses.json（唐迟·熟词僻义，OCR + 人工核对）
  2) 熟义：tools/ecdict.csv 的 translation 首义（取前 2 个义项）
  3) 原句：在题库（阅读 / 完形 / 新题型 / 翻译 全部题型）里找【含该词的短句】，优先 ≤115 字符；
     没有短句时截取以该词为中心的片段（对齐单词边界）。出处标注「年份 英语一/二 · 题型」。

词频 freq = 该词（精确词形变体）在题库全部真题句中的出现次数，用于排序（最常出现的排最前面）。

运行：python -X utf8 tools/build_wordnotes.py
"""
import csv
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'pwa', 'data')

SKIP_FILES = ['deck', 'index', 'chain', 'mindmap', 'freq', 'hard', 'phrases', 'dict', 'tc_', 'wordnotes']

TYPE_CN = {
    'text1': '阅读', 'text2': '阅读', 'text3': '阅读', 'text4': '阅读',
    'cloze': '完形', 'newtype': '新题型', 'translation': '翻译',
    'writing_a': '写作', 'writing_b': '写作',
}
SHORT_LIMIT = 115      # 短句阈值（字符）
SNIP_LIMIT = 100       # 截取片段目标长度


# ==================== 载入 ====================
def load_sentences():
    """题库全部真题句（en + cn + 年份 + 英一/英二 + 题型）"""
    out = []
    files = sorted(glob.glob(os.path.join(DATA_DIR, '*.json'))) + \
            sorted(glob.glob(os.path.join(DATA_DIR, 'en1', '*.json')))
    for p in files:
        base = os.path.basename(p)
        if any(k in base for k in SKIP_FILES):
            continue
        try:
            dd = json.load(open(p, encoding='utf-8'))
        except Exception:
            continue
        if not isinstance(dd, dict):
            continue
        is_en1 = 'en1' in p.replace('\\', '/')
        m = re.search(r'(\d{4})', base)
        year = m.group(1) if m else ''
        for a in dd.get('articles', []):
            if not isinstance(a, dict):
                continue
            tcn = TYPE_CN.get(a.get('type', ''), a.get('type', ''))
            for s in a.get('sentences', []) or []:
                en = s.get('en') or ''
                if not en:
                    continue
                out.append({
                    'en': re.sub(r'\s+', ' ', en).strip(),
                    'cn': re.sub(r'\s+', ' ', s.get('cn') or '').strip(),
                    'year': year,
                    'book': '英语一' if is_en1 else '英语二',
                    'type': tcn,
                })
    return out


def load_common(path):
    """ecdict 熟义（translation 首义）"""
    trans = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if w and w not in trans:
                trans[w] = (row.get('translation') or '').strip()
    return trans


# ==================== 文本处理 ====================
def clean_common(raw):
    """'n. 打击, 打, 冲撞, 讽刺\\nv. ...' → 'n. 打击；打'"""
    if not raw:
        return ''
    first = raw.split('\\n')[0].strip()
    m = re.match(r'^([a-z]+\.)\s*(.*)$', first, re.I)
    pos, body = (m.group(1), m.group(2)) if m else ('', first)
    items = [x.strip() for x in re.split(r'[,，;；]', body) if x.strip()][:2]
    return (pos + ' ' + '；'.join(items)).strip()


def clean_uncommon(raw):
    """僻义：去 OCR 序号（①②…）改用「；」连接，压缩空白"""
    if not raw:
        return ''
    t = re.sub(r'\s+', '', raw)
    t = re.sub(r'[\u2460-\u2473]', '；', t)
    t = t.replace('..', '.')
    return t.strip('；,，')


# 讲义分析 / 试题解析 / 结构切分特征 —— 译文命中即整条丢弃（全有或全无，避免残缺误导）
_CN_STRONG = [
    r'[\u2236]',                                    # ∶ 比例冒号（讲义专用）
    r'[\u2460-\u2473]',                             # ①②③ 圈数字
    r'结构切分|句子主干|主干\s*[:：]|拆句|句子成分',
    r'定语从句|状语从句|宾语从句|同位语|系动词|疑问代词|引导词|独立主格',
    r'谓语|主语|宾语|状语|表语|补语|定语',
    r'精准定位|定位到|本题|选项|题干|答案解析|技巧总结|考点|命题|第[一二三四五六七八九十]+段',
    r'篡改|排除|同义替换|无中生有|过度推断|答非所问|偷换概念',
    r'主旨|语篇|篇章|行文|段落大意|引出|继而',
    r'认准淘宝|淘宝|店铺|工作室|赠送|配套课程|考研',
]


def clean_cn(cn):
    """清洗译文：混入讲义分析/结构切分/解析文字的一律置空"""
    if not cn:
        return ''
    cn = re.sub(r'\s+', ' ', cn).strip()
    for pat in _CN_STRONG:
        if re.search(pat, cn):
            return ''
    for sig in ['记：', '【', '［', '（解析', '解析：', '本题考查']:
        i = cn.find(sig)
        if i >= 0:
            cn = cn[:i]
    cn = cn.strip(' ，,；;、')
    zh = len(re.findall(r'[\u4e00-\u9fff]', cn))
    if zh < 4 or zh / max(len(cn), 1) < 0.5:
        return ''
    return cn[:200]


# ==================== 词形与取句 ====================
def variants(w):
    """精确词形变体（词频统计用，避免 see 误配 seem）"""
    vs = {w}
    if w.endswith('e'):
        vs |= {w + 'd', w[:-1] + 'ing'}
    else:
        vs |= {w + 'ed', w + 'ing'}
    vs |= {w + 's', w + 'es', w + 'ness', w + 'ment', w + 'tion'}
    if w.endswith('y'):
        vs |= {w[:-1] + 'ies', w[:-1] + 'ied'}
    return vs


def word_re(w):
    """词族匹配（例句候选用）：词根（去尾 e）+ 至多 6 字母后缀"""
    stem = w[:-1] if w.endswith('e') else w
    return re.compile(r'\b' + re.escape(stem) + r"[a-z]{0,6}\b", re.I)


def freq_re(w):
    """词频统计正则：仅精确变体"""
    alts = '|'.join(re.escape(v) for v in sorted(variants(w), key=len, reverse=True))
    return re.compile(r'\b(?:' + alts + r')\b', re.I)


def snippet(en, w, limit=SNIP_LIMIT):
    """原句过长时截取以该词为中心的片段（在标点/空格边界断开，不切单词）"""
    m = word_re(w).search(en)
    if not m:
        return en if len(en) <= limit else en[:limit].strip() + ' …'
    start, end = m.start(), m.end()
    budget = max(limit - (end - start), 24)
    left, right = budget // 2, budget - budget // 2
    a = max(0, start - left)
    b = min(len(en), end + right)
    if a > 0 and en[a - 1].isalpha() and en[a].isalpha():
        sp = en.rfind(' ', 0, a)
        if sp > 0:
            a = sp + 1
    if b < len(en) and en[b - 1].isalpha() and en[b].isalpha():
        sp = en.find(' ', b)
        if sp > 0:
            b = sp
    frag = en[a:b].strip()
    if a > 0:
        cut = max(frag.rfind(', '), frag.rfind('; '), frag.rfind(': '))
        if 0 < cut < 40:
            frag = frag[cut + 2:]
        frag = '… ' + frag
    if b < len(en):
        cands = [x for x in [frag.find(', ', 10), frag.find('; ', 10)] if x > 0]
        cut = min(cands) if cands else len(frag)
        frag = frag[:cut].rstrip(' ,;') + ' …'
    return frag.strip()


# ==================== 主流程 ====================
def main():
    deck = json.load(open(os.path.join(DATA_DIR, 'deck_tc_senses.json'), encoding='utf-8'))
    sents = load_sentences()
    common_map = load_common(os.path.join(ROOT, 'tools', 'ecdict.csv'))
    print(f'题库句 {len(sents)} 条（阅读/完形/新题型/翻译），熟词僻义词条 {len(deck["words"])}')

    rows = []
    seen = set()
    stat = {'short': 0, 'snip': 0, 'fallback': 0, 'none': 0}
    for it in deck['words']:
        w = (it.get('word') or '').strip()
        if not w:
            continue
        wl = w.lower()
        if wl in seen:
            continue
        seen.add(wl)

        rx = word_re(wl)
        freq = sum(len(freq_re(wl).findall(s['en'])) for s in sents)

        cands = [s for s in sents if rx.search(s['en'])]
        # 指纹池：与讲义例句实词有交集的句子（更可能使用偏僻义）
        ex_raw = re.sub(r'\s+', ' ', it.get('example_en') or '').strip()
        fp_words = [x for x in re.findall(r"[A-Za-z][A-Za-z'-]{3,}", ex_raw.lower()) if x != wl]
        fingered = [s for s in cands if any(t in s['en'].lower() for t in fp_words)] if fp_words else []

        src = en = cn = ''
        pick = None
        # 取句优先级：① 带译文的短句(≤115) ② 带译文的稍长句(≤150) ③ 短句(无译文) ④ 截取
        for pool in (fingered, cands):
            for seg, lim, need_cn in ((pool, SHORT_LIMIT, True), (pool, 130, True), (pool, SHORT_LIMIT, False)):
                segs = [s for s in seg if len(s['en']) <= lim and (clean_cn(s['cn']) if need_cn else True)]
                if segs:
                    pick = min(segs, key=lambda s: len(s['en']))
                    break
            if pick:
                break
        if pick:
            en, cn = pick['en'], clean_cn(pick['cn'])
            src = f"{pick['year']} {pick['book']} · {pick['type']}" if pick['year'] else pick['type']
            stat['short'] += 1
        elif cands:
            pool2 = fingered or cands
            p2 = min(pool2, key=lambda s: len(s['en']))
            en = snippet(p2['en'], wl)
            src = (f"{p2['year']} {p2['book']} · {p2['type']}（截取）" if p2['year'] else f"{p2['type']}（截取）")
            stat['snip'] += 1
        else:
            if ex_raw:
                en = snippet(ex_raw, wl) if len(ex_raw) > SHORT_LIMIT else ex_raw
                cn = clean_cn(it.get('example_cn') or '')
                src = '讲义例证'
                stat['fallback'] += 1
            else:
                stat['none'] += 1

        rows.append({
            'w': w,
            'freq': freq,
            'common': clean_common(common_map.get(wl, '')),
            'uncommon': clean_uncommon(it.get('meaning') or ''),
            'en': en, 'cn': cn, 'src': src,
        })

    # —— 合并用户笔记源（大白英语笔记），同词优先覆盖 ——
    notes_path = os.path.join(DATA_DIR, 'wordnotes_notes.json')
    if os.path.exists(notes_path):
        notes = json.load(open(notes_path, encoding='utf-8'))
        idx = {r['w'].lower(): r for r in rows}
        n_add = n_ovr = 0
        for nr in notes.get('rows', []):
            w2 = (nr.get('word') or '').strip()
            if not w2:
                continue
            wl2 = w2.lower()
            tag = ('大白笔记 ' + (nr.get('year') or '')).strip()
            if wl2 in idx:
                row = idx[wl2]
                row['common'] = nr.get('common') or row['common']
                row['uncommon'] = nr.get('uncommon') or row['uncommon']
                if nr.get('en'):
                    row['en'] = nr['en']
                    row['cn'] = nr.get('cn', '')
                    row['src'] = tag
                n_ovr += 1
            else:
                rows.append({
                    'w': w2,
                    'freq': sum(len(freq_re(wl2).findall(s['en'])) for s in sents),
                    'common': nr.get('common', ''),
                    'uncommon': nr.get('uncommon', ''),
                    'en': nr.get('en', ''),
                    'cn': nr.get('cn', ''),
                    'src': tag,
                })
                n_add += 1
        print(f'合并大白笔记源：新增 {n_add} 条，覆盖 {n_ovr} 条')

    rows.sort(key=lambda r: (-r['freq'], r['w'].lower()))
    out = {'name': '熟词僻义', 'count': len(rows), 'rows': rows}
    dst = os.path.join(DATA_DIR, 'wordnotes.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    print(f'写入 {dst}｜{len(rows)} 条，按词频降序')
    print('短句', stat['short'], '｜截取片段', stat['snip'], '｜讲义例证', stat['fallback'], '｜无例句', stat['none'])

    # —— 长度检测报告 ——
    enl = sorted(len(r['en']) for r in rows)
    cnl = sorted(len(r['cn']) for r in rows if r['cn'])
    print(f"[长度检测] 原句 en：max {enl[-1]}｜中位 {enl[len(enl) // 2]}｜>115 字符 {sum(1 for x in enl if x > 115)} 条")
    print(f"[长度检测] 译文 cn：max {cnl[-1] if cnl else 0}｜中位 {cnl[len(cnl) // 2] if cnl else 0}｜空译文 {sum(1 for r in rows if not r['cn'])} 条")

    print('\nTop 10（词频降序）：')
    for r in rows[:10]:
        print(f"  {r['freq']:>3}  {r['w']:<12} {r['uncommon'][:12]:<14} {r['en'][:72]}")
    print('\n样例（用户点名）：')
    for r in rows:
        if r['w'] in ('term', 'build', 'handsome'):
            print(f"  {r['w']}: {r['en']}\n      译文: {r['cn'][:70] or '（无）'}  [{r['src']}]")


if __name__ == '__main__':
    main()
