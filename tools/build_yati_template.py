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
P2 = {
    1: [
        ('First, an answer that takes seconds is hard to refuse when a deadline is close.',
         '首先，当截止日期临近时，几秒钟就能得到的答案很难让人拒绝。'),
        ('Equally important, marks still reward the finished product rather than the thinking behind it.',
         '同样重要的是，评分仍然看最终的成品，而不看背后的思考过程。'),
        ('Beyond that, school rules have not caught up with how quickly these tools have spread.',
         '此外，学校的规定没能跟上这类工具的普及速度。'),
    ],
    2: [
        ('First, work leaves many parents too tired to give a child their full attention at night.',
         '首先，工作让许多家长晚上疲惫不堪，难以把注意力完全放在孩子身上。'),
        ("Equally important, a phone keeps offering something new, while a child's day sounds ordinary.",
         '同样重要的是，手机总能带来新鲜内容，而孩子的一天听起来平淡无奇。'),
        ('Beyond that, many parents assume that sitting in the same room is enough.',
         '此外，不少家长以为和孩子待在同一个房间就够了。'),
    ],
    3: [
        ('First, competition for grades and jobs now starts earlier and lasts longer than before.',
         '首先，对成绩和工作的竞争开始得更早，也持续得更久。'),
        ('Equally important, phones keep work and messages within reach late into the night.',
         '同样重要的是，手机让工作和消息直到深夜都触手可及。'),
        ('Beyond that, few people are taught how to rest before they are exhausted.',
         '此外，很少有人在自己耗尽之前学过怎样休息。'),
    ],
    4: [
        ('First, layers of wrapping let sellers charge more for very little.',
         '首先，层层包装让商家能用很少的东西卖出更高的价钱。'),
        ('Equally important, gifts are still judged partly by how presentable the box looks.',
         '同样重要的是，人们评判礼物时仍部分看盒子是否体面。'),
        ('Beyond that, recycling systems struggle with packages made of mixed materials.',
         '此外，回收体系难以处理由多种材料混合制成的包装。'),
    ],
    5: [
        ('First, platforms earn far more from attention than from accuracy.',
         '首先，平台从流量中获得的收益远多于从准确性中获得的收益。'),
        ('Equally important, recommendation systems keep feeding users what they already believe.',
         '同样重要的是，推荐系统不断向用户推送他们本就相信的内容。'),
        ('Beyond that, few people are taught how to check a source before sharing it.',
         '此外，很少有人学过在转发之前怎样核实信息来源。'),
    ],
    6: [
        ('First, technology changes so fast that skills learned at school go out of date within a few years.',
         '首先，技术更新极快，学校里学到的技能几年之内就会过时。'),
        ('Equally important, employers now look at what a person can actually do rather than at diplomas alone.',
         '同样重要的是，用人单位如今更看重一个人实际能做什么，而不只是文凭。'),
        ('Beyond that, working adults have found that learning a new field keeps a career from stalling.',
         '此外，职场人也发现，学习一个新领域能让职业发展不至于停滞。'),
    ],
    7: [
        ('First, growing concern about air quality has made low-emission travel a matter of personal responsibility.',
         '首先，人们对空气质量的关注不断增强，使低排放出行成为一种个人责任。'),
        ('Equally important, charging an electric car costs far less than filling a petrol tank every week.',
         '同样重要的是，给电动车充电的花费远低于每周加满一箱油。'),
        ('Beyond that, more charging points and more models have removed the worries that once held buyers back.',
         '此外，充电桩和车型不断增多，打消了曾经让消费者犹豫的顾虑。'),
    ],
    8: [
        ('First, mobile payment and map apps have turned hailing a car into a matter of a few taps.',
         '首先，移动支付和地图应用让打车变成点几下手机的事。'),
        ('Equally important, shared bicycles cover the last kilometre that buses never quite reach.',
         '同样重要的是，共享单车填补了公交始终难以覆盖的最后一公里。'),
        ('Beyond that, fixed routes and long waits have made the bus a less attractive choice.',
         '此外，固定线路和长时间等车让公交的吸引力明显下降。'),
    ],
    9: [
        ('First, young people now value room to grow more than a post they can hold for decades.',
         '首先，如今年轻人更看重成长空间，而不是一份能守上几十年的岗位。'),
        ('Equally important, the cost of living in big cities keeps pay near the top of the list.',
         '同样重要的是，大城市的生活成本使薪酬依然排在前列。'),
        ('Beyond that, recruitment sites and former employees have made company reputation easier to check.',
         '此外，招聘网站和离职员工的评价让公司声誉更容易查证。'),
    ],
    10: [
        ('First, long working hours have left city dwellers little time for large supermarkets.',
         '首先，漫长的工时让城市居民几乎没有时间逛大型超市。'),
        ('Equally important, round-the-clock opening hours match the irregular schedules of shift workers.',
         '同样重要的是，二十四小时营业契合了倒班人群不规律的作息。'),
        ('Beyond that, chains have moved into smaller cities, where such stores were once rare.',
         '此外，连锁品牌不断进入小城市，这类门店过去在那里并不多见。'),
    ],
    11: [
        ('First, new regulations require public buildings to provide step-free access.',
         '首先，新的法规要求公共建筑提供无障碍通行条件。'),
        ('Equally important, an ageing population has made accessibility a concern for ordinary families.',
         '同样重要的是，人口老龄化让无障碍成为普通家庭也会关心的问题。'),
        ('Beyond that, wider public attention has pushed many venues to improve their facilities on their own.',
         '此外，公众关注度提高，也促使不少场所主动改善自身的设施。'),
    ],
    12: [
        ('First, first-aid courses have been brought into schools and neighbourhoods.',
         '首先，急救课程已经进入学校和社区。'),
        ('Equally important, reports of accidents have shown people how much a few minutes can matter.',
         '同样重要的是，事故报道让人们看到短短几分钟有多关键。'),
        ('Beyond that, short online lessons make training far easier to fit into a busy week.',
         '此外，简短的线上课程让培训更容易安排进忙碌的一周。'),
    ],
    13: [
        ('First, China now offers research and business opportunities that once existed only abroad.',
         '首先，国内如今提供了过去只在海外才有的科研与创业机会。'),
        ('Equally important, being close to parents matters more as they grow older.',
         '同样重要的是，父母年纪渐长，留在身边变得愈发重要。'),
        ('Beyond that, local governments have eased household registration and funding for start-ups.',
         '此外，地方政府在落户和创业资金方面放宽了条件。'),
    ],
    14: [
        ('First, better hospitals and wider medical insurance have pushed life expectancy steadily upward.',
         '首先，更好的医院和更广的医保覆盖推动人均寿命稳步上升。'),
        ('Equally important, improved nutrition and sanitation have cut deaths from infectious disease.',
         '同样重要的是，营养与卫生条件改善，使传染病导致的死亡大幅减少。'),
        ('Beyond that, a falling birth rate has made the share of older people rise even faster.',
         '此外，出生率持续走低，使老年人口的占比上升得更快。'),
    ],
    15: [
        ('First, cold-chain delivery has made it practical to order ice cream to the door.',
         '首先，冷链配送让冰激凌送货上门成为现实。'),
        ('Equally important, people have grown used to buying everyday items on their phones.',
         '同样重要的是，人们已经习惯用手机购买日常用品。'),
        ('Beyond that, online promotions and wider choices attract buyers who once shopped only in stores.',
         '此外，线上促销和更多口味吸引了原本只在实体店购买的顾客。'),
    ],
    16: [
        ('First, official protection lists and funding have kept many traditional skills alive.',
         '首先，官方的保护名录和资金支持让许多传统技艺得以延续。'),
        ('Equally important, short videos have brought these arts to young viewers who seldom visit museums.',
         '同样重要的是，短视频把这些艺术带到很少走进博物馆的年轻观众面前。'),
        ('Beyond that, schools and community centres now run courses taught by working artists.',
         '此外，学校和社区中心如今开设由在职艺人授课的课程。'),
    ],
    17: [
        ('First, a tight job market makes popular majors look like a safer bet.',
         '首先，就业市场紧张，让热门专业看起来更像稳妥的选择。'),
        ('Equally important, genuine interest is what carries a student through years of hard work.',
         '同样重要的是，真正的兴趣才能支撑一个人熬过多年苦学。'),
        ('Beyond that, many families follow whatever is said to be hot without checking the facts.',
         '此外，不少家庭只是听说什么热门就跟着选，并未核实实际情况。'),
    ],
    18: [
        ('First, visitor numbers have grown far faster than local roads and waste systems can handle.',
         '首先，游客数量的增长远远超出当地道路和垃圾处理能力。'),
        ('Equally important, some operators put short-term profit before the carrying capacity of a site.',
         '同样重要的是，一些经营者把短期利润置于景区承载能力之上。'),
        ('Beyond that, existing rules are poorly enforced during the peak season.',
         '此外，现行规定在旅游旺季执行不力。'),
    ],
}

