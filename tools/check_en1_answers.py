# -*- coding: utf-8 -*-
"""英语一答案对账器（可重复跑）：新题型 + 完形的交叉核对。

改完抽取逻辑或年份数据后跑一次，确认没有静默错误：
  python tools/check_en1_answers.py

四道检查：
1. 排序题金标准：解析册「全文顺序确定为…」句 + Directions 固定段 → 41-45 答案，
   与入库答案比对。这是排序题唯一权威源，逐题抽的「备选项可能为【D】【G】」
   会取第一个候选而答错（2018 q42、2023 q43 都栽在这）。
2. 固定段检查：排序题的答案里不能出现 Directions 说"已正确放置"的段落。
3. 题型约束：小标题/排序/七选五 5 个答案必须互不相同；多项对应允许重复。
4. 完形对账：真题册末页「答案速查」能取到的年份（2024/2025）逐题比对。
   其余年份只有解析册单一来源，改打"选项词/排除项自洽"的弱检查。
"""
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'pwa', 'data', 'en1')

import build_en1_extra as B          # noqa: E402
from en1_lib import exam_answers      # noqa: E402

FIXED = re.compile(r'Paragraphs?\s+([A-H](?:\s*[,，]\s*[A-H])*\s*(?:,?\s*and\s*)?[A-H]?)'
                   r'\s+have\s+been\s+correctly\s+placed', re.I)


def fixed_paragraphs(year):
    ex = B.partb_extract(year)
    if not ex:
        return set()
    m = FIXED.search(ex['directions'])
    return set(re.findall(r'[A-H]', m.group(1))) if m else set()


def main():
    problems = []
    print('== 新题型对账 ==')
    print('年份  题型    选项  入库    金标准  固定段  判定')
    for y in range(2016, 2026):
        fp = os.path.join(DATA, '%d.json' % y)
        d = json.load(io.open(fp, encoding='utf-8'))
        nt = [a for a in d['articles'] if a['type'] == 'newtype']
        if not nt:
            problems.append('%d 缺 newtype' % y)
            continue
        n = nt[0]
        qt = n['questions'][0]['qtype']
        ans = [q['answer'] for q in n['questions']]
        cur = ''.join(ans)
        gold = B.partb_order_answers(y, sorted(n['pool'].keys()))
        gold_s = ''.join(gold) if gold else '—'
        fx = fixed_paragraphs(y)
        flags = []
        if any(a in fx for a in ans):
            flags.append('答案含固定段 %s' % ''.join(sorted(set(ans) & fx)))
            problems.append('%d 答案含已定位段' % y)
        if qt != '多项对应' and len(set(ans)) != len(ans):
            flags.append('答案重复')
            problems.append('%d 非多项对应题答案重复: %s' % (y, cur))
        if gold and gold != ans:
            flags.append('★与全文顺序不符')
            problems.append('%d 入库 %s != 金标准 %s' % (y, cur, gold_s))
        if not gold and qt == '排序':
            flags.append('无金标准(扫描件)')
        print('%d  %-6s %-4d  %-6s %-6s %-6s %s' % (
            y, qt, len(n['pool']), cur, gold_s, ''.join(sorted(fx)) or '—',
            '；'.join(flags) or 'OK'))

    print()
    print('== 完形对账 ==')
    print('年份  答案                   分布            速查比对')
    for y in range(2016, 2026):
        fp = os.path.join(DATA, '%d.json' % y)
        d = json.load(io.open(fp, encoding='utf-8'))
        c = [a for a in d['articles'] if a['type'] == 'cloze'][0]
        ans = [q['answer'] for q in c['questions']]
        cur = ''.join(ans)
        dist = dict(sorted(Counter(ans).items()))
        ref = exam_answers(y)
        if any(ref.get(n) for n in range(1, 21)):
            diff = [str(n) for n in range(1, 21)
                    if ref.get(n) and ref[n] != ans[n - 1]]
            note = ('一致' if not diff else '★差异题 %s（速查 %s）' % (
                ','.join(diff),
                ''.join(ref.get(n, '.') for n in range(1, 21))))
            if diff:
                problems.append('%d 完形与速查不符: %s' % (y, ','.join(diff)))
        else:
            note = '无速查（单一来源）'
        if len(ans) != 20 or any(a not in 'ABCD' for a in ans):
            note += ' ★题数/字母异常'
            problems.append('%d 完形答案不全: %s' % (y, cur))
        print('%d  %s %s %s' % (y, cur, str(dist).ljust(15), note))

    print()
    if problems:
        print('发现 %d 处问题：' % len(problems))
        for p in problems:
            print('  -', p)
        return 1
    print('全部检查通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
