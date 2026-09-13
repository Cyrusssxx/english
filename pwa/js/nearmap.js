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
          "name": "The {{chart}} chart presents an uneven distribution among the categories associated with {{题目相关词}}. 该 {{xx}} 图表呈现了与 {{题目相关词}} 有关的不同类别之间不均衡的分布情况。 · 9 年",
          "en": "The {{chart}} chart presents an uneven distribution among the categories associated with {{题目相关词}}.",
          "rest": "该 {{xx}} 图表呈现了与 {{题目相关词}} 有关的不同类别之间不均衡的分布情况。 · 9 年"
        },
        {
          "name": "{{事物1}} accounts for the largest share, at {{百分比1}}. {{事物1}} 所占比例最大，达到 {{百分比1}}。 · 9 年",
          "en": "{{事物1}} accounts for the largest share, at {{百分比1}}.",
          "rest": "{{事物1}} 所占比例最大，达到 {{百分比1}}。 · 9 年"
        },
        {
          "name": "As for {{事物1}} and {{事物2}}, they register {{百分比1}} and {{百分比2}} respectively. 就 {{事物1}} 与 {{事物2}} 而言，它们分别为 {{百分比1}} 和 {{百分比2}}。 · 6 年",
          "en": "As for {{事物1}} and {{事物2}}, they register {{百分比1}} and {{百分比2}} respectively.",
          "rest": "就 {{事物1}} 与 {{事物2}} 而言，它们分别为 {{百分比1}} 和 {{百分比2}}。 · 6 年"
        },
        {
          "name": "In contrast, {{事物4}} and {{事物5}} make up relatively small proportions of {{百分比4}} and {{百分比5}}. 相比之下，{{事物4}} 和 {{事物5}} 所占比例较小，分别为 {{百分比4}} 和 {{百分比5}}。 · 6 年",
          "en": "In contrast, {{事物4}} and {{事物5}} make up relatively small proportions of {{百分比4}} and {{百分比5}}.",
          "rest": "相比之下，{{事物4}} 和 {{事物5}} 所占比例较小，分别为 {{百分比4}} 和 {{百分比5}}。 · 6 年"
        },
        {
          "name": "{{事物2}} and {{事物3}} form the middle group, representing {{百分比2}} and {{百分比3}}, respectively. {{事物2}} 和 {{事物3}} 处于中间位置，分别占 {{百分比2}} 和 {{百分比3}}。 · 4 年",
          "en": "{{事物2}} and {{事物3}} form the middle group, representing {{百分比2}} and {{百分比3}}, respectively.",
          "rest": "{{事物2}} 和 {{事物3}} 处于中间位置，分别占 {{百分比2}} 和 {{百分比3}}。 · 4 年"
        }
      ]
    },
    {
      "name": "第一段 · 动态图描述（4）",
      "color": "#0ea5e9",
      "children": [
        {
          "name": "The line chart shows that the items associated with {{题目相关词}} did not move in a uniform direction during the periods presented. 该折线图表明，与 {{题目相关词}} 有关的不同项目在相应时期内并未朝着相同方向变化。 · 8 年",
          "en": "The line chart shows that the items associated with {{题目相关词}} did not move in a uniform direction during the periods presented.",
          "rest": "该折线图表明，与 {{题目相关词}} 有关的不同项目在相应时期内并未朝着相同方向变化。 · 8 年"
        },
        {
          "name": "{{事物1}} climbed from {{数字1}} in {{时间1}} to {{数字2}} in {{时间2}}, while {{事物2}} rose from {{数字3}} in {{时间3}} to {{数字4}} in {{时间4}}. {{事物1}} 由 {{时间1}} 的 {{数字1}} 上升至 {{时间2}} 的 {{数字2}}，{{事物2}} 则从 {{时间3}} 的 {{数字3}} 增至 {{时间4}} 的 {{数字4}}。 · 8 年",
          "en": "{{事物1}} climbed from {{数字1}} in {{时间1}} to {{数字2}} in {{时间2}}, while {{事物2}} rose from {{数字3}} in {{时间3}} to {{数字4}} in {{时间4}}.",
          "rest": "{{事物1}} 由 {{时间1}} 的 {{数字1}} 上升至 {{时间2}} 的 {{数字2}}，{{事物2}} 则从 {{时间3}} 的 {{数字3}} 增至 {{时间4}} 的 {{数字4}}。 · 8 年"
        },
        {
          "name": "From {{时间1}} to {{时间2}}, {{事物1}} rose from {{数字1}} to {{数字2}}, showing a steady upward trend. 自 {{时间1}} 至 {{时间2}}，{{事物1}} 由 {{数字1}} 升至 {{数字2}}，呈现稳定上升趋势。 · 3 年",
          "en": "From {{时间1}} to {{时间2}}, {{事物1}} rose from {{数字1}} to {{数字2}}, showing a steady upward trend.",
          "rest": "自 {{时间1}} 至 {{时间2}}，{{事物1}} 由 {{数字1}} 升至 {{数字2}}，呈现稳定上升趋势。 · 3 年"
        },
        {
          "name": "By contrast, {{事物3}} fell from {{数字5}} in {{时间5}} to {{数字6}} in {{时间6}}. 相比之下，{{事物3}} 由 {{时间5}} 的 {{数字5}} 下降至 {{时间6}} 的 {{数字6}}。 · 2019",
          "en": "By contrast, {{事物3}} fell from {{数字5}} in {{时间5}} to {{数字6}} in {{时间6}}.",
          "rest": "相比之下，{{事物3}} 由 {{时间5}} 的 {{数字5}} 下降至 {{时间6}} 的 {{数字6}}。 · 2019"
        }
      ]
    },
    {
      "name": "第二段 · 经济类归因（4）",
      "color": "#f97316",
      "children": [
        {
          "name": "Undoubtedly, the country's rapid economic growth has laid a solid material foundation for the emergence of {{题目相关词}}. 毫无疑问，国家经济的飞速发展，为 {{题目相关词}} 的出现奠定了坚实的物质基础。 · 6 年",
          "en": "Undoubtedly, the country's rapid economic growth has laid a solid material foundation for the emergence of {{题目相关词}}.",
          "rest": "毫无疑问，国家经济的飞速发展，为 {{题目相关词}} 的出现奠定了坚实的物质基础。 · 6 年"
        },
        {
          "name": "As the pace of life accelerates, individuals attach greater importance to convenience and efficiency and become increasingly willing to embrace new ways of living. 随着生活节奏加快，个人开始更加重视便利和效率，也更愿意接受新的生活方式。 · 6 年",
          "en": "As the pace of life accelerates, individuals attach greater importance to convenience and efficiency and become increasingly willing to embrace new ways of living.",
          "rest": "随着生活节奏加快，个人开始更加重视便利和效率，也更愿意接受新的生活方式。 · 6 年"
        },
        {
          "name": "Growing public attention to {{题目相关词}} stems from its ability to meet practical needs in everyday life. {{题目相关词}} 之所以受到越来越多关注，是因为它能够回应人们在现实生活中的实际需要。 · 3 年",
          "en": "Growing public attention to {{题目相关词}} stems from its ability to meet practical needs in everyday life.",
          "rest": "{{题目相关词}} 之所以受到越来越多关注，是因为它能够回应人们在现实生活中的实际需要。 · 3 年"
        },
        {
          "name": "Seen in this light, the development of {{题目相关词}} is no coincidence but a natural consequence of broader changes in social life. 由此可见，{{题目相关词}} 的发展并非偶然，而是社会生活发生变化后的自然结果。 · 3 年",
          "en": "Seen in this light, the development of {{题目相关词}} is no coincidence but a natural consequence of broader changes in social life.",
          "rest": "由此可见，{{题目相关词}} 的发展并非偶然，而是社会生活发生变化后的自然结果。 · 3 年"
        }
      ]
    },
    {
      "name": "第二段 · 校园/成长类归因（4）",
      "color": "#eab308",
      "children": [
        {
          "name": "{{题目相关词}} can enable individuals to approach routine tasks with greater maturity, preventing them from giving up too readily in the face of temporary difficulties. {{题目相关词}} 能够使个人以更加成熟的态度处理日常任务，不因暂时困难就轻易放弃。 · 7 年",
          "en": "{{题目相关词}} can enable individuals to approach routine tasks with greater maturity, preventing them from giving up too readily in the face of temporary difficulties.",
          "rest": "{{题目相关词}} 能够使个人以更加成熟的态度处理日常任务，不因暂时困难就轻易放弃。 · 7 年"
        },
        {
          "name": "Ultimately, {{题目相关词}} can not only improve individuals' present conduct but also strengthen their capacity for self-management, thereby laying a solid foundation for their future growth. 最终，{{题目相关词}} 不仅能够改善个人当下的行为表现，也会增强其自我管理能力，为今后的成长提供稳定支持。 · 7 年",
          "en": "Ultimately, {{题目相关词}} can not only improve individuals' present conduct but also strengthen their capacity for self-management, thereby laying a solid foundation for their future growth.",
          "rest": "最终，{{题目相关词}} 不仅能够改善个人当下的行为表现，也会增强其自我管理能力，为今后的成长提供稳定支持。 · 7 年"
        },
        {
          "name": "The influence of {{题目相关词}} is not confined to a single action; rather, it continues to shape the way individuals handle everyday responsibilities. {{题目相关词}} 的作用，并不会局限于某一次行为，而会持续影响个人处理日常事务的方式。 · 6 年",
          "en": "The influence of {{题目相关词}} is not confined to a single action; rather, it continues to shape the way individuals handle everyday responsibilities.",
          "rest": "{{题目相关词}} 的作用，并不会局限于某一次行为，而会持续影响个人处理日常事务的方式。 · 6 年"
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
          "name": "Changes reflected in {{题目相关词}} are closely linked to rising public awareness of personal health and increasingly favorable conditions for physical exercise. {{题目相关词}} 所反映的变化，与公众健康意识的提高和公共运动条件的改善密切相关。 · 3 年",
          "en": "Changes reflected in {{题目相关词}} are closely linked to rising public awareness of personal health and increasingly favorable conditions for physical exercise.",
          "rest": "{{题目相关词}} 所反映的变化，与公众健康意识的提高和公共运动条件的改善密切相关。 · 3 年"
        },
        {
          "name": "As physical exercise becomes increasingly integrated into everyday life, the number of people willing to take part in related activities will continue to grow. 随着体育锻炼逐渐融入日常生活，愿意参与相关活动的人数也会不断增加。 · 3 年",
          "en": "As physical exercise becomes increasingly integrated into everyday life, the number of people willing to take part in related activities will continue to grow.",
          "rest": "随着体育锻炼逐渐融入日常生活，愿意参与相关活动的人数也会不断增加。 · 3 年"
        },
        {
          "name": "For this reason, {{题目相关词}} not only reflects the continued advancement of national fitness but also demonstrates the growing acceptance of healthy living. 正因如此，{{题目相关词}} 不仅体现了全民健身事业的持续推进，也说明健康生活正在得到更加广泛的认可。 · 2 年",
          "en": "For this reason, {{题目相关词}} not only reflects the continued advancement of national fitness but also demonstrates the growing acceptance of healthy living.",
          "rest": "正因如此，{{题目相关词}} 不仅体现了全民健身事业的持续推进，也说明健康生活正在得到更加广泛的认可。 · 2 年"
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
          "name": "{{题目相关词}} can establish a channel of communication between traditional culture and the public, allowing cultural content to be explained with greater clarity. {{题目相关词}} 为传统文化与公众之间建立了交流渠道，使文化内容能够得到更加清楚的解释。 · 2017",
          "en": "{{题目相关词}} can establish a channel of communication between traditional culture and the public, allowing cultural content to be explained with greater clarity.",
          "rest": "{{题目相关词}} 为传统文化与公众之间建立了交流渠道，使文化内容能够得到更加清楚的解释。 · 2017"
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
          "name": "Relevant authorities should provide the necessary support and create favorable conditions under which {{题目相关词}} can play a constructive role. 有关部门应提供必要支持，为 {{题目相关词}} 发挥作用创造良好条件。 · 17 年",
          "en": "Relevant authorities should provide the necessary support and create favorable conditions under which {{题目相关词}} can play a constructive role.",
          "rest": "有关部门应提供必要支持，为 {{题目相关词}} 发挥作用创造良好条件。 · 17 年"
        },
        {
          "name": "Individuals should also make well-informed choices in light of their own circumstances, ensuring that {{题目相关词}} genuinely contributes to their long-term development. 个人也应结合自身情况作出合理选择，使 {{题目相关词}} 真正服务于自身的长期发展。 · 11 年",
          "en": "Individuals should also make well-informed choices in light of their own circumstances, ensuring that {{题目相关词}} genuinely contributes to their long-term development.",
          "rest": "个人也应结合自身情况作出合理选择，使 {{题目相关词}} 真正服务于自身的长期发展。 · 11 年"
        },
        {
          "name": "For {{题目相关词}} to continue exerting a positive influence on personal growth, concerted efforts from all sectors of society are essential. 要使 {{题目相关词}} 持续为个人成长带来积极影响，需要社会各方共同努力。 · 10 年",
          "en": "For {{题目相关词}} to continue exerting a positive influence on personal growth, concerted efforts from all sectors of society are essential.",
          "rest": "要使 {{题目相关词}} 持续为个人成长带来积极影响，需要社会各方共同努力。 · 10 年"
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
          "name": "the leisure activities of the elderly 老年人的日常休闲活动 · 题目相关词",
          "en": "the leisure activities of the elderly",
          "rest": "老年人的日常休闲活动（{{题目相关词}}）"
        },
        {
          "name": "line 折线 · chart",
          "en": "line",
          "rest": "折线（{{chart}}）"
        },
        {
          "name": "dining out 外出就餐 · 题目相关词",
          "en": "dining out",
          "rest": "外出就餐（{{题目相关词}}）"
        },
        {
          "name": "domestic auto brands 国产汽车品牌 · 题目相关词",
          "en": "domestic auto brands",
          "rest": "国产汽车品牌（{{题目相关词}}）"
        },
        {
          "name": "express delivery 快递服务 · 题目相关词",
          "en": "express delivery",
          "rest": "快递服务（{{题目相关词}}）"
        },
        {
          "name": "festival spending 节日花销 · 题目相关词",
          "en": "festival spending",
          "rest": "节日花销（{{题目相关词}}）"
        },
        {
          "name": "further education 继续深造 · 题目相关词",
          "en": "further education",
          "rest": "继续深造（{{题目相关词}}）"
        },
        {
          "name": "health literacy 健康素养 · 题目相关词",
          "en": "health literacy",
          "rest": "健康素养（{{题目相关词}}）"
        },
        {
          "name": "job satisfaction 工作满意度 · 题目相关词",
          "en": "job satisfaction",
          "rest": "工作满意度（{{题目相关词}}）"
        },
        {
          "name": "labor practice courses 劳动实践课 · 题目相关词",
          "en": "labor practice courses",
          "rest": "劳动实践课（{{题目相关词}}）"
        },
        {
          "name": "mobile reading 手机阅读 · 题目相关词",
          "en": "mobile reading",
          "rest": "手机阅读（{{题目相关词}}）"
        },
        {
          "name": "mobile services 手机服务 · 题目相关词",
          "en": "mobile services",
          "rest": "手机服务（{{题目相关词}}）"
        },
        {
          "name": "museums 博物馆 · 题目相关词",
          "en": "museums",
          "rest": "博物馆（{{题目相关词}}）"
        },
        {
          "name": "outdoor activities 户外活动 · 题目相关词",
          "en": "outdoor activities",
          "rest": "户外活动（{{题目相关词}}）"
        },
        {
          "name": "part-time jobs 兼职 · 题目相关词",
          "en": "part-time jobs",
          "rest": "兼职（{{题目相关词}}）"
        },
        {
          "name": "physical exercise 体育锻炼 · 题目相关词",
          "en": "physical exercise",
          "rest": "体育锻炼（{{题目相关词}}）"
        },
        {
          "name": "travel 旅行 · 题目相关词",
          "en": "travel",
          "rest": "旅行（{{题目相关词}}）"
        },
        {
          "name": "urbanization 城镇化 · 题目相关词",
          "en": "urbanization",
          "rest": "城镇化（{{题目相关词}}）"
        },
        {
          "name": "table 表格 · chart",
          "en": "table",
          "rest": "表格（{{chart}}）"
        },
        {
          "name": "Spring Festival spending 春节花销 · 题目相关词",
          "en": "Spring Festival spending",
          "rest": "春节花销（{{题目相关词}}）"
        },
        {
          "name": "express delivery volumes nationwide and in rural areas 全国与农村的快递业务量 · 题目相关词",
          "en": "express delivery volumes nationwide and in rural areas",
          "rest": "全国与农村的快递业务量（{{题目相关词}}）"
        },
        {
          "name": "graduates' choices after university 本科毕业生的去向 · 题目相关词",
          "en": "graduates' choices after university",
          "rest": "本科毕业生的去向（{{题目相关词}}）"
        },
        {
          "name": "job satisfaction across the age groups 各年龄段的工作满意度 · 题目相关词",
          "en": "job satisfaction across the age groups",
          "rest": "各年龄段的工作满意度（{{题目相关词}}）"
        },
        {
          "name": "mobile-phone subscriptions in developing and developed countries 发展中国家与发达国家的手机订阅量 · 题目相关词",
          "en": "mobile-phone subscriptions in developing and developed countries",
          "rest": "发展中国家与发达国家的手机订阅量（{{题目相关词}}）"
        },
        {
          "name": "the benefits students gained from labor practice courses 学生从劳动实践课中得到的收获 · 题目相关词",
          "en": "the benefits students gained from labor practice courses",
          "rest": "学生从劳动实践课中得到的收获（{{题目相关词}}）"
        },
        {
          "name": "the exercise methods chosen by city residents 城市居民的锻炼方式 · 题目相关词",
          "en": "the exercise methods chosen by city residents",
          "rest": "城市居民的锻炼方式（{{题目相关词}}）"
        },
        {
          "name": "the factors consumers consider when choosing a restaurant 消费者选择餐厅时的关注因素 · 题目相关词",
          "en": "the factors consumers consider when choosing a restaurant",
          "rest": "消费者选择餐厅时的关注因素（{{题目相关词}}）"
        },
        {
          "name": "the health literacy rate of Chinese residents 中国居民的健康素养水平 · 题目相关词",
          "en": "the health literacy rate of Chinese residents",
          "rest": "中国居民的健康素养水平（{{题目相关词}}）"
        },
        {
          "name": "the market shares of Chinese, Japanese and American auto brands 中国、日本与美国汽车品牌的市场份额 · 题目相关词",
          "en": "the market shares of Chinese, Japanese and American auto brands",
          "rest": "中国、日本与美国汽车品牌的市场份额（{{题目相关词}}）"
        },
        {
          "name": "the number of museums and museum visitors 博物馆数量与参观人数 · 题目相关词",
          "en": "the number of museums and museum visitors",
          "rest": "博物馆数量与参观人数（{{题目相关词}}）"
        },
        {
          "name": "the perceived benefits of children's outdoor activities 人们看重的儿童户外活动益处 · 题目相关词",
          "en": "the perceived benefits of children's outdoor activities",
          "rest": "人们看重的儿童户外活动益处（{{题目相关词}}）"
        },
        {
          "name": "the proportion of college students taking part-time jobs 大学生兼职比例 · 题目相关词",
          "en": "the proportion of college students taking part-time jobs",
          "rest": "大学生兼职比例（{{题目相关词}}）"
        },
        {
          "name": "the purposes of mobile reading among college students 大学生的手机阅读目的 · 题目相关词",
          "en": "the purposes of mobile reading among college students",
          "rest": "大学生的手机阅读目的（{{题目相关词}}）"
        },
        {
          "name": "the purposes of travel among college students 大学生的旅游目的 · 题目相关词",
          "en": "the purposes of travel among college students",
          "rest": "大学生的旅游目的（{{题目相关词}}）"
        },
        {
          "name": "the urban and rural population 城镇与农村人口 · 题目相关词",
          "en": "the urban and rural population",
          "rest": "城镇与农村人口（{{题目相关词}}）"
        }
      ]
    },
    {
      "name": "主体 · 事物（63）",
      "color": "#8b5cf6",
      "children": [
        {
          "name": "Appreciating the beauty of the scenery 欣赏风景 · 事物1",
          "en": "Appreciating the beauty of the scenery",
          "rest": "欣赏风景（{{事物1}}）"
        },
        {
          "name": "Chinese brands 国产品牌 · 事物1",
          "en": "Chinese brands",
          "rest": "国产品牌（{{事物1}}）"
        },
        {
          "name": "Distinguishing features 餐厅特色 · 事物1",
          "en": "Distinguishing features",
          "rest": "餐厅特色（{{事物1}}）"
        },
        {
          "name": "Gaining knowledge 获取知识 · 事物1",
          "en": "Gaining knowledge",
          "rest": "获取知识（{{事物1}}）"
        },
        {
          "name": "Gaining relevant knowledge 获得相关知识 · 事物1",
          "en": "Gaining relevant knowledge",
          "rest": "获得相关知识（{{事物1}}）"
        },
        {
          "name": "Satisfying curiosity 满足好奇心 · 事物1",
          "en": "Satisfying curiosity",
          "rest": "满足好奇心（{{事物1}}）"
        },
        {
          "name": "Subscriptions in developing countries 发展中国家的订阅量 · 事物1",
          "en": "Subscriptions in developing countries",
          "rest": "发展中国家的订阅量（{{事物1}}）"
        },
        {
          "name": "The group over 50 50 岁以上群体 · 事物1",
          "en": "The group over 50",
          "rest": "50 岁以上群体（{{事物1}}）"
        },
        {
          "name": "The health literacy rate 健康素养水平 · 事物1",
          "en": "The health literacy rate",
          "rest": "健康素养水平（{{事物1}}）"
        },
        {
          "name": "The national volume 全国业务量 · 事物1",
          "en": "The national volume",
          "rest": "全国业务量（{{事物1}}）"
        },
        {
          "name": "The number of museums 博物馆数量 · 事物1",
          "en": "The number of museums",
          "rest": "博物馆数量（{{事物1}}）"
        },
        {
          "name": "The rate 这一比例 · 事物1",
          "en": "The rate",
          "rest": "这一比例（{{事物1}}）"
        },
        {
          "name": "The urban population 城镇人口 · 事物1",
          "en": "The urban population",
          "rest": "城镇人口（{{事物1}}）"
        },
        {
          "name": "Travelling, gift giving and dinners with friends or relatives 旅行、送礼以及与亲友聚餐 · 事物1",
          "en": "Travelling, gift giving and dinners with friends or relatives",
          "rest": "旅行、送礼以及与亲友聚餐（{{事物1}}）"
        },
        {
          "name": "Watching television 看电视 · 事物1",
          "en": "Watching television",
          "rest": "看电视（{{事物1}}）"
        },
        {
          "name": "Working out alone 独自锻炼 · 事物1",
          "en": "Working out alone",
          "rest": "独自锻炼（{{事物1}}）"
        },
        {
          "name": "the proportion entering employment 就业比例 · 事物1",
          "en": "the proportion entering employment",
          "rest": "就业比例（{{事物1}}）"
        },
        {
          "name": "American brands 美系品牌 · 事物2",
          "en": "American brands",
          "rest": "美系品牌（{{事物2}}）"
        },
        {
          "name": "Relieving pressure 缓解压力 · 事物2",
          "en": "Relieving pressure",
          "rest": "缓解压力（{{事物2}}）"
        },
        {
          "name": "enhancing observation skills 促进观察力 · 事物2",
          "en": "enhancing observation skills",
          "rest": "促进观察力（{{事物2}}）"
        },
        {
          "name": "exercising with friends 与朋友一起锻炼 · 事物2",
          "en": "exercising with friends",
          "rest": "与朋友一起锻炼（{{事物2}}）"
        },
        {
          "name": "gifts for colleagues 给同事的礼物 · 事物2",
          "en": "gifts for colleagues",
          "rest": "给同事的礼物（{{事物2}}）"
        },
        {
          "name": "improving practical ability 提升实践能力 · 事物2",
          "en": "improving practical ability",
          "rest": "提升实践能力（{{事物2}}）"
        },
        {
          "name": "killing time 消磨时间 · 事物2",
          "en": "killing time",
          "rest": "消磨时间（{{事物2}}）"
        },
        {
          "name": "service 服务 · 事物2",
          "en": "service",
          "rest": "服务（{{事物2}}）"
        },
        {
          "name": "taking walks 散步 · 事物2",
          "en": "taking walks",
          "rest": "散步（{{事物2}}）"
        },
        {
          "name": "the number of visitors 参观人数 · 事物2",
          "en": "the number of visitors",
          "rest": "参观人数（{{事物2}}）"
        },
        {
          "name": "the proportion in the graduation year 毕业当年的比例 · 事物2",
          "en": "the proportion in the graduation year",
          "rest": "毕业当年的比例（{{事物2}}）"
        },
        {
          "name": "the proportion pursuing further education 升学比例 · 事物2",
          "en": "the proportion pursuing further education",
          "rest": "升学比例（{{事物2}}）"
        },
        {
          "name": "the rate in the same period 同期的这一比例 · 事物2",
          "en": "the rate in the same period",
          "rest": "同期的这一比例（{{事物2}}）"
        },
        {
          "name": "the rural population 农村人口 · 事物2",
          "en": "the rural population",
          "rest": "农村人口（{{事物2}}）"
        },
        {
          "name": "the rural volume 农村业务量 · 事物2",
          "en": "the rural volume",
          "rest": "农村业务量（{{事物2}}）"
        },
        {
          "name": "those aged 41 to 50 41 至 50 岁的员工 · 事物2",
          "en": "those aged 41 to 50",
          "rest": "41 至 50 岁的员工（{{事物2}}）"
        },
        {
          "name": "those in developed countries 发达国家同期的订阅量 · 事物2",
          "en": "those in developed countries",
          "rest": "发达国家同期的订阅量（{{事物2}}）"
        },
        {
          "name": "Japanese brands 日系品牌 · 事物3",
          "en": "Japanese brands",
          "rest": "日系品牌（{{事物3}}）"
        },
        {
          "name": "employees aged 31 to 40 31 至 40 岁的员工 · 事物3",
          "en": "employees aged 31 to 40",
          "rest": "31 至 40 岁的员工（{{事物3}}）"
        },
        {
          "name": "household decorations 家庭装饰 · 事物3",
          "en": "household decorations",
          "rest": "家庭装饰（{{事物3}}）"
        },
        {
          "name": "improving physical fitness 强身健体 · 事物3",
          "en": "improving physical fitness",
          "rest": "强身健体（{{事物3}}）"
        },
        {
          "name": "obtaining cheerful moods 获得愉悦心情 · 事物3",
          "en": "obtaining cheerful moods",
          "rest": "获得愉悦心情（{{事物3}}）"
        },
        {
          "name": "obtaining information 获取信息 · 事物3",
          "en": "obtaining information",
          "rest": "获取信息（{{事物3}}）"
        },
        {
          "name": "other aims 其他目的 · 事物3",
          "en": "other aims",
          "rest": "其他目的（{{事物3}}）"
        },
        {
          "name": "planting flowers 养花 · 事物3",
          "en": "planting flowers",
          "rest": "养花（{{事物3}}）"
        },
        {
          "name": "the dining environment 就餐环境 · 事物3",
          "en": "the dining environment",
          "rest": "就餐环境（{{事物3}}）"
        },
        {
          "name": "the proportion starting a business 创业比例 · 事物3",
          "en": "the proportion starting a business",
          "rest": "创业比例（{{事物3}}）"
        },
        {
          "name": "working out with family members 与家人一起锻炼 · 事物3",
          "en": "working out with family members",
          "rest": "与家人一起锻炼（{{事物3}}）"
        },
        {
          "name": "employees aged 40 or younger 40 岁及以下员工 · 事物4",
          "en": "employees aged 40 or younger",
          "rest": "40 岁及以下员工（{{事物4}}）"
        },
        {
          "name": "enhancing cooperative ability 增强合作能力 · 事物4",
          "en": "enhancing cooperative ability",
          "rest": "增强合作能力（{{事物4}}）"
        },
        {
          "name": "making more friends 广交朋友 · 事物4",
          "en": "making more friends",
          "rest": "广交朋友（{{事物4}}）"
        },
        {
          "name": "other items such as fireworks 烟花等其他项目 · 事物4",
          "en": "other items such as fireworks",
          "rest": "烟花等其他项目（{{事物4}}）"
        },
        {
          "name": "other purposes 其他目的 · 事物4",
          "en": "other purposes",
          "rest": "其他目的（{{事物4}}）"
        },
        {
          "name": "playing team sports 参加团队运动 · 事物4",
          "en": "playing team sports",
          "rest": "参加团队运动（{{事物4}}）"
        },
        {
          "name": "price 价格 · 事物4",
          "en": "price",
          "rest": "价格（{{事物4}}）"
        },
        {
          "name": "reading 阅读 · 事物4",
          "en": "reading",
          "rest": "阅读（{{事物4}}）"
        },
        {
          "name": "strengthening parent-child interaction 增强亲子互动 · 事物4",
          "en": "strengthening parent-child interaction",
          "rest": "增强亲子互动（{{事物4}}）"
        },
        {
          "name": "fostering independence 培养独立能力 · 事物5",
          "en": "fostering independence",
          "rest": "培养独立能力（{{事物5}}）"
        },
        {
          "name": "miscellaneous spending 杂项支出 · 事物5",
          "en": "miscellaneous spending",
          "rest": "杂项支出（{{事物5}}）"
        },
        {
          "name": "other benefits 其他益处 · 事物5",
          "en": "other benefits",
          "rest": "其他益处（{{事物5}}）"
        },
        {
          "name": "other factors 其他因素 · 事物5",
          "en": "other factors",
          "rest": "其他因素（{{事物5}}）"
        },
        {
          "name": "other forms of exercise 其他锻炼形式 · 事物5",
          "en": "other forms of exercise",
          "rest": "其他锻炼形式（{{事物5}}）"
        },
        {
          "name": "other gains 其他收获 · 事物5",
          "en": "other gains",
          "rest": "其他收获（{{事物5}}）"
        },
        {
          "name": "playing chess 下棋 · 事物5",
          "en": "playing chess",
          "rest": "下棋（{{事物5}}）"
        },
        {
          "name": "the remaining aims 其余目标 · 事物5",
          "en": "the remaining aims",
          "rest": "其余目标（{{事物5}}）"
        },
        {
          "name": "the remaining respondents 其余受访者 · 事物5",
          "en": "the remaining respondents",
          "rest": "其余受访者（{{事物5}}）"
        }
      ]
    },
    {
      "name": "数据 · 数值（36）",
      "color": "#f59e0b",
      "children": [
        {
          "name": "0.5 billion 5 亿 · 数字1",
          "en": "0.5 billion",
          "rest": "5 亿（{{数字1}}）"
        },
        {
          "name": "300 million 3 亿 · 数字1",
          "en": "300 million",
          "rest": "3 亿（{{数字1}}）"
        },
        {
          "name": "4,169 4169 · 数字1",
          "en": "4,169",
          "rest": "4169（{{数字1}}）"
        },
        {
          "name": "51 billion pieces 510 亿件 · 数字1",
          "en": "51 billion pieces",
          "rest": "510 亿件（{{数字1}}）"
        },
        {
          "name": "67.77% 67.77% · 数字1",
          "en": "67.77%",
          "rest": "67.77%（{{数字1}}）"
        },
        {
          "name": "68.1% 68.1% · 数字1",
          "en": "68.1%",
          "rest": "68.1%（{{数字1}}）"
        },
        {
          "name": "8.80% 8.80% · 数字1",
          "en": "8.80%",
          "rest": "8.80%（{{数字1}}）"
        },
        {
          "name": "a modest share 一个不大的份额 · 数字1",
          "en": "a modest share",
          "rest": "一个不大的份额（{{数字1}}）"
        },
        {
          "name": "25.40% 25.40% · 数字2",
          "en": "25.40%",
          "rest": "25.40%（{{数字2}}）"
        },
        {
          "name": "4 billion 40 亿 · 数字2",
          "en": "4 billion",
          "rest": "40 亿（{{数字2}}）"
        },
        {
          "name": "4,692 4692 · 数字2",
          "en": "4,692",
          "rest": "4692（{{数字2}}）"
        },
        {
          "name": "60.7% 60.7% · 数字2",
          "en": "60.7%",
          "rest": "60.7%（{{数字2}}）"
        },
        {
          "name": "670 million 6.7 亿 · 数字2",
          "en": "670 million",
          "rest": "6.7 亿（{{数字2}}）"
        },
        {
          "name": "83 billion pieces 830 亿件 · 数字2",
          "en": "83 billion pieces",
          "rest": "830 亿件（{{数字2}}）"
        },
        {
          "name": "88.24% 88.24% · 数字2",
          "en": "88.24%",
          "rest": "88.24%（{{数字2}}）"
        },
        {
          "name": "the leading position 领先地位 · 数字2",
          "en": "the leading position",
          "rest": "领先地位（{{数字2}}）"
        },
        {
          "name": "0.7 billion 7 亿 · 数字3",
          "en": "0.7 billion",
          "rest": "7 亿（{{数字3}}）"
        },
        {
          "name": "12 billion pieces 120 亿件 · 数字3",
          "en": "12 billion pieces",
          "rest": "120 亿件（{{数字3}}）"
        },
        {
          "name": "26.3% 26.3% · 数字3",
          "en": "26.3%",
          "rest": "26.3%（{{数字3}}）"
        },
        {
          "name": "637 million 6.37 亿 · 数字3",
          "en": "637 million",
          "rest": "6.37 亿（{{数字3}}）"
        },
        {
          "name": "8.80% 8.80% · 数字3",
          "en": "8.80%",
          "rest": "8.80%（{{数字3}}）"
        },
        {
          "name": "820 million 8.2 亿 · 数字3",
          "en": "820 million",
          "rest": "8.2 亿（{{数字3}}）"
        },
        {
          "name": "83.7% 83.7% · 数字3",
          "en": "83.7%",
          "rest": "83.7%（{{数字3}}）"
        },
        {
          "name": "a small share 一个较小的份额 · 数字3",
          "en": "a small share",
          "rest": "一个较小的份额（{{数字3}}）"
        },
        {
          "name": "1 billion 10 亿 · 数字4",
          "en": "1 billion",
          "rest": "10 亿（{{数字4}}）"
        },
        {
          "name": "25.40% 25.40% · 数字4",
          "en": "25.40%",
          "rest": "25.40%（{{数字4}}）"
        },
        {
          "name": "30 billion pieces 300 亿件 · 数字4",
          "en": "30 billion pieces",
          "rest": "300 亿件（{{数字4}}）"
        },
        {
          "name": "34.0% 34.0% · 数字4",
          "en": "34.0%",
          "rest": "34.0%（{{数字4}}）"
        },
        {
          "name": "680 million 6.8 亿 · 数字4",
          "en": "680 million",
          "rest": "6.8 亿（{{数字4}}）"
        },
        {
          "name": "88.24% 88.24% · 数字4",
          "en": "88.24%",
          "rest": "88.24%（{{数字4}}）"
        },
        {
          "name": "954 million 9.54 亿 · 数字4",
          "en": "954 million",
          "rest": "9.54 亿（{{数字4}}）"
        },
        {
          "name": "a slightly larger share 略大的份额 · 数字4",
          "en": "a slightly larger share",
          "rest": "略大的份额（{{数字4}}）"
        },
        {
          "name": "1.3% 1.3% · 数字5",
          "en": "1.3%",
          "rest": "1.3%（{{数字5}}）"
        },
        {
          "name": "their peak level 其最高水平 · 数字5",
          "en": "their peak level",
          "rest": "其最高水平（{{数字5}}）"
        },
        {
          "name": "2.6% 2.6% · 数字6",
          "en": "2.6%",
          "rest": "2.6%（{{数字6}}）"
        },
        {
          "name": "a much lower level 远低于此的水平 · 数字6",
          "en": "a much lower level",
          "rest": "远低于此的水平（{{数字6}}）"
        }
      ]
    },
    {
      "name": "时间（34）",
      "color": "#3b82f6",
      "children": [
        {
          "name": "2013 2013 年 · 时间1",
          "en": "2013",
          "rest": "2013 年（{{时间1}}）"
        },
        {
          "name": "2013 2013 年 · 时间3",
          "en": "2013",
          "rest": "2013 年（{{时间3}}）"
        },
        {
          "name": "1990 1990 年 · 时间1",
          "en": "1990",
          "rest": "1990 年（{{时间1}}）"
        },
        {
          "name": "2000 2000 年 · 时间1",
          "en": "2000",
          "rest": "2000 年（{{时间1}}）"
        },
        {
          "name": "2012 2012 年 · 时间1",
          "en": "2012",
          "rest": "2012 年（{{时间1}}）"
        },
        {
          "name": "2018 2018 年 · 时间1",
          "en": "2018",
          "rest": "2018 年（{{时间1}}）"
        },
        {
          "name": "the earlier period 前一时期 · 时间1",
          "en": "the earlier period",
          "rest": "前一时期（{{时间1}}）"
        },
        {
          "name": "the first year 大一 · 时间1",
          "en": "the first year",
          "rest": "大一（{{时间1}}）"
        },
        {
          "name": "2008 2008 年 · 时间2",
          "en": "2008",
          "rest": "2008 年（{{时间2}}）"
        },
        {
          "name": "2010 2010 年 · 时间2",
          "en": "2010",
          "rest": "2010 年（{{时间2}}）"
        },
        {
          "name": "2015 2015 年 · 时间2",
          "en": "2015",
          "rest": "2015 年（{{时间2}}）"
        },
        {
          "name": "2018 2018 年 · 时间2",
          "en": "2018",
          "rest": "2018 年（{{时间2}}）"
        },
        {
          "name": "2020 2020 年 · 时间2",
          "en": "2020",
          "rest": "2020 年（{{时间2}}）"
        },
        {
          "name": "2021 2021 年 · 时间2",
          "en": "2021",
          "rest": "2021 年（{{时间2}}）"
        },
        {
          "name": "the final year 大四 · 时间2",
          "en": "the final year",
          "rest": "大四（{{时间2}}）"
        },
        {
          "name": "the later period 后一时期 · 时间2",
          "en": "the later period",
          "rest": "后一时期（{{时间2}}）"
        },
        {
          "name": "1990 1990 年 · 时间3",
          "en": "1990",
          "rest": "1990 年（{{时间3}}）"
        },
        {
          "name": "2000 2000 年 · 时间3",
          "en": "2000",
          "rest": "2000 年（{{时间3}}）"
        },
        {
          "name": "2012 2012 年 · 时间3",
          "en": "2012",
          "rest": "2012 年（{{时间3}}）"
        },
        {
          "name": "2018 2018 年 · 时间3",
          "en": "2018",
          "rest": "2018 年（{{时间3}}）"
        },
        {
          "name": "the earlier period 前一时期 · 时间3",
          "en": "the earlier period",
          "rest": "前一时期（{{时间3}}）"
        },
        {
          "name": "the third year 大三 · 时间3",
          "en": "the third year",
          "rest": "大三（{{时间3}}）"
        },
        {
          "name": "2008 2008 年 · 时间4",
          "en": "2008",
          "rest": "2008 年（{{时间4}}）"
        },
        {
          "name": "2010 2010 年 · 时间4",
          "en": "2010",
          "rest": "2010 年（{{时间4}}）"
        },
        {
          "name": "2015 2015 年 · 时间4",
          "en": "2015",
          "rest": "2015 年（{{时间4}}）"
        },
        {
          "name": "2018 2018 年 · 时间4",
          "en": "2018",
          "rest": "2018 年（{{时间4}}）"
        },
        {
          "name": "2020 2020 年 · 时间4",
          "en": "2020",
          "rest": "2020 年（{{时间4}}）"
        },
        {
          "name": "2021 2021 年 · 时间4",
          "en": "2021",
          "rest": "2021 年（{{时间4}}）"
        },
        {
          "name": "the final year 大四 · 时间4",
          "en": "the final year",
          "rest": "大四（{{时间4}}）"
        },
        {
          "name": "the later period 后一时期 · 时间4",
          "en": "the later period",
          "rest": "后一时期（{{时间4}}）"
        },
        {
          "name": "2013 2013 年 · 时间5",
          "en": "2013",
          "rest": "2013 年（{{时间5}}）"
        },
        {
          "name": "the earlier period 前一时期 · 时间5",
          "en": "the earlier period",
          "rest": "前一时期（{{时间5}}）"
        },
        {
          "name": "2018 2018 年 · 时间6",
          "en": "2018",
          "rest": "2018 年（{{时间6}}）"
        },
        {
          "name": "the later period 后一时期 · 时间6",
          "en": "the later period",
          "rest": "后一时期（{{时间6}}）"
        }
      ]
    },
    {
      "name": "数据 · 占比（42）",
      "color": "#ef4444",
      "children": [
        {
          "name": "a still smaller share 更小的比例 · 百分比5",
          "en": "a still smaller share",
          "rest": "更小的比例（{{百分比5}}）"
        },
        {
          "name": "36.3% 36.3% · 百分比1",
          "en": "36.3%",
          "rest": "36.3%（{{百分比1}}）"
        },
        {
          "name": "37% 37% · 百分比1",
          "en": "37%",
          "rest": "37%（{{百分比1}}）"
        },
        {
          "name": "40% 40% · 百分比1",
          "en": "40%",
          "rest": "40%（{{百分比1}}）"
        },
        {
          "name": "54.6% 54.6% · 百分比1",
          "en": "54.6%",
          "rest": "54.6%（{{百分比1}}）"
        },
        {
          "name": "59.5% 59.5% · 百分比1",
          "en": "59.5%",
          "rest": "59.5%（{{百分比1}}）"
        },
        {
          "name": "80% of the total 总额的 80% · 百分比1",
          "en": "80% of the total",
          "rest": "总额的 80%（{{百分比1}}）"
        },
        {
          "name": "90.8% 90.8% · 百分比1",
          "en": "90.8%",
          "rest": "90.8%（{{百分比1}}）"
        },
        {
          "name": "91.3% 91.3% · 百分比1",
          "en": "91.3%",
          "rest": "91.3%（{{百分比1}}）"
        },
        {
          "name": "slightly over half of the respondents 略超受访者半数 · 百分比1",
          "en": "slightly over half of the respondents",
          "rest": "略超受访者半数（{{百分比1}}）"
        },
        {
          "name": "21.3% 21.3% · 百分比2",
          "en": "21.3%",
          "rest": "21.3%（{{百分比2}}）"
        },
        {
          "name": "26.8% 26.8% · 百分比2",
          "en": "26.8%",
          "rest": "26.8%（{{百分比2}}）"
        },
        {
          "name": "33% 33% · 百分比2",
          "en": "33%",
          "rest": "33%（{{百分比2}}）"
        },
        {
          "name": "47.7% 47.7% · 百分比2",
          "en": "47.7%",
          "rest": "47.7%（{{百分比2}}）"
        },
        {
          "name": "54.5% 54.5% · 百分比2",
          "en": "54.5%",
          "rest": "54.5%（{{百分比2}}）"
        },
        {
          "name": "68.3% 68.3% · 百分比2",
          "en": "68.3%",
          "rest": "68.3%（{{百分比2}}）"
        },
        {
          "name": "84.8% 84.8% · 百分比2",
          "en": "84.8%",
          "rest": "84.8%（{{百分比2}}）"
        },
        {
          "name": "a small share 一个很小的比例 · 百分比2",
          "en": "a small share",
          "rest": "一个很小的比例（{{百分比2}}）"
        },
        {
          "name": "the lowest level 最低水平 · 百分比2",
          "en": "the lowest level",
          "rest": "最低水平（{{百分比2}}）"
        },
        {
          "name": "15% 15% · 百分比3",
          "en": "15%",
          "rest": "15%（{{百分比3}}）"
        },
        {
          "name": "17.0% 17.0% · 百分比3",
          "en": "17.0%",
          "rest": "17.0%（{{百分比3}}）"
        },
        {
          "name": "23.8% 23.8% · 百分比3",
          "en": "23.8%",
          "rest": "23.8%（{{百分比3}}）"
        },
        {
          "name": "23.9% 23.9% · 百分比3",
          "en": "23.9%",
          "rest": "23.9%（{{百分比3}}）"
        },
        {
          "name": "34.7% 34.7% · 百分比3",
          "en": "34.7%",
          "rest": "34.7%（{{百分比3}}）"
        },
        {
          "name": "37.2% 37.2% · 百分比3",
          "en": "37.2%",
          "rest": "37.2%（{{百分比3}}）"
        },
        {
          "name": "54.4% 54.4% · 百分比3",
          "en": "54.4%",
          "rest": "54.4%（{{百分比3}}）"
        },
        {
          "name": "a modest level 中等水平 · 百分比3",
          "en": "a modest level",
          "rest": "中等水平（{{百分比3}}）"
        },
        {
          "name": "a smaller share 更小的比例 · 百分比3",
          "en": "a smaller share",
          "rest": "更小的比例（{{百分比3}}）"
        },
        {
          "name": "12% 12% · 百分比4",
          "en": "12%",
          "rest": "12%（{{百分比4}}）"
        },
        {
          "name": "16.7% 16.7% · 百分比4",
          "en": "16.7%",
          "rest": "16.7%（{{百分比4}}）"
        },
        {
          "name": "2.2% 2.2% · 百分比4",
          "en": "2.2%",
          "rest": "2.2%（{{百分比4}}）"
        },
        {
          "name": "31.8% 31.8% · 百分比4",
          "en": "31.8%",
          "rest": "31.8%（{{百分比4}}）"
        },
        {
          "name": "32.6% 32.6% · 百分比4",
          "en": "32.6%",
          "rest": "32.6%（{{百分比4}}）"
        },
        {
          "name": "33.2% 33.2% · 百分比4",
          "en": "33.2%",
          "rest": "33.2%（{{百分比4}}）"
        },
        {
          "name": "8.4% 8.4% · 百分比4",
          "en": "8.4%",
          "rest": "8.4%（{{百分比4}}）"
        },
        {
          "name": "9% 9% · 百分比4",
          "en": "9%",
          "rest": "9%（{{百分比4}}）"
        },
        {
          "name": "less than 16% 不足 16% · 百分比4",
          "en": "less than 16%",
          "rest": "不足 16%（{{百分比4}}）"
        },
        {
          "name": "18.4% 18.4% · 百分比5",
          "en": "18.4%",
          "rest": "18.4%（{{百分比5}}）"
        },
        {
          "name": "4.7% 4.7% · 百分比5",
          "en": "4.7%",
          "rest": "4.7%（{{百分比5}}）"
        },
        {
          "name": "6% 6% · 百分比5",
          "en": "6%",
          "rest": "6%（{{百分比5}}）"
        },
        {
          "name": "8% 8% · 百分比5",
          "en": "8%",
          "rest": "8%（{{百分比5}}）"
        },
        {
          "name": "a negligible share 微不足道的比例 · 百分比5",
          "en": "a negligible share",
          "rest": "微不足道的比例（{{百分比5}}）"
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