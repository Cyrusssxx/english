# -*- coding: utf-8 -*-
"""范文重点词/短语真源 → pwa/data/writing_keywords.json

内容取舍原则：
- 只收「在自己大作文 17 篇 + 小作文 8 类 + 押题 26 篇范文里真实出现过」的表达（脚本逐条校验命中，
  未命中的直接报错，避免词库与范文两张皮）；
- 每组给：释义、怎么用（放哪一段、接什么）、一句补充例句（英文 + 中文）；
- 前端在范文正文里长词组优先匹配，包成 .kw 可点，点击弹卡（复用 .word-pop 样式）。

用法：python tools/build_writing_keywords.py
"""
import json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PWA = os.path.join(ROOT, 'pwa')
DATA = os.path.join(PWA, 'data')

GROUPS = [
    ('chart', '图表描述', '第一段把图说清楚、说出重点'),
    ('argue', '论证说理', '第二段解释原因、讲清机制'),
    ('advice', '建议收束', '第三段提对策、作结论'),
    ('letter', '书信套语', '小作文开头、请求、结尾'),
]


def K(en, cn, use, ex, ex_cn, g):
    return {'k': en, 'cn': cn, 'use': use, 'ex': ex, 'exCn': ex_cn, 'g': g}


ITEMS = [
    # ---------- 图表描述 ----------
    K('clearly illustrates', '清楚地显示出（图表内容）', '第一段描述图表：The chart clearly illustrates + 名词短语，比 shows 更书面。',
      'The bar chart clearly illustrates the steady growth of online shopping over the past decade.',
      '柱状图清楚地显示了近十年网购的稳步增长。', 'chart'),
    K('rose sharply', '急剧上升', '描述陡升：rise sharply / rose sharply from A to B；缓升用 rose steadily。',
      'The number of delivery orders rose sharply from 2 billion to 13 billion in ten years.',
      '十年间快递业务量从 20 亿件猛增到 130 亿件。', 'chart'),
    K('account for', '占（多大比例）', '讲占比：A accounts for X% of the total，也可换成 makes up / represents。',
      'Students who take part-time jobs account for 37 per cent of the total.',
      '兼职学生占总人数的 37%。', 'chart'),
    K('largest share', '占比最大的一块', '饼图描述最大项：X accounts for the largest share, at X%。',
      'Mobile payment accounts for the largest share, at 45 per cent.',
      '移动支付占比最大，达到 45%。', 'chart'),
    K('comes last', '排在最后（占比最小）', '描述最小项：X comes last, at only X%，和前两项形成对照。',
      'Reading for pleasure comes last, at only 8 per cent.',
      '为消遣而阅读排在最后，仅占 8%。', 'chart'),
    K('bar chart', '柱状图', '点明图型：bar chart / line chart / pie chart；开头一句先交代图型最稳。',
      'The bar chart compares the purposes of continuing education among employees.',
      '该柱状图比较了在职人员参加继续学习的目的。', 'chart'),
    K('household incomes', '家庭收入', '图表主体词：rising household incomes（家庭收入提高）常作原因。',
      'Rising household incomes have made travel affordable for ordinary families.',
      '家庭收入的提高让普通家庭也负担得起旅行。', 'chart'),
    K('everyday necessity', '日常必需品', '把消费类图表落到「生活」层面的用词，比 daily goods 更书面。',
      'Smartphones have changed from a luxury into an everyday necessity.',
      '智能手机已从奢侈品变成日常必需品。', 'chart'),

    # ---------- 论证说理 ----------
    K('a combination of factors', '多种因素共同作用', '第二段万能引入，不承诺条数：This phenomenon can be attributed to a combination of factors.',
      'This phenomenon can be attributed to a combination of factors.',
      '这一现象可归因于多种因素的共同作用。', 'argue'),
    K('be attributed to', '归因于', 'A can be attributed to B；比 because of 更书面，注意被动语态。',
      'The shift can be attributed to the rapid spread of mobile payment.',
      '这一转变可归因于移动支付的迅速普及。', 'argue'),
    K('contribute to', '促成、助长（原因之一）', '第二段列原因：Several factors may contribute to this pattern.',
      'Several factors may contribute to this pattern.',
      '若干因素可能共同造成了这一格局。', 'argue'),
    K('equally important', '同样重要的是', '并列第二条理由/对策，替代烂大街的 Secondly。',
      'Equally important, clear rules should be set for online platforms.',
      '同样重要的是，应为网络平台制定明确的规则。', 'argue'),
    K('positive trend worth welcoming', '值得欢迎的积极趋势', '首段末或第二段开头定调，一句把态度说透。',
      'This is a positive trend worth welcoming.',
      '这是一个值得欢迎的积极趋势。', 'argue'),
    K('momentum behind', '…背后的推动力', '抽象原因：the momentum behind this change（这一变化背后的推力）。',
      'The momentum behind this change comes largely from government support.',
      '这一变化背后的推力主要来自政府支持。', 'argue'),
    K('by no means', '决不（否定强调）', '句首时部分倒装：By no means should we + 动词原形。',
      'By no means should we give up our efforts to protect the environment.',
      '我们决不应当放弃保护环境的努力。', 'argue'),
    K('within our reach', '力所能及、指日可待', '第三段收束的乐观句：... will be within our reach。',
      'A balance between development and protection will be within our reach.',
      '发展与保护之间的平衡将指日可待。', 'argue'),
    K('top the list', '位居榜首', '数据/原因排序：X tops the list at X%，后接 followed by。',
      'Personal development prospects top the list at 65 per cent, followed by pay at 53 per cent.',
      '个人发展前景以 65% 位居榜首，其次是薪酬 53%。', 'argue'),
    K('bear in mind', '牢记、记住', '第三段提建议：We should bear in mind that + 从句。',
      'We should bear in mind that lifelong learning is of great importance to personal development.',
      '我们应牢记，终身学习对个人发展至关重要。', 'argue'),
    K('of great importance', '至关重要', 'be of great importance to sb/sth，替代 very important。',
      'Accessible facilities are of great importance to people with mobility difficulties.',
      '无障碍设施对行动不便者至关重要。', 'argue'),
    K('only through', '只有通过…（才）', '句首 + 部分倒装：Only through ... can we ...，收束段最有力。',
      'Only through the joint efforts of communities and individuals can these skills become widely available.',
      '只有通过社区与个人的共同努力，这些技能才能普及。', 'argue'),

    # ---------- 建议收束 ----------
    K('clear rules', '明确的规则', '对策句主干：set clear rules for ...（为…立规矩）。',
      'Clear rules should be set for online platforms to curb false information.',
      '应为网络平台立下明确规则，以遏制虚假信息。', 'advice'),
    K('steady funding', '稳定的资金投入', '对策句：steady funding from the government（政府稳定投入）。',
      'Steady funding from the government is the key to spreading first-aid training.',
      '政府稳定的资金投入是普及急救培训的关键。', 'advice'),
    K('in the long run', '从长远来看', '结论句常用；与 in the short term 相对。',
      'Establishing a regular habit of exercise will yield substantial benefits in the long run.',
      '养成规律锻炼的习惯，长远来看收益巨大。', 'advice'),

    # ---------- 书信套语 ----------
    K('I hope this message finds you well', '希望你一切都好', '书信开头第一句，最稳的问候，替代 How are you。',
      'I hope this message finds you well.',
      '希望你一切都好。', 'letter'),
    K('I would appreciate it', '如果…我将不胜感激', '礼貌请求：I would appreciate it (very much) if you could + 动词原形。',
      'I would appreciate it if you could arrange an immediate replacement.',
      '如能安排立即更换，我将不胜感激。', 'letter'),
    K('at your earliest convenience', '在您方便时尽快', '催回复/催安排：reply at your earliest convenience。',
      'I would be grateful if you could reply at your earliest convenience.',
      '如能尽早回复，我将不胜感激。', 'letter'),
    K('look forward to', '期待（后接名词/动名词）', '结尾句：I look forward to your reply / to hearing from you.',
      'I look forward to your early reply.',
      '期待您早日回复。', 'letter'),
    K('make full use of', '充分利用', '建议类书信：make full use of the resources available。',
      'You can make full use of the library and the online courses.',
      '你可以充分利用图书馆和线上课程。', 'letter'),
    K('take place', '举行、发生（不及物）', '活动/会议安排：The lecture will take place in Room 302.',
      'The lecture will take place in the main hall next Friday.',
      '讲座将于下周五在主楼大厅举行。', 'letter'),
    K('consider taking concrete steps', '考虑采取具体措施', '建议信核心句：I suggest that you consider taking concrete steps to ...',
      'You may consider taking concrete steps to improve your listening.',
      '你可以考虑采取具体措施提高听力。', 'letter'),
    K('let me know', '告诉我、让我知道', '结尾提供帮助：Please let me know if you need further information.',
      'Please let me know if you need any further information.',
      '如需更多信息，请告诉我。', 'letter'),
    K('due to', '由于（后接名词）', '说明原因/致歉：due to a change of plan。',
      'The delay was due to an unexpected change of plan.',
      '延误是由于计划意外变更造成的。', 'letter'),
    K('yours sincerely', '您诚挚的（落款）', '知道收信人姓名时用 Yours sincerely，不知姓名用 Yours faithfully。',
      'Yours sincerely, Li Ming',
      '您诚挚的，李明', 'letter'),

    # ---------- 论证补充（小作文也能用） ----------
    K('my profound gratitude', '我深切的谢意', '感谢信：express my profound gratitude to you for ...。',
      'I am writing to express my profound gratitude for your generous help.',
      '我写此信是为了对你的慷慨帮助表达深切谢意。', 'letter'),
]


