# -*- coding: utf-8 -*-
'''把 17 篇大作文「套用示范」改成「全模板填空」：每篇由模板句子拼成，只填 {{}} 槽位。

规则
  · 一句话都没自写：P1 取 chart_static / chart_dynamic 的模板句或功能句，P2 取 para2_* 的句子，
    P3 取 para3_positive / para3_negative 的句子。
  · 唯一的例外是 chart_dynamic 首句的走势短语（同向上升／单线上升的年份写「并未朝同一方向变化」会与事实相反），
    用 `trend` 覆盖它——这部分会被标注器正确地标为「自写/改写」。
  · 词数按考研口径（含字母的空白串算 1 个，纯数字不计，连字符算 1），目标 165-180。

产出
  · 写回 pwa/data/writing_apply.json 的 apply_en / apply_cn
  · 重新生成 key_phrases（=本篇用到的模板句型）与 slot_phrases（=本篇填槽的题相关表达）
用法：python tools/build_apply_from_templates.py
'''
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
TPL_FP = os.path.join(DATA, 'writing_templates.json')
AP_FP = os.path.join(DATA, 'writing_apply.json')

PH = re.compile(r'\{\{(.+?)\}\}')
NL2 = chr(10) + chr(10)          # 段落分隔（避免在本文件里写裸反斜杠 n）
EN_S = re.compile(r'(?<=[.!?])\s+')
CN_S = re.compile(r'(?<=[\u3002\uff01\uff1f])')


def en_sents(t):
    return [s.strip() for s in EN_S.split((t or '').replace('\n', ' ')) if s.strip()]


def cn_sents(t):
    return [s.strip() for s in CN_S.split(t or '') if s.strip()]


def wc(t):
    '''考研口径：纯数字/百分比不计，其余按空白切分（连字符词算 1 个）'''
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z]', x)])


def load_templates():
    d = json.load(open(TPL_FP, encoding='utf-8'))
    out = {}
    for sec in d['sections']:
        out[sec['id']] = {
            'title': sec.get('title', sec['id']),
            'en': en_sents(sec.get('en')),
            'cn': cn_sents(sec.get('cn')),
            'fen': en_sents(sec.get('negative_en')),
            'fcn': cn_sents(sec.get('negative_cn')),
            'fn': [x['en'] for x in sec.get('sentences', [])],
            'fcn_items': [x.get('cn', '') for x in sec.get('sentences', [])],
            # 走势变体（chart_dynamic）：按年份选一套，再由 main 覆盖 en/cn
            'skel': [{'label': v.get('label', ''), 'years': v.get('years', ''),
                      'en': en_sents(v.get('en')), 'cn': cn_sents(v.get('cn'))}
                     for v in (sec.get('skeletons') or [])],
        }
    return out


def apply_skeleton(TPL, sid, year):
    """把该 section 的 en/cn 换成「这一年该用的那套走势骨架」"""
    tp = TPL.get(sid)
    if not tp or not tp.get('skel'):
        return None
    for i, sk in enumerate(tp['skel']):
        if year and year in sk['years']:
            TPL[sid] = dict(tp, en=sk['en'], cn=sk['cn'])
            return i
    return None


ALIAS = {'xx': 'chart', '图表': 'chart'}

# 主谓一致：只有「复数槽位值」**正后方紧跟**的谓语才需要改（v2 曾产出 "brands has moved" / "features takes"）
PL_LEAD = [('has', 'have'), ('is', 'are'), ('serves', 'serve'), ('takes', 'take'), ('comes', 'come'),
           ('breaks', 'break'), ('rounds', 'round'), ('matters', 'matter'), ('points', 'point'),
           ('teaches', 'teach'), ('brings', 'bring'), ('reaches', 'reach'), ('matters', 'matter'),
           ('goes', 'go'), ('account for', 'account for'), ('accounts for', 'account for')]
PL_ADV = r'(?:(?:now|also|still|only|usually|often|alone)\s+)?'
# 少数句子里代词也指代主题（仅此两处模板）
PL_PHR = [('so that it reaches', 'so that they reach'),
          ('instead of treating it as an extra', 'instead of treating them as an extra')]


def finalize(s, slots, pl_values):
    """① 表格图别写成 "table chart"；② 复数槽位值后紧跟的谓语改复数（别的谓语一律不动）"""
    s = s.replace('table chart', 'table')
    for k, v in slots.items():
        if not v or v not in (pl_values or []):
            continue
        i = s.lower().find(v.lower())        # 句首槽位会被 fill() 首字母大写，必须大小写不敏感定位
        if i < 0:
            continue
        head, tail = s[:i + len(v)], s[i + len(v):]
        for a, b in PL_LEAD:
            tail = re.sub(r'^(\s+' + PL_ADV + r')' + re.escape(a) + r'\b',
                          lambda m: m.group(1) + b, tail)
        for a, b in PL_PHR:
            tail = tail.replace(a, b)
        s = head + tail
    return s



CJK = r'一-鿿　-〿＀-￯'


