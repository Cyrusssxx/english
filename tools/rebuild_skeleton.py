# -*- coding: utf-8 -*-
'''大作文模板「重置」（2026-09-15）：把骨架从「一整段套话」改成「最短框架 + 机制句池」。

设计理由（上帝视角）
  · 考研英二大作文只要三段：描述图（data）→ 解释为什么（reason）→ 评论（stance + 建议）。
    只有第一段是「图的题」，第二三段是自由发挥——所以第二三段不该背整段话。
  · 旧版问题：① 第三段骨架是两句空话（more than one side has to act / each has a different job），
    同义反复、零内容；② 第二段按话题拆 5 段，等于逼学生背 185 词，还要先给图表贴「经济/校园/文化」标签；
    ③ 静态首段第四句用 "By contrast"，只是「小的那几类」谈不上对比；④ 动态② 的 "only went from" 预设了
    快慢（2022 年农村其实涨得更快，只能临场改句）。
  · 新结构：必背降到 ~150 词——第一段 4 套短骨架（静态 / 单线 / 多线同向 / 一升一降，各 2~4 句），
    第二段 1 句引入 + 12 条机制句（现挑 3 条），第三段 立场句 + 主体句池 + 收束句。

用法：python tools/rebuild_skeleton.py    （幂等，靠 _skeleton_ver 标记）
'''
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, 'pwa', 'data', 'writing_templates.json')
VER = 'skel-2026-09-16'


def S(t, r):
    return [t, r]


def norm_struct(struct):
    """允许写成 [[片段, 片段]]（单句多包一层方括号）——自动剥掉，避免结构标注多一层"""
    if len(struct) == 1 and isinstance(struct[0], list) and struct[0] and isinstance(struct[0][0], list):
        return struct[0]
    return struct


def sent(en, cn, struct):
    return {'en': en, 'cn': cn, 'struct': norm_struct(struct)}


# ══════════ 一、第一段：4 套短骨架 ══════════
STATIC = [
    sent('The {{chart}} chart above clearly illustrates how {{topic}} is distributed.',
         '该 {{chart}} 图清晰地展示了 {{topic}} 的分布情况。',
         [[S('The {{chart}} chart above', 't'), S(' clearly illustrates', 'p'), S(' how {{topic}} is distributed', 'o'), S('.', '')]]),
    sent('{{item1}} takes the lead, accounting for {{percent1}}, followed by {{item2}} and {{item3}} at {{percent2}} and {{percent3}} respectively, while {{item4}} comes last at {{percent4}}.',
         '{{item1}} 遥遥领先，占 {{percent1}}；其后是 {{item2}} 和 {{item3}}，分别占 {{percent2}} 和 {{percent3}}；而 {{item4}} 位居最后，占 {{percent4}}。',
         [[S('{{item1}}', 't'), S(' takes the lead', 'p'), S(', accounting for {{percent1}}', 'o'), S(', followed by ', 'trans'),
           S('{{item2}} and {{item3}}', 't'), S(' at {{percent2}} and {{percent3}} respectively', 'o'), S(', while ', 'trans'),
           S('{{item4}}', 't'), S(' comes last at {{percent4}}', 'o'), S('.', '')]]),
]

DYN_OPEN = sent('The {{chart}} chart above clearly illustrates the changes in {{topic}} from {{time1}} to {{time2}}.',
                '该 {{chart}} 图清晰地展示了 {{time1}} 到 {{time2}} 期间 {{topic}} 的变化。',
                [[S('The {{chart}} chart above', 't'), S(' clearly illustrates', 'p'), S(' the changes in {{topic}}', 'o'), S(' from {{time1}} to {{time2}}', 'o'), S('.', '')]])

# ③ 的开头句自带「对比框架」（一升一降本来就有 sharp contrast）
DYN_OPEN3 = sent('The {{chart}} chart above clearly illustrates the sharp contrast in {{topic}} between {{item1}} and {{item2}} from {{time1}} to {{time2}}.',
                 '该 {{chart}} 图清晰地展示了 {{time1}} 到 {{time2}} 期间 {{topic}} 在 {{item1}} 与 {{item2}} 之间的鲜明反差。',
                 [[S('The {{chart}} chart above', 't'), S(' clearly illustrates', 'p'), S(' the sharp contrast in {{topic}}', 'o'), S(' between {{item1}} and {{item2}}', 'o'), S(' from {{time1}} to {{time2}}', 'o'), S('.', '')]])

