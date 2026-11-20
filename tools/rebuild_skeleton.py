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
     'cn': DYN_OPEN['cn'] + '在此期间，它从 {{num1}} 稳步升至 {{num2}}，始终没有明显回落。',
     'struct': [DYN_OPEN['struct'],
                [S('During this period', 'trans'), S(', it', 't'), S(' rose steadily', 'p'), S(' from {{num1}} to {{num2}}', 'o'), S(', without any noticeable fall', 'o'), S('.', '')]],
     'alts': {'rose steadily': 'climbed steadily / kept rising'},
     'demo': ('The bar chart above clearly illustrates the changes in the proportion of college students taking part-time jobs '
              'from freshman year to senior year. During this period, it rose steadily from 67.77% to 88.24%, without any noticeable fall.')},
    {'label': '② 两条都在涨', 'years': '2010 · 2017 · 2022',
     'en': DYN_OPEN['en'] + ' ' + 'During this period, {{item1}} rose sharply from {{num1}} to {{num2}}. By contrast, the figure for {{item2}} saw a modest increase, climbing from {{num3}} to {{num4}} over the same period.',
     'cn': DYN_OPEN['cn'] + '在此期间，{{item1}} 从 {{num1}} 急剧增至 {{num2}}。相比之下，{{item2}} 仅略有增加，从 {{num3}} 攀升至 {{num4}}。',
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
     'cn': DYN_OPEN3['cn'] + '在此期间，{{item1}} 从 {{num1}} 急剧增至 {{num2}}。相比之下，{{item2}} 则稳步下降，从 {{num3}} 降至 {{num4}}。',
     'struct': [DYN_OPEN3['struct'],
                [S('During this period', 'trans'), S(', {{item1}}', 't'), S(' rose sharply', 'p'), S(' from {{num1}} to {{num2}}', 'o'), S('.', '')],
                [S('By contrast', 'trans'), S(', the figure for {{item2}}', 't'), S(' saw', 'p'), S(' a steady decline', 'o'), S(', falling from {{num3}} to {{num4}}', 'o'), S('.', '')]],
     'alts': {'sharp contrast': 'marked contrast / striking gap', 'rose sharply': 'rose dramatically', 'saw a steady decline': 'declined steadily', 'By contrast': 'In contrast'},
     'demo': ('The bar chart above clearly illustrates the sharp contrast in market share between Chinese and Japanese car brands '
              'from 2008 to 2009. During this period, Chinese brands rose sharply from 26% to 31%. By contrast, the figure for '
              'Japanese brands saw a steady decline, falling from 35% to 26%.')},
    {'label': '④ 先稳后急（图有分段就换这套）', 'years': '2013 · 2023',
     'en': DYN_OPEN['en'] + ' ' + 'From {{time1}} to {{time3}}, it rose steadily from {{num1}} to {{num3}}, and then climbed sharply to {{num2}}.',
     'cn': DYN_OPEN['cn'] + '{{time1}} 到 {{time3}} 期间，它从 {{num1}} 稳步升至 {{num3}}，随后急剧攀升至 {{num2}}。',
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
                  '这一现象可归因于多种因素的综合作用。',
                  [[S('This phenomenon', 't'), S(' can be attributed to', 'p'), S(' a combination of factors', 'o'), S('.', '')]])
PARA2_SKEL['alts'] = {'can be attributed to': 'is largely attributable to（加长版）/ stems from',
                      'a combination of factors': 'two major factors（写 2 条）/ three major factors（写 3 条）/ several major factors（写 4 条）'}

