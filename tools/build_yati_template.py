# -*- coding: utf-8 -*-
"""押题范文「模板化」生成器。

规则（用户 2026-11-20 定）：
  · 单图表 5 篇 + 小作文 8 篇：首段也用模板句重写，全篇皆用户模板句。
  · 其余 13 篇（图画 / 双图表）：首段保留原题描述原句（只配中文），
    第二、三段换成用户模板池的通用句。
  · 每句 en/cn 成对写进 yati.json 的 blocks[].sents，前端逐句点开中文。

真源：
  · 大作文句池 / 骨架：pwa/data/writing_templates.json（由 rebuild_skeleton.py 生成）
  · 小作文场景骨架：pwa/data/small_writing.json（由 build_small_writing.py 生成）
  · 本文件只放「选句方案 + 首段文案」，不手写模板句本身。

幂等：重复运行覆盖 essay 字段，不动 notes/img/blocks.v 之外的东西。
用法：python tools/build_yati_template.py
"""
import json, os, io, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PWA = os.path.join(ROOT, 'pwa')
YATI = os.path.join(PWA, 'data', 'yati.json')
WTPL = os.path.join(PWA, 'data', 'writing_templates.json')
SW = os.path.join(PWA, 'data', 'small_writing.json')

with io.open(YATI, encoding='utf-8') as f:
    Y = json.load(f)
with io.open(WTPL, encoding='utf-8') as f:
    T = json.load(f)
with io.open(SW, encoding='utf-8') as f:
    S = json.load(f)

# ── 模板池索引：tag -> (en, cn) ──────────────────────────────
POOL = {}
for sec in T['sections']:
    sid = sec['id']
    for x in (sec.get('sentences') or []):
        POOL[(sid, x['tag'])] = (x['en'], x.get('cn', ''))
    if sid in ('para3_positive', 'para3_negative'):
        for i, x in enumerate(sec.get('sentences') or []):
            POOL[(sid, '#%d' % i)] = (x['en'], x.get('cn', ''))

PARA2_INTRO = ('This phenomenon can be attributed to a combination of factors.',
               '这一现象可归因于多种因素的综合作用。')
# 立场句 / 收尾句：来自 para3_*.en 的两半（模板固定句，不随 topic 变）
P3_OPEN_POS = ('On balance, this is a positive trend worth welcoming.', '总的来说，这是一个值得欢迎的积极趋势。')
P3_CLOSE_POS = ('Given the momentum behind it, there is every reason to believe that it will continue in the years ahead.',
                '鉴于其背后的势头，我们有充分的理由相信，这一趋势将在未来几年继续发展。')
P3_OPEN_NEG = ('On balance, the figures point to a problem worth taking seriously.', '总的来说，这些数据指向一个不容忽视的问题。')
P3_CLOSE_NEG = ('Unless effective measures are taken, it may well get worse.', '若不采取有效措施，问题很可能进一步恶化。')

# ── 逐篇方案 ────────────────────────────────────────────────
# topic_en / topic_cn：填 {{topic}}（英文句子里是裸词，填英文；中文句子填中文）
# p1：首段句子列表 [(en, cn)]；单图表用模板骨架写，图画题保留原句+中文
# p2：第二段机制 tag（从 para2_why 池取，按写作页链接词顺序展开）
# p3：第三段对策 tag（从 para3_positive / negative 池取）
# stance: pos / neg

