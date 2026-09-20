# -*- coding: utf-8 -*-
"""2026 考研英语二 新题型 Part B（信息匹配，41-45）→ 合并进 pwa/data/2026.json + index.json

数据来源（多源交叉核验，4 源一致）：
  · 官方试题 PDF：http://www.zkedu.com.cn/upload/download/2026_yu.pdf（含 Directions）
  · 完整版 PDF：https://images.eduego.com/Uploads/files/wenjian/202601/202601120046408.pdf
    （本脚本正文/选项/答案/解析逐字取自该 PDF 第 15-17 页，段落划分按原文行文重建）
  · 沈阳华章真题页、希赛网试题页（选项与答案互校）
答案：41 E / 42 A / 43 G / 44 C / 45 D（EAGCD，四源一致）
注：原文无标题（Part B 惯例），title/topic 为便于站内展示的中文概括；
    逐句中文译文为本脚本新译（官方无 Part B 译文），非引自解析。
幂等：重复执行会覆盖 2026_newtype 这一篇，不影响 2026 其他文章。
"""
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'pwa', 'data')

TITLE = '森林恢复：种子供给的瓶颈与「为谁恢复」之问'
TOPIC = ('新题型（信息匹配）：将左栏的五位森林恢复领域人士与右栏中与其观点相符的陈述相匹配'
         '（右栏有 A-G 七项，其中两项多余）。')

# (para, en, cn)
BODY = [
    # ── 第 1 段
    (1, 'In an effort to support restoration programmes, specialists are developing supplies of seeds and seedlings, '
        'maintaining gene banks and sequencing the genomes of indigenous trees and other crops.',
        '为了支持生态恢复项目，专家们正在开发种子与树苗的供给，维护基因库，并对本土树木和其他作物的基因组进行测序。'),
    (1, 'Their work deals with one of the problems that could block major restoration efforts in different parts of the world.',
        '他们的工作针对的是一个可能阻碍世界不同地区大规模恢复工作的难题。'),
    # ── 第 2 段
    (2, '“Where’s the planting material going to come from? That’s one big bottleneck,” says genetic-resources specialist '
        'Ramni Jamnadass.',
        '遗传资源专家拉姆尼·贾姆纳达斯说：“种植材料从哪里来？这是一个大瓶颈。”'),
    # ── 第 3 段
    (3, 'Asia is arguably the region most neglected by global efforts to increase diversity in restoration and to study '
        'native species.',
        '可以说，在提高恢复工作的多样性、研究本土物种方面，亚洲是全球努力中最被忽视的地区。'),
    (3, 'Christopher Kettle, Bioversity International’s director for forest genetic resources and restoration in Rome, '
        'says that the need for infrastructure—things such as mechanisms for collecting and storing seeds, and nurseries '
        'to raise seedlings—might be most desperate here because many trees are ‘masting’ species, which don’t produce '
        'seeds every year.',
        '国际生物多样性中心（Bioversity International）驻罗马的森林遗传资源与恢复事务主任克里斯托弗·凯特尔表示，当地对基础设施'
        '——比如收集和储存种子的机制、培育树苗的苗圃——的需求可能最为迫切，因为许多树木都属于“大小年结籽”（masting）的物种，'
        '并非每年都结籽。'),
    (3, 'People need to be ready.',
        '人们必须提前做好准备。'),
    # ── 第 4 段
    (4, '“Otherwise, you miss the boat, you lose all the seed and you’ve got to wait another seven years,” says Kettle.',
        '凯特尔说：“否则你就错过时机了，种子全丢了，还得再等七年。”'),
    (4, '“This is a really, really critical issue for restoration in Southeast Asia, because many of the most important '
        'timber species and tree species—the ones that will lock up the most carbon—they’re all masting species.”',
        '“对东南亚的生态恢复来说，这是一个极其关键的问题，因为许多最重要的用材树种和乔木树种——也就是固碳最多的那些——'
        '都属于大小年结籽的物种。”'),
    # ── 第 5 段
    (5, 'Climate change is a driving factor in the push to restore forests, but it also raises questions, such as where '
        'trees can thrive in the future.',
        '气候变化是推动森林恢复的一大因素，但它也带来了新的问题，比如树木未来能在哪里繁茂生长。'),
    (5, 'Climate change is also expected to alter relationships between trees, insects, diseases and other forest species.',
        '气候变化预计还会改变树木、昆虫、病害以及其他森林物种之间的关系。'),
    # ── 第 6 段
    (6, '“Insects that today are a minor problem may become a major problem if they can produce three or four generations '
        'in a year,” says forest ecologist John Stanturf.',
        '森林生态学家约翰·斯坦特夫说：“今天看来还算小问题的昆虫，如果一年能繁殖三四代，就可能变成大问题。”'),
    (6, 'This remains a significant knowledge gap.',
        '这仍然是一个重大的知识空白。'),
    (6, '“We know enough to know that this is a concern, but we don’t know enough about how to respond to it yet. '
        'That’s a great area to be doing research.”',
        '“我们知道的足以让我们意识到这是个隐患，但对如何应对还了解得不够。这是一个很值得研究的领域。”'),
    # ── 第 7 段
    (7, 'So is soil, says Cindy Prescott, a forest ecologist at the University of British Columbia in Vancouver.',
        '不列颠哥伦比亚大学（位于温哥华）的森林生态学家辛迪·普雷斯科特说，土壤也是如此。'),
    (7, '“If you don’t look at the soil at the start, you can spend a lot of money and time putting in species that '
        'aren’t going to survive there.”',
        '“如果一开始不考虑土壤，你可能会花掉大量金钱和时间，种下一些根本没法在那里存活的物种。”'),
    # ── 第 8 段
    (8, 'With so much research left to do, leaders in the field have been doing some soul-searching, and acknowledging '
        'that restoration can be motivated by—and designed to meet—different needs.',
        '由于还有大量研究要做，该领域的领军人物一直在反思，并承认恢复工作可能出于不同的目的，也应满足不同的需求。'),
    (8, '“When you talk about conservation or restoration, the first question has to be restoration by whom, for whom?” '
        'says Daniel Janzen, a biologist at the University of Pennsylvania.',
        '宾夕法尼亚大学生物学家丹尼尔·詹森说：“谈到保护或恢复，首要问题必须是：由谁来恢复，又为谁恢复？”'),
    # ── 第 9 段
    (9, 'The question can have more than one answer.',
        '这个问题的答案可能不止一个。'),
    (9, 'Much of the global funding for restoration is dedicated to developing it as a tool to mitigate climate change, '
        'notes restoration ecologist Pedro Brancalion.',
        '恢复生态学家佩德罗·布兰卡利翁指出，全球用于恢复的资金大部分都致力于把恢复打造成缓解气候变化的工具。'),
    (9, '“But if you ask a farmer in Brazil if he or she is concerned about climate change, they would say, ‘No, I am '
        'concerned about water,’” he says.',
        '他说：“但如果你问巴西的农民是否担心气候变化，他们会说：‘不，我担心的是水。’”'),
    (9, 'Their interests as stewards of the land need to be better integrated with those who have the money to support '
        'restoration.',
        '作为土地的守护者，他们的利益需要与那些有钱支持恢复工作的人更好地结合起来。'),
    # ── 第 10 段
    (10, 'That has been the strongest lesson of all for Robin Chazdon, a forest ecologist at the University of Connecticut.',
         '对康涅狄格大学的森林生态学家罗宾·查兹登来说，这是所有教训中最深刻的一条。'),
    (10, 'Restoration is about more than what gets planted in the ground, she says.',
         '她说，恢复工作不只是把什么种进土里那么简单。'),
    (10, '“Yes, it’s about forests, but it’s really about people. They are the agents of restoration.”',
         '“是的，这关乎森林，但真正关乎的是人。人才是恢复工作的执行者。”'),
]

