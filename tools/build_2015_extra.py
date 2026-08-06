# -*- coding: utf-8 -*-
"""为 2015 年构建完形/新题型/翻译/作文四模块数据，输出 tools/extracted/modules/2015_extra.json。

数据来源：
- 真题文本 tools/extracted/2015_exam.txt（英文原文/选项干净）
- 解析文本 tools/extracted/2015_notes.txt（官方译文/范文/答案）

用法：python -X utf8 tools/build_2015_extra.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'tools' / 'extracted' / 'modules' / '2015_extra.json'


# ---------- 完形填空 ----------
CLOZE_ANSWERS = list('ADBACBADC BACCDCDABDB'.replace(' ', ''))
assert len(CLOZE_ANSWERS) == 20, len(CLOZE_ANSWERS)

CLOZE_OPTIONS = {
    1: {'A': 'signal', 'B': 'permit', 'C': 'ticket', 'D': 'record'},
    2: {'A': 'nothing', 'B': 'little', 'C': 'another', 'D': 'much'},
    3: {'A': 'beaten', 'B': 'plugged', 'C': 'guided', 'D': 'brought'},
    4: {'A': 'message', 'B': 'code', 'C': 'notice', 'D': 'sign'},
    5: {'A': 'under', 'B': 'beyond', 'C': 'behind', 'D': 'from'},
    6: {'A': 'misapplied', 'B': 'misinterpreted', 'C': 'misadjusted', 'D': 'mismatched'},
    7: {'A': 'judged', 'B': 'fired', 'C': 'replaced', 'D': 'delayed'},
    8: {'A': 'unreasonable', 'B': 'ungrateful', 'C': 'unconventional', 'D': 'unfamiliar'},
    9: {'A': 'comfortable', 'B': 'confident', 'C': 'anxious', 'D': 'angry'},
    10: {'A': 'attend', 'B': 'turn', 'C': 'take', 'D': 'point'},
    11: {'A': 'dangerous', 'B': 'mysterious', 'C': 'violent', 'D': 'boring'},
    12: {'A': 'bend', 'B': 'resist', 'C': 'hurt', 'D': 'decay'},
    13: {'A': 'lecture', 'B': 'debate', 'C': 'conversation', 'D': 'negotiation'},
    14: {'A': 'trainees', 'B': 'employees', 'C': 'researchers', 'D': 'passengers'},
    15: {'A': 'reveal', 'B': 'choose', 'C': 'predict', 'D': 'design'},
    16: {'A': 'voyage', 'B': 'flight', 'C': 'walk', 'D': 'ride'},
    17: {'A': 'went through', 'B': 'did away', 'C': 'caught up', 'D': 'put up'},
    18: {'A': 'In turn', 'B': 'In fact', 'C': 'In particular', 'D': 'In consequence'},
    19: {'A': 'unless', 'B': 'whereas', 'C': 'if', 'D': 'since'},
    20: {'A': 'funny', 'B': 'simple', 'C': 'logical', 'D': 'rare'},
}

CLOZE_BODY = [
    "In our contemporary culture, the prospect of communicating with - or even looking at - a stranger is virtually unbearable.",
    "Everyone around us seems to agree by the way they cling to their phones, even without a [1] on a subway.",
    "It's a sad reality - our desire to avoid interacting with other human beings - because there's [2] to be gained from talking to the stranger standing by you.",
    "But you wouldn't know it, [3] into your phone.",
    "This universal protection sends the [4]: \"Please don't approach me.\"",
    "What is it that makes us feel we need to hide [5] our screens?",
    "One answer is fear, according to Jon Wortmann, an executive mental coach.",
    "We fear rejection, or that our innocent social advances will be [6] as \"weird.\"",
    "We fear we'll be [7].",
    "We fear we'll be disruptive.",
    "Strangers are inherently [8] to us, so we are more likely to feel [9] when communicating with them compared with our friends and acquaintances.",
    "To avoid this uneasiness, we [10] to our phones.",
    "\"Phones become our security blanket,\" Wortmann says.",
    "\"They are our happy glasses that protect us from what we perceive is going to be more [11].\"",
    "But once we rip off the band-aid, tuck our smartphones in our pockets and look up, it doesn't [12] so bad.",
    "In one 2011 experiment, behavioral scientists Nicholas Epley and Juliana Schroeder asked commuters to do the unthinkable: Start a [13].",
    "They had Chicago train commuters talk to their fellow [14].",
    "\"When Dr. Epley and Ms. Schroeder asked other people in the same train station to [15] how they would feel after talking to a stranger, the commuters thought their [16] would be more pleasant if they sat on their own,\" The New York Times summarizes.",
    "Though the participants didn't expect a positive experience, after they [17] with the experiment, \"not a single person reported having been embarrassed.\"",
    "[18], these commutes were reportedly more enjoyable compared with those without communication, which makes absolute sense, [19] human beings thrive off of social connections.",
    "It's that [20]: Talking to strangers can make you feel connected.",
]
CLOZE_CN = [
    "在我们的当代文化中，与陌生人交流，或甚至是看一眼陌生人，这种情形几乎是难以忍受的。",
    "我们身边的每一个人似乎都颇有同感：人们抱着手机不放，哪怕地铁里没有一点儿信号。",
    "这是个可悲的现实——我们想要避免和其他人交流的愿望——因为与站在你身边的陌生人交谈会获益良多。",
    "但你不懂得这一点，一心沉浸在你的手机中。",
    "这个大家都在使用的护身装束传达出这样一条信息：\u201c请不要靠近我。\u201d",
    "是什么让我们觉得自己需要躲在屏幕后面？",
    "高级心理培训师乔恩·沃特曼认为，答案之一是恐惧。",
    "我们害怕被拒绝，或者害怕我们单纯的主动社交行为会被误解为是\u201c怪异的\u201d。",
    "我们害怕自己会被品头论足。",
    "我们害怕会打扰到别人。",
    "我们本来就对陌生人不熟悉，因此与朋友或熟人相比，我们与陌生人交流时更有可能会感到焦虑。",
    "为了避免这种局促感，我们转向我们的手机。",
    "\u201c手机成了我们的安全毯，\u201d沃特曼说道。",
    "\u201c它们是我们愉悦的眼镜，使我们免受我们认为可能会更危险的事物之害。\u201d",
    "但一旦我们撕掉这个绷带，把我们的智能手机塞入口袋，抬起头来，其实情况并没那么糟糕。",
    "在2011年的一项实验中，行为科学家尼古拉斯·埃普利和朱莉安娜·施罗德让通勤者做了一件不可思议的事：主动攀谈。",
    "他们让芝加哥火车通勤乘客与同车的乘客聊天。",
    "\u201c当埃普利博士和施罗德女士让同一车站的其他人预测他们与陌生人交谈之后是什么感受时，那些通勤者认为，如果他们自己一个人坐着，旅途会更愉悦。\u201d《纽约时报》总结道。",
    "尽管参与者并没有期待会有一次积极体验，但当他们完成实验后，\u201c没有一个人声称自己感到尴尬\u201d。",
    "实际上，这些（参与交流的）通勤者的旅程据称比那些没有沟通的通勤者的旅程更加令人愉悦，这是完全合乎情理的，因为人类是在社会交往中发展起来的。",
    "道理很简单：与陌生人交谈可以让你感受到自己与他人是有联系的。",
]
assert len(CLOZE_BODY) == len(CLOZE_CN) == 21

CLOZE_EXPL = {
    1: '本题考查上下文语义。空格所在句描述现代人"不与陌生人交流"这一倾向的突出表现形式cling to their phones（紧握手机不放），even without a [1] on a subway（甚至在地铁里面都没有……）作为状语，修饰cling to...这一动作。B、C项虽能与句中subway构成语义场，表示乘坐地铁的条件"地铁票"，但两者并非"人们抱着手机不放"的潜在条件，因此首先排除；[D]项record可表示"手机记录"，但without a record on a subway（地铁上没有记录）不知所云，故排除该项；只有[A] signal既与subway构成语义场（根据常识地铁里常常没有信号），又能作为"玩手机（上网）"的潜在条件，故[A]正确。',
    2: '本题考查句内语义。It\u2019s a sad reality对上文"人们沉溺于手机而不愿与陌生人交流"这一事实作出评价，破折号间进一步重复该事实，随后以because...从句解释"可悲"的原因：there\u2019s [2] to be gained from talking to the stranger...（"与陌生人交流"使我们收获……），要符合"可悲"这一逻辑，该部分只能表达"与陌生人交流会产生正面作用"，[A]与[B]传达的"所获甚少"与此相反，首先排除；[C] another（又一）通常用于引出并列的第二面，而前文未曾提到相应的第一面，故排除；只有[D] much（获益良多），符合上下文语义逻辑。',
    3: '本题考查上下文语义。空格所在句But you wouldn\u2019t know it, [3] into your phone（……在你的手机中）后半句作为伴随状语，其逻辑主语为you，描述"人们对手机做出的某种动作"。根据前半句"人们未意识到与陌生人交流的益处"，以及随后一句This universal protection的回指功能（指代phone），空格所在句意思应为：人们用手机把自己防护起来（免于打扰他人或被打扰），也即"埋头玩手机，漠视一切外物"，选项中只有[B] plugged（本指"接插头，塞"）与into搭配可以喻指"沉溺其中"，符合语义逻辑。beat sb into sth意为"强迫某人做某事"，但"玩手机"属自愿行为，因此排除该项；[C]与[D]后接into your phone（引导人手机、卷入手机），逻辑上均不能成立。',
    4: '本题考查上下文语义+词义辨析。上句指出"人们忽略了与他人交流的意义，沉浸在手机中。"本句随后指出"大家都在使用的这个\u2018护身装束\u2019发送出[4]：请不要靠近我。"首先，从"主谓搭配"角度考虑，该句主语为"物"，物体不可能发出"通知"，因此可以首先排除[C]；其次，由于冒号后内容直接说明空格词，而"不要靠近我"显然是众所周知的内容，而非"代码、密码"或"迹象、符号"，排除[B]、[D]。只有[A] message与动词sends搭配，能与冒号后内容相统一，即"传达\u2018不要靠近我\u2019的信息"。',
    5: '本题考查句内语义+介词用法。空格处介词与our screens搭配作状语，说明动作hide（躲藏）的方式。句中screens指"手机屏幕"，根据上下文可知，本句就"人们为何需要沉溺于手机当中"发问，能表达"沉溺于手机（plugged into your phone）、以手机为护身装束（protection）"的只能是hide behind our screens（藏匿于手机之后）。[A] under与hide搭配意为"躲在……下方"，接宾语screens不符合逻辑，因此排除；[D]（hide sth/sb）from sb表示"（隐藏……）以免被某人发现"，与screens搭配同样不合逻辑。[B] beyond不能与hide搭配。正确项为[C]。',
    6: '本题考查词义辨析。空格所在句指出，我们害怕遭到拒绝，或者害怕我们单纯的主动社交行为会被[6]为是"怪异的"（will be...as weird），空格词必须从语法上能够与as...搭配，同时在语义上必须与前半句rejection传递出的"被排斥，被拒绝"这一负面感受一致；misapplied、misadjusted和mismatched三词虽含有否定意义，但从语法上来看均不能与as...构成合理搭配；只有misinterpreted既可以与as搭配，意为"被误解为是……的"，同时符合句内逻辑，因此[B]正确。',
    7: '本题考查平行结构+上下文语义。空格所在句"我们害怕自己会被[7]"。其前后两句We fear rejection, or that...、We fear we\u2019ll be disruptive排比列出人们害怕出现的情形。此三句间的平行关系暗示空格处动词应该与weird（古怪的）及disruptive（扰乱的）传递的负面感情保持一致，同时与上句动词misinterpreted相呼应，选项中只有[A] judged最符合，be judged可以表示"受到他人评论（但可能与事实不符）"，同时与上句"害怕被误认为是古怪的"相照应。[B] fired、[C] replaced与[D] delayed三项虽然带负面色彩，但原文并未涉及"与陌生人交往会\u2018被攻击\u2019、\u2018被取代\u2019或\u2018被耽搁\u2019令人害怕"，因此排除。[A]正确。',
    8: '本题考查词义辨析。空格处形容词作为表语，其逻辑主语为Strangers（陌生人），说明"陌生人对我们来说是怎样的"。由副词inherently可知，空格词应当体现strangers内在的通性，因此首先排除[A] unreasonable和[B] ungrateful，两者将一切陌生人蒙上"贬义"色彩，不合常识；[C] unconventional通常表示"（人、行为、态度、做法等）非常规的，非传统的"，但文中并未涉及"陌生人标新立异"这一内容，故排除。只有[D] unfamiliar（to us）完美概括了"陌生人"的通性——"不熟悉，不了解"，与后半句compared with our friends and acquaintances相照应，为正确项。',
    9: '本题考查上下文语义。空格所在句指出，"我们跟陌生人交谈比跟熟人和朋友交谈，更可能体会到[9]"，后句紧接着指出："为了避免这种焦虑（this uneasiness），我们……手机。"根据this的回指功能，可推知两句间呈现人们"遭遇问题（某种负面感情）——应对问题（使用手机）"的逻辑。故先排除正向的[A]、[B]项；[D]虽为负面含义，但"愤怒"之意在文中并未涉及，亦不符常理，故排除。只有[C] anxious（感到焦虑）与下句this uneasiness感情上色彩一致，含义上统一，符合题意。',
    10: '本题考查固定搭配。空格所在句指出"为了避免这种焦虑，我们[10]我们的手机"。目的状语To avoid...提示主句为"应对措施"，选项中只有[B] turn(to)暗含"求助于"之意，与上文"人们埋头玩手机，不与陌生人沟通"相呼应。[A] attend(to)作为"专心于"解时，描述一种"努力、尽责的态度"，后多接"工作、责任"等作宾语，如：to attend to one\u2019s duties做好自己的工作，尽职；作"听取"和"照顾"讲时，从逻辑上均不能以our phones作为宾语，故排除该项；[C] take(to)取"（尤指短时间内）喜欢上"之意时，无法成为"躲避焦虑的应对措施"。[D] point(to)虽可与our phones搭配，但"指向手机"不合逻辑。',
    11: '本题考查句内语义。空格所在句指出："手机成了我们的安全毯……，保护我们免受我们认为可能更[11]的事物的伤害"。显然，空格词只能表示"危险的、有危害的"，[B] mysterious为中性词，不含"伤害、危险"的意味，首先排除；[C] violent虽涉及"危险"，但人们不可能通过手机去规避暴力，故排除该项；[D] boring利用文中happy glasses（愉悦的眼镜）以及"手机能够带给人极大的娱乐"的常识设置干扰，但文中并未提及"与陌生人交流很无趣"这一内容，选项脱离语境，不合题意；[A] dangerous不仅能表示"具体事物所带来的危险"，还能够表示"抽象事物对人的心理伤害"，文中特指"人们认为的\u2018比与陌生人交流带来的焦虑感更甚的心理伤害\u2019"。',
    12: '本题考查上下文语义。it doesn\u2019t [12] so bad（情况并没有……得那么厉害）是对实验结果的概述，由段末"（实验参与者）没有一个人声称自己感到尴尬（not a single...embarrassed）"可知实验结果是正面的，即"将手机弃之一旁未带来负面感受"，只有[C] hurt符合这一逻辑，同时印证段首But一词，与上文"手机被视作保护毯，防止外界伤害"形成语义转折。[A] bend、[B] resist与[D] decay与doesn\u2019t...so bad搭配，指"屈服/抗拒/衰退得不那么厉害"，与上下文均无法衔接。',
    13: '本题考查上下文语义。空格所在句指出，"行为科学家让这些往返乘客做一件难以想象的事情：Start a [13]"。后一句指出"他们让芝加哥火车通勤乘客与同车乘客交谈（talk to）"，不难看出，后一句具体说明空格所在句，start a [13]与talk to同指，只有[C] conversation能够表达此意。其他三项分别表示"演讲"、"辩论"和"谈判"，不符合文中"与陌生人进行随意交流"这一语境，故排除，正确项为[C]。',
    14: '本题考查上下文语义。空格所在句为"他们让芝加哥火车通勤者与他们同车的[14]聊天（talk to their fellow...）"。由fellow（同种情况的，同类的人）一词可知，空格词应该与commuters相对应，两者均为"去芝加哥上班的人"，而实验中的交通工具为"火车"，故只有[D] passengers符合语境。[A] trainees（实习生）用train制造干扰，但该词与"乘坐火车的人"相差甚远。[B] employees与fellow搭配，表示"认识的同事"，不符合"实验中让通勤者与陌生同行者进行交谈"这一语义，故排除。[C] researchers利用与段中behavioral scientists干扰，同样不符合语境。',
    15: '本题考查上下文语义。空格所在句为"当科学家让同一车站的其他人[15]他们与陌生人交谈之后是什么感受时，通勤者认为……"。后一句说明实验结论："尽管参与者没有期待会有一场积极体验（didn\u2019t expect a positive experience...），……。"从④句thought...would（虚拟语气）和⑤句reported可知，两句应该是"先表预测，后揭示实际结果"的逻辑关系，因此空格词应该与expect意义相近，选项中只有[C] predict符合要求，表示对未来情况的"预测、预计"。[A] reveal和[B] choose两者的宾语只能为"已经发生、存在的事实"，与文中would...虚拟语气相矛盾，故排除；[D] design无法与宾语从句how they would feel搭配："感受不能设计"，故排除。正确项为[C]。',
    16: '本题考查词义辨析。空格所在句表达的是if假设情况下的结果推测："那些通勤者认为，如果他们各自坐在自己位置上，会觉得他们的[16]更令人愉悦"。纵观四个选项，正确项应该符合（train）commuters、sat on their own所包含的语义，只有[D] ride（乘汽车/火车等出行）符合要求，[A]指"乘船航行"，[B]指"乘坐飞机飞行"，[C]指"步行"，均不适合此语境，故[D]为正确项。',
    17: '本题考查固定搭配。空格所在句内容为环环相扣的三部曲：最初，实验参与者没有预计到会有一场积极体验→随后，他们进行了实验→最后，在[17]实验后，没有一个人声称自己感到尴尬。从逻辑上来看，只有"完成实验"，才能串起三部曲，揭晓实验结论，故正确项应为[A] went through，与with搭配表示"完成（实验）"。[B] "废除（实验）"与[C] "赶上（实验）"均不合逻辑，排除；[D] put up(with)意为"忍受（实验）"，虽然实验参与者起初不太愿意与陌生人交流，但不能就此推知他们在"（认为实验很糟糕而）容忍实验"。正确项为[A]。',
    18: '本题考查上下文逻辑关系。上文末句指出"与陌生乘客交谈的参与者中，所有人都未感到尴尬"，空格后指出，据称这些通勤者比起那些没有与他人交流的人来说，旅途更令人愉快；显然后句是对前一句的补充和递进，选项中只有[B] in fact（用于补充说明，强调前面所说的话）符合这一语义逻辑。[A] in turn表示as a result of sth，即"前文为后文的原因"；[C] in particular用于引出"特别的、需要强调的"举例。[D] in consequence引出结果，上文为"原因"，三项均不合语境。正确项为[B]。',
    19: '本题考查句内逻辑关系。空格前指出，"据称，这些（参与交流的）通勤者的旅程比那些没与人沟通的通勤者的旅程更加令人愉悦，这是完全合乎情理的"，空格后指出，"社会交往使人受益并获得发展（thrive off of social connections）。"不难看出，后半句对前半句"有沟通的旅程更令人愉悦"作出了解释，即"人类靠交往实现发展，交往使人愉悦便不足为奇"，[D] since含因果逻辑，符合题意。[B] whereas虽然也可以表达"原因"，但多位于句首，用于正式公文当中，排除；[A] unless和[C] if均表示"条件"，但"人类靠社会交往而发展"并非"有交流的旅途更令人愉悦"的条件。正确项为[D]。',
    20: '本题考查上下文语义。空格处形容词作表语修饰it，冒号引出对it所指内容的说明：与陌生人交谈让你感受到与他人相联系。即，交谈就是一种建立联系的过程，这显而易见，只有[B] simple符合要求。而文中并未指出这一现象"有趣"或"稀有"，故排除[A]、[D]；[C] logical侧重"逻辑推理"，而文中偏重于强调显而易见的道理，不存在"是否合乎逻辑"之说。因此正确项为[B]。',
}


def build_cloze():
    sentences = []
    for i, (en, cn) in enumerate(zip(CLOZE_BODY, CLOZE_CN), 1):
        sentences.append({
            'id': f'2015_cloze_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(1, 21):
        questions.append({
            'id': f'2015_cloze_q{n:02d}', 'number': n, 'qtype': '完形',
            'stem': f'第 {n} 空：选择最合适的词填入空白 [{n}]', 'stem_cn': '',
            'options': CLOZE_OPTIONS[n],
            'options_cn': {L: '' for L in 'ABCD'},
            'answer': CLOZE_ANSWERS[n - 1],
            'explanation': CLOZE_EXPL[n],
            'related_sentences': [f'2015_cloze_s{i:02d}' for i in range(1, len(CLOZE_BODY) + 1)],
        })
    return {
        'id': '2015_cloze', 'type': 'cloze',
        'title': 'Talking to Strangers',
        'topic': '完形填空：放下手机，与陌生人交流——与陌生人交谈会获益良多。',
        'source': 'Section I Use of English',
        'sentences': sentences, 'questions': questions,
    }


# ---------- 新题型（小标题对应） ----------
NEWTYPE_POOL = {
    'A': 'You are not alone',
    'B': 'Experience helps you grow',
    'C': 'Pave your own unique path',
    'D': 'Most of your fears are unreal',
    'E': 'Think about the present moment',
    'F': "Don't fear responsibility for your life",
    'G': 'There are many things to be grateful for',
}
NEWTYPE_POOL_CN = {
    'A': '你并非孤立无援',
    'B': '经历助你成长',
    'C': '走出属于自己的独特道路',
    'D': '大多数恐惧都是虚幻的',
    'E': '关注当下时刻',
    'F': '不要害怕对自己的人生负责',
    'G': '值得感恩的事很多',
}
NEWTYPE_ANSWERS = {41: 'D', 42: 'E', 43: 'G', 44: 'A', 45: 'C'}
NEWTYPE_EXPL = {
    41: '第三段首先指出，恐惧有用也有害；然后在此基础上进一步表明观点：恐惧并非真实，而只是我们丰富想象力的产物。可见，选项[D] Most of your fears are unreal为对本段内容的恰当概括，fears体现本段讨论对象，unreal则概括not real/...a product of thoughts you create...is a choice...just the product of our luxuriant imagination等内容。',
    42: '第四段首句给出建议：若面临被各种问题困扰的情形，那就努力关注当下。随后指出，为过去难过等于是在用你无法改变的事物破坏着你的现在。最后指出正确做法：珍视当下，享受周围的美好并留意面前的机会；幸福便是有意融入当下的心态。通观全段，作者主要观点为"关注当下"，[E]选项Think about the present moment即是对该段主旨的概括。',
    43: '第五段首先指出人们很容易会在困难时期感觉糟糕，忘记停下来欣赏自己已有的东西。随后提出正确的做法：选择微笑并珍视自己的生活。可见选项[G] There are many things to be grateful for应为该段小标题。',
    44: '第六段首句提出建议：你要记住你不是孤立无援。随后进一步阐释：如果你要努力做出改变，几乎每个人都会尊重你、愿意帮你，尤其是你最亲最近的人。然后给出建议——多交朋友。可见，选项[A] You are not alone与全段内容统一，更是对主旨句核心部分的重现。',
    45: '第七段首两句驳斥人们"觉得很难相信自己观点，转而从外部寻求客观性"这一做法：这是在贬低自己的见解，是在表明你没有能力经营自己的人生。随后正面提出建议：你应该相信自己的决定，把握自己的人生。由此可见，[C]选项Pave your own unique path为对本段主要观点的概括，与段落中managing your own life、believe in yourself、think your own thoughts, have your own values、make your own choices相契合。',
}
NEWTYPE_BODY = [
    "Unfortunately, life is not a bed of roses.",
    "We are going through life facing sad experiences.",
    "Moreover, we are grieving various kinds of loss: a friendship, a romantic relationship or a house.",
    "Hard times may hold you down at what usually seems like the most inopportune time, but you should remember that they won't last forever.",
    "When our time of mourning is over, we press forward, stronger with a greater understanding and respect for life.",
    "Furthermore, these losses make us mature and eventually move us toward future opportunities for growth and happiness.",
    "I want to share these old truths I've learned along the way.",
    "Fear is both useful and harmful.",
    "This normal human reaction is used to protect us by signaling danger and preparing us to deal with it.",
    "Unfortunately, people create inner barriers with a help of exaggerating fears.",
    "My favorite actor Will Smith once said, \"Fear is not real.",
    "It is a product of thoughts you create.",
    "Do not misunderstand me.",
    "Danger is very real.",
    "But fear is a choice.\"",
    "I do completely agree that fears are just the product of our luxuriant imagination.",
    "If you are surrounded by problems and cannot stop thinking about the past, try to focus on the present moment.",
    "Many of us are weighed down by the past or anxious about the future.",
    "You may feel guilt over your past, but you are poisoning the present with the things and circumstances you cannot change.",
    "Value the present moment and remember how fortunate you are to be alive.",
    "Enjoy the beauty of the world around and keep the eyes open to see the possibilities before you.",
    "Happiness is not a point of future and not a moment from the past, but a mindset that can be designed into the present.",
    "Sometimes it is easy to feel bad because you are going through tough times.",
    "You can be easily caught up by life problems that you forget to pause and appreciate the things you have.",
    "Only strong people prefer to smile and value their life instead of crying and complaining about something.",
    "No matter how isolated you might feel and how serious the situation is, you should always remember that you are not alone.",
    "Try to keep in mind that almost everyone respects and wants to help you if you are trying to make a good change in your life, especially your dearest and nearest people.",
    "You may have a circle of friends who provide constant good humor, help and companionship.",
    "If you have no friends or relatives, try to participate in several online communities, full of people who are always willing to share advice and encouragement.",
    "Today many people find it difficult to trust their own opinion and seek balance by gaining objectivity from external sources.",
    "This way you devalue your opinion and show that you are incapable of managing your own life.",
    "When you are struggling to achieve something important you should believe in yourself and be sure that your decision is the best.",
    "You live in your skin, think your own thoughts, have your own values and make your own choices.",
]
NEWTYPE_CN = [
    "很不幸，人生并非事事如意。",
    "我们在生活中都会遇到一些令人悲伤的经历。",
    "此外，我们要为各种失去而伤心：失去一段友谊，失去一段爱情，或是失去一套房子。",
    "困难时刻似乎总在你最不顺心的时候令你倍感压抑，但你应该记住，它们不会永远持续。",
    "悲伤过后，我们努力前行，（此时因为）有了对生活更深刻的理解和更多的尊重而变得更加坚强。",
    "此外，这些失去让我们变得成熟，最终让我们获得未来成长和幸福的机会。",
    "在此，我想分享我一路走来所领悟到的一些古老真理。",
    "恐惧既有用也有害。",
    "这一正常的人体反应通过发出危险信号让我们做好应对准备的方式来保护我们。",
    "遗憾的是，人们往往会夸大恐惧，从而制造内心障碍。",
    "我最喜爱的演员威尔·史密斯曾经说过，\u201c恐惧并非真实存在。",
    "它是你自己创造出来的一种思维产物。",
    "不要误解我的意思。",
    "危险是真实的。",
    "但是恐惧是可选的。\u201d",
    "我的确完全同意\u201c恐惧只是我们丰富想象力的产物\u201d这一观点。",
    "如果你被一堆问题所困，并且无法停止回想过去，那就努力去关注当下。",
    "我们中许多人会被过去所累，或是为未来焦虑。",
    "你也许为你的过去感到内疚，但你这是在用你无法改变的事物和环境破坏着你的现在。",
    "珍惜当下时刻并记住自己能活着是多么幸运。",
    "享受周围世界的美好，并睁大眼睛留意面前的机会。",
    "快乐不是未来的某一点，也不是过去的某一刻，而是一种有意融入当下的心态。",
    "有时候你很容易会因为正在经历困难时期而感觉糟糕。",
    "你很容易被生活中的问题所困，以至于忘了停下来欣赏自己已有的东西。",
    "只有坚强的人才会选择微笑并珍视自己的生活，而不会选择哭泣和抱怨。",
    "不管你感觉多么孤独无助，也不管情况多么严重，你要永远牢记，你并非孤立无援。",
    "请记住，如果你努力在生活中作出积极的改变，那么几乎所有的人都会尊重你并且愿意帮助你，尤其是你至亲至近的人。",
    "你身边可能有一个朋友圈子，给你持续提供好心情，帮助以及陪伴。",
    "假如你没有朋友或亲人，那么努力加入几个在线社区吧，那里有许多人总是乐意分享建议和鼓励。",
    "如今很多人觉得很难信任自己的观点，并通过从外部来源获得客观性来寻求平衡。",
    "这样做贬低了你自己的见解，显示你没有能力经营自己的人生。",
    "当你奋力获取某一重要之物时，你应该相信自己，确信自己的决定是最好的。",
    "你栖息在自己的身体里，思考着你自己的想法，有你自己的价值观并做出你自己的选择。",
]
assert len(NEWTYPE_BODY) == len(NEWTYPE_CN) == 33


def build_newtype():
    sentences = []
    for i, (en, cn) in enumerate(zip(NEWTYPE_BODY, NEWTYPE_CN), 1):
        sentences.append({
            'id': f'2015_newtype_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    questions = []
    for n in range(41, 46):
        questions.append({
            'id': f'2015_newtype_q{n}', 'number': n, 'qtype': '小标题',
            'stem': f'第 {n} 段：选择最合适的小标题填入空白', 'stem_cn': '',
            'options': {}, 'options_cn': {},
            'answer': NEWTYPE_ANSWERS[n],
            'explanation': NEWTYPE_EXPL[n],
            'related_sentences': [f'2015_newtype_s{i:02d}' for i in range(1, len(NEWTYPE_BODY) + 1)],
        })
    return {
        'id': '2015_newtype', 'type': 'newtype',
        'title': 'Old Truths to Help You Overcome Tough Times',
        'topic': '新题型（小标题对应）：帮助度过艰难时期的五个古老真理。',
        'source': 'Section II Part B',
        'pool': NEWTYPE_POOL, 'pool_cn': NEWTYPE_POOL_CN,
        'sentences': sentences, 'questions': questions,
    }


# ---------- 翻译 ----------
TRANSLATION_BODY = [
    "Think about driving a route that's very familiar.",
    "It could be your commute to work, a trip into town or the way home.",
    "Whichever it is, you know every twist and turn like the back of your hand.",
    "On these sorts of trips it's easy to lose concentration on the driving and pay little attention to the passing scenery.",
    "The consequence is that you perceive that the trip has taken less time than it actually has.",
    "This is the well-travelled road effect: People tend to underestimate the time it takes to travel a familiar route.",
    "The effect is caused by the way we allocate our attention.",
    "When we travel down a well-known route, because we don't have to concentrate much, time seems to flow more quickly.",
    "And afterwards, when we come to think back on it, we can't remember the journey well because we didn't pay much attention to it.",
    "So we assume it was shorter.",
]
TRANSLATION_CN = [
    "试想开车走一条非常熟悉的路。",
    "可以是上下班、进城或是回家的路。",
    "不管是哪条路，你对每一处曲曲弯弯都了如指掌。",
    "在这种路上，很容易不专注于驾驶，很少注意沿途的景色。",
    "结果你就觉得旅途所花的时间比实际的要短。",
    "这就是熟路效应：人们走熟路时往往会低估所需的时间。",
    "这种效应是由我们分配自己注意力的方式造成的。",
    "我们走很熟的路时，由于不必非常专注，时间似乎就过得快些。",
    "之后，我们回想起这段旅程时，由于当时没怎么注意，所以记得不很清楚。",
    "这样，我们就觉得时间短了。",
]
TRANSLATION_REF = '试想开车走一条非常熟悉的路。可以是上下班、进城或是回家的路。不管是哪条路，你对每一处曲曲弯弯都了如指掌。在这种路上，很容易不专注于驾驶，很少注意沿途的景色。结果你就觉得旅途所花的时间比实际的要短。这就是熟路效应：人们走熟路时往往会低估所需的时间。这种效应是由我们分配自己注意力的方式造成的。我们走很熟的路时，由于不必非常专注，时间似乎就过得快些。之后，我们回想起这段旅程时，由于当时没怎么注意，所以记得不很清楚。这样，我们就觉得时间短了。'
assert len(TRANSLATION_BODY) == len(TRANSLATION_CN) == 10


def build_translation():
    sentences = []
    for i, (en, cn) in enumerate(zip(TRANSLATION_BODY, TRANSLATION_CN), 1):
        sentences.append({
            'id': f'2015_translation_s{i:02d}', 'para': 1, 'en': en, 'cn': cn, 'words': [],
        })
    return {
        'id': '2015_translation', 'type': 'translation',
        'title': 'The Well-travelled Road Effect',
        'topic': '翻译：熟路效应——人们走熟路时往往会低估所需的时间，及其成因。',
        'source': 'Section III Translation',
        'ref_cn': TRANSLATION_REF,
        'sentences': sentences, 'questions': [],
    }


# ---------- 作文 ----------
WRITING_A = {
    'id': '2015_writinga', 'type': 'writing_a',
    'title': 'Part A 应用文：招募夏令营的志愿者',
    'topic': '小作文：写一份通知，简要介绍高中夏令营活动并号召大家报名担任志愿者。',
    'source': 'Section IV Writing Part A',
    'sample_en': """Recruitment Announcement
