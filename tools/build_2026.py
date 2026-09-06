# -*- coding: utf-8 -*-
"""2026 考研英语二 → pwa/data/2026.json
数据来源：新东方/海文/希赛/人人文库等多源交叉核验（真题原文+答案）。
覆盖：Text1-4 + 完形 + 翻译 + 写作A/B（新题型 PartB 原文缺，暂不含）。
"""
import json, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def mk_sentences(items):
    """items: [(para, en, cn)] → sentence dicts"""
    return [{"id": f"2026_{AID}{i:02d}", "para": p, "en": e, "cn": c, "words": []}
            for i, (p, e, c) in enumerate(items, 1)]

def mk_questions(qs, prefix, start):
    """qs: [(number, qtype, stem, stem_cn, options, options_cn, answer)]"""
    out = []
    for i, (num, qt, stem, stem_cn, opts, opts_cn, ans) in enumerate(qs, 1):
        out.append({"id": f"2026_{prefix}_q{i}", "number": num, "qtype": qt,
                    "stem": stem, "stem_cn": stem_cn,
                    "options": opts, "options_cn": opts_cn,
                    "answer": ans, "explanation": "", "related_sentences": []})
    return out

# ============ Text 1 公共图书馆 ============
AID = "text1"
T1 = [
(1, "Ask people about public libraries and a certain image springs to mind: dusty, old-fashioned, the sort of place you enjoyed as a child but, rather like a British seaside town, would you go there now? And anyway—aren't they all closing?",
 "问起公共图书馆，人们脑海中浮现的往往是这样的形象：积满灰尘、老气横秋，小时候喜欢去的地方——可就像英国的海滨小镇一样，你现在还会去吗？而且——它们不是都在关门吗？"),
(2, "The reality is startlingly different, as I discovered when the culture department commissioned me to conduct an independent review of English public libraries, published yesterday.",
 "实际情况却截然不同——文化部门委托我对英格兰公共图书馆进行独立审查，这份审查昨天已经发布，我在调查中发现了这一点。"),
(2, "As I visited libraries up and down the country, I was surprised to learn there are more than twice the number of libraries (2,892) as there are branches of McDonald's.",
 "当我走访全国各地的图书馆时，我惊讶地发现图书馆的数量（2892 家）是麦当劳门店数量的两倍还多。"),
(3, "Enter any one of them and you will find a hive of activity; while books are, and should always be, at the heart of any library, a multitude of other services are offered: employment advice, language classes or digital access and support.",
 "走进任何一家图书馆，你都会发现一派繁忙景象；虽然书籍始终是图书馆的核心，但图书馆还提供大量其他服务：就业咨询、语言课程，或数字接入与支持。"),
(4, "There are libraries with business and intellectual property (IP) centres, which can help business owners and entrepreneurs.",
 "有些图书馆设有商业与知识产权中心，能够帮助企业主和创业者。"),
(4, "Many have nurses on site to carry out basic health checks, with a link to the GP's surgery.",
 "许多图书馆还配有护士进行基本健康检查，并与全科医生诊所对接。"),
(4, "There are libraries where young people can borrow a Fifa-standard football free.",
 "有些图书馆的年轻人可以免费借到比赛标准的足球。"),
(5, "In return for all of this, you'll be asked for precisely nothing.",
 "这一切都完全免费，不会向你索取任何东西。"),
(5, "There will be no charge and you will never be asked to justify or explain yourself; you will simply be welcomed in, offered help if you need it, and left alone if you do not.",
 "不收取任何费用，也从不要求你说明来意；你只会被热情迎入，需要帮助时有人援手，不需要时没人打扰。"),
(5, "There is no other institution, public or private, that can say the same.",
 "没有其他任何公立或私营机构能做到这一点。"),
(5, "Yet still our libraries are often overlooked and underappreciated.",
 "然而，我们的图书馆却常常被忽视、被低估。"),
(5, "There is an overall decline in visits and many are struggling as local authorities come under continued financial pressure.",
 "访问人数整体下降，许多图书馆在地方政府持续财政压力下艰难维持。"),
(6, "The number of libraries that have closed since 2010 is disputed.",
 "自 2010 年以来关闭的图书馆数量存在争议。"),
(6, "An annual survey by the Chartered Institute of Public Finance and Accountancy puts it at nearly 800 across the UK; official statistics held by the Arts Council record 230 in England.",
 "英国特许公共财政与会计学会的年度调查称，全英关闭了近 800 家；而艺术委员会掌握的官方数据显示英格兰关闭了 230 家。"),
(6, "It is, of course, 230 libraries too many.",
 "当然，即便 230 家也太多了。"),
(6, "So if we are to protect our libraries for future generations, we must raise awareness of them and the work they do.",
 "因此，如果我们要为子孙后代守护图书馆，就必须提高人们对图书馆及其工作的认识。"),
(7, "The review recommends a national branding campaign to give libraries a stronger physical presence, the reintroduction of a scheme to enable members to use their card in any library in the country, and automatic memberships for children.",
 "审查报告建议：开展全国品牌推广活动以增强图书馆的实体存在感，重新引入一项让会员可在全国任何图书馆使用其借书卡的方案，并为儿童自动办理会员资格。"),
(7, "If we don't use them, we will end up losing them.",
 "如果我们不去使用图书馆，最终就会失去它们。"),
(7, "And for those who haven't been to a library for some time, they may be surprised by what they find.",
 "对于那些很久没去过图书馆的人来说，他们可能会对今天的发现感到惊讶。"),
]
T1_Q = [
(21, "detail", "What was the author commissioned to do about English public libraries?",
 "作者被委托就英格兰公共图书馆做些什么？",
 {"A": "Document their valuable traditions.", "B": "Make a plan for their expansions.", "C": "Obtain reader opinions on them.", "D": "Look into their current situation."},
 {"A": "记录它们的宝贵传统", "B": "为它们的扩张制定计划", "C": "收集读者对它们的意见", "D": "调查它们的现状"}, "D"),
(22, "inference", "According to Paragraphs 3 and 4, the author finds that libraries ______.",
 "根据第三、四段，作者发现图书馆______。",
 {"A": "boast desirable book collections.", "B": "keep detailed visitor records.", "C": "perform diversified functions.", "D": "attract mostly young readers."},
 {"A": "拥有理想的藏书", "B": "保留详细的访客记录", "C": "发挥着多样化的功能", "D": "主要吸引年轻读者"}, "C"),
(23, "inference", "It is implied in Paragraph 5 that libraries should ______.",
 "第五段暗示，图书馆应该______。",
 {"A": "be given greater attention.", "B": "impose stricter visit limits.", "C": "work with private institutions.", "D": "get their equipment upgraded."},
 {"A": "得到更多关注", "B": "实施更严格的到访限制", "C": "与私营机构合作", "D": "升级设备"}, "A"),
(24, "inference", "The statistics mentioned in Paragraph 6 show ______.",
 "第六段提到的统计数据表明______。",
 {"A": "the crisis faced by libraries.", "B": "the advancement of libraries.", "C": "the contributions of libraries.", "D": "the flaws existing in libraries."},
 {"A": "图书馆面临的危机", "B": "图书馆的进步", "C": "图书馆的贡献", "D": "图书馆存在的缺陷"}, "A"),
(25, "detail", "Which of the following is suggested for libraries in the last paragraph?",
 "最后一段为图书馆提出了以下哪项建议？",
 {"A": "Inviting public feedback.", "B": "Seeking adequate funding.", "C": "Improving user convenience.", "D": "Offering lifetime memberships."},
 {"A": "邀请公众反馈", "B": "争取充足资金", "C": "提升用户便利性", "D": "提供终身会员资格"}, "C"),
]

