# -*- coding: utf-8 -*-
"""合并短语最后一段（350 条）的筛选结果：规范化粘连形态 + 去重 + 入库"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TOOLS = 'tools'

PH = [
    # (规范短语, 释义, 类别)   —— 已剔除源数据粘连残缺项与已有重复项
    ('settle down', '安定下来，过安定生活', '社会生活'),
    ('nest egg', '储备金，养老积蓄', '社会生活'),
    ('catch-all term', '含义甚广的统称，笼统说法', '商业经济'),
    ('rule out', '排除，不考虑', '教育文化历史'),
    ('easy come, easy go', '来得容易去得快', '教育文化历史'),
    ('eat one\'s words', '收回前言，承认说错', '教育文化历史'),
    ('on a shoestring', '以极少的钱，小本经营', '政法'),
    ('go hand in hand', '密切相关，相伴随行', '社会生活'),
    ('on the ground', '在现场；在实地', '政法'),
    ('follow through', '贯彻到底，坚持完成', '科学科技'),
    ('chances are', '很可能，大概', '政法'),
    ('shore up', '支撑，加固', '政法'),
    ('get one\'s hands on', '弄到手，得到', '教育文化历史'),
    ('bring about', '引起，导致', '科学科技'),
    ('bring up', '养育，抚养', '教育文化历史'),
    ('break with', '与……决裂，背离', '教育文化历史'),
    ('stand up for', '捍卫，维护', '政法'),
    ('find one\'s way to', '设法到达，进入', '教育文化历史'),
    ('by all means', '当然可以；务必', '教育文化历史'),
    ('may well', '很可能', '科学科技'),
    ('give rise to', '引起，激发', '科学科技'),
    ('keep track of', '追踪，记录', '政法'),
    ('fall off', '数量减少，下降', '商业经济'),
    ('capitalize on', '充分利用，从……获利', '商业经济'),
    ('hit home', '使人深刻理解，正中要害', '教育文化历史'),
    ('sail through', '顺利通过', '政法'),
    ('join forces', '联合，合作', '商业经济'),
    ('come to life', '变得生动，鲜活起来', '教育文化历史'),
    ('account for', '解释；（在数量上）占', '科学科技'),
    ('around the corner', '即将到来', '社会生活'),
    ('at odds with', '与……不一致，相冲突', '商业经济'),
    ('bear out', '证实，支持', '科学科技'),
    ('beef up', '加强，提高', '社会生活'),
    ('boil down to', '归纳为，归根结底是', '教育文化历史'),
    ('bring out', '激发，使显出', '社会生活'),
    ('call out', '公开批评，指摘', '教育文化历史'),
    ('clamp down', '严厉打击，严控', '政法'),
    ('come across', '给人……的印象', '社会生活'),
    ('come up with', '想出，提出', '科学科技'),
    ('count on', '依靠，指望', '社会生活'),
    ('crop up', '突然出现', '社会生活'),
    ('do one\'s bit', '做分内事，尽本分', '社会生活'),
    ('draw on', '凭借，利用', '教育文化历史'),
    ('fall short', '未达到，不足', '商业经济'),
    ('flesh out', '充实，补充细节', '教育文化历史'),
    ('follow suit', '效仿，照着做', '政法'),
    ('fork over', '不情愿地交出', '政法'),
    ('fuss over', '过分关心，过度紧张', '社会生活'),
    ('grapple with', '努力应对，设法克服', '商业经济'),
    ('knock out', '淘汰，击倒', '政法'),
    ('lay off', '辞退，解雇', '社会生活'),
    ('lie with', '在于，由……决定', '科学科技'),
    ('live by', '遵守，按照（准则）', '政法'),
    ('live off', '靠……过活，以……为生', '商业经济'),
    ('look down on', '轻视，看不起', '社会生活'),
    ('part with', '放弃，交出', '政法'),
    ('pin down', '确定，证实', '科学科技'),
    ('plunge into', '陷入（不快之事）', '教育文化历史'),
    ('pop into', '（念头）闪现；突然进入', '社会生活'),
    ('pour out', '倾诉，倾吐', '社会生活'),
    ('press for', '极力要求，敦促', '科学科技'),
    ('prey on', '坑骗，敲诈（弱者）', '商业经济'),
    ('pull off', '做成（难事）', '社会生活'),
    ('put down to', '归因于', '教育文化历史'),
    ('rest with', '在于；由……负责', '科学科技'),
    ('roll out', '推出（新产品等）', '政法'),
    ('rush through', '匆匆通过，草草处理', '政法'),
    ('scale back', '缩减，减少', '政法'),
    ('seize on', '抓住，热衷于', '教育文化历史'),
    ('set the tone', '定下基调', '教育文化历史'),
    ('sort out', '解决，理清', '政法'),
    ('stake out', '明确表明，界定', '政法'),
    ('stand down', '退职，退位', '政法'),
    ('strike sb. as', '给……的印象', '教育文化历史'),
    ('throw into', '投身于', '社会生活'),
    ('to the letter', '丝毫不差地，严格地', '政法'),
    ('touch on', '提及，谈到', '科学科技'),
    ('turn around', '扭转，出现好转', '社会生活'),
    ('turn on its head', '彻底颠覆', '教育文化历史'),
    ('usher in', '开创，迎来', '政法'),
    ('ward off', '防止，避开', '社会生活'),
    ('weigh in', '参与讨论，发表意见', '政法'),
    ('lie in', '在于', '政法'),
    ('wear lightly', '学识渊博却不卖弄', '教育文化历史'),
    ('take a page from', '借鉴（他人经验）', '商业经济'),
    ('renege on', '违背，毁约', '政法'),
    ('abide by', '遵守', '政法'),
    ('a string of', '一系列（事件）', '政法'),
    ('go to war with', '与……对抗，交锋', '政法'),
]

SKIP_GARBAGE = ['bring...tobear（on', 'couldyetdosth。']


def key(s):
    s = s.lower().replace('’', "'")
    s = s.replace('one\'s', 'ones').replace('sb.', 'sb')
    s = re.sub(r'[^a-z ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def main():
    ph_rows = json.load(open(os.path.join(TOOLS, 'wn2_phrases_worklist.json'), encoding='utf-8'))['rows']
    idx = {key(r['w']): r for r in ph_rows}
    dec = json.load(open(os.path.join(TOOLS, 'wn2_decisions.json'), encoding='utf-8'))
    have = {key(x['w']) for x in dec.get('phrases', [])}

    ok, dup, miss = 0, [], []
    for w, m, c in PH:
        k = key(w)
        if k in have:
            dup.append(w)
            continue
        r = idx.get(k)
        if not r:
            miss.append(w)
            continue
        dec['phrases'].append({'w': w, 'meaning': m, 'cat': c})
        have.add(k)
        ok += 1
    print('短语入库 %d ｜重复跳过 %d %s ｜源中找不到 %d %s' % (ok, len(dup), dup, len(miss), miss))

    # 剩余全部标记为已筛（丢弃）
    allph = json.load(open(os.path.join(TOOLS, 'wn2_phrases_worklist.json'), encoding='utf-8'))['rows']
    done = {key(x['w']) for x in dec.get('phrases', [])} | \
           {key(w) for w in dec.get('pdropped', [])}
    n = 0
    for r in allph:
        if key(r['w']) not in done:
            dec.setdefault('pdropped', []).append(r['w'])
            done.add(key(r['w']))
            n += 1
    print('剩余标记已筛 %d ｜累计丢弃 %d' % (n, len(dec['pdropped'])))
    json.dump(dec, open(os.path.join(TOOLS, 'wn2_decisions.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)


main()
