# -*- coding: utf-8 -*-
"""小作文：md 之外的补充内容与分层规则（供 tools/build_small_writing.py 读取）

包含：
  1) EXTRA_BANKS —— md 缺的 4 个第二段类型（感谢 / 投诉 / 询问 / 观点分享），每类 2 组 × 3 句
  2) EXTRA_TYPES —— 这 4 类在「按信件类型」视图里的顺序
  3) GUIDE_MAP   —— 17 年真题（2010–2026 英语二 A 节）→ 类型 + 该挑哪些句
  4) DECISIONS   —— 选句决策（题干关键词 → 类型 → 挑哪几句）
  5) EXTRA_TOKENS_CN —— 新句子里用到的占位符中文说明
  6) 分层规则：MUST_SLOTS（必背槽位）/ FREQ3_SLOTS / TAG_RULES
"""

# ---------------- 1) 补的 4 类第二段展开句 ----------------
# 写法对齐 md 的句式（与真题 directions 对得上），带适用年份
EXTRA_BANKS = {
    'p2_thanks_s2': {
        'part': 2, 'type': '感谢', 'slot': 2,
        'label': '第二段 · 感谢类 第二句（具体谢什么）',
        'items': [
            ['I would like to express my heartfelt thanks for the warm reception you gave me during my stay.',
             '我想对你在我逗留期间给予的热情接待表示由衷的感谢。', '2010'],
            ['Without your generous help, I could never have made such progress in {{topic}}.',
             '没有你慷慨的帮助，我不可能在{{topic}}上取得这样的进步。', '2016'],
            ['Your timely support meant a great deal to me, and I truly appreciate it.',
             '你的及时支持对我意义重大，我由衷感激。', ''],
        ],
    },
    'p2_thanks_s3': {
        'part': 2, 'type': '感谢', 'slot': 3,
        'label': '第二段 · 感谢类 第三句（说影响 / 感受）',
        'items': [
            ['What impressed me most was your patience and kindness, which made me feel at home.',
             '最让我感动的是你的耐心与友善，让我感到宾至如归。', '2010'],
            ['Thanks to your encouragement, I have gained far more confidence than before.',
             '因为你的鼓励，我比以前自信多了。', '2016'],
            ['The experience you offered me has become one of my most treasured memories.',
             '你给我的这段经历已成为我最珍贵的回忆之一。', ''],
        ],
    },
    'p2_complaint_s2': {
        'part': 2, 'type': '投诉', 'slot': 2,
        'label': '第二段 · 投诉类 第二句（出了什么问题）',
        'items': [
            ['To my disappointment, the {{product}} I bought from your online store last week has failed to work properly.',
             '令我失望的是，上周在贵网店购买的{{product}}无法正常使用。', '2012'],
            ['Specifically, {{problem}} appeared only three days after it arrived.',
             '具体来说，到货才三天就出现了{{problem}}。', '2012'],
            ['What troubles me most is that the problem has seriously affected my daily study.',
             '最让我困扰的是，这个问题已经严重影响了我的日常学习。', ''],
        ],
    },
    'p2_complaint_s3': {
        'part': 2, 'type': '投诉', 'slot': 3,
        'label': '第二段 · 投诉类 第三句（要求怎么解决）',
        'items': [
            ['I would appreciate it if you could arrange a repair or a full refund as soon as possible.',
             '如果你能尽快安排维修或全额退款，我将不胜感激。', '2012'],
            ['I therefore request a replacement or a refund within the coming week.',
             '因此，我请求在下周内为我更换或退款。', ''],
            ['I have kept the receipt and am ready to provide any further information you may need.',
             '我已保留收据，并愿意提供你可能需要的任何进一步信息。', ''],
        ],
    },
    'p2_inquire_s2': {
        'part': 2, 'type': '询问', 'slot': 2,
        'label': '第二段 · 询问类 第二句（想问什么）',
        'items': [
            ['In particular, I would like to know how I can better adapt to the local way of life.',
             '具体而言，我想知道我怎样才能更好地适应当地的生活方式。', '2014'],
            ['More specifically, I am not sure whether my plan is practical, so I would value your opinion.',
             '更具体地说，我不确定我的计划是否可行，所以很想听听你的意见。', '2024'],
            ['Could you please tell me what I should pay special attention to before I set off?',
             '能否告诉我出发前需要特别注意什么？', ''],
        ],
    },
    'p2_inquire_s3': {
        'part': 2, 'type': '询问', 'slot': 3,
        'label': '第二段 · 询问类 第三句（说明为什么问你）',
        'items': [
            ['Since you are familiar with the situation there, your advice would be of great value to me.',
             '由于你对那边的情况很熟悉，你的建议对我会非常有价值。', '2014'],
            ['As you have lived there for years, your suggestions will help me avoid many unnecessary troubles.',
             '你在那里生活多年，你的建议能帮我省去许多不必要的麻烦。', ''],
            ['Any advice from you, however small, will be highly appreciated.',
             '你的任何建议，无论多小，我都十分感激。', ''],
        ],
    },
    'p2_opinion_s2': {
        'part': 2, 'type': '观点', 'slot': 2,
        'label': '第二段 · 观点类 第二句（我的看法）',
        'items': [
            ['To be honest, I am deeply impressed by what you shared, especially {{detail}}.',
             '说实话，你分享的内容让我印象很深，尤其是{{detail}}。', '2026'],
            ['In my view, it is far more than a simple record; it shows how travel broadens a person\u2019s mind.',
             '在我看来，它远不只是一段简单的记录，而是展现了旅行如何开阔一个人的心胸。', '2026'],
            ['If I may say so, it reflects your careful observation and genuine love for life.',
             '依我看，它体现了你细致的观察和对生活真诚的热爱。', ''],
        ],
    },
    'p2_opinion_s3': {
        'part': 2, 'type': '观点', 'slot': 3,
        'label': '第二段 · 观点类 第三句（为什么这样看）',
        'items': [
            ['What strikes me most is {{detail}}, which makes it stand out from ordinary travel records.',
             '最打动我的是{{detail}}，这让它从普通的旅行记录中脱颖而出。', '2026'],
            ['The reason is that such records help us rediscover the beauty of ordinary moments.',
             '原因在于，这类记录帮我们重新发现平凡时刻里的美好。', ''],
            ['Besides, sharing these moments brings people closer and invites more communication.',
             '此外，分享这些时刻让人与人更亲近，也带来了更多交流。', ''],
        ],
    },
}

