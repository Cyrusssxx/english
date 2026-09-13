# -*- coding: utf-8 -*-
'''给 17 篇大作文「套用示范」做逐句标注，产出 pwa/data/writing_apply_marks.json：
  · spans   每句按「模板固定 / 可替换槽 / 非模板自写」切段的带标注文本
  · src     该句最接近的模板句（分区 · 模板第N句 / 功能句N）
  · ratio   相似度
  · keys    该句里出现的「关键句型」
  · cn      该句的中文译文（仅当该段中英句数相等时按序配对，避免错位）
  · wc      段落与全文词数（考研英语二要求 ≥150）
用法：python tools/annotate_writing_apply.py
'''
import difflib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
TPL_FP = os.path.join(DATA, 'writing_templates.json')
AP_FP = os.path.join(DATA, 'writing_apply.json')
OUT_FP = os.path.join(DATA, 'writing_apply_marks.json')

PH_RE = re.compile(r'\{\{(.+?)\}\}')
TOK_RE = re.compile(r"[A-Za-z0-9]+(?:[.'\u2019\-][A-Za-z0-9]+)*")
SENT_SPLIT_EN = re.compile(r'(?<=[.!?])\s+')
SENT_SPLIT_CN = re.compile(r'(?<=[\u3002\uff01\uff1f])')


def wc(text):
    return len([x for x in re.split(r'\s+', (text or '').strip()) if re.search(r'[A-Za-z0-9]', x)])


def en_sents(t):
    return [s.strip() for s in SENT_SPLIT_EN.split((t or '').replace('\n', ' ')) if s.strip()]


def cn_sents(t):
    return [s.strip() for s in SENT_SPLIT_CN.split(t or '') if s.strip()]


def paras(t):
    return [p.strip() for p in re.split(r'\n\s*\n', (t or '').strip()) if p.strip()]


def ref_tokens(text):
    '''模板句 → (token 列表, 占位符边界集合)。占位符被抽掉，边界处记录「此处原本是槽」。'''
    toks, holes = [], set()
    pos = 0
    for m in PH_RE.finditer(text):
        toks.extend(t.lower() for t in TOK_RE.findall(text[pos:m.start()]))
        holes.add(len(toks))          # 在 toks[b-1] 与 toks[b] 之间有一个 {{}}
        pos = m.end()
    toks.extend(t.lower() for t in TOK_RE.findall(text[pos:]))
    return toks, holes


def build_pool(tpl):
    '''参考池：所有模板正文句 / 功能句 / 负面版句 → (tokens, holes, 标签, 类型)'''
    pool = []
    for sec in tpl.get('sections', []):
        title = sec.get('title', sec.get('id', ''))
        for i, s in enumerate(en_sents(sec.get('en'))):
            toks, holes = ref_tokens(s)
            pool.append((toks, holes, '%s · 模板第%d句' % (title, i + 1), 'tpl'))
        for i, s in enumerate(sec.get('sentences', [])):
            toks, holes = ref_tokens(s.get('en', ''))
            pool.append((toks, holes, '%s · 功能句%d' % (title, i + 1), 'func'))
        for i, s in enumerate(en_sents(sec.get('negative_en'))):
            toks, holes = ref_tokens(s)
            pool.append((toks, holes, '%s · 负面版第%d句' % (title, i + 1), 'neg'))
    return [p for p in pool if p[0]]


def match_stats(sm):
    '''(匹配 token 数, 覆盖率 = 匹配数 / demo 句长)'''
    matched = sum(i2 - i1 for op, i1, i2, _, _ in sm.get_opcodes() if op == 'equal')
    return matched


def best_ref(demo_toks, pool):
    '''双阈值：
      · 匹配 token 数 ≥ 4                            —— 排除短句之间的偶发巧合
      · demo 覆盖率 ≥ 0.25                            —— 排除「只借了模板一个短零件」的假匹配
    排序用 demo 覆盖率（demo 句有多少比例来自模板），它越大说明越接近照抄。'''
    cands = []
    for toks, holes, label, kind in pool:
        if not toks:
            continue
        sm = difflib.SequenceMatcher(None, demo_toks, toks, autojunk=False)
        matched = match_stats(sm)
        ref_cov = matched / len(toks)
        if matched >= 4 and matched / max(len(demo_toks), 1) >= 0.25:
            cands.append((matched / max(len(demo_toks), 1), matched, ref_cov, holes, label, kind, sm))
    if not cands:
        return 0.0, 0, set(), '自写句（模板未覆盖）', 'own', 0, None
    cands.sort(key=lambda c: (-c[0], -c[1]))
    demo_cov, matched, ref_cov, holes, label, kind, sm = cands[0]
    return demo_cov, matched, holes, label, kind, len(sm.b), sm


# 图表类型词：模板规则明确「按图选词」，一律视为可替换槽
CHART_WORDS = {'bar', 'line', 'pie', 'table', 'column', 'chart', 'graph', 'figure'}
# 功能词：单独高亮没有意义，一律并回「模板固定」
STOPWORDS = {'a', 'an', 'the', 'and', 'or', 'of', 'in', 'on', 'to', 'from', 'with', 'by',
             'as', 'at', 'for', 'while', 'that', 'this', 'these', 'those', 'it', 'its',
             'is', 'are', 'was', 'were', 'be', 'been', 'their', 'they', 'we', 'our'}


