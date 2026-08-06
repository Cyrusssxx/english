# -*- coding: utf-8 -*-
"""为 2016 年构建完形/新题型/翻译/作文四模块数据，输出 tools/extracted/modules/2016_extra.json。

数据来源：
- 真题文本 tools/extracted/2016_exam.txt（英文原文/选项干净）
- 解析文本 tools/extracted/2016_notes.txt（官方译文/范文/答案）

用法：python -X utf8 tools/build_2016_extra.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'extracted' / 'modules' / '2016_extra.json'


# ---------- 完形填空 ----------
CLOZE_ANSWERS = list('BBACDBADCAACBDCDACDB')
assert len(CLOZE_ANSWERS) == 20, len(CLOZE_ANSWERS)

CLOZE_OPTIONS = {
    1: {'A': 'why', 'B': 'how', 'C': 'where', 'D': 'when'},
    2: {'A': 'In return', 'B': 'In particular', 'C': 'In contrast', 'D': 'In conclusion'},
    3: {'A': 'necessary', 'B': 'famous', 'C': 'perfect', 'D': 'sufficient'},
    4: {'A': 'individualism', 'B': 'realism', 'C': 'optimism', 'D': 'modernism'},
    5: {'A': 'miss', 'B': 'echo', 'C': 'spoil', 'D': 'change'},
    6: {'A': 'imagined', 'B': 'measured', 'C': 'assumed', 'D': 'invented'},
    7: {'A': 'Sure', 'B': 'Odd', 'C': 'Unfortunate', 'D': 'Often'},
    8: {'A': 'divided', 'B': 'advertised', 'C': 'overtaxed', 'D': 'headquartered'},
    9: {'A': 'summarize', 'B': 'overstate', 'C': 'explain', 'D': 'emphasize'},
    10: {'A': 'factors', 'B': 'stages', 'C': 'levels', 'D': 'methods'},
    11: {'A': 'desirable', 'B': 'sociable', 'C': 'reliable', 'D': 'reputable'},
    12: {'A': 'resumed', 'B': 'emerged', 'C': 'held', 'D': 'broke'},
    13: {'A': 'assign', 'B': 'attribute', 'C': 'transfer', 'D': 'compare'},
    14: {'A': 'serious', 'B': 'civilized', 'C': 'ambitious', 'D': 'experienced'},
    15: {'A': 'instead', 'B': 'thus', 'C': 'also', 'D': 'never'},
    16: {'A': 'rapidly', 'B': 'directly', 'C': 'regularly', 'D': 'equally'},
    17: {'A': 'While', 'B': 'Until', 'C': 'After', 'D': 'Since'},
    18: {'A': 'arrives', 'B': 'jumps', 'C': 'hints', 'D': 'strikes'},
    19: {'A': 'share', 'B': 'rediscover', 'C': 'simplify', 'D': 'shape'},
    20: {'A': 'pray for', 'B': 'lean towards', 'C': 'send out', 'D': 'give away'},
}

CLOZE_BODY = [
    "Happy people work differently.",
    "They're more productive, more creative, and willing to take greater risks.",
    "And new research suggests that happiness might influence [1] firms work, too.",
    "Companies located in places with happier people invest more, according to a recent research paper.",
    "[2], firms in happy places spend more on R&D (research and development).",
    "That's because happiness is linked to the kind of longer-term thinking [3] for making investments for the future.",
    "The researchers wanted to know if the [4] and inclination for risk-taking that come with happiness would [5] the way companies invested.",
    "So they compared U.S. cities' average happiness [6] by Gallup polling with the investment activity of publicly traded firms in those areas.",
    "[7] enough, firms' investment and R&D intensity were correlated with the happiness of the area in which they were [8].",
    "But is it really happiness that's linked to investment, or could something else about happier cities [9] why firms there spend more on R&D?",
    "To find out, the researchers controlled for various [10] that might make firms more likely to invest - like size, industry, and sales - and for indicators that a place was [11] to live in, like growth in wages or population.",
    "The link between happiness and investment generally [12] even after accounting for these things.",
    "The correlation between happiness and investment was particularly strong for younger firms, which the authors [13] to \"less codified decision making process\" and the possible presence of \"younger and less [14] managers who are more likely to be influenced by sentiment.\"",
    "The relationship was [15] stronger in places where happiness was spread more [16].",
    "Firms seem to invest more in places where most people are relatively happy, rather than in places with happiness inequality.",
    "[17] this doesn't prove that happiness causes firms to invest more or to take a longer-term view, the authors believe it at least [18] at that possibility.",
    "It's not hard to imagine that local culture and sentiment would help [19] how executives think about the future.",
    "\"It surely seems plausible that happy people would be more forward-thinking and creative and [20] R&D more than the average,\" said one researcher.",
]
CLOZE_CN = [
    "幸福的人工作方式有所不同。",
    "他们更高效，更有创造力，且愿意去冒更大风险。",
    "新的研究表明幸福感也可能影响公司如何运作。",
    "根据近期一篇研究论文，位于居民幸福感更强的地方的公司投资更多。",
    "尤其是在研发上投入更多。",
    "那是因为幸福感与对未来做投资所必需的那种长远思考相联系。",
    "研究者想要了解随幸福感而来的乐观和冒险倾向是否会改变公司的投资方式。",
    "于是，他们将由盖洛普民意测验调查得出的美国城市平均幸福指数与那些地区上市公司的投资活动进行了比较。",
    "果然，公司的投资和研发力度与其总部所在地的幸福指数相关。",
    "但与投资相联系的真的是幸福指数吗？或者说，和幸福指数较高城市相关的其他方面能否解释为何那里的公司在研发上投入更多？",
    "为了查明真相，研究者们控制了可能促使公司更愿意投资的多种因素——比如规模、产业和销售——以及一个地方适宜居住的指标，比如工资涨幅或人口增长。",
    "甚至在考虑了这些情况之后，幸福感和投资之间的关联依然普遍适用。",
    "幸福感和投资之间的关联在较年轻公司尤其明显，作者将其归因于\u201c不那么固守成规的决策过程\u201d以及（企业）可能存在\u201c较为年轻且经验较少的管理者，他们更容易受到情感的影响\u201d。",
    "这一关联在幸福感较为均等分布的地方也更加明显。",
    "公司似乎在大多数人都比较幸福的地区投资更多，而不是在幸福感不均等的地区。",
    "尽管这并不能证明幸福感致使公司增加投资或更有远见，作者相信它至少隐含了那种可能性。",
    "不难想象，地方文化和思想情感将有助于塑造管理者思考未来的方式。",
    "\u201c似乎可以确信的是，幸福的人更有远见，更加创新，并且比一般人更倾向于研发，\u201d一位研究者说道。",
]
assert len(CLOZE_BODY) == len(CLOZE_CN) == 18

CLOZE_EXPL = {
    1: '本题考查句内语义＋宾语从句引导词。由表并列关系的副词too以及people work/firms work可知①②句与①句并列，①②句指出幸福感对人工作方式产生影响（work differently指工作方式不同），使人更高效、创新，也更愿意冒险，因此可推知③句说明幸福感也影响公司运作方式。选项中只有[B]表示方式，为正确答案。空格后firms work为主谓结构的句子，因此空格处需填入一个连接词引导从句firms work做influence的宾语。四个备选项在语法上均能引导宾语从句，why, how, where, when分别表示原因、方式、地点和时间。但上下文内容并未涉及公司运作的原因和时间，因此[A]和[D]可轻松排除。由于下文第二段出现Companies located in places.../firms in happy places，考生很可能会误选[C]where，认为幸福感会影响公司的选址，但通过继续阅读第二段发现，该段意在说明\u201c一个地方的幸福指数影响公司的投资\u201d，这与公司运作相关，而与公司选址并无关系。',
    2: '本题考查上下文语义逻辑＋词义辨析。空格上文①句指出，位于幸福指数高的地方的公司投资更多；②句指出位于幸福地方的公司在研发上投入更多。通过一组对应词汇companies/firms、in places with happier people/in happy places、invest more/spend more on R&D可知②句具体说明①句，明示公司在哪一方面投资更多，由此推知，①②句语义上为递进关系，[B] In particular符合文义。[A]意为\u201c作为对某事物的回报／回应／交换\u201d，表示所涉双方间的互动关系，而①②句仅涉及一个事物\u201c幸福感较高的地方的公司\u201d（Companies和firms同指）的具体行为，并未存在互动的双方。[C]表示两事物或两部分论述内容间存在巨大差异和对比，与①②句的同向语义内容不符。[D]表示后文是对前文的总结或结束语，也与①②句间的关系不符。',
    3: '本题考查句内语义。空格所在句对前两句内容\u201c幸福指数高的地方的公司在研发上投资更多\u201d进行解释，指出幸福与长远思考相联系，而\u201c这种长远思考\u201d和\u201c对未来的投资\u201d存在某种关系。联系常识可知，对未来投资需要长远思考，后者是前者的必要条件，[A]符合文义，同时也能与介词for搭配。本题其他选项均能与介词for构成合理搭配，其中famous for意为\u201c以……而著名\u201d，显然\u201c长远思考因未来投资而著名\u201d逻辑不通；perfect for意为\u201c理想的、非常适合……\u201d，表明X是Y的理想条件，显然\u201c长远思考是未来投资的理想条件\u201d也逻辑不通；sufficient for意为\u201c充足的\u201d，表示充分条件，也就是说\u201c长远思考一定会带来未来投资\u201d，显然这不一定成立。',
    4: '本题考查句内语义。选项均根据同根-ism而设置，但根据定语从句that come with happiness可知（因为come为动词原形，因此可知该定语从句修饰and所连接的两个名词词组，而不是仅仅修饰inclination for risk-taking），幸福感所带来的应是某种心态，而并未上升至表示意识形态的\u201c主义\u201d，备选项中只有[C]含有\u201c乐观心态\u201d之意，为正确答案。干扰项[A]、[B]和[D]仿照正确项[C]的同根以及另一含义\u201c乐观主义\u201d设置，意图利用常识\u201c公司投资会受到个人／现实／现代环境的影响\u201d来干扰考生判断，但该三项完全偏离本文关键词happiness，与\u201c幸福感\u201d并无直接关联。',
    5: '本题考查上下文语义。本文首段提出全文论点\u201c幸福感可能影响公司如何运作\u201d（happiness might influence how firms work），因此本句研究者的研究目的（The researchers wanted to know）自然也是想要找出随幸福感而来的乐观和冒险倾向是否会影响到公司的投资方式（the way companies invested），[D]\u201c使发生变化、改变\u201d符合文义。[A]和[C]利用第二段末句longer-term thinking设置干扰，欲使考生误认为\u201c长时间思考投资可能会错过或损失投资机会\u201d，但[A]与the way companies invested搭配不当，即\u201c错过公司的投资方式\u201d语义不通，[C]则过度推断，上文仅提到幸福感会影响公司投资，但并未说明这种影响是好是坏。[B]本意为\u201c发出回声、回响\u201d，含比喻义\u201c……是……的回应或反映\u201d，借come with happiness设置干扰，欲误导考生认为\u201c幸福感是公司投资方式的反映／回应\u201d，而根据文义，公司的投资方式应是幸福感的反映。',
    6: '本题考查句内语义＋词义辨析。浏览发现备选项均为动词过去分词，与by搭配一般表被动，也即U.S. cities\' average happiness和Gallup polling为受事—施事关系。由常识可知，城市的平均幸福指数一般经由民意测验调查得出，[B]符合文义。其他三个选项在用法上都能与by搭配表示被动含义，但盖洛普民意测验是美国调查机构发起的一项调查，其所调查得出的城市平均幸福指数显然不可能是经由想象／假设／虚构而得出。',
    7: '本题考查上下文语义＋逻辑衔接。空格后介绍研究发现，指出一个地区的幸福指数与公司投资正相关，是对第三段①句研究目的\u201c想要了解幸福感是否影响公司投资\u201d的肯定验证，是意料之中的结果，备选项中[A]与enough搭配，意为\u201c果真、果然\u201d，符合文义。干扰项均能与enough搭配使用，但[B]和[C]暗含语义转折，与第三、四段间\u201c介绍研究目的和方法→肯定研究发现\u201d的顺承关系不符。[D]表示频率，often enough意为\u201c非常频繁的、经常性的\u201d，暗示研究发现\u201c幸福感和公司投资正相关\u201d还有特殊情况存在，而实际上两者关系普遍存在，本文并未提及任何特殊情况。',
    8: '本题考查上下文语义。空格所在句重申本文论点\u201c果然，公司投资与研发力度与公司总部所在地区的幸福指数相关\u201d，文中they回指firms，in which they were ___做后置定语修饰area，也即公司在这些地区有某种行为。结合第二段内容Companies located in places with happier people invest more/firms in happy places spend more on R&D可知公司所在地区的幸福指数影响公司投资，推知本句中the area即是公司的所在地，[D]（设立总部于）符合文义。另外根据常识可知，公司总部对公司未来投资决策起决定性作用，在此能起到强化地区幸福指数与公司投资之间关系的作用。若考生误认为they回指的是area，可能会误选[A]认为\u201c土地被分割／划分\u201d，但实际上they回指firms；[A]还可能被理解为\u201c公司被划分成多个分公司或分支\u201d，也即公司设立分支的地区的幸福指数影响公司投资，这与常识\u201c公司总部决定公司未来投资决策\u201d存在出入。[B]和[C]均根据公司可能的行为\u201c在某地做广告宣传自己\u201d和可能遇到的情况\u201c公司在某地被过度征税\u201d设置干扰，但是\u201c公司被广告宣传的地方\u201d和\u201c公司被过度征税的地方\u201d与\u201c公司所在地\u201d未必同指，且与全文论点\u201c地区幸福感影响公司投资\u201d并无直接关系。',
    9: '本题考查上下文语义。②句中could something else about happier cities ___ why对研究方法中的干扰因素提出疑问，③④句给出回答，由此推知为增加研究发现的严密性和科学性，②句在①句研究发现的基础上进一步分析（除幸福指数外，）其他因素对公司投资的影响，也即something else...与why firms there spend more on R&D为因果解释关系，[C]符合文义。[A]表示对已经确定的东西进行总结，[B]表示对已经存在的事实进行夸张描述，[D]表示对已知情况进行强化凸显，这三项均与②句分析干扰因素对研究的影响的写作目的不符。',
    10: '本题考查句内语义。空格所填词是various ___ that might make firms more likely to invest的中心词，破折号后like size, industry, and sales对其举例说明，可以推知，这些都是促使公司更可能投资的影响因素，[A]符合文义。[B]和[C]与that从句构成\u201c促使企业投资的阶段／水平\u201d，明显搭配不当；[D]虽能与that从句搭配\u201c促使企业投资的方法\u201d，但后文举例size, industry, and sales明显不属于\u201c投资方法\u201d。',
    11: '本题考查上下文语义＋词义辨析。空格词修饰a place，用以说明在某地居住的特点。再由like growth in wages or population可知，工资涨幅和人口增长指标是该地这一特点的例证说明。联系第二段②句U.S. cities\' average happiness、本段①句happiness of the area、②句happier cities可知，该地特点和\u201c幸福指数\u201d息息相关，[A]符合文义，a place was desirable to live in指\u201c某地宜居\u201d。空格所填词修饰a place，而[B]只能用以修饰人，说明人善于社交的特点；[C]一般用于说明人或事物很可靠，但不能用来修饰地方，即\u201c在某地居住很可靠\u201d搭配不当。[D]能够用来修饰地方，但后文举例growth in wages or population并非是一个地方声誉好坏的体现，同时地方声誉好并不一定与居民幸福指数挂钩。',
    12: '本题考查句内语义＋词义辨析。空格所在句总结研究结论指出，幸福指数和投资之间的关系普遍……，其他因素的影响不大（these things指代③句中various factors that... and for indicators that...）。由even的让步转折语气可知，即使在考虑了幸福城市的其他因素后，幸福感和投资之间的关系依然普遍成立／适用／有效。[C]符合文义。hold这里为熟词僻意，意为to continue to be true, good, available\u201c继续适用或有效\u201d，generally hold为固定搭配，意为\u201c普遍适用\u201d。[A]意为\u201c重新开始、继续\u201d，表示某事中断之后继续；[B]表示\u201c（新事物）出现、显现\u201d；而由generally（普遍地）和even的让步转折语气可知，幸福感和公司投资之间的关系一直存在，并未出现中断、也并不是在考虑其他因素后初次显现。[D]反向干扰，表明\u201c幸福感和投资之间的关系在考虑其他因素后就不成立了\u201d，这显然与even的让步转折语气以及全文一直重申的观点相悖。',
    13: '本题考查句内逻辑。空格所在句中，which之前重申研究结论\u201c幸福感和投资的关系在较年轻公司里尤其明显\u201d，which之后以and连接的两个名词短语\u201cless codified decision making process\u201d（决策过程不那么固守成规）和the possible presence of\u201cyounger and less ___ managers who...\u201d（管理者年轻、易受情感影响）说明年轻公司的特点，这一特点能够解释为何幸福感和投资的关系在年轻公司里尤其明显，也即which前后为果因关系，[B] attribute与to搭配表原因，为正确答案。干扰项均能与to构成合理搭配，但[A]多用于assign sb to (do) sth/assign sth to sb，意为\u201c把（任务）指派／分配给某人\u201d，与文中\u201c决策过程\u201d不能搭配；[C]一般用于transfer (from sth) to sth，表示事物在地点上的变化，显然不符合文义；[D]表示句子主干所描述的现象与which从句所说明的年轻公司特点是比较关系，但两者并不存在可比性。',
    14: '本题考查句内语义。空格词与younger及who...从句共同修饰managers，说明年轻公司管理者的特点\u201c年轻、缺少／不怎么……、易受情感影响\u201d。所填词之前有less限定，说明年轻管理者缺少某种特质，且这种特质影响公司投资，浏览选项发现，[D]（有经验的）与公司投资有直接关系，且less experienced符合年轻管理者的特点，为正确答案。干扰项均是能表示人的特点的形容词，[A]、[B]与less连用，即\u201c不太严肃认真／没有教养\u201d，可能是年轻人的特点，但两者和公司投资并无直接显性关系；[C]反向干扰，因为年轻人一般胸怀野心，而非野心更小（less ambitious）。',
    15: '本题考查上下文逻辑。空格所在的②句中，The relationship回指①句The correlation between happiness and investment，表地点的places where...对应①句younger firms，表明论述对象由\u201c年轻公司\u201d转换到\u201c某一地区\u201d，stronger与①句particularly strong近义，结合③句Firms seem to invest more in places where...可推知，②③句与①句语义同向并列，②句意在说明幸福感和投资的关系在某一地区也更加明显，[C]符合文义。[A]表明反义关系，与①②句的同向论述关系不符；[B]表因果顺承关系，干扰性较强，但①②句的论述对象younger firms（年轻公司）、places where...（……的地方）并无联系；[D]表否定，即\u201c这种关系在……地方并不更明显\u201d，与③句\u201c公司在这些地方似乎投资更多\u201d相悖。',
    16: '本题考查上下文语义。②句指出，幸福感和投资的关系在幸福感较为___分布的地方也很明显，③句进一步解释，公司在大多数人都比较幸福的地方投资更多，在幸福感不均等的地方投资不多。综合可知，places where happiness was spread more ___与③句中where most people are relatively happy同义，与places with happiness inequality反义。[D]与inequality同源反义，故正确。干扰项[A]、[B]、[C]在语法上均能与spread搭配，但与本题解题关键where most people are relatively happy/places with happiness inequality（③句）无关，不能体现②③句间的解释说明关系。',
    17: '本题考查句内逻辑。空格所在句指出，这（this指代上述研究结论）不能证明幸福感致使公司增加投资或更有远见（cause意为\u201c导致、引发\u201d，强调幸福感和投资之间存在明显直接的因果关系），作者相信它（it回指this，同指研究结论）至少……，at least表明作者在承认前述研究局限性的情况下，对研究最基本的价值予以肯定，以体现论述的严密性和严谨性。也就是说，本句两个分句之间为让步转折关系，即\u201c尽管……，但作者还是相信它至少……\u201d，[A]符合文义。[B]和[C]一般引导时间状语从句，而空格后的句子与时间无关。[D]表原因，与at least所体现的让步转折关系不符。',
    18: '本题考查词语搭配＋词义辨析。空格所在句指出，尽管上述研究不能证明幸福感致使公司增加投资，但作者相信它至少——这种可能性，由cause的含义to make sth happen可知，作者意欲先让步指出上述研究不能证明幸福感和投资存在直接显性的因果关系，之后转折指出它至少隐含了这种可能性。[C]\u201c暗示、示意\u201d符合文义。空格词应能与at搭配做谓语，其宾语为that possibility。[A]与at搭配意为\u201c达成（协议／结论）\u201d，表示已经达到或实现了那种可能性，这显然与前文内容相悖；[B]与at搭配意为\u201c匆忙做出（结论）\u201d，但其宾语that possibility显然不是结论；[D]原意为\u201c打／击／撞／碰\u201d，与at搭配意为\u201c朝……打去；伤害、危害\u201d，与本句让步转折关系不利。',
    19: '本题考查上下文语义。②句指出，地方文化和情感有助于___管理者对未来的思考。综合全文，通篇都在论述某地的幸福指数影响该地区公司的投资，具体来说即，地方文化和人文情怀等地域因素潜移默化地影响管理者对未来投资的思考，且这种影响可能已经内化成为管理者思维的一部分，[D]\u201c塑造\u201d能体现这种由内而外的影响过程，为正确答案。全文围绕主题\u201c幸福感影响公司投资\u201d展开，本句是对这一主题的重申和深层解释。干扰项[A]、[B]、[C]虽在语法上能与how...从句搭配，但在语义上，\u201c分享／重新发现／简化管理者思考未来的方式\u201d均未触及地区文化与管理者思考方式的深层联系，不足以影响公司的投资。',
    20: '本题考查句内语义。空格词说明幸福的人对研发的态度。综合第一段①句\u201c幸福的人更创新、更愿意冒险\u201d，第二段②句\u201c位于幸福指数高的地区的公司在研发上投入更多\u201d，第四段①句\u201c公司投资和研发力度与公司总部所在地的幸福指数相关\u201d，可以推知，幸福的人更愿意在研发上投入，即他们更倾向于／偏向于研发。[B]符合文义。lean to/towards sth意为\u201c倾向／偏向于某事物\u201d。[A]一般用于向上帝祈祷以达成某种愿望，如pray for peace\u201c祈求和平\u201d，或表示非常希望某事发生，如pray for good weather on Saturday\u201c企盼星期六是个好天气\u201d，但将其代入原文，即\u201c幸福的人祈求或企盼研发\u201d带有强烈主观色彩，语义过重，与本文客观介绍研究发现不符。[C]意为\u201c发送某物或派遣某人\u201d，[D]意为\u201c分发、泄露\u201d等，均和R&D搭配不当。',
}


def build_cloze():
    sentences = []
    for i, (en, cn) in enumerate(zip(CLOZE_BODY, CLOZE_CN), 1):
        sentences.append({
            'id': f'2016_cloze_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(1, 21):
        questions.append({
            'id': f'2016_cloze_q{n:02d}', 'number': n, 'qtype': '完形',
            'stem': f'第 {n} 空：选择最合适的词填入空白 [{n}]', 'stem_cn': '',
            'options': CLOZE_OPTIONS[n],
            'options_cn': {L: '' for L in 'ABCD'},
            'answer': CLOZE_ANSWERS[n - 1],
            'explanation': CLOZE_EXPL[n],
            'related_sentences': [f'2016_cloze_s{i:02d}' for i in range(1, len(CLOZE_BODY) + 1)],
        })
    return {
        'id': '2016_cloze', 'type': 'cloze',
        'title': 'Companies in Happy Cities Invest More for the Long Term',
        'topic': '完形填空：幸福感影响公司投资——幸福指数高的城市，公司更注重长远投资。',
        'source': 'Section I Use of English',
        'sentences': sentences, 'questions': questions,
    }


# ---------- 新题型（小标题对应） ----------
NEWTYPE_POOL = {
    'A': 'Be silly',
    'B': 'Have fun',
    'C': 'Ask for help',
    'D': 'Express your emotions',
    'E': "Don't overthink it",
    'F': 'Be easily pleased',
    'G': 'Notice things',
}
NEWTYPE_POOL_CN = {
    'A': '傻点儿',
    'B': '玩得开心',
    'C': '寻求帮助',
    'D': '表达情绪',
    'E': '别想太多',
    'F': '容易满足',
    'G': '留意事物',
}
NEWTYPE_ANSWERS = {41: 'D', 42: 'F', 43: 'A', 44: 'B', 45: 'E'}
NEWTYPE_EXPL = {
    41: '第二段首六句先介绍孩子的情绪反应：喜怒哀乐非常直白（sad→cries，angry→shouts，Scared→both）。随后⑦至⑨句介绍成年人控制／抑制情绪，且说明这有害健康（suppressing emotions... can even make us ill）。⑩句顺而提出建议：要像孩子一样承认并表达情绪（acknowledge and express what we feel appropriately）。[D] Express your emotions紧扣段落中心emotions，故正确。',
    42: '第三段前三句对比说明\u201c孩子们容易对小事感到幸福（一件不到五镑的T恤便令继女极为高兴），而成年人认为只有大事（新工作、大房子、好车）才能带来幸福，实则这些东西对幸福水平影响甚微\u201d，④句作者给出对成年人的建议\u201c对小事情充满感激可以提升幸福\u201d（being grateful for small things every day is a much better way to improve wellbeing）。[F] Be easily pleased（容易满足）正确。',
    43: '第四段首两句作者由孩子们爱笑，指出成年人应该也保留一些傻气和傻笑（indulge in a bit of silliness and giggling），并说明这样有益健康（reduce stress hormones, increase good hormones, improve blood flow, fight off infection）。末句指出这会提升幸福水平。[A] Be silly正确。[干扰项设置][G]容易因该段首句出现\u201cnoticed how much...\u201d而误选。实际上该句不是作者建议的内容，句意重点也不在notice之上。',
    44: '第五段先以\u201c让步—转折\u201d指出成年人虽要应付诸多事情（work, mortgage payments, figuring out what to cook），但也可以控制好工作日程，安排时间享受、放松（schedule in time to enjoy the things we love），然后说明成年人可以如何放松玩乐（social, sporting, creative or completely random）。[B] Have fun正确。[干扰项设置][C]可能因为该段首句所述\u201c成年人要应付太多事情\u201d而主观臆测出\u201c成年人需要寻求帮助\u201d，实际上该段后文强调要\u201c适时玩乐\u201d，并未提及要\u201c寻求帮助\u201d。',
    45: '第六段首句即亮明建议：不应该过分追求／顾念幸福（shouldn\'t try too hard to be happy）。随后引用科学发现（backfire and actually have a negative impact on our wellbeing）和庄子名言（Happiness is the absence of striving for happiness）解释原因：以幸福为念反而可能会适得其反；幸福不是目标，而是顺其自然的收获（happiness is not a goal but a natural byproduct of the way they live）。[E] Don\'t overthink it正确。',
}
NEWTYPE_BODY = [
    "As adults, it seems that we are constantly pursuing happiness, often with mixed results.",
    "Yet children appear to have it down to an art - and for the most part they don't need self-help books or therapy.",
    "Instead, they look after their wellbeing instinctively, and usually more effectively than we do as grownups.",
    "Perhaps it's time to learn a few lessons from them.",
    "What does a child do when he's sad?",
    "He cries.",
    "When he's angry?",
    "He shouts.",
    "Scared?",
    "Probably a bit of both.",
    "As we grow up, we learn to control our emotions so they are manageable and don't dictate our behaviours, which is in many ways a good thing.",
    "But too often we take this process too far and end up suppressing emotions, especially negative ones.",
    "That's about as effective as brushing dirt under a carpet and can even make us ill.",
    "What we need to do is find a way to acknowledge and express what we feel appropriately, and then - again, like children - move on.",
    "A couple of Christmases ago, my youngest stepdaughter, who was nine years old at the time, got a Superman T-shirt for Christmas.",
    "It cost less than a fiver but she was overjoyed, and couldn't stop talking about it.",
    "Too often we believe that a new job, bigger house or better car will be the magic silver bullet that will allow us to finally be content, but the reality is these things have very little lasting impact on our happiness levels.",
    "Instead, being grateful for small things every day is a much better way to improve wellbeing.",
    "Have you ever noticed how much children laugh?",
    "If we adults could indulge in a bit of silliness and giggling, we would reduce the stress hormones in our bodies, increase good hormones like endorphins, improve blood flow to our hearts and even have a greater chance of fighting off infection.",
    "All of which would, of course, have a positive effect on our happiness levels.",
    "The problem with being a grownup is that there's an awful lot of serious stuff to deal with - work, mortgage payments, figuring out what to cook for dinner.",
    "But as adults we also have the luxury of being able to control our own diaries and it's important that we schedule in time to enjoy the things we love.",
    "Those things might be social, sporting, creative or completely random (dancing around the living room, anyone?) - it doesn't matter, so long as they're enjoyable, and not likely to have negative side effects, such as drinking too much alcohol or going on a wild spending spree if you're on a tight budget.",
    "Having said all of the above, it's important to add that we shouldn't try too hard to be happy.",
    "Scientists tell us this can backfire and actually have a negative impact on our wellbeing.",
    "As the Chinese philosopher Chuang Tzu is reported to have said: \"Happiness is the absence of striving for happiness.\"",
    "And in that, once more, we need to look to the example of our children, to whom happiness is not a goal but a natural byproduct of the way they live.",
]
NEWTYPE_CN = [
    "作为成年人，似乎我们在不断追寻幸福，结局却往往不一。",
    "而孩子们似乎对此驾轻就熟——并且在很大程度上，他们不需要自助书籍或治疗。",
    "相反，他们本能地守住自己的幸福，且通常比我们成年人做起来更有成效。",
    "也许是时候向他们学习一些经验了。",
    "当一个孩子伤心时他会做什么呢？",
    "他会大哭。",
    "当他生气时呢？",
    "他会大叫。",
    "害怕时呢？",
    "大概两者都有那么一点。",
    "在成长过程中，我们会学着控制情绪，为的是使其易于控制而不会支配我们的行为，这在许多方面是好事情。",
    "但我们常常会将这一步做得太过，并最终压抑情绪，尤其是负面情绪。",
    "这样做的影响大致等同于将灰尘扫到地毯下，甚至会让我们患病。",
    "我们需要做的就是找到一种方式承认并适当地表达我们的感觉，然后——再次像孩子一样——继续前行。",
    "几年前的圣诞节，我最小的继女，那时九岁，得到了一件超人T恤作为圣诞礼物。",
    "这件T恤只花了不到五镑但却令她极为高兴，她简直不能停止谈论它。",
    "我们常常认为一份新工作，一套更大的房子或一辆更好的车会是让我们最终得以满足的神奇良方，但真实情况是这些东西对我们的幸福水平产生的持久影响微乎其微。",
    "相反，每天因小事情充满感激是提升幸福的更优方式。",
    "你曾注意过孩子们是多么爱笑吗？",
    "如果我们成年人能够纵情于一点傻气和傻笑，那么我们将会减少体内的压力激素，增加有益激素如内啡肽，提高心脏血流量，甚至提升防御传染病的可能。",
    "所有这一切当然会对我们的幸福水平具有积极的影响。",
    "作为成年人面对的问题是有太多严肃的事情需要处理——工作，按揭付款，计划晚餐该做什么。",
    "但作为成年人，我们也可以拥有\u201c把控自己工作日程\u201d这样的奢侈机会，而且\u201c适时安排以享受我们喜欢的事情\u201d是非常重要的。",
    "那些事情可以是有关社交的，运动的，创意的或完全随机的（在客厅翩翩起舞，有人做过吗？）——这没关系，只要它们令人愉快，且不大可能有负面影响，如饮酒过度或在预算紧张的情况下疯狂挥霍。",
    "上面说了这么多，有必要补充说明的是，我们不应该过分追逐幸福。",
    "科学家告诉我们这可能适得其反，并且实际上对我们的幸福有负面影响。",
    "正如中国哲学家庄子曾言：\u201c无为诚乐。\u201d",
    "在这一点上，我们需再次以孩子们为榜样，对他们来说，幸福不是目标而是其生活方式的自然额外收获。",
]
assert len(NEWTYPE_BODY) == len(NEWTYPE_CN) == 28


def build_newtype():
    sentences = []
    for i, (en, cn) in enumerate(zip(NEWTYPE_BODY, NEWTYPE_CN), 1):
        sentences.append({
            'id': f'2016_newtype_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(41, 46):
        questions.append({
            'id': f'2016_newtype_q{n}', 'number': n, 'qtype': '小标题',
            'stem': f'第 {n} 段：选择最合适的小标题填入空白', 'stem_cn': '',
            'options': {}, 'options_cn': {},
            'answer': NEWTYPE_ANSWERS[n],
            'explanation': NEWTYPE_EXPL[n],
            'related_sentences': [f'2016_newtype_s{i:02d}' for i in range(1, len(NEWTYPE_BODY) + 1)],
        })
    return {
        'id': '2016_newtype', 'type': 'newtype',
        'title': 'Act Your Shoe Size, Not Your Age',
        'topic': '新题型（小标题对应）：成年人应向孩子学习如何获取幸福。',
        'source': 'Section II Part B',
        'pool': NEWTYPE_POOL, 'pool_cn': NEWTYPE_POOL_CN,
        'sentences': sentences, 'questions': questions,
    }


# ---------- 翻译 ----------
TRANSLATION_BODY = [
    "The supermarket is designed to lure customers into spending as much time as possible within its doors.",
    "The reason for this is simple: The longer you stay in the store, the more stuff you'll see, and the more stuff you see, the more you'll buy.",
    "And supermarkets contain a lot of stuff.",
    "The average supermarket, according to the Food Marketing Institute, carries some 44,000 different items, and many carry tens of thousands more.",
    "The sheer volume of available choice is enough to send shoppers into a state of information overload.",
    "According to brain-scan experiments, the demands of so much decision-making quickly become too much for us.",
    "After about 40 minutes of shopping, most people stop struggling to be rationally selective, and instead begin shopping emotionally - which is the point at which we accumulate the 50 percent of stuff in our cart that we never intended buying.",
]
TRANSLATION_CN = [
    "超市的设计就是要诱使顾客尽可能久地待在店内。",
    "其理由很简单：你在店里逗留越久，看到的东西就越多，看到的东西越多，买的就越多。",
    "而超市里的东西多得很。",
    "按食品营销研究院所说，普通超市售卖约44,000种各式货品，而且许多超市的货品还要多出成千上万种。",
    "单是可供选择的货品数量就足以让购物者陷入信息超负荷的状态。",
    "根据大脑扫描实验，如此之大的决策量带来的负担会很快令我们无法承受。",
    "购物约40分钟后，大多数人就不再费心去理性选购，而是开始冲动购物了——就是从这一刻起，我们把本来根本没打算买的那一半东西堆进了购物车。",
]
TRANSLATION_REF = '超市的设计就是要诱使顾客尽可能久地待在店内。其理由很简单：你在店里逗留越久，看到的东西就越多，看到的东西越多，买的就越多。而超市里的东西多得很。按食品营销研究院所说，普通超市售卖约44,000种各式货品，而且许多超市的货品还要多出成千上万种。单是可供选择的货品数量就足以让购物者陷入信息超负荷的状态。根据大脑扫描实验，如此之大的决策量带来的负担会很快令我们无法承受。购物约40分钟后，大多数人就不再费心去理性选购，而是开始冲动购物了——就是从这一刻起，我们把本来根本没打算买的那一半东西堆进了购物车。'
assert len(TRANSLATION_BODY) == len(TRANSLATION_CN) == 7


def build_translation():
    sentences = []
    for i, (en, cn) in enumerate(zip(TRANSLATION_BODY, TRANSLATION_CN), 1):
        sentences.append({
            'id': f'2016_translation_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    return {
        'id': '2016_translation', 'type': 'translation',
        'title': 'Surviving the Sneaky Psychology of Supermarkets',
        'topic': '翻译：超市心理学——诱使顾客久留与冲动购物的设计奥秘。',
        'source': 'Section III Translation',
        'ref_cn': TRANSLATION_REF,
        'sentences': sentences, 'questions': [],
    }


# ---------- 作文 ----------
WRITING_A = {
    'id': '2016_writinga', 'type': 'writing_a',
    'title': 'Part A 应用文：建议信（翻译学习）',
    'topic': '小作文：回复朋友邮件，感谢其祝贺，并就如何提高翻译水平提出建议。',
    'source': 'Section IV Writing Part A',
    'sample_en': """Dear Jack,