DYN = [
    {'label': '① 一条线在走', 'years': '2013 · 2023',
     'en': DYN_OPEN['en'] + ' ' + 'During this period, it rose steadily from {{num1}} to {{num2}}, without any noticeable fall.',
     'cn': DYN_OPEN['cn'] + '在此期间，它由 {{num1}} 稳步升至 {{num2}}，全程没有明显回落。',
     'struct': [DYN_OPEN['struct'],
                [S('During this period', 'trans'), S(', it', 't'), S(' rose steadily', 'p'), S(' from {{num1}} to {{num2}}', 'o'), S(', without any noticeable fall', 'o'), S('.', '')]],
     'alts': {'rose steadily': 'climbed steadily / kept rising'},
     'demo': ('The bar chart above clearly illustrates the changes in the proportion of college students taking part-time jobs '
              'from freshman year to senior year. During this period, it rose steadily from 67.77% to 88.24%, without any noticeable fall.')},
    {'label': '② 两条都在涨', 'years': '2010 · 2017 · 2022',
     'en': DYN_OPEN['en'] + ' ' + 'During this period, {{item1}} rose sharply from {{num1}} to {{num2}}. By contrast, the figure for {{item2}} saw a modest increase, climbing from {{num3}} to {{num4}} over the same period.',
     'cn': DYN_OPEN['cn'] + '在此期间，{{item1}} 由 {{num1}} 大幅升至 {{num2}}。相比之下，{{item2}} 的数字增幅温和，由 {{num3}} 增至 {{num4}}。',
     'struct': [DYN_OPEN['struct'],
                [S('During this period', 'trans'), S(', {{item1}}', 't'), S(' rose sharply', 'p'), S(' from {{num1}} to {{num2}}', 'o'), S('.', '')],
                [S('By contrast', 'trans'), S(', the figure for {{item2}}', 't'), S(' saw', 'p'), S(' a modest increase', 'o'), S(', climbing from {{num3}} to {{num4}} over the same period', 'o'), S('.', '')]],
     'alts': {'rose sharply': 'rose dramatically / climbed quickly', 'By contrast': 'In contrast', 'saw a modest increase': 'saw only a slight rise', 'climbing from': 'rising from'},
     'demo': ('The bar chart above clearly illustrates the changes in mobile-phone subscriptions between developing and developed '
              'countries from 2000 to 2008. During this period, subscriptions in developing countries rose sharply from 0.5 billion '
              'to 4 billion. By contrast, the figure for developed countries saw a modest increase, climbing from 0.7 billion to '
              '1 billion over the same period.')},
    {'label': '③ 一升一降', 'years': '2011 · 2014 · 2019',
     'en': DYN_OPEN3['en'] + ' ' + 'During this period, {{item1}} rose sharply from {{num1}} to {{num2}}. By contrast, the figure for {{item2}} saw a steady decline, falling from {{num3}} to {{num4}}.',
     'cn': DYN_OPEN3['cn'] + '在此期间，{{item1}} 由 {{num1}} 大幅升至 {{num2}}。相比之下，{{item2}} 的数字稳步下降，由 {{num3}} 降至 {{num4}}。',
     'struct': [DYN_OPEN3['struct'],
                [S('During this period', 'trans'), S(', {{item1}}', 't'), S(' rose sharply', 'p'), S(' from {{num1}} to {{num2}}', 'o'), S('.', '')],
                [S('By contrast', 'trans'), S(', the figure for {{item2}}', 't'), S(' saw', 'p'), S(' a steady decline', 'o'), S(', falling from {{num3}} to {{num4}}', 'o'), S('.', '')]],
     'alts': {'sharp contrast': 'marked contrast / striking gap', 'rose sharply': 'rose dramatically', 'saw a steady decline': 'declined steadily', 'By contrast': 'In contrast'},
     'demo': ('The bar chart above clearly illustrates the sharp contrast in market share between Chinese and Japanese car brands '
              'from 2008 to 2009. During this period, Chinese brands rose sharply from 26% to 31%. By contrast, the figure for '
              'Japanese brands saw a steady decline, falling from 35% to 26%.')},
    {'label': '④ 先稳后急（图有分段就换这套）', 'years': '2013 · 2023',
     'en': DYN_OPEN['en'] + ' ' + 'From {{time1}} to {{time3}}, it rose steadily from {{num1}} to {{num3}}, and then climbed sharply to {{num2}}.',
     'cn': DYN_OPEN['cn'] + '{{time1}} 到 {{time3}} 期间，它由 {{num1}} 稳步升至 {{num3}}，随后急剧攀升至 {{num2}}。',
     'struct': [DYN_OPEN['struct'],
                [S('From {{time1}} to {{time3}}', 'o'), S(', it', 't'), S(' rose steadily', 'p'), S(' from {{num1}} to {{num3}}', 'o'),
                 S(', and then', 'trans'), S(' climbed sharply', 'p'), S(' to {{num2}}', 'o'), S('.', '')]],
     'alts': {'rose steadily': 'climbed steadily / kept rising', 'climbed sharply': 'surged / shot up'},
     'demo': ('The line chart above clearly illustrates the changes in the health literacy rate of Chinese residents from 2012 to 2021. '
              'From 2012 to 2015, it rose steadily from 8.80% to 10.25%, and then climbed sharply to 25.40%.')},
]