MECH = [
    (3, '收入', 'As household incomes have grown, {{topic}} has moved from a luxury to an everyday necessity.',
     '随着家庭收入提高，{{topic}} 已从奢侈品变成日常必需。'),
    (3, '便利', 'Online platforms and mobile payment have made {{topic}} quicker and easier to arrange.',
     '线上平台和移动支付使 {{topic}} 变得更快、更方便。'),
    (3, '观念', 'People now judge {{topic}} by what it does for them rather than by what others think.',
     '如今，人们评判 {{topic}} 的标准是它能为自己带来什么，而非他人的看法。'),
    (3, '数据回扣', 'The figure for {{item1}} climbed from {{num1}} to {{num2}}, which matches the overall trend.',
     '{{item1}} 从 {{num1}} 升到 {{num2}}，与整体趋势一致。'),
    (2, '公共投入', 'Public spending on infrastructure has made {{topic}} far more widely available.',
     '基础设施方面的公共支出使 {{topic}} 更加普及。'),
    (2, '城市化', 'Cities have absorbed millions of new residents, and demand for {{topic}} has grown with them.',
     '随着城市吸纳了大量新居民，{{topic}} 的需求也随之增长。'),
    (2, '久坐', 'Sitting all day has turned {{topic}} from a hobby into a practical need.',
     '长期久坐使 {{topic}} 从爱好变成了切实的需求。'),
    (2, '职场时间', 'Longer working hours have made people value the little free time they have.',
     '工作时间变长，人们更看重仅有的空闲时间。'),
    (2, '学校', 'Schools now treat {{topic}} as part of the routine rather than an optional extra.',
     '学校现在将 {{topic}} 视为常规活动的一部分，而非可选的附加内容。'),
    (2, '文化传承', 'Old traditions survive only when people find new ways to pass them on.',
     '只有当人们找到新的方式来传承旧传统时，它们才能得以延续。'),
    (2, '人口结构', 'Longer life expectancy has changed how families plan for their later years.',
     '寿命的延长改变了家庭对晚年的规划。'),
    (2, '国产替代', 'Domestic producers have narrowed the quality gap, so buyers no longer pay a premium for foreign brands.',
     '国产品牌缩小了质量差距，消费者不再愿意为外国品牌支付溢价。'),
    (2, '职场流动', 'Young people change jobs far more often than their parents did, so loyalty works differently.',
     '如今的年轻人比父辈换工作频繁得多，「忠诚」的意义也随之改变。'),
    (1, '就业门槛', 'Employers now look for experience as much as for grades.',
     '如今用人单位既看重成绩，也看重经验。'),
    (1, '生活节奏', 'Daily life has become more rushed, and {{topic}} is one of the few things people still fit in.',
     '生活节奏不断加快，{{topic}} 成了人们为数不多还愿意抽出时间去做的事。'),
    # ── 2026-11-16 追加：押题预测五个方向（AI 教育 / 传统文化 / 教育公平 / 绿色消费 / 绿色出行）──
    # 追加在末尾、不插队：老句的索引与 apply_plan 的 f:tag 引用全部不动。
    # 排序交给 fit（见 P2_FIT）：押题句给 18~23，压过「观念 15」等通用句 → 前端自动排最前。
    (3, '科技普及', 'Advances in technology have made {{topic}} part of daily life rather than a privilege.',
     '科技的进步让 {{topic}} 从少数人的特权变成日常生活的一部分。'),
    (3, 'AI 教育', 'AI-powered tutoring gives students instant feedback that a single teacher can hardly provide.',
     '人工智能辅导能给学生即时反馈，这是单个老师很难做到的。'),
    (3, '教育公平', 'Shared online courses have begun to narrow the gap between urban and rural classrooms.',
     '共享网课已经开始缩小城乡课堂之间的差距。'),
    (3, '环保意识', 'Rising environmental awareness has turned {{topic}} into a mark of responsible living.',
     '环保意识的提升，使 {{topic}} 成为负责任生活的标志。'),
    (3, '绿色出行', 'Better public transport has made low-carbon travel a practical choice for young people.',
     '更完善的公共交通，让低碳出行成为年轻人切实可行的选择。'),
    (3, '文化新媒介', 'Short videos and self-media have opened a far easier route into {{topic}} for young people.',
     '短视频和自媒体，为年轻人了解 {{topic}} 打开了一条便捷得多的路径。'),
    # ── 2026-11-19 追加：负面题的「问题成因」──
    # 上面 21 条全是「为什么涨」（收入/技术/观念/投入），没有一条能解释「为什么出问题」。
    # 仍追加在末尾，不插队：老句 tag 引用与 apply_plan 的 f:tag 全部不动。
    (3, '逐利', 'Some providers put immediate profit first, which leaves quality and safety poorly managed.',
     '一些商家把眼前利润放在首位，导致质量与安全疏于管理。'),
    (3, '规则滞后', 'Rules have not kept pace with how quickly {{topic}} has spread.',
     '规则的更新速度，赶不上 {{topic}} 扩散的速度。'),
    # ── 2026-11-20 追加：从原范文提炼的「无槽」机制句 + 论证功能句 ──
    # 用户定调：① 纯原因句和论证功能句都要；② 一律不留 {{topic}} 槽（用 this shift / it 指代），
    # 换任何题都不会填错；③ fit 给 29~34 压过押题句（18~23）→ 前端自动置顶（「功能句前移」）。
    # 仍追加末尾、不插队：老句索引与 apply_plan 的 f:tag 引用全部不动。
    (3, '技术降本', 'Technology has steadily lowered the cost of what once required far more time and money.',
     '技术不断降低那些过去需要更多时间和金钱才能获得的东西的成本。'),
    (3, '供给响应', 'Suppliers have noticed the demand and moved quickly to meet it.',
     '供给方察觉到了需求，并迅速作出回应。'),
    (3, '需求叠加', 'Different groups have piled their needs on top of one another, and supply has struggled to keep pace.',
     '不同群体的需求层层叠加，供给已经难以跟上。'),
    (3, '递进', 'Not only has this shift changed how people spend their time, but it has also reshaped what they expect from daily life.',
     '这一变化不仅改变了人们支配时间的方式，也重塑了他们对日常生活的期待。'),
    (3, '转折', 'We cannot ignore the fact that it also brings problems that were less visible before.',
     '我们不能忽视，它同时也带来了此前不那么明显的问题。'),
    (3, '条件', 'Without proper guidance, people may follow the trend without understanding its costs.',
     '若缺乏恰当引导，人们可能盲目跟风，却不了解其中的代价。'),
    # ── 2026-11-20 第二批：原因句池扩容（从原范文 26 篇第二段逐条提炼）──
    # 用户澄清「机制句池要扩张」——这些是新的「为什么」，角度不与现有 23 条重复：
    # 现有已覆盖 收入/便利/观念/公共投入/城市化/久坐/职场时间/学校/文化传承/人口结构/
    # 国产替代/职场流动/就业门槛/生活节奏/科技普及/逐利/规则滞后，以下补空缺角度。
    (3, '竞争', 'Fiercer competition has made {{topic}} a way for people to keep their edge.',
     '竞争加剧，使 {{topic}} 成为人们保持优势的一种方式。'),
    (3, '示范效应', 'Seeing friends and colleagues take up {{topic}} makes others far more willing to follow.',
     '看到朋友和同事开始 {{topic}}，其他人也更愿意跟随。'),
    (3, '政策支持', 'Supportive policies have removed much of the risk from choosing {{topic}}.',
     '支持性政策消除了选择 {{topic}} 的大部分风险。'),
    (3, '信息传播', 'Information about {{topic}} now spreads faster than anyone can verify it.',
     '关于 {{topic}} 的信息传播速度，已经快过任何人核实的速度。'),
    (3, '健康意识', 'Growing concern about health has turned {{topic}} into a routine rather than an occasional choice.',
     '健康意识的增强，使 {{topic}} 从偶尔的选择变成日常习惯。'),
    (2, '家庭结构', 'Smaller households have changed what families expect from {{topic}}.',
     '家庭规模变小，改变了家庭对 {{topic}} 的期待。'),
    (2, '教育扩张', 'Longer years in education have raised demand for {{topic}}.',
     '受教育年限延长，推高了对 {{topic}} 的需求。'),
    (2, '营销', 'Careful marketing has made {{topic}} look like a natural part of modern life.',
     '精心设计的营销，使 {{topic}} 看起来像现代生活理所当然的一部分。'),
    # 负面题专用（为什么出问题）
    (2, '信息不对称', 'Consumers often cannot tell good {{topic}} from bad until it is too late.',
     '消费者往往直到为时已晚，才分得清 {{topic}} 的好坏。'),
    (2, '从众焦虑', 'The fear of missing out pushes people into {{topic}} before they have thought it through.',
     '害怕错过的焦虑，促使人们还没想清楚就投入 {{topic}}。'),
    (2, '短期行为', 'Short-term thinking leads people to ignore what {{topic}} costs in the long run.',
     '短期思维让人们忽视 {{topic}} 长期要付出的代价。'),
    # ── 2026-11-20 第三批：图表范文原句直取（NO6–15 第二段逐句提取，只挖槽 / 去具体化，不改措辞）──
    # 用户核对「到底有没有提取范文原句」——前两批是按角度重写，这一批才是原句。
    # 仍追加末尾、不插队；fit 给 29~40 压过押题句 → 前端置顶。
    (3, '技能更新', 'Changing job requirements push employees to update their knowledge and practical skills.',
     '岗位要求不断变化，促使员工更新知识和实用技能。'),                       # NO6 二段②
    (3, '使用成本', 'Lower running costs may encourage consumers to consider {{topic}}.',
     '更低的使用成本，可能促使消费者考虑 {{topic}}。'),               # NO7 二段③
    (3, '路径依赖', 'The lasting appeal of familiar ways keeps some people from switching.',
     '熟悉做法经久不衰的吸引力，让一些人迟迟不愿改变。'),                         # NO7 二段④
    (3, '供给多样', 'Different options serve different needs, so there is something for almost everyone.',
     '不同的选择满足不同需求，几乎人人都能找到合适的一种。'),               # NO8 二段④
    (3, '时间灵活', 'Longer opening hours make {{topic}} easier to fit into a busy day.',
     '更长的营业时间，让 {{topic}} 更容易塞进忙碌的一天。'),       # NO10 二段③
    (3, '运营效率', 'Improvements in distribution and management help businesses operate more efficiently.',
     '配送与管理的改善，帮助企业更高效地运转。'),                   # NO10 二段④
    (3, '公平权利', 'Equal participation requires accessible facilities.',
     '平等参与需要无障碍的设施。'),                     # NO11 二段②
    (3, '溢出效应', 'These facilities not only help the intended users but also benefit older people and others with limited mobility.',
     '这些设施不仅帮助目标使用者，也惠及老年人和行动不便的人。'),                           # NO11 二段④
    (3, '时效紧迫', 'Timely assistance can make a difference in an emergency.',
     '及时的帮助在紧急情况下能起决定作用。'),                 # NO12 二段②
    (3, '门槛降低', 'Courses open to communities and workplaces encourage more people to take part.',
     '向社区和职场开放的课程，鼓励更多人参与。'),                   # NO12 二段③
    (3, '机会供给', 'Developments in research, technology and business provide attractive opportunities.',
     '研究、技术和商业的发展提供了有吸引力的机会。'),                               # NO13 二段②
    (3, '互补优势', 'They can apply what they learned abroad while benefiting from local knowledge.',
     '他们能运用在海外所学，同时受益于本地经验。'),                         # NO13 二段③
]

