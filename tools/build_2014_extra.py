# -*- coding: utf-8 -*-
"""为 2014 年试点构建完形/新题型/翻译/作文四模块数据，合并进 pwa/data/2014.json。

数据来源：
- 真题文本 tools/extracted/2014_exam.txt（英文原文/选项干净）
- 解析文本 tools/extracted/2014_notes.txt（官方译文/范文/答案）

用法：python -X utf8 tools/build_2014_extra.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'pwa' / 'data'
EXAM = ROOT / 'tools' / 'extracted' / '2014_exam.txt'
NOTES = ROOT / 'tools' / 'extracted' / '2014_notes.txt'

exam = EXAM.read_text(encoding='utf-8')
notes = NOTES.read_text(encoding='utf-8')


def split_paras(text):
    """按空行/段首缩进切句，返回段落列表（每段为若干句）。"""
    paras = [p for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras


# ---------- 完形填空 ----------
# 20 题标准答案（考研英语二 2014 Section I Use of English）
CLOZE_ANSWERS = list('BADDAABCBDACBDCDACDB')

# 20 题选项（真题文本顺序）：每行 'n. [X]word'
CLOZE_RAW = """1. denied, concluded, doubted, ensured
2. protective, dangerous, sufficient, troublesome
3. Instead, However, Likewise, Therefore
4. indicator, objective, origin, example
5. impact, relevance, assistance, concern
6. in terms of, in case of, in favor of, in respects of
7. measures, determines, equals, modifies
8. in essence, in contrast, in turn, in part
9. complicated, conservative, variable, straightforward
10. so, while, since, unless
11. shape, spirit, balance, taste
12. start, qualify, retire, stay
13. strange, changeable, normal, constant
14. option, reason, opportunity, tendency
15. employed, pictured, imitated, monitored
16. compared, combined, settled, associated
17. Even, Still, Yet, Only
18. despised, corrected, ignored, grounded
19. discussions, businesses, policies, studies
20. for, against, with, without""".split('\n')

# 完形正文：保留 [n] 占位，切成句子（按句号/问号分句，跨行合并）
CLOZE_BODY = """Thinner isn't always better. A number of studies have [1] that normal-weight people are in fact at higher risk of some diseases compared to those who are overweight. And there are health conditions for which being overweight is actually [2]. For example, heavier women are less likely to develop calcium deficiency than thin women. [3] among the elderly, being somewhat overweight is often an [4] of good health. Of even greater [5] is the fact that obesity turns out to be very difficult to define. It is often defined [6] body mass index, or BMI. BMI [7] body mass divided by the square of height. An adult with a BMI of 18 to 25 is often considered to be normal weight. Between 25 and 30 is overweight. And over 30 is considered obese. Obesity, [8], can be divided into moderately obese, severely obese, and very severely obese. While such numerical standards seem [9], they are not. Obesity is probably less a matter of weight than body fat. Some people with a high BMI are in fact extremely fit, [10] others with a low BMI may be in poor [11]. For example, many collegiate and professional football players [12] as obese, though their percentage body fat is low. Conversely, someone with a small frame may have high body fat but a [13] BMI. Today we have a(n) [14] to label obesity as a disgrace. The overweight are sometimes [15] in the media with their faces covered. Stereotypes [16] with obesity include laziness, lack of will power, and lower prospects for success. Teachers, employers, and health professionals have been shown to harbor biases against the obese. [17] very young children tend to look down on the overweight, and teasing about body build has long been a problem in schools. Negative attitudes toward obesity, [18] in health concerns, have stimulated a number of anti-obesity [19]. My own hospital system has banned sugary drinks from its facilities. Many employers have instituted weight loss and fitness initiatives. Michelle Obama has launched a high-visibility campaign [20] childhood obesity, even claiming that it represents our greatest national security threat."""

