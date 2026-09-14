#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小作文（英语二 A 节 · 应用文）功能句库 —— 从原始 md 生成 pwa/data/small_writing.json

数据源：D:/cjx/下载/download/考研英语小作文功能句全集（可直接复制粘贴到Word）.md
产物：  pwa/data/small_writing.json

规则：
  1) 原始 md 用 `\\[角色\\]` 标槽位、用「题目相关词」标主题 → 统一换成项目占位符 {{token}}（英文）；
     同时自动汇总「占位符图例」（token → 中文角色 + 首个例句）。
  2) 段落 / 类别 / 第几句 三级结构 → banks（扁平句库，带 part/type/slot）。
  3) 另出 types（按信件类型拼装视图），供前端「按类型」页签使用。
可重复执行（幂等）。
"""
import io
import os
import re
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import small_writing_extra as EXTRA      # 补充类型 / 真题适配表 / 选句决策 / 分层规则

MD = r'D:/cjx/下载/download/考研英语小作文功能句全集（可直接复制粘贴到Word）.md'
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.normpath(os.path.join(ROOT, '..')), 'pwa', 'data', 'small_writing.json')
DATA_DIR = os.path.normpath(os.path.join(ROOT, '..', 'pwa', 'data'))

# ---------- 槽位角色 → 英文 token ----------
PH = {
    '题目相关词': 'topic',
    '题目相关短语或者词': 'detail',
    '动词ing形式，比如 putting': 'ving',
    '动词ing，比如 cultivating': 'ving',
    '建议行动，动词短语': 'action',
    '受邀行动，比如 take part in': 'join',
    '受邀行动，动词短语': 'join',
    '要做的事': 'task',
    '好处是什么': 'benefit',
    '受到邀请带来的好处': 'gain',
    '邀请带来的好处': 'gain',
    '邀请相关能力或品质': 'quality',
    '邀请相关短语': 'gain',
    '邀请收获': 'gain',
    '参加收获': 'gain',
    '参加相关短语': 'gain',
    '过失行为': 'fault',
    '产生的影响': 'impact',
    '客观原因': 'cause',
    '主观原因，例如 proper planning': 'reason',
    '主观原因，例如 my carelessness': 'reason',
    '本应做到的事': 'should',
    '取得的成就': 'achievement',
    '品质或能力': 'quality',
    '品质或努力过程': 'quality',
    '受众对象': 'audience',
    '具体表现': 'performance',
    '付出或过程': 'effort',
    '关键努力': 'effort',
    '良好习惯': 'habit',
    '长期坚持的行为': 'persistence',
    '积极行为': 'behavior',
    '具体做法': 'approach',
    '相关价值': 'value',
    '其他任务或责任': 'duty',
    '学习到的能力或品质': 'quality',
    '未来行动': 'next step',
    '下一阶段目标': 'goal',
    '未来发展方向': 'goal',
    '未来收获或成就': 'goal',
    '未来成长': 'goal',
    '未来挑战或目标': 'goal',
    '长期目标': 'goal',
    '更高层次的成就': 'goal',
    '介绍对象或概念': 'subject',
    '核心特点': 'feature',
    '概括性定义': 'definition',
    '重点方面': 'focus',
    '功能或作用': 'function',
    '具体益处': 'benefit',
    '要素 1': 'part1',
    '要素 2': 'part2',
    '主要内容': 'content',
    '总体目标': 'purpose',
    '角色定位': 'role',
    '应用场景': 'scene',
    '简要描述': 'profile',
    '对比对象': 'contrast',
    '日常习惯 1': 'habit1',
    '日常习惯 2': 'habit2',
    '生活相关优点，如 a balanced and healthy lifestyle': 'advantage',
    '作息习惯，如 get up early': 'routine',
    '学习/锻炼习惯，如 set aside time for regular exercise': 'activity',
    '状态，如 energetic and focused': 'state',
    '学习习惯 1': 'habit1',
    '兴趣习惯 2': 'habit2',
    '生活方式优点，如 a positive and self-disciplined lifestyle': 'advantage',
    '方面 1': 'aspect1',
    '方面 2': 'aspect2',
    '具体收获 1': 'gain1',
    '具体作用 2': 'effect',
    '特定群体': 'audience',
    '内容 1': 'content1',
    '内容 2': 'content2',
    '内容 3': 'content3',
    '整体效果': 'effect',
    '亮点设计': 'highlight',
    '使用或理解方面的好处': 'benefit',
    '使用动作': 'action',
    '提升点': 'improve',
    '具体内容': 'content',
    '支持对象': 'audience',
    '目标人群': 'audience',
    '目标需求': 'need',
    '帮助理解的内容': 'content',
    '延伸价值': 'value',
    '使用目的': 'purpose',
    '受益者': 'beneficiary',
    '核心优势': 'advantage',
    '具体任务或目标': 'goal',
    '应用方向': 'scene',
    '表面印象': 'impression',
    '深层价值': 'value',
    '突出优点': 'advantage',
    '适用领域': 'field',
    '时间信息': 'time',
    '参加对象': 'audience',
    '对象': 'audience',
    '地点信息': 'place',
    '起始时间': 'time1',
    '结束时间': 'time2',
    '主要环节': 'session',
    '活动主题或内容': 'theme',
    '目标问题': 'problem',
    '主办单位': 'organizer',
    '协办单位': 'coorganizer',
    '形式 1': 'form1',
    '形式 2': 'form2',
    '预期效果': 'effect',
    '重点环节 1': 'session1',
    '重点环节 2': 'session2',
    '具体安排，如 group discussion or Q and A': 'arrangement',
    '环节，如 free communication': 'session',
    '具体收获': 'gain',
    '注意事项或要求': 'requirement',
    '携带物品或准备事项': 'item',
    '纪律或安全要求': 'rule',
    '通知渠道': 'channel',
    '期待动作': 'expect',
    '时间节点': 'deadline',
    '总体目的': 'purpose',
    '受益对象': 'beneficiary',
    '期待成效': 'outcome',
    '期望结果': 'outcome',
    '积极变化': 'change',
    '积极结果': 'outcome',
    # —— 中文译文里同一槽位的另一种说法（归一化后按同一 token 处理）——
    '动词ing，比如 putting': 'ving',
    '时间地点信息': 'time place',
    '好处之一': 'benefit1',
    '好处之二': 'benefit2',
    '生活相关优点，如均衡而健康的生活方式': 'advantage',
    '作息习惯，如早起': 'routine',
    '学习/锻炼习惯，如留出固定时间进行锻炼': 'activity',
    '状态，如充沛的精力与集中的注意力': 'state',
    '生活方式优点，如积极而自律的生活方式': 'advantage',
    '应用场景 1': 'scene1',
    '应用场景 2': 'scene2',
    '具体安排，如分组讨论或答疑交流': 'arrangement',
    '环节，如自由交流': 'session',
}


def norm(s):
    return re.sub(r'\s+', '', s or '').lower()


PH_N = {}
for k, v in PH.items():
    PH_N[norm(k)] = (v, k)
UNMAPPED = {}


def conv(text, ph_example):
    """把 [角色] 与「题目相关词」换成 {{token}}，并登记占位符图例"""
    def rep_bracket(m):
        raw = m.group(1)
        hit = PH_N.get(norm(raw))
        if not hit:
            UNMAPPED[raw] = UNMAPPED.get(raw, 0) + 1
            tok = 'slot'
        else:
            tok, cn = hit
        ph_example.setdefault(tok, cn if hit else raw)
        return '{{' + tok + '}}'
    out = re.sub(r'\[([^\]]+)\]', rep_bracket, text)
    out = out.replace('题目相关词', '{{topic}}')
    return out


def unesc(s):
    for a, b in [(r'\.', '.'), (r'\[', '['), (r'\]', ']'), (r'\(', '('), (r'\)', ')'),
                 (r'\-', '-'), (r"\'", "'"), (r'\"', '"'), (r'\!', '!'),
                 (r'\*', '*'), (r'\_', '_')]:
        s = s.replace(a, b)
    return s.replace('\u2011', '-').replace('\u2010', '-').strip()


NUM_RE = re.compile(r'^(\d+)[.、]\s*(.+)$')
PART_RE = re.compile(r'^##\s*第(.)段功能句')
GRP_RE = re.compile(r'^###\s*(.+?)：?\s*$')
SLOT_RE = re.compile(r'^####\s*(.+?)：?\s*$')

PART_CN = {'一': 1, '二': 2, '三': 3}
# part2 的类别 → id/英文名
TYPE_MAP = [('建议', 'advice'), ('邀请', 'invite'), ('道歉', 'apology'),
            ('祝贺', 'congrats'), ('介绍', 'intro'), ('通知', 'notice')]


def merge_extra(banks, order):
    """并入 md 缺的 4 个第二段类型（感谢 / 投诉 / 询问 / 观点）"""
    for bid, spec in EXTRA.EXTRA_BANKS.items():
        items = []
        for en, cn, yrs in spec['items']:
            items.append({'en': en, 'cn': cn, 'tag': (yrs + ' 真题') if yrs else '通用'})
        banks[bid] = {'id': bid, 'part': spec['part'], 'type': spec['type'],
                      'label': spec['label'], 'items': items}
        order.append(bid)


def tag_of(bid, en):
    for pre, rx, tag in EXTRA.TAG_RULES:
        if bid.startswith(pre) and re.search(rx, en, re.I):
            return tag
    if bid == 'p2s1':
        return '引出'
    if bid == 'p3':
        return '收尾'
    if bid == 'p1s1':
        return '问候'
    if bid == 'p1s2':
        return '来意'
    m = re.match(r'p2_\w+_s(\d)', bid)
    if m:
        return EXTRA.SLOT_TAGS.get('s' + m.group(1), '展开')
    return ''


CORE_SLOTS = ('p1s1', 'p1s2', 'p2s1', 'p3')   # ⭐⭐ 骨架：任何一封信都要用的 4 句
TYPE_MUST_SLOTS = 2                          # 每个类型只把前 2 个槽位的首句标 ⭐


def compute_layers(banks):
    """三档：core（⭐⭐骨架 4 句）/ must（⭐必背，每类型 2 句）/ ammo（⚡弹药）
       freq：3 通用 / 2 常用 / 1 专场"""
    keep = set()
    by_type = {}
    for b in banks:
        m = re.match(r'p2_(\w+)_s(\d)', b['id'])
        if m:
            by_type.setdefault(m.group(1), []).append(int(m.group(2)))
    for tid, slots in by_type.items():
        for s in sorted(slots)[:TYPE_MUST_SLOTS]:
            keep.add('p2_%s_s%d' % (tid, s))
    for b in banks:
        bid = b['id']
        for i, it in enumerate(b['items']):
            if bid in CORE_SLOTS:
                it['tier'] = 'core' if i == 0 else 'ammo'
            elif bid in keep:
                it['tier'] = 'must' if i == 0 else 'ammo'
            else:
                it['tier'] = 'ammo'
            it['must'] = it['tier'] != 'ammo'
            if bid == 'p2s1':
                it['freq'] = 3
            elif bid == 'p1s1':
                it['freq'] = 3 if i < 8 else (2 if i < 13 else 1)
            elif bid == 'p3':
                it['freq'] = 3 if i < 6 else 2
            elif bid == 'p1s2':
                it['freq'] = 3 if i in (0, 4, 5, 8, 9) else 2
            else:
                it['freq'] = 3 if i == 0 else 2
            it['tag'] = tag_of(bid, it['en'])
        # 骨架 → 必背 → 弹药，同档内按考频降序（稳定排序）
        rank = {'core': 0, 'must': 1, 'ammo': 2}
        b['items'].sort(key=lambda x: (rank[x['tier']], -x['freq']))


def build_guide():
    """17 年真题适配表（题型 + 主题 + 该挑哪些句 + 跳原文）"""
    rows = []
    for y in sorted(EXTRA.GUIDE_MAP):
        tid, tname, hint = EXTRA.GUIDE_MAP[y]
        aid, topic = '%s_writinga' % y, ''
        fp = os.path.join(DATA_DIR, '%s.json' % y)
        if os.path.exists(fp):
            d = json.load(open(fp, encoding='utf-8'))
            for a in (d.get('articles') or []):
                if str(a.get('id')).replace('_writing_a', '_writinga') == aid:
                    aid = a['id']
                    topic = re.sub(r'^Part A\s*(应用文)?[：:]\s*', '', str(a.get('title') or '')).strip()
                    break
        rows.append({'year': y, 'type': tname, 'typeId': tid, 'topic': topic,
                     'hint': hint, 'aid': aid})
    return rows


def main():
    lines = io.open(MD, encoding='utf-8').read().split('\n')
    part, group, slot = 0, '', ''
    banks = {}       # id -> bank
    order = []
    cur = None
    cur_item = None
    i = 0
    notes = []
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        i += 1
        if not line:
            continue
        m = PART_RE.match(line)
        if m:
            part, group, slot, cur, cur_item = PART_CN[m.group(1)], '', '', None, None
            continue
        m = SLOT_RE.match(line)
        if m:
            slot = unesc(m.group(1))
            cur = None
            cur_item = None
            continue
        m = GRP_RE.match(line)
        if m and not line.startswith('####'):
            g = unesc(m.group(1))
            if g.endswith('功能句挑选'):
                slot = g
            else:
                group = g
            cur = None
            cur_item = None
            continue
        if line.startswith('>'):
            body = unesc(line.lstrip('> '))
            if body.startswith('秘密先说'):
                notes.append({'part': part, 'slot': slot, 'text': body.replace('秘密先说：', '').strip()})
                continue
            # 示例（2010 英语二）
            mm = re.match(r'示例（(.+?)）', body)
            src = mm.group(1) if mm else ''
            if cur_item is None:
                continue
            ex = {'en': '', 'cn': '', 'src': src}
            while i < len(lines):
                nxt = lines[i].strip()
                if not nxt or nxt.startswith('>') or NUM_RE.match(nxt) or nxt.startswith('#'):
                    break
                i += 1
                t = unesc(nxt)
                if not ex['en']:
                    ex['en'] = t
                elif not ex['cn']:
                    ex['cn'] = t
            if ex['en']:
                cur_item.setdefault('ex', []).append(ex)
            continue
        m = NUM_RE.match(line)
        if m:
            en = unesc(m.group(2))
            cn = ''
            if i < len(lines):
                nxt = lines[i].strip()
                if nxt and not nxt.startswith(('#', '>')) and not NUM_RE.match(nxt):
                    cn = unesc(nxt)
                    i += 1
            # 银行 id
            if part == 1:
                head = (slot or '') + (group or '')
                first = '第一段第一句' in head
                bid = 'p1s1' if first else 'p1s2'
                label = '第一段 · 首句（问候 / 自我介绍）' if first else '第一段 · 第二句（表明来意）'
                typ = '通用'
            elif part == 2:
                if group.startswith('通用'):
                    bid, label, typ = 'p2s1', '第二段 · 通用首句（引出下文）', '通用'
                else:
                    name = group.replace('类', '')
                    eid = next((e for c, e in TYPE_MAP if c == name), 'other')
                    sn = re.search(r'第(.)句', slot)
                    si = {'二': 2, '三': 3, '四': 4}.get(sn.group(1) if sn else '', 2)
                    bid = 'p2_%s_s%d' % (eid, si)
                    label = '第二段 · %s类 第%s句' % (name, sn.group(1) if sn else '二')
                    typ = name
            else:
                bid, label, typ = 'p3', '第三段 · 收尾 / 客套', '收尾'
            if bid not in banks:
                banks[bid] = {'id': bid, 'part': part, 'type': typ, 'label': label, 'items': []}
                order.append(bid)
            cur = banks[bid]
            cur_item = {'en': '', 'cn': cn, 'raw': en}
            cur['items'].append(cur_item)
            continue
    # 占位符转换（保持登记顺序）
    ph_example = {}
    for bid in order:
        for it in banks[bid]['items']:
            it['en'] = conv(it['raw'], ph_example)
            del it['raw']
            for ex in it.get('ex', []):
                ex['en'] = conv(ex['en'], ph_example)
                ex['cn'] = conv(ex['cn'], ph_example)
            if it['cn']:
                it['cn'] = conv(it['cn'], ph_example)

    if UNMAPPED:
        print('⚠ 未映射的角色:', json.dumps(UNMAPPED, ensure_ascii=False))
        raise SystemExit('存在未映射占位符角色，请补到 PH 表')

    # 占位符图例：token → 中文角色；例句取首个含该 token 的句子
    ph_list = []
    for tok, cn in ph_example.items():
        eg = ''
        for bid in order:
            for it in banks[bid]['items']:
                if '{{' + tok + '}}' in it['en']:
                    eg = it['en']
                    break
            if eg:
                break
        ph_list.append([tok, cn, eg])

    # 补齐 md 缺的 4 类
    merge_extra(banks, order)

    # dump 模式：打印「md 原始顺序」的候选清单（供人工挑保留句），不写文件
    if 'dump' in sys.argv:
        for k in order:
            b = banks[k]
            print('=' * 96)
            print('### %s  (%d 句)' % (b['label'], len(b['items'])))
            for i, it in enumerate(b['items']):
                ex = ('｜示例' + it['ex'][0]['src']) if it.get('ex') else ''
                print('%2d%s %s' % (i, ex, it['en']))
        return

    # 按人工挑的保留清单删冗余（EXTRA.PRUNE：bankId → 保留的自然序号）
    pruned = 0
    for k in order:
        keep = EXTRA.PRUNE.get(k)
        if keep is None:
            continue
        b = banks[k]
        before = len(b['items'])
        b['items'] = [it for i, it in enumerate(b['items']) if i in keep]
        pruned += before - len(b['items'])
        if not b['items']:
            raise SystemExit('%s 被清空，检查 PRUNE' % k)
    if pruned:
        print('  按保留清单删去 %d 句冗余' % pruned)

    # 分层（必背 / 弹药）
    compute_layers([banks[k] for k in order])

    # 图例：扫描全部句子，补上补充类型里出现的新 token
    for k in order:
        for it in banks[k]['items']:
            for tok in re.findall(r'\{\{(.+?)\}\}', it['en']):
                if tok not in ph_example:
                    ph_example[tok] = EXTRA.EXTRA_TOKENS_CN.get(tok, tok)

    # 类型视图（10 类，顺序见 EXTRA.TYPE_ORDER）
    types = []
    for eid in EXTRA.TYPE_ORDER:
        bs = [b for b in ('p1s1', 'p2s1', 'p2_%s_s2' % eid, 'p2_%s_s3' % eid, 'p2_%s_s4' % eid, 'p3')
              if b in banks]
        if not bs:
            continue
        name = {'notice': '通知'}.get(eid)
        if not name:
            name = next((x['name'] for x in EXTRA.EXTRA_TYPES if x['id'] == eid), None)
        if not name:
            name = next(c for c, e in TYPE_MAP if e == eid) + '信'
        types.append({'id': eid, 'name': name, 'banks': bs})

    steps = [
        {'no': 1, 'name': '称呼（补充，原文未含）',
         'body': 'Dear Sir or Madam,（不认识对方）／ Dear Bob,（认识）／ Dear Mr. Smith,。顶格写，后面<b>用逗号</b>。'},
        {'no': 2, 'name': '第一段（2 句，约 25 词）',
         'body': '首句<b>问候 / 自我介绍</b>（I hope this message finds you well.…）＋ 第二句<b>表明来意</b>（I am writing to…）。'},
        {'no': 3, 'name': '第二段（2~4 句，约 55 词）',
         'body': '先用<b>通用首句</b>引出（To be more specific…），再按<b>信件类型</b>挑 2~3 句展开。这一段的句子可以跨类型混用。'},
        {'no': 4, 'name': '第三段（1~2 句，约 20 词）',
         'body': '客套收尾 / 期待回复（I would appreciate it very much if…）。'},
        {'no': 5, 'name': '落款（补充，原文未含）',
         'body': 'Yours sincerely,（正式）／ Best wishes,（朋友）＋ 换行写题目给的名字（Li Ming）。'},
    ]

    study = ('先自己写：拿功能句对着题目写一遍（写错也没关系），写完再让 AI 按题目要求改。'
             '越少依赖 AI，你越强。')

    data = {
        'meta': {
            'title': '小作文（应用文）功能句库',
            'desc': '英语二 A 节 · 应用文（书信 / 通知），约 100 词。下面按「第几句」收集了可直接套用的功能句；'
                    '{{ }} 包住的是按题目替换的槽位，词句本身不要动。',
            'note': '数据源：考研英语小作文功能句全集（用户提供）。第 1、5 步的称呼与落款原文未含，为本站补充。',
        },
        'steps': steps,
        'study': study,
        'notes': notes,
        'placeholders': ph_list,
        'banks': [banks[b] for b in order],
        'types': types,
        'guide': build_guide(),
        'decisions': EXTRA.DECISIONS,
        'teacher': EXTRA.TEACHER,
    }
    all_items = [it for b in data['banks'] for it in b['items']]

    def wc(s):
        return len([x for x in re.split(r'\s+', (s or '').strip()) if re.search(r'[A-Za-z0-9]', x)])

    def pick(tier):
        return [x for x in all_items if x.get('tier') == tier]

    core, musty = pick('core'), pick('must')
    data['stats'] = {
        'items': len(all_items), 'banks': len(data['banks']), 'types': len(types),
        'core': len(core), 'core_words': sum(wc(x['en']) for x in core),
        'must': len(musty), 'must_words': sum(wc(x['en']) for x in musty),
        'ammo': len(pick('ammo')),
        'freq3': sum(1 for x in all_items if x.get('freq') == 3),
        'guide': len(data['guide']),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(data, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    total = sum(len(b['items']) for b in data['banks'])
    print('写入 %s' % os.path.relpath(OUT, os.path.dirname(ROOT)))
    print('  句库 %d 组 / %d 句 | 占位符 %d 个 | 类型 %d 个 | 提示 %d 条'
          % (len(data['banks']), total, len(ph_list), len(types), len(notes)))
    s = data['stats']
    print('  ⭐⭐骨架 %d 句 / %d 词 ｜ ⭐必背 %d 句 / %d 词 ｜ 合计 %d 句 %d 词（≈ %.1f 词/天，30 天）'
          % (s['core'], s['core_words'], s['must'], s['must_words'],
             s['core'] + s['must'], s['core_words'] + s['must_words'],
             (s['core_words'] + s['must_words']) / 30.0))
    print('  ⚡弹药 %d 句 ｜ ★★★ %d 句 ｜ 适配表 %d 年 ｜ 类型 %d 个'
          % (s['ammo'], s['freq3'], s['guide'], s['types']))
    for b in data['banks']:
        print('    %-14s %-28s %d 句' % (b['id'], b['label'], len(b['items'])))


if __name__ == '__main__':
    main()