# ══════════ 二、第二段：1 句引入 + 机制句池 ══════════
# 万能开头句（2026-09-16 审计后定稿）：a combination of factors 不承诺条数，17 年全部成立
PARA2_SKEL = sent('This phenomenon can be attributed to a combination of factors.',
                  '这一现象是多种因素共同作用的结果。',
                  [[S('This phenomenon', 't'), S(' can be attributed to', 'p'), S(' a combination of factors', 'o'), S('.', '')]])
PARA2_SKEL['alts'] = {'can be attributed to': 'is largely attributable to（加长版）/ stems from',
                      'a combination of factors': 'two major factors（写 2 条）/ three major factors（写 3 条）/ several major factors（写 4 条）'}

MECH = [
    (3, '收入', 'As household incomes have grown, {{topic}} has moved from a luxury to an everyday necessity.',
     '随着家庭收入提高，{{topic}} 已从奢侈品变成日常必需。'),
    (3, '成本', 'Technology has cut the cost of {{topic}} and put it within reach of far more people.',
     '技术把 {{topic}} 的成本压了下来，让更多人够得着。'),
    (3, '便利', 'Online platforms and mobile payment have made {{topic}} quicker and easier to arrange.',
     '线上平台和移动支付让 {{topic}} 变得更快更方便。'),
    (3, '观念', 'People now judge {{topic}} by what it does for them rather than by what others think.',
     '人们现在看 {{topic}} 好不好用，而不是看别人怎么想。'),
    (3, '数据回扣', 'The figure for {{item1}} climbed from {{num1}} to {{num2}}, which matches the overall trend.',
     '{{item1}} 从 {{num1}} 升到 {{num2}}，与整体趋势一致。'),
    (2, '公共投入', 'Public spending on infrastructure has made {{topic}} far more widely available.',
     '公共基础设施投入让 {{topic}} 的覆盖面大大增加。'),
    (2, '城市化', 'Cities have absorbed millions of new residents, and demand for {{topic}} has grown with them.',
     '城市吸纳了大量新居民，{{topic}} 的需求随之增长。'),
    (2, '久坐', 'Sitting all day has turned {{topic}} from a hobby into a practical need.',
     '整天坐着，让 {{topic}} 从爱好变成了实际需要。'),
    (2, '职场时间', 'Longer working hours have made people value the little free time they have.',
     '工作时间变长，人们更看重仅有的空闲时间。'),
    (2, '学校', 'Schools now treat {{topic}} as part of the routine rather than an optional extra.',
     '学校现在把 {{topic}} 当成日常安排，而不是可选项。'),
    (2, '文化传承', 'Old traditions survive only when people find new ways to pass them on.',
     '老传统只有在被不断重新传递时才能活下来。'),
    (2, '人口结构', 'Longer life expectancy has changed how families plan for their later years.',
     '寿命延长，改变了家庭对晚年的安排。'),
    (2, '国产替代', 'Domestic producers have narrowed the quality gap, so buyers no longer pay a premium for foreign brands.',
     '国产品牌把质量差距缩小了，消费者不再为外国牌子多掏钱。'),
    (2, '职场流动', 'Young people change jobs far more often than their parents did, so loyalty works differently.',
     '年轻人换工作比父辈频繁得多，「忠诚」的含义已不同。'),
    (1, '就业门槛', 'Employers now look for experience as much as for grades.',
     '现在用人单位既看成绩，也看经验。'),
    (1, '生活节奏', 'Daily life has become more rushed, and {{topic}} is one of the few things people still fit in.',
     '生活节奏越来越快，{{topic}} 是少数还能挤进去的事。'),
]

