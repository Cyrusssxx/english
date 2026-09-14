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
S = {
    "chart_static": [
        [
            [
                "The {{chart}} chart",
                "t"
            ],
            [
                " shows",
                "p"
            ],
            [
                " how {{topic}} is distributed among the categories",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{item1}}",
                "t"
            ],
            [
                " takes",
                "p"
            ],
            [
                " the largest share",
                "o"
            ],
            [
                ", at {{percent1}}",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{item2}} and {{item3}}",
                "t"
            ],
            [
                " come next",
                "p"
            ],
            [
                ", at {{percent2}} and {{percent3}}",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "By contrast",
                "trans"
            ],
            [
                ", ",
                ""
            ],
            [
                "{{item4}} and {{item5}}",
                "t"
            ],
            [
                " account for",
                "p"
            ],
            [
                " only {{percent4}} and {{percent5}}",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "chart_dynamic": [
        [
            [
                "The {{chart}} chart",
                "t"
            ],
            [
                " tracks",
                "p"
            ],
            [
                " how {{topic}} changed from {{time1}} to {{time2}}",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{item1}}",
                "t"
            ],
            [
                " climbed",
                "p"
            ],
            [
                " from {{num1}} to {{num2}}",
                "o"
            ],
            [
                ", while ",
                "trans"
            ],
            [
                "{{item2}}",
                "t"
            ],
            [
                " rose more slowly",
                "p"
            ],
            [
                ", from {{num3}} to {{num4}}",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "By contrast",
                "trans"
            ],
            [
                ", ",
                ""
            ],
            [
                "{{item3}}",
                "t"
            ],
            [
                " fell",
                "p"
            ],
            [
                " from {{num5}} to {{num6}}",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_economy": [
        [
            [
                "The trend in the chart",
                "t"
            ],
            [
                " is closely tied to",
                "p"
            ],
            [
                " how people live and spend today",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{item1}}",
                "t"
            ],
            [
                " rose from {{num1}} in {{time1}} to {{num2}} in {{time2}}",
                "p"
            ],
            [
                ", and that change did not happen by itself",
                ""
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_campus": [
        [
            [
                "Behind the numbers in the chart",
                ""
            ],
            [
                " lies",
                "p"
            ],
            [
                " a change in how students spend their time",
                "t"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Habits built at this stage",
                "t"
            ],
            [
                " shape",
                "p"
            ],
            [
                " how young people take responsibility later",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{topic}}",
                "t"
            ],
            [
                " is",
                "p"
            ],
            [
                " one of the clearest examples",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_campus_neg": [
        [
            [
                "Behind the numbers in the chart",
                ""
            ],
            [
                " lies",
                "p"
            ],
            [
                " a problem that deserves attention",
                "t"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Habits formed at this stage",
                "t"
            ],
            [
                " are hard to change later",
                "p"
            ],
            [
                ", and the wrong ones carry a lasting cost",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "{{topic}}",
                "t"
            ],
            [
                " shows",
                "p"
            ],
            [
                " how easily that cost can build up",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_social": [
        [
            [
                "The change in the chart",
                "t"
            ],
            [
                " reflects",
                "p"
            ],
            [
                " a broader shift in how people live and work",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Once basic needs are met",
                ""
            ],
            [
                ", people",
                "t"
            ],
            [
                " care more about",
                "p"
            ],
            [
                " how they spend their time",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_sports": [
        [
            [
                "The figures",
                "t"
            ],
            [
                " are less about",
                "p"
            ],
            [
                " sport itself",
                "o"
            ],
            [
                " than about how people now look after themselves",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Long working hours",
                "t"
            ],
            [
                " have turned",
                "p"
            ],
            [
                " health",
                "o"
            ],
            [
                " into something to plan for",
                ""
            ],
            [
                ", and {{topic}} is the easiest way to do that",
                ""
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para2_culture": [
        [
            [
                "Traditional culture",
                "t"
            ],
            [
                " does not survive by",
                "p"
            ],
            [
                " being preserved in a museum",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "It",
                "t"
            ],
            [
                " survives",
                "p"
            ],
            [
                " when people find new ways to pass it on",
                "o"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "The growth shown in the chart",
                "t"
            ],
            [
                " is",
                "p"
            ],
            [
                " that process at work",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para3_positive": [
        [
            [
                "If the trend in the chart is to continue",
                ""
            ],
            [
                ", more than one side",
                "t"
            ],
            [
                " has to act",
                "p"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Each of them",
                "t"
            ],
            [
                " has",
                "p"
            ],
            [
                " a different job to do",
                "o"
            ],
            [
                ", and none can do it alone",
                ""
            ],
            [
                ".",
                ""
            ]
        ]
    ],
    "para3_negative": [
        [
            [
                "If nothing is done",
                ""
            ],
            [
                ", the problem shown in the chart",
                "t"
            ],
            [
                " will only get worse",
                "p"
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "Any serious response",
                "t"
            ],
            [
                " has to come from",
                "p"
            ],
            [
                " several directions at once",
                "o"
            ],
            [
                ".",
                ""
            ]
        ]
    ]
}


P = {
    "chart_static": [
        [
            "shows how … is distributed",
            "显示…的分布情况"
        ],
        [
            "takes the largest share",
            "占据最大份额"
        ],
        [
            "come next",
            "紧随其后"
        ],
        [
            "account for only",
            "仅占"
        ],
        [
            "are fairly evenly matched",
            "占比相差不大"
        ],
        [
            "is concentrated in",
            "集中在…"
        ]
    ],
    "chart_dynamic": [
        [
            "tracks how … changed",
            "记录…的变化"
        ],
        [
            "a steady climb",
            "稳步上升"
        ],
        [
            "over the same period",
            "同一时期"
        ],
        [
            "held steady at",
            "稳定在"
        ],
        [
            "more than doubled",
            "翻了一倍多"
        ],
        [
            "went the other way",
            "走势相反"
        ]
    ],
    "para2_economy": [
        [
            "is closely tied to",
            "与…密切相关"
        ],
        [
            "moved from a luxury to an everyday necessity",
            "从奢侈品变成日常必需品"
        ],
        [
            "within reach of ordinary families",
            "普通家庭负担得起"
        ],
        [
            "cut the time and cost of",
            "降低…的时间和成本"
        ],
        [
            "a passing fashion",
            "一时风尚"
        ]
    ],
    "para2_campus": [
        [
            "Behind the numbers in the chart lies …",
            "数字背后是…"
        ],
        [
            "Habits built at this stage",
            "这个阶段养成的习惯"
        ],
        [
            "shape the way sb do sth",
            "影响某人做事的方式"
        ],
        [
            "have a part to play",
            "需要参与、有作用"
        ],
        [
            "crowd out",
            "挤占"
        ]
    ],
    "para2_social": [
        [
            "a broader shift in how people live and work",
            "生活与工作方式的更大转变"
        ],
        [
            "the time they can call their own",
            "属于自己的时间"
        ],
        [
            "matter as much as",
            "和…一样重要"
        ],
        [
            "works differently",
            "运作逻辑已经不同"
        ],
        [
            "a change in expectations",
            "期望值的变化"
        ]
    ],
    "para2_sports": [
        [
            "are less about … than about …",
            "与其说关于…不如说关于…"
        ],
        [
            "look after themselves",
            "照顾自己的身体"
        ],
        [
            "a practical need rather than a hobby",
            "是实际需要而非爱好"
        ],
        [
            "stay motivated",
            "保持动力"
        ],
        [
            "the gap is widening",
            "差距在扩大"
        ]
    ],
    "para2_culture": [
        [
            "being preserved in a museum",
            "被供在博物馆里"
        ],
        [
            "find new ways to pass it on",
            "找到新的传递方式"
        ],
        [
            "bring … closer to ordinary life",
            "把…拉近日常生活"
        ],
        [
            "take part in",
            "参与其中"
        ],
        [
            "is being used rather than only admired",
            "在被使用而不只是被欣赏"
        ]
    ],
    "para3_positive": [
        [
            "more than one side has to act",
            "需要多方行动"
        ],
        [
            "has a different job to do",
            "各司其职"
        ],
        [
            "none can do it alone",
            "单靠一方做不到"
        ],
        [
            "is not limited to those who can pay",
            "不只属于付得起钱的人"
        ],
        [
            "set the tone",
            "带动风气、定下基调"
        ],
        [
            "rather than follow the crowd",
            "而不是随大流"
        ]
    ],
    "para3_negative": [
        [
            "will only get worse",
            "只会更严重"
        ],
        [
            "from several directions at once",
            "多个方向同时发力"
        ],
        [
            "before the habit takes hold",
            "在习惯养成之前"
        ],
        [
            "rather than treat them as scare stories",
            "而不是当成吓人的故事"
        ],
        [
            "makes the public numb instead of alert",
            "让公众麻木而非警觉"
        ]
    ]
}

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
