# -*- coding: utf-8 -*-
"""大作文（英语二 B 节 · 图表作文，15 分）：句池保留清单 + 三个新板块的内容。

由 tools/apply_writing_extra.py 合并进 pwa/data/writing_templates.json：
  PRUNE       —— 句池删冗余（sectionId → 保留的「原始顺序」下标）
  TEACHER     —— 🎓 评分老师视角（15 分口径）
  FLOW        —— ✍️ 答题动线（审题 → 交卷，含时间分配）
  DATA_LANG   —— 📐 数据描述语言工具（图表作文的核心得分工具）+ 常见错误
  CHECKLIST   —— ✅ 交卷前自查表
"""

VER = 1

# ---------------- 1) 句池保留清单 ----------------
# 原则：同一功能只留 1 句；「不同归因角度」的保留（那不是重复）。
PRUNE = {
    'chart_static':    [0, 1, 4, 6, 7],        # 最大类别 / 长尾 / 前几类合计 / 分布集中 / 分布均衡（删「过半·前三合计·主导」等 3 句同义）
    'chart_dynamic':   [0, 1, 2, 3, 4],        # 上升 / 下降 / 翻倍 / 同向不同速 / 平稳（删「加速·反差·窄幅波动」）
    'para2_economy':   [0, 2, 3, 4, 5, 6],     # 收入 / 数据回扣 / 观念 / 技术 / 城市化 / 政策（删「价格」与收入重叠、「人群」偏弱）
    'para2_campus':    [0, 2, 3, 4, 5, 6],     # 时间管理 / 负面·挤占 / 合作 / 长期收益 / 负面·盲从 / 家校协同
    'para2_social':    [0, 1, 2, 5, 6, 7],     # 工作 / 消费 / 数据回扣 / 职场流动 / 生活旅游 / 养老
    'para2_sports':    [0, 1, 2, 3, 4, 5],     # 久坐 / 数据回扣 / 观念 / 工具 / 设施 / 宣传
    'para2_culture':   [0, 1, 3, 4, 5],        # 贴近生活 / 数据回扣 / 新媒体 / 课程 / 文化自信
    'para3_positive':  [0, 1, 2, 3, 4, 5, 6, 9, 10, 11],   # 6 主体首句 + 政府·企业·媒体·个人的第二句
    'para3_negative':  [0, 1, 2, 3, 4, 5, 7, 8, 11],       # 6 主体首句 + 学校·家庭·个人的第二句
}

# ---------------- 2) 🎓 评分老师视角（15 分） ----------------
TEACHER = [
    ['档位的分界线不是语言，是内容针对性',
     '四档（10~12）与五档（13~15）的区别不在句式，而在<b>内容要点是否全部覆盖且贴合这张图</b>。'
     '语言再漂亮，只要第二段归因、第三段建议<b>换到任何年份都能原样使用</b>，就会被压在四档——这是模板最大的风险，'
     '也是每次写作必须往句子里塞「本题专属信息」的原因。'],
    ['数据必须准确，这是硬指标',
     '数值、单位、年份、倍数一个都不能错：最高/最低值要有，起止值要对得上图。'
     '<b>算错倍数或抄错数字，直接扣内容分</b>，比语法错误严重得多（如 0.5 → 4 billion 是 8 倍，不是"翻了一倍"）。'],
    ['三段字数这样分',
     '<b>P1 图表描述 40~55 词 · P2 归因 55~65 词 · P3 评论建议 45~55 词</b>，合计 <b>150~180 词</b>。'
     '超 200 词不加分，只会提高出错率；低于 150 词按字数不足扣分。'],
    ['万能句只能保底，不能加分',
     '<b>Relevant authorities should…</b>、<b>with the development of…</b>、<b>Only in this way can…</b> 阅卷人一眼能认出。'
     '它们保证语言分不掉，但内容分要靠<b>图里的具体信息</b>：最高值是谁、涨了多少、哪一年翻倍、哪个主体在领跑。'],
    ['评论段要"为什么/怎么办"，不要表态',
     'P3 写「我认为这个现象很好」等于没写。四档以上要求「对目标读者产生预期效果」——'
     '<b>要么给出机制（为什么会这样），要么给出可执行的做法（谁该做什么）</b>。'],
    ['时态：图用过去，评论用现在',
     '图表数据都是历史年份 → <b>一般过去时 / 过去完成时</b>（climbed / had doubled by 2008）；'
     '归因与建议 → <b>一般现在时</b>（has become / should provide）。<b>时态混用是最常见的失分点</b>。'],
    ['别整句照抄题干',
     '题干里 directions 的句子抄进作文不计内容分，还可能被判套作。'
     '把 "interpret the chart and give your comments" 这种要求<b>用自己的话转述</b>成句子框架。'],
    ['分数预期：认真填槽 11~13 分，13+ 靠"本题专属"',
     '数据准确 + 三段完整 + 语言基本准确 = 二档到三档（<b>11~13 / 15</b>）；'
     '<b>13 分以上要求每一段都有针对这张图的具体归类或具体主体</b>，这是模板给不了的，只能靠平时套真题练出来。'],
]

