# 四大模块 JSON 数据 Schema（供数据构建参考）

目标：为每年份 `pwa/data/{year}.json` 补充 4 类文章（完形/新题型/翻译/作文）。

## 文章 id 规则
- `{year}_cloze`、`{year}_newtype`、`{year}_translation`、`{year}_writinga`、`{year}_writingb`
- 注意：id 只能含 `[a-z0-9]`（**禁止下划线**），`{year}` 为 4 位年份，如 `2010_cloze`。

## 各类型结构

### 1. 完形 `cloze`
```json
{
  "id": "2010_cloze", "type": "cloze",
  "title": "英文标题", "topic": "中文主题概要", "source": "Section I Use of English",
  "sentences": [ {"id": "2010_cloze_s01", "para": 1, "en": "英文句子（可含 [1] 空格编号）", "cn": "官方译文", "words": []} ],
  "questions": [ {"id": "2010_cloze_q01", "number": 1, "qtype": "完形",
    "stem": "第 1 空：选择最合适的词填入空白 [1]", "stem_cn": "",
    "options": {"A": "选项词1", "B": "选项词2", "C": "选项词3", "D": "选项词4"},
    "options_cn": {"A": "", "B": "", "C": "", "D": ""},
    "answer": "B", "explanation": "官方精解", "related_sentences": ["2010_cloze_s01", "..."]}]
}
```
- 正文需按句拆分成 `sentences`，每句带官方译文（英中句数必须一致）
- `[n]` 占位符放正文句子中，1-20 题对应
- `explanation` 用官方解析文本

### 2. 新题型 `newtype`（三种题型统一用 pool）
```json
{
  "id": "2010_newtype", "type": "newtype",
  "title": "英文标题", "topic": "中文主题", "source": "Section II Part B",
  "pool": {"A": "选项文本", "B": "...", "C": "...", "D": "...", "E": "...", "F": "...", "G": "..."},
  "pool_cn": {"A": "选项中文", "B": "...", "...": "..."},
  "sentences": [ {"id": "2010_newtype_s01", "para": 1, "en": "正文句子", "cn": "官方译文", "words": []} ],
  "questions": [ {"id": "2010_newtype_q41", "number": 41, "qtype": "匹配|小标题|判断",
    "stem": "题干", "stem_cn": "题干中文",
    "options": {}, "options_cn": {},
    "answer": "D", "explanation": "官方精解", "related_sentences": ["..."]} ]
}
```
- `pool` 为共享选项池，`answer` 指向 pool 的 key（字母）
- 三种题型：
  - **多项对应**：pool 是 A-G 右栏表述，stem 是左栏词条（如人名）
  - **小标题对应**：pool 是 A-G 小标题，stem 是段落号（如"第 1 段"或 Q41 对应段落）
  - **判断 T/F**：pool = {"T": "True", "F": "False"}，stem 是待判断的陈述句
- `qtype` 字段值：多项对应="匹配"，小标题对应="小标题"，判断T/F="判断"

### 3. 翻译 `translation`
```json
{
  "id": "2010_translation", "type": "translation",
  "title": "英文标题", "topic": "中文主题", "source": "Section III Translation",
  "ref_cn": "官方全文参考译文（一段文本）",
  "sentences": [ {"id": "2010_translation_s01", "para": 1, "en": "英文句子", "cn": "官方译文", "words": []} ],
  "questions": []
}
```

### 4. 作文 `writing_a` / `writing_b`
```json
{
  "id": "2010_writinga", "type": "writing_a",
  "title": "Part A 应用文：XXX", "topic": "中文主题", "source": "Section IV Writing Part A",
  "sample_en": "官方范文英文", "sample_cn": "官方范文中文",
  "questions": []
}
```
- writing_b 额外有 `"chart_img": "img/{year}_writingb_chart.png"`（由构建者另行渲染，agent 无需生成图片，只需知道存在即可）
- writing_b 的 title/topic 描述图表类型

## 说明
- 所有英文/中文必须来自真题与官方解析文本（不得编造）
- `sentences` 的 en/cn 必须逐句对应，句数一致
- 答案必须来自官方解析（每题解析中的"正确"标记）
- `words` 一律为空数组 `[]`
