# -*- coding: utf-8 -*-
"""押题范文生成器（26 篇：大作文 18 + 小作文 8）。

规则（用户 2026-11-20 定，2026-11-20 二次修订）：
  · 段数与结构一律按用户的作文模板：首段描述数据/图画 → 第二段「引入句 + 三条原因」
    （First / Equally important / Beyond that）→ 第三段「立场句 + 2~3 条对策 + 收尾句」。
  · 单图表 5 篇：首段也用模板骨架句（{{percent}} 等槽位写死为真题数值）。
  · 图画 / 双图表 13 篇：首段保留原题描述原句（只配中文），二三段按模板结构重写。
  · 每句 en/cn 成对存进 yati.json 的 blocks[].sents；中文为人工译文，
    要求准确、完整、自然——不允许把英文原样塞进 cn，也不允许逐词硬拼。
  · 第二段的三条原因、第三段的对策按题写成能站得住的内容（模板给的只是句式与衔接词），
    避免「Public spending has made 人口老龄化 widely available」这类填槽错位。

真源：本文件。数据只由本文件生成为 pwa/data/yati.json，不要手改 JSON。
幂等：重复运行得到相同结果。

用法：python tools/build_yati_template.py
"""
import json, os, io, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWA = os.path.join(ROOT, 'pwa')
YATI = os.path.join(PWA, 'data', 'yati.json')

# ── 复用「套用示范」的取句引擎：从模板句池按 tag 取原句 + 填槽 + 主谓一致 ──
# 保证押题范文每一句都是用户自己背过的模板原句，而不是另写的新句。
import importlib.util
_spec = importlib.util.spec_from_file_location('baf', os.path.join(ROOT, 'tools', 'build_apply_from_templates.py'))
BAF = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(BAF)
TPL = BAF.load_templates()
_spec2 = importlib.util.spec_from_file_location('ytplan', os.path.join(ROOT, 'tools', 'yati_tpl_plan.py'))
YPLAN = importlib.util.module_from_spec(_spec2); _spec2.loader.exec_module(YPLAN)
TPLAN = YPLAN.PLAN

_TPL_RAW = json.load(io.open(os.path.join(PWA, 'data', 'writing_templates.json'), encoding='utf-8'))
def _tag_index(sid):
    sec = next(x for x in _TPL_RAW['sections'] if x['id'] == sid)
    return {x['tag']: i + 1 for i, x in enumerate(sec.get('sentences', []))}
IDX = {sid: _tag_index(sid) for sid in ('para2_why', 'para3_positive', 'para3_negative')}

# P2 三条机制句的骨架衔接词（用户选「骨架那套」，去掉套用示范里的 First）
# Primary among these is / A further driver is 后接完整句需 that；Equally important 是副词短语直接接句。
P2_LINK = [
    ('Primary among these is that ', '首要的是，'),
    ('Equally important, ', '同样重要的是，'),
    ('A further driver is that ', '另一个推动因素是，'),
]
# that 从句里的首词一律小写（这些开头词都不是专有名词）；真正的专有名词才保留大写
# 首词已是小写或以缩写开头（AI-...）时不降格；其余开头词降格到 that 从句里
def _lower_first(en):
    w = en.split()[0]
    if w[:2].isupper():        # AI-powered 等缩写
        return en
    return w[0].lower() + w[1:] + en[len(w):]

_PLURAL_TOPICS = {'AI tools', 'new energy vehicles', 'convenience stores', 'online and offline sales'}
def _fix_topic_verb(en, topic):
    """topic 在从句里作主语且为复数时，把紧跟的 has/is 改 have/are。
       只改「topic + has/is」前面不是介词（for/by/of/with）的情况——那些位置 topic 是宾语，谓语另有所指。"""
    if topic not in _PLURAL_TOPICS:
        return en
    t = re.escape(topic)
    # 负向前瞻：前面是 "for "/"in " 等介词时不改（宾语位置）
    en = re.sub(r'(?<!for )(?<!in )(?<!of )(?<!with )\b(' + t + r')\s+has\b', r'\1 have', en)
    en = re.sub(r'(?<!for )(?<!in )(?<!of )(?<!with )\b(' + t + r')\s+is\b', r'\1 are', en)
    return en

