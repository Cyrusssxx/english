# -*- coding: utf-8 -*-
"""为 2013 年构建完形/新题型/翻译/作文四模块数据，输出 tools/extracted/modules/2013_extra.json。

数据来源：
- 真题文本 tools/extracted/2013_exam.txt（英文原文/选项干净）
- 解析文本 tools/extracted/2013_notes.txt（官方译文/范文/答案）

用法：python -X utf8 tools/build_2013_extra.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'extracted' / 'modules' / '2013_extra.json'


def split_cn(text):
    """中文按句号/问号/叹号切句。"""
    return [s.strip() for s in re.split(r'(?<=[。！？])', text) if s.strip()]


# ---------- 完形填空 ----------
CLOZE_ANSWERS = list('BDBACBADC AACBDCDABDC'.replace(' ', ''))  # 20 题答案
assert len(CLOZE_ANSWERS) == 20, len(CLOZE_ANSWERS)

# 20 题选项（真题文本顺序）
CLOZE_OPTIONS = {
    1: {'A': 'Moreover', 'B': 'However', 'C': 'Therefore', 'D': 'Otherwise'},
    2: {'A': 'off', 'B': 'back', 'C': 'over', 'D': 'around'},
    3: {'A': 'power', 'B': 'concept', 'C': 'history', 'D': 'role'},
    4: {'A': 'reverse', 'B': 'resist', 'C': 'resume', 'D': 'reward'},
    5: {'A': 'silent', 'B': 'sudden', 'C': 'slow', 'D': 'steady'},
    6: {'A': 'for', 'B': 'against', 'C': 'with', 'D': 'on'},
    7: {'A': 'expensive', 'B': 'imaginative', 'C': 'sensitive', 'D': 'productive'},
    8: {'A': 'similar', 'B': 'original', 'C': 'temporary', 'D': 'dominant'},
    9: {'A': 'collect', 'B': 'copy', 'C': 'provide', 'D': 'print'},
    10: {'A': 'give up', 'B': 'take over', 'C': 'bring back', 'D': 'pass down'},
    11: {'A': 'before', 'B': 'after', 'C': 'since', 'D': 'when'},
    12: {'A': 'kept', 'B': 'borrowed', 'C': 'withdrawn', 'D': 'released'},
    13: {'A': 'Unless', 'B': 'Because', 'C': 'Until', 'D': 'Though'},
    14: {'A': 'hide', 'B': 'express', 'C': 'ease', 'D': 'raise'},
    15: {'A': 'analyzed', 'B': 'shared', 'C': 'stored', 'D': 'displayed'},
    16: {'A': 'unsafe', 'B': 'unnatural', 'C': 'unclear', 'D': 'uncommon'},
    17: {'A': 'steal', 'B': 'choose', 'C': 'benefit', 'D': 'return'},
    18: {'A': 'consideration', 'B': 'prevention', 'C': 'manipulation', 'D': 'justification'},
    19: {'A': 'call for', 'B': 'fight against', 'C': 'adapt to', 'D': 'cope with'},
    20: {'A': 'chunk', 'B': 'chip', 'C': 'trail', 'D': 'path'},
}

# 完形正文（含 [n] 占位符），逐句与官方译文对齐
CLOZE_BODY = [
    "Given the advantages of electronic money, you might think that we would move quickly to the cashless society in which all payments are made electronically.",
    "[1], a true cashless society is probably not around the corner.",
    "Indeed, predictions have been [2] for two decades but have not yet come to fruition.",
    'For example, Business Week predicted in 1975 that electronic means of payment would soon "revolutionize the very [3] of money itself," only to [4] itself several years later.',
    "Why has the movement to a cashless society been so [5] in coming?",
    "Although electronic means of payment may be more efficient than a payments system based on paper, several factors work [6] the disappearance of the paper system.",
    "First, it is very [7] to set up the computer, card reader, and telecommunications networks necessary to make electronic money the [8] form of payment.",
    "Second, paper checks have the advantage that they [9] receipts, something that many consumers are unwilling to [10].",
    "Third, the use of paper checks gives consumers several days of \"float\" - it takes several days [11] a check is cashed and funds are [12] from the issuer's account, which means that the writer of the check can earn interest on the funds in the meantime.",
    "[13] electronic payments are immediate, they eliminate the float for the consumer.",
    "Fourth, electronic means of payment may [14] security and privacy concerns.",
    "We often hear media reports that an unauthorized hacker has been able to access a computer database and to alter information [15] there.",
    "The fact that this is not an [16] occurrence means that dishonest persons might be able to access bank accounts in electronic payments systems and [17] from someone else's accounts.",
    "The [18] of this type of fraud is no easy task, and a new field of computer science is developing to [19] security issues.",
    "A further concern is that the use of electronic means of payment leaves an electronic [20] that contains a large amount of personal data.",
    "There are concerns that government, employers, and marketers might be able to access these data, thereby violating our privacy.",
]
CLOZE_CN = [
    "鉴于电子货币的优势，你或许认为我们将迅速步入无现金社会，所有支付将电子化。",
    "然而真正的无现金社会可能不会马上到来。",
    "实际上，二十年来一直有这样的预测，但至今还没有实现。",
    '例如，1975年《商业周刊》预测称，电子支付手段不久将"彻底改变（人们对）钱币本身的观念"，不料几年之后该言论也不攻自破了。',
    "为什么步入无现金社会的步伐如此缓慢？",
    "尽管电子支付手段可能会比纸币付款系统更为高效，但是一些因素却阻止了纸币付款系统的消失。",
    "其一，建立使电子货币成为主要支付方式的计算机、读卡器以及电信网络是非常昂贵的。",
    "其二，纸质支票的优势在于它们提供了很多消费者都不愿意放弃的收据。",
    "其三，纸质支票给消费者提供了几天的\u201c浮动期\u201d——支票兑现及资金从出票人账户中提取需要几天的时间，这意味着出票人在此期间能够获取资金的利息。",
    "由于电子支付是即时的，消费者便没有了浮动期。",
    "其四，电子支付方式可能会引发安全和隐私忧虑。",
    "我们经常听媒体报道称，非法黑客已经能够访问计算机数据库，并改变储存于其中的信息。",
    "而这并非罕见事件的事实意味着欺诈分子能够访问电子支付系统的银行账户，并从别人的账户中进行窃取。",
    "此种欺诈行为的预防并不容易，人们还要研究新的计算机科学领域以应对安全问题。",
    "更令人担忧的是，电子支付手段会留下电子踪迹，其中包含大量的个人数据信息。",
    "有人担心，政府、雇主和营销人员可能能够访问这些数据，从而侵犯我们的隐私。",
]
assert len(CLOZE_BODY) == len(CLOZE_CN) == 16

# 完形官方精解（依据 2013_notes.txt 试题精解整理）
CLOZE_EXPL = {
    1: '本题考查上下文逻辑关系。上文指出鉴于电子货币的优势，你或许认为我们将迅速步入无现金社会……。后文则指出真正的无现金社会可能不会马上到来。上下文为语义转折关系，[B]正确。',
    2: '本题考查句内语义+副词特殊用法。空格所在句指"实际上，二十年来（关于人类将迅速步入无现金社会的）预测一直……，但至今还没有实现"。根据句内的语义转折，应是20年来相关预测一直持续，但没有实现过。around意为existing, present in a place"存在，出现"，符合文意。',
    3: '本题考查上下文语义。空格所在句例证（for example）上文"关于\u2018人类将迅速步入无现金社会\u2019的预测一直存在但都未实现"，即《商业周刊》1975年预测"电子支付手段不久将\u2018彻底改变钱币本身的……\u2019"。cash→cashless/electronic means of payment是"人类将迅速步入无现金社会"的同义表述。从纸币支付到电子支付，这体现的是货币本身概念的变化，而非其力量、历史、角色职能的变化。[B]正确。',
    4: '本题考查上下文语义。由第3题分析可知，空格所在句例证上文，主句介绍《商业周刊》1975年的预测内容，空格所在部分为结果状语，only to do结构强调结果令人失望或意外，指出预测未能实现。reverse oneself（on sth）意为"承认错误，放弃（立场）"，[A]符合文意。',
    5: '本题考查上下文语义。空格所在句根据上文提出疑问。上文已经指出"关于人类将迅速步入无现金社会的预言20年来一直存在，但却一直没有实现"，并给出了例证。这都说明无现金社会不会很快到来。选项中符合文意的是[C]，代入表示"为什么步入无现金社会的步伐如此缓慢"？',
    6: '本题考查上下文语义+动词短语。文章首段末句提出问题"为何步入无现金社会的步伐如此缓慢"，纵观下文，列举了4个因素对此进行了分析和解答。因此空格所在句的several factors应是步入无现金社会缓慢的原因，其对纸币付款系统的消失自然是起到对抗、限制的效果。[B]符合文意。',
    7: '本题考查上下文语义。空格所在句意在说明"建立电子支付方式所必需的计算机、读卡器以及电信网络是非常……的"。根据文意，这是制约纸币付款系统消失因素中的第一条，应为纸币付款系统的优势或电子支付系统的弊端，排除[D]。[B]、[C]明显不符合文意。[A]项代入，表示建立电子支付所需设施非常昂贵，为电子支付手段的一个弊端，符合文意。',
    8: '本题考查上下文语义。空格所在句意为"建立使电子货币成为……支付方式的设施是非常昂贵的"。全文论述了两种支付方式，即纸币和电子货币。论述围绕为何电子货币时代不会很快到来展开，即，电子支付方式不会很快成为首要的、占优势的支付方式。空格所在句便是决定电子支付方式不会很快成为首要支付方式的原因之一，[D]符合文意。其他项与文章相关度不大，排除。',
    9: '本题考查句内语义+常识。空格所在句从纸质支票优势入手论述了第二个制约纸币支付系统消失的因素，即，"纸质支票……收据（即付款凭证）"。纸质支票显然不能收集、复制、打印收据，但纸质支票却能够成为付款凭证；[C]项代入表示"纸质支票提供收据"，符合文意。',
    10: '本题考查句内语义+动词短语。空格所在部分作定语修饰something（即上半句的receipts），意在说明纸质支票的优势在于它们提供了很多消费者都不愿意……的收据。既然是优势，其提供的东西，即收据，自然是很多消费者需要的，即不愿舍弃的，[A]符合文意。',
    11: '本题考查句内逻辑。空格所在句论述的是第三个因素，即纸质支票为消费者提供几天的"浮动期"，破折号后的空格部分对此做出解释，因此应是支票兑现及资金从出票人账户中……之前需要几天时间，这段时间构成了"浮动期"，出票人可在此期间获取资金的利息。[A]符合文意。',
    12: '本题考查句内语义。空格所在部分含义为"资金从出票人账户中……"，纸质支票支付给收款人（卖方）的金额应该是从出票人（消费者）账户中提取的。[C]与文意相吻合。',
    13: '本题考查句内逻辑关系。上文指出，由于纸质支票的兑现和提取需要几天的时间，从而给消费者提供了几天的"浮动期"；可知空格所在句"……电子支付是即时的，消费者便没有了浮动期"的从句和主句为因果关系，即由于电子支付是即时的，因此没有了浮动期。[B]为正确选项。',
    14: '本题考查上下文语义。空格所在句意为"电子支付方式可能会……安全性和隐私问题"，下文谈到了黑客入侵计算机账户，政府、企业等可能获取包含有个人隐私的数据，这些都表明电子支付方式对安全和隐私构成了威胁。选项中能表达这层意思的只有[D]。',
    15: '本题考查句内语义。空格后的there即指（in）a computer database（计算机数据库），空格填入词语用于说明信息与计算机数据库之间的关系。空格所在句论述安全及隐私，因此信息并非公开的、可分享的，排除[B]、[D]；[A]明显与文意不符。[C]代入指储存于数据库中的信息，符合文意。',
    16: '本题考查上下文语义。空格所在句中，that引导的从句做the fact的同位语，其中this指代上一句中"黑客潜入电脑数据库更改信息"的内容。而上一句句首提到我们经常（often）听到媒体报道这类事件，证明这类事件是常见的，即不是罕见的。[D]正确。',
    17: '本题考查上下文语义。空格处的动作由欺诈分子发出，作用于其他人的账户，结合上文内容，可知该行为损害人们的财产安全，[A]符合文意。',
    18: '本题考查上下文语义。空格所在部分"此种欺诈行为的……并非易事"中，this type of fraud指代上文介绍的电子货币支付系统的弊端之一"安全问题"，空格处填入词应为对这种安全问题采取的行动，[B]符合文意。',
    19: '本题考查上下文语义+动词短语。结合18题分析可知，空格所在部分介绍"预防这种欺诈行为"的一项具体措施，空格所在不定式结构to security issues介绍措施的目的，即"处理/应对安全问题"，[D]正确。',
    20: '本题考查上下文语义。空格所在句论述电子支付手段另一弊端，即会留下包含大量个人资料的电子……。[A]无法与electronic搭配，[B]违背常识，首先排除。[D]为积极色彩，与"这些\u2018电子……\u2019有可能为政府、雇主和营销人员所利用"不衔接。[C]项代入表示"电子踪迹"，符合文意要求。',
}


def build_cloze():
    sentences = []
    for i, (en, cn) in enumerate(zip(CLOZE_BODY, CLOZE_CN), 1):
        sentences.append({
            'id': f'2013_cloze_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(1, 21):
        questions.append({
            'id': f'2013_cloze_q{n:02d}', 'number': n, 'qtype': '完形',
            'stem': f'第 {n} 空：选择最合适的词填入空白 [{n}]', 'stem_cn': '',
            'options': CLOZE_OPTIONS[n],
            'options_cn': {L: '' for L in 'ABCD'},
            'answer': CLOZE_ANSWERS[n - 1],
            'explanation': CLOZE_EXPL[n],
            'related_sentences': [f'2013_cloze_s{i:02d}' for i in range(1, len(CLOZE_BODY) + 1)],
        })
    return {
        'id': '2013_cloze', 'type': 'cloze',
        'title': 'Cashless Society Is Not Around the Corner',
        'topic': '完形填空：电子支付时代不会很快到来，文章分析了限制纸币系统消失的四个原因。',
        'source': 'Section I Use of English',
        'sentences': sentences, 'questions': questions,
    }


# ---------- 新题型（小标题对应） ----------
NEWTYPE_POOL = {
    'A': 'Live like a peasant',
    'B': 'Balance your diet',
    'C': 'Shopkeepers are your friends',
    'D': 'Remember to treat yourself',
    'E': 'Stick to what you need',
    'F': 'Planning is everything',
    'G': 'Waste not, want not',
}
NEWTYPE_POOL_CN = {
    'A': '像农民一样生活',
    'B': '均衡你的膳食',
    'C': '店主是你的朋友',
    'D': '记得犒劳自己',
    'E': '坚持自己所需',
    'F': '计划是一切',
    'G': '不浪费就不会匮乏',
}
NEWTYPE_ANSWERS = {41: 'F', 42: 'E', 43: 'G', 44: 'C', 45: 'D'}
NEWTYPE_EXPL = {
    41: '第二段首句即亮明建议：冲动消费不可取，应该事先规划一周菜单。随后解释了这样做的意义，不仅最大程度地节省了开支，而且可以均衡膳食。选项[F] planning is everything与段中主旨句plan your...in advance, making...lists...相一致，因此[F]为正确选项。',
    42: '第三段首句紧承小标题内容指出（这样的话），超市购物的优势就凸显出来，第二句解释：可以买其所想，无需担心购物量少会造成尴尬。可见stick to what you need应为该段小标题，即"坚持只购买自己所需要的"；其次，段中第三句进一步以例子明确了该段中心：you\u2019ll know that you only need...与标题[E]相对应，因此[E]为正确选项。',
    43: '第四段通过对比指出"储备食品不是越少越好，相反应当在确保储备量的情况下最大化利用多余食品"，因此本段中心在于"尽可能不浪费"，选项[G]中waste not与之相统一。其次，段中第二句说明博主理念：储备足够多的东西；随后第三句实际上反过来表明实现"储备丰富，食物不缺"的途径：不浪费。因此waste not, want not（不浪费就不会匮乏）很好地概括了本段内容。',
    44: '第五段首句指出小标题所涉内容是省钱妙招。第二、三句作出说明：经常定期友善地光顾食品零售店，很快会获赠免费熬汤食材。第二句Shop at...regularly, even for small things, and be super friendly与Shopkeepers are your friends相契合，即与店主保持良好友谊利于省下熬汤原料的开支，因此正确答案为[C]。',
    45: '第六段首句save your pennies and once...treat yourself to...at a good restaurant表明即使经济拮据，也应当用省下来的钱定期犒劳自己一顿美食。[D]选项Remember to treat yourself是对该段主旨的概括。',
}
# 正文（导言段 + 41-45 段），逐句对齐
NEWTYPE_BODY = [
    "The hugely popular blog the Skint Foodie chronicles how Tony balances his love of good food with living on benefits.",
    "After bills, Tony has £60 a week to spend, £40 of which goes on food, but 10 years ago he was earning £130,000 a year working in corporate communications and eating at London's best restaurants at least twice a week.",
    "Then his marriage failed, his career burned out and his drinking became serious.",
    "\"The community mental health team saved my life.",
    "And I felt like that again, to a certain degree, when people responded to the blog so well.",
    "It gave me the validation and confidence that I'd lost.",
    "But it's still a day-by-day thing.\"",
    "Now he's living in a council flat and fielding offers from literary agents.",
    "He's feeling positive, but he'll carry on blogging - not about eating as cheaply as you can - \"there are so many people in a much worse state, with barely any money to spend on food\" - but eating well on a budget.",
    "Here's his advice for economical foodies.",
    "Impulsive spending isn't an option, so plan your week's menu in advance, making shopping lists for your ingredients in their exact quantities.",
    "I have an Excel template for a week of breakfast, lunch and dinner.",
    "Stop laughing: it's not just cost effective but helps you balance your diet.",
    "It's also a good idea to shop daily instead of weekly, because, being human, you'll sometimes change your mind about what you fancy.",
    "This is where supermarkets and their anonymity come in handy.",
    "With them, there's not the same embarrassment as when buying one carrot in a little greengrocer.",
    "And if you plan properly, you'll know that you only need, say, 350g of shin of beef and six rashers of bacon, not whatever weight is pre-packed in the supermarket chiller.",
    "You may proudly claim to only have frozen peas in the freezer - that's not good enough.",
    "Mine is filled with leftovers, bread, stock, meat and fish.",
    "Planning ahead should eliminate wastage, but if you have surplus vegetables you'll do a vegetable soup, and all fruits threatening to \"go off\" will be cooked or juiced.",
    "Everyone says this, but it really is a top tip for frugal eaters.",
    "Shop at butchers, delis and fish-sellers regularly, even for small things, and be super friendly.",
    "Soon you'll feel comfortable asking if they've any knuckles of ham for soups and stews, or beef bones, chicken carcasses and fish heads for stock which, more often than not, they'll let you have for free.",
    "You won't be eating out a lot, but save your pennies and once every few months treat yourself to a set lunch at a good restaurant - £1.75 a week for three months gives you £21 - more than enough for a three-course lunch at Michelin-starred Arbutus.",
    "It's £16.95 there - or £12.99 for a large pizza from Domino's: I know which I'd rather eat.",
]
NEWTYPE_CN = [
    "广受欢迎的博客Skint Foodie（穷光蛋美食家）记录了托尼在靠救济金度日的同时如何实现自己对美食的热爱。",
    "支付完各种账单后，托尼每周只剩60英镑可供花销，其中有40英镑花在吃上，但是10年前他在通讯公司工作时年薪高达13万英镑，每周至少在伦敦顶级饭店就餐两次。",
    "后来他婚姻破裂，事业衰败，并且酗酒严重。",
    "\u201c社区精神卫生小组救了我。",
    "人们在博客热情留言回复时，我在某种程度上又有了对生活的渴望。",
    "这让我找回曾经失去的认可和自信。",
    "但是记录博客仍然是每天都必须要做的事情。\u201d",
    "现在他住在救济公寓中处理来自文稿代理商的约稿。",
    "他现在心态很积极，但是他还是会继续更新博客——不是围绕尽可能吃得便宜——\u201c有许多人情况更糟，几乎没什么钱买食物\u201d——而是如何通过避免不必要的开支吃好。",
    "以下是他为节约型美食家提供的一些建议。",
    "冲动消费不可取，所以提前规划好你每周的菜单，食材购买清单要详细标明数量。",
    "我这里有一周早午晚三餐的Excel模板。",
    "别笑：这不仅能节约开支，还可以均衡膳食。",
    "每天购物比每周购物要好，因为人有时难免会想换换口味。",
    "这时超市及其匿名性就有用武之地了。",
    "有了超市，就不用因为在一家小蔬菜店里只买了一根胡萝卜而感到尴尬。",
    "如果你计划得当，你会知道自己只需要，比如，350克的牛内脏骨和6片培根，而不是超市冷柜中分装好的任何分量。",
    "你也许会自豪地表示冰箱里只有冷冻青豆——这还不够好。",
    "我的冰箱里满满的都是剩饭、面包、高汤、肉和鱼等。",
    "提前计划可能会减少浪费，但是如果有多余的蔬菜，就可以做蔬菜汤，所有即将变质的水果也可以用来做菜或榨汁。",
    "每个人都这样说，不过这的确是让节约的食客更省钱的妙方。",
    "定期光顾肉店、熟食店和鱼产店，哪怕是买些很小的东西，而且要非常友善。",
    "不久，当你询问卖家是否有可以炖汤的大棒骨或者用来熬高汤的牛骨、鸡架、鱼头等时，你就不会觉得尴尬，因为他们常常会把这些东西免费送给你。",
    "你不用常常下馆子，但把每分钱节约下来，每隔几月去高级餐厅款待自己一顿午间套餐——每周节约1.75英镑，三个月就是21英镑——这在米其林星级饭店Arbutus吃一顿三道菜午餐绰绰有余。",
    "16.95英镑足矣——或者在多米诺消费12.99英镑买一份大披萨：我知道自己更爱吃哪样。",
]
assert len(NEWTYPE_BODY) == len(NEWTYPE_CN) == 25


def build_newtype():
    sentences = []
    for i, (en, cn) in enumerate(zip(NEWTYPE_BODY, NEWTYPE_CN), 1):
        sentences.append({
            'id': f'2013_newtype_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(41, 46):
        questions.append({
            'id': f'2013_newtype_q{n}', 'number': n, 'qtype': '小标题',
            'stem': f'第 {n} 段：选择最合适的小标题填入空白', 'stem_cn': '',
            'options': {}, 'options_cn': {},
            'answer': NEWTYPE_ANSWERS[n],
            'explanation': NEWTYPE_EXPL[n],
            'related_sentences': [f'2013_newtype_s{i:02d}' for i in range(1, len(NEWTYPE_BODY) + 1)],
        })
    return {
        'id': '2013_newtype', 'type': 'newtype',
        'title': 'Eating Well on a Budget',
        'topic': '新题型（小标题对应）：博客作者在经济拮据的情况下如何吃好的五条建议。',
        'source': 'Section II Part B',
        'pool': NEWTYPE_POOL, 'pool_cn': NEWTYPE_POOL_CN,
        'sentences': sentences, 'questions': questions,
    }


# ---------- 翻译 ----------
TRANSLATION_BODY = [
    "I can pick a date from the past 53 years and know instantly where I was, what happened in the news and even the day of the week.",
    "I've been able to do this since I was four.",
    "I never feel overwhelmed with the amount of information my brain absorbs.",
    "My mind seems to be able to cope and the information is stored away neatly.",
    "When I think of a sad memory, I do what everybody does - try to put it to one side.",
    "I don't think it's harder for me just because my memory is clearer.",
    "Powerful memory doesn't make my emotions any more acute or vivid.",
    "I can recall the day my grandfather died and the sadness I felt when we went to the hospital the day before.",
    "I also remember that the musical play Hair opened on Broadway on the same day - they both just pop into my mind in the same way.",
]
TRANSLATION_CN = [
    "在过去的53年中任意挑一天，我马上就能知道那天我在什么地方，新闻报道了什么，甚至那天是星期几。",
    "我从四岁开始就有这本事了。",
    "我从来不会因为脑子吸收大量信息而受不了。",
    "我的脑子似乎能够应付，而且这些信息也储存得有条有理。",
    "当我回想起一件悲伤的事情时，我所做的和大家一样——尽量把它放到一边。",
    "我不觉得就因为我的记忆更清晰，我就会更难受。",
    "强大的记忆力并没有使我的情感更为强烈或更为鲜明。",
    "我能回想起我祖父去世的那一天，以及我们前一天去医院时我伤心的感觉。",
    "我同样记得，音乐剧《毛发》在同一天于百老汇上演——这两件事在我脑海里突然出现的方式没什么两样。",
]
TRANSLATION_REF = '在过去的53年中任意挑一天，我马上就能知道那天我在什么地方，新闻报道了什么，甚至那天是星期几。我从四岁开始就有这本事了。我从来不会因为脑子吸收大量信息而受不了。我的脑子似乎能够应付，而且这些信息也储存得有条有理。当我回想起一件悲伤的事情时，我所做的和大家一样——尽量把它放到一边。我不觉得就因为我的记忆更清晰，我就会更难受。强大的记忆力并没有使我的情感更为强烈或更为鲜明。我能回想起我祖父去世的那一天，以及我们前一天去医院时我伤心的感觉。我同样记得，音乐剧《毛发》在同一天于百老汇上演——这两件事在我脑海里突然出现的方式没什么两样。'
assert len(TRANSLATION_BODY) == len(TRANSLATION_CN) == 9


def build_translation():
    sentences = []
    for i, (en, cn) in enumerate(zip(TRANSLATION_BODY, TRANSLATION_CN), 1):
        sentences.append({
            'id': f'2013_translation_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    return {
        'id': '2013_translation', 'type': 'translation',
        'title': 'A Remarkable Memory',
        'topic': '翻译：超凡的记忆能力——作者讲述自己具有超凡的记忆力，大脑能自如应对庞大信息量。',
        'source': 'Section III Translation',
        'ref_cn': TRANSLATION_REF,
        'sentences': sentences, 'questions': [],
    }


# ---------- 作文 ----------
WRITING_A = {
    'id': '2013_writinga', 'type': 'writing_a',
    'title': 'Part A 应用文：邀请同学参加义卖',
    'topic': '小作文：给同学写一封电子邮件，告知班级义卖活动的细节并鼓励他们参加。',
    'source': 'Section IV Writing Part A',
    'sample_en': """Dear classmates,