# ============ Text 2 AI 职场 ============
AID = "text2"
T2 = [
(1, "According to our research, around one in five workers in the UK talk to AI like a friend, looking for guidance on personal and professional problems.",
 "根据我们的研究，英国约有五分之一的员工像朋友一样与 AI 交谈，就个人和职业问题寻求建议。"),
(1, "Our data shows that engaging with AI like this can leave us feeling heard and less isolated.",
 "我们的数据表明，像这样与 AI 互动可以让我们感到被倾听、不再那么孤立。"),
(1, "But, with this newfound connection, many of us share sensitive, sometimes highly confidential information, even though over a third of people don't realise that AI platforms may not be very good at keeping our secrets... secret.",
 "但有了这种新建立的连接，我们中的许多人都分享敏感、有时高度机密的信息，尽管超过三分之一的人没有意识到 AI 平台可能并不擅长保守我们的秘密。"),
(2, "For businesses, the implications are worrying.",
 "对企业来说，其影响令人担忧。"),
(2, "Consider Microsoft Copilot, for example.",
 "以微软 Copilot 为例。"),
(2, "It grants Microsoft broad rights to the data inputted or outputted by any user—rights to use this data in any way it sees fit; it can even share it with third parties.",
 "它赋予微软对任何用户输入或输出数据的广泛权利——以它认为合适的任何方式使用这些数据的权利；它甚至可以与第三方共享。"),
(2, "This means that any sensitive business information could potentially be exposed to the world.",
 "这意味着任何敏感的商业信息都有可能暴露于众。"),
(3, "Employers are taking note and taking action.",
 "雇主们正在关注并采取行动。"),
(3, "According to our research, 25% have decided to either outright ban AI or regulate its use within their organisations.",
 "根据我们的研究，25% 的雇主已决定要么彻底禁止 AI，要么在组织内部对其使用加以规范。"),
(3, "But even with these policies in place, some employees choose to break the rules.",
 "但即使制定了这些政策，一些员工仍然选择违规。"),
(3, "They have their reasons—around 63% of them report that using AI increases their productivity, and some even feel AI offers more help than their human colleagues.",
 "他们有他们的理由——约 63% 的人表示使用 AI 提高了工作效率，有些人甚至觉得 AI 比人类同事的帮助更大。"),
(4, "The situation presents a delicate balance between leveraging AI for its productivity gains and risking confidential data exposure.",
 "当前局面需要在利用 AI 提升生产力与冒机密数据泄露的风险之间取得微妙的平衡。"),
(4, "Employers need to manage AI tools with the same level of care as any other form of data sharing or storage.",
 "雇主需要像对待任何其他形式的数据共享或存储一样，以同样的谨慎来管理 AI 工具。"),
(4, "There's also a knowledge gap that needs to be addressed—40% of individuals surveyed are unsure about who retains ownership over the content produced by AI.",
 "还有一个需要填补的知识空白——40% 的受访者不确定 AI 生成内容的所有权归谁。"),
(4, "By instilling best practices in AI engagement and creating policies that evolve with the technology, businesses can positively shift the AI landscape.",
 "通过灌输 AI 使用的最佳实践、制定随技术发展而演变的政策，企业可以积极地改变 AI 格局。"),
(5, "With AI's potential to simplify our professional lives, do the admin and enhance the work experience, it's up to us to navigate its usage cautiously so it supports us without compromising our privacy.",
 "既然 AI 有简化职业生活、处理行政事务、提升工作体验的潜力，谨慎使用它、让它在不损害隐私的前提下支持我们，便是我们的责任。"),
(5, "There's no need to back away from progress, as long as we're equipped with the knowledge and tools to make sure AI remains a friend.",
 "只要我们掌握了让 AI 始终成为朋友的知识和工具，就没有必要回避进步。"),
(5, "And this is where the challenge lies.",
 "而挑战就在这里。"),
(5, "There are so many products out there, being promoted with huge advertising and marketing budgets, that it's easy to fall victim.",
 "市面上有太多产品，用巨额广告和营销预算推广，人们很容易上当受骗。"),
(5, "But by building a culture of digital responsibility within our business, we can create a future where AI can help us without spilling the beans.",
 "但只要在企业内部营造数字责任文化，我们就能创造一个 AI 帮助我们而又不泄露机密的未来。"),
]
T2_Q = [
(26, "detail", "According to Paragraph 1, workers' engagement with AI can ______.",
 "根据第一段，员工与 AI 的互动可以______。",
 {"A": "facilitate their career progress.", "B": "give them emotional support.", "C": "help maintain their motivation.", "D": "improve workplace communication."},
 {"A": "促进他们的职业发展", "B": "给他们情感支持", "C": "帮助保持他们的积极性", "D": "改善职场沟通"}, "B"),
(27, "detail", "Microsoft Copilot is cited to show that the use of AI may ______.",
 "引用微软 Copilot 是为了说明使用 AI 可能______。",
 {"A": "pose a threat to businesses.", "B": "generate unnecessary data.", "C": "promote business cooperation.", "D": "encourage information sharing."},
 {"A": "对企业构成威胁", "B": "产生不必要的数据", "C": "促进企业合作", "D": "鼓励信息共享"}, "A"),
(28, "detail", "Some employees choose to break the rules on AI due to ______.",
 "一些员工在 AI 问题上选择违规，是因为______。",
 {"A": "easy access to AI products.", "B": "the desire to stay well-informed.", "C": "its significant role in their work.", "D": "the need to compete with others."},
 {"A": "AI 产品易于获取", "B": "保持信息灵通的愿望", "C": "它在他们工作中的重要作用", "D": "与他人竞争的需要"}, "C"),
(29, "detail", "To positively shift the AI landscape, businesses should ______.",
 "要积极地改变 AI 格局，企业应该______。",
 {"A": "increase the transparency of their data sources.", "B": "prioritize the quality of AI-produced content.", "C": "include employee perspectives in their rules.", "D": "adjust their management to AI development."},
 {"A": "提高数据来源的透明度", "B": "优先保证 AI 生成内容的质量", "C": "在规则中纳入员工视角", "D": "让管理适应 AI 的发展"}, "D"),
(30, "inference", "According to the last paragraph, we may easily fall victim to AI as we ______.",
 "根据最后一段，我们很容易沦为 AI 的受害者，因为我们______。",
 {"A": "have a limited understanding of it.", "B": "underestimate its economic costs.", "C": "tend to overemphasise its power.", "D": "are excessively exposed to it."},
 {"A": "对它了解有限", "B": "低估了它的经济成本", "C": "倾向于夸大它的力量", "D": "过度接触它"}, "A"),
]