# ══════════ 三、第三段：立场句 + 主体句池 + 收束句 ══════════
P3_POS = [
    sent('On balance, this is a positive trend worth welcoming.',
         '总体来看，这是值得欢迎的积极趋势。',
         [[S('On balance', 'trans'), S(', this', 't'), S(' is', 'p'), S(' a positive trend worth welcoming', 'o'), S('.', '')]]),
    sent('Given the momentum behind it, there is every reason to believe that this trend will continue in the years ahead.',
         '考虑到它背后的推动力，我们完全有理由相信，这一趋势将在未来几年持续下去。',
         [[S('Given the momentum behind it', 'trans'), S(', there', 't'), S(' is', 'p'), S(' every reason to believe that this trend will continue in the years ahead', 'o'), S('.', '')]]),
]
P3_NEG = [
    sent('On balance, the figures point to a problem worth taking seriously.',
         '总体来看，这些数据指向一个不容忽视的问题。',
         [[S('On balance', 'trans'), S(', the figures', 't'), S(' point to', 'p'), S(' a problem worth taking seriously', 'o'), S('.', '')]]),
    sent('Unless effective measures are taken, it may well get worse.',
         '若不采取有效措施，问题很可能进一步恶化。',
         [[S('Unless effective measures are taken', 'trans'), S(', it', 't'), S(' may well get worse', 'p'), S('.', '')]]),
]

# 高级衔接词（替代 First and foremost / Furthermore / To sum up 等烂大街写法；同篇不重样）
P2_LINKERS = [
    {'banned': 'First and foremost / The first one is', 'better': 'Primary among these is ... / The most immediate factor is ... / Chief among them is ...'},
    {'banned': 'Furthermore / What is more', 'better': 'Equally important, ... / Just as significant, ... / Beyond that, ...'},
    {'banned': 'So / As a result（焊因果）', 'better': 'which 从句：..., which has lowered the threshold for ...'},
]
P3_LINKERS = [
    {'banned': 'To sum up / In conclusion', 'better': 'On balance / Taking everything into account / Given the trends above'},
    {'banned': 'will rise（预测）', 'better': 'is predicted to rise / is set to rise / is estimated to stay stable'},
]

# 第二段拼装框架：引入句 → 高级衔接词 + 机制句（步骤固定，机制句从池里挑）
# 条数规则（2026-09-16 审计 17 年方案）：适配机制句全是 3~4 条、0 年两条；示范文实写 3 条(5 篇)/4 条(12 篇)
# → 引入句的条数词必须跟正文条数走；拿不准就用 a combination of factors（不承诺条数）
P2_FRAMEWORK = [
    {'en': 'This phenomenon can be attributed to a combination of factors.', 'trans': '这一现象是多种因素共同作用的结果。',
     'cn': '通用开头句：不承诺条数，17 年任何图表都成立；想点明条数再换 two / three / several major factors（见下方同义升级，须与正文条数一致）。'},
    {'en': 'Primary among these is + 机制句 ①', 'trans': '其中，首要的一条是……',
     'cn': '第 1 条：高级衔接词开头，接句池里最有力的原因（收入 / 成本 / 观念…）。'},
    {'en': 'Equally important, + 机制句 ②', 'trans': '同样重要的是，……',
     'cn': '第 2 条：换个衔接词、换个角度；句尾可用 which 从句焊因果（..., which has lowered the threshold for ...）。'},
    {'en': '（可选）A further driver is + 机制句 ③', 'trans': '（可选）另一个推动因素是……',
     'cn': '第 3 条想写就写（17 年的适配方案全是 3~4 条候选，写 3 条最稳）。'},
]

