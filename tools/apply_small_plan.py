# -*- coding: utf-8 -*-
"""
小作文「真题套用示范」人工方案（2026-09-16）

每年：
  aid        题库里的文章 id
  title      示范标题
  typeId     信件类型（对应 small_writing.json 的 types）
  salutation 称呼（通知类写标题、落款留空）
  close      落款
  paras      段落 = [[ (bankId, idx, {槽位: (英文, 中文)}), ... ], ...]
             槽位值 **必须给 (en, cn) 二元组**：英文填进英文句、中文填进中文译文
  tips       套用建议

原则（与大作文一致）：
  · 示范文全部由句库句子拼成，**不自写句**；槽位按真题信息填
  · 同功能句不重复用；每句都能在句库中定位到来源（key_phrases.src）
  · 词数控制在 95~115（真题要求 about 100 words）
"""

V = 'small-2026-09-16'

PLAN = {
    # ---------------- 2010 感谢 + 邀请 ----------------
    '2010': {
        'aid': '2010_writinga', 'typeId': 'thanks',
        'title': '2010 真题套用示范 · Part A 感谢信（+ 发出邀请）',
        'salutation': 'Dear Michael,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}), ('p1s2', 5, {})],
            [('p2_thanks_s2', 0, {}), ('p2_thanks_s3', 0, {}),
             ('p2_invite_s2', 0, {
                 'join': ('visit', '来'),
                 'topic': ('China', '中国'),
                 'gain': ('a chance to see Chinese culture and daily life at first hand', '近距离感受中国文化和日常生活的机会')})],
            [('p3', 4, {'outcome': ('experience the country for yourself', '亲自体验这个国家')})],
        ],
        'tips': [
            '感谢类两句是固定搭配：先「表示由衷感谢」，再「说一件让你印象最深的事」（热情接待 + 耐心友善）。',
            '本题第二问是「欢迎对方适时访华」，所以再接一句<b>邀请类</b>句，三个槽位都换成该题信息。',
            '称呼写对方名字（题里只说 American colleague，用 Dear Michael 这类常见名）；落款用题目指定的 Li Ming。',
        ],
    },

    # ---------------- 2011 祝贺 + 建议 ----------------
    '2011': {
        'aid': '2011_writinga', 'typeId': 'congrats',
        'title': '2011 真题套用示范 · Part A 祝贺信（+ 给建议）',
        'salutation': 'Dear Cousin,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}), ('p1s2', 7, {})],
            [('p2_congrats_s2', 0, {
                'topic': ('the university entrance examination', '高考'),
                'quality': ('solid academic ability and years of steady effort', '扎实的学力和多年稳扎稳打的付出')}),
             ('p2_congrats_s3', 0, {
                 'effort': ('keep working for what you want', '为自己想要的东西持续努力'),
                 'topic': ('the long preparation for the exam', '备考那漫长的过程')}),
             ('p2_advice_s2', 1, {
                 'action': ('plan your studies', '规划学习'),
                 'topic': ('your interests in university life', '你在大学生活中的兴趣'),
                 'detail': ('your sense of direction at university', '你在大学里的方向感')})],
            [('p3', 3, {'purpose': ('help you settle into university life more smoothly', '帮助你更顺利地适应大学生活')})],
        ],
        'tips': [
            '祝贺类骨架 = 「具体夸什么」+「这份成绩从哪来」：{{topic}} 填录取这件事，{{quality}}/{{effort}} 填品质与付出。',
            '本题第二问是「如何为大学生活做准备」，第三句接<b>建议类</b>：{{action}} 是建议动作，{{detail}} 是这样做能看到什么。',
            '收尾用「以上建议是为了……」这句，比「期待回信」更贴建议类题目。',
        ],
    },

    # ---------------- 2012 投诉 ----------------
    '2012': {
        'aid': '2012_writinga', 'typeId': 'complaint',
        'title': '2012 真题套用示范 · Part A 投诉信（+ 要求解决）',
        'salutation': 'Dear Sir or Madam,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 10, {'topic': ('the electronic dictionary I bought from your online store', '我从贵网店购买的电子词典')})],
            [('p2_complaint_s2', 0, {'product': ('electronic dictionary', '电子词典')}),
             ('p2_complaint_s2', 1, {'problem': ('a serious system failure', '严重的系统故障')}),
             ('p2_complaint_s3', 0, {})],
            [('p3', 0, {
                'expect': ('arrange a replacement or a full refund', '安排换货或全额退款'),
                'deadline': ('the end of this week', '本周末')})],
        ],
        'tips': [
            '投诉信最忌「只说情绪不说事实」：第二句点名 {{product}}，第三句给出具体 {{problem}}（到货三天就出故障）。',
            '要求用<b>一句</b>说清即可（维修 / 换货 / 退款三选一），第三段再用「如能……将不胜感激」收口。',
            '写给客服中心且不知对方姓名时，称呼用 <b>Dear Sir or Madam,</b>（顶格 + 逗号）。',
        ],
    },

    # ---------------- 2013 告知 + 鼓励参加（义卖） ----------------
    '2013': {
        'aid': '2013_writinga', 'typeId': 'invite',
        'title': '2013 真题套用示范 · Part A 告知 + 鼓励参加（班级义卖）',
        'salutation': 'Dear classmates,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 0, {'topic': ('the charity sale for children in need', '为困境儿童举办的慈善义卖')})],
            [('p2s1', 2, {}),
             ('p2_notice_s2', 1, {
                 'topic': ('the charity sale', '本次义卖'),
                 'place': ('the school auditorium', '学校礼堂'),
                 'audience': ('classmates', '同学')}),
             ('p2_invite_s2', 0, {
                 'join': ('join', '参加'),
                 'topic': ('us in the charity sale', '我们这次义卖'),
                 'gain': ('a chance to do something meaningful for children in need', '为困境儿童做点实事的机会')})],
            [('p3', 1, {
                'expect': ('let me know if you can come', '告诉我你能否参加'),
                'topic': ('all the money raised', '所筹得的善款')})],
        ],
        'tips': [
            '本题两问 = 「告知细节」+「鼓励参加」：第二段先用<b>通知类</b>交代时间地点，再用<b>邀请类</b>拉人。',
            '{{place}} 一定要填具体场地（学校礼堂 / 操场），这是「细节」的评分点。',
            '写给同学用 <b>Dear classmates,</b>；收尾句的 {{topic}} 填「所筹善款」这类活动目标，句子才顺。',
        ],
    },

    # ---------------- 2014 介绍自己 + 征求意见 ----------------
    '2014': {
        'aid': '2014_writinga', 'typeId': 'intro',
        'title': '2014 真题套用示范 · Part A 介绍自己 + 征求意见',
        'salutation': 'Dear John,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 0, {'topic': ('our living habits and the life there', '我们的生活习惯以及那边的生活')})],
            [('p2_intro_s2', 2, {
                'habit1': ('keep the room clean and quiet', '保持房间整洁安静'),
                'habit2': ('cook simple meals at home', '在家做些简单的饭菜'),
                'advantage': ('a regular and healthy routine', '规律健康的生活节奏')}),
             ('p2_inquire_s2', 0, {}), ('p2_inquire_s3', 0, {})],
            [('p3', 0, {
                'expect': ('share your advice with me', '把你的建议告诉我'),
                'deadline': ('I move in next month', '我下个月搬进去之前')})],
        ],
        'tips': [
            '「介绍生活习惯」有现成句：{{habit1}}/{{habit2}} 各填一个具体习惯（作息、做饭、安静），{{advantage}} 填好处。',
            '「征求意见」用<b>询问类</b>两句：先说要问什么，再解释为什么问你（因为你熟悉那边情况）。',
            '收尾 {{deadline}} 给一个时间点（我下个月搬进去之前），比空泛的「期待回复」更像真实邮件。',
        ],
    },

    # ---------------- 2015 通知（招募志愿者） ----------------
    '2015': {
        'aid': '2015_writinga', 'typeId': 'notice',
        'title': '2015 真题套用示范 · Part A 通知（招募夏令营志愿者）',
        'salutation': 'Volunteers Needed for the Summer Camp', 'close': '',
        'paras': [
            [('p1s2', 2, {'topic': ('the summer camp for high school students', '面向高中生的夏令营')})],
            [('p2_notice_s2', 0, {
                'time': ('July 15', '7月15日'),
                'topic': ('the summer camp', '夏令营'),
                'audience': ('volunteers', '志愿者')}),
             ('p2_notice_s3', 0, {
                 'topic': ('the summer camp', '夏令营'),
                 'content1': ('academic workshops', '学业辅导'),
                 'content2': ('team-building games', '团队拓展游戏'),
                 'content3': ('outdoor field trips', '户外考察')}),
             ('p2_notice_s4', 0, {
                 'audience': ('volunteers', '志愿者'),
                 'requirement': ('sign up at the student union office before July 10', '于7月10日前到学生会办公室报名'),
                 'topic': ('the recruitment', '本次招募')})],
            [('p3', 5, {})],
        ],
        'tips': [
            '通知与书信的差别就在这里：**标题顶格代替称呼**，结尾不写落款（题目明确要求不写自己的名字和学校名）。',
            '「介绍活动」用通知类第二、三句：{{time}} 给时间，{{content1~3}} 三项并列列出活动内容——三项都填、不要漏。',
            '「招募志愿者」用第四句交代要求（报名方式 + 截止时间），再以「请仔细阅读并转告相关同学」收尾，这是通知的标准收尾句。',
        ],
    },

    # ---------------- 2016 感谢 + 建议（回信） ----------------
    '2016': {
        'aid': '2016_writinga', 'typeId': 'thanks',
        'title': '2016 真题套用示范 · Part A 感谢 + 建议（回信）',
        'salutation': 'Dear Jack,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 1, {}), ('p1s2', 5, {})],
            [('p2_thanks_s2', 1, {'topic': ('translation', '翻译')}),
             ('p2_advice_s2', 1, {
                 'action': ('work steadily', '稳步下功夫'),
                 'topic': ('translation', '翻译'),
                 'detail': ('your sense of how Chinese and English differ', '你对中英差异的敏感度')}),
             ('p2_advice_s3', 0, {'task': ('translate one short passage every day', '每天翻译一小段文字')})],
            [('p3', 4, {'outcome': ('make steady progress in translation', '在翻译上稳步进步')})],
        ],
        'tips': [
            '回信型题目第一句用 <b>I am so delighted to receive your letter.</b>（你确实收到了信），再用感谢句回应对方的祝贺。',
            '感谢类第二句可用「没有你的帮助我不可能……」，{{topic}} 填对方帮过你的事。',
            '两问都完成：先感谢、再给建议，建议用「建议类」两句（一句给做法、一句给可执行动作），不要两句都讲道理。',
        ],
    },

    # ---------------- 2017 接受邀请 + 介绍要点 ----------------
    '2017': {
        'aid': '2017_writinga', 'typeId': 'intro',
        'title': '2017 真题套用示范 · Part A 接受邀请 + 介绍要点',
        'salutation': 'Dear Professor Williams,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 0, {'topic': ('your invitation to give a presentation on Chinese culture', '你邀请我作一场关于中国文化的讲座')})],
            [('p2_intro_s2', 0, {
                 'topic': ('my presentation', '讲座内容'),
                 'subject': ('four key aspects of Chinese culture', '中国文化的四个主要方面'),
                 'feature': ('a balance between tradition and everyday life', '传统与日常生活的交融')}),
             ('p2_intro_s3', 0, {
                 'aspect1': ('traditional festivals, food and family life', '传统节日、饮食与家庭生活'),
                 'audience': ('international students', '留学生'),
                 'gain1': ('get a clearer picture of how Chinese people actually live', '更清楚地看到中国人真实的生活')}),
             ('p2_invite_s4', 0, {
                 'topic': ('the presentation', '这场讲座'),
                 'benefit': ('understand China a little better', '对中国多一些了解')})],
            [('p3', 4, {'outcome': ('enjoy the talk', '享受这场讲座')})],
        ],
        'tips': [
            '接受邀请不必写「我接受」三个字：来意句的 {{topic}} 填「这场邀请」本身，就完成了「接受」的功能。',
            '「介绍要点」用介绍类两句：先总述（几个方面 + 特点），再展开第一个要点（{{aspect1}}）。',
            '给教授写信落款用 <b>Yours sincerely,</b>；本题不需要对方回复，收尾用 I sincerely hope… 比 Please reply 更得体。',
        ],
    },

    # ---------------- 2018 道歉 + 另约时间 ----------------
    '2018': {
        'aid': '2018_writinga', 'typeId': 'apology',
        'title': '2018 真题套用示范 · Part A 道歉信（+ 另约时间）',
        'salutation': 'Dear Professor Smith,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 3, {'topic': ('the cancellation of my visit', '我取消此次拜访')})],
            [('p2_apology_s2', 1, {
                'fault': ('the sudden change in my schedule', '行程突变'),
                'topic': ('the planned visit', '原定的拜访'),
                'impact': ('great inconvenience', '诸多不便')}),
             ('p2_apology_s3', 0, {'cause': ('an urgent family matter', '家里有急事')}),
             ('p2_advice_s3', 0, {'task': ('let me know a date in early October that suits you', '告诉我十月初一个对你合适的日期')})],
            [('p3', 0, {
                'expect': ('let me know which date suits you', '告诉我哪个时间合适'),
                'deadline': ('the end of this month', '本月底')})],
        ],
        'tips': [
            '道歉信三段式：<b>承认问题 → 解释原因（但责任在我）→ 提出补救</b>。第二句的 {{impact}} 要写对方受到的影响，比只说 sorry 有力。',
            '{{cause}} 不要写成推责（The traffic was terrible），用「家里有急事」这类中性说法即可。',
            '本题第二问是「另约时间」，所以第三句接建议类（{{action}} 给新方案），最后一句请对方确认时间。',
        ],
    },

    # ---------------- 2019 建议（辩题 + 安排） ----------------
    '2019': {
        'aid': '2019_writinga', 'typeId': 'advice',
        'title': '2019 真题套用示范 · Part A 建议信（辩题 + 安排）',
        'salutation': 'Dear Professor Smith,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 9, {'topic': ('the topic of the debate on city traffic', '本次城市交通辩论赛的辩题')})],
            [('p2s1', 1, {}),
             ('p2_advice_s2', 1, {
                 'action': ('choose "Is Traffic Jam Caused by Poor Road Planning" as the topic', '选用「交通拥堵源于道路规划不足吗」作为辩题'),
                 'topic': ('city traffic', '城市交通'),
                 'detail': ('the quality of the debate on both sides', '正反双方交锋的质量')}),
             ('p2_advice_s3', 0, {'task': ('set the debate for next Friday afternoon in Room 302', '把辩论安排在下周五下午302教室')})],
            [('p3', 0, {
                'expect': ('confirm the topic and the date', '确认辩题和日期'),
                'deadline': ('this Friday', '本周五')})],
        ],
        'tips': [
            '两问 = 「建议辩题 + 说明安排」，正好各用一句建议类：第一句给辩题，第二句给时间地点。',
            '辩题写成<b>一个疑问句</b>（Is Traffic Jam Caused by…）才像辩题，这是本题的得分细节。',
            '收尾请对方确认，{{deadline}} 给明确时间点，避免「尽快」这类模糊表达。',
        ],
    },

    # ---------------- 2020 介绍古迹 + 旅行建议 ----------------
    '2020': {
        'aid': '2020_writinga', 'typeId': 'intro',
        'title': '2020 真题套用示范 · Part A 介绍古迹 + 旅行建议',
        'salutation': 'Dear Friends,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 4, {'topic': ('the Terracotta Army in Xi\u2019an', '西安的兵马俑')})],
            [('p2_intro_s2', 0, {
                'topic': ('the Terracotta Army', '兵马俑'),
                'subject': ('an army of over 8,000 life-size clay soldiers', '一支由八千多尊等身陶俑组成的军阵'),
                'feature': ('over 2,000 years of history', '两千多年历史')}),
             ('p2_intro_s3', 0, {
                 'aspect1': ('three large exhibition pits', '三个大型展示坑'),
                 'audience': ('visitors', '参观者'),
                 'gain1': ('gain a vivid sense of the Qin Dynasty', '获得对秦朝的鲜活感受')}),
             ('p2_advice_s2', 1, {
                 'action': ('book tickets online in advance', '提前在网上订票'),
                 'topic': ('the date of your visit', '参观的日期'),
                 'detail': ('your experience at the site', '你在遗址的参观体验')})],
            [('p3', 4, {'outcome': ('enjoy every moment of the tour', '享受参观的每一刻')})],
        ],
        'tips': [
            '「介绍景点」用介绍类两句：第一句给「是什么 + 特征」（数量 + 年代最好写），第二句展开一个看点。',
            '{{aspect1}} 填 three exhibition pits 这类<b>具体结构</b>，比说 beautiful 有效得多——这是内容分的来源。',
            '「旅行建议」不要新起一段，接一句建议类即可；写给一群人用 <b>Dear Friends,</b>。',
        ],
    },

    # ---------------- 2021 邀请（线上会议） ----------------
    '2021': {
        'aid': '2021_writinga', 'typeId': 'invite',
        'title': '2021 真题套用示范 · Part A 邀请信（线上会议）',
        'salutation': 'Dear Jack,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 6, {'topic': ('our monthly online reading session', '我们每月一次的线上读书会')})],
            [('p2s1', 2, {}),
             ('p2_notice_s2', 1, {
                 'topic': ('the online meeting', '本次线上会议'),
                 'place': ('Zoom', 'Zoom 线上平台'),
                 'audience': ('participants', '参会者')}),
             ('p2_invite_s2', 0, {
                 'join': ('join', '参加'),
                 'topic': ('us in the online meeting', '我们这次线上会议'),
                 'gain': ('a chance to share a famous writer from your own country', '分享贵国一位著名作家的机会')})],
            [('p3', 0, {
                'expect': ('confirm your attendance', '确认你是否参加'),
                'deadline': ('next Wednesday', '下周三')})],
        ],
        'tips': [
            '邀请信第二段 = 「安排细节 + 邀请理由」：先用通知类交代时间和平台，再用邀请类说明参加能得到什么。',
            '{{gain}} 填与本题主题相关的收益（分享自己国家的作家），这是「为什么值得来」的评分点。',
            '收尾请对方确认出席并给截止时间，是邀请信最稳的收尾方式。',
        ],
    },

    # ---------------- 2022 介绍 + 邀请（美食节） ----------------
    '2022': {
        'aid': '2022_writinga', 'typeId': 'invite',
        'title': '2022 真题套用示范 · Part A 介绍 + 邀请（校园美食节）',
        'salutation': 'Dear international students,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 4, {'topic': ('our campus food festival', '我们的校园美食节')})],
            [('p2_notice_s2', 1, {
                'topic': ('the food festival', '美食节'),
                'place': ('the Main Dining Hall', '学校主食堂'),
                'audience': ('international students', '留学生')}),
             ('p2_invite_s2', 0, {
                 'join': ('join', '参加'),
                 'topic': ('us in the food festival', '我们这次美食节'),
                 'gain': ('a taste of dishes from across China', '品尝中国各地美食的机会')}),
             ('p2_invite_s3', 0, {
                 'task': ('trying the local specialties', '品尝当地特色菜'),
                 'topic': ('the festival', '美食节'),
                 'gain': ('understand Chinese food culture first-hand', '亲身理解中国饮食文化')})],
            [('p3', 1, {
                'expect': ('come and join us', '前来参加'),
                'topic': ('the festival', '美食节')})],
        ],
        'tips': [
            '本题两问 = 「介绍美食节 + 邀请参加」：先点明活动地点，再发邀请，最后一句讲参加能获得什么。',
            '两处 {{gain}} 不要重复：第一处说「尝到什么」，第二处说「理解到什么」，形成递进。',
            '写给留学生群体用 <b>Dear international students,</b>；收尾用「请您参加以便活动更好开展」比 Thank you 更扣题。',
        ],
    },

    # ---------------- 2023 建议（二选一 + 理由） ----------------
    '2023': {
        'aid': '2023_writinga', 'typeId': 'advice',
        'title': '2023 真题套用示范 · Part A 建议信（二选一 + 理由）',
        'salutation': 'Dear David,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 1, {}),
             ('p1s2', 9, {'topic': ('which event to visit on Sunday', '周日该去看哪一个活动')})],
            [('p2s1', 1, {}),
             ('p2_advice_s2', 1, {
                 'action': ('go to the robot show', '去看机器人展'),
                 'topic': ('your choice', '你的选择'),
                 'detail': ('the direction technology is moving in', '技术发展的方向')}),
             ('p2_advice_s3', 0, {'task': ('book the tickets online in advance', '提前在网上订票')})],
            [('p3', 4, {'outcome': ('enjoy a memorable Sunday', '度过一个难忘的周日')})],
        ],
        'tips': [
            '「二选一」题必须<b>明确表态</b>：{{action}} 直接填 go to the robot show，不要写 it depends。',
            '「理由」用 {{detail}} 一句话交代即可，再补一句可执行建议（提前订票），两问就都完成了。',
            '回信型开头用 <b>I am so delighted to receive your letter.</b>，符合本题「朋友来信问」的场景。',
        ],
    },

    # ---------------- 2024 计划 + 征求意见 ----------------
    '2024': {
        'aid': '2024_writinga', 'typeId': 'intro',
        'title': '2024 真题套用示范 · Part A 计划 + 征求意见',
        'salutation': 'Dear Jack,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 8, {'topic': ('our survey plan on the protection of old houses', '我们关于老宅保护的调查计划')})],
            [('p2_intro_s2', 1, {
                 'topic': ('the survey', '这次调查'),
                 'content': ('interviews with local residents and on-site visits', '走访当地居民和实地勘察'),
                 'purpose': ('find out how these old houses can be better protected', '弄清如何更好地保护这些老宅')}),
             ('p2_inquire_s2', 1, {}), ('p2_inquire_s3', 0, {})],
            [('p3', 0, {
                'expect': ('tell me what you think of the plan', '告诉我你对这个计划的看法'),
                'deadline': ('next Monday', '下周一')})],
        ],
        'tips': [
            '「提出计划」用介绍类：{{content}} 填具体做法（走访 + 实地勘察），{{purpose}} 填目的，比只写 plan 有内容。',
            '「征求意见」用询问类两句（想问什么 + 为什么问你）；本题两人是搭档，问句可以直白一些。',
            '收尾把 {{deadline}} 写成 next Monday，并请对方直接给意见——本题不需要太多客套。',
        ],
    },

    # ---------------- 2025 介绍短剧 + 邀请参演 ----------------
    '2025': {
        'aid': '2025_writinga', 'typeId': 'invite',
        'title': '2025 真题套用示范 · Part A 介绍 + 邀请（短剧参演）',
        'salutation': 'Dear John,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 4, {'topic': ('a short play based on The Romance of the Three Kingdoms', '一部改编自《三国演义》的短剧')})],
            [('p2_intro_s2', 1, {
                'topic': ('the play', '这部短剧'),
                'content': ('the stories of strategy, loyalty and heroism in the novel', '小说中谋略、忠义与英雄气概的故事'),
                'purpose': ('bring a classic Chinese story to the stage', '把一个中国经典故事搬上舞台')}),
             ('p2_invite_s2', 0, {
                 'join': ('take a role in it', '出演其中一个角色'),
                 'topic': ('the play', '这部短剧'),
                 'gain': ('a deeper understanding of Chinese culture', '更深入地理解中国文化')}),
             ],
            [('p3', 1, {
                'expect': ('let me know your decision', '告诉我你的决定'),
                'topic': ('the play', '这部短剧')})],
        ],
        'tips': [
            '本题两问 = 「介绍短剧 + 邀请参演」：用介绍类点明改编来源和看点，再用邀请类发出邀请。',
            '{{content}} 写出小说的三个关键词（谋略、忠义、英雄气概），这是「介绍」部分最能得分的地方。',
            '再接一句通知类交代开拍时间，让「介绍」有具体信息；收尾请对方回复决定即可。',
        ],
    },

    # ---------------- 2026 观点分享（回复邮件） ----------------
    '2026': {
        'aid': '2026_writing_a', 'typeId': 'opinion',
        'title': '2026 真题套用示范 · 回复邮件（分享对旅行视频的看法）',
        'salutation': 'Dear Jack,', 'close': 'Yours sincerely,\nLi Ming',
        'paras': [
            [('p1s1', 0, {}),
             ('p1s2', 1, {'topic': ('your travel video', '你的旅行视频')})],
            [('p2_opinion_s2', 0, {'detail': ('the way you captured the local people and their daily life', '你镜头下当地人与他们的日常生活')}),
             ('p2_opinion_s3', 0, {}),
             ('p2_invite_s2', 0, {
                 'join': ('take me along on', '让我随行参加'),
                 'topic': ('your next trip', '你的下一次旅行'),
                 'gain': ('a chance to see the world through your camera', '透过你的镜头看世界的机会')})],
            [('p3', 4, {'outcome': ('keep sharing such wonderful moments with us', '继续与我们分享这样的美好瞬间')})],
        ],
        'tips': [
            '观点分享类目前只考过一次（2026），结构最简单：<b>分享看法 → 说清为什么 → 顺势回应</b>。',
            '{{detail}} 要具体（当地人与日常生活），空泛地说 interesting 拿不到内容分。',
            '本题要求「分享看法」而非「办事」，所以收尾不要写「期待回复」，用「希望继续分享」这类呼应主题的句子。',
        ],
    },
}