# ============ Text 3 意大利高铁 ============
AID = "text3"
T3 = [
(1, "Since the 2008 launch of the high-speed rail network between Rome and Milan, trains have become the preferred means of travel across Italy for locals and tourists alike.",
 "自 2008 年罗马与米兰之间的高铁网络开通以来，火车已成为意大利本地人和游客的首选出行方式。"),
(1, "Fast trains can cover the 500km between the two cities in three hours.",
 "高铁只需三个小时即可跑完两城之间 500 公里的路程。"),
(1, "The network also connects Naples, Bologna, Florence and Turin.",
 "该网络还连接那不勒斯、博洛尼亚、佛罗伦萨和都灵。"),
(1, "In many cases, it is the best option—in terms of travel time and cost—for both leisure and business travellers.",
 "在很多时候，就出行时间和成本而言，它都是休闲和商务旅客的最佳选择。"),
(2, "This is why the recent severe delays caused by numerous maintenance works have thrown the rail industry into chaos at a time when most people head on holiday, which matters for business in a country where tourism accounts for 10 per cent of GDP.",
 "正因如此，大量维护工程造成的严重延误，在多数人外出度假之际使铁路行业陷入混乱——而在一个旅游业占 GDP 10% 的国家，这对商业影响重大。"),
(3, "Disruptions have become increasingly frequent with train delays now a fixture in Italian media coverage.",
 "中断事件越来越频繁，火车晚点已成为意大利媒体报道的常客。"),
(3, "Ferrovie dello Stato Italiane, the publicly controlled group that owns train operator Trenitalia and the national train network RFI, said 23 per cent of high-speed trains it operated were late in 2023.",
 "意大利国家铁路集团（Ferrovie dello Stato Italiane）——这家公有集团旗下拥有列车运营商 Trenitalia 和国家铁路网 RFI——表示，2023 年其运营的高铁中有 23% 晚点。"),
(4, "The huge improvements in Italy's obsolete infrastructure partly explained the disruption, said Ferrovie.",
 "Ferrovie 表示，对意大利陈旧基础设施的大规模改造在一定程度上解释了这些中断。"),
(4, "RFI, the network operator, is the single largest European recovery fund beneficiary with planned investments of €24bn by 2026.",
 "网络运营商 RFI 是欧洲复苏基金最大的单一受益者，计划到 2026 年投资 240 亿欧元。"),
(4, "Ferrovie will invest a total of €124bn in infrastructure over the next 10 years.",
 "Ferrovie 未来 10 年将在基础设施上总共投资 1240 亿欧元。"),
(5, "But lack of capacity is another problem.",
 "但运力不足是另一个问题。"),
(5, "Transport economist Andrea Giuricin said the planned investments would bring improvements but disruptions in the meantime were inevitable.",
 "交通经济学家 Andrea Giuricin 表示，计划中的投资会带来改善，但与此同时中断在所难免。"),
(5, "'We have a mixed system, there is no spare capacity and as soon as there's a hiccup on the line, the situation becomes highly complex,' he said.",
 "他说：“我们的系统是混合的，没有富余运力，线路上一旦出点小故障，局面就会变得非常复杂。”"),
(6, "A mixed system means that high-speed trains must travel on the regular tracks on certain routes or when passing through large cities.",
 "混合系统意味着高铁在某些线路上或穿越大城市时，必须使用普通轨道行驶。"),
(6, "If there's congestion or, for example, a local train breaks down, the entire high-speed network is affected.",
 "如果出现拥堵，或者例如一列普速列车发生故障，整个高铁网络都会受到影响。"),
(7, "One of the most important changes the upgrades will bring is the segregation of the high-speed line from the regular one in certain urban centres through the construction of underground rail links.",
 "升级将带来的最重要变化之一，是通过修建地下铁路联络线，将某些城市中心的高铁线与普速线分离开来。"),
(8, "Improvements will also come from the high-density technology and satellite signalling that RFI has been investing in for years, say experts.",
 "专家表示，改善还将来自 RFI 多年投资的高密度技术和卫星信号系统。"),
(8, "It will allow for a reduction of the distance between high-speed trains travelling on the same line at any given time, which should mean a significant increase in capacity and traffic fluidity, according to Giuricin.",
 "据 Giuricin 称，这将允许减少同一线路上同一时间行驶的高铁列车之间的间距，意味着运力和通行顺畅度将显著提升。"),
]
T3_Q = [
(31, "detail", "According to the first two paragraphs, the high-speed rail network in Italy ______.",
 "根据前两段，意大利的高铁网络______。",
 {"A": "is seen by tourists as outdated.", "B": "is a popular option for travelling.", "C": "is inadequately utilised by locals.", "D": "is an example of good maintenance."},
 {"A": "被游客视为过时", "B": "是受欢迎的出行选择", "C": "被当地人利用不足", "D": "是维护良好的典范"}, "B"),
(32, "detail", "Ferrovie is quoted in Paragraph 3 to show ______.",
 "第三段引用 Ferrovie 是为了说明______。",
 {"A": "the common occurrence of train delays.", "B": "the value of the Italian train network.", "C": "the wide media coverage of trains.", "D": "the high efficiency of Trenitalia."},
 {"A": "火车晚点的普遍性", "B": "意大利铁路网络的价值", "C": "媒体对火车的广泛报道", "D": "Trenitalia 的高效率"}, "A"),
(33, "detail", "Which of the following is one cause of the disruptions in the network?",
 "以下哪项是网络中断的原因之一？",
 {"A": "Complex train schedules.", "B": "Shortage of investments.", "C": "Its limited capacity.", "D": "Its massive scale."},
 {"A": "复杂的列车时刻表", "B": "投资短缺", "C": "运力有限", "D": "规模庞大"}, "C"),
(34, "inference", "It can be learned that the mixed system ______.",
 "可以得知，混合系统______。",
 {"A": "provides a wide choice of routes.", "B": "requires extra operational spending.", "C": "increases the level of travel comfort.", "D": "puts the high-speed network in trouble."},
 {"A": "提供了广泛的路线选择", "B": "需要额外的运营支出", "C": "提升了出行的舒适度", "D": "使高铁网络陷入困境"}, "D"),
(35, "detail", "Improvements to the Italian train network will ______.",
 "对意大利铁路网络的改进将______。",
 {"A": "reconstructing the regular train lines.", "B": "shortening high-speed train intervals.", "C": "building more stations in urban centres.", "D": "enhancing the safety of high-speed trains."},
 {"A": "重建普通铁路线路", "B": "缩短高铁发车间隔", "C": "在城市中心修建更多车站", "D": "提高高铁的安全性"}, "B"),
]