# 主体句池（沿用旧版并按更自然的口径重写两句；第一位是「通用档」）
SUBJ_POS = [
    (3, '观念', 'What matters most is whether families and schools treat {{topic}} as a normal part of life.', '最关键的是家庭和学校把它当成生活的正常一部分，而不是额外负担。'),
    (3, '政府', 'Government can fund public facilities so that {{topic}} is not limited to those who can pay.', '政府可以投入公共设施，让 {{topic}} 不只属于付得起钱的人。'),
    (3, '学校', 'Schools can build {{topic}} into daily routines instead of treating it as an extra.', '学校可以把 {{topic}} 纳入日常安排，而不是当成额外任务。'),
    (3, '家庭', 'Families matter most: children copy what adults do far more than what they are told.', '家庭最关键：孩子模仿大人怎么做，远多于听大人怎么说。'),
    (3, '企业/平台', 'Companies can make {{topic}} cheaper and easier to use, so that it reaches more people.', '企业可以把 {{topic}} 做得更便宜好用，让它覆盖更多人。'),
    (3, '媒体', 'Media should report on {{topic}} honestly, without exaggerating its benefits or its risks.', '媒体应如实报道 {{topic}}，既不夸大好处，也不夸大风险。'),
    (3, '个人', 'Individuals should choose what fits their own situation rather than follow the crowd.', '个人应按自身情况选择，而不是随大流。'),
    (2, '政府·长效', 'Clear rules and steady funding matter more than one-off campaigns.', '明确的规则和持续投入，比一次性活动更重要。'),
    (2, '平台·设计', 'Platforms should design simple, honest services instead of ones that hold users\u2019 attention for as long as possible.', '平台应把服务做得简单诚实，而不是想方设法长时间留住用户。'),
    (2, '媒体·展示', 'Documentaries and short videos can show how {{topic}} works in real life.', '纪录片和短视频能让人看到 {{topic}} 在现实中怎样运作。'),
    (2, '个人·习惯', 'Small habits matter: a little {{topic}} every day adds up over a year.', '小习惯很重要：每天一点 {{topic}}，一年下来就不一样。'),
]
SUBJ_NEG = [
    (3, '政府', 'Authorities should set clear limits and make sure they are actually enforced.', '政府应设定明确的上限，并确保真正执行。'),
    (3, '学校/家庭', 'Schools and families should warn young people before the habit takes hold.', '学校和家庭应在习惯养成之前提醒年轻人。'),
    (3, '家庭', 'Parents who ignore their own habits cannot expect children to do better.', '父母自己不注意，就别指望孩子做得好。'),
    (3, '企业/平台', 'Platforms should label or restrict content that encourages misuse.', '平台应对诱导滥用的内容加以标注或限制。'),
    (3, '媒体', 'Media should report the real risks rather than treat them as scare stories.', '媒体应报道真实风险，而不是把它当成吓人的故事。'),
    (3, '个人', 'Individuals need to watch their own habits instead of assuming they are safe.', '个人需要留意自己的习惯，而不是想当然认为没问题。'),
    (2, '企业·雇主', 'Employers should find out why experienced staff are the least satisfied, not just look at the overall figure.', '雇主应弄清为什么资深员工最不满意，而不是只看总体数字。'),
    (2, '企业·管理', 'A company that ignores this gap will lose the very people it most depends on.', '忽视这一差距的公司，会失去它最依赖的那批人。'),
    (2, '学校·课程', 'Classes on {{topic}} can help students tell safe use from misuse.', '关于 {{topic}} 的课程能帮学生分清正常使用和滥用。'),
    (2, '家庭·作息', 'A stable routine at home leaves less room for the problem to grow.', '家里作息稳定，问题就不容易滋生。'),
    (2, '个人·记录', 'Keeping a simple record of daily use is often enough to spot the problem early.', '简单记录一下每天的使用情况，往往就能及早发现问题。'),
]