PLAN = {
    # ============ 单图表 5 篇：首段也用模板骨架 ============
    6: dict(topic=('continuing education', '继续教育'), stance='pos',
        p1=[
            ('The bar chart above clearly illustrates how the purposes of continuing education among working people are distributed.',
             '该柱状图清晰地展示了在职群体参加继续教育的目的的分布情况。'),
            ('Improving current job skills takes the lead, accounting for 65%, followed by learning about new fields and developing personal interests at 48% and 37% respectively, while obtaining qualifications comes last at 26%.',
             '提升现有岗位技能遥遥领先，占 65%；其后是学习新领域和发展个人兴趣，分别占 48% 和 37%；而获得文凭位居最后，占 26%。'),
            ('Taken together, the three largest items make up 150%.',
             '前三项加起来占 150%。'),
        ],
        p2=['职场时间', '就业门槛', '观念'], p3=['政府', '学校', '个人']),
    7: dict(topic=('new energy vehicles', '新能源汽车'), stance='pos',
        p1=[
            ('The line chart above clearly illustrates the changes in domestic sales of conventional and new energy vehicles from January to June 2025.',
             '该折线图清晰地展示了 2025 年 1 月至 6 月燃油车与新能源汽车国内销量的变化。'),
            ('Sales of new energy vehicles rose from 0.79 million to 1.12 million, while the figure for conventional vehicles fluctuated and peaked at 1.33 million in March.',
             '新能源汽车销量从 79 万辆增至 112 万辆，而燃油车销量则起伏波动，在 3 月达到 133 万辆的峰值。'),
            ('The two moved in the same direction, but not at the same pace.',
             '两者方向一致，但速度不同。'),
        ],
        p2=['科技普及', '便利', '环保意识'], p3=['企业/平台', '政府', '个人']),
    8: dict(topic=('daily transport choices', '日常出行方式'), stance='pos',
        p1=[
            ('The chart above clearly illustrates the changes in daily transport choices in a city from 2015 to 2021.',
             '该图清晰地展示了 2015 年至 2021 年某市居民日常出行方式的变化。'),
            ('The proportion of residents choosing buses fell from just over 50% to under 30%, while the shares for ride-hailing services and shared bicycles rose to approximately a quarter each.',
             '选择公交的居民比例从略高于 50% 降至不足 30%，而网约车和共享单车的占比各自升至约四分之一。'),
            ('The two moved in opposite directions.',
             '两者朝相反的方向变化。'),
        ],
        p2=['便利', '科技普及', '公共投入'], p3=['政府', '企业/平台', '个人']),
    9: dict(topic=('job preferences', '择业考虑'), stance='pos',
        p1=[
            ('The bar chart above clearly illustrates how the factors considered by university students when choosing a job are distributed.',
             '该柱状图清晰地展示了大学生择业时考虑的各项因素的分布情况。'),
            ('Personal development prospects take the lead, accounting for 65%, followed by pay and company reputation at 53% and 31% respectively, while personal interests and the working environment come last at 22% and 9%.',
             '个人发展前景遥遥领先，占 65%；其后是薪酬和公司声誉，分别占 53% 和 31%；而个人兴趣和工作环境位居最后，占 22% 和 9%。'),
            ('The gap between the largest and the smallest is wide.',
             '最大项与最小项之间差距很大。'),
        ],
        p2=['就业门槛', '职场流动', '收入'], p3=['学校', '个人', '政府']),
    10: dict(topic=('convenience stores', '便利店'), stance='pos',
        p1=[
            ('The line chart above clearly illustrates the growth in the number of convenience stores in China from 2015 to 2023.',
             '该折线图清晰地展示了 2015 年至 2023 年全国便利店门店数量的增长。'),
            ('The total rose from roughly 90,000 to approximately 320,000, and the first half of the period saw a steady rise while the last few years brought a sharp acceleration.',
             '门店总数从约 9 万家增至约 32 万家；前半段稳步上升，最后几年明显加速。'),
            ('The figure more than doubled over the period.',
             '这一数字在该时期翻了一倍多。'),
        ],
        p2=['收入', '便利', '城市化'], p3=['政府·长效', '企业/平台', '个人']),

    # ============ 图画 / 双图表 13 篇：首段保留原句，二三段套模板 ============
    1: dict(topic=('AI tools', '人工智能工具'), stance='neg',
        p1=[
            ('The cartoon above presents us with a thought-provoking scene: a student is delighted with an AI tool that has generated answers to his homework.',
             '上图为我们展现了一个发人深省的场景：一名学生因为 AI 工具帮他写出了作业答案而沾沾自喜。'),
            ('The caption suggests that the assignment is already complete.',
             '图下文字暗示，作业已经完成了。'),
            ('The drawing invites us to reflect on whether finishing a task necessarily means learning something.',
             '这幅画促使我们思考：完成任务是否必然意味着学到了东西。'),
        ],
        p2=['科技普及', '便利', '规则滞后'], p3=['家庭', '个人', '政府']),
    2: dict(topic=('real companionship', '真正的陪伴'), stance='neg',
        p1=[
            ('As is symbolically depicted in the cartoon above, a father sits beside his son but keeps his eyes on his mobile phone.',
             '正如上图所象征性描绘的，一位父亲坐在儿子身边，眼睛却始终盯着手机。'),
            ('The boy asks whether his father is listening.',
             '男孩问父亲有没有在听他说话。'),
            ('The caption beneath the drawing reminds us that being physically present does not necessarily mean providing real companionship.',
             '图画下方的文字提醒我们，人在身边并不等于真正的陪伴。'),
        ],
        p2=['职场时间', '生活节奏', '观念'], p3=['家庭', '个人', '媒体']),
    3: dict(topic=('stress management', '压力管理'), stance='neg',
        p1=[
            ('Depicted in the picture above is a scene that strikes us as both familiar and thought-provoking: a man sits at a desk with his head lowered, surrounded by documents and reminders.',
             '上图描绘的场景既熟悉又发人深省：一名男子埋首于书桌前，四周堆满了文件和待办提醒。'),
            ('The word "pressure" appears prominently above him.',
             '他头顶上方醒目地写着「压力」二字。'),
            ('The drawing highlights the burden that excessive stress can place on daily life.',
             '这幅画凸显了过度压力给日常生活带来的负担。'),
        ],
        p2=['职场时间', '就业门槛', '生活节奏'], p3=['个人', '企业·雇主', '政府']),
    4: dict(topic=('responsible consumption', '理性消费'), stance='neg',
        p1=[
            ('The cartoon above presents us with a thought-provoking scene: a person stands beside a pile of boxes and wonders why buying one gift requires so much packaging.',
             '上图为我们展现了一个发人深省的场景：一个人站在一堆包装盒旁，困惑为什么买一件礼物需要这么多包装。'),
            ('The contrast between the small purchase and the large amount of wrapping highlights the problem of excessive packaging.',
             '小小的商品与大量包装之间的反差，凸显了过度包装的问题。'),
        ],
        p2=['逐利', '环保意识', '观念'], p3=['企业/平台', '政府', '个人']),
    5: dict(topic=('information literacy', '信息辨别能力'), stance='neg',
        p1=[
            ('As is symbolically depicted in the cartoon above, a confused man faces a computer surrounded by conflicting messages.',
             '正如上图所象征性描绘的，一个困惑的人面对着电脑，四周充斥着相互矛盾的信息。'),
            ('The caption points to the difficulty of distinguishing reliable online information from falsehoods.',
             '图下文字指出了辨别可靠网络信息与虚假信息的困难。'),
            ('The drawing raises an important question about honesty and judgment in the digital age.',
             '这幅画提出了一个关于数字时代诚信与判断力的重要问题。'),
        ],
        p2=['科技普及', '逐利', '规则滞后'], p3=['企业/平台', '政府', '个人']),
    11: dict(topic=('accessible facilities', '无障碍设施'), stance='pos',
        p1=[
            ('The cartoon above depicts a wheelchair user approaching a public building by an accessible route, while the chart illustrates improvements in accessibility.',
             '上图描绘了一名轮椅使用者通过无障碍通道接近公共建筑，而下图则展示了无障碍环境的改善。'),
            ('The proportion of public places with accessible routes in a city rose steadily from 56% in 2021 to 85% in 2025.',
             '某市配备无障碍通道的公共场所比例从 2021 年的 56% 稳步升至 2025 年的 85%。'),
            ('Together, the two images highlight progress toward a more inclusive society.',
             '两幅材料共同凸显了社会走向包容的进步。'),
        ],
        p2=['公共投入', '观念', '人口结构'], p3=['政府', '政府·长效', '个人']),
    12: dict(topic=('first-aid training', '急救培训'), stance='pos',
        p1=[
            ('The cartoon above depicts a person teaching others a basic first-aid skill, while the chart illustrates growing participation in first-aid training.',
             '上图描绘了一个人向他人传授基本急救技能，下图则展示了急救培训参与度的提升。'),
            ('In a city, the proportion of residents aged 18 to 60 who received such training increased steadily from 9% in 2021 to 32% in 2025.',
             '某市 18 至 60 岁居民中接受过此类培训的比例，从 2021 年的 9% 稳步升至 2025 年的 32%。'),
            ('These materials highlight the spread of practical knowledge of emergency response.',
             '这些材料凸显了应急处置实用知识的普及。'),
        ],
        p2=['公共投入', '学校', '观念'], p3=['学校', '政府', '个人']),
    13: dict(topic=('returning overseas students', '留学人员回国'), stance='pos',
        p1=[
            ('The cartoon above depicts overseas students returning to China, while the chart below illustrates the growth in their numbers.',
             '上图描绘了留学人员回国，下图则展示了回国人数的增长。'),
            ('The annual number of returning students increased from 134,800 in 2010 to 600,000 in 2019, rising to more than four times its initial level.',
             '年度回国人数从 2010 年的 13.48 万增至 2019 年的 60 万，达到最初水平的四倍多。'),
            ('Together, the materials highlight the growing appeal of returning home after studying abroad.',
             '两则材料共同凸显了留学后回国发展的吸引力日益增强。'),
        ],
        p2=['科技普及', '职场流动', '观念'], p3=['政府', '企业/平台', '个人']),
    14: dict(topic=('an aging population', '人口老龄化'), stance='pos',
        p1=[
            ('The charts above illustrate changes in life expectancy and population aging in China.',
             '以上两幅图展示了中国人均预期寿命与人口老龄化的变化。'),
            ('Average life expectancy rose from 72.54 years in 2004 to 79 years in 2024.',
             '人均预期寿命从 2004 年的 72.54 岁升至 2024 年的 79 岁。'),
            ('Meanwhile, the proportion of people aged 60 and above increased from 10.97% to 22%, slightly more than doubling.',
             '与此同时，60 岁及以上人口比例从 10.97% 升至 22%，略高于翻倍。'),
        ],
        p2=['人口结构', '公共投入', '收入'], p3=['政府', '家庭', '政府·长效']),
    15: dict(topic=('online shopping', '线上购物'), stance='pos',
        p1=[
            ('The pie charts above illustrate the shares of online and offline ice cream sales in China in 2020 and 2021.',
             '以上饼图展示了 2020 年与 2021 年中国冰激凌线上与线下销售的占比。'),
            ('The online share rose from 5% to 20%, while the offline share fell from 95% to 80%.',
             '线上占比从 5% 升至 20%，而线下占比从 95% 降至 80%。'),
            ('Although online sales gained 15 percentage points, offline purchases remained dominant.',
             '尽管线上销售提高了 15 个百分点，线下购买仍占主导。'),
        ],
        p2=['科技普及', '便利', '观念'], p3=['企业/平台', '政府', '个人']),
    16: dict(topic=('traditional Chinese art', '中国传统艺术'), stance='pos',
        p1=[
            ('The pictures above present us with thought-provoking scenes of traditional Chinese art being passed on.',
             '以上两幅图为我们展现了中国传统艺术得以传承的动人场景。'),
            ('In the first picture, an older artist demonstrates a traditional skill to a young learner.',
             '第一幅图中，一位老艺人向年轻学习者演示传统技艺。'),
            ('In the second, the younger generation shares and practices the art.',
             '第二幅图中，年轻一代分享并实践这门艺术。'),
        ],
        p2=['文化传承', '学校', '文化新媒介'], p3=['学校', '媒体', '个人']),
    17: dict(topic=('choosing a major', '专业选择'), stance='pos',
        p1=[
            ('The pictures above present two considerations when choosing a major.',
             '以上两幅图呈现了专业选择时的两种考量。'),
            ('In the first, a student is attracted by strong market demand and promising career prospects.',
             '第一幅图中，一名学生被强劲的市场需求和良好的职业前景所吸引。'),
            ('In the second, another student expresses enthusiasm for a particular subject.',
             '第二幅图中，另一名学生表达了对某一学科的浓厚兴趣。'),
        ],
        p2=['就业门槛', '职场流动', '观念'], p3=['学校', '个人', '政府']),
    18: dict(topic=('tourism development', '旅游发展'), stance='neg',
        p1=[
            ('The pictures above present a striking contrast between a scenic area in the past and the same place today.',
             '以上两幅图呈现了某景区过去与今天的鲜明反差。'),
            ('The earlier scene features a peaceful natural landscape, whereas the later one shows crowded tourist facilities, numerous boats and scattered rubbish.',
             '早先的画面是宁静的自然景观，而如今却是拥挤的旅游设施、众多游船和散落的垃圾。'),
            ('The contrast highlights the environmental cost of poorly managed tourism.',
             '这一反差凸显了管理不善的旅游业所付出的环境代价。'),
        ],
        p2=['逐利', '环保意识', '规则滞后'], p3=['政府', '企业/平台', '个人']),
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
    26: [1, 4, 3, 1],
}
SMALL_K = {  # 每段的 block 类型（缺省 p）
    19: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    20: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    21: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    22: ['p', 'p', 'p', 'p', 'sign', 'sign'],
    23: ['p', 'p', 'p', 'p', 'sign'],
    24: ['p', 'p', 'p', 'p', 'sign'],
    25: ['h', 'meta', 'p', 'p', 'sign'],
    26: ['h', 'meta', 'p', 'p'],
}