It is a great honor to inform you that a charity sale is scheduled for September 23 from 8 a.m. to 5 p.m. This sale is going to be held in the auditorium for the sake of kids on the verge of dropping out and the gain will be donated to the Project Hope. We are desirous of raising sufficient money to help 15 kids in financially strained families. Your participation is necessary to achieve this aim.
Hopefully, you can come and pick up your desired commodities. You will happily find latest books and pretty stationery being sold at a discount there.
Yours sincerely,
Li Ming""",
    'sample_cn': """亲爱的同学们：
很荣幸地通知你们一场义卖将于9月23日上午8点到下午5点举办。义卖举办地点在礼堂，目的是帮助辍学边缘的孩子们，所有义卖所得将捐献给希望工程。我们希望筹集到足够资金帮助15位家境贫寒的孩子。你们的参加是实现这一目的的必要条件。
希望你们能来挑选心仪的商品。你们将很高兴地发现有最新的图书和漂亮的文具打折出售。
诚挚的，
李明""",
    'questions': [],
}

WRITING_B = {
    'id': '2013_writingb', 'type': 'writing_b',
    'title': 'Part B 大作文：大学生兼职比例柱状图',
    'topic': '大作文：根据柱状图写一篇约150词的短文，解读大学生兼职比例逐年上升的数据并发表评论。',
    'source': 'Section IV Writing Part B',
    'chart_img': 'img/2013_writingb_chart.png',
    'sample_en': """The rate of college students taking part-time jobs during school time rises annually from 67.77% in the first year to 88.24% in the final year. The biggest increase occurs in the graduation year, with the rate 16% higher than a year ago.