# ---------------- 3) ✍️ 答题动线 ----------------
FLOW = [
    ['① 审题', '3 min',
     '圈出四件事：<b>图型</b>（柱 / 饼 / 折线 / 表格）、<b>对象</b>（几个事物、谁和谁比）、<b>时间跨度</b>（哪年到哪年 / 单一时间点）、'
     '<b>单位</b>（billion / million / %）。再判断类型：<b>静态</b>（一个时间点的占比分布）还是<b>动态</b>（随年份变化）。'],
    ['② 定骨架', '1 min',
     '静态 → 用「静态骨架」；动态 → 三套走势骨架里选一套：'
     '<b>单线上升</b>（只有一个事物）/ <b>同向不同速</b>（都在涨但快慢不同）/ <b>一升一降</b>（有涨有跌）。'
     '选错骨架整段都会别扭。'],
    ['③ 定归因', '2 min',
     '想好 2 个<b>具体机制</b>，不要写「生活水平提高」这种空话。可用的一套推理链：'
     '<b>收入↑ → 价格↓ / 可及性↑</b>；<b>技术↑ → 成本↓</b>；<b>政策 + 基建 → 供给↑</b>；<b>观念变 → 需求变</b>。'],
    ['④ 写作', '22 min',
     'P1 = 骨架 + 1 句数据补充；P2 = 骨架 + 2 句归因；P3 = 骨架 + 2 句主体句。'
     '<b>边写边填 {{ }} 槽位</b>，不要留到最后统一填（容易漏）。'],
    ['⑤ 填槽', '随写随填',
     '每个 {{ }} 都要换成本题的具体内容，数字与图一致、单位统一。'
     '不确定写哪个主体时，回头用「⚡ 弹药句池」按用途标签挑。'],
    ['⑥ 检查', '5 min',
     '对着下方「✅ 交卷前自查表」逐条过；重点看<b>数字、时态、单位、词数</b>四项。'],
]

# ---------------- 4) 📐 数据描述语言工具 ----------------
DATA_LANG = [
    ['上升 / 增长', 'climb · rise · grow · increase · surge · soar',
     'climb / rise / grow 是中性动词，surge / soar 表示猛涨。<b>rise 是不及物动词，没有被动</b>：'
     'the number <b>rose</b> ✓ / was risen ✗。典型句：<b>It climbed from 0.5 billion in 2000 to 4 billion in 2008.</b>'],
    ['下降 / 减少', 'fall · decline · drop · decrease · slide',
     '同样<b>没有被动语态</b>：the figure <b>fell</b> from 0.7 to 0.5。'
     '说到"降到"用 <b>drop to</b>，"下降了 X"用 <b>fall by X</b>（to 是终点、by 是幅度，别混）。'],
    ['幅度与速度', 'sharply · steadily · slightly · dramatically · gradually',
     '副词修饰动词：<b>rose steadily</b> / <b>fell sharply</b>。'
     '说倍数最划算：<b>more than doubled</b>（翻了一倍多）/ <b>nearly tripled</b> / <b>three times as many as</b>。'],
    ['占比（饼图/柱图）', 'account for · make up · take up · constitute · the largest share',
     '标准说法：<b>{{item1}} alone accounts for {{percent1}} of the total.</b>'
     '注意 <b>account for 用主动</b>，占比的主语是事物本身。'
     'percentage 指数值本身（a high percentage），percent 跟在数字后（20 percent，<b>不加 s</b>）。'],
    ['比较与对照', 'three times as many as · twice the figure for · outnumber … by 2 to 1 · slightly higher than',
     '两组对比的万能骨架：<b>A rose from X to Y, while B fell from P to Q.</b>'
     '幅度不同时：<b>Both rose, but A climbed faster than B.</b>'],
    ['极值与走势', 'peak at · hit a low of · level off · remain steady · fluctuate within a narrow range',
     '最高点 <b>peaked at 4 billion</b>；最低点 <b>hit a low of 0.5 billion</b>；'
     '走平 <b>levelled off at</b>；小幅波动 <b>fluctuated within a narrow range</b>。'
     '写极值是拿内容分最省力的一步，<b>别漏</b>。'],
]

MISTAKES = [
    ['rise / fall 加了被动', 'the number <b>was risen</b> ✗ → the number <b>rose</b> ✓（rise / fall / decline / drop 都不及物）'],
    ['amount / number 用错', 'the <b>amount</b> of people ✗ → the <b>number</b> of people ✓（number 可数、amount 不可数）'],
    ['数字写法', '<b>0.5 billion</b> ✓ / 500 millions ✗ / 500 million ✓；<b>20 percent</b> 不加 s'],
    ['时态混用', '数据用过去时（climbed），归因用现在时（has become）；"到某年为止"用过去完成 <b>had doubled by 2008</b>'],
    ['主谓一致', 'The <b>number</b> of users <b>was</b>…（单数）；The <b>figures</b> <b>were</b>…（复数）'],
    ['比较级不成立', 'more higher ✗ / higher ✓；as many as 中间放原级：<b>three times as many as</b>'],
]

# ---------------- 5) ✅ 交卷前自查表 ----------------
CHECKLIST = [
    '数字与图逐个核对：起止值、最高值、最低值、倍数',
    '单位统一：billion / million 没混用，百分比写成 % 或 percent',
    '时态：图表用过去时，归因/建议用现在时',
    '每个 {{ }} 槽位都换成本题内容了吗',
    '主谓一致：The number / The percentage 用单数',
    '三段都有主题句，段落数符合题目要求',
    '词数在 150~180（不够补一句归因，超了删一句弹药）',
    '没有整句照抄题干 directions',
    '开头没有 "With the development of…" 这类空话',
    '拼写与大小写：句首字母、专有名词、专名首字母',
]