# ── 第二段机制句池分类（2026-11-20）──
# 40 条按「考场怎么挑」分组：先挑万能逻辑句，再看题目属于哪一类。
# 组顺序 = 展示顺序；组内仍按 fit 降序。tag → 组名，未列出的 tag 会在构建时断言报错。
MECH_CAT = {
    # 万能逻辑：无槽，任何题都能接
    '数据回扣': '万能逻辑', '递进': '万能逻辑', '转折': '万能逻辑', '条件': '万能逻辑',
    # 押题热点：2027 预测命中主题
    'AI 教育': '押题热点', '教育公平': '押题热点', '绿色出行': '押题热点', '文化新媒介': '押题热点',
    # 经济与市场：为什么变普及 / 变便宜 / 卖得动
    '收入': '经济与市场', '便利': '经济与市场', '技术降本': '经济与市场',
    '国产替代': '经济与市场', '竞争': '经济与市场', '营销': '经济与市场',
    # 技术与信息
    '科技普及': '技术与信息', '信息传播': '技术与信息', '信息不对称': '技术与信息',
    # 观念与文化：人的看法变了
    '观念': '观念与文化', '健康意识': '观念与文化', '环保意识': '观念与文化',
    '文化传承': '观念与文化', '示范效应': '观念与文化',
    # 社会与人口：社会结构变了
    '人口结构': '社会与人口', '家庭结构': '社会与人口', '城市化': '社会与人口',
    '教育扩张': '社会与人口', '就业门槛': '社会与人口', '职场流动': '社会与人口',
    '职场时间': '社会与人口', '生活节奏': '社会与人口', '久坐': '社会与人口', '学校': '社会与人口',
    # 供给与政策
    '公共投入': '供给与政策', '供给响应': '供给与政策', '需求叠加': '供给与政策', '政策支持': '供给与政策',
    # 问题成因：负面题专用
    '逐利': '问题成因', '规则滞后': '问题成因', '从众焦虑': '问题成因', '短期行为': '问题成因',
    # 图表范文原句（2026-11-20 第三批）
    '技能更新': '社会与人口', '时间灵活': '经济与市场', '使用成本': '经济与市场',
    '运营效率': '经济与市场', '机会供给': '经济与市场',
    '路径依赖': '观念与文化', '公平权利': '观念与文化',
    '供给多样': '供给与政策', '门槛降低': '供给与政策',
    '溢出效应': '万能逻辑', '时效紧迫': '万能逻辑', '互补优势': '万能逻辑',
}
MECH_GROUPS = [
    ('万能逻辑', '先看这组：不带槽，任何题接上都成立'),
    ('押题热点', '2027 预测命中主题，考到直接用'),
    ('经济与市场', '钱变多 / 变便宜 / 买得到 / 有人在卖'),
    ('技术与信息', '技术推动，或信息跑得太快'),
    ('观念与文化', '人的看法变了，才愿意掏钱或参与'),
    ('社会与人口', '社会结构变了，需求跟着变'),
    ('供给与政策', '供给方扩产，或政策托底'),
    ('问题成因', '负面题专用：为什么出问题'),
]

