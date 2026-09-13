# -*- coding: utf-8 -*-
'''给 writing_templates.json 加三类数据（可重复执行，幂等覆盖）：
1) en_struct / negative_struct：模板正文逐句主干标注（片段拼接必须与原句完全一致，脚本内断言）
   role: t=主语 p=谓语 o=宾语/表 lead=从句引导 trans=转折/对比 caus=因果 ''=不着色
2) phrases：每张模板卡的「✨ 精句」词组（英中对照）
'''
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

FP = 'pwa/data/writing_templates.json'


def split_en(t):
    parts = re.findall(r'[^.!?]+[.!?]+["\')\]]*\s*|[^.!?]+$', t or '')
    return [p.strip() for p in parts if p.strip()]


def norm(st):
    '''归一化片段：["text"] → ["text", ""]（漏写 role 的兜底为不着色）'''
    out = []
    for x in st:
        if isinstance(x, str):
            x = [x]
        if len(x) == 1:
            x = [x[0], '']
        out.append(x)
    return out


def check(sec_id, sents, structs):
    assert len(sents) == len(structs), '%s: 句数 %d != 标注 %d' % (sec_id, len(sents), len(structs))
    for i, (s, st) in enumerate(zip(sents, structs)):
        st = norm(st)
        structs[i] = st
        cat = ''.join(x[0] for x in st)
        assert cat == s, '%s S%d 拼接不一致:\n  原句: %r\n  拼接: %r' % (sec_id, i + 1, s, cat)
        for x in st:
            assert x[1] in ('t', 'p', 'o', 'lead', 'trans', 'caus', ''), '%s S%d role=%r' % (sec_id, i + 1, x[1])


# ===== chart_static 静态图表第一段 =====
S = {}
S['chart_static'] = [
    [["The {{chart}} chart", "t"], [" presents", "p"], [" an uneven distribution", "o"],
     [" among the categories associated with {{题目相关词}}", ""], ["."]],
    [["{{事物1}}", "t"], [" accounts for", "p"], [" the largest share", "o"], [", at {{百分比1}}", ""], ["."]],
    [["{{事物2}} and {{事物3}}", "t"], [" form", "p"], [" the middle group", "o"],
     [", representing {{百分比2}} and {{百分比3}}, respectively", ""], ["."]],
    [["In contrast", "trans"], [", ", ""], ["{{事物4}} and {{事物5}}", "t"], [" make up", "p"],
     [" relatively small proportions of {{百分比4}} and {{百分比5}}", ""], ["."]],
]
P = {}
P['chart_static'] = [
    ["presents an uneven distribution", "呈现出不均匀的分布"],
    ["associated with", "与…相关的"],
    ["accounts for the largest share", "所占比例最大"],
    ["at 54.6%", "达到某比例（at + 数字）"],
    ["form the middle group", "处于中间位置"],
    ["respectively", "分别地（对应前面两个数字）"],
    ["make up relatively small proportions", "占比较小"],
    ["In contrast", "相比之下（引出对比）"],
]

S['chart_dynamic'] = [
    [["The line chart", "t"], [" shows", "p"], [" that", "lead"],
     [" the items associated with {{题目相关词}}", "t"], [" did not move in a uniform direction", "p"],
     [" during the periods presented", ""], ["."]],
    [["{{事物1}}", "t"], [" climbed", "p"], [" from {{数字1}} in {{时间1}} to {{数字2}} in {{时间2}}", ""],
     [", while", "trans"], [" {{事物2}}", "t"], [" rose", "p"],
     [" from {{数字3}} in {{时间3}} to {{数字4}} in {{时间4}}", ""], ["."]],
    [["By contrast", "trans"], [", ", ""], ["{{事物3}}", "t"], [" fell", "p"],
     [" from {{数字5}} in {{时间5}} to {{数字6}} in {{时间6}}", ""], ["."]],
]
P['chart_dynamic'] = [
    ["shows that", "表明（引出宾语从句）"],
    ["associated with", "与…相关的"],
    ["did not move in a uniform direction", "变化方向并不一致（同向上升时改写）"],
    ["during the periods presented", "在所示时期内"],
    ["climbed from … to …", "从…攀升至…"],
    ["rose from … to …", "从…上升至…"],
    ["over the same span", "在同一时期"],
    ["while", "而（一句内对比两事物）"],
    ["By contrast", "相比之下（另起对比）"],
    ["the pace of growth differed sharply", "增速差异显著"],
]

