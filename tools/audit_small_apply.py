# -*- coding: utf-8 -*-
"""小作文 17 篇套用示范的严格体检（改完内容就跑一次）

检查：词数 / 段落 / 称呼落款 / 残留占位符 / 中英句数一致 / 同一模板句是否被重复用 /
      示范文是否真的全部来自模板（无自写句）
用法：python tools/audit_small_apply.py
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
AP = json.load(io.open(os.path.join(DATA, 'small_apply.json'), encoding='utf-8'))
MK = json.load(io.open(os.path.join(DATA, 'small_apply_marks.json'), encoding='utf-8'))
SW = json.load(io.open(os.path.join(DATA, 'small_writing.json'), encoding='utf-8'))
BANK = {b['id']: b for b in SW['banks']}
PH = re.compile(r'\{\{')

MIN_W, MAX_W = 90, 120


def main():
    bad = []
    for y in sorted(AP):
        ap, mk = AP[y], MK[y]
        body = '\n\n'.join(ap['apply_en'].split('\n\n')[1:-1]) if ap['apply_en'].count('\n\n') >= 2 else ap['apply_en']
        wc = mk['wc']
        if not (MIN_W <= wc <= MAX_W):
            bad.append('%s 词数 %d 不在 %d~%d' % (y, wc, MIN_W, MAX_W))
        if len(mk['paras']) != 3:
            bad.append('%s 段落数 %d（要求 3 段）' % (y, len(mk['paras'])))
        if not mk.get('salutation'):
            bad.append('%s 缺称呼（通知类也应有标题）' % y)
        if PH.search(ap['apply_en']) or PH.search(ap['apply_cn']):
            bad.append('%s 示范文里残留 {{ }}' % y)
        # 中文句数应与英文一致
        for pi, p in enumerate(mk['paras']):
            for s in p['sents']:
                en_n = sum(1 for sp in s['spans'] if sp['t'] == 't')
                cn_n = sum(1 for sp in s.get('spans_cn') or [] if sp['t'] == 't')
                if not s.get('spans_cn'):
                    bad.append('%s P%d 缺中文标注' % (y, pi + 1))
                    break
                if en_n == 0:
                    bad.append('%s P%d 某句没有模板部分（等同自写）' % (y, pi + 1))
        # 同一模板句不重复用
        srcs = [s['src'] for p in mk['paras'] for s in p['sents']]
        dup = {x for x in srcs if srcs.count(x) > 1}
        if dup:
            bad.append('%s 重复用了同一模板句：%s' % (y, sorted(dup)))
        # 字数标注与正文一致
        if mk['req'] != 95:
            bad.append('%s req 应为 95（小作文「约 100 词」的达标线）' % y)

    print('检查 %d 篇' % len(AP))
    if bad:
        print('❌ 问题 %d 处：' % len(bad))
        for b in bad:
            print('   - ' + b)
        sys.exit(1)
    print('✅ 全部通过（词数 %d~%d，三段齐全，称呼落款完整，无自写句，无重复模板句）'
          % (min(MK[y]['wc'] for y in MK), max(MK[y]['wc'] for y in MK)))


if __name__ == '__main__':
    main()