# ══════════ 三、第三段：立场句 + 主体句池 + 收束句 ══════════
P3_POS = [
    sent('On balance, this is a positive trend worth welcoming.',
         '总的来说，这是一个值得欢迎的积极趋势。',
         [[S('On balance', 'trans'), S(', this', 't'), S(' is', 'p'), S(' a positive trend worth welcoming', 'o'), S('.', '')]]),
    sent('Given the momentum behind it, there is every reason to believe that it will continue in the years ahead.',
         '鉴于其背后的势头，我们有充分的理由相信，这一趋势将在未来几年继续发展。',
         [[S('Given the momentum behind it', 'trans'), S(', there', 't'), S(' is', 'p'), S(' every reason to believe that it will continue in the years ahead', 'o'), S('.', '')]]),
]

# 第三段拼装框架（与 P2 同款）：立场 → 主体/对策 → 收束（用户反馈「第三段怪怪的」= 缺拼装视图 + trend 重复）
P3_FW_POS = [
    {'en': 'On balance, this is a positive trend worth welcoming.', 'trans': '总的来说，这是一个值得欢迎的积极趋势。',
     'cn': '立场句：先亮态度，正面题直接用。'},
    {'en': 'To make the most of this trend, + 主体句 ①', 'trans': '要充分利用这一趋势，……',
     'cn': '主体句：谁来做——政府 / 学校 / 家庭 / 企业 / 媒体 / 个人，按题目挑 1~2 个；衔接词自带目的感，不用再写 Also。'},
    {'en': 'Given the momentum behind it, there is every reason to believe that it will continue in the years ahead.',
     'trans': '鉴于其背后的势头，我们有充分的理由相信，这一趋势将在未来几年继续发展。',
     'cn': '收束句：展望收尾，主体句写几条都接得住。'},
]
P3_FW_NEG = [
    {'en': 'On balance, the figures point to a problem worth taking seriously.', 'trans': '总的来说，这些数据指向一个值得认真对待的问题。',
     'cn': '立场句：负面题直接用。'},
    {'en': 'To reverse this trend, + 对策句 ①', 'trans': '要想扭转这一趋势，……',
     'cn': '对策句：谁来管——政府 / 学校 / 家庭 / 平台 / 个人，挑 1~2 个主体给对策。'},
    {'en': 'Unless effective measures are taken, it may well get worse.',
     'trans': '若不采取有效措施，问题很可能进一步恶化。',
     'cn': '收束句：警示收尾，与立场句的「问题」呼应。'},
]
# 中性版拼装框架：不表态，把判断权交给「怎么管」
P3_FW_MID = [
    {'en': 'On balance, what the figures reveal is a shift that deserves careful judgment rather than simple praise or blame.',
     'trans': '总的来说，这些数据揭示的是一种变化，它值得审慎判断，而非简单的褒贬。',
     'cn': '立场句：双面题 / 现状分布题用——既不吹好也不唱衰。'},
    {'en': 'To make the most of this shift, + 主体句 ①', 'trans': '要把握好这一变化，……',
     'cn': '主体句：正负两版的句池都能挑，中性题优先挑「观念 / 政府 / 学校 / 个人」这类不带褒贬的。'},
    {'en': 'Whether it proves to be a blessing or a burden depends on how well it is managed in the years ahead.',
     'trans': '它究竟成为福祉还是负担，取决于未来能否得到妥善管理。',
     'cn': '收束句：把结论落到「管理」上，避开对趋势本身下判断。'},
]
P3_NEG = [
    sent('On balance, the figures point to a problem worth taking seriously.',
         '总的来说，这些数据指向一个不容忽视的问题。',
         [[S('On balance', 'trans'), S(', the figures', 't'), S(' point to', 'p'), S(' a problem worth taking seriously', 'o'), S('.', '')]]),
    sent('Unless effective measures are taken, it may well get worse.',
         '若不采取有效措施，问题很可能进一步恶化。',
         [[S('Unless effective measures are taken', 'trans'), S(', it', 't'), S(' may well get worse', 'p'), S('.', '')]]),
]

# ── 第三档：中性版（2026-11-20 追加）──
# 为什么需要：正面版说「值得欢迎」、负面版说「问题严重」，但双面题（老龄化=寿命延长+养老压力）
# 和现状分布题（择业因素 / 线上线下占比）两边都不合。中性版不表态，只说「值得审慎判断」。
P3_MID = [
    sent('On balance, what the figures reveal is a shift that deserves careful judgment rather than simple praise or blame.',
         '总的来说，这些数据揭示的是一种变化，它值得审慎判断，而非简单的褒贬。',
         [[S('On balance', 'trans'), S(', what the figures reveal', 't'), S(' is', 'p'),
           S(' a shift that deserves careful judgment rather than simple praise or blame', 'o'), S('.', '')]]),
    sent('Whether it proves to be a blessing or a burden depends on how well it is managed in the years ahead.',
         '它究竟成为福祉还是负担，取决于未来能否得到妥善管理。',
         [[S('Whether it proves to be a blessing or a burden', 'o'), S(' depends on', 'p'),
           S(' how well it is managed in the years ahead', 'o'), S('.', '')]]),
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
    {'en': 'This phenomenon can be attributed to a combination of factors.', 'trans': '这一现象可归因于多种因素的综合作用。',
     'cn': '通用开头句：不承诺条数，17 年任何图表都成立；想点明条数再换 two / three / several major factors（见下方同义升级，须与正文条数一致）。'},
    {'en': 'Primary among these is + 机制句 ①', 'trans': '其中，首要的一条是……',
     'cn': '第 1 条：高级衔接词开头，接句池里最有力的原因（押题句 / 观念 / 收入…）。'},
    {'en': 'Equally important, + 机制句 ②', 'trans': '同样重要的是，……',
     'cn': '第 2 条：换个衔接词、换个角度；句尾可用 which 从句焊因果（..., which has lowered the threshold for ...）。'},
    {'en': '（可选）A further driver is + 机制句 ③', 'trans': '（可选）另一个推动因素是……',
     'cn': '第 3 条想写就写（17 年的适配方案全是 3~4 条候选，写 3 条最稳）。'},
]

