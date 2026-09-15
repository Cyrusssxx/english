# -*- coding: utf-8 -*-
'''交叉索引：把 17 篇大作文「套用示范」里的内容反挂进词汇板块，分**两组**：
  ① 模板句型  —— 该年真正用到的模板句（跨年重复自动合并成「高频 · N 年」）
  ② 填槽表达  —— 该年往 {{槽位}} 里填的题相关表达（换词应万变）
落到三处：
  1. pwa/data/writing_patterns.json（句型索引，仅存档；2026-09-15 起不再进词汇页）
  2. pwa/data/phrasebook.json  清理「写作句式」「填槽表达」两类（幂等）
  3. pwa/js/nearmap.js         移除「写作句式」注入块（幂等）
用法：python tools/build_writing_patterns.py
'''
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'pwa', 'data')
JSDIR = os.path.join(ROOT, 'pwa', 'js')
APPLY_FP = os.path.join(DATA, 'writing_apply.json')
OUT_FP = os.path.join(DATA, 'writing_patterns.json')
PH_FP = os.path.join(DATA, 'phrasebook.json')
NM_FP = os.path.join(JSDIR, 'nearmap.js')

CAT_TPL = '写作句式'
CAT_SLOT = '填槽表达'

# 槽位名的功能归类（用于地图分簇）
SLOT_GROUP = [
    ('图型 · 引出词', ['chart', 'topic']),
    ('主体 · 事物', ['item1', 'item2', 'item3', 'item4', 'item5']),
    ('数据 · 占比', ['percent1', 'percent2', 'percent3', 'percent4', 'percent5']),
    ('数据 · 数值', ['num1', 'num2', 'num3', 'num4', 'num5', 'num6']),
    ('时间', ['time1', 'time2', 'time3', 'time4', 'time5', 'time6']),
]
SLOT_COLOR = {
    '图型 · 引出词': '#0d9488',
    '主体 · 事物': '#8b5cf6',
    '数据 · 占比': '#ef4444',
    '数据 · 数值': '#f59e0b',
    '时间': '#3b82f6',
    '其他': '#64748b',
}

# 模板句 → 功能簇（按模板所属段落判断）
SEC_FUNC = {
    'chart_static': ('第一段 · 静态图描述', '#0d9488'),
    'chart_dynamic': ('第一段 · 动态图描述', '#0ea5e9'),
    'para2_why': ('第二段 · 原因（机制句池）', '#f97316'),
    'para3_positive': ('第三段 · 正面总结建议', '#06b6d4'),
    'para3_negative': ('第三段 · 负面总结建议', '#64748b'),
}


def title_map():
    '''模板文件里的 id → title（示范里的 src 就是用它拼的）'''
    d = json.load(open(os.path.join(DATA, 'writing_templates.json'), encoding='utf-8'))
    return {s.get('title', ''): s['id'] for s in d['sections']}


def build():
    ap = json.load(open(APPLY_FP, encoding='utf-8'))
    TITLE2ID = title_map()
    tpl_groups = defaultdict(list)     # 功能簇 → [{w, cn, years, src}]
    slot_groups = defaultdict(list)    # 槽位组 → [{w, cn, years, names}]
    tpl_seen = {}
    slot_seen = {}

    for y in sorted(ap):
        v = ap[y]
        for k in v.get('key_phrases', []):
            key = k['en']
            if key in tpl_seen:
                tpl_seen[key]['years'].append(y)
                continue
            sid = next((s for tt, s in TITLE2ID.items() if k['src'].startswith(tt)),
                       'para2_economy')   # 用最长前缀匹配，兼容「第三段 · 正面版」这类多段标题
            gname, color = SEC_FUNC[sid]
            rec = {'w': key, 'cn': k['cn'], 'years': [y], 'src': k['src'], 'color': color}
            tpl_seen[key] = rec
            tpl_groups[gname].append(rec)
        for s in v.get('slot_phrases', []):
            norm = s['name']
            skey = (norm, s['en'])
            if skey in slot_seen:
                slot_seen[skey]['years'].append(y)
                continue
            grp = '其他'
            for g, names in SLOT_GROUP:
                if norm in names:
                    grp = g
                    break
            rec = {'w': s['en'], 'cn': s['cn'], 'name': norm,
                   'para': s['para'], 'years': [y]}
            slot_seen[skey] = rec
            slot_groups[grp].append(rec)

    for g in tpl_groups:
        tpl_groups[g].sort(key=lambda x: (-len(x['years']), x['src']))
    for g in slot_groups:
        slot_groups[g].sort(key=lambda x: (-len(x['years']), x['name'], x['w']))

    order = [SEC_FUNC[k][0] for k in SEC_FUNC]
    tpl_ordered = {g: tpl_groups[g] for g in order if g in tpl_groups}
    for g in tpl_groups:
        tpl_ordered.setdefault(g, tpl_groups[g])
    payload = {
        'count': len(tpl_seen),
        'slot_count': len(slot_seen),
        'tpl_groups': tpl_ordered,
        'tpl_colors': {SEC_FUNC[k][0]: SEC_FUNC[k][1] for k in SEC_FUNC},
        'slot_groups': dict(slot_groups),
        'slot_colors': SLOT_COLOR,
    }
    json.dump(payload, open(OUT_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入 writing_patterns.json：模板句型 %d 条 / 填槽表达 %d 条' % (len(tpl_seen), len(slot_seen)))
    for g, items in tpl_groups.items():
        print('  模板 %-22s %d 条' % (g, len(items)))
    for g, items in slot_groups.items():
        print('  填槽 %-22s %d 条' % (g, len(items)))
    return payload


def merge_phrasebook(payload=None):
    """从 phrasebook.json 里清掉「写作句式 / 填槽表达」两类。

    2026-09-15 用户要求：模板相关内容不要再塞进「近义词 / 熟词短语」页。
    数据仍在 writing_patterns.json 里存档，需要时可从这里取回。"""
    ph = json.load(open(PH_FP, encoding='utf-8'))
    drop_n = sum(len(v) for k, v in ph.get('groups', {}).items() if k in (CAT_TPL, CAT_SLOT))
    cats = [c for c in ph.get('cats', []) if c not in (CAT_TPL, CAT_SLOT)]
    groups = {k: v for k, v in ph.get('groups', {}).items() if k not in (CAT_TPL, CAT_SLOT)}
    ph['cats'] = cats
    ph['groups'] = groups
    ph['count'] = sum(len(v) for v in groups.values())
    json.dump(ph, open(PH_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('phrasebook.json：清掉模板相关 %d 条 → 余 %d 条 / %d 类' % (drop_n, ph['count'], len(cats)))


NM_START = '  /* >>> 写作句式（tools/build_writing_patterns.py 自动生成，勿手改） >>> */'
NM_END = '  /* <<< 写作句式 <<< */'


def inject_nearmap(payload=None):
    """从 nearmap.js 移除「写作句式」注入块（旧版本是注入两张地图，现改为清理）。"""
    src = open(NM_FP, encoding='utf-8').read()
    pat = r'\n+[ \t]*' + re.escape(NM_START) + r'.*?' + re.escape(NM_END)
    if not re.search(pat, src, flags=re.S):
        print('nearmap.js：无写作句式块，跳过')
        return
    src = re.sub(pat, '\n', src, count=1, flags=re.S)
    open(NM_FP, 'w', encoding='utf-8', newline='\n').write(src)
    print('nearmap.js：已移除写作句式注入块')


def main():
    payload = build()
    merge_phrasebook(payload)
    inject_nearmap(payload)


if __name__ == '__main__':
    main()