# ============ Text 4 芝加哥街头节庆 ============
AID = "text4"
T4 = [
(1, "In 2023, Chicago lost one of its most beloved street festivals.",
 "2023 年，芝加哥失去了它最受欢迎的街头节庆之一。"),
(1, "The Silver Room Block Party, staged by Hyde Park community leader Eric Williams, announced it would not return in 2024.",
 "由海德公园社区领袖 Eric Williams 主办的银屋街区派对宣布，2024 年将不再举办。"),
(1, "What began as a small neighborhood gathering blossomed into a massive cultural event, welcoming tens of thousands of people each year over nearly two decades before abruptly shutting down.",
 "这场最初只是小型邻里聚会的活动，在近二十年间发展成每年吸引数万人的大型文化盛事，却突然停办了。"),
(2, "Williams pointed to rising production costs and declining attendee donations as primary reasons the Silver Room Block Party could not continue, highlighting a reality that all street festival organizers face right now.",
 "Williams 指出，制作成本上涨和观众捐赠减少是银屋街区派对难以为继的主要原因，这也凸显了当下所有街头节庆主办方面临的现实。"),
(2, "The cost of producing a street festival in Chicago has skyrocketed.",
 "在芝加哥举办一场街头节庆的成本已大幅飙升。"),
(2, "Security, entertainment, portable restrooms, insurance and even basics such as fencing and staffing have all become significantly more expensive.",
 "安保、演出、移动公厕、保险，甚至围栏和人工等基础开支都变得昂贵得多。"),
(2, "At the same time, donations at festival gates have dropped dramatically.",
 "与此同时，节庆入口处的捐赠大幅下降。"),
(3, "Chicago's summer festivals are about more than just entertainment; they are economic engines that directly benefit the neighborhoods they're in and the city of Chicago as a whole.",
 "芝加哥的夏日节庆不只是娱乐；它们是直接惠及所在社区乃至整个芝加哥市的经济引擎。"),
(3, "Street festivals drive foot traffic to local businesses and foster the kind of cultural vibrancy that makes our city special.",
 "街头节庆为本地商家带来客流，并营造出让我们这座城市与众不同的文化活力。"),
(4, "We often hear people ask why we solicit donations at our entry points, especially when the city's largest festivals like the Chicago Jazz Festival do not request donations.",
 "我们常听到人们问，为什么我们要在入口处募集捐款，尤其当芝加哥爵士音乐节这样的全市最大节庆并不要求捐款时。"),
(4, "The fact is, unlike those large, city-produced music festivals, your neighborhood street festivals receive no city funding and rely on a combination of sponsorships, vendor fees and gate donations to cover their costs.",
 "事实是，与那些由政府主办的大型音乐节不同，社区街头节庆拿不到市政拨款，只能依靠企业赞助、摊贩费用和入口捐赠来支付成本。"),
(5, "Wicker Park Fest has long been one of Chicago's most anticipated summer festivals, drawing upward of 70,000 attendees for a full weekend of live indie music, local art, small business vendors and, most importantly, community connection.",
 "威克公园节庆一直是芝加哥最受期待的夏日活动之一，一个完整周末能吸引七万多名参与者，现场有独立音乐演出、本土艺术、小商户摊位，最重要的是社区联结。"),
(5, "In 2024, Wicker Park Fest saw record-breaking attendance.",
 "2024 年，威克公园节庆到场人数创下历史新高。"),
(5, "Despite the turnout, gate donations reached their lowest point in our history.",
 "尽管人气如此之高，入口捐赠却跌至我们历史上的最低点。"),
(5, "This year, we've been forced to scale back the footprint of the fest.",
 "今年，我们被迫缩减节庆的举办规模。"),
(5, "We are eliminating a stage, booking fewer performers and making additional cuts to reduce our costs, all while striving to keep the festival as vibrant as ever, as supportive of local artists and businesses, and as true to Wicker Park's unique spirit and reputation as festgoers have come to expect.",
 "我们撤掉一个舞台、减少签约艺人，并进一步压缩开支以降低成本，同时努力让节庆保持往日的活力，一如既往地支持本地艺术家和商户，不负观众对威克公园独特精神与口碑的期待。"),
(6, "This summer, as you enjoy your favorite neighborhood street festival, I hope you'll remember that they exist because of community support.",
 "今年夏天，当你在享受喜爱的社区街头节庆时，我希望你记得：它们的存在依靠的是社区的支持。"),
(6, "A thriving summer festival season doesn't happen by accident; it happens when we all chip in.",
 "一个热闹的夏日节庆季不会凭空而来；它发生在大家共同出力之时。"),
]
T4_Q = [
(36, "inference", "It can be learned from Paragraph 1 that the Silver Room Block Party ______.",
 "从第一段可以得知，银屋街区派对______。",
 {"A": "has been replaced by other festivals.", "B": "has gained great international fame.", "C": "was held in various neighborhoods.", "D": "was an appealing cultural gathering."},
 {"A": "已被其他节庆取代", "B": "获得了巨大的国际声誉", "C": "曾在多个社区举办", "D": "曾是一场极具吸引力的文化聚会"}, "D"),
(37, "detail", "One reality street festival organizers face is that ______.",
 "街头节庆主办方面临的一个现实是______。",
 {"A": "they are unable to use the donations wisely.", "B": "they are unable to get sufficient facilities.", "C": "they have to tackle financial difficulties.", "D": "they have to step up security measures."},
 {"A": "他们无法合理使用捐赠", "B": "他们无法获得足够的设施", "C": "他们必须应对资金困难", "D": "他们必须加强安保措施"}, "C"),
(38, "detail", "According to Paragraphs 3 and 4, Chicago's street festivals ______.",
 "根据第三、四段，芝加哥的街头节庆______。",
 {"A": "reflect typical urban lifestyles.", "B": "are funded by the government.", "C": "contribute to the local economy.", "D": "are famous for their music shows."},
 {"A": "反映典型的都市生活方式", "B": "由政府出资", "C": "带动地方经济发展", "D": "以音乐演出著称"}, "C"),
(39, "inference", "It is implied that the organizers of Wicker Park Fest have to ______.",
 "文章暗示，威克公园节庆的主办方不得不______。",
 {"A": "count on amateur artists' participation.", "B": "reduce the number of performances.", "C": "give up its most prominent feature.", "D": "collaborate with large businesses."},
 {"A": "依靠业余艺人的参与", "B": "减少演出场次", "C": "放弃它最突出的特色", "D": "与大型企业合作"}, "B"),
(40, "attitude", "The author holds that the future of street festivals depends on ______.",
 "作者认为，街头节庆的未来取决于______。",
 {"A": "the variety of activities.", "B": "the generosity of attendees.", "C": "the reputation of neighborhoods.", "D": "the management of expenditures."},
 {"A": "活动的多样性", "B": "观众的慷慨捐助", "C": "社区的声誉", "D": "开支的管理"}, "B"),
]