# 句池适配年数（fit）：该 tag 在 tools/apply_plan.py 的 17 年方案里被实际引用的年份数——
# 用于句池展示排序（模板页/速记页「⚡ 弹药句池」按 fit 降序，把适配面广的句子排最前）。
# 数据来源：2026-09-21 全量统计（p1/p2/p3 的 f:tag 引用，跨 17 年方案）。
#   · P2 机制池：观念15 / 公共投入7 / 收入·便利·学校6 / 职场时间·职场流动4 / 城市化·就业门槛·久坐3 /
#     文化传承2 / 国产替代·成本·人口结构1 / 数据回扣·生活节奏0
#   · P3 正池：个人6 / 政府·长效5 / 政府·学校·观念4 / 企业·媒体·个人习惯3 / 家庭·平台设计2 / 媒体展示1
#   · P3 负池：个人·记录3（通用对策句，手动置前）/ 企业·雇主·企业·管理2（2012 真题用过）/ 个人1 / 其余0
P2_FIT = {'观念': 15, '收入': 6, '便利': 6, '学校': 6, '职场时间': 4, '职场流动': 4,
          '城市化': 3, '就业门槛': 3, '久坐': 3, '文化传承': 2, '国产替代': 1, '成本': 1,
          '人口结构': 1, '公共投入': 7, '数据回扣': 0, '生活节奏': 0,
          # 押题优先级（2026-11-16）：18~23 压过所有通用句，前端按 fit 降序自动置顶
          '科技普及': 23, 'AI 教育': 22, '教育公平': 21,
          '环保意识': 20, '绿色出行': 19, '文化新媒介': 18,
          # 负面题专用（2026-11-19）：只对「数据里出现低值项/负增长」的年份有用
          # （2012 满意度 / 2019 就业因素），可用年份少 → fit 压低，但负面题里是首选
          '逐利': 4, '规则滞后': 4,
          # 原范文提炼的通用功能句（2026-11-20）：无槽、任何题可接 → 排押题句之后、老通用句之前
          '递进': 17, '转折': 16, '条件': 15,
          '技术降本': 14, '供给响应': 13, '需求叠加': 12,
          # 原因句池扩容（2026-11-20 第二批）：新角度，不与已有 23 条重复
          '竞争': 11, '示范效应': 10, '政策支持': 9, '信息传播': 9,
          '健康意识': 8, '家庭结构': 8, '教育扩张': 7, '营销': 7,
          '信息不对称': 6, '从众焦虑': 6, '短期行为': 5,
          # 图表范文原句直取（2026-11-20 第三批）：原句措辞最稳 → fit 最高，压过押题句置顶
          '技能更新': 40, '使用成本': 39, '路径依赖': 38, '供给多样': 37,
          '时间灵活': 36, '运营效率': 35, '公平权利': 34, '溢出效应': 33,
          '时效紧迫': 32, '门槛降低': 31, '机会供给': 30, '互补优势': 29}
P3P_FIT = {'个人': 6, '政府·长效': 5, '政府': 4, '学校': 4, '观念': 4, '企业/平台': 3,
           '媒体': 3, '个人·习惯': 3, '家庭': 2, '平台·设计': 2, '媒体·展示': 1,
           # 原范文提炼的通用功能句（2026-11-20）：无槽、三段通用 → fit 最高，前端置顶
           '立场·中性': 19, '收尾·回扣': 18, '收尾·联合': 17, '收尾·条件': 16,
           # 图表范文第三段原句原型（2026-11-20 第三批）→ 再压一头
           '立场·重要性': 21, '分工·协同': 20}
P3N_FIT = {'个人·记录': 3, '企业·雇主': 2, '企业·管理': 2, '个人': 1,
           '政府': 0, '学校/家庭': 0, '家庭': 0, '企业/平台': 0, '媒体': 0,
           '学校·课程': 0, '家庭·作息': 0,
           '立场·中性': 19, '收尾·回扣': 18, '收尾·联合': 17, '收尾·条件': 16,
           '立场·重要性': 21, '分工·协同': 20}
# 中性版复用正负两版并集 → fit 取两边较大值
P3M_FIT = {}
for _k, _v in list(P3N_FIT.items()) + list(P3P_FIT.items()):
    P3M_FIT[_k] = max(P3M_FIT.get(_k, 0), _v)