def tighten_cn(s):
    '''中文里「字 词 字」之间的空格是模板为排版留的，去掉'''
    s = re.sub(r'(?<=[' + CJK + r'])\s+(?=[' + CJK + r'])', '', s)
    s = re.sub(r'\s+(?=[' + CJK + r'])', '', s)
    s = re.sub(r'(?<=[' + CJK + r'])\s+', '', s)
    return re.sub(r'\s+', ' ', s).strip()


def fill(text, slots, strict=True):
    def rep(m):
        k = m.group(1).strip()
        v = slots.get(k)
        if v is None and k in ALIAS:
            v = slots.get(ALIAS[k])
        if v is not None:
            # 槽位落在句首时首字母大写（如 "taking walks and …" → "Taking walks and …"）
            return v[0].upper() + v[1:] if m.start() == 0 and v else v
        if strict:
            raise KeyError('缺槽位 %s' % k)
        return m.group(0)
    return re.sub(r'\s+', ' ', PH.sub(rep, text)).strip()


def pick(tpl, refs, slots, side):
    '''refs: ('t', n) 模板句 / ('f', n) 功能句 / ('n', n) 负面版句'''
    out = []
    for kind, n in refs:
        if kind == 't':
            s = tpl['en'][n - 1] if side == 'en' else tpl['cn'][n - 1]
        elif kind == 'n':
            s = tpl['fen'][n - 1] if side == 'en' else tpl['fcn'][n - 1]
        else:
            s = tpl['fn'][n - 1] if side == 'en' else (tpl['fcn_items'][n - 1] or tpl['fn'][n - 1])
        out.append(fill(s, slots))
    return out


def build_year(y, spec, TPL):
    paras_en, paras_cn = [], []
    used_tpl, used_slot = [], []
    pl_all = spec.get('pl') or []
    for pkey in ('p1', 'p2', 'p3'):
        pid, refs = spec[pkey][0], spec[pkey][1]
        slots = spec.get('slots_' + pkey, {})
        slots_cn = spec.get('slots_' + pkey + '_cn') or slots
        tpl = TPL[pid]
        en = [finalize(x, slots, pl_all) for x in pick(tpl, refs, slots, 'en')]
        cn = [tighten_cn(x) for x in pick(tpl, refs, slots_cn, 'cn')]
        if pkey == 'p1' and slots.get('chart'):
            cw = slots['chart']
            en = [s.replace('line chart', cw + ' chart') for s in en]
            cn = [s.replace('折线图', slots_cn.get('chart', cw) + '图') for s in cn]
        if slots.get('chart') == 'table':                     # 表格图：英文 "table chart" → "table"
            cn = [s.replace('表格图', '表格') for s in cn]
        if spec.get('trend') and pkey == 'p1':
            en = [s.replace('did not move in a uniform direction', spec['trend']) for s in en]
            cn = [s.replace('并未朝着相同方向变化', spec.get('trend_cn', '')) for s in cn]
        paras_en.append(' '.join(en))
        paras_cn.append(''.join(cn))
        used_tpl.append((pid, refs))
        for k in sorted(slots):
            if slots[k]:
                used_slot.append({'para': pkey, 'name': k, 'en': slots[k],
                                  'cn': slots_cn.get(k, '')})
    return '\n\n'.join(paras_en), '\n\n'.join(paras_cn), used_tpl, used_slot