def main():
    d = json.load(io.open(TPL, encoding='utf-8'))
    secs = d['sections']
    by_id = {s['id']: s for s in secs}

    def set_skeleton(sec, sents):
        sec['en'] = ' '.join(x['en'] for x in sents)
        sec['cn'] = ''.join(x['cn'] for x in sents)
        sec['en_struct'] = [x['struct'] for x in sents]

    # 第一段
    s = by_id['chart_static']
    set_skeleton(s, STATIC)
    s['alts'] = {'takes the lead': 'ranks first / comes top', 'comes last': 'ranks last / trails behind'}
    s['demo'] = ('The pie chart above clearly illustrates how the purposes of travel are distributed. '
                 'Appreciating the scenery takes the lead, accounting for 37%, followed by relieving pressure and other aims '
                 'at 33% and 15% respectively, while fostering independence comes last at 6%.')
    s['sentences'] = [
        {'en': 'Taken together, the three largest items make up {{percent total}}.', 'cn': '前三项加起来占 {{percent total}}。', 'freq': 3, 'tag': '合计'},
        {'en': 'The pattern is clear: a few items dominate the rest.', 'cn': '格局很清楚：少数几项占了大头。', 'freq': 2, 'tag': '集中度'},
        {'en': 'The gap between the largest and the smallest is wide.', 'cn': '最大项与最小项之间差距很大。', 'freq': 2, 'tag': '差距'},
        {'en': 'The figure varies sharply from group to group: it stands at {{percent1}} for {{item1}}, but falls to just {{percent3}} for {{item3}}.',
         'cn': '组与组之间差别悬殊：{{item1}} 高达 {{percent1}}，而 {{item3}} 只有 {{percent3}}。', 'freq': 3, 'tag': '交叉表·组间对比'},
    ]
    s = by_id['chart_dynamic']
    s['skeletons'] = DYN
    set_skeleton(s, [{'en': DYN[1]['en'], 'cn': DYN[1]['cn'], 'struct': DYN[1]['struct']}])
    s['en'] = DYN[1]['en']          # 兼容：sec['en'] 保留中间那套
    s['cn'] = DYN[1]['cn']
    s['en_struct'] = DYN[1]['struct']
    s['sentences'] = [
        {'en': 'The two moved in the same direction, but not at the same pace.', 'cn': '两者方向一致，但速度不同。', 'freq': 3, 'tag': '同向不同速'},
        {'en': 'The gap between the two widened over the period.', 'cn': '两者的差距在这一时期拉大了。', 'freq': 3, 'tag': '差距'},
        {'en': 'Growth was slow at first and then sped up.', 'cn': '增长起初缓慢，后来明显加快。', 'freq': 3, 'tag': '加速'},
        {'en': 'The first half of the period saw a steady rise, while the last few years brought a sharp acceleration.', 'cn': '前半段稳步上升，最后几年明显加速。', 'freq': 3, 'tag': '分段·先稳后急'},
        {'en': 'In the later years, {{item1}} climbed sharply while {{item2}} stayed almost flat.', 'cn': '后几年 {{item1}} 急剧上升，而 {{item2}} 几乎原地不动。', 'freq': 3, 'tag': '分段·后段分化'},
        {'en': 'From {{time1}} to {{time3}}, it rose steadily, and after {{time3}} it accelerated sharply to reach {{num2}}.', 'cn': '{{time1}} 到 {{time3}} 稳步上升，{{time3}} 之后明显加速，最终达到 {{num2}}。', 'freq': 2, 'tag': '分段·中点句'},
        {'en': 'The two moved in opposite directions.', 'cn': '两者朝相反的方向变化。', 'freq': 3, 'tag': '反差'},
        {'en': 'The figure more than doubled over the period.', 'cn': '这一数字在该时期翻了一倍多。', 'freq': 2, 'tag': '倍数'},
    ]

    # 第二段：合并成一段
    old2 = [x for x in secs if x['id'].startswith('para2_')]
    for x in old2:
        secs.remove(x)
    secs.insert(2, {
        'id': 'para2_why', 'title': '第二段 · 原因（机制句池）',
        'subtitle': '不背整段：1 句引入 + 从下面 16 条机制里挑 3 条（每条都是一个完整原因）',
        'group': secs[0].get('group', ''),
        'en': PARA2_SKEL['en'], 'cn': PARA2_SKEL['cn'], 'en_struct': [PARA2_SKEL['struct']],
        'alts': PARA2_SKEL['alts'],
        'linkers': P2_LINKERS,
        'framework': P2_FRAMEWORK,
        'priority': True,
        'sentences': [{'en': e, 'cn': c, 'freq': f, 'tag': t} for f, t, e, c in MECH],
        'phrases': [
            ['be attributed to', '归因于（P2 引入句）'],
            ['within reach', '够得着、负担得起'],
            ['value the little free time', '看重仅有的空闲时间'],
            ['a practical need', '实际需要'],
            ['pass them on', '把它传下去'],
            ['as much as', '和……一样（不只是）'],
        ],
        'tips': [
        "万能开头：a combination of factors 不承诺条数，什么年份都成立；想点明条数再换 two / three / several major factors（必须与正文条数一致）。第 1 条用「Primary among these is ...」，第 2 条换「Equally important, ...」——高级衔接词见下方 ✎ 行，同篇不重样，别用 First and foremost。",'引入句 10 词 + 机制句挑 3 条 ≈ 55~62 词。',
                 '每条机制句自带 {{槽位}}，改成这道题的具体对象即可；不要 16 条都写。',
                 '挑法：先看图表属于「钱变多 / 技术变便宜 / 人变忙 / 政策投入 / 观念变了」哪两类，再各挑一条。'],
    })

    # 第三段
    s = by_id['para3_positive']
    s['title'] = '第三段 · 正面版（立场 + 建议）'
    s['subtitle'] = '立场句 + 从主体句池挑 1~2 句 + 收束句'
    set_skeleton(s, P3_POS)
    s['alts'] = {'will continue': 'is predicted to continue / is set to continue', 'Given the momentum behind it': 'Considering the forces driving it'}
    s['linkers'] = P3_LINKERS
    s['sentences'] = [{'en': e, 'cn': c, 'freq': f, 'tag': t} for f, t, e, c in SUBJ_POS]
    s = by_id['para3_negative']
    s['title'] = '第三段 · 负面版（立场 + 对策）'
    s['subtitle'] = '立场句 + 从主体句池挑 1~2 句 + 收束句'
    set_skeleton(s, P3_NEG)
    s['alts'] = {'Unless effective measures are taken': 'If left unchecked / Without timely intervention', 'may well get worse': 'is unlikely to correct itself'}
    s['linkers'] = P3_LINKERS
    s['sentences'] = [{'en': e, 'cn': c, 'freq': f, 'tag': t} for f, t, e, c in SUBJ_NEG]

    # 顺序：第一段 → 第二段 → 第三段
    order = ['chart_static', 'chart_dynamic', 'para2_why', 'para3_positive', 'para3_negative']
    by_id = {s['id']: s for s in secs}     # 插入 para2_why 后重建索引
    d['sections'] = [by_id[i] for i in order]
    d['_skeleton_ver'] = VER

    # 适配表 hint 里引用的「三套走势骨架」标签同步
    for r in d['chart_guide']['table']:
        r['hint'] = (r['hint']
                     .replace('只写一条上升线，配 steady upward trend', '一条线 → 用「① 一条线在走」')
                     .replace('both rose steadily', '两条都在涨 → 用「② 两条都在涨」'))
    json.dump(d, io.open(TPL, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def wc(t):
        import re
        return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z]', x)])
    w_static = sum(wc(x['en']) for x in STATIC)
    w_dyn = [wc(x['en']) for x in DYN]
    core = w_static + max(w_dyn) + wc(PARA2_SKEL['en']) + sum(wc(x['en']) for x in P3_POS) + sum(wc(x['en']) for x in P3_NEG)
    print('骨架重置完成：%d 个段落' % len(d['sections']))
    print('  P1 静态 %d 词（2 句）｜ 动态 ①%d ②%d ③%d ④%d 词' % (w_static, w_dyn[0], w_dyn[1], w_dyn[2], w_dyn[3]))
    print('  P2 %d 词 + 机制句池 %d 条 ｜ P3 正 %d 词 / 负 %d 词 + 主体句池 %d+%d 条' % (
        wc(PARA2_SKEL['en']), len(MECH),
        sum(wc(x['en']) for x in P3_POS), sum(wc(x['en']) for x in P3_NEG), len(SUBJ_POS), len(SUBJ_NEG)))
    print('  → 必背估算 %d 词（静态 %d + 动态最长的② %d + P2 %d + P3 两版 %d）'
          % (core, w_static, max(w_dyn), wc(PARA2_SKEL['en']),
             sum(wc(x['en']) for x in P3_POS) + sum(wc(x['en']) for x in P3_NEG)))


if __name__ == '__main__':
    main()