# 完形全文官方译文（解析整理，逐句）
CLOZE_CN = """瘦并不总是意味着更好。一些研究得出结论，与超重人群相比，体重正常的人其实患某些疾病的风险更高。并且在一些健康状况方面，超重实际上是保护性的。例如，与苗条的女性相比，较重的女性更不容易缺钙。该道理在老年人中同样适用，有几分超重往往是身体健康的标志。更令人关注的是，肥胖被证明是很难界定的。它通常依据身高体重指数（BMI）来定义。BMI 等于体重除以身高的平方。一个成年人的 BMI 介于 18 至 25 之间，往往被视作体重正常。BMI 介于 25 至 30 之间被认为是超重。BMI 为 30 以上被看作是肥胖。而肥胖也相应地可再分为中度肥胖、重度肥胖和极重度肥胖。虽然这样的数值标准看起来一目了然，但事实并非如此。肥胖也许更多地关乎体脂含量而非体重。一些 BMI 很高的人实际上体态极佳，而另一些 BMI 低的人可能外形欠佳。例如，许多大学和职业足球选手（按照 BMI 来衡量）可算作是肥胖者，可是他们的身体脂肪百分比却很低。反之，一些小身形的人可能身体脂肪含量很高但 BMI 却正常。如今，我们倾向于把肥胖看作一种耻辱。超重者有时在媒体上露面时面部被打上马赛克。与肥胖相关的刻板印象包括懒惰、缺乏意志力以及成功希望渺茫。教师、雇主和卫生专业人员都被证明对肥胖人群怀有偏见。甚至幼儿也往往看不起超重者，针对体型的嘲弄长期来一直是校园里的一大问题。对肥胖的负面态度植根于健康关切，已经催生了一系列反肥胖政策。我所在的医院系统已经禁止在其设施内销售含糖饮料。许多雇主已经实施了减肥和健身计划。米歇尔·奥巴马发起了一项针对儿童肥胖的高关注度运动，甚至声称这代表了美国最大的国家安全威胁。"""

# 完形逐句切分（把 CLOZE_CN 按 CLOZE_BODY 句数对齐）
def split_sentences(text):
    """按句末标点切句（保留标点）。"""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def split_cn_sentences(text):
    """中文按句号/问号/叹号切句。"""
    return [s.strip() for s in re.split(r'(?<=[。！？])', text) if s.strip()]

CLOZE_SENTS = split_sentences(CLOZE_BODY)
CLOZE_CN_SENTS = split_cn_sentences(CLOZE_CN)
print(f'完形正文 {len(CLOZE_SENTS)} 句 / 译文 {len(CLOZE_CN_SENTS)} 句')
if len(CLOZE_SENTS) != len(CLOZE_CN_SENTS):
    print('!! 完形句数与译文句数不一致，请人工核对')

# 完形选项解析
def parse_cloze_options(raw_lines):
    """'1. denied, concluded, doubted, ensured' -> {1: {A:denied, B:concluded, C:doubted, D:ensured}}"""
    out = {}
    for line in raw_lines:
        n, opts = line.split('. ', 1)
        words = [w.strip() for w in opts.split(',')]
        assert len(words) == 4, f'题 {n} 选项数不为4: {words}'
        out[int(n)] = dict(zip('ABCD', words))
    return out

CLOZE_OPTIONS = parse_cloze_options(CLOZE_RAW)
assert len(CLOZE_OPTIONS) == 20 and len(CLOZE_ANSWERS) == 20