P3 = {
    1: [
        ('Schools should assess the process, such as drafts and notes, not only the final essay.',
         '学校应考察过程，比如草稿和笔记，而不只看最终交上来的文章。'),
        ('Teachers can show students where these tools help and where they weaken learning.',
         '教师可以向学生说明这类工具在哪些环节有帮助、在哪些环节会削弱学习。'),
        ('Students need to try a problem themselves before asking a machine.',
         '学生则应先自己动手试一试，再去求助机器。'),
    ],
    2: [
        ('Parents should set aside half an hour without a phone and let the child lead the talk.',
         '家长应留出半小时不碰手机，让孩子主导这段谈话。'),
        ('Schools can remind families that real attention matters more than hours spent together.',
         '学校可以提醒家庭：真正的回应比共处的时间更重要。'),
        ('Children also need to say plainly when they want to be heard.',
         '孩子也需要直接说出自己希望被倾听。'),
    ],
    3: [
        ('Schools and employers should treat rest as part of performance rather than a reward.',
         '学校和用人单位应把休息视为状态的一部分，而不是一种奖励。'),
        ('Individuals can protect their sleep and take short walks instead of scrolling at night.',
         '个人可以守住睡眠，用散步代替深夜刷手机。'),
        ('Those who feel unwell should ask for help early, not wait for a breakdown.',
         '感到不适的人应及早求助，而不是等到崩溃。'),
    ],
    4: [
        ('Government should set limits on packaging layers and charge for excess.',
         '政府应对包装层数设限，并对超标部分收费。'),
        ('Retailers can offer simple wrapping that still looks presentable.',
         '商家可以提供简约而同样体面的包装。'),
        ('Shoppers should say no to unnecessary boxes at the counter.',
         '消费者则应在柜台前拒绝不必要的包装盒。'),
        ('Schools can explain to children why a plain package is often the better gift.',
         '学校可以告诉孩子，为什么朴素的包装往往是更好的礼物。'),
    ],
    5: [
        ('Platforms should label unverified claims and slow their spread.',
         '平台应标注未经核实的信息，并减缓其传播速度。'),
        ('Schools can teach students to compare sources and look for evidence.',
         '学校可以教学生比对多个来源、寻找证据。'),
        ('Readers should pause before forwarding anything that stirs strong feelings.',
         '读者在转发任何让人情绪激动的内容之前，都应先停一停。'),
        ('Libraries and community centres can run short sessions on how to check a fact.',
         '图书馆和社区中心可以开设短课，教人怎样核实一条信息。'),
    ],
    6: [
        ('Government can fund evening schools and open online courses so that learning does not depend on income.',
         '政府可以资助夜校和免费的网络课程，让学习不再取决于收入。'),
        ('Employers should set aside a few paid hours each month for staff training.',
         '用人单位应每月留出几个带薪小时用于员工培训。'),
        ('Individuals need to choose courses that fit their stage of career rather than follow the crowd.',
         '个人则应根据自己所处的职业阶段选课，而不是随大流。'),
    ],
    7: [
        ('Car makers should keep improving batteries so that one charge covers a longer distance.',
         '车企应持续改进电池，让一次充电能跑更远的距离。'),
        ('Government can speed up the building of charging points in older neighbourhoods.',
         '政府可以加快老旧小区充电桩的建设。'),
        ('Individuals should pick a model that suits their daily travel rather than follow the crowd.',
         '个人应根据自己的日常出行需求选车，而不是跟风。'),
    ],
    8: [
        ('Government can redraw bus routes and add bus lanes so that public transport saves real time.',
         '政府可以重划公交线路、增设公交专用道，让公共交通真正省时。'),
        ('Platforms should keep prices clear and stop bicycles from blocking pavements.',
         '平台应保持价格透明，并避免共享单车堵塞人行道。'),
        ('Residents can cycle for short trips and take the bus for longer ones.',
         '居民短途可以骑车，长途则选择公交。'),
    ],
    9: [
        ('Universities should offer career courses that help students compare offers in a clear framework.',
         '高校应开设职业课程，帮助学生用清晰的框架比较不同选择。'),
        ('Employers should spell out promotion paths instead of promising vague opportunities.',
         '用人单位应明确写出晋升路径，而不是给出模糊的机会承诺。'),
        ('Students need to weigh their own strengths before following a popular choice.',
         '学生则应在跟从热门选择之前，先衡量自己的优势。'),
    ],
    10: [
        ('Chains should keep food fresh and treat their staff fairly while they expand.',
         '连锁企业在扩张的同时，应保证食品新鲜、善待员工。'),
        ('Government can tighten checks on food safety and on how these stores are run.',
         '政府可以加强对食品安全和门店经营的检查。'),
        ('Individuals should buy only what they need instead of stocking up on discounts.',
         '个人应按需购买，而不是一见打折就囤货。'),
    ],
    11: [
        ('Government should check that ramps and lifts actually work instead of counting them on paper.',
         '政府应检查坡道和电梯是否真正可用，而不是只在纸面上统计数量。'),
        ('Venues should keep accessible routes clear of bicycles and goods.',
         '各类场所应保持无障碍通道不被自行车和货物占用。'),
        ('Individuals can speak up when they see a barrier blocking someone else.',
         '个人在看到障碍物挡住他人通行时，也可以主动反映。'),
    ],
    12: [
        ('Government can make first aid a required part of the school curriculum.',
         '政府可以把急救纳入学校的必修内容。'),
        ('Communities should hold practice sessions so that the skills are not forgotten.',
         '社区应定期组织演练，让这些技能不至于遗忘。'),
        ('Individuals can learn basic CPR before they actually need it.',
         '个人可以在真正需要之前学会基本的心肺复苏。'),
    ],
    13: [
        ('Government can shorten paperwork for returnees who start companies or join research labs.',
         '政府可以简化回国人员创业、进入实验室的办事流程。'),
        ('Universities and firms should create posts that let returnees use what they learned abroad.',
         '高校和企业应设置岗位，让回国人员用上海外所学。'),
        ('Returnees need to adapt to local ways of working instead of expecting them to change.',
         '回国人员则需要适应本地的工作方式，而不是期待它为自己改变。'),
    ],
    14: [
        ('Government should expand community clinics and affordable care for older people.',
         '政府应扩大社区诊所和面向老年人的平价照护。'),
        ('Companies can design products and services that suit older customers.',
         '企业可以设计适合老年客户的产品与服务。'),
        ('Families need to share care duties instead of leaving them to one member.',
         '家庭成员应分担照护责任，而不是全压在一个人身上。'),
    ],
    15: [
        ('Platforms should keep the cold chain reliable, or the goods arrive unfit to eat.',
         '平台应保证冷链可靠，否则到手的东西根本无法食用。'),
        ('Stores can turn themselves into places where customers taste before buying.',
         '实体店可以把自己变成能先尝后买的场所。'),
        ('Individuals should order what they will finish rather than stock up on discounts.',
         '个人应按能吃完的量下单，而不是见折扣就囤。'),
    ],
    16: [
        ('Government should pay inheritors a steady income so that teaching is not a hobby.',
         '政府应给传承人稳定收入，让教学不再只是业余爱好。'),
        ('Platforms can give such content more exposure and protect it from misuse.',
         '平台可以给这类内容更多曝光，并防止其被滥用。'),
        ('Individuals can learn one craft or simply take a child to see a real performance.',
         '个人可以学一门手艺，或者只是带孩子去看一场真正的演出。'),
    ],
    17: [
        ('Universities should explain what each major actually involves before students choose.',
         '高校应在学生做选择之前，讲清每个专业究竟学些什么。'),
        ('Employers should judge graduates by ability rather than by the name of their major.',
         '用人单位应以能力而非专业名称来评判毕业生。'),
        ('Students need to ask themselves what they can keep doing for years.',
         '学生则需要问自己：什么事是我能坚持做很多年的。'),
    ],
    18: [
        ('Government should cap daily visitors and use bookings to spread the flow.',
         '政府应限制每日游客数量，并用预约把客流分散开。'),
        ('Scenic areas can spend ticket income on rubbish collection and repair work.',
         '景区可以把门票收入用于垃圾清运和生态修复。'),
        ('Visitors should take their rubbish away and travel outside the peak weeks.',
         '游客应带走自己的垃圾，并避开高峰期出行。'),
    ],
}

# 立场句/收尾句默认取模板（pos / neg 两版）；第 17 篇题意是「热门 vs 热爱」，
# 模板的「趋势值得欢迎 / 势头将继续」不贴合，单独给一对（其余 17 篇一律用模板句）。
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
    stance = STANCE_TYPE[no]
    pair = STANCE.get(no)
    op, cl = pair if pair else ((P3_OPEN_NEG, P3_CLOSE_NEG) if stance == 'neg' else (P3_OPEN_POS, P3_CLOSE_POS))
    sents = [sent(e, c) for e, c in p1]
    sents.append(sent(*PARA2_INTRO))
    sents += [sent(e, c) for e, c in P2[no]]
    sents.append(sent(*op))
    sents += [sent(e, c) for e, c in P3[no]]
    sents.append(sent(*cl))
    n1 = len(p1)
    n2 = 1 + len(P2[no])
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