def _pick_by_tags(sid, tags, slots, slots_cn, pl=None):
    out = []
    topic = slots.get('topic', '')
    for tag in tags:
        n = IDX[sid].get(tag)
        if n is None:
            raise SystemExit('tag 不在池 %s: %s' % (sid, tag))
        en = BAF.pick(TPL[sid], [('f', n)], slots, 'en')[0]
        cn = BAF.pick(TPL[sid], [('f', n)], slots_cn, 'cn')[0]
        en = _fix_topic_verb(en, topic)
        out.append((en, cn))
    return out

def build_p2_p3(no):
    p = TPLAN[no]
    stance = p['stance']
    slots2, slots2cn = {'topic': p['topic2']}, {'topic': p['topic2cn']}
    slots3, slots3cn = {'topic': p['topic3']}, {'topic': p['topic3cn']}
    # 不传 pl：这些机制句里 topic 都作宾语（demand for {{topic}} has grown / made {{topic}} ...），
    # 句池原句的主谓本身正确；传 pl 会把宾语后面的 has 误改成 have。
    why = _pick_by_tags('para2_why', p['why'], slots2, slots2cn, [])
    p2 = [(P2_LINK[i][0] + _lower_first(en), P2_LINK[i][1] + cn) for i, (en, cn) in enumerate(why)]
    psid = 'para3_positive' if stance == 'pos' else 'para3_negative'
    dos = _pick_by_tags(psid, p['do'], slots3, slots3cn, [])
    p3 = [(BAF.finalize(en, slots3, []), BAF.tighten_cn(cn)) for en, cn in dos]
    return p2, p3

with io.open(YATI, encoding='utf-8') as f:
    Y = json.load(f)

# ── 模板固定句（与 writing_templates.json 的 para2_why 引入句 / para3_* 立场收尾句一致）──
PARA2_INTRO = ('This phenomenon can be attributed to a combination of factors.',
               '这一现象是多种因素共同作用的结果。')
P3_OPEN_POS = ('On balance, this is a positive trend worth welcoming.',
               '总体来看，这是一个值得肯定的积极趋势。')
P3_CLOSE_POS = ('Given the momentum behind it, there is every reason to believe that it will continue in the years ahead.',
                '鉴于其背后的势头，我们有充分理由相信，这一趋势在未来几年仍会延续。')
P3_OPEN_NEG = ('On balance, the figures point to a problem worth taking seriously.',
               '总体来看，这些数据指向一个不容忽视的问题。')
P3_CLOSE_NEG = ('Unless effective measures are taken, it may well get worse.',
                '若不采取有效措施，情况很可能进一步恶化。')

# 各篇立场：pos = 趋势值得肯定；neg = 问题需要重视
STANCE_TYPE = {
    1: 'neg', 2: 'neg', 3: 'neg', 4: 'neg', 5: 'neg',
    6: 'pos', 7: 'pos', 8: 'pos', 9: 'pos', 10: 'pos',
    11: 'pos', 12: 'pos', 13: 'pos', 14: 'neg', 15: 'pos',
    16: 'pos', 17: 'pos', 18: 'neg',
}

