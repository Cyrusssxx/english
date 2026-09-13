# -*- coding: utf-8 -*-
'''把 17 篇大作文套用示范扩写到 175-195 词（考研英语二要求 150 词以上，正常 170-200）。
策略：保留原有段落与数字，只做三类定点修改——
  fixes   : 段内定点替换（既补词数，也让 5 条关键句型在正文里字面出现）
  p1_add / p2_add / p3_add : 段尾追加句子（英文+中文成对）
用法：python tools/expand_apply.py
'''
import json
import re
import sys

AP_FP = 'pwa/data/writing_apply.json'


def wc(t):
    return len([x for x in re.split(r'\s+', (t or '').strip()) if re.search(r'[A-Za-z0-9]', x)])


def paras(t):
    return [p.strip() for p in re.split(r'\n\s*\n', (t or '').strip()) if p.strip()]


# ===== 逐年份补写（EN / CN 成对） =====
PATCH = {    '2011': {
        'p1_new': ('The bar chart shows that the market shares associated with the three auto brands did not move '
                   'in a uniform direction during the periods presented. Chinese brands climbed from a modest '
                   'share to the leading position, while Japanese brands fell by nearly 10 percentage points and '
                   'were displaced from their leading position. Chinese brands expanded their share by nearly the same '
                   'margin as Japanese brands lost theirs. By contrast, American brands held steady, with only a '
                   'slight increase.'),
        'p1_new_cn': ('该柱状图表明，三个汽车品牌的市场份额在相应时期内并未朝着相同方向变化。国产品牌从'
                      '一个不大的份额攀升至领先地位，日系品牌则下降近 10 个百分点、被赶下了头名位置。两大'
                      '国产品牌扩大的份额与日系品牌失去的份额大致相当。相比之下，美系品牌保持稳定，仅略有增长。'),
        'p2_add': ('In addition, rising national confidence has made domestic brands a more attractive option.'),
        'p2_add_cn': '此外，民族自信的提升也让国产品牌更具吸引力。',
        'p3_add': ('Manufacturers should invest more in research and development instead of competing merely on '
                   'price, and should listen to the feedback of car owners.'),
        'p3_add_cn': '厂商应加大研发投入，而不是仅仅打价格战，并认真听取车主的反馈。',
    },    '2012': {
        'fixes': [
            ('where none of them satisfied and 64% expressing dissatisfaction', None),
            ('with none of them satisfied and 64% expressing dissatisfaction',
             'where none of them felt satisfied and 64% expressed dissatisfaction'),
            ('account for the largest share of satisfaction, at 40%',
             'account for the largest share, at 40%'),
        ],
        'fixes_cn': [
            ('41 至 50 岁的中间组水平最低，无人满意，64% 表示不满。',
             '41 至 50 岁的中间组水平最低，无一人感到满意，64% 表示不满。'),
            ('50 岁以上员工满意度占比最大，达 40%', '50 岁以上员工占比最大，达 40%'),
        ],
        'p2_add': 'Middle-aged staff therefore need more encouragement rather than more pressure.',
        'p2_add_cn': '因此，中年员工需要的是更多鼓励，而不是更大压力。',
        'p3_add': ('Employers should also design more reasonable assessment systems for middle-aged staff, so that '
                   'experience is rewarded rather than overlooked.'),
        'p3_add_cn': '雇主还应为中年员工设计更合理的考核机制，让经验得到回报而不是被忽视。',
    },    '2013': {
        'p1_add': 'Overall, the figure kept showing a steady upward trend throughout the four years.',
        'p1_add_cn': '总体来看，这一比例在四年间呈现稳定上升趋势。',
        'p3_add': ('Media organizations should present the value of part-time work objectively, so that students do '
                   'not mistake it for a way of earning easy money.'),
        'p3_add_cn': '媒体应客观介绍兼职的价值，避免学生把它误认为轻松赚钱的途径。',
    },    '2014': {
        'p1_add': 'The gap therefore narrowed from 520 million to 10 million.',
        'p1_add_cn': '差距因此从 5.2 亿缩小到 1000 万。',
        'p3_add': ('Cities should also lower the barriers for newcomers and protect the rights of migrant workers, '
                   'so that those who move can settle down with dignity.'),
        'p3_add_cn': '城市也应降低落户门槛、保障外来务工人员的权益，让进城的人能够有尊严地安顿下来。',
    },    '2015': {
        'fixes': [
            ('In contrast, other items make up a relatively small proportion.',
             'In contrast, other items, such as decorations and fireworks, make up a relatively small proportion '
             'of the remaining 20%.'),
            ('The pie chart presents an uneven distribution among',
             'This pie chart presents an uneven distribution among'),
        ],
        'fixes_cn': [
            ('相比之下，其他项目占比很小。', '相比之下，装饰、烟花等其他项目占比很小，仅占余下的 20%。'),
        ],
        'p1_add': 'Seen as a whole, the chart shows how much weight Chinese families place on togetherness.',
        'p1_add_cn': '总体来看，这张图显示出中国家庭对团聚的重视程度。',
        'p3_add': ('Relevant authorities and media organizations should also encourage a plain and healthy holiday '
                   'culture, so that the true meaning of reunion is not buried under lavish spending.'),
        'p3_add_cn': '有关部门与媒体也应倡导朴素健康的节庆文化，别让团圆的本意被铺张消费掩盖。',
    },    '2016': {
        'p2_add': 'In other words, the figures mirror how students nowadays balance study and rest.',
        'p2_add_cn': '换言之，这些数字反映出当下学生如何平衡学习与休息。',
        'p3_add': ('Universities may also offer more affordable travel programmes, so that students with limited '
                   'budgets are not excluded from the chance to see the wider world.'),
        'p3_add_cn': '高校也可提供更多价格合理的出行项目，让预算有限的学生同样有机会看看外面的世界。',
    },    '2017': {
        'fixes': [("keep pace with the public's growing demand", 'keep pace with the public demand')],
        'fixes_cn': [],
        'p1_add': 'Taken together, the two lines point to a booming cultural market.',
        'p1_add_cn': '总体来看，两条曲线共同指向一个繁荣的文化市场。',
        'p2_add': 'Besides, museums themselves have become more visitor-friendly, with free admission and better exhibitions.',
        'p2_add_cn': '此外，博物馆自身也变得更友好，免费开放且展览更优质。',
        'p3_add': ('Measures should also be taken to spread such resources more evenly, so that people in smaller '
                   'cities can enjoy them as well.'),
        'p3_add_cn': '还应采取措施让这些资源分布更均衡，让中小城市的居民同样能够享受。',
    },    '2018': {
        'p3_add': ('Restaurants should not chase distinctive features at the cost of food quality, and consumers '
                   'should remember that dining out is a pleasure rather than a burden.'),
        'p3_add_cn': '餐厅不该以牺牲菜品质量为代价追求特色，消费者也应记住外出就餐是享受而非负担。',
    },    '2019': {
        'fixes': [('a way of securing an advantage', 'a way to secure an advantage')],
        'fixes_cn': [],
        'p3_add': ('Authorities should also create more favourable conditions for young people who choose to start '
                   'their own businesses, so that entrepreneurship is a real option rather than a last resort.'),
        'p3_add_cn': '有关部门还应创造条件支持选择自主创业的年轻人，让创业成为真正的选择而非退路。',
        'p3_add2': 'Authorities should also create more favourable conditions for young entrepreneurs.',
        'p3_add2_cn': '有关部门也应为青年创业者创造更有利的条件。',
    },    '2020': {
        'p1_add': 'Such a pattern shows that mobile reading has become part of daily campus life.',
        'p1_add_cn': '这一格局说明手机阅读已成为校园日常生活的一部分。',
        'p2_add': 'Finally, the wide coverage of campus networks has made reading on a phone almost effortless.',
        'p2_add_cn': '最后，校园网络的广泛覆盖让用手机阅读几乎不费力气。',
        'p3_add': ('They should also set aside time for printed books and face-to-face communication, so that '
                   'fragmented reading does not crowd out deeper thinking.'),
        'p3_add_cn': '还应留出时间阅读纸质书、进行面对面交流，别让碎片化阅读挤占深度思考。',
    },    '2021': {
        'p3_add': ('Communities should also organize group activities, so that residents can enjoy the company of '
                   'others as well as the freedom of exercising alone.'),
        'p3_add_cn': '社区还可组织集体活动，让居民既能享受独自锻炼的自由，也能体会与他人结伴的乐趣。',
        'p3_add2': 'Communities should also organize more group activities for residents.',
        'p3_add2_cn': '社区也应为居民组织更多集体活动。',
    },    '2022': {
        'fixes': [('the growth in rural areas was particularly striking', 'the trend is particularly striking in rural areas')],
        'fixes_cn': [('但农村地区的增长尤为显著', '但农村地区这一趋势尤为显著')],
        'p3_add': ('Packaging and delivery should also be made greener, so that the rapid growth does not come at '
                   'the cost of the environment.'),
        'p3_add_cn': '还应推进包装与配送的绿色化，别让快速增长以牺牲环境为代价。',
        'p3_add2': 'Packaging and delivery should also be made greener.',
        'p3_add2_cn': '包装与配送也应更绿色。',
    },    '2023': {
        'fixes': [('marked a watershed, when the growth accelerated', 'marked a watershed when the growth accelerated')],
        'fixes_cn': [],
        'p1_add': 'The figure has grown almost threefold within a decade, and the momentum has yet to fade.',
        'p1_add_cn': '这一数值十年间增长近两倍，势头仍未减弱。',
        'p2_add': 'Finally, health education has been introduced into school curricula from an early age.',
        'p2_add_cn': '最后，健康教育已从小学阶段起进入课程体系。',
        'p3_add': ('Media organizations should also present medical information objectively, so that the public is '
                   'not misled by exaggerated claims.'),
        'p3_add_cn': '媒体还应客观介绍医学信息，避免公众被夸大的宣传误导。',
    },    '2024': {
        'p2_add': 'Meanwhile, employers increasingly ask for evidence of real experience rather than exam scores alone.',
        'p2_add_cn': '与此同时，雇主越来越看重真实经历，而不只是考试分数。',
        'p3_add': ('Courses should also be linked more closely with local industries, so that what is learned in '
                   'class can be put to use in real workplaces.'),
        'p3_add_cn': '课程还应与本地产业更紧密衔接，让课堂所学能在真实岗位中用得上。',
    },    '2025': {
        'fixes': [('a low-intensity activity suitable for most elderly people', 'a low-intensity activity suitable for the elderly')],
        'fixes_cn': [('散步是适合多数老年人的低强度活动', '散步是适合老年人的低强度活动')],
        'p1_add': 'Taken together, these figures show that the elderly prefer simple and accessible pastimes.',
        'p1_add_cn': '总体来看，这些数字说明老年人更偏爱简单、方便的活动。',
        'p3_add': ('Families should care about the elderly\u2019s real needs rather than simply keeping them '
                   'entertained, and communities should organize activities suited to older residents.'),
        'p3_add_cn': '家庭应关心老年人的真实需求，而不只是让他们有消遣；社区也应组织适合老年人的活动。',
    },    '2026': {
        'p3_add': ('Families should join their children in these activities rather than merely watching them, and '
                   'communities may make public spaces safer and more accessible for children.'),
        'p3_add_cn': '家庭应参与孩子的活动而非只是旁观，社区也可让公共空间更安全、更适合儿童使用。',
        'p3_add2': 'Families should also set aside regular time for outdoor play.',
        'p3_add2_cn': '家庭还应留出固定的户外活动时间。',
    },
}