EXTRA_TYPES = [
    {'id': 'thanks', 'name': '感谢信', 'banks': ['p1s1', 'p2s1', 'p2_thanks_s2', 'p2_thanks_s3', 'p3']},
    {'id': 'complaint', 'name': '投诉信', 'banks': ['p1s1', 'p2s1', 'p2_complaint_s2', 'p2_complaint_s3', 'p3']},
    {'id': 'inquire', 'name': '询问 · 征求意见', 'banks': ['p1s1', 'p2s1', 'p2_inquire_s2', 'p2_inquire_s3', 'p3']},
    {'id': 'opinion', 'name': '观点分享（回复邮件）', 'banks': ['p1s1', 'p2s1', 'p2_opinion_s2', 'p2_opinion_s3', 'p3']},
]

# 类型视图的展示顺序：6 类来自 md + 4 类补充
# 保留清单（人工挑，2026-09-15）：bankId → 保留的「md 原始顺序」序号
# 原则：同组内只留「角度不同」的句子；同一个模板换开头词的（First and foremost / At this stage /
#       In particular / A sensible step…）只留最万能的那一句。带真题示例的优先保留。
PRUNE = {
    # —— 第一段 ——
    'p1s1': {0, 1, 10},                       # 通用问候 / 回信 / 通知致谢（10 句同义问候 + 3 句会议纪要删掉）
    'p1s2': {0, 1, 2, 3, 5, 6, 9, 10, 15, 20, 21},   # 万能·感谢·邀请·祝贺·观点·通知·讨论·建议·道歉·介绍·投诉
    # —— 第二段通用首句 ——
    'p2s1': {0, 5, 12},                       # 通用引出 / 建议类 / 活动通知类
    # —— 建议类 ——
    'p2_advice_s2': {0, 3},
    'p2_advice_s3': {2},
    'p2_advice_s4': {0},
    # —— 邀请类 ——
    'p2_invite_s2': {0, 5},
    'p2_invite_s3': {2},
    'p2_invite_s4': {0},
    # —— 道歉类 ——
    'p2_apology_s2': {0, 4},
    'p2_apology_s3': {0},
    # —— 祝贺类 ——
    'p2_congrats_s2': {0, 1},
    'p2_congrats_s3': {0},
    'p2_congrats_s4': {0},
    # —— 介绍类 ——
    'p2_intro_s2': {0, 4, 7},                 # 介绍事物 / 介绍内容 / 介绍自己（2014 真题）
    'p2_intro_s3': {0},
    'p2_intro_s4': {0},
    # —— 通知类 ——
    'p2_notice_s2': {0, 1},
    'p2_notice_s3': {0},
    'p2_notice_s4': {0},
    # —— 第三段 ——
    'p3': {0, 2, 5, 11, 14, 18},              # 期待动作 / 通知被动 / 感谢回复 / 总结 / 展望 / 通知后续
    # —— 补充的 4 类（本来就 3 句一组，各留 2 + 1）——
    'p2_thanks_s2': {0, 1},
    'p2_thanks_s3': {0},
    'p2_complaint_s2': {0, 1},
    'p2_complaint_s3': {0},
    'p2_inquire_s2': {0, 1},
    'p2_inquire_s3': {0},
    'p2_opinion_s2': {0, 2},
    'p2_opinion_s3': {1},
}

TYPE_ORDER = ['advice', 'invite', 'thanks', 'congrats', 'apology', 'complaint', 'intro', 'notice', 'inquire', 'opinion']

EXTRA_TOKENS_CN = {
    'product': '有问题的商品 / 服务',
    'problem': '具体问题',
    'detail': '题目相关短语或词',
    'topic': '题目相关词',
}

# ---------------- 3) 17 年真题 → 类型 + 挑句指引 ----------------
GUIDE_MAP = {
    '2010': ('thanks', '感谢信（+ 邀请）', '感谢类 2 句；若要发出邀请，再加「邀请类 第 1 句」'),
    '2011': ('congrats', '祝贺信（+ 建议）', '祝贺类 2 句 + 建议类 第 1 句'),
    '2012': ('complaint', '投诉信', '投诉类 第 1 + 2 句（先讲问题、再提要求）'),
    '2013': ('invite', '邀请 / 告知（义卖）', '来意用「通知类」句；展开用「邀请类 第 1 + 2 句」'),
    '2014': ('inquire', '介绍自己 + 征求意见', '介绍类 第 1 句 + 询问类 第 1 + 2 句'),
    '2015': ('notice', '通知（招募志愿者）', '通知类 第 1 + 2 句'),
    '2016': ('thanks', '感谢 + 建议（回信）', '感谢类 第 1 句 + 建议类 2 句'),
    '2017': ('invite', '接受邀请 + 介绍要点', '邀请类 第 1 句（接受）+ 介绍类 第 1 句'),
    '2018': ('apology', '道歉信', '道歉类 2 句（先认错、再补救）'),
    '2019': ('advice', '建议信（辩题 + 安排）', '建议类 第 1 + 2 句'),
    '2020': ('intro', '介绍古迹 + 旅行建议', '介绍类 第 1 句 + 建议类 第 1 句'),
    '2021': ('invite', '邀请信（线上会议）', '邀请类 2 句（邀请 + 细节）'),
    '2022': ('invite', '介绍 + 邀请（美食节）', '介绍类 第 1 句 + 邀请类 第 1 句'),
    '2023': ('advice', '建议（二选一 + 理由）', '建议类 第 1 句 + 建议类 第 3 句（讲理由）'),
    '2024': ('inquire', '计划 + 征求意见', '询问类 第 1 + 2 句'),
    '2025': ('invite', '介绍短剧 + 邀请参演', '介绍类 第 1 句 + 邀请类 第 1 句'),
    '2026': ('opinion', '观点分享（回复邮件）', '观点类 第 1 + 2 句'),
}