# ============ 完形填空 ============
AID = "cloze"
CLOZE = [
(1, "Most of us strive for self-respect—to see ourselves in a positive light, to be _1_ of who we are.",
 "我们多数人都努力维护自尊——以积极的态度看待自己，为自己的身份感到自豪。"),
(1, "Any comments or experiences that undermine those feelings of self-worth can be uncomfortable and it's only _2_ to want to avoid them.",
 "任何削弱自我价值感的话语或经历都会让人不适，想要避开它们完全是人之常情。"),
(1, "But the thing is, _3_ your self-worth really is being undermined is, to a large degree, subjective.",
 "但问题是，你的自我价值是否真的受到损害，在很大程度上是主观的。"),
(1, "Much of it comes down to your _4_ of what someone said or did.",
 "这在很大程度上取决于你如何理解别人的言行。"),
(2, "When you take things personally, you're interpreting these situations as saying something significant and negative about you as a person.",
 "当你凡事往自己身上揽时，你会把这些情况解读为对你个人意义重大且负面的评价。"),
(2, "Say your boss picks holes in your sales report, and you come away feeling like this means she thinks you're a _5_ member of staff.",
 "比如老板在你的销售报告里挑毛病，你就觉得这说明她认为你是个能力差的员工。"),
(2, "Or, two of your friends cancel your _6_ get-together at the pub and you interpret this as meaning they're bored of you.",
 "或者，两个朋友取消了和你约好的酒吧聚会，你就把这解读为他们厌倦了你。"),
(2, "Psychologists have a _7_ for this way of thinking: personalisation.",
 "心理学家为这种思维方式起了一个名称：个人化归因。"),
(2, "But the _8_ is that your boss might view you very highly.",
 "但事实可能是，你的老板非常看重你。"),
(2, "It's just you made some _9_ in the report and she wanted to point these out so that you do better next time.",
 "只不过你在报告里犯了错，她想指出来让你下次做得更好。"),
(2, "_10_, in the case of your friends cancelling, perhaps they both felt unwell that weekend or they just _11_ their minds.",
 "同样，就朋友取消聚会而言，也许他们那个周末都不舒服，或者只是改变了主意。"),
(3, "In both _12_—and others that we all experience—there's another _13_ at work that psychologists call mind reading.",
 "在这两个例子以及我们都经历过的其他情形中，还有另一种心理机制在起作用，心理学家称之为读心术。"),
(3, "This is when you assume you know what other people are thinking about you, when you can't really know without _14_ them directly.",
 "所谓读心术，就是在你其实无法确定、只能直接去问才能知道的情况下，却自以为了解别人对你的看法。"),
(4, "One simple way to avoid _15_ personalisation and mind reading is to challenge your negative assumptions of what's _16_.",
 "避免陷入个人化归因和读心术的一个简单方法，是质疑自己对已发生之事的消极假设。"),
(4, "When you find yourself taking a situation personally, try to think of other interpretations that are less focused on you—especially in the sense of saying anything deep or _17_ about you.",
 "当你发现自己把事情往自己身上揽时，试着想想其他不那么以你为中心的解读——尤其是那些不会说你什么深层次或根本性问题的话。"),
(5, "When you do this, it might help to try to put yourself in other people's shoes.",
 "这样做时，试着设身处地站在别人的角度思考可能会有帮助。"),
(5, "The fact your boss took the time to give you _18_ at all means they care enough to want to help you _19_.",
 "老板肯花时间给你反馈，本身就意味着他足够关心你、想帮助你进步。"),
(5, "When it comes to your friends—maybe it's because your friendship is so _20_ that they felt able to cancel at late notice.",
 "至于你的朋友——也许正是因为你们的友谊如此深厚，他们才觉得可以临时取消约会。"),
]
CLOZE_OPTS = {
1: ({"A":"afraid","B":"critical","C":"proud","D":"tolerant"}, "C"),
2: ({"A":"risky","B":"natural","C":"admirable","D":"foolish"}, "B"),
3: ({"A":"whether","B":"where","C":"why","D":"how"}, "A"),
4: ({"A":"citation","B":"imitation","C":"perception","D":"introduction"}, "C"),
5: ({"A":"poor","B":"loyal","C":"creative","D":"shy"}, "A"),
6: ({"A":"sponsored","B":"crowded","C":"disputed","D":"planned"}, "D"),
7: ({"A":"method","B":"term","C":"design","D":"goal"}, "B"),
8: ({"A":"evidence","B":"theory","C":"condition","D":"reality"}, "D"),
9: ({"A":"complaints","B":"choices","C":"mistakes","D":"suggestions"}, "C"),
10: ({"A":"Similarly","B":"Relatively","C":"Accordingly","D":"Contrarily"}, "A"),
11: ({"A":"opened","B":"changed","C":"trained","D":"cleared"}, "B"),
12: ({"A":"quotations","B":"experiments","C":"questions","D":"examples"}, "D"),
13: ({"A":"process","B":"objective","C":"outcome","D":"background"}, "A"),
14: ({"A":"blaming","B":"warning","C":"teaching","D":"asking"}, "D"),
15: ({"A":"arguing about","B":"accounting for","C":"engaging in","D":"interfering with"}, "C"),
16: ({"A":"happened","B":"continued","C":"returned","D":"disappeared"}, "A"),
17: ({"A":"casual","B":"obvious","C":"familiar","D":"fundamental"}, "D"),
18: ({"A":"reward","B":"feedback","C":"trust","D":"proof"}, "B"),
19: ({"A":"innovate","B":"concentrate","C":"improve","D":"relax"}, "C"),
20: ({"A":"strange","B":"strong","C":"vulnerable","D":"valuable"}, "B"),
}
CLOZE_CN = {"proud":"自豪的","natural":"自然的，正常的","whether":"是否","perception":"认知，看法","poor":"差的，糟糕的","planned":"计划好的","term":"术语，名称","reality":"现实，事实","mistakes":"错误","Similarly":"类似地","changed":"改变（了主意）","examples":"例子","process":"过程，机制","asking":"询问","engaging in":"从事，陷入","happened":"发生","fundamental":"根本的，基本的","feedback":"反馈","improve":"改进，提高","strong":"深厚的，牢固的"}
def cloze_questions():
    qs = []
    for num in range(1, 21):
        opts, ans = CLOZE_OPTS[num]
        stem = f"第{num}题（完形填空）: 选择最佳选项"
        qs.append({"id": f"2026_cloze_q{num}", "number": num, "qtype": "cloze",
                   "stem": stem, "stem_cn": "选择最佳词填入空格",
                   "options": opts,
                   "options_cn": {k: CLOZE_CN.get(v, v) for k, v in opts.items()},
                   "answer": ans, "explanation": "", "related_sentences": []})
    return qs