def main():
    data = json.load(open(AP_FP, encoding='utf-8'))
    report = []
    for y, p in PATCH.items():
        v = data[y]
        en = paras(v['apply_en'])
        cn = paras(v.get('apply_cn'))
        # 段内定点替换
        for old, new in p.get('fixes', []):
            if new is None:
                continue
            for i, para in enumerate(en):
                if old in para:
                    en[i] = para.replace(old, new)
                    break
            else:
                print('  ⚠ %s 未找到 EN 定点串: %s' % (y, old[:40]))
        for old, new in p.get('fixes_cn', []):
            for i, para in enumerate(cn):
                if old in para:
                    cn[i] = para.replace(old, new)
                    break
            else:
                print('  ⚠ %s 未找到 CN 定点串: %s' % (y, old[:30]))
        # 整段替换 P1
        if p.get('p1_new'):
            en[0] = p['p1_new']
            cn[0] = p['p1_new_cn']
        # 段尾补句
        for k, pk in (('p1_add', 'p1'), ('p2_add', 'p2'), ('p3_add', 'p3')):
            if p.get(k):
                idx = int(pk[1]) - 1
                en[idx] = en[idx].rstrip() + ' ' + p[k].strip()
                if p.get(k + '_cn'):
                    cn[idx] = cn[idx].rstrip() + p[k + '_cn'].strip()
        v['apply_en'] = '\n\n'.join(en)
        v['apply_cn'] = '\n\n'.join(cn)
        report.append((y, wc(v['apply_en'])))
    json.dump(data, open(AP_FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('%-6s %s' % ('年份', '扩写后词数'))
    for y, n in report:
        bad = '' if 170 <= n <= 200 else '  ⚠'
        print('%-6s %-5d%s' % (y, n, bad))


if __name__ == '__main__':
    main()