We are looking for some volunteers for the summer camp for high school students. The summer camp is organized to facilitate high school students' academic learning and more importantly cultivate their cooperation ability and practical skills through activities including but not limited to reading salon and business-starting competition.
Volunteers are required to help organize activities and cope with daily affairs during the summer camp. Ideal candidates should be patient, active, warm-hearted and responsible. Having relevant experience is preferred. Anyone interested please contact us by students' union@abcuniversity.edu.cn or reach us at 12345678.
Students' Union""",
    'sample_cn': """招募启事
我们正在为高中夏令营招募几位志愿者。组织夏令营是为了通过活动促进高中生的学业学习，更重要的是培养他们的合作能力和实践技能。这些活动包括但不局限于读书沙龙和创业大赛。
要求志愿者帮助组织活动，并处理夏令营中的日常事务。理想的人选应该有耐心、积极、热心并且负责。有相关经验更佳。感兴趣者请通过students' union@abcuniversity.edu.cn联系我们，或者拨打电话12345678联系我们。
学生会""",
    'questions': [],
}

WRITING_B = {
    'id': '2015_writingb', 'type': 'writing_b',
    'title': 'Part B 大作文：春节假期花销比例饼图',
    'topic': '大作文：根据饼图写一篇约150词的短文，解读春节假期各项花销比例并发表评论。',
    'source': 'Section IV Writing Part B',
    'chart_img': 'img/2015_writingb_chart.png',
    'sample_en': """The chart reflects the Spring Festival spending types and their respective proportions. Chinese people's money is mainly used for three purposes during the Spring Festival: traveling, New Year's gift giving and having dinners with friends or relatives. They account for 80% of total spending.
Most spending is used to maintain or facilitate interpersonal relationship. This finding is not strange, since the Spring Festival is a Chinese traditional festival for family reunion. Developing relationship is beneficial and necessary for a person's fulfillment and investing on people we love is sweet and happy.
However, we should not go to extremes. In China, there are many people fond of appearing extraordinary and hating to be known as weaker and poorer. They use handsome money to blindly pursue pride. Such intention causes huge waste of money and imposes heavy economic burden on people involved. The pride gotten by squandering money is transient and can only be a topic for gossip soon forgotten by others. Therefore, we should think rationally before opening our purses. We should remember it is happiness that is the main concern.""",
    'sample_cn': """表格体现了春节开销的类型和各自的比例。在春节期间中国人的钱主要有三种用途：交通、送新年礼物和与朋友、亲人共进晚餐。它们占了花费总额的80%。
绝大多数开支被用来维护和促进入际关系。鉴于春节是中国传统的家庭团圆的节日，这个发现不奇怪。发展人际关系对一个人的幸福是有益和必需的，在我们爱的人身上投资是甜蜜而幸福的。
但是，我们不能走向极端。在中国，很多人喜欢显得不凡，讨厌被认为比别人弱或穷。他们花大量的钱去盲目追求面子。这样的意图造成了金钱的大量浪费，给相关人带来了沉重的经济压力。靠挥霍钱获得的面子是短暂的，只能作为一个八卦话题，很快被其他人遗忘。因此，我们在打开钱包前，应该理性思考。我们应该记住幸福才是我们关注的重点。""",
    'questions': [],
}

EXTRA = [build_cloze(), build_newtype(), build_translation(), WRITING_A, WRITING_B]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data = {'year': 2015, 'articles': EXTRA}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已写入 {OUT}')
    for a in EXTRA:
        print(f"  {a['id']}: {len(a.get('sentences', []))} 句 / {len(a.get('questions', []))} 题")


if __name__ == '__main__':
    main()
