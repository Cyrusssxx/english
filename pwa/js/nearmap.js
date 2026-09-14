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
  [{
  "id": "writing",
  "title": "写作句式 · 模板句型（大作文 2010-2026）",
  "root": "写作句式",
  "rootColor": "#0d9488",
  "intro": "来源：2010-2026 英语二大作文「真题套用示范」真正用到的模板句。{{ }} 是留给题目的槽位，尾部数字为该句在多届示范里出现过的年数——数字越大越适合直接背。",
  "branches": [
    {
      "name": "第一段 · 静态图描述（5）",
      "color": "#0d9488",
      "children": [
        {
          "name": "The {{chart}} chart presents an uneven distribution among the categories associated with {{topic}}. 该 {{xx}} 图表呈现了与 {{topic}} 有关的不同类别之间不均衡的分布情况。 · 9 年",
          "en": "The {{chart}} chart presents an uneven distribution among the categories associated with {{topic}}.",
          "rest": "该 {{xx}} 图表呈现了与 {{topic}} 有关的不同类别之间不均衡的分布情况。 · 9 年"
        },
        {
          "name": "{{item1}} accounts for the largest share, at {{percent1}}. {{item1}} 所占比例最大，达到 {{percent1}}。 · 9 年",
          "en": "{{item1}} accounts for the largest share, at {{percent1}}.",
          "rest": "{{item1}} 所占比例最大，达到 {{percent1}}。 · 9 年"
        },
        {
          "name": "As for {{item1}} and {{item2}}, they register {{percent1}} and {{percent2}} respectively. 就 {{item1}} 与 {{item2}} 而言，它们分别为 {{percent1}} 和 {{percent2}}。 · 6 年",
          "en": "As for {{item1}} and {{item2}}, they register {{percent1}} and {{percent2}} respectively.",
          "rest": "就 {{item1}} 与 {{item2}} 而言，它们分别为 {{percent1}} 和 {{percent2}}。 · 6 年"
        },
        {
          "name": "In contrast, {{item4}} and {{item5}} make up relatively small proportions of {{percent4}} and {{percent5}}. 相比之下，{{item4}} 和 {{item5}} 所占比例较小，分别为 {{percent4}} 和 {{percent5}}。 · 6 年",
          "en": "In contrast, {{item4}} and {{item5}} make up relatively small proportions of {{percent4}} and {{percent5}}.",
          "rest": "相比之下，{{item4}} 和 {{item5}} 所占比例较小，分别为 {{percent4}} 和 {{percent5}}。 · 6 年"
        },
        {
          "name": "{{item2}} and {{item3}} form the middle group, representing {{percent2}} and {{percent3}}, respectively. {{item2}} 和 {{item3}} 处于中间位置，分别占 {{percent2}} 和 {{percent3}}。 · 4 年",
          "en": "{{item2}} and {{item3}} form the middle group, representing {{percent2}} and {{percent3}}, respectively.",
          "rest": "{{item2}} 和 {{item3}} 处于中间位置，分别占 {{percent2}} 和 {{percent3}}。 · 4 年"
        }
      ]
    },
    {
      "name": "第一段 · 动态图描述（4）",
      "color": "#0ea5e9",
      "children": [
        {
          "name": "The line chart shows that the items associated with {{topic}} did not move in a uniform direction during the periods presented. 该折线图表明，与 {{topic}} 有关的不同项目在相应时期内并未朝着相同方向变化。 · 8 年",
          "en": "The line chart shows that the items associated with {{topic}} did not move in a uniform direction during the periods presented.",
          "rest": "该折线图表明，与 {{topic}} 有关的不同项目在相应时期内并未朝着相同方向变化。 · 8 年"
        },
        {
          "name": "{{item1}} climbed from {{num1}} in {{time1}} to {{num2}} in {{time2}}, while {{item2}} rose from {{num3}} in {{time3}} to {{num4}} in {{time4}}. {{item1}} 由 {{time1}} 的 {{num1}} 上升至 {{time2}} 的 {{num2}}，{{item2}} 则从 {{time3}} 的 {{num3}} 增至 {{time4}} 的 {{num4}}。 · 8 年",
          "en": "{{item1}} climbed from {{num1}} in {{time1}} to {{num2}} in {{time2}}, while {{item2}} rose from {{num3}} in {{time3}} to {{num4}} in {{time4}}.",
          "rest": "{{item1}} 由 {{time1}} 的 {{num1}} 上升至 {{time2}} 的 {{num2}}，{{item2}} 则从 {{time3}} 的 {{num3}} 增至 {{time4}} 的 {{num4}}。 · 8 年"
        },
        {
          "name": "From {{time1}} to {{time2}}, {{item1}} rose from {{num1}} to {{num2}}, showing a steady upward trend. 自 {{time1}} 至 {{time2}}，{{item1}} 由 {{num1}} 升至 {{num2}}，呈现稳定上升趋势。 · 3 年",
          "en": "From {{time1}} to {{time2}}, {{item1}} rose from {{num1}} to {{num2}}, showing a steady upward trend.",
          "rest": "自 {{time1}} 至 {{time2}}，{{item1}} 由 {{num1}} 升至 {{num2}}，呈现稳定上升趋势。 · 3 年"
        },
        {
          "name": "By contrast, {{item3}} fell from {{num5}} in {{time5}} to {{num6}} in {{time6}}. 相比之下，{{item3}} 由 {{time5}} 的 {{num5}} 下降至 {{time6}} 的 {{num6}}。 · 2019",
          "en": "By contrast, {{item3}} fell from {{num5}} in {{time5}} to {{num6}} in {{time6}}.",
          "rest": "相比之下，{{item3}} 由 {{time5}} 的 {{num5}} 下降至 {{time6}} 的 {{num6}}。 · 2019"
        }
      ]
    },
    {
      "name": "第二段 · 经济类归因（4）",
      "color": "#f97316",
      "children": [
        {
          "name": "Undoubtedly, the country's rapid economic growth has laid a solid material foundation for the emergence of {{topic}}. 毫无疑问，国家经济的飞速发展，为 {{topic}} 的出现奠定了坚实的物质基础。 · 6 年",
          "en": "Undoubtedly, the country's rapid economic growth has laid a solid material foundation for the emergence of {{topic}}.",
          "rest": "毫无疑问，国家经济的飞速发展，为 {{topic}} 的出现奠定了坚实的物质基础。 · 6 年"
        },
        {
          "name": "As the pace of life accelerates, individuals attach greater importance to convenience and efficiency and become increasingly willing to embrace new ways of living. 随着生活节奏加快，个人开始更加重视便利和效率，也更愿意接受新的生活方式。 · 6 年",
          "en": "As the pace of life accelerates, individuals attach greater importance to convenience and efficiency and become increasingly willing to embrace new ways of living.",
          "rest": "随着生活节奏加快，个人开始更加重视便利和效率，也更愿意接受新的生活方式。 · 6 年"
        },
        {
          "name": "Growing public attention to {{topic}} stems from its ability to meet practical needs in everyday life. {{topic}} 之所以受到越来越多关注，是因为它能够回应人们在现实生活中的实际需要。 · 3 年",
          "en": "Growing public attention to {{topic}} stems from its ability to meet practical needs in everyday life.",
          "rest": "{{topic}} 之所以受到越来越多关注，是因为它能够回应人们在现实生活中的实际需要。 · 3 年"
        },
        {
          "name": "Seen in this light, the development of {{topic}} is no coincidence but a natural consequence of broader changes in social life. 由此可见，{{topic}} 的发展并非偶然，而是社会生活发生变化后的自然结果。 · 3 年",
          "en": "Seen in this light, the development of {{topic}} is no coincidence but a natural consequence of broader changes in social life.",
          "rest": "由此可见，{{topic}} 的发展并非偶然，而是社会生活发生变化后的自然结果。 · 3 年"
        }
      ]
    },
    {
      "name": "第二段 · 校园/成长类归因（4）",
      "color": "#eab308",
      "children": [
        {
          "name": "{{topic}} can enable individuals to approach routine tasks with greater maturity, preventing them from giving up too readily in the face of temporary difficulties. {{topic}} 能够使个人以更加成熟的态度处理日常任务，不因暂时困难就轻易放弃。 · 7 年",
          "en": "{{topic}} can enable individuals to approach routine tasks with greater maturity, preventing them from giving up too readily in the face of temporary difficulties.",
          "rest": "{{topic}} 能够使个人以更加成熟的态度处理日常任务，不因暂时困难就轻易放弃。 · 7 年"
        },
        {
          "name": "Ultimately, {{topic}} can not only improve individuals' present conduct but also strengthen their capacity for self-management, thereby laying a solid foundation for their future growth. 最终，{{topic}} 不仅能够改善个人当下的行为表现，也会增强其自我管理能力，为今后的成长提供稳定支持。 · 7 年",
          "en": "Ultimately, {{topic}} can not only improve individuals' present conduct but also strengthen their capacity for self-management, thereby laying a solid foundation for their future growth.",
          "rest": "最终，{{topic}} 不仅能够改善个人当下的行为表现，也会增强其自我管理能力，为今后的成长提供稳定支持。 · 7 年"
        },
        {
          "name": "The influence of {{topic}} is not confined to a single action; rather, it continues to shape the way individuals handle everyday responsibilities. {{topic}} 的作用，并不会局限于某一次行为，而会持续影响个人处理日常事务的方式。 · 6 年",
          "en": "The influence of {{topic}} is not confined to a single action; rather, it continues to shape the way individuals handle everyday responsibilities.",
          "rest": "{{topic}} 的作用，并不会局限于某一次行为，而会持续影响个人处理日常事务的方式。 · 6 年"
        },
        {
          "name": "In this process, individuals gradually become less dependent on external reminders and begin to take responsibility for their own choices. 在这一过程中，个人会逐步减少对外界提醒的依赖，并开始主动为自己的选择负责。 · 2024",
          "en": "In this process, individuals gradually become less dependent on external reminders and begin to take responsibility for their own choices.",
          "rest": "在这一过程中，个人会逐步减少对外界提醒的依赖，并开始主动为自己的选择负责。 · 2024"
        }
      ]
    },
    {
      "name": "第二段 · 体育健康类归因（4）",
      "color": "#10b981",
      "children": [
        {
          "name": "Changes reflected in {{topic}} are closely linked to rising public awareness of personal health and increasingly favorable conditions for physical exercise. {{topic}} 所反映的变化，与公众健康意识的提高和公共运动条件的改善密切相关。 · 3 年",
          "en": "Changes reflected in {{topic}} are closely linked to rising public awareness of personal health and increasingly favorable conditions for physical exercise.",
          "rest": "{{topic}} 所反映的变化，与公众健康意识的提高和公共运动条件的改善密切相关。 · 3 年"
        },
        {
          "name": "As physical exercise becomes increasingly integrated into everyday life, the number of people willing to take part in related activities will continue to grow. 随着体育锻炼逐渐融入日常生活，愿意参与相关活动的人数也会不断增加。 · 3 年",
          "en": "As physical exercise becomes increasingly integrated into everyday life, the number of people willing to take part in related activities will continue to grow.",
          "rest": "随着体育锻炼逐渐融入日常生活，愿意参与相关活动的人数也会不断增加。 · 3 年"
        },
        {
          "name": "For this reason, {{topic}} not only reflects the continued advancement of national fitness but also demonstrates the growing acceptance of healthy living. 正因如此，{{topic}} 不仅体现了全民健身事业的持续推进，也说明健康生活正在得到更加广泛的认可。 · 2 年",
          "en": "For this reason, {{topic}} not only reflects the continued advancement of national fitness but also demonstrates the growing acceptance of healthy living.",
          "rest": "正因如此，{{topic}} 不仅体现了全民健身事业的持续推进，也说明健康生活正在得到更加广泛的认可。 · 2 年"
        },
        {
          "name": "Improved sports infrastructure makes it easier for people to participate in physical exercise, while a wider range of exercise methods enables different groups to make choices suited to their own circumstances. 更加完善的体育设施为人们参与体育锻炼提供了便利，而多样化的运动方式也使不同群体能够根据自身情况作出选择。 · 2021",
          "en": "Improved sports infrastructure makes it easier for people to participate in physical exercise, while a wider range of exercise methods enables different groups to make choices suited to their own circumstances.",
          "rest": "更加完善的体育设施为人们参与体育锻炼提供了便利，而多样化的运动方式也使不同群体能够根据自身情况作出选择。 · 2021"
        }
      ]
    },
    {
      "name": "第二段 · 文化自信类归因（3）",
      "color": "#a855f7",
      "children": [
        {
          "name": "Traditional culture cannot be effectively conveyed through the one-way delivery of content alone; its modes of expression must also be adjusted in response to real-world feedback. 传统文化的传播不能只是向公众单向传递内容，也需要根据现实反馈不断调整表达方式。 · 2017",
          "en": "Traditional culture cannot be effectively conveyed through the one-way delivery of content alone; its modes of expression must also be adjusted in response to real-world feedback.",
          "rest": "传统文化的传播不能只是向公众单向传递内容，也需要根据现实反馈不断调整表达方式。 · 2017"
        },
        {
          "name": "{{topic}} can establish a channel of communication between traditional culture and the public, allowing cultural content to be explained with greater clarity. {{topic}} 为传统文化与公众之间建立了交流渠道，使文化内容能够得到更加清楚的解释。 · 2017",
          "en": "{{topic}} can establish a channel of communication between traditional culture and the public, allowing cultural content to be explained with greater clarity.",
          "rest": "{{topic}} 为传统文化与公众之间建立了交流渠道，使文化内容能够得到更加清楚的解释。 · 2017"
        },
        {
          "name": "Public participation can also give rise to new forms of cultural expression, enabling traditional culture to adapt to social change while preserving its core values. 公众的参与也会为传统文化带来新的表达，使其在保留核心价值的同时适应社会变化。 · 2017",
          "en": "Public participation can also give rise to new forms of cultural expression, enabling traditional culture to adapt to social change while preserving its core values.",
          "rest": "公众的参与也会为传统文化带来新的表达，使其在保留核心价值的同时适应社会变化。 · 2017"
        }
      ]
    },
    {
      "name": "第三段 · 正面总结建议（3）",
      "color": "#06b6d4",
      "children": [
        {
          "name": "Relevant authorities should provide the necessary support and create favorable conditions under which {{topic}} can play a constructive role. 有关部门应提供必要支持，为 {{topic}} 发挥作用创造良好条件。 · 17 年",
          "en": "Relevant authorities should provide the necessary support and create favorable conditions under which {{topic}} can play a constructive role.",
          "rest": "有关部门应提供必要支持，为 {{topic}} 发挥作用创造良好条件。 · 17 年"
        },
        {
          "name": "Individuals should also make well-informed choices in light of their own circumstances, ensuring that {{topic}} genuinely contributes to their long-term development. 个人也应结合自身情况作出合理选择，使 {{topic}} 真正服务于自身的长期发展。 · 11 年",
          "en": "Individuals should also make well-informed choices in light of their own circumstances, ensuring that {{topic}} genuinely contributes to their long-term development.",
          "rest": "个人也应结合自身情况作出合理选择，使 {{topic}} 真正服务于自身的长期发展。 · 11 年"
        },
        {
          "name": "For {{topic}} to continue exerting a positive influence on personal growth, concerted efforts from all sectors of society are essential. 要使 {{topic}} 持续为个人成长带来积极影响，需要社会各方共同努力。 · 10 年",
          "en": "For {{topic}} to continue exerting a positive influence on personal growth, concerted efforts from all sectors of society are essential.",
          "rest": "要使 {{topic}} 持续为个人成长带来积极影响，需要社会各方共同努力。 · 10 年"
        }
      ]
    }
  ]
},
   {
  "id": "writing_slot",
  "title": "填槽表达 · 换词应万变（大作文 2010-2026）",
  "root": "填槽表达",
  "rootColor": "#8b5cf6",
  "intro": "来源：17 篇示范里真正填进模板 {{槽位}} 的题相关表达。写新题时在同类里换词即可——例如「占比最大」的主体、「时间」的起止年份，都有现成说法可套。",
  "branches": [
    {
      "name": "图型 · 引出词（37）",
      "color": "#0d9488",
      "children": [
        {
          "name": "bar 柱状 · chart",
          "en": "bar",
          "rest": "柱状（{{chart}}）"
        },
        {
          "name": "pie 饼 · chart",
          "en": "pie",
          "rest": "饼（{{chart}}）"
        },
        {
          "name": "the leisure activities of the elderly 老年人的日常休闲活动 · topic",
          "en": "the leisure activities of the elderly",
          "rest": "老年人的日常休闲活动（{{topic}}）"
        },
        {
          "name": "line 折线 · chart",
          "en": "line",
          "rest": "折线（{{chart}}）"
        },
        {
          "name": "dining out 外出就餐 · topic",
          "en": "dining out",
          "rest": "外出就餐（{{topic}}）"
        },
        {
          "name": "domestic auto brands 国产汽车品牌 · topic",
          "en": "domestic auto brands",
          "rest": "国产汽车品牌（{{topic}}）"
        },
        {
          "name": "express delivery 快递服务 · topic",
          "en": "express delivery",
          "rest": "快递服务（{{topic}}）"
        },
        {
          "name": "festival spending 节日花销 · topic",
          "en": "festival spending",
          "rest": "节日花销（{{topic}}）"
        },
        {
          "name": "further education 继续深造 · topic",
          "en": "further education",
          "rest": "继续深造（{{topic}}）"
        },
        {
          "name": "health literacy 健康素养 · topic",
          "en": "health literacy",
          "rest": "健康素养（{{topic}}）"
        },
        {
          "name": "job satisfaction 工作满意度 · topic",
          "en": "job satisfaction",
          "rest": "工作满意度（{{topic}}）"
        },
        {
          "name": "labor practice courses 劳动实践课 · topic",
          "en": "labor practice courses",
          "rest": "劳动实践课（{{topic}}）"
        },
        {
          "name": "mobile reading 手机阅读 · topic",
          "en": "mobile reading",
          "rest": "手机阅读（{{topic}}）"
        },
        {
          "name": "mobile services 手机服务 · topic",
          "en": "mobile services",
          "rest": "手机服务（{{topic}}）"
        },
        {
          "name": "museums 博物馆 · topic",
          "en": "museums",
          "rest": "博物馆（{{topic}}）"
        },
        {
          "name": "outdoor activities 户外活动 · topic",
          "en": "outdoor activities",
          "rest": "户外活动（{{topic}}）"
        },
        {
          "name": "part-time jobs 兼职 · topic",
          "en": "part-time jobs",
          "rest": "兼职（{{topic}}）"
        },
        {
          "name": "physical exercise 体育锻炼 · topic",
          "en": "physical exercise",
          "rest": "体育锻炼（{{topic}}）"
        },
        {
          "name": "travel 旅行 · topic",
          "en": "travel",
          "rest": "旅行（{{topic}}）"
        },
        {
          "name": "urbanization 城镇化 · topic",
          "en": "urbanization",
          "rest": "城镇化（{{topic}}）"
        },
        {
          "name": "table 表格 · chart",
          "en": "table",
          "rest": "表格（{{chart}}）"
        },
        {
          "name": "Spring Festival spending 春节花销 · topic",
          "en": "Spring Festival spending",
          "rest": "春节花销（{{topic}}）"
        },
        {
          "name": "express delivery volumes nationwide and in rural areas 全国与农村的快递业务量 · topic",
          "en": "express delivery volumes nationwide and in rural areas",
          "rest": "全国与农村的快递业务量（{{topic}}）"
        },
        {
          "name": "graduates' choices after university 本科毕业生的去向 · topic",
          "en": "graduates' choices after university",
          "rest": "本科毕业生的去向（{{topic}}）"
        },
        {
          "name": "job satisfaction across the age groups 各年龄段的工作满意度 · topic",
          "en": "job satisfaction across the age groups",
          "rest": "各年龄段的工作满意度（{{topic}}）"
        },
        {
          "name": "mobile-phone subscriptions in developing and developed countries 发展中国家与发达国家的手机订阅量 · topic",
          "en": "mobile-phone subscriptions in developing and developed countries",
          "rest": "发展中国家与发达国家的手机订阅量（{{topic}}）"
        },
        {
          "name": "the benefits students gained from labor practice courses 学生从劳动实践课中得到的收获 · topic",
          "en": "the benefits students gained from labor practice courses",
          "rest": "学生从劳动实践课中得到的收获（{{topic}}）"
        },
        {
          "name": "the exercise methods chosen by city residents 城市居民的锻炼方式 · topic",
          "en": "the exercise methods chosen by city residents",
          "rest": "城市居民的锻炼方式（{{topic}}）"
        },
        {
          "name": "the factors consumers consider when choosing a restaurant 消费者选择餐厅时的关注因素 · topic",
          "en": "the factors consumers consider when choosing a restaurant",
          "rest": "消费者选择餐厅时的关注因素（{{topic}}）"
        },
        {
          "name": "the health literacy rate of Chinese residents 中国居民的健康素养水平 · topic",
          "en": "the health literacy rate of Chinese residents",
          "rest": "中国居民的健康素养水平（{{topic}}）"
        },
        {
          "name": "the market shares of Chinese, Japanese and American auto brands 中国、日本与美国汽车品牌的市场份额 · topic",
          "en": "the market shares of Chinese, Japanese and American auto brands",
          "rest": "中国、日本与美国汽车品牌的市场份额（{{topic}}）"
        },
        {
          "name": "the number of museums and museum visitors 博物馆数量与参观人数 · topic",
          "en": "the number of museums and museum visitors",
          "rest": "博物馆数量与参观人数（{{topic}}）"
        },
        {
          "name": "the perceived benefits of children's outdoor activities 人们看重的儿童户外活动益处 · topic",
          "en": "the perceived benefits of children's outdoor activities",
          "rest": "人们看重的儿童户外活动益处（{{topic}}）"
        },
        {
          "name": "the proportion of college students taking part-time jobs 大学生兼职比例 · topic",
          "en": "the proportion of college students taking part-time jobs",
          "rest": "大学生兼职比例（{{topic}}）"
        },
        {
          "name": "the purposes of mobile reading among college students 大学生的手机阅读目的 · topic",
          "en": "the purposes of mobile reading among college students",
          "rest": "大学生的手机阅读目的（{{topic}}）"
        },
        {
          "name": "the purposes of travel among college students 大学生的旅游目的 · topic",
          "en": "the purposes of travel among college students",
          "rest": "大学生的旅游目的（{{topic}}）"
        },
        {
          "name": "the urban and rural population 城镇与农村人口 · topic",
          "en": "the urban and rural population",
          "rest": "城镇与农村人口（{{topic}}）"
        }
      ]
    },
    {
      "name": "主体 · 事物（63）",
      "color": "#8b5cf6",
      "children": [
        {
          "name": "Appreciating the beauty of the scenery 欣赏风景 · item1",
          "en": "Appreciating the beauty of the scenery",
          "rest": "欣赏风景（{{item1}}）"
        },
        {
          "name": "Chinese brands 国产品牌 · item1",
          "en": "Chinese brands",
          "rest": "国产品牌（{{item1}}）"
        },
        {
          "name": "Distinguishing features 餐厅特色 · item1",
          "en": "Distinguishing features",
          "rest": "餐厅特色（{{item1}}）"
        },
        {
          "name": "Gaining knowledge 获取知识 · item1",
          "en": "Gaining knowledge",
          "rest": "获取知识（{{item1}}）"
        },
        {
          "name": "Gaining relevant knowledge 获得相关知识 · item1",
          "en": "Gaining relevant knowledge",
          "rest": "获得相关知识（{{item1}}）"
        },
        {
          "name": "Satisfying curiosity 满足好奇心 · item1",
          "en": "Satisfying curiosity",
          "rest": "满足好奇心（{{item1}}）"
        },
        {
          "name": "Subscriptions in developing countries 发展中国家的订阅量 · item1",
          "en": "Subscriptions in developing countries",
          "rest": "发展中国家的订阅量（{{item1}}）"
        },
        {
          "name": "The group over 50 50 岁以上群体 · item1",
          "en": "The group over 50",
          "rest": "50 岁以上群体（{{item1}}）"
        },
        {
          "name": "The health literacy rate 健康素养水平 · item1",
          "en": "The health literacy rate",
          "rest": "健康素养水平（{{item1}}）"
        },
        {
          "name": "The national volume 全国业务量 · item1",
          "en": "The national volume",
          "rest": "全国业务量（{{item1}}）"
        },
        {
          "name": "The number of museums 博物馆数量 · item1",
          "en": "The number of museums",
          "rest": "博物馆数量（{{item1}}）"
        },
        {
          "name": "The rate 这一比例 · item1",
          "en": "The rate",
          "rest": "这一比例（{{item1}}）"
        },
        {
          "name": "The urban population 城镇人口 · item1",
          "en": "The urban population",
          "rest": "城镇人口（{{item1}}）"
        },
        {
          "name": "Travelling, gift giving and dinners with friends or relatives 旅行、送礼以及与亲友聚餐 · item1",
          "en": "Travelling, gift giving and dinners with friends or relatives",
          "rest": "旅行、送礼以及与亲友聚餐（{{item1}}）"
        },
        {
          "name": "Watching television 看电视 · item1",
          "en": "Watching television",
          "rest": "看电视（{{item1}}）"
        },
        {
          "name": "Working out alone 独自锻炼 · item1",
          "en": "Working out alone",
          "rest": "独自锻炼（{{item1}}）"
        },
        {
          "name": "the proportion entering employment 就业比例 · item1",
          "en": "the proportion entering employment",
          "rest": "就业比例（{{item1}}）"
        },
        {
          "name": "American brands 美系品牌 · item2",
          "en": "American brands",
          "rest": "美系品牌（{{item2}}）"
        },
        {
          "name": "Relieving pressure 缓解压力 · item2",
          "en": "Relieving pressure",
          "rest": "缓解压力（{{item2}}）"
        },
        {
          "name": "enhancing observation skills 促进观察力 · item2",
          "en": "enhancing observation skills",
          "rest": "促进观察力（{{item2}}）"
        },
        {
          "name": "exercising with friends 与朋友一起锻炼 · item2",
          "en": "exercising with friends",
          "rest": "与朋友一起锻炼（{{item2}}）"
        },
        {
          "name": "gifts for colleagues 给同事的礼物 · item2",
          "en": "gifts for colleagues",
          "rest": "给同事的礼物（{{item2}}）"
        },
        {
          "name": "improving practical ability 提升实践能力 · item2",
          "en": "improving practical ability",
          "rest": "提升实践能力（{{item2}}）"
        },
        {
          "name": "killing time 消磨时间 · item2",
          "en": "killing time",
          "rest": "消磨时间（{{item2}}）"
        },
        {
          "name": "service 服务 · item2",
          "en": "service",
          "rest": "服务（{{item2}}）"
        },
        {
          "name": "taking walks 散步 · item2",
          "en": "taking walks",
          "rest": "散步（{{item2}}）"
        },
        {
          "name": "the number of visitors 参观人数 · item2",
          "en": "the number of visitors",
          "rest": "参观人数（{{item2}}）"
        },
        {
          "name": "the proportion in the graduation year 毕业当年的比例 · item2",
          "en": "the proportion in the graduation year",
          "rest": "毕业当年的比例（{{item2}}）"
        },
        {
          "name": "the proportion pursuing further education 升学比例 · item2",
          "en": "the proportion pursuing further education",
          "rest": "升学比例（{{item2}}）"
        },
        {
          "name": "the rate in the same period 同期的这一比例 · item2",
          "en": "the rate in the same period",
          "rest": "同期的这一比例（{{item2}}）"
        },
        {
          "name": "the rural population 农村人口 · item2",
          "en": "the rural population",
          "rest": "农村人口（{{item2}}）"
        },
        {
          "name": "the rural volume 农村业务量 · item2",
          "en": "the rural volume",
          "rest": "农村业务量（{{item2}}）"
        },
        {
          "name": "those aged 41 to 50 41 至 50 岁的员工 · item2",
          "en": "those aged 41 to 50",
          "rest": "41 至 50 岁的员工（{{item2}}）"
        },
        {
          "name": "those in developed countries 发达国家同期的订阅量 · item2",
          "en": "those in developed countries",
          "rest": "发达国家同期的订阅量（{{item2}}）"
        },
        {
          "name": "Japanese brands 日系品牌 · item3",
          "en": "Japanese brands",
          "rest": "日系品牌（{{item3}}）"
        },
        {
          "name": "employees aged 31 to 40 31 至 40 岁的员工 · item3",
          "en": "employees aged 31 to 40",
          "rest": "31 至 40 岁的员工（{{item3}}）"
        },
        {
          "name": "household decorations 家庭装饰 · item3",
          "en": "household decorations",
          "rest": "家庭装饰（{{item3}}）"
        },
        {
          "name": "improving physical fitness 强身健体 · item3",
          "en": "improving physical fitness",
          "rest": "强身健体（{{item3}}）"
        },
        {
          "name": "obtaining cheerful moods 获得愉悦心情 · item3",
          "en": "obtaining cheerful moods",
          "rest": "获得愉悦心情（{{item3}}）"
        },
        {
          "name": "obtaining information 获取信息 · item3",
          "en": "obtaining information",
          "rest": "获取信息（{{item3}}）"
        },
        {
          "name": "other aims 其他目的 · item3",
          "en": "other aims",
          "rest": "其他目的（{{item3}}）"
        },
        {
          "name": "planting flowers 养花 · item3",
          "en": "planting flowers",
          "rest": "养花（{{item3}}）"
        },
        {
          "name": "the dining environment 就餐环境 · item3",
          "en": "the dining environment",
          "rest": "就餐环境（{{item3}}）"
        },
        {
          "name": "the proportion starting a business 创业比例 · item3",
          "en": "the proportion starting a business",
          "rest": "创业比例（{{item3}}）"
        },
        {
          "name": "working out with family members 与家人一起锻炼 · item3",
          "en": "working out with family members",
          "rest": "与家人一起锻炼（{{item3}}）"
        },
        {
          "name": "employees aged 40 or younger 40 岁及以下员工 · item4",
          "en": "employees aged 40 or younger",
          "rest": "40 岁及以下员工（{{item4}}）"
        },
        {
          "name": "enhancing cooperative ability 增强合作能力 · item4",
          "en": "enhancing cooperative ability",
          "rest": "增强合作能力（{{item4}}）"
        },
        {
          "name": "making more friends 广交朋友 · item4",
          "en": "making more friends",
          "rest": "广交朋友（{{item4}}）"
        },
        {
          "name": "other items such as fireworks 烟花等其他项目 · item4",
          "en": "other items such as fireworks",
          "rest": "烟花等其他项目（{{item4}}）"
        },
        {
          "name": "other purposes 其他目的 · item4",
          "en": "other purposes",
          "rest": "其他目的（{{item4}}）"
        },
        {
          "name": "playing team sports 参加团队运动 · item4",
          "en": "playing team sports",
          "rest": "参加团队运动（{{item4}}）"
        },
        {
          "name": "price 价格 · item4",
          "en": "price",
          "rest": "价格（{{item4}}）"
        },
        {
          "name": "reading 阅读 · item4",
          "en": "reading",
          "rest": "阅读（{{item4}}）"
        },
        {
          "name": "strengthening parent-child interaction 增强亲子互动 · item4",
          "en": "strengthening parent-child interaction",
          "rest": "增强亲子互动（{{item4}}）"
        },
        {
          "name": "fostering independence 培养独立能力 · item5",
          "en": "fostering independence",
          "rest": "培养独立能力（{{item5}}）"
        },
        {
          "name": "miscellaneous spending 杂项支出 · item5",
          "en": "miscellaneous spending",
          "rest": "杂项支出（{{item5}}）"
        },
        {
          "name": "other benefits 其他益处 · item5",
          "en": "other benefits",
          "rest": "其他益处（{{item5}}）"
        },
        {
          "name": "other factors 其他因素 · item5",
          "en": "other factors",
          "rest": "其他因素（{{item5}}）"
        },
        {
          "name": "other forms of exercise 其他锻炼形式 · item5",
          "en": "other forms of exercise",
          "rest": "其他锻炼形式（{{item5}}）"
        },
        {
          "name": "other gains 其他收获 · item5",
          "en": "other gains",
          "rest": "其他收获（{{item5}}）"
        },
        {
          "name": "playing chess 下棋 · item5",
          "en": "playing chess",
          "rest": "下棋（{{item5}}）"
        },
        {
          "name": "the remaining aims 其余目标 · item5",
          "en": "the remaining aims",
          "rest": "其余目标（{{item5}}）"
        },
        {
          "name": "the remaining respondents 其余受访者 · item5",
          "en": "the remaining respondents",
          "rest": "其余受访者（{{item5}}）"
        }
      ]
    },
    {
      "name": "数据 · 数值（36）",
      "color": "#f59e0b",
      "children": [
        {
          "name": "0.5 billion 5 亿 · num1",
          "en": "0.5 billion",
          "rest": "5 亿（{{num1}}）"
        },
        {
          "name": "300 million 3 亿 · num1",
          "en": "300 million",
          "rest": "3 亿（{{num1}}）"
        },
        {
          "name": "4,169 4169 · num1",
          "en": "4,169",
          "rest": "4169（{{num1}}）"
        },
        {
          "name": "51 billion pieces 510 亿件 · num1",
          "en": "51 billion pieces",
          "rest": "510 亿件（{{num1}}）"
        },
        {
          "name": "67.77% 67.77% · num1",
          "en": "67.77%",
          "rest": "67.77%（{{num1}}）"
        },
        {
          "name": "68.1% 68.1% · num1",
          "en": "68.1%",
          "rest": "68.1%（{{num1}}）"
        },
        {
          "name": "8.80% 8.80% · num1",
          "en": "8.80%",
          "rest": "8.80%（{{num1}}）"
        },
        {
          "name": "a modest share 一个不大的份额 · num1",
          "en": "a modest share",
          "rest": "一个不大的份额（{{num1}}）"
        },
        {
          "name": "25.40% 25.40% · num2",
          "en": "25.40%",
          "rest": "25.40%（{{num2}}）"
        },
        {
          "name": "4 billion 40 亿 · num2",
          "en": "4 billion",
          "rest": "40 亿（{{num2}}）"
        },
        {
          "name": "4,692 4692 · num2",
          "en": "4,692",
          "rest": "4692（{{num2}}）"
        },
        {
          "name": "60.7% 60.7% · num2",
          "en": "60.7%",
          "rest": "60.7%（{{num2}}）"
        },
        {
          "name": "670 million 6.7 亿 · num2",
          "en": "670 million",
          "rest": "6.7 亿（{{num2}}）"
        },
        {
          "name": "83 billion pieces 830 亿件 · num2",
          "en": "83 billion pieces",
          "rest": "830 亿件（{{num2}}）"
        },
        {
          "name": "88.24% 88.24% · num2",
          "en": "88.24%",
          "rest": "88.24%（{{num2}}）"
        },
        {
          "name": "the leading position 领先地位 · num2",
          "en": "the leading position",
          "rest": "领先地位（{{num2}}）"
        },
        {
          "name": "0.7 billion 7 亿 · num3",
          "en": "0.7 billion",
          "rest": "7 亿（{{num3}}）"
        },
        {
          "name": "12 billion pieces 120 亿件 · num3",
          "en": "12 billion pieces",
          "rest": "120 亿件（{{num3}}）"
        },
        {
          "name": "26.3% 26.3% · num3",
          "en": "26.3%",
          "rest": "26.3%（{{num3}}）"
        },
        {
          "name": "637 million 6.37 亿 · num3",
          "en": "637 million",
          "rest": "6.37 亿（{{num3}}）"
        },
        {
          "name": "8.80% 8.80% · num3",
          "en": "8.80%",
          "rest": "8.80%（{{num3}}）"
        },
        {
          "name": "820 million 8.2 亿 · num3",
          "en": "820 million",
          "rest": "8.2 亿（{{num3}}）"
        },
        {
          "name": "83.7% 83.7% · num3",
          "en": "83.7%",
          "rest": "83.7%（{{num3}}）"
        },
        {
          "name": "a small share 一个较小的份额 · num3",
          "en": "a small share",
          "rest": "一个较小的份额（{{num3}}）"
        },
        {
          "name": "1 billion 10 亿 · num4",
          "en": "1 billion",
          "rest": "10 亿（{{num4}}）"
        },
        {
          "name": "25.40% 25.40% · num4",
          "en": "25.40%",
          "rest": "25.40%（{{num4}}）"
        },
        {
          "name": "30 billion pieces 300 亿件 · num4",
          "en": "30 billion pieces",
          "rest": "300 亿件（{{num4}}）"
        },
        {
          "name": "34.0% 34.0% · num4",
          "en": "34.0%",
          "rest": "34.0%（{{num4}}）"
        },
        {
          "name": "680 million 6.8 亿 · num4",
          "en": "680 million",
          "rest": "6.8 亿（{{num4}}）"
        },
        {
          "name": "88.24% 88.24% · num4",
          "en": "88.24%",
          "rest": "88.24%（{{num4}}）"
        },
        {
          "name": "954 million 9.54 亿 · num4",
          "en": "954 million",
          "rest": "9.54 亿（{{num4}}）"
        },
        {
          "name": "a slightly larger share 略大的份额 · num4",
          "en": "a slightly larger share",
          "rest": "略大的份额（{{num4}}）"
        },
        {
          "name": "1.3% 1.3% · num5",
          "en": "1.3%",
          "rest": "1.3%（{{num5}}）"
        },
        {
          "name": "their peak level 其最高水平 · num5",
          "en": "their peak level",
          "rest": "其最高水平（{{num5}}）"
        },
        {
          "name": "2.6% 2.6% · num6",
          "en": "2.6%",
          "rest": "2.6%（{{num6}}）"
        },
        {
          "name": "a much lower level 远低于此的水平 · num6",
          "en": "a much lower level",
          "rest": "远低于此的水平（{{num6}}）"
        }
      ]
    },
    {
      "name": "时间（34）",
      "color": "#3b82f6",
      "children": [
        {
          "name": "2013 2013 年 · time1",
          "en": "2013",
          "rest": "2013 年（{{time1}}）"
        },
        {
          "name": "2013 2013 年 · time3",
          "en": "2013",
          "rest": "2013 年（{{time3}}）"
        },
        {
          "name": "1990 1990 年 · time1",
          "en": "1990",
          "rest": "1990 年（{{time1}}）"
        },
        {
          "name": "2000 2000 年 · time1",
          "en": "2000",
          "rest": "2000 年（{{time1}}）"
        },
        {
          "name": "2012 2012 年 · time1",
          "en": "2012",
          "rest": "2012 年（{{time1}}）"
        },
        {
          "name": "2018 2018 年 · time1",
          "en": "2018",
          "rest": "2018 年（{{time1}}）"
        },
        {
          "name": "the earlier period 前一时期 · time1",
          "en": "the earlier period",
          "rest": "前一时期（{{time1}}）"
        },
        {
          "name": "the first year 大一 · time1",
          "en": "the first year",
          "rest": "大一（{{time1}}）"
        },
        {
          "name": "2008 2008 年 · time2",
          "en": "2008",
          "rest": "2008 年（{{time2}}）"
        },
        {
          "name": "2010 2010 年 · time2",
          "en": "2010",
          "rest": "2010 年（{{time2}}）"
        },
        {
          "name": "2015 2015 年 · time2",
          "en": "2015",
          "rest": "2015 年（{{time2}}）"
        },
        {
          "name": "2018 2018 年 · time2",
          "en": "2018",
          "rest": "2018 年（{{time2}}）"
        },
        {
          "name": "2020 2020 年 · time2",
          "en": "2020",
          "rest": "2020 年（{{time2}}）"
        },
        {
          "name": "2021 2021 年 · time2",
          "en": "2021",
          "rest": "2021 年（{{time2}}）"
        },
        {
          "name": "the final year 大四 · time2",
          "en": "the final year",
          "rest": "大四（{{time2}}）"
        },
        {
          "name": "the later period 后一时期 · time2",
          "en": "the later period",
          "rest": "后一时期（{{time2}}）"
        },
        {
          "name": "1990 1990 年 · time3",
          "en": "1990",
          "rest": "1990 年（{{time3}}）"
        },
        {
          "name": "2000 2000 年 · time3",
          "en": "2000",
          "rest": "2000 年（{{time3}}）"
        },
        {
          "name": "2012 2012 年 · time3",
          "en": "2012",
          "rest": "2012 年（{{time3}}）"
        },
        {
          "name": "2018 2018 年 · time3",
          "en": "2018",
          "rest": "2018 年（{{time3}}）"
        },
        {
          "name": "the earlier period 前一时期 · time3",
          "en": "the earlier period",
          "rest": "前一时期（{{time3}}）"
        },
        {
          "name": "the third year 大三 · time3",
          "en": "the third year",
          "rest": "大三（{{time3}}）"
        },
        {
          "name": "2008 2008 年 · time4",
          "en": "2008",
          "rest": "2008 年（{{time4}}）"
        },
        {
          "name": "2010 2010 年 · time4",
          "en": "2010",
          "rest": "2010 年（{{time4}}）"
        },
        {
          "name": "2015 2015 年 · time4",
          "en": "2015",
          "rest": "2015 年（{{time4}}）"
        },
        {
          "name": "2018 2018 年 · time4",
          "en": "2018",
          "rest": "2018 年（{{time4}}）"
        },
        {
          "name": "2020 2020 年 · time4",
          "en": "2020",
          "rest": "2020 年（{{time4}}）"
        },
        {
          "name": "2021 2021 年 · time4",
          "en": "2021",
          "rest": "2021 年（{{time4}}）"
        },
        {
          "name": "the final year 大四 · time4",
          "en": "the final year",
          "rest": "大四（{{time4}}）"
        },
        {
          "name": "the later period 后一时期 · time4",
          "en": "the later period",
          "rest": "后一时期（{{time4}}）"
        },
        {
          "name": "2013 2013 年 · time5",
          "en": "2013",
          "rest": "2013 年（{{time5}}）"
        },
        {
          "name": "the earlier period 前一时期 · time5",
          "en": "the earlier period",
          "rest": "前一时期（{{time5}}）"
        },
        {
          "name": "2018 2018 年 · time6",
          "en": "2018",
          "rest": "2018 年（{{time6}}）"
        },
        {
          "name": "the later period 后一时期 · time6",
          "en": "the later period",
          "rest": "后一时期（{{time6}}）"
        }
      ]
    },
    {
      "name": "数据 · 占比（42）",
      "color": "#ef4444",
      "children": [
        {
          "name": "a still smaller share 更小的比例 · percent5",
          "en": "a still smaller share",
          "rest": "更小的比例（{{percent5}}）"
        },
        {
          "name": "36.3% 36.3% · percent1",
          "en": "36.3%",
          "rest": "36.3%（{{percent1}}）"
        },
        {
          "name": "37% 37% · percent1",
          "en": "37%",
          "rest": "37%（{{percent1}}）"
        },
        {
          "name": "40% 40% · percent1",
          "en": "40%",
          "rest": "40%（{{percent1}}）"
        },
        {
          "name": "54.6% 54.6% · percent1",
          "en": "54.6%",
          "rest": "54.6%（{{percent1}}）"
        },
        {
          "name": "59.5% 59.5% · percent1",
          "en": "59.5%",
          "rest": "59.5%（{{percent1}}）"
        },
        {
          "name": "80% of the total 总额的 80% · percent1",
          "en": "80% of the total",
          "rest": "总额的 80%（{{percent1}}）"
        },
        {
          "name": "90.8% 90.8% · percent1",
          "en": "90.8%",
          "rest": "90.8%（{{percent1}}）"
        },
        {
          "name": "91.3% 91.3% · percent1",
          "en": "91.3%",
          "rest": "91.3%（{{percent1}}）"
        },
        {
          "name": "slightly over half of the respondents 略超受访者半数 · percent1",
          "en": "slightly over half of the respondents",
          "rest": "略超受访者半数（{{percent1}}）"
        },
        {
          "name": "21.3% 21.3% · percent2",
          "en": "21.3%",
          "rest": "21.3%（{{percent2}}）"
        },
        {
          "name": "26.8% 26.8% · percent2",
          "en": "26.8%",
          "rest": "26.8%（{{percent2}}）"
        },
        {
          "name": "33% 33% · percent2",
          "en": "33%",
          "rest": "33%（{{percent2}}）"
        },
        {
          "name": "47.7% 47.7% · percent2",
          "en": "47.7%",
          "rest": "47.7%（{{percent2}}）"
        },
        {
          "name": "54.5% 54.5% · percent2",
          "en": "54.5%",
          "rest": "54.5%（{{percent2}}）"
        },
        {
          "name": "68.3% 68.3% · percent2",
          "en": "68.3%",
          "rest": "68.3%（{{percent2}}）"
        },
        {
          "name": "84.8% 84.8% · percent2",
          "en": "84.8%",
          "rest": "84.8%（{{percent2}}）"
        },
        {
          "name": "a small share 一个很小的比例 · percent2",
          "en": "a small share",
          "rest": "一个很小的比例（{{percent2}}）"
        },
        {
          "name": "the lowest level 最低水平 · percent2",
          "en": "the lowest level",
          "rest": "最低水平（{{percent2}}）"
        },
        {
          "name": "15% 15% · percent3",
          "en": "15%",
          "rest": "15%（{{percent3}}）"
        },
        {
          "name": "17.0% 17.0% · percent3",
          "en": "17.0%",
          "rest": "17.0%（{{percent3}}）"
        },
        {
          "name": "23.8% 23.8% · percent3",
          "en": "23.8%",
          "rest": "23.8%（{{percent3}}）"
        },
        {
          "name": "23.9% 23.9% · percent3",
          "en": "23.9%",
          "rest": "23.9%（{{percent3}}）"
        },
        {
          "name": "34.7% 34.7% · percent3",
          "en": "34.7%",
          "rest": "34.7%（{{percent3}}）"
        },
        {
          "name": "37.2% 37.2% · percent3",
          "en": "37.2%",
          "rest": "37.2%（{{percent3}}）"
        },
        {
          "name": "54.4% 54.4% · percent3",
          "en": "54.4%",
          "rest": "54.4%（{{percent3}}）"
        },
        {
          "name": "a modest level 中等水平 · percent3",
          "en": "a modest level",
          "rest": "中等水平（{{percent3}}）"
        },
        {
          "name": "a smaller share 更小的比例 · percent3",
          "en": "a smaller share",
          "rest": "更小的比例（{{percent3}}）"
        },
        {
          "name": "12% 12% · percent4",
          "en": "12%",
          "rest": "12%（{{percent4}}）"
        },
        {
          "name": "16.7% 16.7% · percent4",
          "en": "16.7%",
          "rest": "16.7%（{{percent4}}）"
        },
        {
          "name": "2.2% 2.2% · percent4",
          "en": "2.2%",
          "rest": "2.2%（{{percent4}}）"
        },
        {
          "name": "31.8% 31.8% · percent4",
          "en": "31.8%",
          "rest": "31.8%（{{percent4}}）"
        },
        {
          "name": "32.6% 32.6% · percent4",
          "en": "32.6%",
          "rest": "32.6%（{{percent4}}）"
        },
        {
          "name": "33.2% 33.2% · percent4",
          "en": "33.2%",
          "rest": "33.2%（{{percent4}}）"
        },
        {
          "name": "8.4% 8.4% · percent4",
          "en": "8.4%",
          "rest": "8.4%（{{percent4}}）"
        },
        {
          "name": "9% 9% · percent4",
          "en": "9%",
          "rest": "9%（{{percent4}}）"
        },
        {
          "name": "less than 16% 不足 16% · percent4",
          "en": "less than 16%",
          "rest": "不足 16%（{{percent4}}）"
        },
        {
          "name": "18.4% 18.4% · percent5",
          "en": "18.4%",
          "rest": "18.4%（{{percent5}}）"
        },
        {
          "name": "4.7% 4.7% · percent5",
          "en": "4.7%",
          "rest": "4.7%（{{percent5}}）"
        },
        {
          "name": "6% 6% · percent5",
          "en": "6%",
          "rest": "6%（{{percent5}}）"
        },
        {
          "name": "8% 8% · percent5",
          "en": "8%",
          "rest": "8%（{{percent5}}）"
        },
        {
          "name": "a negligible share 微不足道的比例 · percent5",
          "en": "a negligible share",
          "rest": "微不足道的比例（{{percent5}}）"
        }
      ]
    }
  ]
}].forEach(function (m) { DATA.maps.push(m); });
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