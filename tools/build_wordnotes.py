# -*- coding: utf-8 -*-
"""生成熟词僻义表格数据 pwa/data/wordnotes.json

数据来源（全部为已有资料，无 AI 生成）：
  1) 单词 + 僻义：pwa/data/deck_tc_senses.json（唐迟·熟词僻义，OCR + 人工核对）
  2) 熟义：tools/ecdict.csv 的 translation 首义（取前 2 个义项）
  3) 原句：优先用「僻义例句实词指纹」在题库真题句里定位到的完整原句（带年份 + 官方译文）；
     定位失败则退回 deck 的 example_en/example_cn（OCR 例句，标注为“例证句”）

输出结构：
  {"name": "熟词僻义", "years": [{"year": "2024", "rows": [{w, common, uncommon, en, cn, src}]}, ...]}
  "通用" 区收年份未定位的词条，排在最后。

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

STOP = set('''a an the of to in on at for with by from about as is are was were be been being do does did have has had
it its this that these those their them they we you he she his her our your not no and but so if then than
most more some any all both each other such which who when where why how what while because can could will would
should may might must into over under between among against during before after above through'''.split())

SKIP_FILES = ['deck', 'index', 'chain', 'mindmap', 'freq', 'hard', 'phrases', 'dict', 'tc_', 'wordnotes']


def load_sentences():
    """题库全部真题句（en + cn + 年份 + 英一/英二）"""
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
            for s in a.get('sentences', []) or []:
                en = s.get('en') or ''
                if not en:
                    continue
                out.append({
                    'en': re.sub(r'\s+', ' ', en).strip(),
                    'cn': re.sub(r'\s+', ' ', s.get('cn') or '').strip(),
                    'year': year,
                    'book': '英语一' if is_en1 else '英语二',
                    'aid': a.get('id', ''),
                })
    return out


def load_common(path):
    """ecdict 熟义（translation 首义，取前 2 个义项）"""
    trans = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            w = (row.get('word') or '').strip().lower()
            if w and w not in trans:
                trans[w] = (row.get('translation') or '').strip()
    return trans


def clean_common(raw):
    """'n. 打击, 打, 冲撞, 讽刺\\nv. ...' → 'n. 打击；打'"""
    if not raw:
        return ''
    first = raw.split('\\n')[0].strip()
    m = re.match(r'^([a-z]+\.)\s*(.*)$', first, re.I)
    pos, body = (m.group(1), m.group(2)) if m else ('', first)
    items = [x.strip() for x in re.split(r'[,，;；]', body) if x.strip()]
    items = items[:2]
    body = '；'.join(items)
    return (pos + ' ' + body).strip()


def clean_uncommon(raw):
    """去 OCR 序号（①②…）改用「；」连接，压缩空白"""
    if not raw:
        return ''
    t = re.sub(r'\s+', '', raw)
    t = re.sub(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫]', '；', t)
    t = t.replace('..', '.')
    return t.strip('；,，')


def variants(w):
    """常见词形变化"""
    vs = {w}
    if w.endswith('e'):
        vs |= {w + 'd', w[:-1] + 'ing'}
    else:
        vs |= {w + 'ed', w + 'ing'}
    vs |= {w + 's', w + 'es'}
    if w.endswith('y'):
        vs |= {w[:-1] + 'ies', w[:-1] + 'ied'}
    return vs


def content_words(text, exclude):
    ws = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", (text or '').lower())
    return [x for x in ws if x not in STOP and x != exclude]


def main():
    deck = json.load(open(os.path.join(DATA_DIR, 'deck_tc_senses.json'), encoding='utf-8'))
    sents = load_sentences()
    common_map = load_common(os.path.join(ROOT, 'tools', 'ecdict.csv'))
    print(f'题库句 {len(sents)} 条，熟词僻义词条 {len(deck["words"])}，ecdict 词条 {len(common_map)}')

    rows_by_year = {}
    seen = set()
    stat = {'located': 0, 'loose': 0, 'fallback': 0, 'no_example': 0, 'no_common': 0, 'dup': 0}
    for it in deck['words']:
        w = (it.get('word') or '').strip()
        if not w:
            continue
        wl = w.lower()
        if wl in seen:            # 同词去重，保留首次（来源更优）
            stat['dup'] += 1
            continue
        seen.add(wl)
        uncommon = clean_uncommon(it.get('meaning') or '')
        common = clean_common(common_map.get(wl, ''))
        if not common:
            stat['no_common'] += 1

        # 1) 指纹定位：含该词 + 例句实词命中最多者（较可能是僻义用法）
        ex = it.get('example_en') or ''
        target = content_words(ex, wl)
        best, best_score = None, 0
        for s in sents:
            low = s['en'].lower()
            if not re.search(r'\b' + re.escape(wl) + r"[a-z]{0,3}\b", low):
                continue
            score = sum(1 for t in target if t in low)
            if score > best_score:
                best_score, best = score, s
        if best and best_score >= 1:
            stat['located'] += 1
            year = best['year'] or '通用'
            src = f"{best['year']} {best['book']}" if best['year'] else ''
            en, cn = best['en'], best['cn']
        else:
            # 2) 宽松定位：只要求句中出现该词，取最短的完整真题句（避免长难句喧宾夺主）
            cands = [s for s in sents
                     if re.search(r'\b' + re.escape(wl) + r"[a-z]{0,3}\b", s['en'].lower())]
            if cands:
                cand = min(cands, key=lambda s: len(s['en']))
                stat['loose'] += 1
                year = cand['year'] or '通用'
                src = (f"{cand['year']} {cand['book']} · 真题句" if cand['year'] else '真题句')
                en, cn = cand['en'], cand['cn']
            else:
                # 3) 退回 OCR 例证句
                en = re.sub(r'\s+', ' ', ex).strip()
                cn = re.sub(r'\s+', ' ', it.get('example_cn') or '').strip()
                if not en:
                    stat['no_example'] += 1
                else:
                    stat['fallback'] += 1
                year = '通用'
                src = '例证句'
        rows_by_year.setdefault(year, []).append({
            'w': w, 'common': common, 'uncommon': uncommon,
            'en': en, 'cn': cn, 'src': src,
        })

    def ykey(y):
        return (1, '9999') if y == '通用' else (0, y)

    years = []
    for y in sorted(rows_by_year, key=ykey):
        rows = sorted(rows_by_year[y], key=lambda r: r['w'].lower())
        # 原句为空的排到本区末尾
        rows.sort(key=lambda r: (not r['en'], r['w'].lower()))
        years.append({'year': y, 'rows': rows})

    out = {'name': '熟词僻义', 'count': sum(len(v['rows']) for v in years), 'years': years}
    dst = os.path.join(DATA_DIR, 'wordnotes.json')
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'写入 {dst}')
    print(f"分区 {len(years)} 个，共 {out['count']} 条")
    print('指纹定位', stat['located'], '｜宽松定位', stat['loose'], '｜退回例证句', stat['fallback'], '｜无例句', stat['no_example'], '｜无熟义', stat['no_common'], '｜重复去重', stat['dup'])
    print('\n样例：')
    for y in years[:2] + years[-1:]:
        print(f"== {y['year']} ({len(y['rows'])}) ==")
        for r in y['rows'][:3]:
            print(f"  {r['w']} | 熟:{r['common']} | 僻:{r['uncommon']} | {r['src']} | {r['en'][:70]}")


if __name__ == '__main__':
    main()