# ---------- 从官方解析 notes.txt 提取完形/新题型精解 ----------
def extract_notes_explanations():
    """返回 ({题号: 精解文本}, {41-45: 精解文本})"""
    notes = NOTES.read_text(encoding='utf-8', errors='replace')
    cloze = {}
    for m in re.finditer(r'\n(\d{1,2})\.\s*\[[^\n]*', notes):
        n = int(m.group(1))
        if n < 1 or n > 20:
            continue
        nm = re.search(r'\n(\d{1,2})\.\s*\[', notes[m.start() + 10:])
        seg_end = m.start() + 10 + nm.start() if nm else len(notes)
        seg = notes[m.start():seg_end]
        jm = re.search(r'［试题精解(?:］|J)(.*?)(?=\n\n|\n\d{1,2}\.\s*\[|\Z)', seg, re.S)
        if jm:
            body = re.sub(r'\s+', ' ', jm.group(1)).strip()
            if body:
                cloze[n] = body
    newtype = {}
    for m in re.finditer(r'(\d{2})\.\s*［答案[^\n]*\n(?:［精解］|\[精解］)(.*?)(?=\d{2}\.\s*［答案|===== \[page|\Z)', notes, re.S):
        n = int(m.group(1))
        if 41 <= n <= 45:
            body = re.sub(r'\s+', ' ', m.group(2)).strip()
            body = re.sub(r'［干扰项设置］.*$', '', body).strip()   # 去掉干扰项分析，保持精解简洁
            if body:
                newtype[n] = body
    return cloze, newtype


CLOZE_EXPL, NEWTYPE_EXPL = extract_notes_explanations()
# 缺 5/15（PDF 中该两题精解格式特殊，人工补）
CLOZE_EXPL.setdefault(5, '本题考查上下文语义。空格所在部分为倒装句，正常语序应为 the fact is of even greater ...；the fact 后有 that 引导的同位语从句说明其内容：肥胖。此处表示"更令人关注的是，肥胖被证明是很难界定的"，故 impact 符合文意。')
CLOZE_EXPL.setdefault(15, '本题考查上下文语义与熟词僻义。上文指出人们倾向于将肥胖视作一件丢脸的事，因此超重的人有时在媒体拍摄中出现时脸部都会被遮住。picture 作动词有"拍摄"之意。')
# 45 答案行被 PDF 拆成 "1[5 ." 导致正则漏配，人工补
NEWTYPE_EXPL.setdefault(45, '根据题干 Seven Days 定位到第七段。该段第二句 Seven Days, consists of a single beautiful black-and-white photograph taken on an epic walk 表明《七天》是作者在一次跋涉中完成，[A] 选项 originates from a long walk 是原文 taken on an epic walk 的同义替换，故正确。')
print(f'完形精解 {len(CLOZE_EXPL)}/20，新题型精解 {len(NEWTYPE_EXPL)}/5')


def build_cloze():
    sentences = []
    for i, (en, cn) in enumerate(zip(CLOZE_SENTS, CLOZE_CN_SENTS), 1):
        sentences.append({
            'id': f'2014_cloze_s{i:02d}',
            'para': 1,
            'en': en,
            'cn': cn,
            'words': [],
        })
    questions = []
    for n in range(1, 21):
        letters = 'ABCD'
        questions.append({
            'id': f'2014_cloze_q{n:02d}',
            'number': n,
            'qtype': '完形',
            'stem': f'第 {n} 空：选择最合适的词填入空白 [{n}]',
            'stem_cn': '',
            'options': CLOZE_OPTIONS[n],
            'options_cn': {L: '' for L in letters},
            'answer': CLOZE_ANSWERS[n - 1],
            'explanation': CLOZE_EXPL.get(n, ''),
            'related_sentences': [f'2014_cloze_s{i:02d}' for i in range(1, len(CLOZE_SENTS) + 1)],
        })
    return {
        'id': '2014_cloze', 'type': 'cloze',
        'title': 'Thinner Isn\'t Always Better',
        'topic': '完形填空：研究表明肥胖并非总是有害，超重在诸多方面甚至具有保护作用。',
        'source': 'Section I Use of English',
        'sentences': sentences,
        'questions': questions,
    }