# ── 首段（P1） ───────────────────────────────────────────────
PLAN_P1 = {
    6: [
        ('The bar chart above clearly illustrates how the purposes of continuing education among working people are distributed.',
         '该柱状图清晰地展示了在职群体参加继续教育的目的分布情况。'),
        ('Improving current job skills takes the lead, accounting for 65%, followed by learning about new fields and developing personal interests at 48% and 37% respectively, while obtaining qualifications comes last at 26%.',
         '提升现有岗位技能遥遥领先，占 65%；其后是学习新领域和发展个人兴趣，分别占 48% 和 37%；而获得文凭位居最后，占 26%。'),
        ('Taken together, the three largest items make up 150%.',
         '前三项加起来占 150%。'),
    ],
    7: [
        ('The line chart above clearly illustrates the changes in domestic sales of conventional and new energy vehicles from January to June 2025.',
         '该折线图清晰地展示了 2025 年 1 月至 6 月燃油车与新能源汽车国内销量的变化。'),
        ('Sales of new energy vehicles rose from 0.79 million to 1.12 million, while the figure for conventional vehicles fluctuated and peaked at 1.33 million in March.',
         '新能源汽车销量从 79 万辆增至 112 万辆，而燃油车销量则起伏波动，在 3 月达到 133 万辆的峰值。'),
        ('The two moved in the same direction, but not at the same pace.',
         '两者方向一致，但速度不同。'),
    ],
    8: [
        ('The chart above clearly illustrates the changes in daily transport choices in a city from 2015 to 2021.',
         '该图清晰地展示了 2015 年至 2021 年某市居民日常出行方式的变化。'),
        ('The proportion of residents choosing buses fell from just over 50% to under 30%, while the shares for ride-hailing services and shared bicycles rose to approximately a quarter each.',
         '选择公交的居民比例从略高于 50% 降至不足 30%，而网约车和共享单车的占比各自升至约四分之一。'),
        ('The two moved in opposite directions.',
         '两者朝相反的方向变化。'),
    ],
    9: [
        ('The bar chart above clearly illustrates how the factors considered by university students when choosing a job are distributed.',
         '该柱状图清晰地展示了大学生择业时考虑的各项因素的分布情况。'),
        ('Personal development prospects take the lead, accounting for 65%, followed by pay and company reputation at 53% and 31% respectively, while personal interests and the working environment come last at 22% and 9%.',
         '个人发展前景遥遥领先，占 65%；其后是薪酬和公司声誉，分别占 53% 和 31%；而个人兴趣和工作环境位居最后，占 22% 和 9%。'),
        ('The gap between the largest and the smallest is wide.',
         '最大项与最小项之间差距很大。'),
    ],
    10: [
        ('The line chart above clearly illustrates the growth in the number of convenience stores in China from 2015 to 2023.',
         '该折线图清晰地展示了 2015 年至 2023 年全国便利店门店数量的增长。'),
        ('The total rose from roughly 90,000 to approximately 320,000, and the first half of the period saw a steady rise while the last few years brought a sharp acceleration.',
         '门店总数从约 9 万家增至约 32 万家；前半段稳步上升，最后几年明显加速。'),
        ('The figure more than doubled over the period.',
         '这一数字在该时期翻了一倍多。'),
    ],
    11: [
        ('The cartoon above depicts a wheelchair user approaching a public building by an accessible route, while the chart illustrates improvements in accessibility.',
         '上图描绘了一名轮椅使用者沿无障碍通道走向一栋公共建筑，而旁边的图表则显示了无障碍环境的改善。'),
        ('The proportion of public places with accessible routes in a city rose steadily from 56% in 2021 to 85% in 2025.',
         '某市配备无障碍通道的公共场所比例从 2021 年的 56% 稳步升至 2025 年的 85%。'),
        ('Together, the two images highlight progress toward a more inclusive society.',
         '两幅材料共同凸显了社会走向包容的进步。'),
    ],
    12: [
        ('The cartoon above depicts a person teaching others a basic first-aid skill, while the chart illustrates growing participation in first-aid training.',
         '上图描绘了一个人向他人传授基本急救技能，下图则展示了急救培训参与度的提升。'),
        ('In a city, the proportion of residents aged 18 to 60 who received such training increased steadily from 9% in 2021 to 32% in 2025.',
         '某市 18 至 60 岁居民中接受过此类培训的比例，从 2021 年的 9% 稳步升至 2025 年的 32%。'),
        ('These materials highlight the spread of practical knowledge of emergency response.',
         '这些材料凸显了应急处置实用知识的普及。'),
    ],
    13: [
        ('The cartoon above depicts overseas students returning to China, while the chart below illustrates the growth in their numbers.',
         '上图描绘了留学人员回国，下图则展示了回国人数的增长。'),
        ('The annual number of returning students increased from 134,800 in 2010 to 600,000 in 2019, rising to more than four times its initial level.',
         '年度回国人数从 2010 年的 13.48 万增至 2019 年的 60 万，达到最初水平的四倍多。'),
        ('Together, the materials highlight the growing appeal of returning home after studying abroad.',
         '两则材料共同凸显了留学后回国发展的吸引力日益增强。'),
    ],
    14: [
        ('The charts above illustrate changes in life expectancy and population aging in China.',
         '以上两幅图展示了中国人均预期寿命与人口老龄化的变化。'),
        ('Average life expectancy rose from 72.54 years in 2004 to 79 years in 2024.',
         '人均预期寿命从 2004 年的 72.54 岁升至 2024 年的 79 岁。'),
        ('Meanwhile, the proportion of people aged 60 and above increased from 10.97% to 22%, slightly more than doubling.',
         '与此同时，60 岁及以上人口比例从 10.97% 升至 22%，略高于翻倍。'),
        ('Taken together, the two trends describe a society that lives longer and grows older at the same time.',
         '综合来看，这两组趋势所描述的，是一个寿命更长、同时老得更快的社会。'),
    ],
    15: [
        ('The pie charts above illustrate the shares of online and offline ice cream sales in China in 2020 and 2021.',
         '以上饼图展示了 2020 年与 2021 年中国冰激凌线上与线下销售的占比。'),
        ('The online share rose from 5% to 20%, while the offline share fell from 95% to 80%.',
         '线上占比从 5% 升至 20%，而线下占比从 95% 降至 80%。'),
        ('Although online sales gained 15 percentage points, offline purchases remained dominant.',
         '尽管线上占比提高了 15 个百分点，线下购买仍占主导。'),
    ],
    1: [
        ('The cartoon above presents us with a thought-provoking scene: a student is delighted with an AI tool that has generated answers to his homework.',
         '上图为我们展现了一个发人深省的场景：一名学生因为 AI 工具帮他写出了作业答案而沾沾自喜。'),
        ('The caption suggests that the assignment is already complete.',
         '图下文字暗示，作业已经完成了。'),
        ('The drawing invites us to reflect on whether finishing a task necessarily means learning something.',
         '这幅画促使我们思考：完成任务是否必然意味着学到了东西。'),
    ],
    2: [
        ('As is symbolically depicted in the cartoon above, a father sits beside his son but keeps his eyes on his mobile phone.',
         '正如上图所象征性描绘的，一位父亲坐在儿子身边，眼睛却始终盯着手机。'),
        ('The boy asks whether his father is listening.',
         '男孩问父亲有没有在听他说话。'),
        ('The caption beneath the drawing reminds us that being physically present does not necessarily mean providing real companionship.',
         '图画下方的文字提醒我们，人在身边并不等于真正的陪伴。'),
    ],
    3: [
        ('Depicted in the picture above is a scene that strikes us as both familiar and thought-provoking: a man sits at a desk with his head lowered, surrounded by documents and reminders.',
         '上图描绘的场景既熟悉又发人深省：一名男子埋首于书桌前，四周堆满了文件和待办提醒。'),
        ('The word "pressure" appears prominently above him.',
         '他头顶上方醒目地写着「压力」二字。'),
        ('The drawing highlights the burden that excessive stress can place on daily life.',
         '这幅画凸显了过度压力给日常生活带来的负担。'),
    ],
    4: [
        ('The cartoon above presents us with a thought-provoking scene: a person stands beside a pile of boxes and wonders why buying one gift requires so much packaging.',
         '上图为我们展现了一个发人深省的场景：一个人站在一堆包装盒旁，困惑为什么买一件礼物需要这么多包装。'),
        ('The contrast between the small purchase and the large amount of wrapping highlights the problem of excessive packaging.',
         '小小的商品与大量包装之间的反差，凸显了过度包装的问题。'),
    ],
    5: [
        ('As is symbolically depicted in the cartoon above, a confused man faces a computer surrounded by conflicting messages.',
         '正如上图所象征性描绘的，一个困惑的人面对着电脑，四周充斥着相互矛盾的信息。'),
        ('The caption points to the difficulty of distinguishing reliable online information from falsehoods.',
         '图下文字指出了辨别可靠网络信息与虚假信息的困难。'),
        ('The drawing raises an important question about honesty and judgment in the digital age.',
         '这幅画提出了一个关于数字时代诚信与判断力的重要问题。'),
    ],
    16: [
        ('The pictures above present us with thought-provoking scenes of traditional Chinese art being passed on.',
         '以上两幅图为我们展现了中国传统艺术得以传承的动人场景。'),
        ('In the first picture, an older artist demonstrates a traditional skill to a young learner.',
         '第一幅图中，一位老艺人向年轻学习者演示传统技艺。'),
        ('In the second, the younger generation shares and practices the art.',
         '第二幅图中，年轻一代分享并实践这门艺术。'),
    ],
    17: [
        ('The pictures above present two considerations when choosing a major.',
         '以上两幅图呈现了专业选择时的两种考量。'),
        ('In the first, a student is attracted by strong market demand and promising career prospects.',
         '第一幅图中，一名学生被强劲的市场需求和良好的职业前景所吸引。'),
        ('In the second, another student expresses enthusiasm for a particular subject.',
         '第二幅图中，另一名学生表达了对某一学科的浓厚兴趣。'),
    ],
    18: [
        ('The pictures above present a striking contrast between a scenic area in the past and the same place today.',
         '以上两幅图呈现了某景区过去与今天的鲜明反差。'),
        ('The earlier scene features a peaceful natural landscape, whereas the later one shows crowded tourist facilities, numerous boats and scattered rubbish.',
         '早先的画面是宁静的自然景观，而如今却是拥挤的旅游设施、众多游船和散落的垃圾。'),
        ('The contrast highlights the environmental cost of poorly managed tourism.',
         '这一反差凸显了管理不善的旅游业所付出的环境代价。'),
    ],
}

