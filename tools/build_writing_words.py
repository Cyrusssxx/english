# -*- coding: utf-8 -*-
"""生成写作词库速查页数据 data/writing_words.json。

内容来源：
- 27考研英语二大作文押题预测_视频总结.md（五个押题方向的主题词/加分短语，逐条抄录）
- writing_apply.json / small_apply.json 真题范文里的高频实词、书信人名、图表动词
- 历年真题小作文 directions 里指定的人名（Li Ming / Zhang Wei）
- 英语二图表作文常用描述词、连接词（教学整理）
- 27考研英语作文押题精选.pdf（26 道押题话题中英对照）+ ai归来版范文.pdf（26 篇配套范文的高级套语、称呼落款）

结构：groups = [{id,name,icon,desc,items:[{en,cn,tag?}]}]
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'pwa', 'data', 'writing_words.json')

def I(en, cn, tag=None, sub=None):
    d = {'en': en, 'cn': cn}
    if tag:
        d['tag'] = tag
    if sub:
        d['sub'] = sub
    return d

groups = []

# 1. 押题主题词（按押题 md 五方向 + 历年真题热点）
groups.append({
    'id': 'topic', 'name': '主题词 · 押题高频', 'icon': '🎯',
    'desc': '27 押题五个方向 + 历年真题热点的核心名词，写作文靠它们定位话题。标「押」为押题原词表，标「真」为真题出现过。',
    'items': [
        # AI 教育
        I('artificial intelligence (AI)', '人工智能', '押'),
        I('online learning', '线上学习', '押'),
        I('offline study', '线下学习', '押'),
        I('reading duration', '阅读时长', '押'),
        I('educational technology', '教育科技', '押'),
        I('intelligent tutoring', '智能辅导', '押'),
        # 传统文化
        I('traditional culture', '传统文化', '押'),
        I('cultural heritage', '文化遗产', '押'),
        I('cultural inheritance', '文化传承', '押'),
        I('cultural experience', '文化体验', '押'),
        I('cultural confidence', '文化自信', '押'),
        I('short video', '短视频', '押'),
        I('self-media', '自媒体', '押'),
        I('live streaming', '直播', '押'),
        # 教育公平
        I('educational resources', '教育资源', '押'),
        I('urban and rural areas', '城乡地区', '押'),
        I('educational equity', '教育公平', '押'),
        I('balanced development', '均衡发展', '押'),
        I('rural education', '乡村教育', '押'),
        # 绿色消费
        I('green consumption', '绿色消费', '押'),
        I('energy-saving home appliances', '节能家电', '押'),
        I('eco-friendly daily products', '环保日用品', '押'),
        I('green food', '绿色食品', '押'),
        I('sustainable travel', '可持续出行', '押'),
        I('low-carbon concept', '低碳理念', '押'),
        I('environmental awareness', '环保意识', '押'),
        I('sustainable lifestyle', '可持续生活方式', '押'),
        # 绿色出行
        I('green travel', '绿色出行', '押'),
        I('high-speed rail', '高铁', '押'),
        I('public transport', '公共交通', '押'),
        I('bicycle / cycling', '自行车', '押'),
        I('on foot / walking', '步行', '押'),
        I('private cars', '私家车', '押'),
        I('low-carbon lifestyle', '低碳生活方式', '押'),
        I('eco-friendly transportation', '环保交通方式', '押'),
        # 历年真题热点
        I('mobile-phone subscriptions', '手机用户数', '真'),
        I('physical exercise', '体育锻炼', '真'),
        I('health literacy', '健康素养', '真'),
        I('express delivery', '快递业务', '真'),
        I('labour practice course', '劳动实践课', '真'),
        I('leisure activities', '休闲活动', '真'),
        I('outdoor activities', '户外活动', '真'),
        I('museum', '博物馆', '真'),
        I('career choice', '职业选择', '真'),
        I('consumer behaviour', '消费者行为', '真'),
        # 26 道押题话题核心名词（来自押题精选 PDF）
        I('companionship', '陪伴（「陪着」不等于「陪伴」）', '题'),
        I('mental and physical health', '身心健康', '题'),
        I('excessive packaging', '过度包装', '题'),
        I('online information', '网络信息', '题'),
        I('continuing education', '继续教育', '题'),
        I('new energy vehicles', '新能源汽车', '题'),
        I('transport choices', '出行选择', '题'),
        I('convenience store', '便利店', '题'),
        I('accessible facilities', '无障碍设施', '题'),
        I('first-aid knowledge', '急救知识', '题'),
        I('returning students', '留学回国人员', '题'),
        I('life expectancy', '平均寿命', '题'),
        I('aging population', '人口老龄化', '题'),
        I('online and offline sales', '线上与线下销售', '题'),
        I('traditional Chinese art', '中国传统艺术', '题'),
        I('career prospects', '职业前景', '题'),
        I('tourism development', '旅游发展', '题'),
        I('food waste', '食物浪费', '题'),
    ],
})

# --- topic 主题词组：按题材分 5 块（与 topics26 一致），打 sub 并按块序重排 ---
_topic = groups[-1]
_topic['blocks'] = [
    {'name': '科技与教育', 'words': []},
    {'name': '社会与健康', 'words': []},
    {'name': '文化与传承', 'words': []},
    {'name': '环境与消费', 'words': []},
]
_TOPIC_SUB = {
    # 科技与教育
    'artificial intelligence (AI)': '科技与教育', 'online learning': '科技与教育',
    'offline study': '科技与教育', 'reading duration': '科技与教育',
    'educational technology': '科技与教育', 'intelligent tutoring': '科技与教育',
    'educational resources': '科技与教育', 'urban and rural areas': '科技与教育',
    'educational equity': '科技与教育', 'balanced development': '科技与教育',
    'rural education': '科技与教育', 'continuing education': '科技与教育',
    'mobile-phone subscriptions': '科技与教育', 'labour practice course': '科技与教育',
    'online information': '科技与教育',
    # 文化与传承
    'traditional culture': '文化与传承', 'cultural heritage': '文化与传承',
    'cultural inheritance': '文化与传承', 'cultural experience': '文化与传承',
    'cultural confidence': '文化与传承', 'short video': '文化与传承',
    'self-media': '文化与传承', 'live streaming': '文化与传承',
    'museum': '文化与传承', 'traditional Chinese art': '文化与传承',
    # 环境与消费
    'green consumption': '环境与消费', 'energy-saving home appliances': '环境与消费',
    'eco-friendly daily products': '环境与消费', 'green food': '环境与消费',
    'sustainable travel': '环境与消费', 'low-carbon concept': '环境与消费',
    'environmental awareness': '环境与消费', 'sustainable lifestyle': '环境与消费',
    'green travel': '环境与消费', 'high-speed rail': '环境与消费',
    'public transport': '环境与消费', 'bicycle / cycling': '环境与消费',
    'on foot / walking': '环境与消费', 'private cars': '环境与消费',
    'low-carbon lifestyle': '环境与消费', 'eco-friendly transportation': '环境与消费',
    'express delivery': '环境与消费', 'consumer behaviour': '环境与消费',
    'excessive packaging': '环境与消费', 'new energy vehicles': '环境与消费',
    'transport choices': '环境与消费', 'convenience store': '环境与消费',
    'online and offline sales': '环境与消费', 'tourism development': '环境与消费',
    # 社会与健康
    'physical exercise': '社会与健康', 'health literacy': '社会与健康',
    'leisure activities': '社会与健康', 'outdoor activities': '社会与健康',
    'career choice': '社会与健康', 'companionship': '社会与健康',
    'mental and physical health': '社会与健康', 'accessible facilities': '社会与健康',
    'first-aid knowledge': '社会与健康', 'returning students': '社会与健康',
    'life expectancy': '社会与健康', 'aging population': '社会与健康',
    'career prospects': '社会与健康', 'food waste': '社会与健康',
}
for _it in _topic['items']:
    _it['sub'] = _TOPIC_SUB.get(_it['en'], '社会与健康')
_topic_order = {b['name']: i for i, b in enumerate(_topic['blocks'])}
_topic['items'].sort(key=lambda x: (_topic_order.get(x['sub'], 99),))

# 2. 加分短语（只留写作模板/范文里真实出现的，删掉的均 0 次命中）
groups.append({
    'id': 'phrase', 'name': '加分短语 · 现挑现用', 'icon': '✨',
    'desc': '只收写作模板和范文里真实出现的高级搭配：归因、多因素、抓紧、起手表态。按话题挑 1~2 个塞进主体段。',
    'items': [
        I('be attributed to', '归因于', '范'),
        I('a combination of factors', '多种因素的综合', '范'),
        I('make full use of', '充分利用', '范'),
        I('narrow the gap', '缩小差距', '押'),
        I('bear in mind that', '牢记……（第三段起手）', '范2'),
        I('There is no doubt that', '毫无疑问', '范2'),
        I('several factors contribute to', '若干因素促成了……', '范2'),
        I('cannot ignore the fact that', '不能忽视……的事实', '范2'),
        I('It is not difficult to draw the conclusion that', '不难得出结论', '范2'),
        I('Only through the joint efforts of', '只有通过……的共同努力', '范2'),
        I('within our reach', '指日可待；够得着', '范2'),
        I('place pressure on', '给……带来压力', '范2'),
        I('by no means', '绝不（置首倒装）', '范2'),
        I('make a difference', '起作用；有影响', '范2'),
        I('room to grow', '改进/增长空间', '范2'),
        I('top the list', '位居首位', '范2'),
    ],
})

# 3. 图表描述词
groups.append({
    'id': 'chart', 'name': '图表词 · 开头段必备', 'icon': '📊',
    'desc': '第一段描述图表要用：图表类型 + 升降动词 + 程度副词。标「动词」的注意时态（过去年份用过去式）。',
    'items': [
        I('bar chart', '柱状图', '类型'),
        I('pie chart', '饼图', '类型'),
        I('table', '表格', '类型'),
        I('clearly illustrate', '清晰地展示', '动词'),
        I('account for', '占（比例）', '动词'),
        I('takes the lead', '居首位', '动词'),
        I('followed by', '紧随其后', '动词'),
        I('respectively', '分别地', '副词'),
        I('rose sharply', '急剧上升', '动词'),
        I('saw a modest increase', '小幅增长', '动词'),
        I('climbed steadily', '稳步攀升', '动词'),
        I('fluctuated', '波动', '动词'),
        I('over the same period', '同期', '搭配'),
        I('in contrast', '相比之下', '搭配'),
        I('the figure for', '……的数据', '搭配'),
    ],
})

# 4. 连接词 / 逻辑词（只收写作模板骨架里真实出现的，来源 writing_templates.json 的
#    sections[].framework 句首 + linkers.better 升级链 + sections[].en / skeletons[].en；
#    不收押题范文、demo、替换句里的词。按「引出原因→机制句→立场→主体→图表对比」分组）
groups.append({
    'id': 'link', 'name': '连接词 · 逻辑衔接', 'icon': '🔗',
    'desc': '只收写作模板骨架里真实出现的衔接词：第二段引出原因、三条机制句、第三段立场与主体、图表同期对比。都是你自己骨架里写的，背了直接能套。',
    'items': [
        # 第二段：引出原因
        I('a combination of factors', '多种因素的综合（引出原因）', '引因'),
        I('Primary among these is', '其中首要的是（机制句①）', '机制'),
        I('Equally important,', '同样重要的是（机制句②）', '机制'),
        I('A further driver is', '另一个推动因素是（机制句③）', '机制'),
        # linkers.better 同义升级链
        I('The most immediate factor is', '最直接的因素是', '机制'),
        I('Chief among them is', '其中最主要的是', '机制'),
        I('Just as significant,', '同样重要的是', '机制'),
        I('Beyond that,', '除此之外', '机制'),
        # 第三段：立场 / 主体 / 收束
        I('On balance,', '总的来说（立场句）', '立场'),
        I('Taking everything into account', '综合考虑', '立场'),
        I('Given the trends above', '鉴于上述趋势', '立场'),
        I('To make the most of these gains,', '要延续这些成效（正面主体）', '主体'),
        I('To address this problem,', '要解决这一问题（负面主体）', '主体'),
        I('To keep both sides in view,', '要兼顾两面（双面主体）', '主体'),
        I('With such steps in place,', '有了这些举措（收束）', '收束'),
        # 图表描述：同期 / 对比 / 手段
        I('during this period', '在此期间', '同期'),
        I('over the same period', '同期', '同期'),
        I('by contrast', '相比之下', '对比'),
        I('whereas', '而（对比）', '对比'),
        I('in this way', '这样', '手段'),
        I('only through', '只有通过', '条件'),
        I('overall', '总体而言', '总结'),
    ],
})

# 5. 小作文功能词 / 书信套语（只留模板里真实出现的；删掉的均 0 次命中）
groups.append({
    'id': 'letter', 'name': '小作文 · 功能句词', 'icon': '✉️',
    'desc': '只收小作文模板里真实出现的称呼落款与功能套语。邀请建议感谢投诉按题目挑对应的一句。',
    'items': [
        I('Dear Sir or Madam', '尊敬的先生/女士', '称呼'),
        I('Yours sincerely', '谨启（正式）', '落款'),
        I('I am writing to', '我写信是为了', '开头'),
        I('express my gratitude', '表达感谢', '功能'),
        I('I would appreciate it if', '如果……将不胜感激', '功能'),
        I('be delighted to', '很高兴做', '功能'),
        I('look forward to your reply', '期待你的回复', '结尾'),
    ],
})

# 6. 人名 / 地名 / 专有名词（写作+翻译都会遇到）
groups.append({
    'id': 'name', 'name': '人名 · 地名 · 专名', 'icon': '🌏',
    'desc': '小作文落款固定用 Li Ming 或 Zhang Wei（看题目指定，不要写真名）。地名、节日、机构名翻译要记牢首字母大写。',
    'items': [
        I('Li Ming', '李明（小作文落款）', '人名'),
        I('Zhang Wei', '张伟（小作文落款）', '人名'),
        I('Beijing', '北京', '地名'),
        I('Shanghai', '上海', '地名'),
        I('China', '中国', '地名'),
        I('Chinese', '中国的；中国人；汉语', '地名'),
        I('the Great Wall', '长城', '专名'),
        I('the Spring Festival', '春节', '专名'),
        I('the Mid-Autumn Festival', '中秋节', '专名'),
        I('the Dragon Boat Festival', '端午节', '专名'),
        I('Project Hope', '希望工程', '专名'),
        I('Peking University', '北京大学', '专名'),
        I('Tsinghua University', '清华大学', '专名'),
        # 范文/真题常见收信人（称呼用，不是落款）
        I('Michael', '迈克尔（收信人）', '称呼'),
        I('Jane', '简（收信人）', '称呼'),
        I('Alex', '亚历克斯（收信人）', '称呼'),
        I('James', '詹姆斯（收信人）', '称呼'),
        I('Professor Thomas', '托马斯教授', '称呼'),
        I('the Center for Cultural Interchange', '文化交流中心', '机构'),
        I('the Cultural and Tourism Association', '文化旅游协会', '机构'),
        I('ChatGPT', '聊天机器人（AI 工具名）', '专名'),
    ],
})

# 7. 押题话题 26 题（中英对照，来自押题精选 PDF 的 26 道题目）
groups.append({
    'id': 'topics26', 'name': '押题话题 · 26 题中英对照', 'icon': '📝',
    'desc': '押题精选 PDF 的 18 道大作文 + 8 道小作文题目，按题材分块、逐题中英对照；每块附一组高频词，看到中文题目要能立刻反应出英文关键词。',
    # 按题材分 5 块；每块配 5-8 个该类高频词（复用 topic/letter 组的中英对照）
    'blocks': [
        {'name': '科技与教育', 'words': [
            I('artificial intelligence (AI)', '人工智能'),
            I('online learning', '线上学习'),
            I('educational technology', '教育科技'),
            I('intelligent tutoring', '智能辅导'),
            I('continuing education', '继续教育'),
            I('online information', '网络信息'),
            I('educational resources', '教育资源'),
            I('self-media', '自媒体'),
        ]},
        {'name': '社会与健康', 'words': [
            I('companionship', '陪伴'),
            I('mental and physical health', '身心健康'),
            I('career choice', '职业选择'),
            I('accessible facilities', '无障碍设施'),
            I('first-aid knowledge', '急救知识'),
            I('aging population', '人口老龄化'),
            I('life expectancy', '平均寿命'),
            I('health literacy', '健康素养'),
        ]},
        {'name': '文化与传承', 'words': [
            I('traditional culture', '传统文化'),
            I('cultural heritage', '文化遗产'),
            I('cultural confidence', '文化自信'),
            I('cultural inheritance', '文化传承'),
            I('traditional Chinese art', '中国传统艺术'),
            I('cultural experience', '文化体验'),
        ]},
        {'name': '环境与消费', 'words': [
            I('green consumption', '绿色消费'),
            I('excessive packaging', '过度包装'),
            I('new energy vehicles', '新能源汽车'),
            I('transport choices', '出行选择'),
            I('convenience store', '便利店'),
            I('low-carbon lifestyle', '低碳生活方式'),
            I('green travel', '绿色出行'),
            I('consumer behaviour', '消费者行为'),
        ]},
        {'name': '小作文应用文', 'words': [
            I('make a suggestion', '提出建议'),
            I('seek your advice', '征求你的建议'),
            I('express my gratitude', '表达感谢'),
            I('extend an invitation', '发出邀请'),
            I('look forward to your reply', '期待你的回复'),
            I('I would appreciate it if', '如果……将不胜感激'),
            I('participate in', '参加'),
            I('on behalf of', '代表'),
        ]},
    ],
    'items': [
        I('the use of AI tools', '人工智能工具的使用', '大1'),
        I('accompanying vs. companionship', '「陪着」不等于「陪伴」', '大2'),
        I('stress and mental health', '压力与身心健康', '大3'),
        I('excessive packaging and green consumption', '过度包装与绿色消费', '大4'),
        I('online information and rational judgment', '网络信息与理性辨别', '大5'),
        I('purposes of continuing education for working adults', '在职群体参加继续学习的目的', '大6'),
        I('domestic sales of fuel and new energy vehicles', '燃油车与新能源汽车国内销量', '大7'),
        I('residents\' daily transport choices', '居民日常出行选择', '大8'),
        I('factors in career choice for graduates', '大学生择业考虑因素', '大9'),
        I('the number of convenience stores nationwide', '全国便利店门店数量', '大10'),
        I('the spread of accessible routes in public places', '公共场所无障碍通道的普及', '大11'),
        I('the spread of first-aid knowledge', '急救知识的普及', '大12'),
        I('returnees developing their careers at home', '留学人员回国发展', '大13'),
        I('life expectancy and population aging', '中国人平均寿命与人口老龄化', '大14'),
        I('online vs. offline ice cream sales', '冰激凌线上与线下销售占比', '大15'),
        I('the inheritance of traditional Chinese art', '中国传统艺术的传承', '大16'),
        I('popularity vs. genuine passion', '热门与热爱', '大17'),
        I('tourism development and environmental protection', '旅游发展与环境保护', '大18'),
        I('peer mentoring program: introduction and reply', '新生朋辈指导项目：介绍与回复', '小19'),
        I('Chinese culture speech: suggestions and arrangements', '中国文化演讲：建议与安排', '小20'),
        I('recommend a learning tool: advice and explanation', '学习工具推荐：建议与说明', '小21'),
        I('pick-up plan change: apology and suggestion', '接机计划变更：道歉与建议', '小22'),
        I('help with overseas study: thanks and invitation', '海外学习帮助：感谢与邀请', '小23'),
        I('volunteer at cultural exchange center: application', '文化交流中心志愿者：申请与说明', '小24'),
        I('volunteer recruitment notice', '文化旅游协会：志愿者招募通知', '小25'),
        I('minutes of meeting: preventing food waste', '防止食物浪费：会议纪要', '小26'),
    ],
})

# --- topics26：按题材块给 26 条打 sub 标签、按块顺序重排，并把整组挪到 topic 组后面相邻 ---
_t26 = next(g for g in groups if g['id'] == 'topics26')
_T26_SUB = {
    # 科技与教育
    '大1': '科技与教育', '大5': '科技与教育', '大6': '科技与教育',
    # 社会与健康
    '大2': '社会与健康', '大3': '社会与健康', '大9': '社会与健康',
    '大11': '社会与健康', '大12': '社会与健康', '大13': '社会与健康', '大14': '社会与健康',
    # 文化与传承
    '大16': '文化与传承', '大17': '文化与传承',
    # 环境与消费
    '大4': '环境与消费', '大7': '环境与消费', '大8': '环境与消费',
    '大10': '环境与消费', '大15': '环境与消费', '大18': '环境与消费',
}
for _it in _t26['items']:
    _it['sub'] = _T26_SUB.get(_it['tag'], '小作文应用文')
_block_order = {b['name']: i for i, b in enumerate(_t26['blocks'])}
_t26['items'].sort(key=lambda x: (_block_order.get(x['sub'], 99),))
# 挪到 topic 组后面
_topic_idx = next(i for i, g in enumerate(groups) if g['id'] == 'topic')
groups.remove(_t26)
groups.insert(_topic_idx + 1, _t26)

# ============================================================
# 高频前置：按「范文里反复出现 / 写作最常用的词」把每组内的词条往前排。
# 这里是稳定排序：表里列出的按出现顺序置顶，其余保持原相对顺序。
# topics26 组保持题目原序（大1..大18/小19..小26），不参与重排。
# 说明：rank = 在下面列表中的下标；不在列表 = 9999（保持原序）。
# ============================================================
HIGH_FREQ = {
    'topic': [
        'artificial intelligence (AI)', 'online learning', 'traditional culture',
        'cultural heritage', 'cultural confidence', 'green consumption',
        'environmental awareness', 'physical exercise', 'career choice',
        'educational resources', 'public transport', 'low-carbon lifestyle',
        'companionship', 'life expectancy', 'excessive packaging',
    ],
    'phrase': [
        'bear in mind that', 'There is no doubt that', 'cannot ignore the fact that',
        'several factors contribute to', 'Only through the joint efforts of',
        'within our reach', 'It is not difficult to draw the conclusion that',
        'be attributed to', 'make full use of',
    ],
    'chart': [
        'clearly illustrate', 'account for', 'rose sharply', 'followed by',
        'respectively', 'bar chart', 'pie chart', 'table',
        'fluctuated', 'over the same period', 'in contrast', 'the figure for',
    ],
    'link': [
        'a combination of factors', 'Primary among these is', 'Equally important,',
        'A further driver is', 'On balance,', 'To address this problem,',
        'by contrast', 'during this period', 'With such steps in place,',
    ],
    'letter': [
        'I am writing to', 'look forward to your reply', 'express my gratitude',
        'be delighted to', 'I would appreciate it if', 'Yours sincerely',
        'Dear Sir or Madam',
    ],
    'name': [
        'Li Ming', 'Zhang Wei', 'Beijing', 'China', 'Chinese',
        'the Spring Festival', 'the Great Wall', 'Peking University',
    ],
}

def rank_group(gid, items):
    table = HIGH_FREQ.get(gid)
    if not table:
        return items
    rank = {en: i for i, en in enumerate(table)}
    return sorted(items, key=lambda it: rank.get(it['en'], 9999))

for _g in groups:
    if _g['id'] != 'topics26':
        _g['items'] = rank_group(_g['id'], _g['items'])

data = {
    'meta': {
        'title': '写作词库速查',
        'desc': '把大小作文模板、范文和押题里的高频词整理成一张速查表：主题词、加分短语、图表词、连接词、书信词、人名地名。英文可点查词。',
    },
    'groups': groups,
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)
    f.write('\n')

n = sum(len(g['items']) for g in groups)
print('written:', OUT)
print('groups:', len(groups), 'items:', n)