# ── 组装 ─────────────────────────────────────────────────────
def fill(text, topic_en, topic_cn):
    """模板句占位符填充：{{topic}} 按中英文分别填，{{item*}} 等保持原样（首段已写死）。"""
    return text.replace('{{topic}}', topic_en), text.replace('{{topic}}', topic_cn)


def sent(en, cn):
    return {'en': re.sub(r'\s+', ' ', en).strip(), 'cn': re.sub(r'\s+', ' ', cn).strip()}


def build_big(it, plan):
    topic_en, topic_cn = plan['topic']
    sents = [sent(e, c) for e, c in plan['p1']]
    intro_en, intro_cn = fill(PARA2_INTRO[0], topic_en, topic_cn)
    sents.append(sent(intro_en, intro_cn))
    for i, tag in enumerate(plan['p2']):
        key = ('para2_why', tag)
        if key not in POOL:
            raise SystemExit('缺机制句 tag: ' + tag)
        en, cn = POOL[key]
        en, cn = fill(en, topic_en, topic_cn)
        sents.append(sent(en, cn))
    neg = (plan['stance'] == 'neg')
    op = P3_OPEN_NEG if neg else P3_OPEN_POS
    cl = P3_CLOSE_NEG if neg else P3_CLOSE_POS
    sents.append(sent(*op))
    sec = 'para3_negative' if neg else 'para3_positive'
    for tag in plan['p3']:
        key = (sec, tag)
        if key not in POOL:
            raise SystemExit('缺对策句 tag: %s / %s' % (sec, tag))
        en, cn = POOL[key]
        en, cn = fill(en, topic_en, topic_cn)
        sents.append(sent(en, cn))
    sents.append(sent(*cl))
    # 3 段：首段 / 第二段（引入+机制）/ 第三段（立场+对策+收尾）
    n1 = len(plan['p1'])
    n2 = 1 + len(plan['p2'])
    return [
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[:n1]), 'sents': sents[:n1]},
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[n1:n1+n2]), 'sents': sents[n1:n1+n2]},
        {'k': 'p', 'v': ' '.join(s['en'] for s in sents[n1+n2:]), 'sents': sents[n1+n2:]},
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
        elif no in PLAN:
            it['blocks'] = build_big(it, PLAN[no])
        else:
            raise SystemExit('未覆盖题号: ' + str(no))
        changed += 1

