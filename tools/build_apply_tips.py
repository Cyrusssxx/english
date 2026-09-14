# -*- coding: utf-8 -*-
'''按「实际用到的句组」重生成 17 篇的「套用要点」（tips）。

为什么自动生成：手动写的要点会随模板改版而飘（出现过要点还在教 `did not move in a uniform direction`
这种已被删掉的句式）。这里全部从 `apply_plan.py`（人工方案）+ `writing_templates.json` + `chart_guide`
推导，改模板后重跑即同步。

产出：写回 pwa/data/writing_apply.json 的 tips 字段（每篇 4 条）
用法：python tools/build_apply_tips.py
'''
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import apply_plan as P                                       # noqa: E402

TPL_FP = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')
AP_FP = os.path.join(ROOT, 'pwa', 'data', 'writing_apply.json')

CHART_CN = {'bar': '柱状图', 'pie': '饼图', 'line': '折线图', 'table': '表格'}
POL_CN = {'para3_positive': ('正面版', '继续向好'), 'para3_negative': ('负面版', '问题可能恶化')}


def load(fp):
    return json.load(io.open(fp, encoding='utf-8'))


def sec(tpl, sid):
    return [s for s in tpl['sections'] if s['id'] == sid][0]


def skeleton_of(sec_d, year):
    for i, sk in enumerate(sec_d.get('skeletons') or []):
        if year in (sk.get('years') or ''):
            return i + 1, sk
    return None, None


def figures(s):
    """从槽位里挑出「数值型」键，按 item/num 成对 -> '主题 初值 → 终值'"""
    pairs = []
    for i in range(1, 7):
        it, a, b = s.get('item%d' % i), s.get('num%d' % (2 * i - 1)), s.get('num%d' % (2 * i))
        if it and a and b:
            pairs.append('%s %s → %s' % (it, a, b))
    for i in range(1, 6):
        it, pc = s.get('item%d' % i), s.get('percent%d' % i)
        if it and pc:
            pairs.append('%s 占 %s' % (it, pc))
    return pairs


def main():
    tpl = load(TPL_FP)
    ap = load(AP_FP)
    guide = {r['year']: r for r in tpl['chart_guide']['table']}
    n = 0
    for y in sorted(ap):
        if y not in P.CHART:
            continue
        c = P.CHART[y]
        g = guide.get(y, {})
        pol = 'negative' if c['p3'][0] == 'para3_negative' else 'positive'
        p2 = sec(tpl, c['p2'][0])
        p3 = sec(tpl, c['p3'][0])
        pool2 = [x['en'] for x in (p2.get('sentences') or [])]
        tags2 = [x.get('tag', '') for x in (p2.get('sentences') or [])]
        pool3 = [x['en'] for x in (p3.get('sentences') or [])]
        tags3 = [x.get('tag', '') for x in (p3.get('sentences') or [])]

        def picked(sec_d, refs_txt):
            """本条按 refs 实际用到的句池标签 / 句子（refs_txt 形如 't1 t2 f4'）"""
            tg, sents = [], []
            for m in re.findall(r'([tf])(\d+)', refs_txt):
                kind, ref = m[0], int(m[1])
                if kind == 'f':
                    tg.append((sec_d['sentences'][ref - 1].get('tag') or '').strip())
                    sents.append(sec_d['sentences'][ref - 1]['en'])
            return tg, sents

        # ① 图型 + 走势 + 骨架
        t1 = '%s、%s（%s 个事物 / %s）→ ' % (CHART_CN.get(c['ch'], c['ch']), g.get('trend', ''), g.get('items', '?'), g.get('type', ''))
        if c['p1'][0] == 'chart_dynamic':
            idx, sk = skeleton_of(sec(tpl, 'chart_dynamic'), y)
            t1 += '用 **%s 骨架**（适用 %s）。' % (sk['label'], sk['years'])
        else:
            t1 += '用**静态骨架**（各类别占比，没有时间变化）。'
        if c['multi']:
            t1 += '注意这是**多选题**，各项占比之和 > 100%，**不能用「合计」类句子**。'

        # ② 数据要点
        figs = figures(c['s'])
        t2 = '数据要点：' + '；'.join(figs[:4]) + '。'
        if c['multi']:
            t2 += '数值与图逐个核对，别漏最大值。'
        else:
            t2 += '只需要首末值 + 极值，不必逐年罗列；单位统一。'

        # ③ 第二段
        tg2, _ = picked(p2, c['p2'][1])
        tg2 = [x for x in tg2 if x]
        paras = (ap[y].get('apply_en') or '').split('\n\n')
        nsk2 = len([x for x in (sec(tpl, c['p2'][0]).get('en') or '').split('. ') if x.strip()])
        t3 = '第二段套 **%s**：句池挑「%s」；本段骨架 %d 句 + 句池 %d 句 ≈ %s 词。' % (
            p2.get('title', ''), '」「'.join(tg2[:3]), nsk2, len(tg2),
            (str(len(paras[1].split())) if len(paras) > 1 else '?'))

        # ④ 第三段
        polcn, tone = POL_CN[c['p3'][0]]
        tg3, _ = picked(p3, c['p3'][1])
        t4 = '第三段用 **%s**（%s）：主体 = %s；**只挑 2 个主体**，不要六个都写。' % (
            polcn, tone, ' + '.join([x for x in tg3 if x][:3]) or '按题挑主体')
        ap[y]['tips'] = [t1, t2, t3, t4]
        n += 1
    json.dump(ap, io.open(AP_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('已重写 %d 篇 tips' % n)
    for y in ('2010', '2015', '2023'):
        print('\n【%s】' % y)
        for t in ap[y]['tips']:
            print('  -', t)


if __name__ == '__main__':
    main()