def auto_compose(y, sp, TPL):
    '''每个段落从「候选句列表」里挑一个**按原顺序的递增子集**，让全文词数落进 165-180（目标 172）'''
    import itertools
    cand = {}
    for pkey in ('p1', 'p2', 'p3'):
        cand[pkey] = [tuple(x) for x in sp[pkey][1]]
    def subsets(refs):
        out = []
        for k in range(2, min(6, len(refs)) + 1):   # 上限 6：让「骨架 3 句 + 句池 2 句」这类组合能被搜到
            for c in itertools.combinations(range(len(refs)), k):
                out.append([refs[i] for i in c])   # combinations 天然保序
        return out or [list(refs)]
    opts = {k: subsets(v) for k, v in cand.items()}
    must = [tuple(x) for x in sp.get('p1_must', [['t', 1], ['t', 2]])]
    opts['p1'] = [c for c in opts['p1'] if all(m in [tuple(x) for x in c] for m in must)]
    if not opts['p1']:
        raise SystemExit('%s 的 P1 必选句无法满足' % y)
    best = None
    for c1 in opts['p1']:
        for c2 in opts['p2']:
            for c3 in opts['p3']:
                trial = dict(sp)
                trial['p1'] = [sp['p1'][0], c1]
                trial['p2'] = [sp['p2'][0], c2]
                trial['p3'] = [sp['p3'][0], c3]
                try:
                    en, cn, ut, us = build_year(y, trial, TPL)
                except KeyError:
                    continue
                pw = [wc(x) for x in en.split(NL2)]
                # 分段配额：三段均衡，避免出现「28 词的图表段 / 100 词的归因段」
                if not (38 <= pw[0] <= 70 and 54 <= pw[1] <= 84 and 40 <= pw[2] <= 66):
                    continue
                n = wc(en)
                gaps = 0
                for pk, cc in zip(('p1', 'p2', 'p3'), (c1, c2, c3)):
                    idx = [cand[pk].index(tuple(x)) for x in cc]
                    if idx:
                        gaps += (idx[-1] - idx[0] + 1) - len(idx)
                score = (abs(n - 172) + abs(pw[0] - 56) * 0.3 + abs(pw[1] - 68) * 0.3
                         + abs(pw[2] - 52) * 0.3 + gaps * 1.5)
                if 165 <= n <= 181 and (best is None or score < best[0]):
                    best = (score, n, [c1, c2, c3], pw)
    if best is None:
        near = []
        for c1 in opts['p1']:
            for c2 in opts['p2']:
                for c3 in opts['p3']:
                    trial = dict(sp)
                    trial['p1'] = [sp['p1'][0], c1]
                    trial['p2'] = [sp['p2'][0], c2]
                    trial['p3'] = [sp['p3'][0], c3]
                    try:
                        en2, _, _, _ = build_year(y, trial, TPL)
                    except KeyError:
                        continue
                    pw2 = [wc(x) for x in en2.split(NL2)]
                    near.append((wc(en2), pw2, c1, c2, c3))
        near.sort(key=lambda z: abs(z[0] - 172))
        print('✘ %s 无解，最接近的 5 组：' % y)
        for n, pw, a, b, c in near[:5]:
            print('   %3d 词 段%s  %s | %s | %s' % (n, pw, a, b, c))
        raise SystemExit(1)
    c1, c2, c3 = best[2]
    sp['p1'] = [sp['p1'][0], c1]
    sp['p2'] = [sp['p2'][0], c2]
    sp['p3'] = [sp['p3'][0], c3]
    return build_year(y, sp, TPL)


def main():
    TPL = load_templates()
    spec = json.load(open(os.path.join(ROOT, 'tools', 'apply_tpl_spec.json'), encoding='utf-8'))
    plan_fp = os.path.join(ROOT, 'tools', 'apply_plan.json')
    if os.path.exists(plan_fp):
        spec = json.load(open(plan_fp, encoding='utf-8'))   # 人工挑句组（apply_plan.py 生成）
        print('用人工方案 apply_plan.json（%d 年）' % len(spec))
    data = json.load(open(AP_FP, encoding='utf-8'))
    print('%-6s %-5s %s' % ('年份', '词数', '各段词数'))
    bad = []
    for y in sorted(spec):
        sp = dict(spec[y])
        apply_skeleton(TPL, sp['p1'][0], y)      # 动态图：先定这一年用哪套走势骨架
        if sp.get('fixed'):
            en, cn, used_tpl, used_slot = build_year(y, sp, TPL)   # 直接用人工挑的句组，不做组合搜索
        else:
            en, cn, used_tpl, used_slot = auto_compose(y, sp, TPL)
        data[y]['apply_en'] = en
        data[y]['apply_cn'] = cn
        data[y]['tpl_used'] = [{'id': a, 'refs': [list(r) for r in b]} for a, b in used_tpl]
        data[y]['slot_used'] = used_slot
        # —— 两组关键内容：① 模板句型（本篇真正用到的模板句）② 填槽表达（本篇要填的题相关词）——
        kp, seen = [], set()
        PART = {'p1': '第一段', 'p2': '第二段', 'p3': '第三段'}
        for pid, refs in used_tpl:
            tp = TPL[pid]
            for kind, n in refs:
                if kind == 't':
                    pe, pc = tp['en'][n - 1], tp['cn'][n - 1]
                    label = '%s · 模板第%d句' % (tp['title'], n)
                elif kind == 'n':
                    pe, pc = tp['fen'][n - 1], tp['fcn'][n - 1]
                    label = '%s · 负面版第%d句' % (tp['title'], n)
                else:
                    pe = tp['fn'][n - 1]
                    pc = tp['fcn_items'][n - 1] or tp['fn'][n - 1]
                    label = '%s · 功能句%d' % (tp['title'], n)
                if pe in seen:
                    continue
                seen.add(pe)
                kp.append({'en': pe, 'cn': pc, 'src': label})
        data[y]['key_phrases'] = kp
        data[y]['slot_phrases'] = [{'name': s['name'], 'en': s['en'], 'cn': s['cn'],
                                    'para': PART.get(s['para'], s['para'])} for s in used_slot]
        n = wc(en)
        pw = [wc(p) for p in en.split('\n\n')]
        flag = '' if 165 <= n <= 180 else '  ★'
        if flag:
            bad.append((y, n))
        print('%-6s %-5d %s%s' % (y, n, ' / '.join(map(str, pw)), flag))
    json.dump(data, open(AP_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    ns = [wc(data[y]['apply_en']) for y in spec]
    print('%d 篇，词数 %d-%d，均值 %.1f，区间外 %s' % (len(spec), min(ns), max(ns), sum(ns) / len(ns), bad or '无'))


if __name__ == '__main__':
    main()