# ── 第二段原因 / 第三段对策 ──────────────────────────────────
# P2/P3 已改由上方 build_p2_p3() 从句池动态取句（原手写 P2/P3 字典已移除）。
# 选句方案见 tools/yati_tpl_plan.py。

STANCE = {
    17: (
        ('On balance, interest deserves at least as much weight as market demand.',
         '总体来看，兴趣至少应与市场需求同等重要。'),
        ('A choice that balances both is far more likely to last.',
         '兼顾两者的选择，才更可能走得长远。'),
    ),
    # 1~5 为单幅图画，没有「数据」，否定版立场句的 figures 改成 picture
    1: (('On balance, the picture points to a problem worth taking seriously.',
         '总体来看，这幅画指向一个不容忽视的问题。'),
        P3_CLOSE_NEG),
    2: (('On balance, the picture points to a problem worth taking seriously.',
         '总体来看，这幅画指向一个不容忽视的问题。'),
        P3_CLOSE_NEG),
    3: (('On balance, the picture points to a problem worth taking seriously.',
         '总体来看，这幅画指向一个不容忽视的问题。'),
        P3_CLOSE_NEG),
    4: (('On balance, the picture points to a problem worth taking seriously.',
         '总体来看，这幅画指向一个不容忽视的问题。'),
        P3_CLOSE_NEG),
    5: (('On balance, the picture points to a problem worth taking seriously.',
         '总体来看，这幅画指向一个不容忽视的问题。'),
        P3_CLOSE_NEG),
    # 18 是两幅图的今昔对比
    18: (('On balance, the two pictures point to a problem worth taking seriously.',
          '总体来看，这两幅画指向一个不容忽视的问题。'),
         P3_CLOSE_NEG),
}