S['para2_economy'] = [
    [["Growing public attention to {{题目相关词}}", "t"], [" stems from", "p"],
     [" its ability to meet practical needs in everyday life", "o"], ["."]],
    [["Undoubtedly", ""], [", the country's rapid economic growth", "t"], [" has laid", "p"],
     [" a solid material foundation", "o"], [" for the emergence of {{题目相关词}}", ""], ["."]],
    [["As", "lead"], [" the pace of life accelerates", ""], [", individuals", "t"], [" attach", "p"],
     [" greater importance to convenience and efficiency", "o"],
     [" and become increasingly willing to embrace new ways of living", "p"], ["."]],
    [["Consequently", "caus"], [", ", ""], ["{{题目相关词}}", "t"],
     [" has gradually become integrated into", "p"], [" everyday life", "o"], [", while", "trans"],
     [" its practical value", "t"], [" has gained", "p"], [" wider recognition", "o"], ["."]],
    [["Seen in this light", ""], [", the development of {{题目相关词}}", "t"],
     [" is no coincidence but a natural consequence of broader changes in social life", "p"], ["."]],
]
P['para2_economy'] = [
    ["Growing public attention to …", "公众对…日益关注"],
    ["stems from", "源于"],
    ["meet practical needs", "满足实际需求"],
    ["lay a solid material foundation for", "为…奠定坚实的物质基础"],
    ["the emergence of …", "…的出现"],
    ["as the pace of life accelerates", "随着生活节奏加快"],
    ["attach greater importance to", "更加重视"],
    ["become integrated into everyday life", "融入日常生活"],
    ["gain wider recognition", "得到更广泛认可"],
    ["Seen in this light", "由此观之（总结句开头）"],
]

S['para2_campus'] = [
    [["The influence of {{题目相关词}}", "t"], [" is not confined to", "p"], [" a single action", "o"],
     ["; rather", "trans"], [", it", "t"], [" continues to shape", "p"],
     [" the way individuals handle everyday responsibilities", "o"], ["."]],
    [["{{题目相关词}}", "t"], [" can enable", "p"],
     [" individuals to approach routine tasks with greater maturity", "o"],
     [", preventing them from giving up too readily in the face of temporary difficulties", ""], ["."]],
    [["In this process", ""], [", individuals", "t"], [" gradually become", "p"],
     [" less dependent on external reminders", "o"], [" and begin to take responsibility for their own choices", "p"],
     ["."]],
    [["Ultimately", ""], [", {{题目相关词}}", "t"], [" can not only improve", "p"], [" individuals' present conduct", "o"],
     [" but also strengthen", "p"], [" their capacity for self-management", "o"], [", thereby", "caus"],
     [" laying a solid foundation for their future growth", ""], ["."]],
]
S['para2_campus_neg'] = [
    [["The harmful influence of {{题目相关词}}", "t"], [" is not confined to", "p"], [" a single action", "o"],
     ["; rather", "trans"], [", it", "t"], [" can continue to disrupt", "p"],
     [" the way individuals handle everyday responsibilities", "o"], ["."]],
    [["{{题目相关词}}", "t"], [" can cause", "p"],
     [" individuals to approach routine tasks with less commitment", "o"],
     [", making them more likely to give up", ""], [" when", "lead"], [" temporary difficulties arise", ""], ["."]],
    [["In this process", ""], [", individuals", "t"], [" may become", "p"],
     [" increasingly dependent on external reminders and less willing to take responsibility for their own choices", "o"],
     ["."]],
    [["Ultimately", ""], [", {{题目相关词}}", "t"], [" can not only undermine", "p"], [" individuals' present conduct", "o"],
     [" but also weaken", "p"], [" their capacity for self-management", "o"], [", thereby", "caus"],
     [" creating a persistent obstacle to future growth", ""], ["."]],
]
P['para2_campus'] = [
    ["is not confined to", "不局限于"],
    ["shape the way sb handle …", "塑造某人处理…的方式"],
    ["enable sb to do sth", "使某人能够做…"],
    ["approach routine tasks with greater maturity", "更成熟地处理日常事务"],
    ["prevent sb from giving up", "防止某人放弃"],
    ["in the face of temporary difficulties", "面对暂时的困难"],
    ["take responsibility for", "为…承担责任"],
    ["not only … but also …", "不仅…而且…（句子加长利器）"],
    ["strengthen the capacity for self-management", "增强自我管理能力"],
    ["lay a solid foundation for future growth", "为未来成长打下坚实基础"],
]