# ---------- 新题型 ----------
# 选项池（左栏 41-45 匹配右栏 A-G，两项多余）
NEWTYPE_POOL = {
    'A': 'originates from a long walk that the artist took.',
    'B': 'illustrates a kind of landscape-orientated light conceptual art.',
    'C': 'reminds people of the English landscape painting tradition.',
    'D': 'represents the elegance of the British land art.',
    'E': 'depicts the ordinary side of the British land art.',
    'F': 'embodies a romantic escape into the Scottish outdoors.',
    'G': 'contains images from different parts of the same photograph.',
}
NEWTYPE_POOL_CN = {
    'A': '源于艺术家的一次远足。',
    'B': '阐明了一种以风景为导向的光概念艺术。',
    'C': '使人们想起了英国风景绘画传统。',
    'D': '代表了英国地景艺术高雅的一面。',
    'E': '描绘了英国地景艺术日常生活的一面。',
    'F': '体现了向苏格兰户外生活的一种浪漫逃离。',
    'G': '包含同一张照片里不同的场景。',
}
# 匹配答案：41-45
NEWTYPE_ANSWERS = {
    41: 'D', 42: 'E', 43: 'G', 44: 'C', 45: 'F',
}
NEWTYPE_STEMS = {
    41: 'Stone Circle', 42: 'Olaf Street Study', 43: 'Across the Park',
    44: 'Towards Avebury', 45: 'Seven Days',
}
NEWTYPE_BODY = """Emerging in the late Sixties and reaching a peak in the Seventies, Land Art was one of a range of new forms, including Body Art, Performance Art, Action Art and Installation Art, which pushed art beyond the traditional confines of the studio and gallery. Rather than portraying landscape, land artists used the physical substance of the land itself as their medium. The British land art, typified by Richard Long's piece, was not only more domestically scaled, but a lot quirkier than its American counterpart. Indeed, while you might assume that an exhibition of Land Art would consist only of records of works rather than the works themselves, Long's photograph of his work is the work. Since his "action" is in the past, the photograph is its sole embodiment. That might seem rather an obscure point, but it sets the tone for an exhibition that contains a lot of black-and-white photographs and relatively few natural objects. Long is Britain's best-known Land Artist and his Stone Circle, a perfect ring of purplish rocks from Portishead beach laid out on the gallery floor, represents the elegant, rarefied side of the form. The Boyle Family, on the other hand, stand for its dirty, urban aspect. Comprising artists Mark Boyle and Joan Hills and their children, they recreated random sections of the British landscape on gallery walls. Their Olaf Street Study, a square of brick-strewn waste ground, is one of the few works here to embrace the commonplaceness that characterises most of our experience of the landscape most of the time. Parks feature, particularly in the earlier works, such as John Hilliard's very funny Across the Park, in which a long-haired stroller is variously smiled at by a pretty girl and unwittingly assaulted in a sequence of images that turn out to be different parts of the same photograph. Generally however British land artists preferred to get away from towns, gravitating towards landscapes that are traditionally considered beautiful such as the Lake District or the Wiltshire Downs. While it probably wasn't apparent at the time, much of this work is permeated by a spirit of romantic escapism that the likes of Wordsworth would have readily understood. Derek Jarman's yellow-tinted film Towards Avebury, a collection of long, mostly still shots of the Wiltshire landscape, evokes a tradition of English landscape painting stretching from Samuel Palmer to Paul Nash. In the case of Hamish Fulton, you can't help feeling that the Scottish artist has simply found a way of making his love of walking pay. A typical work, such as Seven Days, consists of a single beautiful black-and-white photograph taken on an epic walk, with the mileage and number of days taken listed beneath. British Land Art as shown in this well selected, but relatively modestly scaled exhibition wasn't about imposing on the landscape, more a kind of landscape-orientated light conceptual art created passing through. It had its origins in the great outdoors, but the results were as gallery-bound as the paintings of Turner and Constable."""
NEWTYPE_CN = """地景艺术出现于六十年代末期，在七十年代达到顶峰，是包括身体艺术、行为艺术、偶发艺术及装置艺术在内的一系列新艺术形式中的一种，这些艺术形式将艺术推向了工作室和画廊的传统界限之外。地景艺术家不描绘风景，而是以土地本身的物质作为媒介。英国的地景艺术，以理查德·朗的作品为代表，不仅在国内更具规模，而且比美国地景艺术更加古怪离奇。事实上，你或许认为一个地景艺术展览只包括作品的种种记录而非作品本身，但朗那些记录其工作的照片就是其作品。他的"行为"发生在过去，因而照片是这种行为的唯一体现。这一点可能显得相当晦涩，但它为这个包含大量黑白照片和相对较少自然物件的展览定下了基调。朗是英国最著名的地景艺术家，他的《石环》——一个用波蒂斯黑德海滩的紫色岩石完美铺就的圆环，铺展在画廊地板上——代表了这一艺术形式优雅而高深的一面。另一方面，博伊尔家族则代表了它粗砺、都市化的一面。由艺术家马克·博伊尔和琼·希尔斯及其子女组成的这个家族，在画廊墙壁上重现了英国风景的随机片段。他们的《奥拉夫街研究》——一块铺满砖块的废地——是这里少数拥抱平庸的作品之一，而这种平庸正是我们大多数时候对景观体验的典型特征。公园尤其出现在早期作品中，比如约翰·希利亚德那幅非常有趣的《漫步公园》，其中一位长发漫步者先后被一位漂亮女孩微笑、被无意间攻击，这一系列图像原来是同一张照片的不同部分。不过总的来说，英国地景艺术家更喜欢远离城镇，倾向于那些传统上被认为美丽的风景，如湖区或威尔特郡丘陵。虽然在当时可能并不明显，但这类作品大多弥漫着一种浪漫的逃避主义精神，华兹华斯之流会很容易理解。德里克·贾曼泛黄的影片《朝向埃夫伯里》——一组威尔特郡风景的长镜头、多为静态镜头——唤起了从塞缪尔·帕尔默到保罗·纳什的英国风景绘画传统。以哈米什·富尔顿为例，你忍不住会觉得这位苏格兰艺术家只是找到了一种让他的步行之爱有所回报的方式。像《七天》这样的典型作品由一张美丽的黑白照片组成，拍摄于一次史诗般的步行途中，照片下方列有里程数和所用天数。正如这个精挑细选但规模相对适度的展览所展示的，英国地景艺术并非凌驾于风景之上，而更像是一种以风景为导向的光概念艺术，在穿行中创作。它起源于广阔的户外，但结果却与特纳和康斯特布尔的画作一样被局限在画廊之中。"""