# ── 小作文 8 篇：场景骨架 + 填槽 ─────────────────────────────
# 每篇手写模板版句子（en/cn），句式取自 small_writing 功能句池 / letters 场景骨架。
SMALL = {
    19: [
        ('Dear Michael,', '亲爱的 Michael：'),
        ('I hope this message finds you well. I am writing to introduce our peer mentoring program for new students.',
         '希望收到此信时你一切安好。我想向你介绍我们的新生朋辈指导项目。'),
        ('To be more specific, the main arrangements are as follows. Each new student is paired with a senior student who offers advice on courses and campus life.',
         '具体来说，主要安排如下。每名新生都与一名高年级学生结对，后者就课程和校园生活提供建议。'),
        ('In addition, weekly meetings provide opportunities to discuss study methods and share experiences, and group activities help you make friends and become familiar with university services.',
         '此外，每周例会提供了讨论学习方法和交流经验的机会，团体活动则帮助你结交朋友并熟悉学校服务。'),
        ('You can register at the department office before Friday.',
         '你可以在周五之前到系办公室报名。'),
        ('I sincerely hope that you will explore this opportunity and experience its distinct advantages.',
         '我真诚地希望你能把握这个机会，体验它独特的益处。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    20: [
        ('Dear Jane,', '亲爱的 Jane：'),
        ('It was a genuine pleasure to receive your thoughtful communication. I am writing to offer a few suggestions on your speech topic.',
         '很高兴收到你详尽的来信。我想就你的演讲主题提几点建议。'),
        ('I would like to recommend Chinese tea culture for its rich history and close connection with daily life.',
         '我想推荐中国茶文化，因为它历史悠久，且与日常生活紧密相连。'),
        ('To be more specific, you could explain how serving tea expresses hospitality and share a personal experience, which will make your speech more engaging.',
         '具体来说，你可以讲讲奉茶如何表达好客之道，并分享一段亲身经历，这会让你的演讲更有吸引力。'),
        ('As for our video call, would 7 p.m. Beijing time this Saturday be convenient for you?',
         '至于我们的视频通话，本周六北京时间晚上七点对你方便吗？'),
        ('I would appreciate it very much if you could confirm the time at your earliest convenience.',
         '如果你能尽早确认时间，我将不胜感激。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    21: [
        ('Dear Alex,', '亲爱的 Alex：'),
        ('I hope this message finds you well. In this letter, I would like to introduce ChatGPT to you as an exceptional option worthy of your attention.',
         '希望收到此信时你一切安好。在这封信里，我想把 ChatGPT 作为一个值得关注的好选择介绍给你。'),
        ('To be more specific, it represents an AI learning tool distinguished by its flexibility and interactive features.',
         '具体来说，它是一款以灵活性和互动性见长的 AI 学习工具。'),
        ('To begin with, you can ask it to explain difficult concepts, generate practice questions or give feedback on your English writing.',
         '首先，你可以让它解释难懂的概念、生成练习题，或为你的英语写作提供反馈。'),
        ('From a personal standpoint, my regular routine involves asking follow-up questions, which helps me examine points I do not fully understand.',
         '就我个人而言，我常会追问，这有助于我弄懂那些没有完全理解的地方。'),
        ('Please check important information against reliable sources and complete your own work independently.',
         '请务必用可靠来源核对重要信息，并独立完成自己的任务。'),
        ('I sincerely hope that you will explore this opportunity and experience its distinct advantages.',
         '我真诚地希望你能尝试这个工具，体验它独特的优势。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    22: [
        ('Dear James,', '亲爱的 James：'),
        ('Please accept my sincere apology for any inconvenience and trouble that the change of my pick-up plan has brought you.',
         '对于接机计划变更给你带来的不便和麻烦，请接受我诚挚的歉意。'),
        ('To provide you with a candid account, the circumstances are detailed as follows.',
         '为如实说明情况，具体缘由如下。'),
        ('I must admit that the unforeseen examination scheduled for that morning was primarily due to an oversight on my part.',
         '我必须承认，那天上午临时安排的考试主要是由于我的疏忽。'),
        ('Consequently, I have asked my roommate to meet you at the arrivals exit instead, and I will send you his phone number in advance.',
         '因此，我已请室友改到到达出口接你，并会提前把他的电话号码发给你。'),
        ('I earnestly request your kind understanding, and I remain at your disposal for any necessary remedy.',
         '我恳请你的谅解，如需任何补救，我随时听候安排。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    23: [
        ('Dear Professor Thomas,', '亲爱的 Thomas 教授：'),
        ('I am writing to express my profound gratitude for the generous assistance you have extended to me during my summer study program abroad.',
         '非常感谢你在我的海外暑期学习项目中给予我的慷慨帮助。'),
        ('To be more specific, several aspects of your kindness warrant my particular appreciation.',
         '具体而言，你的诸多善意尤其值得我感谢。'),
        ('First and foremost, your advice on my research and your help with library resources were invaluable.',
         '首先，你对我研究的指导以及在图书馆资源方面的帮助，令我受益无穷。'),
        ('Furthermore, our discussions about different cultures taught me a great deal and made my experience truly memorable.',
         '此外，我们关于不同文化的讨论让我收获良多，也使这段经历格外难忘。'),
        ('I wonder if you could visit China during your next holiday so that I can show you some historical sites.',
         '不知你下次假期能否来中国，好让我带你看看一些历史遗迹。'),
        ('Once again, please accept my heartfelt appreciation, and I earnestly hope we can maintain close contact.',
         '再次请接受我诚挚的谢意，也真诚希望我们保持密切联系。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    24: [
        ('Dear Sir or Madam,', '尊敬的先生或女士：'),
        ('I hope this message finds you well. I am writing to apply for a volunteer position at the Center for Cultural Interchange.',
         '希望收到此信时您一切安好。我写信申请文化交流中心的志愿者岗位。'),
        ('I believe I am well qualified for this position, and the reasons are as follows.',
         '我相信自己能胜任这一岗位，理由如下。'),
        ('First, my good command of English allows me to communicate effectively with international visitors.',
         '首先，我良好的英语能力使我能与国际访客有效沟通。'),
        ('Moreover, I have helped organize cultural activities on campus and gained experience in welcoming guests and coordinating schedules.',
         '此外，我曾协助组织校园文化活动，积累了接待来宾和协调日程的经验。'),
        ('I am patient, responsible and available at weekends, and I would be grateful for an opportunity to discuss my qualifications in an interview.',
         '我有耐心、责任心强，周末可以出勤；如能获得面试机会详述我的条件，我将不胜感激。'),
        ('Yours sincerely,', '谨启，'),
        ('Li Ming', '李明'),
    ],
    25: [
        ('Notice', '通知'),
        ('November 20, 2026', '2026 年 11 月 20 日'),
        ('In order to further promote cultural exchange, our association has decided to issue the following notice.',
         '为进一步推动文化交流，本协会决定发布以下通知。'),
        ('As for the planned event, the main arrangements are as follows.',
         '至于本次活动，具体安排如下。'),
        ('First, selected volunteers will guide visitors and introduce cultural attractions every Saturday in December.',
         '首先，入选志愿者将在 12 月的每个周六引导访客并介绍文化景点。'),
        ('Furthermore, applicants should be interested in local culture, communicate clearly and work well in a team, and training will be provided before the first shift.',
         '此外，申请人需对本地文化有兴趣、表达清晰并善于团队合作，首次上岗前将提供培训。'),
        ('You are kindly requested to register at the association office by November 28, and successful applicants will be notified by email within a week.',
         '请于 11 月 28 日前到协会办公室报名，入选者将在一周内收到邮件通知。'),
        ('This is an ideal opportunity to contribute to cultural exchange while gaining valuable experience in event organization.',
         '这是为文化交流贡献力量、同时积累活动组织经验的理想机会。'),
        ('Cultural and Tourism Association', '文化与旅游协会'),
    ],
    26: [
        ('Minutes of Meeting', '会议纪要'),
        ('Date: November 10, 2026', '日期：2026 年 11 月 10 日'),
        ('Time: 3:00-4:00 p.m.', '时间：下午 3:00—4:00'),
        ('Location: Room 201', '地点：201 室'),
        ('This meeting was for the purpose of discussing food waste in daily life, and all participants finally came to the same conclusion.',
         '本次会议旨在讨论日常生活中的食物浪费问题，全体参会者最终达成了一致结论。'),
        ('Participants pointed out that oversized portions and unnecessary purchases were common causes of waste, and that leftovers were often discarded simply because nobody remembered to take them home.',
         '参会者指出，分量过大和不必要的购买是造成浪费的常见原因；剩菜也常常因为没人记得打包而被直接丢弃。'),
        ('After a lively discussion, members also agreed to display posters in the dining hall and remind one another to avoid waste at every meal.',
         '经过热烈讨论，成员们还同意在食堂张贴海报，并在每餐时互相提醒避免浪费。'),
        ('The conclusion is that we are supposed to take immediate actions to order smaller portions, plan purchases carefully and store leftovers properly, and progress will be reviewed at the next monthly meeting.',
         '结论是，我们应立即采取行动：按需点餐、仔细规划采购并妥善存放剩菜，并将在下次月度会议上回顾进展。'),
        ('Recorded by: Li Ming', '记录人：李明'),
    ],
}

# 每篇小作文的段落切分（按上面句子列表的索引，累计须等于句子总数）
SMALL_SPLIT = {
    19: [1, 1, 3, 1, 1, 1],
    20: [1, 1, 3, 1, 1, 1],
    21: [1, 1, 4, 1, 1, 1],
    22: [1, 1, 3, 1, 1, 1],
    23: [1, 1, 5, 1, 1],
    24: [1, 1, 4, 1, 1],
    25: [1, 1, 1, 5, 1],
    26: [1, 3, 1, 3, 1],
}
SMALL_K = {  # 每段的 block 类型（缺省 p）
    19: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    20: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    21: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    22: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    23: ['p', 'p', 'p', 'p', 'sign'],
    24: ['p', 'p', 'p', 'p', 'sign'],
    25: ['h', 'meta', 'p', 'p', 'sign'],
    26: ['h', 'meta', 'p', 'p', 'p'],
}

# ── 组装 ─────────────────────────────────────────────────────
def sent(en, cn):
    return {'en': re.sub(r'\s+', ' ', en).strip(), 'cn': re.sub(r'\s+', ' ', cn).strip()}


def build_big(it, no):
    p1 = PLAN_P1[no]
    stance = TPLAN[no]['stance']
    pair = STANCE.get(no)
    op, cl = pair if pair else ((P3_OPEN_NEG, P3_CLOSE_NEG) if stance == 'neg' else (P3_OPEN_POS, P3_CLOSE_POS))
    p2, p3 = build_p2_p3(no)
    sents = [sent(e, c) for e, c in p1]
    sents.append(sent(*PARA2_INTRO))
    sents += [sent(e, c) for e, c in p2]
    sents.append(sent(*op))
    sents += [sent(e, c) for e, c in p3]
    sents.append(sent(*cl))
    n1 = len(p1)
    n2 = 1 + len(p2)
    return [
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[:n1]), 'sents': sents[:n1]},
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[n1:n1 + n2]), 'sents': sents[n1:n1 + n2]},
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[n1 + n2:]), 'sents': sents[n1 + n2:]},
    ]