S['para2_env'] = [
    [["Changes reflected in {{题目相关词}}", "t"], [" are closely linked to", "p"],
     [" rising public awareness of environmental protection and increasingly favorable conditions for environmental action", "o"],
     ["."]],
    [["Improved environmental infrastructure", "t"], [" makes it easier", "p"],
     [" for people to participate in environmental protection", "o"], [", while", "trans"],
     [" a wider range of environmental practices", "t"], [" enables", "p"],
     [" different groups to make choices suited to their own circumstances", "o"], ["."]],
    [["As", "lead"], [" environmental protection becomes increasingly integrated into everyday life", ""],
     [", the number of people willing to take part in related initiatives", "t"], [" will continue to grow", "p"], ["."]],
    [["For this reason", "caus"], [", ", ""], ["{{题目相关词}}", "t"], [" not only reflects", "p"],
     [" the continued advancement of ecological conservation", "o"], [" but also demonstrates", "p"],
     [" the growing acceptance of green living", "o"], ["."]],
]
P['para2_env'] = [
    ["be closely linked to", "与…密切相关"],
    ["rising public awareness of …", "公众…意识不断增强"],
    ["increasingly favorable conditions", "日趋有利的条件"],
    ["make it easier for sb to do", "让人们更容易做…"],
    ["participate in", "参与"],
    ["a wider range of", "更加多样的"],
    ["suited to their own circumstances", "适合自身情况的"],
    ["be integrated into everyday life", "融入日常生活"],
    ["take part in related initiatives", "参与相关行动"],
    ["demonstrate the growing acceptance of …", "体现…日益被接受"],
]

S['para2_sports'] = [
    [["Changes reflected in {{题目相关词}}", "t"], [" are closely linked to", "p"],
     [" rising public awareness of personal health and increasingly favorable conditions for physical exercise", "o"],
     ["."]],
    [["Improved sports infrastructure", "t"], [" makes it easier", "p"],
     [" for people to participate in physical exercise", "o"], [", while", "trans"],
     [" a wider range of exercise methods", "t"], [" enables", "p"],
     [" different groups to make choices suited to their own circumstances", "o"], ["."]],
    [["As", "lead"], [" physical exercise becomes increasingly integrated into everyday life", ""],
     [", the number of people willing to take part in related activities", "t"], [" will continue to grow", "p"], ["."]],
    [["For this reason", "caus"], [", ", ""], ["{{题目相关词}}", "t"], [" not only reflects", "p"],
     [" the continued advancement of national fitness", "o"], [" but also demonstrates", "p"],
     [" the growing acceptance of healthy living", "o"], ["."]],
]
P['para2_sports'] = [
    ["be closely linked to", "与…密切相关"],
    ["rising public awareness of personal health", "公众健康意识不断增强"],
    ["improved sports infrastructure", "更完善的体育设施"],
    ["participate in physical exercise", "参加体育锻炼"],
    ["a wider range of exercise methods", "更多样的锻炼方式"],
    ["the number of … will continue to grow", "…的数量将持续增长"],
    ["the continued advancement of national fitness", "全民健身的持续推进"],
    ["the growing acceptance of healthy living", "健康生活方式日益被接受"],
]

S['para2_culture'] = [
    [["Traditional culture", "t"], [" cannot be effectively conveyed", "p"],
     [" through the one-way delivery of content alone", ""], ["; its modes of expression", "t"],
     [" must also be adjusted", "p"], [" in response to real-world feedback", ""], ["."]],
    [["{{题目相关词}}", "t"], [" can establish", "p"],
     [" a channel of communication between traditional culture and the public", "o"],
     [", allowing cultural content to be explained with greater clarity", ""], ["."]],
    [["Public participation", "t"], [" can also give rise to", "p"], [" new forms of cultural expression", "o"],
     [", enabling traditional culture to adapt to social change", ""], [" while", "trans"],
     [" preserving its core values", ""], ["."]],
    [["Seen from this perspective", ""], [", ", ""], ["{{题目相关词}}", "t"], [" not only enhances", "p"],
     [" the effectiveness of cultural transmission", "o"], [" but also strengthens", "p"],
     [" traditional culture's capacity to remain relevant to contemporary life", "o"], ["."]],
]
P['para2_culture'] = [
    ["be effectively conveyed through", "通过…得到有效传达"],
    ["the one-way delivery of content", "单向的内容输出"],
    ["in response to real-world feedback", "响应现实反馈"],
    ["establish a channel of communication between A and B", "在 A 与 B 之间建立沟通渠道"],
    ["give rise to", "催生、带来"],
    ["adapt to social change", "适应社会变迁"],
    ["preserve its core values", "保留其核心价值"],
    ["enhance the effectiveness of cultural transmission", "提升文化传播效果"],
    ["remain relevant to contemporary life", "与当代生活保持相关"],
]