# 主体句池（沿用旧版并按更自然的口径重写两句；第一位是「通用档」）
SUBJ_POS = [
    (3, '观念', 'What matters most is whether families and schools treat {{topic}} as a normal part of life.', '最关键的是，家庭和学校能否把 {{topic}} 当作日常生活的一部分。'),
    (3, '政府', 'Government can fund public facilities so that {{topic}} is not limited to those who can pay.', '政府可以为公共设施提供资金，使 {{topic}} 不再局限于那些有支付能力的人。'),
    (3, '学校', 'Schools can build {{topic}} into daily routines instead of treating it as an extra.', '学校可以把 {{topic}} 融入日常安排，而非当作额外的任务。'),
    (3, '家庭', 'Families matter most: children copy what adults do far more than what they are told.', '家庭的作用最为关键：孩子模仿的是大人的行动，而非说教。'),
    (3, '企业/平台', 'Companies can make {{topic}} cheaper and easier to use, so that it reaches more people.', '企业可以让 {{topic}} 更低价、更便捷，从而让更多人能够使用。'),
    (3, '媒体', 'Media should report on {{topic}} honestly, without exaggerating its benefits or its risks.', '媒体应如实报道 {{topic}}，既不夸大好处，也不夸大风险。'),
    (3, '个人', 'Individuals should choose what fits their own situation rather than follow the crowd.', '个人应按自身情况选择，而不是随大流。'),
    (2, '政府·长效', 'Clear rules and steady funding matter more than one-off campaigns.', '明确的规则和持续投入，比一次性活动更重要。'),
    (2, '平台·设计', 'Platforms should design simple, honest services instead of ones that hold users\u2019 attention for as long as possible.', '平台应设计简单、真诚的服务，而非想方设法让用户长时间停留。'),
    (2, '媒体·展示', 'Documentaries and short videos can show how {{topic}} works in real life.', '纪录片和短视频可以展示 {{topic}} 在现实生活中的运作方式。'),
    (2, '个人·习惯', 'Small habits matter: a little {{topic}} every day adds up over a year.', '小习惯很重要：每天一点 {{topic}}，日积月累一年下来就不一样。'),
]
SUBJ_NEG = [
    (3, '政府', 'Authorities should set clear limits and make sure they are actually enforced.', '政府应设定明确的上限，并确保真正执行。'),
    (3, '学校/家庭', 'Schools and families should warn young people before the habit takes hold.', '学校和家庭应在坏习惯形成之前提醒年轻人。'),
    (3, '家庭', 'Parents who ignore their own habits cannot expect children to do better.', '父母若放任自己的坏习惯，就别指望孩子能做得更好。'),
    (3, '企业/平台', 'Platforms should label or restrict content that encourages misuse.', '平台应对诱导滥用的内容加以标注或限制。'),
    (3, '媒体', 'Media should report the real risks rather than treat them as scare stories.', '媒体应报道真实风险，而不是把它当成吓人的故事。'),
    (3, '个人', 'Individuals need to watch their own habits instead of assuming they are safe.', '个人需要留意自己的习惯，而不是想当然认为没问题。'),
    (2, '企业·雇主', 'Employers should find out why experienced staff are the least satisfied, not just look at the overall figure.', '雇主应弄清为什么资深员工最不满意，而不是只看总体数字。'),
    (2, '企业·管理', 'A company that ignores this gap will lose the very people it most depends on.', '忽视这一差距的公司，会失去它最依赖的那批人。'),
    (2, '学校·课程', 'Classes on {{topic}} can help students tell safe use from misuse.', '关于 {{topic}} 的课程能帮学生分清正常使用和滥用。'),
    (2, '家庭·作息', 'A stable routine at home leaves less room for the problem to grow.', '家中规律的生活作息，会让问题更难滋生。'),
    (2, '个人·记录', 'Keeping a simple record of daily use is often enough to spot the problem early.', '简单记录一下每天的使用情况，往往就能及早发现问题。'),
]

# 第三段通用功能句（2026-11-20 从原范文提炼，无槽）：三个版本共用，fit 高 → 前端置顶
P3_EXTRA = [
    (3, '立场·中性', 'We should bear in mind that what is at stake goes far beyond the figures themselves.',
     '我们应当记住，真正关键的远不止这些数字本身。'),
    (3, '收尾·回扣', 'In this way, it can become a lasting source of benefit rather than a passing fashion.',
     '这样，它才能成为长久的益处来源，而非一时的风潮。'),
    (3, '收尾·联合', 'Only through the joint efforts of individuals and institutions can this potential be fully realized.',
     '只有个人与机构共同努力，这一潜力才能充分实现。'),
    (3, '收尾·条件', 'If these measures are implemented, a balance between development and protection will be within reach.',
     '若这些措施得以落实，发展与保护之间的平衡便指日可待。'),
    # 2026-11-20 第三批：图表范文第三段原句原型（NO6–15 首句 "We should bear in mind that X is of great
    # importance to Y" 与双主体对策 "A should …, while B should …"）——原句在池里没有对应，直取挖槽。
    (3, '立场·重要性', 'We should bear in mind that {{topic}} is of great importance to long-term development.',
     '我们应当记住，{{topic}} 对长远发展至关重要。'),
    (3, '分工·协同', 'Authorities can set the rules, but only providers and users can make them work in practice.',
     '政府可以制定规则，但只有供给方与使用者才能让规则真正落地。'),
]

# ── 第三段：三套骨架合并展示 + 共用一份句池（2026-11-20）──
# 用户反馈：正面/负面/中性三张卡各带一套句池，重复严重（EXTRA 4 条各出现 3 次、正 11 条 ×2、负 11 条 ×2）。
# 改成：三套骨架并列前移，句池只留一份 26 条（正 + 负 + EXTRA 去重）并分类。
# 关键：句池放 **pool_all** 而非 sentences——`build_apply_plan.parse_refs` 的 `f:tag` 按 tag 查下标
# 且要求 tag 唯一，合并池里「政府 / 家庭 / 企业/平台 / 媒体 / 个人」各有两条不同句子，塞进
# sentences 会直接让 17 篇套用示范的解析报错。sentences 保持原样（供 apply 取句），pool_all 只供前端展示。
P3_CAT = {
    # 首尾骨架：立场 + 收束，任何题都要
    '立场·中性': '立场与收尾', '收尾·回扣': '立场与收尾', '收尾·联合': '立场与收尾', '收尾·条件': '立场与收尾',
    '立场·重要性': '立场与收尾', '分工·协同': '政府与制度',
    # 责任主体
    '政府': '政府与制度', '政府·长效': '政府与制度',
    '学校': '学校与家庭', '学校/家庭': '学校与家庭', '学校·课程': '学校与家庭',
    '家庭': '学校与家庭', '家庭·作息': '学校与家庭',
    '企业/平台': '企业与平台', '企业·雇主': '企业与平台', '企业·管理': '企业与平台', '平台·设计': '企业与平台',
    '媒体': '媒体', '媒体·展示': '媒体',
    '个人': '个人', '个人·记录': '个人',
    # 软措施：改看法、改习惯
    '观念': '观念与习惯', '个人·习惯': '观念与习惯',
}
P3_GROUPS = [
    ('立场与收尾', '三段首尾骨架句，任何题都用得上'),
    ('政府与制度', '立法、投入、长效监管'),
    ('学校与家庭', '课程、作息、家长示范'),
    ('企业与平台', '产品设计、用工管理、平台规则'),
    ('媒体', '如实报道，不夸大不渲染'),
    ('个人', '自己的选择与记录'),
    ('观念与习惯', '看法变了、习惯改了，问题才真正解决'),
]


