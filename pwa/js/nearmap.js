/* 选项高频近义词 - 点亮图
 * 数据内联，零 fetch，离线可用，打开即读。交互同方法导图：点条目点亮（黄色），localStorage 持久化。
 * 词频来源：tools/_optfreq.py / _optfreq2.py 统计 36 年真题（英二 2007-2026 + 英一 2010-2025）阅读/完形/新题型选项文本。
 */
(function () {
  'use strict';

  var DATA = {
    maps: [
      {
        id: "near",
        title: "选项高频近义词",
        root: "选项高频近义词",
        rootColor: "#0d9488",
        intro: "36 年真题（英二 2007–2026 + 英一 2010–2025）阅读 / 完形 / 新题型【选项】里的高频词与短语，按意思相近成簇。词频 = 该词在选项文本里出现的次数。做选择时同簇词先想清各自侧重：如 reduce 是减少、decline 是下降、ease 是缓解。短语簇（连接·过渡 / 因果·由来）专治“选项看了半天不懂”——点条目可点亮标记，再点取消。",
        branches: [
          { name: "增长 · 提升", color: "#ef4444", children: [
            { name: "change 改变 · 61 次" },
            { name: "growth 增长 · 38 次" },
            { name: "development 发展 · 33 次" },
            { name: "improve 改善 · 31 次" },
            { name: "increase 增加 · 30 次" }
          ]},
          { name: "重要 · 关键", color: "#f59e0b", children: [
            { name: "important 重要的 · 25 次" },
            { name: "major 主要的 · 25 次" },
            { name: "critical 关键的 · 20 次" }
          ]},
          { name: "促进 · 增强", color: "#f97316", children: [
            { name: "promote 促进 · 17 次" },
            { name: "advance 推进 · 16 次" },
            { name: "boost 推动 · 14 次" },
            { name: "strengthen 加强 · 14 次" },
            { name: "enhance 增强 · 11 次" },
            { name: "facilitate 促进 · 5 次" }
          ]},
          { name: "减轻 · 缓解", color: "#10b981", children: [
            { name: "reduce 减少 · 30 次" },
            { name: "decline 下降 · 18 次" },
            { name: "lower 降低 · 15 次" },
            { name: "ease 缓解 · 11 次" },
            { name: "relieve 减轻 · 8 次" }
          ]},
          { name: "削弱 · 阻止", color: "#dc2626", children: [
            { name: "prevent 阻止 · 21 次" },
            { name: "weaken 削弱 · 8 次" },
            { name: "undermine 削弱 · 8 次" },
            { name: "hinder 阻碍 · 4 次" }
          ]},
          { name: "支持 · 帮助", color: "#84cc16", children: [
            { name: "help 帮助 · 42 次" },
            { name: "support 支持 · 33 次" },
            { name: "back 支持 · 24 次" },
            { name: "provide 提供 · 20 次" }
          ]},
          { name: "影响 · 效应", color: "#3b82f6", children: [
            { name: "influence 影响 · 34 次" },
            { name: "effect 效果 · 24 次" },
            { name: "impact 影响 · 20 次" }
          ]},
          { name: "原因 · 结果", color: "#8b5cf6", children: [
            { name: "lead 导致 · 55 次" },
            { name: "result 结果 · 50 次" },
            { name: "reason 原因 · 42 次" },
            { name: "because 因为 · 39 次" },
            { name: "cause 原因 · 26 次" },
            { name: "thus 因此 · 15 次" },
            { name: "therefore 因此 · 8 次" }
          ]},
          { name: "研究 · 结果", color: "#0ea5e9", children: [
            { name: "research 研究 · 66 次" },
            { name: "study 研究 · 35 次" },
            { name: "found 发现 · 24 次" },
            { name: "results 结果 · 22 次" }
          ]},
          { name: "商业 · 市场", color: "#ec4899", children: [
            { name: "business 商业 · 53 次" },
            { name: "companies 公司 · 45 次" },
            { name: "market 市场 · 42 次" },
            { name: "industry 行业 · 22 次" },
            { name: "firms 公司 · 19 次" }
          ]},
          { name: "政府 · 法律", color: "#14b8a6", children: [
            { name: "government 政府 · 54 次" },
            { name: "law 法律 · 44 次" },
            { name: "federal 联邦的 · 41 次" },
            { name: "legal 法律的 · 30 次" }
          ]},
          { name: "教育 · 学校", color: "#a855f7", children: [
            { name: "education 教育 · 67 次" },
            { name: "students 学生 · 50 次" },
            { name: "degree 学位 · 27 次" },
            { name: "school 学校 · 25 次" },
            { name: "university 大学 · 25 次" }
          ]},
          { name: "工作 · 就业", color: "#0891b2", children: [
            { name: "work 工作 · 75 次" },
            { name: "jobs 工作 · 32 次" },
            { name: "job 工作 · 31 次" },
            { name: "workers 工人 · 30 次" }
          ]},
          { name: "信息 · 媒体", color: "#06b6d4", children: [
            { name: "data 数据 · 64 次" },
            { name: "media 媒体 · 55 次" },
            { name: "information 信息 · 49 次" },
            { name: "news 新闻 · 26 次" },
            { name: "content 内容 · 20 次" }
          ]},
          { name: "科技 · 数字", color: "#6366f1", children: [
            { name: "science 科学 · 38 次" },
            { name: "scientific 科学的 · 37 次" },
            { name: "digital 数字的 · 32 次" },
            { name: "online 在线的 · 29 次" },
            { name: "technology 技术 · 28 次" }
          ]},
          { name: "经济 · 金融", color: "#0d9488", children: [
            { name: "economic 经济的 · 51 次" },
            { name: "tax 税 · 35 次" },
            { name: "financial 金融的 · 34 次" },
            { name: "gdp 国内生产总值 · 21 次" }
          ]},
          { name: "代替 · 选择", color: "#d946ef", children: [
            { name: "choice 选择 · 22 次" },
            { name: "replace 取代 · 16 次" },
            { name: "option 选择 · 10 次" },
            { name: "alternative 替代 · 7 次" }
          ]},
          { name: "连接 · 过渡", color: "#64748b", children: [
            { name: "rather than 而不是 · 22 次" },
            { name: "so that 以便 · 10 次" },
            { name: "even if 即使 · 7 次" },
            { name: "as to 关于 · 7 次" },
            { name: "even though 尽管 · 5 次" },
            { name: "regardless of 不管 · 5 次" },
            { name: "in terms of 就…而言 · 3 次" }
          ]},
          { name: "因果 · 由来", color: "#334155", children: [
            { name: "lead to 导致 · 10 次" },
            { name: "due to 由于 · 9 次" },
            { name: "in that 在于 · 因为 · 7 次" },
            { name: "in favor of 赞成 · 6 次" },
            { name: "result in 导致 · 3 次" },
            { name: "owing to 由于 · 3 次" },
            { name: "arise from 源于 · 2 次" },
            { name: "give rise to 引发 · 1 次" },
            { name: "account for 占 · 解释 · 1 次" }
          ]},
          { name: "大 · 小", color: "#ca8a04", children: [
            { name: "big 大的 · 36 次" },
            { name: "little 小的 · 30 次" },
            { name: "small 小的 · 22 次" },
            { name: "large 大的 · 21 次" }
          ]},
          { name: "好 · 优秀", color: "#eab308", children: [
            { name: "good 好的 · 40 次" },
            { name: "better 更好的 · 40 次" },
            { name: "well 好 · 37 次" },
            { name: "great 极好的 · 31 次" }
          ]}
        ]
      }
    ]
  };

  /* >>> 写作句式（tools/build_writing_patterns.py 自动生成，勿手改） >>> */
  DATA.maps.push({
  "id": "writing",
  "title": "写作句式 · 同义替换（大作文 2010-2026）",
  "root": "写作句式",
  "rootColor": "#0d9488",
  "intro": "来源：2010-2026 英语二大作文「真题套用示范」里的关键句型，按写作功能成簇。写大作文时同簇表达换着用（如「占比最大」有 3 种说法、「上升」有 5 种说法），就不会通篇 rose / increase 重复。中文即该句型的用法，尾部数字为出现年份数——数字越大越是高频万能句。",
  "branches": [
    {
      "name": "图表引出（4）",
      "color": "#0d9488",
      "children": [
        {
          "name": "did not move in a uniform direction 并未朝着相同方向变化 · 3 年",
          "en": "did not move in a uniform direction",
          "rest": "并未朝着相同方向变化 · 3 年"
        },
        {
          "name": "presents an uneven distribution among the perceived benefits of … 呈现了人们对……各项益处的看法分布 · 2026",
          "en": "presents an uneven distribution among the perceived benefits of …",
          "rest": "呈现了人们对……各项益处的看法分布 · 2026"
        },
        {
          "name": "The table presents an uneven distribution among… 该表格呈现了……之间的不均衡分布 · 2012",
          "en": "The table presents an uneven distribution among…",
          "rest": "该表格呈现了……之间的不均衡分布 · 2012"
        },
        {
          "name": "This pie chart presents an uneven distribution among… 该饼图呈现了……之间的不均衡分布 · 2015",
          "en": "This pie chart presents an uneven distribution among…",
          "rest": "该饼图呈现了……之间的不均衡分布 · 2015"
        }
      ]
    },
    {
      "name": "上升趋势（7）",
      "color": "#ef4444",
      "children": [
        {
          "name": "rose steadily from … to … 从……至……持续上升 · 3 年",
          "en": "rose steadily from … to …",
          "rest": "从……至……持续上升 · 3 年"
        },
        {
          "name": "rose steadily during the periods presented 在相应时期内持续上升 · 2 年",
          "en": "rose steadily during the periods presented",
          "rest": "在相应时期内持续上升 · 2 年"
        },
        {
          "name": "showing a steady upward trend 呈现稳定上升趋势 · 2 年",
          "en": "showing a steady upward trend",
          "rest": "呈现稳定上升趋势 · 2 年"
        },
        {
          "name": "climbed from … to … 由……攀升至…… · 2010",
          "en": "climbed from … to …",
          "rest": "由……攀升至…… · 2010"
        },
        {
          "name": "maintained a dynamic momentum 保持强劲势头 · 2017",
          "en": "maintained a dynamic momentum",
          "rest": "保持强劲势头 · 2017"
        },
        {
          "name": "rose slightly 略有上升 · 2019",
          "en": "rose slightly",
          "rest": "略有上升 · 2019"
        },
        {
          "name": "the biggest increase occurred in … 最大增幅出现在…… · 2013",
          "en": "the biggest increase occurred in …",
          "rest": "最大增幅出现在…… · 2013"
        }
      ]
    },
    {
      "name": "幅度·速度（6）",
      "color": "#f59e0b",
      "children": [
        {
          "name": "expanded their share by nearly the same margin 以相近幅度扩大份额 · 2011",
          "en": "expanded their share by nearly the same margin",
          "rest": "以相近幅度扩大份额 · 2011"
        },
        {
          "name": "had not yet reached saturation 尚未达到饱和 · 2010",
          "en": "had not yet reached saturation",
          "rest": "尚未达到饱和 · 2010"
        },
        {
          "name": "left little room for further growth 几乎没有进一步增长的空间 · 2010",
          "en": "left little room for further growth",
          "rest": "几乎没有进一步增长的空间 · 2010"
        },
        {
          "name": "marked a watershed when the growth accelerated 是增速加快的转折点 · 2023",
          "en": "marked a watershed when the growth accelerated",
          "rest": "是增速加快的转折点 · 2023"
        },
        {
          "name": "the pace of growth differed sharply 增长速度差异明显 · 2010",
          "en": "the pace of growth differed sharply",
          "rest": "增长速度差异明显 · 2010"
        },
        {
          "name": "the trend is particularly striking 这一趋势尤为显著 · 2022",
          "en": "the trend is particularly striking",
          "rest": "这一趋势尤为显著 · 2022"
        }
      ]
    },
    {
      "name": "占比·分布（7）",
      "color": "#8b5cf6",
      "children": [
        {
          "name": "accounts for the largest share, at …% 占比最大，达到……% · 6 年",
          "en": "accounts for the largest share, at …%",
          "rest": "占比最大，达到……% · 6 年"
        },
        {
          "name": "follows closely, representing …% 紧随其后，占……% · 5 年",
          "en": "follows closely, representing …%",
          "rest": "紧随其后，占……% · 5 年"
        },
        {
          "name": "make up relatively small proportions of … 占比相对较小，分别为…… · 5 年",
          "en": "make up relatively small proportions of …",
          "rest": "占比相对较小，分别为…… · 5 年"
        },
        {
          "name": "form the middle group, representing …% and …% respectively 处于中间位置，分别占……% 和……% · 2 年",
          "en": "form the middle group, representing …% and …% respectively",
          "rest": "处于中间位置，分别占……% 和……% · 2 年"
        },
        {
          "name": "account for the largest share, together making up …% of the total 占比最大，合计达总额的……% · 2015",
          "en": "account for the largest share, together making up …% of the total",
          "rest": "占比最大，合计达总额的……% · 2015"
        },
        {
          "name": "accounts for the largest share, at slightly over half of the respondents 占比最大，略超受访者半数 · 2021",
          "en": "accounts for the largest share, at slightly over half of the respondents",
          "rest": "占比最大，略超受访者半数 · 2021"
        },
        {
          "name": "none of them felt satisfied 无一人感到满意 · 2012",
          "en": "none of them felt satisfied",
          "rest": "无一人感到满意 · 2012"
        }
      ]
    },
    {
      "name": "升降对比·转折（4）",
      "color": "#10b981",
      "children": [
        {
          "name": "By contrast 相比之下（用于转折对比） · 2011",
          "en": "By contrast",
          "rest": "相比之下（用于转折对比） · 2011"
        },
        {
          "name": "climbed from … to …, while … declined from … to … 从……攀升至……，而……从……降至…… · 2014",
          "en": "climbed from … to …, while … declined from … to …",
          "rest": "从……攀升至……，而……从……降至…… · 2014"
        },
        {
          "name": "declined from … to …, while … climbed from … to … 从……降至……，而……从……升至…… · 2019",
          "en": "declined from … to …, while … climbed from … to …",
          "rest": "从……降至……，而……从……升至…… · 2019"
        },
        {
          "name": "were displaced from their leading position 从领先位置被取代 · 2011",
          "en": "were displaced from their leading position",
          "rest": "从领先位置被取代 · 2011"
        }
      ]
    },
    {
      "name": "原因·背景（13）",
      "color": "#f97316",
      "children": [
        {
          "name": "a natural consequence of changing parenting ideas 育儿观念变化的自然结果 · 2026",
          "en": "a natural consequence of changing parenting ideas",
          "rest": "育儿观念变化的自然结果 · 2026"
        },
        {
          "name": "a natural consequence of social life 社会生活变化的自然结果 · 2015",
          "en": "a natural consequence of social life",
          "rest": "社会生活变化的自然结果 · 2015"
        },
        {
          "name": "a shift in graduates’ view of post-university life 毕业生对毕业后生活看法的转变 · 2019",
          "en": "a shift in graduates’ view of post-university life",
          "rest": "毕业生对毕业后生活看法的转变 · 2019"
        },
        {
          "name": "as livestreaming e-commerce takes off 随着直播电商兴起 · 2022",
          "en": "as livestreaming e-commerce takes off",
          "rest": "随着直播电商兴起 · 2022"
        },
        {
          "name": "narrowed the technology gap 缩小了技术差距 · 2011",
          "en": "narrowed the technology gap",
          "rest": "缩小了技术差距 · 2011"
        },
        {
          "name": "on account of flexibility and convenience 出于灵活与便利 · 2021",
          "en": "on account of flexibility and convenience",
          "rest": "出于灵活与便利 · 2021"
        },
        {
          "name": "reach a career plateau 进入职业平台期 · 2012",
          "en": "reach a career plateau",
          "rest": "进入职业平台期 · 2012"
        },
        {
          "name": "the awareness of self-improvement 自我提升意识 · 2020",
          "en": "the awareness of self-improvement",
          "rest": "自我提升意识 · 2020"
        },
        {
          "name": "the change in priorities 关注重点的转变 · 2018",
          "en": "the change in priorities",
          "rest": "关注重点的转变 · 2018"
        },
        {
          "name": "the consequent sense of powerlessness 随之而来的无力感 · 2012",
          "en": "the consequent sense of powerlessness",
          "rest": "随之而来的无力感 · 2012"
        },
        {
          "name": "the joint effects of urbanization and unequal economic opportunities 城镇化与经济机会不均的共同作用 · 2014",
          "en": "the joint effects of urbanization and unequal economic opportunities",
          "rest": "城镇化与经济机会不均的共同作用 · 2014"
        },
        {
          "name": "the national endeavour in cultural undertakings 国家在文化事业上的努力 · 2017",
          "en": "the national endeavour in cultural undertakings",
          "rest": "国家在文化事业上的努力 · 2017"
        },
        {
          "name": "with the prosperity of tourism 随着旅游业繁荣 · 2016",
          "en": "with the prosperity of tourism",
          "rest": "随着旅游业繁荣 · 2016"
        }
      ]
    },
    {
      "name": "意义·价值（9）",
      "color": "#eab308",
      "children": [
        {
          "name": "a low-intensity activity suitable for the elderly 适合老年人的低强度活动 · 2025",
          "en": "a low-intensity activity suitable for the elderly",
          "rest": "适合老年人的低强度活动 · 2025"
        },
        {
          "name": "an ideal way to recharge 理想的充电方式 · 2016",
          "en": "an ideal way to recharge",
          "rest": "理想的充电方式 · 2016"
        },
        {
          "name": "enrich the daily life 丰富日常生活 · 2025",
          "en": "enrich the daily life",
          "rest": "丰富日常生活 · 2025"
        },
        {
          "name": "facilitate interpersonal relationships 增进人际关系 · 2015",
          "en": "facilitate interpersonal relationships",
          "rest": "增进人际关系 · 2015"
        },
        {
          "name": "gain easy and fast access to professional advice 便捷快速地获得专业建议 · 2023",
          "en": "gain easy and fast access to professional advice",
          "rest": "便捷快速地获得专业建议 · 2023"
        },
        {
          "name": "gain practical experience 获取实践经验 · 2013",
          "en": "gain practical experience",
          "rest": "获取实践经验 · 2013"
        },
        {
          "name": "regard … as a vivid classroom where children learn through discovery 把……视为孩子通过探索来学习的生动课堂 · 2026",
          "en": "regard … as a vivid classroom where children learn through discovery",
          "rest": "把……视为孩子通过探索来学习的生动课堂 · 2026"
        },
        {
          "name": "the key to standing out 脱颖而出的关键 · 2018",
          "en": "the key to standing out",
          "rest": "脱颖而出的关键 · 2018"
        },
        {
          "name": "varied spiritual nourishment 多样化的精神食粮 · 2017",
          "en": "varied spiritual nourishment",
          "rest": "多样化的精神食粮 · 2017"
        }
      ]
    },
    {
      "name": "建议·展望（12）",
      "color": "#06b6d4",
      "children": [
        {
          "name": "boosted the popularity of doing workouts at home 推动了居家锻炼的流行 · 2021",
          "en": "boosted the popularity of doing workouts at home",
          "rest": "推动了居家锻炼的流行 · 2021"
        },
        {
          "name": "channel more resources into … 向……倾斜更多资源 · 2014",
          "en": "channel more resources into …",
          "rest": "向……倾斜更多资源 · 2014"
        },
        {
          "name": "give impetus to the delivery business 推动快递业务发展 · 2022",
          "en": "give impetus to the delivery business",
          "rest": "推动快递业务发展 · 2022"
        },
        {
          "name": "keep pace with the public demand 跟上公众需求 · 2017",
          "en": "keep pace with the public demand",
          "rest": "跟上公众需求 · 2017"
        },
        {
          "name": "not go to extremes 不走极端 · 2015",
          "en": "not go to extremes",
          "rest": "不走极端 · 2015"
        },
        {
          "name": "on their own initiative 主动地 · 2014",
          "en": "on their own initiative",
          "rest": "主动地 · 2014"
        },
        {
          "name": "paves the way for their career development 为职业发展铺路 · 2024",
          "en": "paves the way for their career development",
          "rest": "为职业发展铺路 · 2024"
        },
        {
          "name": "paves the way for … 为……铺平道路 · 2022",
          "en": "paves the way for …",
          "rest": "为……铺平道路 · 2022"
        },
        {
          "name": "public sports facilities 公共体育设施 · 2021",
          "en": "public sports facilities",
          "rest": "公共体育设施 · 2021"
        },
        {
          "name": "secure an advantage 获取优势 · 2019",
          "en": "secure an advantage",
          "rest": "获取优势 · 2019"
        },
        {
          "name": "stay competitive in the job market 在就业市场中保持竞争力 · 2020",
          "en": "stay competitive in the job market",
          "rest": "在就业市场中保持竞争力 · 2020"
        },
        {
          "name": "strike a balance between work and study 平衡工作与学业 · 2013",
          "en": "strike a balance between work and study",
          "rest": "平衡工作与学业 · 2013"
        }
      ]
    },
    {
      "name": "主题词·术语（3）",
      "color": "#64748b",
      "children": [
        {
          "name": "hands-on experience 实践/动手经历 · 2024",
          "en": "hands-on experience",
          "rest": "实践/动手经历 · 2024"
        },
        {
          "name": "health literacy rate 健康素养水平 · 2023",
          "en": "health literacy rate",
          "rest": "健康素养水平 · 2023"
        },
        {
          "name": "per capita disposable income 人均可支配收入 · 2018",
          "en": "per capita disposable income",
          "rest": "人均可支配收入 · 2018"
        }
      ]
    }
  ]
});
  /* <<< 写作句式 <<< */

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function leafText(t) {
    var m = t.match(/^([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(.+)$/);
    if (m) return '<b>' + esc(m[1]) + '</b> ' + esc(m[2]);
    return esc(t);
  }

  function renderItems(items) {
    var html = '';
    items.forEach(function (it) {
      if (it.children && it.children.length) {
        html += renderItems(it.children);
      } else if (it.en) {
        // 带完整英文词条的条目（如写作句式）：整句英文加粗，其余用浅色
        html += '<div class="leaf-row"><b>' + esc(it.en) + '</b> <span class="leaf-rest">' + esc(it.rest || '') + '</span></div>';
      } else {
        html += '<div class="leaf-row">' + leafText(it.name) + '</div>';
      }
    });
    return html;
  }

  // 响应式卡片网格：每簇一张卡，桌面 2~3 列、手机 1 列（替代原横向横滑，长列表也不再需要横滑）
  function renderMap(map) {
    var html = '';
    if (map.intro) html += '<p class="map-intro">' + esc(map.intro) + '</p>';
    html += '<div class="nm-grid">';
    map.branches.forEach(function (b) {
      html += '<div class="nm-card" style="--c:' + b.color + '">';
      html += '<div class="nm-card-head">' + esc(b.name) + '</div>';
      html += renderItems(b.children);
      html += '</div>';
    });
    html += '</div>';
    return html;
  }

  // ==================== 高亮标记（独立 key，与方法导图互不干扰） ====================
  var HL_KEY = 'nm_highlights_v1';
  var content = null;
  var hlSet = loadHL();

  function loadHL() {
    try { return new Set(JSON.parse(localStorage.getItem(HL_KEY) || '[]')); }
    catch (e) { return new Set(); }
  }
  function saveHL() {
    try { localStorage.setItem(HL_KEY, JSON.stringify(Array.from(hlSet))); } catch (e) {}
  }
  function rowKey(row) { return row.textContent; }

  function restoreHL() {
    if (!content) return;
    var rows = content.querySelectorAll('.leaf-row');
    for (var i = 0; i < rows.length; i++) {
      if (hlSet.has(rowKey(rows[i]))) rows[i].classList.add('hl');
    }
  }
  function onContentClick(e) {
    var row = e.target.closest ? e.target.closest('.leaf-row') : null;
    if (!row) return;
    var k = rowKey(row);
    if (hlSet.has(k)) { hlSet.delete(k); row.classList.remove('hl'); }
    else { hlSet.add(k); row.classList.add('hl'); }
    saveHL();
  }
  window.clearHighlights = function () {
    hlSet.clear();
    saveHL();
    if (content) {
      var rows = content.querySelectorAll('.hl');
      for (var i = 0; i < rows.length; i++) rows[i].classList.remove('hl');
    }
  };

  function init() {
    content = document.getElementById('mmContent');
    if (!content) return;
    content.innerHTML = DATA.maps.map(function (m) {
      return '<section class="map-section"><h2 class="map-h">' + esc(m.title) + '</h2>' + renderMap(m) + '</section>';
    }).join('');
    restoreHL();
    content.addEventListener('click', onContentClick);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();