# ---------------- 4) 选句决策 ----------------
DECISIONS = [
    {'q': '题干里的动词是？', 'a': 'apologize → 道歉类；invite / participate → 邀请类；suggest / advice → 建议类；'
                                  'congratulate → 祝贺类；complain → 投诉类；introduce / tell about → 介绍类；'
                                  'notice / volunteers → 通知类；thanks / gratitude → 感谢类；'
                                  'ask for your opinion → 询问类；share your views → 观点类。'},
    {'q': '第二段挑几句？', 'a': '只挑 <b>2 句</b>（约 45~55 词）。先挑 ⭐ 必背那句，再补一句同类型的。'
                                 '真题第二段大多就是「讲做法 + 讲理由/影响」两句。'},
    {'q': '称呼怎么写？', 'a': '不知道收信人：<b>Dear Sir or Madam,</b>；知道姓名：<b>Dear Jack,</b> / <b>Dear Prof. Smith,</b>。'
                               '顶格写，后面用逗号。'},
    {'q': '落款怎么写？', 'a': '正式：<b>Yours sincerely,</b>；朋友：<b>Best wishes,</b>；通知不用落款人名。'
                               '下一行写题目给的名字（Li Ming），不要写自己的真名。'},
    {'q': '考到没准备过的题材怎么办？', 'a': '来意句用 <b>I am writing to you regarding the matter of {{topic}}.</b>（万能），'
                                            '第二段一律用「建议类」或「介绍类」的 ⭐ 必背句顶——这两类最能兜底。'},
]

# ---------------- 6) 分层规则 ----------------
# 每个槽位的第 1 句 = 该槽位最通用的一句 → 必背（10 类 × 2 槽 + 4 个通用槽 = 24 句）
MUST_SLOTS = ['p1s1', 'p1s2', 'p2s1', 'p3']
# 整组都算「通用」的槽位（freq = 3）
FREQ3_SLOTS = ['p2s1']

# ---------------- 7) 评分老师视角（英二 A 节，10 分） ----------------
TEACHER = [
    ('格式分是白送的，也是最容易丢的',
     '称呼<b>顶格</b>写、以<b>逗号</b>结尾（Dear Sir or Madam,）；落款要 <b>Yours sincerely,</b> 或 <b>Best wishes,</b> 换个行写题目给的名字（Li Ming，<b>别写自己真名</b>）；'
     '通知类不写人名落款。段落数按题目要求（多数是 3 段）。这 4 件做对，格式与语域分稳拿；漏称呼或漏落款会直接掉一档。'),
    ('第二段最多写 2 句长句',
     '本库句子平均 15~16 词，第二段塞 3 句就冲到 110+ 词。<b>第二段固定 2 句</b>：一句讲做法、一句讲理由或要求；'
     '想再补信息，只补一个具体名词（活动名 / 地点 / 时间）塞进已有的句子里，别再加句子。'),
    ('万能句只保底，不拿高分',
     'I would appreciate it very much if…、Only in this way can you… 这类句子阅卷人一眼就认得：它们保证<b>语言分不掉</b>，'
     '但内容分要靠<b>题目里的具体信息</b>撑起来（真题里就是「电子词典」「古镇老宅」「校园美食节」这些词）。'
     '模板给你骨架，<b>血肉必须来自题干</b>。'),
    ('同一功能的句子，背一句就够',
     '这就是这次把 221 句删到 59 句的理由：原来 16 句问候其实等于 1 句，背 10 句是纯浪费，还容易在考场上纠结。'
     '现在每个槽位只留「角度不同」的 1~2 句，必背 24 句就把所有场景覆盖完了。'),
    ('考场 6 句成文（约 100 词）',
     '问候 1 句 + 来意 1 句 + 通用引出 1 句 + 类型展开 2 句 + 收尾 1 句 = <b>6 句 / 95~105 词</b>，正好落在要求区间'
     '（英语二 A 节约 100 词）。低于 90 词会因字数不足扣分，超过 130 词在 15 分钟内很难保证质量。'),
    ('分数预期：认真填槽 6~8 分（满分 10）',
     '格式齐全 + 语言基本准确 + 内容贴题 = 二档到三档；<b>拿 9~10 分必须内容扣住题干的具体信息</b>'
     '（这是任何模板都给不了的）。所以：模板背到能默写之后就不要再背了，去套真题、改错，把「具体名词」练出来。'),
]

TAG_RULES = [
    # (槽位前缀, 关键词正则, 标签)
    ('p1s1', r'notice|gratitude|appreciate all students|extend our thanks', '通知致谢'),
    ('p1s1', r'seminar|meeting minutes|graduation project|academic exchange', '会议纪要'),
    ('p1s2', r'gratitude|thanks for your help|heartfelt thanks', '感谢'),
    ('p1s2', r'invite', '邀请'),
    ('p1s2', r'congratulat', '祝贺'),
    ('p1s2', r'complaint', '投诉'),
    ('p1s2', r'apology|ask for your understanding', '道歉'),
    ('p1s2', r'suggestions|call your attention', '建议'),
    ('p1s2', r'notice|announced|carry out the following', '通知'),
    ('p1s2', r'seek your advice|in detail|discuss', '询问'),
    ('p1s2', r'recommend|introduce', '推荐 / 介绍'),
    ('p1s2', r'share my views', '观点'),
    ('p2s1', r'reasons|causes|justify', '归因'),
    ('p2s1', r'suggestions|measures|actions|recommended|help', '建议'),
    ('p2s1', r'arrangement|schedule|activity|event|notice|planned', '活动安排'),
    ('p2s1', r'details|points|steps|practical', '细节'),
    ('p3', r'summary|conclude|Taken together|efforts|arrangements', '总结 / 号召'),
    ('p3', r'firmly believe|joint efforts|hope that|It is my sincere hope', '展望'),
]

SLOT_TAGS = {
    's2': '具体展开',
    's3': '理由 / 深化',
    's4': '意义 / 号召',
}