def _p3_card(label, years, sents, alts, demo):
    """把一套 P3 骨架转成 skeletons 卡片（与 chart_static 的骨架同构，前端零改动）"""
    return {'label': label, 'years': years,
            'en': ' '.join(x['en'] for x in sents),
            'cn': ''.join(x['cn'] for x in sents),
            'struct': [x['struct'] for x in sents],
            'alts': alts, 'demo': demo}


P3_SKELS = [
    _p3_card('① 正面版 · 趋势向好', '上升 / 普及类：2010 高数、2015 手机阅读、2017 博物馆、2023 老龄化',
             P3_POS,
             {'will continue': 'is predicted to continue / is set to continue',
              'Given the momentum behind it': 'Considering the forces driving it'},
             '拼法：立场 → 从句池挑 1~2 句对策（政府 / 学校 / 家庭 / 企业 / 媒体 / 个人）→ 收束。'),
    _p3_card('② 负面版 · 问题要治', '负面类：2012 员工满意度，或数据里出现低值项 / 负增长',
             P3_NEG,
             {'Unless effective measures are taken': 'If left unchecked / Without timely intervention',
              'may well get worse': 'is unlikely to correct itself'},
             '拼法：立场 → 挑 1~2 句对策（政府 / 学校 / 平台 / 个人）→ 警示收束。'),
    _p3_card('③ 中性版 · 只描述不表态', '双面题 / 现状分布题：老龄化、择业因素、线上线下占比',
             P3_MID,
             {'careful judgment': 'measured assessment / sober judgment',
              'praise or blame': 'celebration or alarm'},
             '拼法：立场 → 正负两版句池都能挑（中性题优先观念 / 政府 / 学校 / 个人）→ 落到「怎么管」。'),
]


