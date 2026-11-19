# -*- coding: utf-8 -*-
"""生成写作词库速查页数据 data/writing_words.json。

内容来源：
- 27考研英语二大作文押题预测_视频总结.md（五个押题方向的主题词/加分短语，逐条抄录）
- writing_apply.json / small_apply.json 真题范文里的高频实词、书信人名、图表动词
- 历年真题小作文 directions 里指定的人名（Li Ming / Zhang Wei）
- 英语二图表作文常用描述词、连接词（教学整理）

结构：groups = [{id,name,icon,desc,items:[{en,cn,tag?}]}]
"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), '..', 'pwa', 'data', 'writing_words.json')

def I(en, cn, tag=None):
    d = {'en': en, 'cn': cn}
    if tag:
        d['tag'] = tag
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
    ],
})

# 2. 加分短语（押题 md 逐条 + 范文常用）
groups.append({
    'id': 'phrase', 'name': '加分短语 · 现挑现用', 'icon': '✨',
    'desc': '押题原词表的加分短语，加范文里反复出现的高级搭配。写作时按话题挑 1~2 个塞进主体段。',
    'items': [
        I('gain increasing popularity', '越来越普及', '押'),
        I('witness a steady rise', '呈现稳步上升', '押'),
        I('facilitate study', '助力学习', '押'),
        I('the largest proportion', '占最大比重', '押'),
        I('cultural confidence', '文化自信', '押'),
        I('inherit fine traditions', '传承优良传统', '押'),
        I('narrow the gap', '缩小差距', '押'),
        I('improve continuously', '持续改善', '押'),
        I('promote educational fairness', '促进教育公平', '押'),
        I('reduce carbon emissions', '减少碳排放', '押'),
        I('play a vital role in', '在……中起重要作用', '范'),
        I('be attributed to', '归因于', '范'),
        I('a combination of factors', '多种因素的综合', '范'),
        I('be aware of', '意识到', '范'),
        I('seek various ways to', '寻求各种方法去', '范'),
        I('be beneficial to', '有益于', '范'),
        I('lay a solid foundation for', '为……打下坚实基础', '范'),
        I('keep pace with', '跟上……的步伐', '范'),
        I('raise public awareness of', '提高公众对……的意识', '范'),
        I('strike a balance between', '在……之间取得平衡', '范'),
        I('attach great importance to', '高度重视', '范'),
        I('make full use of', '充分利用', '范'),
        I('take effective measures', '采取有效措施', '范'),
        I('enjoy a growing popularity', '日益流行', '范'),
    ],
})

# 3. 图表描述词
groups.append({
    'id': 'chart', 'name': '图表词 · 开头段必备', 'icon': '📊',
    'desc': '第一段描述图表要用：图表类型 + 升降动词 + 程度副词。标「动词」的注意时态（过去年份用过去式）。',
    'items': [
        I('bar chart', '柱状图', '类型'),
        I('pie chart', '饼图', '类型'),
        I('line chart', '折线图', '类型'),
        I('table', '表格', '类型'),
        I('clearly illustrate', '清晰地展示', '动词'),
        I('account for', '占（比例）', '动词'),
        I('takes the lead', '居首位', '动词'),
        I('followed by', '紧随其后', '动词'),
        I('respectively', '分别地', '副词'),
        I('rose sharply', '急剧上升', '动词'),
        I('saw a modest increase', '小幅增长', '动词'),
        I('climbed steadily', '稳步攀升', '动词'),
        I('declined gradually', '逐渐下降', '动词'),
        I('remained stable', '保持稳定', '动词'),
        I('fluctuated', '波动', '动词'),
        I('reached a peak', '达到峰值', '动词'),
        I('a steady trend', '平稳趋势', '搭配'),
        I('a slight increase', '轻微增长', '搭配'),
        I('a dramatic decline', '大幅下降', '搭配'),
        I('over the same period', '同期', '搭配'),
        I('in contrast', '相比之下', '搭配'),
        I('the figure for', '……的数据', '搭配'),
    ],
})

# 4. 连接词 / 逻辑词
groups.append({
    'id': 'link', 'name': '连接词 · 逻辑衔接', 'icon': '🔗',
    'desc': '句间过渡用。写作模板里已反复出现，务必拼写正确。',
    'items': [
        I('to begin with', '首先', '顺序'),
        I('first and foremost', '首先（强调）', '顺序'),
        I('in addition', '此外', '递进'),
        I('furthermore', '此外', '递进'),
        I('moreover', '而且', '递进'),
        I('in particular', '尤其', '递进'),
        I('by contrast', '相比之下', '转折'),
        I('nevertheless', '然而', '转折'),
        I('whereas', '然而（对比）', '转折'),
        I('therefore', '因此', '因果'),
        I('as a result', '结果', '因果'),
        I('consequently', '因此', '因果'),
        I('given that', '鉴于', '因果'),
        I('in conclusion', '总之', '总结'),
        I('to conclude', '最后', '总结'),
        I('overall', '总体而言', '总结'),
        I('admittedly', '诚然', '让步'),
        I('that said', '话虽如此', '让步'),
    ],
})

# 5. 小作文功能词 / 书信套语
groups.append({
    'id': 'letter', 'name': '小作文 · 功能句词', 'icon': '✉️',
    'desc': '书信/通知/纪要的高频动词和套语。称呼落款、邀请建议感谢投诉，都从这些词展开。',
    'items': [
        I('Dear Sir or Madam', '尊敬的先生/女士', '称呼'),
        I('Yours sincerely', '谨启（正式）', '落款'),
        I('Yours faithfully', '谨启（不知姓名）', '落款'),
        I('I am writing to', '我写信是为了', '开头'),
        I('express my gratitude', '表达感谢', '功能'),
        I('extend my congratulations', '表示祝贺', '功能'),
        I('lodge a complaint', '提出投诉', '功能'),
        I('seek your advice', '征求你的建议', '功能'),
        I('make a suggestion', '提出建议', '功能'),
        I('extend an invitation', '发出邀请', '功能'),
        I('I would appreciate it if', '如果……将不胜感激', '功能'),
        I('be delighted to', '很高兴做', '功能'),
        I('look forward to your reply', '期待你的回复', '结尾'),
        I('at your earliest convenience', '尽早', '结尾'),
        I('take into consideration', '考虑', '功能'),
        I('a brief introduction', '简要介绍', '功能'),
        I('on behalf of', '代表', '功能'),
        I('be scheduled for', '定于……举行', '功能'),
        I('participate in', '参加', '功能'),
        I('sign up for', '报名参加', '功能'),
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
    ],
})

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