def build_newtype():
    sentences = []
    for i, (en, cn) in enumerate(zip(split_sentences(NEWTYPE_BODY), split_cn_sentences(NEWTYPE_CN)), 1):
        sentences.append({
            'id': f'2014_newtype_s{i:02d}',
            'para': 1,
            'en': en,
            'cn': cn,
            'words': [],
        })
    questions = []
    for n in range(41, 46):
        questions.append({
            'id': f'2014_newtype_q{n}',
            'number': n,
            'qtype': '匹配',
            'stem': f'{NEWTYPE_STEMS[n]}（从右栏选择与之匹配的表述）',
            'stem_cn': f'{NEWTYPE_STEMS[n]}',
            'options': {},
            'options_cn': {},
            'answer': NEWTYPE_ANSWERS[n],
            'explanation': NEWTYPE_EXPL.get(n, ''),
            'related_sentences': [f'2014_newtype_s{i:02d}' for i in range(1, len(sentences) + 1)],
        })
    return {
        'id': '2014_newtype', 'type': 'newtype',
        'title': 'Land Art (New Type)',
        'topic': '新题型（多项对应）：左栏作品与右栏表述匹配。',
        'source': 'Section II Part B',
        'pool': NEWTYPE_POOL,
        'pool_cn': NEWTYPE_POOL_CN,
        'sentences': sentences,
        'questions': questions,
    }