# ============ 翻译 ============
AID = "translation"
TRANS = [
(1, "The influence of wearables on psychology refers to how the clothes we wear affect our thoughts, feelings, and behaviors.",
 "可穿戴服饰对心理的影响，指的是我们所穿着的衣物如何影响我们的思维、情感和行为。"),
(1, "Clothing is not just about covering our bodies; it plays a significant role in shaping our self-perception and interactions with others.",
 "服装不仅仅是为了遮体，它在塑造自我认知以及与他人的互动中发挥着重要作用。"),
(1, "One aspect of this influence is self-expression. The clothes we choose can reflect our personality, mood, and identity.",
 "这种影响的一个方面是自我表达。我们所选择的衣物可以反映出我们的个性、情绪和身份认同。"),
(1, "Whether we opt for bold, colorful outfits or prefer more understated styles, our dress choices convey messages about who we are and how we want to be perceived.",
 "无论我们选择大胆鲜艳的着装，还是偏爱更为低调的风格，我们的穿衣选择都在传递关于我们是谁以及我们希望如何被看待的信息。"),
(1, "Additionally, clothing can impact our confidence. When we wear clothes that make us feel comfortable and confident, it can positively affect our self-esteem and overall mood.",
 "此外，着装能够影响我们的自信心。当我们穿着那些让我们感到舒适和自信的衣服时，这能够对我们的自尊心和整体情绪产生积极的影响。"),
(1, "Moreover, cultural and social influences play a significant role in shaping our dress choices.",
 "再者，文化和社会的影响在塑造我们的穿衣选择方面起着重要作用。"),
(1, "Different cultures have their own norms and expectations regarding dress, which can influence the types of clothing people wear and the meanings attributed to them.",
 "不同的文化对于着装有着各自的规范和期望，这会影响人们穿着的服装类型及其被赋予的意义。"),
]

