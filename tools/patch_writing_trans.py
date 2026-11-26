# -*- coding: utf-8 -*-
"""增量补「押题范文 / 写作模板」语料里点开没译的词到 pwa/data/dict.json（2026-11-27）

背景：dict.json 只收 16 年真题正文里的较难词；写作模板和 26 篇押题范文里有些词
（ride-hailing / first-aid / thought-provoking …）不在语料内，点词卡只能显示
「常用词，离线词典只收难词」。本脚本把缺口一次性补齐，不动已有词条。

真源：tools/ecdict.csv（有现成中文）；复合词与语境义在 MANUAL 里手工给。

⚠ 重跑 tools/build_dict.py 会覆盖本补丁 → 之后必须再跑一次本脚本。

运行：python tools/patch_writing_trans.py
"""
import csv
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, 'tools', 'ecdict.csv')
DICT_PATH = os.path.join(ROOT, 'pwa', 'data', 'dict.json')

TRANS_MAX = 80
csv.field_size_limit(10 * 1024 * 1024)

# 占位符碎片 / 时间缩写，不是可查的词
SKIP = {'num', 'm', 'p'}

# ECDICT 没有的词，或 ECDICT 首选义与范文语境不符的词（手工给语境义）
MANUAL = {
    'ride-hailing': 'n. 网约车；打车（用手机应用叫车）',
    'over-packaging': 'n. 过度包装',
    'ai-powered': 'a. 人工智能驱动的；AI 赋能的',
    'self-media': 'n. 自媒体',
    'step-free': 'a. 无台阶的；无障碍的',
    'chatgpt': 'n. ChatGPT（人工智能聊天机器人）',
    'ramps': 'n. 斜坡；坡道（无障碍坡道）',
    'interchange': 'n. 交流；互换',
    'pick-up': 'n. 接人；接机',
    'inheritance': 'n. 传承；继承；遗产',
    'weakening': 'n. 减弱；削弱',
    'quadrupling': 'v. 增至四倍；翻两番',
    'follow-up': 'a. 后续的；跟进的',
    'dependence': 'n. 依赖；依靠',
    'barrier-free': 'a. 无障碍的',
    'li': 'n. 李（中文姓氏音译）',
    'ming': 'n. 明（中文名字音译）',
    'alex': 'n. 亚历克斯（人名）',
}

# 从押题范文 + 写作模板扫出来的缺译词（见 tools/_scan_missing_trans.js）
TARGETS = """
thought-provoking first-aid creators returnees inheritance learners ride-hailing symbolically
harmonious honesty misuse regained on-the-job lifelong far-reaching overtook admittedly neediest
follow-up recommendation apologize roommate interchange attendees oversized wheelchair ramps
disabilities quadrupling longevity hard-won refrigerated dependable dependence ready-made weaken
weakening recyclable falsehoods corrections self-knowledge careless one-off pick-up barrier-free
over-packaging outsold noticeable ai-powered self-media suppliers first-time step-free
li ming jane beijing alex chatgpt num m p
""".split()


def clean_trans(t):
    t = (t or '').replace('\\n', '; ').replace('\n', '; ').strip()
    t = re.sub(r'\s+', ' ', t)
    if len(t) > TRANS_MAX:
        t = t[:TRANS_MAX].rstrip() + '…'
    return t


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


def main():
    ecdict = {}
    with open(CSV_PATH, encoding='utf-8') as fp:
        for row in csv.DictReader(fp):
            w = (row.get('word') or '').strip().lower()
            if w:
                ecdict[w] = row

    with open(DICT_PATH, encoding='utf-8') as fp:
        data = json.load(fp)

    words = data['words']
    added = []
    for w in TARGETS:
        if w in SKIP:
            continue
        row = ecdict.get(w)
        if w in MANUAL:
            t = MANUAL[w]
        elif row:
            t = clean_trans(row.get('translation'))
        else:
            print('⚠ ECDICT 也查不到，跳过：', w)
            continue
        if not t:
            print('⚠ 空释义，跳过：', w)
            continue
        if w in words:
            continue                      # 不动已有词条
        words[w] = {
            'p': '',                      # ECDICT 音标有乱码，统一不显示
            't': t,
            'frq': to_int(row.get('frq')) if row else 0,
            'tag': '',
        }
        added.append(w)

    with open(DICT_PATH, 'w', encoding='utf-8') as fp:
        # 原 dict.json 是紧凑格式（无空格无换行），必须保持一致，否则体积从 676KB 涨到 943KB
        json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))

    print('补入 %d 词，词典现有 %d 条：' % (len(added), len(words)))
    print(' '.join(added))


if __name__ == '__main__':
    main()