def collect_strs(obj, out):
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, list):
        for x in obj:
            collect_strs(x, out)
    elif isinstance(obj, dict):
        for v in obj.values():
            collect_strs(v, out)


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


corpus = []
for fn in ('writing_apply.json', 'writing_templates.json', 'small_apply.json', 'small_writing.json', 'yati.json'):
    collect_strs(load(fn), corpus)
text = '\n'.join(corpus).lower()

missing = []
for it in ITEMS:
    n = text.count(it['k'].lower())
    it['n'] = n
    if not n:
        missing.append(it['k'])
    print('%-34s %s %3d' % (it['k'], it['g'], n))

if missing:
    raise SystemExit('❌ 这些表达在范文语料里没出现，请删掉或改词：%s' % missing)

# 长词组优先（前端按长度降序匹配，这里排序便于阅读与稳定输出）
ITEMS.sort(key=lambda x: (x['g'], -len(x['k'])))

out = {
    'meta': {
        'title': '范文重点词',
        'desc': '大作文范文 + 小作文范文里反复出现的提分表达：点词看释义、用法和例句。',
        'groups': [{'id': g, 'name': n, 'desc': d} for g, n, d in GROUPS],
        'count': len(ITEMS),
    },
    'items': ITEMS,
}
with open(os.path.join(DATA, 'writing_keywords.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')

print('\n写出 writing_keywords.json：%d 条 / %d 组' % (len(ITEMS), len(GROUPS)))
for g, n, _ in GROUPS:
    print('  %s %s：%d 条' % (g, n, sum(1 for x in ITEMS if x['g'] == g)))
