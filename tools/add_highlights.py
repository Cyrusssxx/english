import json, io

# 官方「亮点词汇」+「必备搭配」（2014 用用户提供版本，其余年份据 OCR 修复）
HIGHLIGHTS = {
2010: {
  'words': [
    ('diagram', '图表'), ('demonstrate', '展示，演示'), ('contrastingly', '形成鲜明对比的是'),
    ('potential', '潜在的'), ('stimulate', '刺激'),
  ],
  'collocations': [
    ('during the same period', '在同一时期'), ('reach saturation', '达到饱和'),
    ('population size', '人口规模'), ('an increasing number of', '越来越多的'),
    ('at a fast rate', '以飞快的速度'), ('in comparison', '相比之下'),
    ('be expected to', '预期会'), ('extra demand', '额外的需求'),
  ],
},
2011: {
  'words': [
    ('dominate', '支配、控制'), ('noticeable', '明显的'), ('slip', '下降'),
    ('given', '鉴于'), ('bargain', '便宜商品'), ('plight', '困境'),
    ('reminder', '提醒认识的事物'), ('soul', '灵魂'), ('consistently', '一贯地'),
  ],
  'collocations': [
    ('a slight increase', '小幅上涨'),
    ('be displaced from one’s leading position by', '被……取代主导地位'),
    ('expand one’s share', '增加市场份额'), ('by nearly the same margin', '几乎相同幅度'),
    ('is to be expected', '预料之中的'), ('worldwide fame', '世界声誉'),
    ('reliable quality', '可信赖的质量'), ('narrow the technology gap', '缩小技术差距'),
    ('appetite for', '对……的喜好'), ('quality complaint', '质量投诉'),
    ('maintain market popularity', '保持市场满意度'),
  ],
},
2012: {
  'words': [
    ('report', '报告'), ('declare', '宣称'), ('express', '表达'),
    ('surely', '肯定'), ('energetic', '有活力的'), ('competent', '有能力的'),
    ('professional', '专业人士'), ('consequent', '相应的'), ('occasional', '偶尔的'),
    ('mostly', '大部分地'), ('understandably', '可以理解地'), ('crown', '圆满完成或结束'),
    ('afflict', '使……苦恼'),
  ],
  'collocations': [
    ('relate to', '与……相关'), ('at the age from...to...', '……岁到……岁之间的'),
    ('reach a career plateau', '进入职场高原'), ('sense of powerlessness', '无力感'),
    ('reduce...to...', '使陷入（坏的）状况或情形中'), ('in an upward spiral', '处在上升阶段'),
    ('career maturity', '职业发展成熟'), ('retirement life', '退休生活'),
    ('career trouble', '职场问题'),
  ],
},
2013: {
  'words': [
    ('occur', '发生'), ('motive', '动机'), ('push', '促使'),
    ('beneficial', '有利的'), ('risk', '风险'),
  ],
  'collocations': [
    ('in the graduation year', '毕业那年，大四'), ('become increasingly willing to', '越来越愿意'),
    ('the growing wish to', '越发迫切地想'), ('reasonable and wise', '有道理且明智的'),
    ('reach a record high', '创下历史新高'), ('reach higher grade level', '进入高年级'),
    ('studying materials', '学习资料'), ('social events', '社交活动'),
    ('erosion of study time', '侵蚀学习时间'), ('suffer academically', '学业上受到损害'),
  ],
},
2014: {
  'words': [
    ('moderate', '温和的、不剧烈的'), ('considerably', '可观地'), ('contrastingly', '相对地、相反地'),
    ('narrow', '缩小'), ('urbanization', '城市化'), ('transform', '变化'),
    ('initiatively', '主动地'), ('drive', '促使'), ('flock', '涌向'),
    ('indication', '指标、标志'), ('superficially', '肤浅地'), ('foster', '促进'),
    ('integration', '融合'),
  ],
  'collocations': [
    ('population distribution', '人口分布'), ('experience a dramatic shift', '经历了巨大变化'),
    ('population gap', '人口差距'), ('joint effects', '联合作用'),
    ('city resident', '城市居民'), ('integrate into', '融入'),
    ('civilized habits', '文明习惯'), ('urban pauper', '城市贫民'),
    ('be isolated from', '与……隔绝'), ('prosperity and convenience', '繁荣和便利'),
  ],
},
2015: {
  'words': [
    ('fulfillment', '幸福感'), ('extraordinary', '超凡'), ('handsome', '大量的'),
    ('blindly', '盲目地'), ('intention', '意图'), ('squander', '挥霍'),
    ('transient', '短暂的'), ('rationally', '理性地'), ('concern', '重要的事'),
  ],
  'collocations': [
    ('respective proportions', '各自的比例'), ('account for', '占'),
    ('facilitate interpersonal relationship', '发展人际关系'), ('family reunion', '家庭团圆'),
    ('invest on', '投资'), ('go to extremes', '走向极端'),
    ('pursue pride', '追求面子'), ('impose heavy economic burden on', '给……造成沉重的经济负担'),
  ],
},
2016: {
  'words': [
    ('illuminating', '有启发性的'), ('poll', '民意测验，调查'), ('foster', '培养，促进'),
    ('unwind', '使松弛，放松'), ('recharge', '放松休息，恢复精力'), ('ample', '足够的，充足的'),
    ('lure', '吸引，诱惑'), ('antidote', '（to）克服……的良方'), ('refreshed', '恢复精神的'),
    ('revitalized', '焕发生机的'),
  ],
  'collocations': [
    ('relieve pressure', '缓解压力'), ('come into contact with', '接触到，遇到'),
    ('have one’s share of', '有自己的一份儿……'), ('attach meaning to', '对……赋予意义'),
  ],
},
}

for y, data in HIGHLIGHTS.items():
    fn = f'tools/extracted/modules/{y}_extra.json'
    d = json.load(io.open(fn, encoding='utf-8'))
    for a in d.get('articles', []):
        if a['type'] == 'writing_b':
            a['vocab_highlights'] = data
    json.dump(d, io.open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(y, 'writing_b 写入 vocab_highlights')