# ============ 写作 ============
WRITING_A = {
 "directions": "Suppose you are Li Ming. Your friend Jack has just posted a video about his travel on social media. Write him an email to share your views on it. You should write about 100 words.",
 "directions_cn": "假设你是李明。你的朋友杰克刚刚在社交媒体上发布了一段关于他旅行的视频。请给他写一封邮件，谈谈你对这段视频的看法。词数约 100 词。",
 "sample_en": """Dear Jack,

I just finished watching your travel video, and I was absolutely captivated by it! The landscapes you filmed were breathtaking, and the way you captured the local culture felt so genuine and immersive. It truly felt like I was traveling alongside you.

The segment about the traditional village particularly caught my interest. The architecture and daily life there looked fascinating. I'd love to hear more about your experiences there and any other interesting stories from your trip that didn't make it into the video.

Looking forward to catching up soon and hearing all about your adventures in more detail.

Best regards,
Yours sincerely,
Li Ming""",
 "sample_cn": """亲爱的杰克：

我刚看完你的旅行视频，完全被它吸引住了！你拍摄的风景令人叹为观止，你捕捉当地文化的方式如此真实而身临其境，感觉就像和你一起旅行一样。

其中关于传统村庄的那一段尤其引起我的兴趣。那里的建筑和日常生活看起来非常迷人。我很想多听听你在那里的经历，以及视频里没有剪进去的其他旅行趣事。

期待尽快与你叙旧，听你详细分享冒险经历。

此致
敬礼
李明""",
}
WRITING_B = {
 "directions": "Write an essay based on the following chart. In your writing, you should 1) describe and interpret the chart, and 2) give your comments. You should write about 150 words.",
 "directions_cn": "根据下面的图表写一篇短文。写作中应：1）描述并解读图表；2）发表你的评论。词数约 150 词。",
 "sample_en": """The chart presents the findings of a survey on the perceived benefits of children's outdoor activities. According to the data, "satisfying curiosity" and "improving observation skills" are considered the most significant advantages, each recognized by 54.5% and 54.6% of respondents respectively. Following closely, "enhancing physical fitness" is acknowledged by 33.2% of participants, while "strengthening parent-child interaction" is valued by 31.2%.

This data reveals a profound shift in parental focus, prioritizing cognitive and exploratory development over purely physical outcomes. The high value placed on curiosity and observation suggests an awareness that outdoor environments serve as vital, unstructured classrooms where children learn through discovery and sensory engagement. Meanwhile, the recognition of parent-child interaction highlights an understanding of the relational and emotional benefits derived from shared outdoor experiences.

In an age dominated by digital screens, these findings underscore a collective yearning for reconnection with the natural world as a foundation for holistic growth. In conclusion, the survey underscores that outdoor activities are not merely recreational but essential for nurturing inquisitive, observant, and well-rounded individuals. Parents and educators should therefore actively create and protect opportunities for children to explore, play, and connect outdoors.""",
 "sample_cn": """该图表呈现了一项关于儿童户外活动益处认知的调查结果。数据显示，"满足好奇心"和"提升观察能力"被认为是最重要的益处，分别得到 54.5% 和 54.6% 受访者的认可。紧随其后，"增强体质"得到 33.2% 受访者的认同，而"增进亲子互动"得到 31.2% 的认同。

这一数据揭示了家长关注点的深刻转变——他们更看重认知与探索能力的发展，而非单纯的体能成果。对好奇心和观察力的高度重视，表明人们意识到户外环境是重要的非结构化课堂，孩子们在探索和感官体验中学习。与此同时，对亲子互动的认可，凸显了人们理解共同户外体验所带来的情感与关系层面的益处。

在数字屏幕主导的时代，这些发现凸显了人们渴望重新与自然建立联系、将其作为全面发展基础的集体诉求。总之，这项调查表明，户外活动不仅是娱乐，更是培养好奇、善于观察、全面发展的个体的必要途径。家长和教育者应当积极创造并守护孩子们在户外探索、玩耍和联结的机会。""",
}