# —— 按大作文规格优化（2026-09-16）：去烂大街 / 同义升级 / 高级衔接词 / 拼装框架 ——
# 句首烂大街衔接词 → 高级版（逐词替换进句子；注意替换后 ALTS 的 key 要对应新文本）
SWAP = [
    ('First and foremost, ', 'To begin with, '),
    ('Last but not least, ', 'Finally, '),
]
# 同义升级（key = 句子替换后的原文，value = 替换串，背一句会三句）
ALTS = {
    'I hope this message finds you well.': 'I hope this email reaches you well / I hope everything is going well with you.',
    'I am writing to you regarding the matter of {{topic}}.': 'I am writing to you about {{topic}} / This letter is intended to discuss {{topic}}.',
    'To be more specific, the main points can be arranged as follows.': 'The main points are as follows / To spell it out, the key points are these.',
    'I would appreciate it very much if you could {{expect}} by {{deadline}}.': 'I would be grateful if you could {{expect}} by {{deadline}} / Your early reply would be highly appreciated.',
    'I would like to express my heartfelt thanks for the warm reception you gave me during my stay.': 'I sincerely appreciate your warm hospitality during my stay.',
    'What impressed me most was your patience and kindness, which made me feel at home.': 'Your patience and kindness left a deep impression on me, making me feel at home.',
    'To my disappointment, the {{product}} I bought from your online store last week has failed to work properly.': 'Much to my regret, the {{product}} I purchased online last week does not work properly.',
    'In particular, I would like to invite you to {{join}} {{topic}}, which will offer you {{gain}}.': 'It is a great pleasure to invite you to {{join}} {{topic}}, which will offer you {{gain}}.',
    'In particular, I would like to know how I can better adapt to the local way of life.': 'I would be grateful to know how I can settle into the local way of life.',
    'I am so delighted to receive your letter.': 'I am truly glad to hear from you / It is a real pleasure to hear from you.',
}
# 高级衔接词（信件专用；banned = 烂大街，better = 高级替换）
LINKERS = [
    {'banned': 'First and foremost / Last but not least（句首烂大街）', 'better': 'To begin with, ... / Finally, ...（必背句里已换高级版）'},
    {'banned': 'In addition, ...', 'better': 'Besides this, ... / Beyond that, ...'},
    {'banned': 'Furthermore, ...', 'better': 'Equally important, ... / Just as significant, ...'},
    {'banned': 'I hope you can ...（请求太软）', 'better': 'I would appreciate it if you could ... / I would be grateful if you could ...'},
    {'banned': 'To be more specific, ...', 'better': 'To spell it out, ... / To put it another way, ...'},
]
# 信件拼装框架（5 步，所有信都这么拼）
FRAMEWORK = [
    {'en': 'I hope this message finds you well.', 'trans': '希望你一切安好。',
     'cn': '① 问候句：所有信通用；给老师/长辈换 Dear Professor / Dear Sir or Madam。'},
    {'en': 'I am writing to ...（invite you to / express my thanks for / make a complaint about ...）', 'trans': '我写信是为了……',
     'cn': '② 来意句：一句话点明写信目的——换动词就是另一种信（p1s2 里都是现成的）。'},
    {'en': 'To begin with, + 要点①（该类型 s2 必背句）', 'trans': '首先，……',
     'cn': '③ 主体第一点：衔接词开头 + 从第二段对应类型挑第 2 句。'},
    {'en': 'Equally important, + 要点②（s3 / 跨类型补 1~2 句）', 'trans': '同样重要的是，……',
     'cn': '④ 主体第二点：s3 或跨类型混搭；第二段 2~4 句就够。'},
    {'en': 'I would appreciate it if you could ... / Looking forward to your early reply.', 'trans': '如蒙……将不胜感激 / 期待您的早日回复。',
     'cn': '⑤ 收尾（p3 必背）：行动请求或期待回复；落款 Yours sincerely, Li Ming。'},
]