POOL = {
    'A': 'People must pay attention to the fact that some kinds of trees do not produce seeds annually.',
    'B': 'Soil is an important element to be taken into account in forest restoration.',
    'C': 'The purpose of restoration efforts may be different from the real needs of the people involved.',
    'D': 'Human factors, as well as trees planted, should be emphasised in forest restoration.',
    'E': 'The supply of seeds is a tough problem that has to be dealt with.',
    'F': 'When it comes to restoration, we have to start with an awareness of whose interests to serve.',
    'G': 'Some creatures in the forest that multiply fast can become a great threat to forest restoration.',
}
POOL_CN = {
    'A': '人们必须注意这样一个事实：有些树种并非每年都结籽。',
    'B': '土壤是森林恢复中必须考虑的一个重要因素。',
    'C': '恢复工作的目的可能与相关人员的真实需求并不一致。',
    'D': '在森林恢复中，除了种下的树木，人的因素也应受到强调。',
    'E': '种子供应是一个必须解决的难题。',
    'F': '谈到恢复，我们必须从一开始就清楚要服务于谁的利益。',
    'G': '森林中繁殖迅速的生物可能成为森林恢复的巨大威胁。',
}

# (题号, 左栏人物, 答案, 解析【照抄官方完整版解析】, 定位段落)
QS = [
    (41, 'Ramni Jamnadass', 'E',
     '【信息匹配】本题主要考查同义复现、词义对应。定位句“种植材料从哪里来？这是一个很大的瓶颈”。选项中 The supply of '
     'seeds 对应原文第二段 the planting material（同义复现）；a tough problem 对应原文第二段 one big bottleneck（情感复现）。故选 E。',
     [2]),
    (42, 'Christopher Kettle', 'A',
     '【信息匹配】本题主要考查同义复现、语义对应。定位句内容较长，可重点关注逻辑关系处：原因状语从句重点论述“因为许多树木都是 '
     '‘masting’ 物种，它们每年都不会结出种子。人们需要做好准备”。People must pay attention to the fact 对应原文第三段 '
     'people need to be ready（同义复现）；some kinds of trees 对应第三段 many trees（原词复现）；do not produce seeds annually '
     '对应第三段 which don’t produce seeds every year。故选 A。',
     [3]),
    (43, 'John Stanturf', 'G',
     '【信息匹配】定位 Stanturf 的引语“Insects that today are a minor problem may become a major problem if they can produce '
     'three or four generations in a year”。creatures in the forest 对应文中的 Insects；multiply fast（繁殖很快）对应 produce '
     'three or four generations in a year；become a great threat 对应 become a major problem。故选 G。',
     [6]),
    (44, 'Pedro Brancalion', 'C',
     '【信息匹配】原文 Brancalion 指出：全球资金把恢复视为缓解气候变化的工具，但巴西农民关心的是水。这说明“官方/资助者的目的”'
     '（mitigate climate change）与“当地参与者的真实需求”（concerned about water）之间存在差异，正对应选项 C 的 '
     'purpose … different from … real needs。故选 C。',
     [9]),
    (45, 'Robin Chazdon', 'D',
     '【信息匹配】定位末段 Chazdon 的总结：Restoration is about more than what gets planted in the ground … “it’s really about '
     'people. They are the agents of restoration.”。其中 as well as trees planted 对应 more than what gets planted；'
     'Human factors … should be emphasised 对应 it’s really about people。故选 D。',
     [10]),
]