def build_small(it):
    no = it['no']
    ss = [sent(e, c) for e, c in SMALL[no]]
    cuts, kinds = SMALL_SPLIT[no], SMALL_K[no]
    if sum(cuts) != len(ss) or len(cuts) != len(kinds):
        raise SystemExit('小作文 %d 分段配置不符: %d != %d, kinds=%d' % (no, sum(cuts), len(ss), len(kinds)))
    groups, idx = [], 0
    for take, k in zip(cuts, kinds):
        seg = ss[idx:idx + take]
        groups.append({'k': k, 'v': ' '.join(s['en'] for s in seg), 'sents': seg})
        idx += take
    return groups


changed = 0
for g in Y['groups']:
    for it in g['items']:
        no = it['no']
        if no in SMALL:
            it['blocks'] = build_small(it)
        elif no in PLAN_P1:
            it['blocks'] = build_big(it, no)
        else:
            raise SystemExit('未覆盖题号: ' + str(no))
        changed += 1

# ── 词数（先算再写盘，页面顶部按 words 显示）─────────────────
wc_bad = []
for g in Y['groups']:
    for it in g['items']:
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", ' '.join(b['v'] for b in it['blocks'])))
        it['words'] = words
        is_small = g['id'] == 't1'
        if is_small and not (85 <= words <= 125):
            wc_bad.append((it['no'], words, 'small'))
        if not is_small and not (145 <= words <= 200):
            wc_bad.append((it['no'], words, 'big'))