# ---------------- 整信背诵：10 类各一封精选润色范文（≥100 词正文） ----------------
# 结构：{'rows': [[src, en, cn], ...], 'cn_paras': [P1段译, P2段译, P3段译]}
#   src  = 来源 bank#idx（en 与来源一致时前端共享高亮键）；
#   cn_paras = 分三段的整体译文（点段末按钮展开，替代逐句翻译）。
# 选句思路：正文 ≥100 词；通知无问候句；感谢/祝贺/介绍/观点不带 p2s1 引出（自带衔接开头）；
# 第三段可双收尾（appreciate + thank you/look forward）；衔接节奏 To begin with -> In addition -> Finally。
LETTERS = {
    'advice': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#9', 'I would like to offer a few suggestions on {{topic}}, which I hope may be of use to you.', '我想就{{topic}}提几点建议，希望能对你有用。'],
            ['p2s1#1', 'As for the practical measures, my suggestions are as follows.', '至于具体措施，我的建议如下。'],
            ['p2_advice_s2#0', 'To begin with, I would suggest that you put {{ving}} {{topic}} into practice, as it can help you gain a deeper understanding of {{detail}}.', '首先，我建议你把{{ving}}{{topic}}付诸实践，这能帮你对{{detail}}有更深的理解。'],
            ['p2_advice_s3#0', 'In addition, you are advised to {{task}} so as to improve the situation.', '此外，建议你{{task}}，以便改善现状。'],
            ['p2_advice_s4#0', 'Finally, I would suggest that you {{task}}, which will help you {{benefit}} in the long run.', '最后，我建议你{{task}}，从长远看这会帮助你真正{{benefit}}。'],
            ['p3#0', 'I would appreciate it very much if you could {{expect}} by {{deadline}}.', '如果你能在{{deadline}}前{{expect}}，我将不胜感激。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。我想就{{topic}}提几点建议，希望能对你有用。',
            '至于具体措施，我的建议如下。首先，我建议你把{{ving}}{{topic}}付诸实践，这能帮你对{{detail}}有更深的理解。此外，建议你{{task}}，以便改善现状。最后，我建议你{{task}}，从长远看这会帮助你真正{{benefit}}。',
            '如果你能在{{deadline}}前{{expect}}，我将不胜感激。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'invite': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#6', 'It gives me great pleasure to invite you to {{topic}}.', '很高兴邀请你参加{{topic}}。'],
            ['p2s1#2', 'As for the planned event, the main arrangements are as follows.', '至于本次活动，具体安排如下。'],
            ['p2_invite_s2#0', 'In particular, I would like to invite you to {{join}} {{topic}}, which will offer you {{gain}}.', '具体而言，我想邀请你{{join}}{{topic}}，这将为你带来{{gain}}。'],
            ['p2_invite_s3#0', 'In addition, by {{task}} during {{topic}}, you will be able to {{gain}}, which is of great benefit to you.', '此外，在{{topic}}期间{{task}}，你将能够{{gain}}，这对你很有好处。'],
            ['p2_invite_s4#0', 'Finally, your presence will make {{topic}} more meaningful and enable you to {{benefit}}.', '最后，你的到来将使{{topic}}更有意义，也能让你{{benefit}}。'],
            ['p3#4', 'I sincerely hope that you will make full use of this opportunity to {{outcome}}.', '我衷心希望你能充分利用这次机会{{outcome}}。'],
            ['p3#0', 'I would appreciate it very much if you could {{expect}} by {{deadline}}.', '如果你能在{{deadline}}前{{expect}}，我将不胜感激。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。很高兴邀请你参加{{topic}}。',
            '至于本次活动，具体安排如下。具体而言，我想邀请你{{join}}{{topic}}，这将为你带来{{gain}}。此外，在{{topic}}期间{{task}}，你将能够{{gain}}，这对你很有好处。最后，你的到来将使{{topic}}更有意义，也能让你{{benefit}}。',
            '我衷心希望你能充分利用这次机会{{outcome}}。如果你能在{{deadline}}前{{expect}}，我将不胜感激。',
        ],
    },
    'thanks': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#5', 'I am truly grateful for the generous help you have given me.', '非常感谢你给予我的慷慨帮助。'],
            ['p2s1#0', 'To be more specific, the following are the things I am truly grateful for.', '具体来说，我真正感激的是以下几件事。'],
            ['p2_thanks_s2#0', 'I would like to express my heartfelt thanks for the warm reception you gave me during my stay.', '我想衷心感谢你在我逗留期间给予的热情接待。'],
            ['p2_thanks_s3#0', 'What impressed me most was your patience and kindness, which made me feel at home.', '最让我印象深刻的是你的耐心和友善，这让我感觉像在自己家一样。'],
            ['p2_thanks_s2#1', 'Without your generous help, I could never have made such progress in {{topic}}.', '若没有你慷慨的帮助，我不可能在{{topic}}上取得这样的进步。'],
            ['', 'Thanks again for your kindness, and I hope we can stay in touch.', '再次感谢你的善意，希望我们保持联系。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。非常感谢你给予我的慷慨帮助。',
            '具体来说，我真正感激的是以下几件事。我想衷心感谢你在我逗留期间给予的热情接待。最让我印象深刻的是你的耐心和友善，这让我感觉像在自己家一样。若没有你慷慨的帮助，我不可能在{{topic}}上取得这样的进步。',
            '再次感谢你的善意，希望我们保持联系。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'congrats': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#7', 'Please allow me to extend my warmest congratulations to you.', '请允许我向你致以最热烈的祝贺。'],
            ['p2_congrats_s2#0', 'To be more specific, your remarkable achievement in {{topic}} clearly shows your {{quality}}.', '更具体地说，你在{{topic}}上的出色表现清楚地展现了你的{{quality}}。'],
            ['p2_congrats_s2#1', 'As far as {{topic}} is concerned, your success in {{achievement}} is truly impressive and inspiring.', '就{{topic}}而言，你在{{achievement}}上的成功确实令人钦佩，也很鼓舞人心。'],
            ['p2_congrats_s3#0', 'To a large extent, this success comes from the sustained effort you have made in {{topic}}.', '在很大程度上，这一成功源于你在{{topic}}上持续付出的努力。'],
            ['p2_congrats_s4#0', 'Finally, this achievement in {{topic}} will surely encourage you to {{next step}}, helping you reach {{goal}}.', '最后，{{topic}}上的这一成就必将激励你{{next step}}，助你迈向{{goal}}。'],
            ['p3#4', 'I sincerely hope that you will make full use of this opportunity to {{outcome}}.', '我衷心希望你能充分利用这次机会{{outcome}}。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。请允许我向你致以最热烈的祝贺。',
            '更具体地说，你在{{topic}}上的出色表现清楚地展现了你的{{quality}}。就{{topic}}而言，你在{{achievement}}上的成功确实令人钦佩，也很鼓舞人心。在很大程度上，这一成功源于你在{{topic}}上持续付出的努力。最后，{{topic}}上的这一成就必将激励你{{next step}}，助你迈向{{goal}}。',
            '我衷心希望你能充分利用这次机会{{outcome}}。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'apology': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#3', 'Please accept my sincere apology for any inconvenience and trouble that {{topic}} has brought you.', '请接受我为{{topic}}给你带来的不便和麻烦所作的诚挚道歉。'],
            ['p2s1#0', 'To be more specific, what happened is as follows.', '具体来说，事情经过如下。'],
            ['p2_apology_s2#0', 'I must admit that {{fault}} on my part concerning {{topic}} has caused {{impact}}.', '我必须承认，{{topic}}上的{{fault}}造成了{{impact}}。'],
            ['p2_apology_s2#1', 'As a result of {{fault}} with regard to {{topic}}, you had to face {{impact}}, which should not have happened.', '由于我在{{topic}}方面{{fault}}，你不得不面对{{impact}}，这本不该发生。'],
            ['p2_apology_s3#0', 'Although {{cause}} partly explains why this happened, the main responsibility still lies with me.', '尽管{{cause}}能部分解释这件事，但主要责任仍在我。'],
            ['', 'I will make sure that this will not happen again.', '我保证这样的事不会再发生。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。请接受我为{{topic}}给你带来的不便和麻烦所作的诚挚道歉。',
            '具体来说，事情经过如下。我必须承认，{{topic}}上的{{fault}}造成了{{impact}}。由于我在{{topic}}方面{{fault}}，你不得不面对{{impact}}，这本不该发生。尽管{{cause}}能部分解释这件事，但主要责任仍在我。',
            '我保证这样的事不会再发生。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'complaint': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#10', 'It is with regret that I write to complain about the recent problems with {{topic}}.', '很遗憾，我不得不就近期{{topic}}出现的问题正式投诉。'],
            ['p2s1#0', 'To be more specific, what happened is as follows.', '具体来说，事情经过如下。'],
            ['p2_complaint_s2#0', 'To my disappointment, the {{product}} I bought from your online store last week has failed to work properly.', '令我失望的是，上周在贵店购买的{{product}}无法正常使用。'],
            ['p2_complaint_s2#1', 'Specifically, {{problem}} appeared only three days after it arrived.', '具体来说，到货仅三天就出现了{{problem}}。'],
            ['p2_complaint_s3#0', 'I would appreciate it if you could arrange a repair or a full refund as soon as possible.', '若你能尽快安排维修或全额退款，我将不胜感激。'],
            ['p3#1', 'You are kindly requested to {{expect}} so that {{topic}} can be handled more effectively.', '请你{{expect}}，以便{{topic}}能得到更有效的处理。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。很遗憾，我不得不就近期{{topic}}出现的问题正式投诉。',
            '具体来说，事情经过如下。令我失望的是，上周在贵店购买的{{product}}无法正常使用。具体来说，到货仅三天就出现了{{problem}}。若你能尽快安排维修或全额退款，我将不胜感激。',
            '请你{{expect}}，以便{{topic}}能得到更有效的处理。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'intro': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#4', 'In this letter, I would like to introduce {{topic}} to you as an excellent option.', '在这封信里，我想把{{topic}}作为一个很好的选择介绍给你。'],
            ['p2_intro_s2#0', 'To be more specific, {{topic}} refers to {{subject}}, which is characterized by {{feature}}.', '具体而言，{{topic}}指的是{{subject}}，它的特点是{{feature}}。'],
            ['p2_intro_s3#0', 'To begin with, it covers {{aspect1}}, enabling {{audience}} to {{gain1}}.', '首先，它涵盖{{aspect1}}，使{{audience}}能够{{gain1}}。'],
            ['p2_intro_s2#2', 'More specifically, in my daily life I usually {{habit1}} and {{habit2}}, which helps me maintain {{advantage}}.', '更具体而言，在日常生活中，我通常会{{habit1}}并且{{habit2}}，这有助于我保持{{advantage}}。'],
            ['p2_intro_s4#0', 'Taken together, these features make {{topic}} an ideal choice for {{audience}} who wish to {{need}}.', '总的来说，这些特点使{{topic}}成为希望{{need}}的{{audience}}的理想选择。'],
            ['p3#4', 'I sincerely hope that you will make full use of this opportunity to {{outcome}}.', '我衷心希望你能充分利用这次机会{{outcome}}。'],
            ['', 'Feel free to let me know if you need any further information.', '如需更多信息，随时告诉我。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。在这封信里，我想把{{topic}}作为一个很好的选择介绍给你。',
            '具体而言，{{topic}}指的是{{subject}}，它的特点是{{feature}}。首先，它涵盖{{aspect1}}，使{{audience}}能够{{gain1}}。更具体而言，在日常生活中，我通常会{{habit1}}并且{{habit2}}，这有助于我保持{{advantage}}。总的来说，这些特点使{{topic}}成为希望{{need}}的{{audience}}的理想选择。',
            '我衷心希望你能充分利用这次机会{{outcome}}。如需更多信息，随时告诉我。',
        ],
    },
    'notice': {
        'rows': [
            ['p1s2#2', 'In order to further promote {{topic}}, our school has decided to issue the following notice.', '为进一步推动{{topic}}，学校决定发布以下通知。'],
            ['p2s1#2', 'As for the planned event, the main arrangements are as follows.', '现将本次活动的具体安排通知如下。'],
            ['p2_notice_s2#0', 'First, {{time}} has been set as the official time for {{topic}}, and all {{audience}} are required to attend on time.', '首先，{{time}}定为{{topic}}的正式时间，届时全体{{audience}}须准时参加。'],
            ['p2_notice_s3#0', 'Furthermore, the main contents of {{topic}} include {{content1}}, {{content2}} and {{content3}}, all of which are closely related to the theme.', '此外，{{topic}}的主要内容包括{{content1}}、{{content2}}和{{content3}}，都与主题密切相关。'],
            ['p2_notice_s4#0', 'Finally, all {{audience}} are required to {{requirement}}, so that {{topic}} can proceed in an orderly way.', '最后，全体{{audience}}须{{requirement}}，以确保{{topic}}有序进行。'],
            ['p3#1', 'You are kindly requested to {{expect}} so that {{topic}} can be handled more effectively.', '请你{{expect}}，以便{{topic}}能得到更有效的处理。'],
            ['p3#5', 'Please read this notice carefully and pass it on to those concerned.', '请仔细阅读本通知并转告相关人员。'],
        ],
        'cn_paras': [
            '为进一步推动{{topic}}，学校决定发布以下通知。',
            '现将本次活动的具体安排通知如下。首先，{{time}}定为{{topic}}的正式时间，届时全体{{audience}}须准时参加。此外，{{topic}}的主要内容包括{{content1}}、{{content2}}和{{content3}}，都与主题密切相关。最后，全体{{audience}}须{{requirement}}，以确保{{topic}}有序进行。',
            '请你{{expect}}，以便{{topic}}能得到更有效的处理。请仔细阅读本通知并转告相关人员。',
        ],
    },
    'inquire': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s2#8', 'I would appreciate the chance to discuss {{topic}} with you in more detail.', '希望能有机会和你更详细地谈谈{{topic}}。'],
            ['p2s1#0', 'To be more specific, my questions are as follows.', '具体来说，我想请教以下几点。'],
            ['p2_inquire_s2#0', 'In particular, I would like to know how I can better adapt to the local way of life.', '具体而言，我想知道如何更好地适应当地的生活。'],
            ['p2_inquire_s2#1', 'More specifically, I am not sure whether my plan is practical, so I would value your opinion.', '另外，我不确定自己的计划是否可行，很想听听你的意见。'],
            ['p2_inquire_s3#0', 'Since you are familiar with the situation there, your advice would be of great value to me.', '鉴于你对当地情况很熟悉，你的建议对我将十分宝贵。'],
            ['p3#0', 'I would appreciate it very much if you could {{expect}} by {{deadline}}.', '如果你能在{{deadline}}前{{expect}}，我将不胜感激。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。希望能有机会和你更详细地谈谈{{topic}}。',
            '具体来说，我想请教以下几点。具体而言，我想知道如何更好地适应当地的生活。另外，我不确定自己的计划是否可行，很想听听你的意见。鉴于你对当地情况很熟悉，你的建议对我将十分宝贵。',
            '如果你能在{{deadline}}前{{expect}}，我将不胜感激。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
    'opinion': {
        'rows': [
            ['p1s1#0', 'I hope this message finds you well.', '希望收到此信时你一切安好。'],
            ['p1s1#1', 'I am so delighted to receive your letter.', '非常高兴收到你的来信。'],
            ['p1s2#1', 'I would like to share with you a few thoughts on {{topic}}.', '我想和你分享我对{{topic}}的几点看法。'],
            ['p2s1#0', 'To be more specific, what I would like to discuss falls into three parts.', '具体来说，我想谈的有三点。'],
            ['p2_opinion_s2#0', 'To be honest, I am deeply impressed by what you shared, especially {{detail}}.', '说实话，你分享的内容让我印象很深，尤其是{{detail}}。'],
            ['p2_opinion_s2#1', 'If I may say so, it reflects your careful observation and genuine love for life.', '在我看来，这体现了你细致的观察和对生活的热爱。'],
            ['p2_opinion_s3#0', 'The reason is that such records help us rediscover the beauty of ordinary moments.', '原因在于，这类记录能帮我们重新发现日常时刻的美好。'],
            ['', 'I would be glad to hear your own view on this matter.', '也很想听听你自己对这件事的看法。'],
            ['p3#2', 'Thank you for your time and attention, and I look forward to your positive response.', '感谢你抽时间阅读这封信，期待你的回复。'],
        ],
        'cn_paras': [
            '希望收到此信时你一切安好。非常高兴收到你的来信。我想和你分享我对{{topic}}的几点看法。',
            '具体来说，我想谈的有三点。说实话，你分享的内容让我印象很深，尤其是{{detail}}。在我看来，这体现了你细致的观察和对生活的热爱。原因在于，这类记录能帮我们重新发现日常时刻的美好。',
            '也很想听听你自己对这件事的看法。感谢你抽时间阅读这封信，期待你的回复。',
        ],
    },
}