def main():
    fp = os.path.join(DATA, '2026.json')
    d = json.load(io.open(fp, encoding='utf-8'))

    sents = []
    for i, (para, en, cn) in enumerate(BODY, 1):
        sents.append({"id": "2026_newtype_s%02d" % i, "para": para, "en": en, "cn": cn, "words": []})

    para_sids = {}
    for s in sents:
        para_sids.setdefault(s['para'], []).append(s['id'])

    qs = []
    for num, person, ans, expl, paras in QS:
        related = [sid for p in paras for sid in para_sids.get(p, [])]
        qs.append({
            "id": "2026_newtype_q%d" % num,
            "number": num,
            "qtype": "匹配",
            "person": person,          # 匹配题必备：阅读区在该人名首次出现句前渲染「[41] 人名 在此作答 ▸」徽标行
            "stem": "第 %d 题：将左栏人物 %s 与右栏中的观点陈述相匹配" % (num, person),
            "stem_cn": "",
            "options": {},
            "options_cn": {},
            "answer": ans,
            "explanation": expl,
            "related_sentences": related,
        })

    art = {
        "id": "2026_newtype",
        "type": "newtype",
        "title": TITLE,
        "topic": TOPIC,
        "source": "Section II Part B",
        "pool": POOL,
        "pool_cn": POOL_CN,
        "sentences": sents,
        "questions": qs,
    }

    # 合并进 2026.json（幂等：先摘掉旧的同 id 篇目，再按考试顺序插入 text4 之后）
    arts = [a for a in d['articles'] if a['id'] != '2026_newtype']
    order = ['text1', 'text2', 'text3', 'text4', 'newtype', 'cloze', 'translation', 'writing_a', 'writing_b']
    arts.append(art)
    arts.sort(key=lambda a: order.index(a['type']) if a['type'] in order else 99)
    d['articles'] = arts
    io.open(fp, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=1))
    print('写入 %s：%d 篇（含 2026_newtype：%d 句 / %d 题 / %d 段）'
          % (fp, len(arts), len(sents), len(qs), len(para_sids)))

    # 同步 index.json 的 2026 年条目
    ifp = os.path.join(DATA, 'index.json')
    idx = json.load(io.open(ifp, encoding='utf-8'))
    for y in idx['years']:
        if y['year'] != 2026:
            continue
        y['articles'] = [a for a in y['articles'] if a['id'] != '2026_newtype']
        y['articles'].append({
            "id": "2026_newtype", "type": "newtype", "title": TITLE, "topic": TOPIC,
            "sentence_count": len(sents), "question_count": len(qs),
        })
        y['articles'].sort(key=lambda a: order.index(a['type']) if a['type'] in order else 99)
        print('index.json 2026 篇目:', [a['id'] for a in y['articles']])
    io.open(ifp, 'w', encoding='utf-8', newline='\n').write(json.dumps(idx, ensure_ascii=False, indent=1))
    print('index.json 已同步')


if __name__ == '__main__':
    main()
