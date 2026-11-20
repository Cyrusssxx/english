# -*- coding: utf-8 -*-
"""押题 18 篇大作文的「套用示范式」选句方案。

每篇 = 用哪些模板句池原句（按 tag）+ 往 {{topic}} 里填的英文主题词。
机制完全复用套用示范：从 writing_templates.json 按 tag 取原句 → 填 topic →
P2 三条机制句前加骨架衔接词。这样押题范文的每一句都是用户自己背过的
模板原句，而不是另写的新句。

字段：
  topic2 / topic2cn   P2 机制句里 {{topic}} 的英文 / 中文填法
  why                 P2 三条机制句的 tag（来自 para2_why 的 sentences[].tag）
  topic3 / topic3cn   P3 对策句里 {{topic}} 的英文 / 中文填法（若对策句无槽位则忽略）
  do                  P3 对策句的 tag；正面用 para3_positive，负面用 para3_negative
  stance              'pos' / 'neg'：立场句 + 收尾句走正面版还是负面版

tag 必须存在于对应池，否则校验会报错。topic 用英文名词短语，填进句子要通顺。
"""
PLAN = {
    # ── 单图表 5 篇 ──
    6: dict(stance='pos', topic2='continuing education', topic2cn='继续教育',
            why=['科技普及', '就业门槛', '教育公平'],
            topic3='lifelong learning', topic3cn='终身学习',
            do=['政府·长效', '学校', '政府']),
    7: dict(stance='pos', topic2='new energy vehicles', topic2cn='新能源汽车',
            why=['科技普及', '环保意识', '绿色出行'],
            topic3='green travel', topic3cn='绿色出行',
            do=['企业/平台', '政府', '个人·习惯']),
    8: dict(stance='pos', topic2='public transport', topic2cn='公共交通',
            why=['城市化', '便利', '绿色出行'],
            topic3='environmentally friendly travel', topic3cn='环保出行',
            do=['政府·长效', '个人·习惯', '媒体']),
    9: dict(stance='pos', topic2='career choice', topic2cn='择业',
            why=['就业门槛', '观念', '教育公平'],
            topic3='genuine interest', topic3cn='真正的兴趣',
            do=['学校', '个人', '企业/平台']),
    10: dict(stance='pos', topic2='convenience stores', topic2cn='便利店',
            why=['城市化', '便利', '收入'],
            topic3='community retail', topic3cn='社区零售',
            do=['政府', '企业/平台', '媒体·展示']),
    # ── 图画题 1~5（负面） ──
    1: dict(stance='neg', topic2='AI tools', topic2cn='人工智能工具',
            why=['AI 教育', '规则滞后', '逐利'],
            topic3='AI tools', topic3cn='人工智能工具',
            do=['学校·课程', '个人·记录', '媒体']),
    2: dict(stance='neg', topic2='companionship', topic2cn='真正的陪伴',
            why=['职场时间', '生活节奏', '观念'],
            topic3='quality time', topic3cn='高质量陪伴',
            do=['家庭·作息', '个人', '学校/家庭']),
    3: dict(stance='neg', topic2='rest', topic2cn='休息',
            why=['职场时间', '生活节奏', '就业门槛'],
            topic3='rest', topic3cn='休息',
            do=['个人·记录', '家庭·作息', '企业·雇主']),
    4: dict(stance='neg', topic2='green consumption', topic2cn='绿色消费',
            why=['逐利', '环保意识', '观念'],
            topic3='over-packaging', topic3cn='过度包装',
            do=['政府', '个人', '媒体']),
    5: dict(stance='neg', topic2='online information', topic2cn='网络信息',
            why=['逐利', '规则滞后', '教育公平'],
            topic3='information literacy', topic3cn='信息素养',
            do=['学校·课程', '个人·记录', '企业/平台']),
    # ── 图表/图画 11~18 ──
    11: dict(stance='pos', topic2='barrier-free access', topic2cn='无障碍通道',
            why=['公共投入', '观念', '城市化'],
            topic3='accessible facilities', topic3cn='无障碍设施',
            do=['政府', '政府·长效', '媒体']),
    12: dict(stance='pos', topic2='first aid', topic2cn='急救知识',
            why=['学校', '公共投入', '科技普及'],
            topic3='first-aid skills', topic3cn='急救技能',
            do=['学校', '政府·长效', '媒体']),
    13: dict(stance='pos', topic2='returning home', topic2cn='回国发展',
            why=['国产替代', '教育公平', '城市化'],
            topic3='home-grown talent', topic3cn='本土人才',
            do=['政府', '企业/平台', '学校']),
    14: dict(stance='neg', topic2='elderly care', topic2cn='养老服务',
            why=['人口结构', '城市化', '公共投入'],
            topic3='elderly care', topic3cn='养老保障',
            do=['政府', '家庭', '个人']),
    15: dict(stance='pos', topic2='online shopping', topic2cn='线上销售',
            why=['科技普及', '便利', '观念'],
            topic3='online and offline sales', topic3cn='线上线下销售',
            do=['企业/平台', '政府·长效', '媒体']),
    16: dict(stance='pos', topic2='traditional art', topic2cn='传统艺术',
            why=['文化新媒介', '文化传承', '教育公平'],
            topic3='traditional culture', topic3cn='传统文化',
            do=['媒体·展示', '学校', '政府·长效']),
    17: dict(stance='pos', topic2='genuine passion', topic2cn='真正的热爱',
            why=['观念', '就业门槛', '教育公平'],
            topic3='personal interest', topic3cn='个人兴趣',
            do=['个人', '学校', '家庭']),
    18: dict(stance='neg', topic2='tourism', topic2cn='旅游',
            why=['环保意识', '逐利', '规则滞后'],
            topic3='tourism development', topic3cn='旅游发展',
            do=['政府', '企业/平台', '媒体']),
}