def classify(demo_toks, ref, ref_holes, ref_len):
    '''返回每个 demo token 的类别：t 模板固定 / s 可替换槽 / o 非模板自写'''
    kinds = ['o'] * len(demo_toks)
    for op, i1, i2, j1, j2 in ref.get_opcodes():
        if op == 'equal':
            for i in range(i1, i2):
                kinds[i] = 't'
        else:  # insert / replace / delete：demo 侧动了词
            past_end = j1 >= ref_len          # 已经走出模板句尾
            in_hole = (j1 in ref_holes) or (j2 in ref_holes)
            k = 's' if (in_hole and not past_end) else 'o'
            for i in range(i1, i2):
                kinds[i] = k
    n = len(kinds)
    # 1) 图表类型词 → 槽位
    for i in range(n):
        if kinds[i] != 't' and demo_toks[i] in CHART_WORDS:
            kinds[i] = 's'
    # 2) 纯功能词的高亮片段 → 并回模板固定
    i = 0
    while i < n:
        if kinds[i] != 't':
            j = i
            while j < n and kinds[j] != 't':
                j += 1
            if all(demo_toks[k] in STOPWORDS for k in range(i, j)):
                for k in range(i, j):
                    kinds[k] = 't'
            i = j
        else:
            i += 1
    # 3) 孤立的高亮单 token（两侧都是模板）→ 并回模板，避免碎点
    for i in range(n):
        if kinds[i] != 't':
            l = kinds[i - 1] if i > 0 else 't'
            r = kinds[i + 1] if i + 1 < n else 't'
            if l == 't' and r == 't' and demo_toks[i] in STOPWORDS:
                kinds[i] = 't'
    return kinds


def spans_of(sent, kinds):
    '''把 token 类别映射回原句字符区间，合并成 spans'''
    spans = []
    idx = 0
    for m in TOK_RE.finditer(sent):
        if spans and spans[-1]['t'] == kinds[idx]:
            spans[-1]['x'] += sent[spans[-1]['_end']:m.start()] + m.group(0)
        else:
            if spans:
                spans[-1]['x'] += sent[spans[-1]['_end']:m.start()]
            spans.append({'t': kinds[idx], 'x': m.group(0), '_end': m.end()})
        spans[-1]['_end'] = m.end()
        idx += 1
    if spans:
        spans[-1]['x'] += sent[spans[-1]['_end']:]
        for s in spans:
            s.pop('_end', None)
    return [s for s in spans if s['x'].strip()] or [{'t': 'o', 'x': sent}]


def segs(pat):
    return [p.strip(' ,.;') for p in re.split(r'\u2026+', pat) if len(p.strip(' ,.;')) > 3]


def norm_apos(s):
    return (s or '').replace('’', "'").replace('‘', "'")


def key_hits(sent, keys):
    low = norm_apos(sent.lower())
    out = []
    for k in keys:
        ss = [norm_apos(x).lower() for x in segs(k)]
        if ss and all(x in low for x in ss):
            out.append(k)
        elif ss:
            longest = max(ss, key=len)
            if longest in low:
                out.append(k)
    return out


def main():
    tpl = json.load(open(TPL_FP, encoding='utf-8'))
    ap = json.load(open(AP_FP, encoding='utf-8'))
    pool = build_pool(tpl)
    print('参考池:', len(pool), '条模板句')

    out = {}
    stat = {'tpl': 0, 'func': 0, 'own': 0}
    for y in sorted(ap):
        v = ap[y]
        en_paras = paras(v['apply_en'])
        cn_paras = paras(v.get('apply_cn'))
        keys = [k['en'] for k in v.get('key_phrases', [])]
        rec = {'wc': wc(v['apply_en']), 'paras': []}
        for pi, para in enumerate(en_paras):
            sents = en_sents(para)
            cns = cn_sents(cn_paras[pi]) if pi < len(cn_paras) else []
            use_cn = len(cns) == len(sents)
            pre = {'wc': wc(para), 'sents': []}
            for si, s in enumerate(sents):
                toks = [t.lower() for t in TOK_RE.findall(s)]
                cov, matched, holes, label, kind, ref_len, sm = best_ref(toks, pool)
                if sm is None:
                    kinds = ['o'] * len(toks)
                    cov, matched = 0.0, 0
                else:
                    kinds = classify(toks, sm, holes, ref_len)
                stat[kind] = stat.get(kind, 0) + 1
                pre['sents'].append({
                    'spans': spans_of(s, kinds),
                    'src': label,
                    'kind': kind,
                    'cov': round(cov, 2),
                    'matched': matched,
                    'wc': len(toks),
                    'keys': key_hits(s, keys),
                    'cn': cns[si] if use_cn else '',
                })
            rec['paras'].append(pre)
        out[y] = rec

    json.dump(out, open(OUT_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入 writing_apply_marks.json')
    print('句来源分布:', stat)
    tot = {y: out[y]['wc'] for y in out}
    print('词数: 最低 %d | 最高 %d' % (min(tot.values()), max(tot.values())))
    print('低于 150 词的年份:', [y for y, n in tot.items() if n < 150] or '无')


if __name__ == '__main__':
    main()