# ---------- 翻译 ----------
TRANSLATION_BODY = """Most people would define optimism as being endlessly happy, with a glass that's perpetually half full. But that's exactly the kind of false cheerfulness that positive psychologists wouldn't recommend. "Healthy optimism means being in touch with reality," says Tal Ben-Shahar, a Harvard professor. According to Ben-Shahar, realistic optimists are those who make the best of things that happen, but not those who believe everything happens for the best. Ben-Shahar uses three optimistic exercises. When he feels down - say, after giving a bad lecture - he grants himself permission to be human. He reminds himself that not every lecture can be a Nobel winner; some will be less effective than others. Next is reconstruction. He analyzes the weak lecture, learning lessons for the future about what works and what doesn't. Finally, there is perspective, which involves acknowledging that in the grand scheme of life, one lecture really doesn't matter."""
TRANSLATION_CN = """大多数人都会把乐观定义为永远快乐，觉得杯子里总有半杯水。但这恰恰不是真正的快乐，积极心理学家们并不提倡。哈佛大学教授 Tal Ben-Shahar 说："健康的乐观意味着不脱离现实。"按照 Ben-Shahar 的说法，现实的乐观主义者是那些不管发生什么事情都力求从中得到最大收获的人，而不是那些指望凡事都有最好结局的人。Ben-Shahar 运用三种方法保持乐观。当他情绪低落时——比如说一次课没讲好——他宽容自己，承认自己是凡人。他提醒自己，不是每堂课都有获诺贝尔奖的水准；总会有一些课的效果不如别的课。第二种方法是回顾。他分析讲得不好的课，为以后汲取有用的经验和失败的教训。最后，还有视角问题，要认识到在宏大的生命长卷里，一堂课真的不算什么。"""
TRANSLATION_REF = TRANSLATION_CN  # 官方参考译文


def build_translation():
    sentences = []
    for i, (en, cn) in enumerate(zip(split_sentences(TRANSLATION_BODY), split_cn_sentences(TRANSLATION_CN)), 1):
        sentences.append({
            'id': f'2014_translation_s{i:02d}',
            'para': 1,
            'en': en,
            'cn': cn,
            'words': [],
        })
    return {
        'id': '2014_translation', 'type': 'translation',
        'title': 'Optimism',
        'topic': '翻译：乐观的真正含义——保持乐观意味着与现实保持接触。',
        'source': 'Section III Translation',
        'ref_cn': TRANSLATION_REF,
        'sentences': sentences,
        'questions': [],
    }


# ---------- 作文 ----------
WRITING_A = {
    'id': '2014_writinga', 'type': 'writing_a',
    'title': 'Part A 应用文：介绍自己',
    'topic': '小作文：给未来室友写信，介绍生活习惯并征求建议。',
    'source': 'Section IV Writing Part A',
    'directions': """Suppose you are going to study abroad and share an apartment with John, a local student. Write him an email to
1) tell him about your living habits, and
2) ask for advice about living there.
You should write about 100 words on the ANSWER SHEET.
Do not use your own name. Use "Li Ming" instead.
Do not write your address. (10 points)""",
    'sample_en': """Dear John,
I am glad that it is you who will be my roommate during my overseas study and cannot wait to meet you. Before my moving in, I think it is necessary to arrive at a basic understanding about each other's living habits.
As a typical Chinese, I observe traditional living rules, sleeping and getting up early, having gorgeous breakfast, good lunch and humble supper and keeping room tidy and clean. In addition, I prefer cooking Chinese dishes at home and hope to get your tolerance for occasional spicy smell during dish preparation. There must also be some special living rules to be respected in your country. Can you explain them to me in advance? Hope to get your early reply.
Yours,
Li Ming""",
    'sample_cn': """亲爱的约翰：
很高兴你是我留学期间的室友，我迫不及待地想要见到你。在我搬进公寓前，我认为必须对各自的生活习惯有个基本了解。
作为一名典型的中国人，我遵循典型的中国生活方式，我会早睡早起，早餐吃好、中餐吃饱、晚餐吃少，并保持房间整洁干净。另外，我喜欢在家做中国菜，希望你能忍受做菜时偶尔会有的辣椒呛人的味道。在你们国家应该也有些需要尊重的生活规范。你能提前向我介绍吗？希望早日收到你的回信。
李明""",
    'questions': [],
}

