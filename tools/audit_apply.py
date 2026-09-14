# -*- coding: utf-8 -*-
'''17 篇真题套用示范的严格体检（把 v2 暴露过的硬伤全部写成断言）。

v2 的问题都是「机器选句 + 槽位填文字」造成的，这里逐项拦：
  ① 词数 150~180（考研口径）
  ② 每篇第一段必须有 ≥3 个真实数字（图表作文最核心的「数据准确」）
  ③ 「rose from X to Y」必须 X<Y；「fell from X to Y」必须 X>Y（防「跌了却变大」）
  ④ 同一数字不在同一段重复 3 次以上（防「of the total of the total」式堆砌）
  ⑤ 无讲义腔黑名单、无 "table chart"、无 "was risen"
  ⑥ 主谓一致抽查（以 s 结尾的名词 + 单数谓语）
  ⑦ 极性：`para3_negative` 只用在负面题（2012 员工满意度）
  ⑧ 图型一致：静态图的年份不许出现「trend / rose from … to …」式时间表述

用法：python tools/audit_apply.py     （退出码非 0 = 有硬伤）
'''
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = os.path.join(ROOT, 'pwa', 'data', 'writing_apply.json')
TPL = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')

BANNED = ['did not move in a uniform direction', 'during the periods presented',
          'solid material foundation', 'no coincidence but', 'concerted efforts',
          'well-informed', 'one-way delivery', 'items associated with', 'table chart',
          'was risen', 'were risen', 'more higher', 'amount of people', 'of the total of the total']
NUM = re.compile(r'\b(\d[\d,]*(?:\.\d+)?)\s*(%|percent|billion|million|pieces)?')
SR = re.compile(r'\b(rose|climbed|grew|increased|doubled|surged)\s+from\s+([\d.,]+)(?:\s*\w+)?\s+to\s+([\d.,]+)')
SF = re.compile(r'\b(fell|declined|dropped|decreased)\s+from\s+([\d.,]+)(?:\s*\w+)?\s+to\s+([\d.,]+)')
SV = re.compile(r"\b([A-Za-z][A-Za-z'’-]*(?:s|es))\s+(?:now\s+|also\s+)?(has|is|serves|takes|comes|teaches|brings|reaches|goes)\b")
SV_WHITE = {'this', 'is', 'was', 'his', 'its', 'as', 'us', 'does', 'has', 'news', 'always',
            'perhaps', 'sometimes', 'means', 'series', 'business', 'who', 'categories', 'figures'}


def wc(t):
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z]', x)])


def num(s):
    return float(s.replace(',', ''))


def main():
    ap = json.load(io.open(AP, encoding='utf-8'))
    tpl = json.load(io.open(TPL, encoding='utf-8'))
    guide = {r['year']: r for r in tpl['chart_guide']['table']}
    bad = []

    for y in sorted(ap):
        a = ap[y]
        en = a.get('apply_en') or ''
        paras = [p.strip() for p in en.split('\n\n') if p.strip()]
        n = wc(en)

        # ① 词数
        if not 150 <= n <= 180:
            bad.append('%s 词数 %d 不在 150~180' % (y, n))

        # ② 第一段数字数（单线图只有一条线，首末值即可 → 门槛 2）
        figs = NUM.findall(paras[0]) if paras else []
        need = 2 if str(guide.get(y, {}).get('items')) == '1' else 3
        if len(figs) < need:
            bad.append('%s 第一段只有 %d 个数字（要求 ≥%d）' % (y, len(figs), need))

        # ③ 方向自洽
        for m in SR.finditer(en):
            if num(m.group(3)) <= num(m.group(2)):
                bad.append('%s 「%s」数值未上升：%s → %s' % (y, m.group(1), m.group(2), m.group(3)))
        for m in SF.finditer(en):
            if num(m.group(3)) >= num(m.group(2)):
                bad.append('%s 「%s」数值未下降：%s → %s' % (y, m.group(1), m.group(2), m.group(3)))

        # ④ 数字重复
        for pi, p in enumerate(paras):
            cnt = {}
            for v, _u in NUM.findall(p):
                cnt[v] = cnt.get(v, 0) + 1
            for v, c in cnt.items():
                if c >= 4:        # 饼图多类别数值相同是真实情况（2015 三个 20%），只拦堆砌式重复
                    bad.append('%s 第%d段数字 %s 出现 %d 次' % (y, pi + 1, v, c))

        # ⑤ 黑名单
        low = en.lower()
        for b in BANNED:
            if b.lower() in low:
                bad.append('%s 含禁用表达：%s' % (y, b))

        # ⑥ 主谓一致抽查
        for m in SV.finditer(en):
            if m.group(1).lower() in SV_WHITE:
                continue
            prev = en[max(0, m.start() - 45):m.end()]
            bad.append('%s 疑似主谓不一致：…%s…' % (y, prev.replace('\n', ' ')))

        # ⑦ 极性
        pol = a.get('tpl_used') and [x for x in a['tpl_used'] if x['id'].startswith('para3')]
        if pol and pol[0]['id'] == 'para3_negative' and y != '2012':
            bad.append('%s 用了负面第三段，但不是负面题' % y)

        # ⑧ 图型一致
        if guide.get(y, {}).get('type') == '静态' and re.search(r'\b(rose|fell|climbed)\s+from\b', en):
            bad.append('%s 是静态图，却出现「rose/fell from … to …」' % y)

    print('审计 17 篇：%s' % ('全部通过 ✅' if not bad else '%d 处问题 ❌' % len(bad)))
    for b in bad:
        print('  ✗ %s' % b)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