I'm writing to express my gratitude for your congratulation on my success in the translation contest. Since you asked for my advice, I'd like to share with you some of my thoughts on how to improve translation skills.
To begin with, it is vital that you appreciate the beauty of language and hone your reading skills. Besides, a good translator usually reads extensively and constantly exposes himself to quality reading materials. One should cultivate a broad knowledge base and keep abreast of current events and issues. Moreover, be persistent. Language learning is not a task that can be accomplished within a short time. Only with a lot of sustained efforts can we improve our translation skills.
I wish you find these suggestions useful and I'm more than willing to discuss it with you about further details. I'm looking forward to your reply.
Yours sincerely,
Li Ming""",
    'sample_cn': """杰克：
我写这封信以表达对你此前恭贺我在翻译比赛中获胜的感谢。另外，因为你咨询我的建议，在此我想就如何提高翻译水平和你分享一些我的看法。
首先，你要欣赏语言之美，并打磨自己的阅读技能，这一点很重要。其次，一位好的译者通常博览群书，而且不断地让自己接触高质量的阅读材料。应当打下广泛的知识基础，同时与时俱进，跟上时事的步伐。此外，还要做到持之以恒。语言学习不是在短时间内就能完成的一项任务。只有持续的、极大的努力才能让我们提高翻译水平。
我希望你觉得这些建议有用。我非常乐意和你进一步探讨这个话题。期待你的回复。
诚挚的，
李明""",
    'questions': [],
}

WRITING_B = {
    'id': '2016_writingb', 'type': 'writing_b',
    'title': 'Part B 大作文：高校学生旅游目的调查',
    'topic': '大作文：根据饼图写一篇约150词的短文，解读高校学生旅游目的并发表评论。',
    'source': 'Section IV Writing Part B',
    'chart_img': 'img/2016_writingb_chart.png',
    'sample_en': """This pie chart, simple yet illuminating, illustrates the purposes of travel for students polled in a certain university. As is reflected by the chart, 37 percent of college students travel to appreciate the beauty of the scenery; next comes the aim of relieving pressure, accounting for 33 percent. Students' other objectives - making more friends, fostering greater independence, and other aims respectively account for 9%, 6% and 15%.