WRITING_B = {
    'id': '2014_writingb', 'type': 'writing_b',
    'title': 'Part B 大作文：城市与乡村人口的变化',
    'topic': '大作文：根据图表写一篇约150词的短文，解读数据并发表评论。',
    'source': 'Section IV Writing Part B',
    'directions': """Write an essay based on the following chart. In your writing, you should
1) interpret the chart, and
2) give your comments.
You should write about 150 words on the ANSWER SHEET. (15 points)
[柱状图：1990/2000/2010 年城镇人口与乡村人口变化]""",
    'sample_en': """From 1990 to 2010 while moderate increase occurred in total population in China, population distribution experienced a dramatic shift. Urban population increased considerably from 300 million to 670 million; contrastingly rural population declined from 820 million to 680 million.
The population gap narrowed largely because of the joint effects of urbanization and unequal economic opportunities. The 20 years' urban sprawl caused millions of peasants to be passively transformed into city residents. Meanwhile, many more peasants initiatively chose to leave their hometown. In the 20 years, while urban living standards were largely improved, few economic opportunities fell on rural areas, making most peasants remain at the poverty line. Poverty prompted the call for change and healthy young peasants were driven to flock to cities to make a better living.
The increase in urban population is a sure indication of economic achievement. However, we should not ignore the inability of many urban newcomers to integrate into cities due to lack of education and civilized habits. They wandered around in the cities as urban paupers, isolated from cities' prosperity and convenience. In this sense, we cannot be superficially satisfied with the optimistic figure, but should endeavor to foster integration of newcomers.""",
    'sample_cn': """1990 年到 2010 年间，中国总人口温和上涨，但人口分布经历了巨大的变化。城市人口从 3 亿上涨到了 6.7 亿，上涨数量可观，与之相对的是农村人口从 8.2 亿下降到 6.8 亿。
（城乡）人口差距缩小主要由于城市化和不公平经济机会的联合作用。20 年的城市扩张导致了数百万农民被动地变为城市居民。同时，更多的农民主动选择离开家乡。20 年里，城市生活水平得到了大幅提高，但农村几乎没有获得经济机会，使大多数农民依然处于贫困中。穷则思变，健康、年轻的农民涌入城市，试图谋得更好的生活。
城市人口的增加无疑是经济成就的一个反映指标。但，我们不能忽视许多城市新居民由于缺乏教育和文明的生活习惯难以融入城市的现实。这些新来者作为城市贫民在城市中游荡，无法享用城市的繁荣和便利。鉴于此，我们不能肤浅地满足于乐观的数据，而应该努力促使新来者融入城市。""",
    'questions': [],
}

EXTRA = [build_cloze(), build_newtype(), build_translation(), WRITING_A, WRITING_B]


def main():
    year_path = DATA / '2014.json'
    data = json.loads(year_path.read_text(encoding='utf-8'))
    existing = {a['id'] for a in data['articles']}
    added = 0
    updated = 0
    for a in EXTRA:
        if a['id'] in existing:
            data['articles'] = [x for x in data['articles'] if x['id'] != a['id']]
            updated += 1
        data['articles'].append(a)
        added += 1
    data['articles'].sort(key=lambda x: x['id'])
    year_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'2014.json 新增 {added} 篇文章（覆盖 {updated} 篇），共 {len(data["articles"])} 篇')

    # index.json 同步
    idx_path = DATA / 'index.json'
    idx = json.loads(idx_path.read_text(encoding='utf-8'))
    for y in idx['years']:
        if y['year'] != 2014:
            continue
        extra_ids = {a['id'] for a in EXTRA}
        y['articles'] = [a for a in y['articles'] if a['id'] not in extra_ids]   # 先移除旧的，重建时同序
        for a in EXTRA:
            y['articles'].append({
                'id': a['id'], 'type': a['type'],
                'title': a['title'], 'topic': a['topic'],
                'sentence_count': len(a.get('sentences', [])),
                'question_count': len(a.get('questions', [])),
            })
        y['articles'].sort(key=lambda x: x['id'])
    idx_path.write_text(json.dumps(idx, ensure_ascii=False, indent=2), encoding='utf-8')
    print('index.json 同步完成')


if __name__ == '__main__':
    main()