S['para3_positive'] = [
    [["For {{题目相关词}} to continue exerting a positive influence on personal growth", ""],
     [", concerted efforts from all sectors of society", "t"], [" are essential", "p"], ["."]],
    [["Relevant authorities", "t"], [" should provide", "p"], [" the necessary support", "o"],
     [" and create", "p"], [" favorable conditions", "o"], [" under which", "lead"],
     [" {{题目相关词}} can play a constructive role", ""], ["."]],
    [["Media organizations", "t"], [" should present", "p"], [" the practical value of {{题目相关词}}", "o"],
     [" objectively", ""], [", thereby", "caus"],
     [" helping the public develop a sound understanding of {{题目相关词}}", ""], ["."]],
    [["Individuals", "t"], [" should also make", "p"], [" well-informed choices", "o"],
     [" in light of their own circumstances", ""], [", ensuring", ""], [" that", "lead"],
     [" {{题目相关词}} genuinely contributes to their long-term development", ""], ["."]],
]
P['para3_positive'] = [
    ["For … to continue exerting a positive influence on …", "为了让…持续对…发挥积极作用"],
    ["concerted efforts from all sectors of society", "社会各方共同努力"],
    ["provide the necessary support", "提供必要支持"],
    ["create favorable conditions under which …", "创造良好条件让…"],
    ["play a constructive role", "发挥建设性作用"],
    ["present … objectively", "客观呈现…"],
    ["develop a sound understanding of", "形成正确认识"],
    ["make well-informed choices", "作出理性选择"],
    ["in light of their own circumstances", "结合自身情况"],
    ["contribute to long-term development", "有助于长远发展"],
]

S['para3_negative'] = [
    [["For the harmful effects of {{题目相关词}} on personal growth to be effectively contained", ""],
     [", concerted efforts across society", "t"], [" are essential", "p"], ["."]],
    [["Relevant authorities", "t"], [" should strengthen", "p"], [" regulatory oversight", "o"],
     [" and keep", "p"], [" {{题目相关词}} within clear and reasonable limits", "o"], ["."]],
    [["Media organizations", "t"], [" should present", "p"], [" the potential risks of {{题目相关词}}", "o"],
     [" objectively", ""], [", thereby", "caus"],
     [" helping the public develop a sound understanding of {{题目相关词}}", ""], ["."]],
    [["Individuals", "t"], [" should also remain", "p"], [" vigilant", "o"],
     [" in light of their own circumstances", ""], [" and guard against", "p"], [" any threat", "o"],
     [" that", "lead"], [" {{题目相关词}} may pose to their long-term development", ""], ["."]],
]
P['para3_negative'] = [
    ["the harmful effects of … on …", "…对…的有害影响"],
    ["be effectively contained", "得到有效遏制"],
    ["concerted efforts across society", "全社会共同努力"],
    ["strengthen regulatory oversight", "加强监管"],
    ["keep … within clear and reasonable limits", "把…控制在清晰合理的限度内"],
    ["present the potential risks objectively", "客观呈现潜在风险"],
    ["remain vigilant", "保持警惕"],
    ["guard against any threat … may pose to …", "防范…可能带来的任何威胁"],
]


def main():
    d = json.load(open(FP, encoding='utf-8'))
    for sec in d['sections']:
        sid = sec['id']
        sents = split_en(sec.get('en'))
        check(sid, sents, S[sid])
        sec['en_struct'] = S[sid]
        sec['phrases'] = P[sid]
        if sec.get('negative_en'):
            key = sid + '_neg'
            ns = split_en(sec['negative_en'])
            check(key, ns, S[key])
            sec['negative_struct'] = S[key]
    json.dump(d, open(FP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('已写入：结构标注 %d 卡 + 负面版 %d 个 + 精句 %d 卡' % (
        len(S), sum(1 for s in d['sections'] if s.get('negative_struct')),
        sum(1 for s in d['sections'] if s.get('phrases'))))


if __name__ == '__main__':
    main()
