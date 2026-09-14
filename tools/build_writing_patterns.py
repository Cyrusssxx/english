# -*- coding: utf-8 -*-
'''交叉索引：把 17 篇大作文「套用示范」里的内容反挂进词汇板块，分**两组**：
  ① 模板句型  —— 该年真正用到的模板句（跨年重复自动合并成「高频 · N 年」）
  ② 填槽表达  —— 该年往 {{槽位}} 里填的题相关表达（换词应万变）
落到三处：
  1. pwa/data/writing_patterns.json
  2. pwa/data/phrasebook.json  新增「写作句式」「填槽表达」两类（幂等）
  3. pwa/js/nearmap.js         两张地图：写作句式（按功能簇）/ 填槽表达（按段落）
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
    'para2_economy': ('第二段 · 经济类归因', '#f97316'),
    'para2_campus': ('第二段 · 校园/成长类归因', '#eab308'),
    'para2_env': ('第二段 · 环境生态类归因', '#22c55e'),
    'para2_sports': ('第二段 · 体育健康类归因', '#10b981'),
    'para2_culture': ('第二段 · 文化自信类归因', '#a855f7'),
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
    payload = payload or json.load(open(OUT_FP, encoding='utf-8'))
    ph = json.load(open(PH_FP, encoding='utf-8'))
    cats = [c for c in ph.get('cats', []) if c not in (CAT_TPL, CAT_SLOT)]
    groups = {k: v for k, v in ph.get('groups', {}).items() if k not in (CAT_TPL, CAT_SLOT)}
    rows = []
    for gname, items in payload['tpl_groups'].items():
        for e in items:
            rows.append({'w': e['w'], 'meaning': e['cn'], 'en': '', 'cn': '',
                         'src': '%s（%s）' % (e['src'], '/'.join(e['years'])),
                         'year': e['years'][-1], 'years': e['years'], 'freq': len(e['years']),
                         'func': gname, 'variants': [], 'aid': ''})
    rows.sort(key=lambda r: (list(payload['tpl_groups']).index(r['func']), -r['freq']))
    srows = []
    for gname, items in payload['slot_groups'].items():
        for e in items:
            srows.append({'w': e['w'], 'meaning': e['cn'], 'en': '', 'cn': '',
                          'src': '%s 的 {{%s}}（%s）' % (e['para'], e['name'], '/'.join(e['years'])),
                          'year': e['years'][-1], 'years': e['years'], 'freq': len(e['years']),
                          'func': gname, 'variants': [], 'aid': ''})
    srows.sort(key=lambda r: (list(payload['slot_groups']).index(r['func']), -r['freq'], r['w']))
    cats.extend([CAT_TPL, CAT_SLOT])
    groups[CAT_TPL] = rows
    groups[CAT_SLOT] = srows
    ph['cats'] = cats
    ph['groups'] = groups
    ph['count'] = sum(len(v) for v in groups.values())
    json.dump(ph, open(PH_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('并入 phrasebook.json：「%s」%d 条、「%s」%d 条，总计 %d 条'
          % (CAT_TPL, len(rows), CAT_SLOT, len(srows), ph['count']))


NM_START = '  /* >>> 写作句式（tools/build_writing_patterns.py 自动生成，勿手改） >>> */'
NM_END = '  /* <<< 写作句式 <<< */'


def inject_nearmap(payload=None):
    payload = payload or json.load(open(OUT_FP, encoding='utf-8'))
    maps = []
    br = []
    for gname, items in payload['tpl_groups'].items():
        if not items:
            continue
        br.append({'name': '%s（%d）' % (gname, len(items)),
                   'color': items[0].get('color', '#0d9488'),
                   'children': [{'name': '%s %s · %s' % (e['w'], e['cn'],
                                ('%d 年' % len(e['years'])) if len(e['years']) > 1 else e['years'][0]),
                                'en': e['w'],
                                'rest': '%s · %s' % (e['cn'], ('%d 年' % len(e['years']))
                                                     if len(e['years']) > 1 else e['years'][0])}
                               for e in items]})
    maps.append({'id': 'writing', 'title': '写作句式 · 模板句型（大作文 2010-2026）',
                 'root': '写作句式', 'rootColor': '#0d9488',
                 'intro': ('来源：2010-2026 英语二大作文「真题套用示范」真正用到的模板句。'
                           '{{ }} 是留给题目的槽位，尾部数字为该句在多届示范里出现过的年数——'
                           '数字越大越适合直接背。'),
                 'branches': br})
    br2 = []
    for gname, items in payload['slot_groups'].items():
        if not items:
            continue
        br2.append({'name': '%s（%d）' % (gname, len(items)),
                    'color': payload['slot_colors'].get(gname, '#64748b'),
                    'children': [{'name': '%s %s · %s' % (e['w'], e['cn'], e['name']),
                                  'en': e['w'],
                                  'rest': '%s（{{%s}}）' % (e['cn'], e['name'])}
                                 for e in items]})
    maps.append({'id': 'writing_slot', 'title': '填槽表达 · 换词应万变（大作文 2010-2026）',
                 'root': '填槽表达', 'rootColor': '#8b5cf6',
                 'intro': ('来源：17 篇示范里真正填进模板 {{槽位}} 的题相关表达。'
                           '写新题时在同类里换词即可——例如「占比最大」的主体、'
                           '「时间」的起止年份，都有现成说法可套。'),
                 'branches': br2})
    block = NM_START + '\n  [' + ',\n   '.join(json.dumps(m, ensure_ascii=False, indent=2) for m in maps) + \
        '].forEach(function (m) { DATA.maps.push(m); });\n' + NM_END
    src = open(NM_FP, encoding='utf-8').read()
    if NM_START in src and NM_END in src:
        src = re.sub(re.escape(NM_START) + r'.*?' + re.escape(NM_END), lambda _: block, src, flags=re.S)
    else:
        anchor = '  function esc(s) {'
        if anchor not in src:
            raise SystemExit('nearmap.js 找不到插入锚点')
        src = src.replace(anchor, block + '\n\n' + anchor, 1)
    open(NM_FP, 'w', encoding='utf-8', newline='\n').write(src)
    print('注入 nearmap.js：%d 张地图（%s）' % (len(maps), ' / '.join(m['title'][:12] for m in maps)))


def main():
    payload = build()
    merge_phrasebook(payload)
    inject_nearmap(payload)


if __name__ == '__main__':
    main()