The survey reveals that most students go on a journey to enjoy the view as well as to unwind and recharge. On the one hand, with the prosperity of tourism, college students who have ample time, curiosity and energy to explore their individuality and see the outside world are lured to go out of campus and come into contact with grandeur and beauty. On the other hand, college students have their share of pressure coming from academic study, employment and interpersonal relationship, to which travelling is a wonderful antidote. One usually comes back from a trip feeling refreshed and revitalized.
In my opinion, though it's natural for college students to seek fun and enjoyment, they should attach deeper meaning to travelling. In the journey one can try to interact with local people and experience their culture in-depth, make friends with people from different cultural backgrounds and feel a sense of independence and self-reliance from the bottom of heart. Travelling truly could benefit a lot.""",
    'sample_cn': """这张简单却具启发性的饼状图图解了某大学被调查的学生旅行的目的。正如图表反映的，37%的大学生旅行是为了欣赏景色的美好；仅次之的是为了缓解压力，占了33%。学生的其他目的——结交更多朋友，培养独立能力以及其他分别占9%，6%和15%。
该项调查显示，大多数学生去旅行的目的都是欣赏美景以及放松休息一下。一方面，随着旅游业的繁荣，有着足够时间、好奇心和精力去探索他们自身个性和看外面世界的大学生们很容易受到大千世界的诱惑，走出大学校园，去接触那些美好和壮阔。另一方面，大学生也有他们自己的压力，来自于学业、就业以及人际关系，而旅行是对抗压力的极妙良方。通常一个人旅行归来，都会感觉神清气爽，焕然一新。
依我看来，尽管大学生寻求旅行的乐趣与享受很自然，但他们也应当赋予旅行更深层次的意义。在这个过程中，一个人可以尝试着去接触当地人并深度体验他们的文化，同来自不同文化背景的人成为朋友，并且从心底感受到一种自由、自立的感觉。旅行的确能让人收益颇丰。""",
    'questions': [],
}

EXTRA = [build_cloze(), build_newtype(), build_translation(), WRITING_A, WRITING_B]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {'year': 2016, 'articles': EXTRA}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已写入 {OUT}')
    for a in EXTRA:
        print(f"  {a['id']}: {len(a.get('sentences', []))} 句 / {len(a.get('questions', []))} 题")


if __name__ == '__main__':
    main()