# ---------------- 迭代润色表（build 读取，重跑不回退） ----------------
# 1) 中文去翻译腔 / 与整信范文同步
CN_FIX2 = {
    'p1s1': {0: '希望收到此信时你一切安好。', 1: '非常高兴收到你的来信。'},
    'p1s2': {
        0: '我写这封信，是想就{{topic}}一事与你沟通。',
        1: '借此信，我想分享我对{{topic}}的一些看法。',
        2: '为进一步推动{{topic}}，学校决定发布以下通知。',
        3: '我写此信，为{{topic}}所引起的问题向你致以诚挚的歉意。',
        4: '在这封信里，我想把{{topic}}作为极佳的选择介绍给你。',
        5: '我写此信，为你的帮助向你表达诚挚的谢意。',
        6: '我写信是想邀请你参加{{topic}}。',
        7: '请允许我向你致以最热烈的祝贺。',
        8: '我写此信，是想与你详细探讨{{topic}}。',
        9: '我写信的主要目的，是就{{topic}}提出几点建议。',
        10: '我写此信，正式反映近期{{topic}}出现的问题。',
    },
    'p2s1': {1: '至于具体措施，我的建议如下。', 2: '至于本次活动，具体安排如下。'},
    'p2_advice_s2': {
        0: '首先，我建议你把{{ving}}{{topic}}落到实处，这能帮你更清楚地认识{{detail}}。',
        1: '具体来说，建议你围绕{{topic}}来{{action}}，这样能逐步改善{{detail}}。',
    },
    'p2_advice_s3': {0: '此外，也建议你{{task}}，以便改善现状。'},
    'p2_invite_s3': {0: '此外，在{{topic}}期间{{task}}，你将能够{{gain}}，这对你大有裨益。'},
    'p2_invite_s4': {0: '最后，你的到来将使{{topic}}更有意义，也能让你{{benefit}}。'},
    'p2_apology_s2': {
        0: '在此我必须承认，我在{{topic}}上的{{fault}}已经造成了{{impact}}。',
        1: '由于我在{{topic}}方面{{fault}}，你不得不面对{{impact}}，这本不该发生。',
    },
    'p2_apology_s3': {0: '尽管{{cause}}在一定程度上解释了事情的起因，但主要责任仍在我。'},
    'p2_congrats_s2': {
        0: '更具体地说，你在{{topic}}上的出色表现清楚地展现了你的{{quality}}。',
        1: '就{{topic}}而言，你在{{achievement}}上的成功确实令人钦佩，也颇具鼓舞意义。',
    },
    'p2_congrats_s4': {0: '最后，{{topic}}上的这一成就必将激励你{{next step}}，助你迈向{{goal}}。'},
    'p2_intro_s2': {
        0: '具体而言，{{topic}}指的是{{subject}}，其突出特点是{{feature}}。',
        1: '从实用的角度看，{{topic}}主要包括{{content}}，目的在于{{purpose}}。',
        2: '更具体而言，在日常生活中，我通常会{{habit1}}并且{{habit2}}，这有助于我保持{{advantage}}。',
    },
    'p2_intro_s3': {0: '首先，它涵盖{{aspect1}}，使{{audience}}能够{{gain1}}。'},
    'p2_intro_s4': {0: '总的来说，这些特点使{{topic}}成为希望{{need}}的{{audience}}的理想选择。'},
    'p2_notice_s2': {
        0: '首先，{{time}}定为{{topic}}的正式时间，届时全体{{audience}}须准时参加。',
        1: '首先，{{topic}}将在{{place}}举行，全体{{audience}}前往都很方便。',
    },
    'p2_notice_s3': {0: '此外，{{topic}}的主要内容包括{{content1}}、{{content2}}和{{content3}}，都紧扣主题。'},
    'p2_notice_s4': {0: '最后，全体{{audience}}须{{requirement}}，以确保{{topic}}有序进行。'},
    'p2_thanks_s2': {
        0: '我想衷心感谢你在我逗留期间给予的热情接待。',
        1: '若没有你慷慨的帮助，我不可能在{{topic}}上取得这样的进步。',
    },
    'p2_thanks_s3': {0: '最让我感动的是你的耐心与友善，让我有宾至如归的感觉。'},
    'p2_complaint_s2': {
        0: '令我失望的是，上周在贵店购买的{{product}}无法正常使用。',
        1: '具体来说，到货仅三天就出现了{{problem}}。',
    },
    'p2_complaint_s3': {0: '若你能尽快安排维修或全额退款，我将不胜感激。'},
    'p2_inquire_s2': {
        0: '具体而言，我想知道如何更好地适应当地的生活。',
        1: '另外，我不确定自己的计划是否可行，很想听听你的意见。',
    },
    'p2_inquire_s3': {0: '鉴于你对当地情况很熟悉，你的建议对我将十分宝贵。'},
    'p2_opinion_s2': {0: '说实话，你分享的内容让我深有感触，尤其是{{detail}}。'},
    'p2_opinion_s3': {0: '原因在于，这类记录能帮我们重新发现平凡时刻中的美好。'},
    'p3': {2: '感谢你抽时间阅读这封信，期待你的回复。', 4: '我衷心希望你能充分利用这次机会{{outcome}}。',
           5: '请仔细阅读本通知并转告相关人员。'},
}
# 2) 英文去被动套路 / 别扭表达
EN_FIX2 = {
    'p2_notice_s2': {1: 'To begin with, {{topic}} will take place at {{place}}, which is convenient for all {{audience}}.'},
}
# 3) 不实用的句子：检索页不再渲染（整信范文未引用，删减不影响任何 src 索引）
HIDE_ITEMS = {
    'p1s1': [2],           # 通知致谢开场：真题通知几乎不这么写，套上就假
    'p2_invite_s2': [1],   # broaden {{gain}} 搭配错误（broaden horizons 才成立）
    'p3': [3],             # To conclude... measures 套路总结句，只适配建议信且烂大街
}
# ---------------- 第三轮：中文中性化 + 英文精简 ----------------
# 原则（用户要求）：模板里的中文**不做文学化润色**，中性直译、贴原意即可——
# 背诵的主体是英文，中文只当"对答案用"，越平实越好记；英文才是打磨重点。
CN_FIX3 = {
    'p1s2': {
        0: '这封信是关于{{topic}}的，希望听听你的看法。',
        1: '我想和你分享我对{{topic}}的几点看法。',
        3: '请接受我为{{topic}}给你带来的不便和麻烦所作的诚挚道歉。',
        4: '在这封信里，我想把{{topic}}作为一个很好的选择介绍给你。',
        5: '非常感谢你给予我的慷慨帮助。',
        6: '很高兴邀请你参加{{topic}}。',
        8: '希望能有机会和你更详细地谈谈{{topic}}。',
        9: '我想就{{topic}}提几点建议，希望能对你有用。',
        10: '很遗憾，我不得不就近期{{topic}}出现的问题正式投诉。',
    },
    'p2s1': {0: '更具体地说，主要有以下几点。'},
    'p2_advice_s2': {0: '首先，我建议你把{{ving}}{{topic}}付诸实践，这能帮你对{{detail}}有更深的理解。'},
    'p2_advice_s3': {0: '此外，建议你{{task}}，以便改善现状。'},
    'p2_apology_s2': {0: '我必须承认，{{topic}}上的{{fault}}造成了{{impact}}。'},
    'p2_apology_s3': {0: '尽管{{cause}}能部分解释这件事，但主要责任仍在我。'},
    'p2_congrats_s2': {1: '就{{topic}}而言，你在{{achievement}}上的成功确实令人钦佩，也很鼓舞人心。'},
    'p2_intro_s2': {0: '具体而言，{{topic}}指的是{{subject}}，它的特点是{{feature}}。'},
    'p2_notice_s3': {0: '此外，{{topic}}的主要内容包括{{content1}}、{{content2}}和{{content3}}，都与主题密切相关。'},
    'p2_thanks_s3': {0: '最让我印象深刻的是你的耐心和友善，这让我感觉像在自己家一样。'},
    'p2_invite_s3': {0: '此外，在{{topic}}期间{{task}}，你将能够{{gain}}，这对你很有好处。'},
    'p2_opinion_s2': {0: '说实话，你分享的内容让我印象很深，尤其是{{detail}}。',
                      1: '在我看来，这体现了你细致的观察和对生活的热爱。'},
    'p2_opinion_s3': {0: '原因在于，这类记录能帮我们重新发现日常时刻的美好。'},
    'p3': {1: '请你{{expect}}，以便{{topic}}能得到更有效的处理。'},
}
# 英文升级：每类来意句用**不同句式 + 精准动词**，正式但避开烂大街模板
# （⚠ 反面教材：I am writing to ... 是中国考生最泛滥的低阶开头，阅卷老师看腻了——
#  "精简"不等于"写简单"，要高级、不套路、且能用得上）
EN_FIX3 = {
    'p1s2': {
        0: 'This letter concerns {{topic}}, and I would appreciate your thoughts on it.',
        1: 'I would like to share with you a few thoughts on {{topic}}.',
        3: 'Please accept my sincere apology for any inconvenience and trouble that {{topic}} has brought you.',
        5: 'I am truly grateful for the generous help you have given me.',
        6: 'It gives me great pleasure to invite you to {{topic}}.',
        8: 'I would appreciate the chance to discuss {{topic}} with you in more detail.',
        9: 'I would like to offer a few suggestions on {{topic}}, which I hope may be of use to you.',
        10: 'It is with regret that I write to complain about the recent problems with {{topic}}.',
    },
    'p2s1': {0: 'To be more specific, the main points are as follows.',
              1: 'As for the practical measures, my suggestions are as follows.'},
    'p2_advice_s2': {0: 'To begin with, I would suggest that you put {{ving}} {{topic}} into practice, as it can help you gain a deeper understanding of {{detail}}.'},
    'p2_advice_s3': {0: 'In addition, you are advised to {{task}} so as to improve the situation.'},
    'p2_apology_s2': {0: 'I must admit that {{fault}} on my part concerning {{topic}} has caused {{impact}}.'},
}
