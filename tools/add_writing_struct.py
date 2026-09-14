# -*- coding: utf-8 -*-
"""作文模板结构标注 / 精句的「校验」脚本。

数据源说明（2026-09-15 起）
    结构标注（en_struct / negative_struct）与精句（phrases）**唯一来源是
    `pwa/data/writing_templates.json` 本身**（由作者或合并脚本写入）。
    本脚本只做校验与体检输出，**不再自带一份字典** —— 之前「脚本自带 S/P 字典」
    的写法是双数据源：改完模板忘记同步就会 KeyError / 句数对不上（已踩过两次）。

校验内容
    1) 每段骨架 en_struct 片段拼接必须与原句完全一致（否则主干高亮会错位）
    2) 句数与标注数必须一致
    3) skeletons（动态第一段 3 套走势骨架）、negative_struct 同样校验
    4) 词数体检：单句片段 ≤22 词、每段骨架 ≤45 词、句池单句 ≤22 词
用法：python tools/add_writing_struct.py
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FP = 'pwa/data/writing_templates.json'


def split_en(t):
    parts = re.findall(r'[^.!?]+[.!?]+["\')\]]*\s*|[^.!?]+$', t or '')
    return [p.strip() for p in parts if p.strip()]


def words(t):
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z0-9]', x)])


def check(tag, sents, structs):
    """片段拼接必须与原句完全一致"""
    assert structs, tag + ' 缺结构标注'
    assert len(sents) == len(structs), '%s: 句数 %d != 标注 %d' % (tag, len(sents), len(structs))
    out = []
    for i, (s, st) in enumerate(zip(sents, structs)):
        frags = []
        for x in st:
            x = [x, ''] if isinstance(x, str) else (x + [''] if len(x) == 1 else x)
            frags.append(x)
        cat = ''.join(x[0] for x in frags)
        assert cat == s, '%s S%d 拼接不一致:\n  原句: %r\n  拼接: %r' % (tag, i + 1, s, cat)
        for x in frags:
            assert words(x[0]) <= 22, '%s S%d 片段过长(%d 词): %s' % (tag, i + 1, words(x[0]), x[0])
        out.append(frags)
    return out


def main():
    d = json.load(open(FP, encoding='utf-8'))
    n_skel = n_neg = 0
    problems = []
    for sec in d['sections']:
        sid = sec['id']
        ss = split_en(sec['en'])
        check(sid, ss, sec.get('en_struct'))
        if words(sec['en']) > 45:
            problems.append('%s 骨架 %d 词 > 45' % (sid, words(sec['en'])))
        n_skel += len(ss)
        for k, v in enumerate(sec.get('skeletons') or []):
            vs = split_en(v['en'])
            check('%s/skel%d(%s)' % (sid, k + 1, v.get('label', '')), vs, v.get('struct'))
            n_skel += len(vs)
        if sec.get('negative_en'):
            check(sid + '_neg', split_en(sec['negative_en']), sec.get('negative_struct'))
            n_neg += 1
        assert sec.get('phrases'), sid + ' 缺 phrases（精句）'
        for x in sec.get('sentences') or []:
            assert x.get('en') and x.get('cn'), sid + ' 句池缺 en/cn'
            if words(x['en']) > 22:
                problems.append('%s 句池超 22 词: %s' % (sid, x['en']))

    must = sum(words(s['en']) + words(s.get('negative_en')) for s in d['sections']) \
        + sum(words(v['en']) for s in d['sections'] for v in (s.get('skeletons') or [])) \
        - sum(words(s['en']) for s in d['sections'] if s.get('skeletons'))
    ammo = sum(len(s.get('sentences') or []) for s in d['sections'])
    print('✅ 校验通过：%d 个 section / %d 句骨架 / %d 个负面版 / %d 张精句卡' % (
        len(d['sections']), n_skel, n_neg, len([s for s in d['sections'] if s.get('phrases')])))
    print('   ⭐ 必背骨架合计: %d 词（平均 %.1f 词/天，按 30 天算）' % (must, must / 30))
    print('   ⚡ 弹药句池: %d 句' % ammo)
    if problems:
        print('   ⚠️ 体检提醒:')
        for x in problems:
            print('      -', x)
    else:
        print('   ✅ 词数体检通过（片段 ≤22 词 / 骨架 ≤45 词 / 句池 ≤22 词）')


if __name__ == '__main__':
    main()
