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
    "para2_env": [
        [
            [
                "The change in the chart",
                "t"
            ],
            [
                " has been building",
                "p"
            ],
            [
                " for years",
                ""
            ],
            [
                ".",
                ""
            ]
        ],
        [
            [
                "People today",
                "t"
            ],
            [
                " are far more aware of",
                "p"
            ],
            [
                " environmental problems",
                "o"
            ],
            [
                " than they were in {{time1}}",
                ""
            ],
            [
                ", and {{topic}} is what that awareness has produced",
                ""
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