with io.open(YATI, 'w', encoding='utf-8') as f:
    json.dump(Y, f, ensure_ascii=False, indent=1)

# ── 校验 ─────────────────────────────────────────────────────
CJK = re.compile(r'[\u4e00-\u9fff]')
err = []
warn = []
for g in Y['groups']:
    for it in g['items']:
        for b in it['blocks']:
            if not b.get('sents'):
                err.append('%d 缺 sents' % it['no'])
            for s in b.get('sents', []):
                if not s.get('en') or not s.get('cn'):
                    err.append('%d 空 en/cn' % it['no'])
                    continue
                if '{{' in s['en'] or '{{' in s['cn'] or '}}' in s['en']:
                    err.append('%d 残留占位符 %s' % (it['no'], s['en']))
                if not CJK.search(s['cn']):
                    err.append('%d 中文缺失: %s' % (it['no'], s['cn'][:50]))
                if s['cn'].strip() == s['en'].strip():
                    err.append('%d 中文等于英文: %s' % (it['no'], s['en'][:50]))
                # 中文里不该成段出现英文（专有名词/缩写允许，连续 4 个以上英文词即视为漏译）
                if len(re.findall(r"[A-Za-z][A-Za-z'-]*", s['cn'])) >= 4:
                    err.append('%d 中文夹杂英文: %s' % (it['no'], s['cn'][:60]))
                # 单句英文过长不利考场书写（首段数据罗列句与早期小作文句允许，仅提示）
                if len(re.findall(r"[A-Za-z][A-Za-z'-]*", s['en'])) > 24:
                    warn.append('%d 长句 %d 词: %s' % (it['no'], len(re.findall(r"[A-Za-z][A-Za-z'-]*", s['en'])), s['en'][:48]))

print('生成 %d 篇' % changed)
print('结构/译文错误:', err[:12] if err else '无')
print('词数越界:', wc_bad if wc_bad else '无')
print('长句提示 %d 条（不阻断）' % len(warn))
if err or wc_bad:
    raise SystemExit(1)
