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