College students will become increasingly willing to work part-time mainly because of the growing wish to gain practical experience to prepare for their later careers. It is reasonable and wise to do such preparation especially after unemployment reached a record high in early 2013. Another motive is obviously the money. As the school year advances, there will be huger costs of studying materials and social events, undoubtedly pushing students to reap money from part-time jobs.
It can indeed be beneficial for college students to be part timers. However, the risk of erosion of study time should be also considered. To benefit from part-time jobs without suffering academically, students should learn to strike a balance.""",
    'sample_cn': """在校大学生兼职比例逐年上升，从大一67.77%到大四88.24%。最大增幅发生在大四，其比率比前一年高16%。
大学生会越来越愿意从事兼职工作，主要源于日益迫切地希望为之后的职业生涯做准备而积累实际经验。做这样的准备是有道理且明智的，尤其在2013年上半年失业人数创下历史新高后更是如此。另一个动机明显是金钱。当学生进入高年级，学习资料和社交会花费更多，无疑迫使学生从兼职中获得收入。
大学生兼职的确是有益的。但是，也不能忽视学习时间会遭到侵蚀的风险。要从兼职中获益的同时不损害学业，学生应该学会谋求平衡。""",
    'questions': [],
}

EXTRA = [build_cloze(), build_newtype(), build_translation(), WRITING_A, WRITING_B]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {'year': 2013, 'articles': EXTRA}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已写入 {OUT}')
    for a in EXTRA:
        print(f"  {a['id']}: {len(a.get('sentences', []))} 句 / {len(a.get('questions', []))} 题")


if __name__ == '__main__':
    main()