# ============ 组装 ============
def article(tid, title, topic, sents, qs, extra=None):
    a = {"id": f"2026_{tid}", "type": tid, "title": title, "topic": topic,
         "source": "2026 年考研英语（二）真题 · 多源交叉核验（新东方/海文/希赛/人人文库）",
         "sentences": mk_sentences(sents), "questions": qs}
    if extra: a.update(extra)
    return a

articles = [
    article("text1", "公共图书馆的多元社会价值", "公共图书馆的多元社会价值",
            T1, mk_questions(T1_Q, "text1", 21)),
    article("text2", "职场 AI 互动：便利与隐私的平衡", "职场 AI 互动：便利与隐私的平衡",
            T2, mk_questions(T2_Q, "text2", 26)),
    article("text3", "意大利高铁：运力与延误的困境", "意大利高铁：运力与延误的困境",
            T3, mk_questions(T3_Q, "text3", 31)),
    article("text4", "芝加哥街头节庆的生存危机", "芝加哥街头节庆的生存危机",
            T4, mk_questions(T4_Q, "text4", 36)),
    article("cloze", "个人化归因：如何停止往自己身上揽", "个人化归因与读心术",
            CLOZE, cloze_questions()),
    article("translation", "可穿戴服饰对心理的影响", "可穿戴服饰对心理的影响",
            TRANS, []),
    article("writing_a", "回复邮件：谈论朋友的旅行视频", "小作文·回复邮件",
            [], [], extra={"directions": WRITING_A["directions"], "directions_cn": WRITING_A["directions_cn"],
                            "sample_en": WRITING_A["sample_en"], "sample_cn": WRITING_A["sample_cn"]}),
    article("writing_b", "图表作文：儿童户外活动的益处", "大作文·图表作文",
            [], [], extra={"directions": WRITING_B["directions"], "directions_cn": WRITING_B["directions_cn"],
                            "sample_en": WRITING_B["sample_en"], "sample_cn": WRITING_B["sample_cn"]}),
]

out = {"schema_version": 1, "exam": "en2", "year": 2026, "articles": articles}
p = os.path.join(BASE, "pwa", "data", "2026.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("wrote", p)
print("articles:", [(a["id"], len(a["sentences"]), len(a["questions"])) for a in articles])