def merge_p3_pool():
    """正 + 负 + EXTRA 去重成一份 26 条。
    同一 tag 在正/负两版里是两种语气（「个人」正=选适合自己的 / 负=管好自己的习惯），
    两条都保留，用 side 标出属于哪套骨架，前端在 tag 旁显示「正 / 负 / 通用」。"""
    seen, out = set(), []
    for side, rows in (('正', SUBJ_POS), ('负', SUBJ_NEG), ('通用', P3_EXTRA)):
        for f, t, e, c in rows:
            if e in seen:
                continue
            seen.add(e)
            out.append({'en': e, 'cn': c, 'freq': f, 'tag': t, 'side': side,
                        'fit': max(P3P_FIT.get(t, 0), P3N_FIT.get(t, 0)),
                        'cat': P3_CAT[t]})
    return out


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
        {'en': 'The pattern is clear: a few items dominate the rest.', 'cn': '整体格局清晰：少数几项占据了主导地位。', 'freq': 2, 'tag': '集中度'},
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
        {'en': 'The first half of the period saw a steady rise, while the last few years brought a sharp acceleration.', 'cn': '前半段稳步上升，最后几年明显加速。', 'freq': 3, 'tag': '分段·先稳后急'},
        {'en': 'In the later years, {{item1}} climbed sharply while {{item2}} stayed almost flat.', 'cn': '后几年 {{item1}} 急剧上升，而 {{item2}} 几乎原地不动。', 'freq': 3, 'tag': '分段·后段分化'},
        {'en': 'The two moved in opposite directions.', 'cn': '两者朝相反的方向变化。', 'freq': 3, 'tag': '反差'},
        {'en': 'The figure more than doubled over the period.', 'cn': '这一数字在该时期翻了一倍多。', 'freq': 2, 'tag': '倍数'},
    ]

    # 第二段：合并成一段
    old2 = [x for x in secs if x['id'].startswith('para2_')]
    for x in old2:
        secs.remove(x)
    secs.insert(2, {
        'id': 'para2_why', 'title': '第二段 · 原因（机制句池）',
        'subtitle': '不背整段：1 句引入 + 从下面 %d 条机制里挑 3 条（每条都是一个完整原因）' % len(MECH),
        'group': secs[0].get('group', ''),
        'en': PARA2_SKEL['en'], 'cn': PARA2_SKEL['cn'], 'en_struct': [PARA2_SKEL['struct']],
        'alts': PARA2_SKEL['alts'],
        'linkers': P2_LINKERS,
        'framework': P2_FRAMEWORK,
        'priority': True,
        'sentences': [{'en': e, 'cn': c, 'freq': f, 'tag': t, 'fit': P2_FIT.get(t, 0),
                       'cat': MECH_CAT[t]} for f, t, e, c in MECH],
        'pool_groups': [{'name': n, 'desc': d} for n, d in MECH_GROUPS],
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
                 '每条机制句自带 {{槽位}}，改成这道题的具体对象即可；不要 %d 条都写。' % len(MECH),
                 '挑法：先看图表属于「钱变多 / 技术变便宜 / 人变忙 / 政策投入 / 观念变了」哪两类，再各挑一条。'],
    })

    # 第三段
    s = by_id['para3_positive']
    s['title'] = '第三段 · 立场 + 对策（三套骨架选一）'
    s['subtitle'] = '正面 / 负面 / 中性三套骨架并列，下面一份句池三套通用'
    set_skeleton(s, P3_POS)
    s['alts'] = {'will continue': 'is predicted to continue / is set to continue', 'Given the momentum behind it': 'Considering the forces driving it'}
    s['linkers'] = P3_LINKERS
    s['framework'] = P3_FW_POS           # 保留给 apply 链路；页面用 skeletons 的 demo 讲拼法
    s['skeletons'] = P3_SKELS            # 三套骨架前移并列
    s['pool_all'] = merge_p3_pool()      # 26 条合并句池（仅展示；sentences 保持原样供 apply 取句）
    s['pool_groups'] = [{'name': n, 'desc': d} for n, d in P3_GROUPS]
    s['sentences'] = [{'en': e, 'cn': c, 'freq': f, 'tag': t, 'fit': P3P_FIT.get(t, 0)} for f, t, e, c in SUBJ_POS + P3_EXTRA]
    s['tips'] = ['三套骨架按题目极性选一套，不要混用：趋势向好选①，问题要治选②，说不清好坏（双面 / 现状分布）选③。',
                 '骨架只给首尾两句，中间对策从句池挑 1~2 句，拼起来 55~70 词。',
                 '同一条 tag 在正/负两版里是两种语气（如「个人」正面写「选适合自己的」、负面写「管好自己的习惯」），按骨架极性挑。']
    s = by_id['para3_negative']
    s['title'] = '第三段 · 负面版（立场 + 对策）'
    s['subtitle'] = '立场句 + 从主体句池挑 1~2 句 + 收束句'
    set_skeleton(s, P3_NEG)
    s['alts'] = {'Unless effective measures are taken': 'If left unchecked / Without timely intervention', 'may well get worse': 'is unlikely to correct itself'}
    s['linkers'] = P3_LINKERS
    s['framework'] = P3_FW_NEG
    s['sentences'] = [{'en': e, 'cn': c, 'freq': f, 'tag': t, 'fit': P3N_FIT.get(t, 0)} for f, t, e, c in SUBJ_NEG + P3_EXTRA]

    # 第三档：中性版（2026-11-20）——立场不表态，主体句复用正负两版并集
    mid = {x['id']: x for x in secs}.get('para3_neutral') or {}
    mid.update({
        'id': 'para3_neutral',
        'title': '第三段 · 中性版（立场 + 建议）',
        'subtitle': '双面题 / 现状分布题用：立场句不表态 + 从正负句池挑 1~2 句 + 收束句',
        'group': by_id['para3_positive'].get('group', ''),
        'priority': False,
        'linkers': P3_LINKERS,
        'framework': P3_FW_MID,
        'alts': {'careful judgment': 'measured assessment / sober judgment',
                 'praise or blame': 'celebration or alarm'},
        'tips': ['什么时候用：图表既说不上好也说不上坏——老龄化（寿命延长 + 养老压力）、择业因素、线上/线下占比。',
                 '正面版说「值得欢迎」、负面版说「问题严重」都不合适时，换这一版：只描述变化，把结论落到「怎么管」。',
                 '主体句直接从下面正负两版的并集里挑，语气中性的（观念 / 政府 / 学校 / 个人）优先。'],
    })
    set_skeleton(mid, P3_MID)
    mid['sentences'] = [{'en': e, 'cn': c, 'freq': f, 'tag': t, 'fit': P3M_FIT.get(t, 0)}
                        for f, t, e, c in SUBJ_POS + SUBJ_NEG + P3_EXTRA]
    if 'para3_neutral' not in {x['id'] for x in secs}:
        secs.append(mid)

    # 负面 / 中性两版只作骨架变体挂在主卡 skeletons 里，页面不再单独出卡（句池共用主卡那一份）。
    # 但 section 本身必须保留：apply_plan.py 用 p3=('para3_negative', ...) 按 id 取骨架句。
    by_id['para3_negative']['render_in'] = 'para3_positive'
    mid['render_in'] = 'para3_positive'

    # 顺序：第一段 → 第二段 → 第三段（正面 / 负面 / 中性）
    order = ['chart_static', 'chart_dynamic', 'para2_why', 'para3_positive', 'para3_negative', 'para3_neutral']
    by_id = {s['id']: s for s in secs}     # 插入 para2_why 后重建索引
    d['sections'] = [by_id[i] for i in order]
    d['_skeleton_ver'] = VER

    # 机制句池分类断言：漏归组 / 多余 tag / 空组都在这里先炸，别让前端落到「其他」
    _tags = [t for f, t, e, c in MECH]
    assert len(_tags) == len(set(_tags)), '机制句 tag 重复：%s' % [t for t in _tags if _tags.count(t) > 1]
    _missing = [t for t in _tags if t not in MECH_CAT]
    _extra = [t for t in MECH_CAT if t not in _tags]
    assert not _missing, '机制句未归组：%s' % _missing
    assert not _extra, 'MECH_CAT 有多余 tag（句池里没有）：%s' % _extra
    _names = [n for n, _ in MECH_GROUPS]
    assert len(_names) == len(set(_names)), 'MECH_GROUPS 组名重复'
    for _n in _names:
        assert any(MECH_CAT[t] == _n for t in _tags), '机制句分组「%s」是空组' % _n
    _assigned = sum(1 for t in _tags if MECH_CAT[t] in _names)
    assert _assigned == len(_tags), '有 %d 条机制句没落到展示分组' % (len(_tags) - _assigned)

    # 第三段：三套骨架 + 一份合并句池的断言
    _p3 = by_id['para3_positive']
    assert len(_p3['skeletons']) == 3, '第三段骨架应 3 套，实际 %d' % len(_p3['skeletons'])
    _p3tags = [t for f, t, e, c in SUBJ_POS + SUBJ_NEG + P3_EXTRA]
    _p3miss = [t for t in _p3tags if t not in P3_CAT]
    assert not _p3miss, '第三段句未归组：%s' % _p3miss
    _pool = _p3['pool_all']
    assert len({x['en'] for x in _pool}) == len(_pool), '合并句池有重复句'
    assert len(_pool) == len({e for f, t, e, c in SUBJ_POS + SUBJ_NEG + P3_EXTRA}), '合并句池条数不对'
    for _n, _ in P3_GROUPS:
        assert any(x['cat'] == _n for x in _pool), '第三段分组「%s」是空组' % _n
    assert all(x['cat'] in {n for n, _ in P3_GROUPS} for x in _pool), '有句子落到未定义的组'
    # 三套骨架拼回去必须与各段 en 一致（防止 _p3_card 写错）
    for _i, (_sk, _src) in enumerate(zip(_p3['skeletons'], (P3_POS, P3_NEG, P3_MID))):
        assert _sk['en'] == ' '.join(x['en'] for x in _src), '第 %d 套骨架 en 拼回不一致' % (_i + 1)
    assert _p3.get('render_in') is None and by_id['para3_negative'].get('render_in') == 'para3_positive'

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