with io.open(YATI, 'w', encoding='utf-8') as f:
    json.dump(Y, f, ensure_ascii=False, indent=1)

# ── 校验 ─────────────────────────────────────────────────────
err = []
for g in Y['groups']:
    for it in g['items']:
        for b in it['blocks']:
            if 'sents' not in b:
                err.append('%d 缺 sents' % it['no'])
            for s in b.get('sents', []):
                if not s.get('en') or not s.get('cn'):
                    err.append('%d 空 en/cn' % it['no'])
                if '{{' in s.get('en', ''):
                    err.append('%d 残留占位符 %s' % (it['no'], s['en']))
# 词数（大作文 150~185，小作文 85~120）
wc_bad = []
for g in Y['groups']:
    for it in g['items']:
        words = len(re.findall(r"[A-Za-z][A-Za-z'-]*", ' '.join(b['v'] for b in it['blocks'])))
        is_small = g['id'] == 't1'
        if is_small and not (85 <= words <= 125):
            wc_bad.append((it['no'], words, 'small'))
        if not is_small and not (145 <= words <= 200):
            wc_bad.append((it['no'], words, 'big'))

print('生成 %d 篇' % changed)
print('结构错误:', err[:10] if err else '无')
print('词数越界:', wc_bad if wc_bad else '无')
if err or wc_bad:
    raise SystemExit(1)
