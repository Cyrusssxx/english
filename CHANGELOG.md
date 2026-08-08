# 更新日志 — 考研英语二真题精翻 PWA

## [en2-v45] 2026-08-06

### 修复：一键记录批量加的生词背出来仍是字母序

- **问题**：v44 的 seq 迁移按 `added_at` 分配序号，但「一键记录/记录本篇难词」批量加入的词时间戳相同，迁移时退化为 IndexedDB 主键（word）字典序 → 背词仍是 abcd。
- **修复**：seq 迁移升级为 v2——全部生词按**来源文章 + 句序**（`article_id` + `sentence_id`）重新分配序号：同一篇文章的词按出现先后排列，跨文章按年份排列，无来源词排最后。此后背词（含只学新词）按加入/记录顺序，不再是字母序。新加入的词（v44 起已带正确 seq）也统一纳入重排，保证整体顺序一致。

## [en2-v44] 2026-08-06

### 背词顺序修复 + 「熟」按钮移到卡片左上角 + 快捷键

- **顺序修复**：上一版按 `added_at` 排序，但批量加入（一键记录/导入）同事务内时间戳相同，仍退化为字母序。新增全局自增 `seq` 字段（`nextSeq()`），`addVocab`/`addWordsBulk` 每条分配，背词队列与生词本列表按 `seq` 排序（历史无 seq 记录迁移时按 `added_at` 升序补号）。**背词顺序=加入生词本顺序，不再是 abcd。**
- **「熟」按钮**：从底部操作条移到**单词卡左上角**（紧邻"新词/复习"标签），底部只保留「✕ 不认识」「✓ 认识」；并加入快捷键体系（默认 **M**），设置面板可自定义绑定。
- 快捷键默认键位保持原样（不认识←、认识→、显示释义空格、回退退格、收藏 F）。

## [en2-v43] 2026-08-06

### 背单词改进：按加入生词本顺序 + 新增「熟」按钮

- **顺序**：`buildQueue` 中到期复习、新词、未到期词各自按 `added_at`（加入生词本时间）升序排列，不再按字母顺序（原为 IndexedDB 主键 word 字母序）。复习优先结构不变。
- **「熟」按钮**：卡片翻面后操作条新增「熟」按钮——点击将该词标记为已掌握（interval=30、state=review），不再进入待背/复习队列，计入「已掌握」统计；可用「↶ 回退」撤销误点。

## [en2-v42] 2026-08-06

### 修复：精翻点词加入生词本进错词书 + 误显示「已加入」

- **问题**：精翻页点高亮词「加入生词本」实际加进的是内置词书 default（收藏目标词书默认值），而非用户**在背单词页顶部指定的背词范围词书**；且「已加入」状态判断基于全部词书，导致「显示已加入、实则不在指定词书」。
- **修复**：新增 `getVocabTarget()`（storage.js）——背词范围选了具体词书则用该词书，否则回退收藏目标词书；article.js 中所有点词/词组加入、一键记录均改用目标词书；`vocabSet` 只含目标词书的词，显示「已加入」与实际归属一致。

## [en2-v41] 2026-08-06

### 作文页新增「官方解析 · 审题与模板」板块

- **背景**：作文页此前只有题目要求、图表、范文、词汇储备，缺少官方解析对题目/范文的解读要点。
- **内容**：新增 `writing_analysis` 字段（2010-2023 全部 28 篇小/大作文，`tools/merge_analysis.py` 合并，4 个 agent 并行从 notes 提取）：
  - **解读要点 prompt**：小作文=审题谋篇的指令关键词解读与要点归纳；大作文=审题谋篇的图表数据分析、现象解读
  - **思路框架 framework**：整篇写作结构，分段落说明每段写什么
  - **应用模板 template**：官方可套用英文模板 + 适用说明 + 模板注释
- **呈现**：作文页「词汇储备」上方新增「官方解析 · 审题与模板」折叠板块（`analysisHtml`，复用储备板块折叠样式，模板用衬线字体）。题目要求仍保持英文原文不翻译。
- 2024/2025 官方解析无审题类内容（仅有句式点评），不显示该板块。

## [en2-v40] 2026-08-06

### 词典增量补词 + 去除进入文章的高亮闪现

- **词典补词**：dict.json 由一次性脚本（已丢失）从 ECDICT + 内置词书扩充，仍缺 919 个语料内可查词（含 `optimism` 等基础词），且 `quirky / quirkier / quirk` 也无法查询。
  - 新增 `tools/patch_dict.py`：扫描 16 年真题语料，把语料内、ECDICT 可查但 dict.json 缺失的词增量补齐（优先用 exchange lemma 收敛原形，原形一并补入），不改动已有词条。
  - 语料词命中率 **96.5% → 96.6%**（6832 词，未覆盖 235 个均为专有名词/连字符复合词/品牌名）。
  - 额外补充非语料但用户常查的基础词 `optimism / optimistic / quirk / quirky / quirkier / quirkiest` 等。
  - dict.json：8525 → **9377** 词条，forms 529 → 2138，体积 762KB → 876KB。
- **进入文章不再高亮闪现**：`restoreScroll` 续读功能保留滚动到上次位置，去掉 `.related` 黄色高亮（2 秒闪现），避免每次点入文章看到首句闪黄。

## [en2-v39] 2026-08-06

### 词形还原：中等难度派生词可点击翻译

- **背景**：`endlessly / perpetually / cheerfulness / optimist / portraying` 等带 `-ly / -ness / -ist / -ing / -ed` 等后缀的派生词，因词典未收录原文词形而无法点击查词。
- **方案**：`pwa/js/dict.js` 新增规则词形还原 `stemCandidates()`：
  - 复数 `-ies/-es/-s`；时态 `-ing/-ed/-ied/-ier/-est`（含去 e、双写还原）
  - 副词 `-ly/-ably/-ibly/-ically/-ally`；名词性 `-ness/-ist/-tion/-sion/-ation/-ment/-ity/-ability/-ibility/-ive/-ful/-ous/-al/-ism/-ize`
  - 反义前缀 `un-/im-/in-/dis-` 剥离
  - **不规则形式表** `IRREGULAR`：常见动词过去式/分词（did/went/began/brought…）、不规则复数（children/men/feet…）、比较级（better/biggest/healthier…）
  - 属格 `'s` 剥离（children's→child、people's→people）
- **效果**：16 年真题 text1-4 + 完形正文的词条可点击率由较低提升至 **96.5%**（23921/24801），剩余未命中多为专有名词（london/john）、缩写（ceo/dna）及词典未收录词（endless/winner/runner 等）。
- **保持不变**：词组词典命中、精选难词高亮（hardwords.json）不受影响，仍按原逻辑。
- `pwa/sw.js` CACHE_VER 升至 `en2-v39`。

## [en2-v38] 2026-08-06

### 作文模块新增官方词汇储备板块（2010–2023）

- 数据：从各年官方解析提取作文范文后的词汇储备板块，写入写作文章 `reserve` 字段：
  - 2010–2016 大作文：**亮点词汇** + **必备搭配**
  - 2010–2023 小作文 + 2017–2023 大作文：**必备表达**
  - 2010–2023：**话题词汇**、**话题表述补充**、**写作素材积累**（存在该板块的年份）
  - 2024 官方解析无此类板块、2025 仅有范文内词汇升级标注，自然缺项
- 清洗：修复 OCR 断裂拼写（dynamic momentum、supply deficiency 等）、词性标记规范化、删除页码/图表 ASCII 噪声。
- 前端：作文页范文末尾新增「词汇储备」区，各板块可折叠展开（`.writing-reserve`），含 `.reserve-grid` 词条网格、`.reserve-text` 话题补充、`.reserve-material` 素材句子。
- 工具：`tools/merge_reserve.py` 合并 `_reserve_{year}.json` 到 extra JSON；4 个并行提取 agent 产出 2010–2023 数据。
- `pwa/sw.js` CACHE_VER 升至 `en2-v38`。

## [en2-v37] 2026-08-06

### 作文模块恢复题目要求 Directions

- 数据：为 2010–2025 全部 16 年 writing_a/writing_b 补齐官方 **Directions**（写作指令原文，如小作文书信要求、大作文图表要求），提取自各年真题 exam.txt（2025 取自 notes_ocr.txt 人工整理）。
- 前端：写作页在范文上方显示「题目要求」面板（`.writing-directions`），无图表不显示图表框；`pwa/js/article.js` 渲染 `article.directions`。
- 样式：`pwa/css/style.css` 新增 `.writing-directions` / `.writing-directions-text`。
- `pwa/sw.js` CACHE_VER 升至 `en2-v37`。

## [en2-v36] 2026-08-06

### 四大模块覆盖全部 16 年（2010–2025），新题型三种题型统一支持

- **数据**：为 2010–2025 全部 16 年补齐**完形填空 / 新题型 / 翻译 / 作文**四大模块（每年 5 篇新文章），全部官方原文/译文/精解/范文，来自各年真题与官方解析 PDF。
  - 完形填空：每年 20 题（选项/答案/官方精解），正文 `[n]` 空格作答。
  - 新题型三种题型统一支持：**多项对应**（匹配）、**小标题对应**（小标题）、**判断 T/F**（2010），共用 `pool` 选项池 + `answer` 指向池 key。
  - 翻译：正文逐句 + `ref_cn` 官方全文参考译文。
  - 作文：Part A/B 官方范文中英对照；Part B 大作文附**真题图表截图**（`pwa/img/{year}_writingb_chart.png`，从真题 PDF 渲染）。
- **数据勘误**：修正 2014 完形答案（官方解析核对：`BACADACCDBABCDBDADCB`，此前误用 `BADDAABCBDACBDCDACDB`）；2014 新题型第 45 题修正为 A。
- **`tools/extracted/modules/{year}_extra.json`**：每年 5 篇文章的独立数据片段，`tools/merge_modules.py` 合并进 `pwa/data/{year}.json` 并同步 `index.json`。
- **`tools/validate.py`**：支持三种新题型、模块型文章校验（翻译查 ref_cn、作文查 sample_en/sample_cn）。
- **前端**：
  - `pwa/js/storage.js` `TYPE_NAMES`：完形/新题型/翻译/写作 PartA/PartB。
  - `pwa/index.html` 排序数组含新模块。
  - `pwa/js/article.js`：翻译/作文隐藏做题面板（`NO_QUIZ_TYPES`）；作文渲染官方范文 + 图表（`chart_img`）；点全文翻译时标题自动展开（`showReadTitle`）；新题型 pool 选项池空对象 fallback 修复。
  - `pwa/css/style.css`：`.writing-chart`、`.translation-ref` 等样式；移除作文题目框样式。
- **`pwa/sw.js`**：预缓存 16 年图表 PNG，CACHE_VER 升至 `en2-v36`。

## [en2-v35] 2026-08-05

### 新增完形填空 / 新题型 / 翻译 / 作文四大模块（2014 试点）

- **数据**：`pwa/data/2014.json` 新增 4 篇模块文章，从官方真题/解析 PDF 提取：
  - `2014_cloze`（完形填空）：26 句正文（`[n]` 空格占位）+ 20 题选项/答案/官方精解 + 官方全文译文。
  - `2014_newtype`（新题型·多项对应）：18 句正文 + 共享选项池 `pool`/`pool_cn`（A–G）+ 5 题（41–45）匹配答案与官方精解。
  - `2014_translation`（翻译）：10 句正文 + 逐句译文 + `ref_cn` 官方全文参考译文。
  - `2014_writinga` / `2014_writingb`（作文 Part A/B）：`directions` 题目要求 + `sample_en`/`sample_cn` 官方范文对照。
- **`tools/build_2014_extra.py`**：新建构建脚本，从 `tools/extracted/2014_exam.txt` / `2014_notes.txt` 提取并生成上述文章，自动同步 `index.json`，可重复运行覆盖。
- **`tools/validate.py`**：`VALID_TYPES` 加入 `translation/writing_a/writing_b`；模块型文章走专属校验（翻译查 `ref_cn`，作文查 `directions/sample_en/sample_cn`），不再强制逐句结构。
- **`pwa/js/storage.js`**：`TYPE_NAMES` 新增 `translation: '翻译'`、`writing_a: '写作 PartA'`、`writing_b: '写作 PartB'`。
- **`pwa/index.html`**：文章列表排序数组加入新模块类型。
- **`pwa/js/article.js`**：
  - `renderArticle` 分支：作文模块渲染题目要求 + 范文中英切换（`toggleWritingCn`）；翻译模块正文下方提供官方全文译文折叠。
  - 修复新题型共享选项池 fallback：`q.options` 为空对象时正确回落 `article.pool`（`questionHtml` / `showResult`）。
- **`pwa/css/style.css`**：新增 `.writing-directions` / `.writing-sample` / `.writing-toggle` / `.translation-ref` 等样式。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v35`。

## [en2-v34] 2026-08-05

### 隐藏正文文章标题（如 Happy Money），点击才显示

- 修正 v33 理解偏差：导航栏标题恢复常显，改为隐藏**正文文章标题**。
- **`pwa/js/article.js`** + **`pwa/css/style.css`**：正文 `.read-title` 默认隐藏，显示 `…` 占位符，点击标题处才显示/再隐藏（`toggleReadTitle`）；新增 `.read-title-placeholder` 样式。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v34`。

## [en2-v33] 2026-08-05

### 隐藏文章标题，避免精读前剧透

- **`pwa/index.html`**：文章列表卡片只显示题型标签，隐藏英文标题（`ac-title` 不再渲染）；「继续学习」条也隐藏文章标题（`cbSub`），仅保留年份+题型。
- **`pwa/js/article.js`** + **`pwa/article.html`**：精翻导航栏标题默认隐藏（显示 `…`），点击标题处才显示/再隐藏（`toggleNavTitle`）；标题从返回链接拆为独立按钮（`.nav-articletitle`）。
- **`pwa/css/style.css`**：新增 `.nav-left` / `.nav-articletitle`（导航标题按钮，hover 高亮）。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v33`。

## [en2-v32] 2026-08-04

### 查词升级：中文反查 + 查询历史 + 悬浮设置 + 自定义快捷键

- **`pwa/js/dict.js`**：新增 `cnLookup()`/`cnIndex()` 中文反查——按中文释义在词典 words + 词组 phrases 中查找对应英文词/词组（含词组标记），供精读页导航栏查中文。
- **`pwa/js/article.js`**：
  - `navLookupWith(q)` 统一查词入口（回车 / 历史点击 / 中文结果点击共用）：含中文自动转反查，弹「相关词条」列表，点击词条再查详情并可加生词本。
  - 查询历史：`en2_hist` localStorage 持久化（去重、上限 12 条、最近优先）；输入框聚焦弹出历史下拉，点击回填查询，可一键清空。
  - 悬浮设置面板：导航栏「⚙ 设置」打开（仿背单词页悬浮窗），收纳夜间模式、导出/导入标注、清空查词历史；导航栏移除原「夜间/导出标注/导入标注」三个按钮。
  - 自定义查词快捷键：默认 **Alt+C** 聚焦查词框，设置面板内点键位后可改绑（支持 Ctrl/Alt/Shift 组合，防重复绑定，Esc 取消）；绑定存 `en2_artkeys`。
- **`pwa/css/style.css`**：新增 `.float-panel`（精读页悬浮设置，复用 ss-* 样式）、`.nav-search-hist`/`.hist-item`/`.hist-clear`（历史下拉）、`.cn-list`/`.cn-row`/`.cn-mean`/`.cn-tip`（中文反查列表）。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v32`（无新增资源，PRECACHE 不变）。

## [en2-v31] 2026-08-03

### 学习计时器：支持手动暂停/继续与重置

- **`pwa/js/common.js`**：计时器新增手动控制——暂停状态存 `localStorage.studyTimerPaused`（跨页/刷新保持）；新增全局 `togglePauseTimer()`（暂停/继续切换）与 `resetTimer()`（二次确认后归零并解除暂停）；每秒累加跳过「切走窗口」与「手动暂停」两种暂停态。
- **5 个页面（index/article/study/vocab/favorites）**：导航栏计时器旁新增两个圆形小按钮——「⏸/▶」暂停继续（暂停时按钮高亮、计时文字变主色加粗）与「↺」重置。
- **`pwa/css/style.css`**：新增 `.nav-timer-btn`（圆形图标按钮、暂停态高亮、暗色适配）与 `.nav-timer.paused`；≤900px 窄屏随 `.nav-timer` 一并隐藏。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v31`（无新增资源，PRECACHE 不变）。

## [en2-v30] 2026-08-03

### 精翻导航栏：新增查词框 + 记单词改为新标签页

- **`pwa/article.html`**：导航栏新增**查词输入框**（`navSearch`，胶囊样式，聚焦展开、Enter 查询）；「记单词」按钮改为 `window.open('study.html')` **新标签页打开**，不打断当前精读。
- **`pwa/js/article.js`**：新增 `navLookup()`——输入单词/词组回车即查，单词走 `dictLookup`（词形还原）、词组走 `phraseLookup`，命中复用词卡弹窗显示音标/释义/考频并可加入生词本；未收录提示「词典与词组库均未收录」，查询后自动全选输入便于连查。
- **`pwa/css/style.css`**：新增 `.nav-search` 样式（含 focus 展开、暗色适配）。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v30`（无新增资源，PRECACHE 不变）。

## [en2-v29] 2026-08-03

### 精翻页「记录生词」只收录精选难词（去掉简单词）

- 词典 v26 扩到 8525 词后，`recordArticleWords` 按词典命中判断"难词"，导致 `and`/`new`/`book` 等简单词也被一键记录（一篇 150-180 个）。
- **`pwa/js/article.js`**：`recordArticleWords` 增加 `isHard()` 精选难词过滤（与「高亮难词」同一口径——熟词僻义 + 真题较难词集合）。一篇降到 17-57 个。
- **`pwa/js/dict.js`**：新增 `isHardLoaded()` 判断精选集合是否加载成功；精选集合加载失败时 `recordArticleWords` 回退为旧逻辑（词典命中即记录），避免降级为空。
- **`pwa/sw.js`**：CACHE_VER 升至 `en2-v29`。

## [en2-v28] 2026-08-03

### 单词本：批量删除 + 按今日/昨日加入快捷选中

- **`pwa/vocab.html`**：词书工具栏新增「批量删除」入口，进入后每张词卡左侧出现多选框（选中卡片琥珀描边 + ✓），点击卡片即勾选。
- **批量操作条**（工具栏下方常驻，删除按钮红色）：显示「已选 N」「今日加入 · N」「昨日加入 · N」「全选」「清除选择」「删除选中 (N)」「退出」。
  - 「今日加入/昨日加入」按 `added_at` 本地日期前缀（YYYY-MM-DD）一键勾选当日/昨日入库的词，支持叠加组合（先选今日再加昨日再全选）。
  - 「删除选中」二次确认，从生词本**彻底删除**（含背单词进度），删除后退出批量模式。
  - 与原有分页（每页 60 张）兼容：追加分页的卡片读选中态渲染，「全选」覆盖整个当前视图（含未加载页）。
- **`pwa/css/style.css`**：新增 `.batch-bar`/`.bb-btn`（含 danger 变体）、`.item-card.batch`（flex 多选布局、hover/sel 态）、`.ic-check`（方框勾选控件）。
- 注意：此改动仅触碰 `vocab.html` + `style.css`，不涉及 SW 清单（无新增资源），`CACHE_VER` 升至 `en2-v28` 使客户端换新页面代码。

## [en2-v27] 2026-08-02

### 高亮难词收窄为精选集合 + 题目词可点翻译

**精选难词集合（高亮难词不再全量高亮）**
- **新增** `tools/build_hardwords.py`：合并内置词书「熟词僻义」+「真题高频·较难词」，词条统一小写归一并用 dict.json forms 展开到原形，产出 **`pwa/data/hardwords.json`（2971 词，44.3KB）**。
- **`pwa/js/dict.js`**：新增 `loadHardwords()`（一次 fetch，失败静默降级为空）+ `isHard(word)`（原始小写 → normWord → forms 原形三级命中）。
- **`pwa/js/article.js`**：正文渲染时对命中精选集合的词（预标注词/词典难词/词组）加 `hard` 类。此前「高亮难词」把全部 8525 个词典命中词标琥珀（一篇约 170 个），现在只标真难/易错词（抽样一篇降到 ~40-60 个）。
- **`pwa/css/style.css`**：`body.show-hard` 高亮规则由 `.word` 改为 **`.word.hard`**。
- **`pwa/sw.js`**：PRECACHE 加入 `data/hardwords.json`；CACHE_VER 升 `en2-v27`。

**题目（题干/选项/选项池）词可点翻译**
- **`pwa/js/article.js`**：`questionHtml`/选项池渲染改用 `quizTextHtml()`（复用 `annotatePhrases` 管道）——题干与选项里的英文词/词组包成可点 span，点词 `stopPropagation` 只弹释义卡、**不触达答题**；点选项空白/字母处仍正常选答案，二者不冲突。
- 新增 `resolveExample(sid)`：例句作用域兼容句子 id（正文词）与题目 id（题目词）——题目词取该题 `related_sentences` 首句作例句，无则用题干文本兜底，保证加入生词本有例句。
- `openPop()` 弹卡增加视口底部防溢出：默认在词下方，超界自动翻到词上方（题目面板底部选项弹卡不再超出屏幕）。

## [en2-v26] 2026-08-01

### 扩充离线词典覆盖（1731 → 8525 词）

- **`pwa/data/dict.json`**：合并 4 本内置词书（真题核心/考纲/形近易混/真题高频）到离线词典，覆盖 209/211 常见测试用例，未命中仅 earning/phone 两个。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v26`。
- 注意：词典扩大后「高亮难词」随之变得过密，已由 en2-v27 引入精选难词集合收敛。

## [en2-v25] 2026-07-27

### 新增浏览器标签页图标（favicon）

- **`pwa/icons/favicon.svg`**：新建矢量 favicon，teal（`#14b8a6→#0f766e`）圆角底 + 白色“英”字 + 右上角金色上标“2”，与主题色一致，小尺寸也清晰。
- **5 个页面（index/article/vocab/favorites/study.html）**：head 补上 `<link rel="icon">`（SVG 优先，PNG 降级），修复标签页无图标问题。
- **`pwa/sw.js`**：PRECACHE 加入 `icons/favicon.svg`；CACHE_VER 升 `en2-v25`。

## [en2-v24] 2026-07-27

### 真题逐句译文改用官方解析译文（2019–2025 全量重跑，收尾）

- **`pwa/data/2019.json`–`pwa/data/2025.json`**：将 2019–2025 共 7 年、每年 4 篇精读文章的逐句 `cn` 字段，从此前手写意译统一替换为官方真题解析译文。其中 2019–2022 为文本层双栏版式，2023–2025 为扫描图版式，均逐页渲染后按段落对照英文人工转录、修正 OCR 错字并对齐补齐缺句后写回，仅改 `cn`，`en`/`words`/`para`/`id` 不变。
- 覆盖句数：2024 共 63 句（text1 16 / text2 14 / text3 17 / text4 16）、2025 共 74 句（text1 20 / text2 18 / text3 21 / text4 15）等。
- 至此 2010–2025 全 16 年真题逐句译文均已统一为官方解析译文。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v24`。

## [en2-v23] 2026-07-27

### 真题逐句译文改用官方解析译文（2010–2018 全量重跑）

- **`pwa/data/2010.json`–`pwa/data/2018.json`**：将 2010–2018 共 9 年、每年 4 篇精读文章的逐句 `cn` 字段，从此前手写意译统一替换为官方真题解析译文——以官方解析 PDF 右栏译文为准，逐句对照英文修正扫描 OCR 错字并补齐缺句/截断句后写回，仅改 `cn`，`en`/`words`/`para`/`id` 不变。
- 覆盖句数：2010(65)、2011(81)、2012(54，text3 此前已完成)、2013(72)、2014(78)、2015(77)、2016(67)、2017(74)、2018(76)。
- 2019–2025 因官方 PDF 为交错双栏版式，旧右栏抽取器不适用，留待后续单独处理。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v23`。

## [en2-v22] 2026-07-28

### 新增内置词书「真题高频·较难词（历年批注）」

- **`pwa/data/deck_realexam.json`**：聚合 2010–2025 全部真题逐句批注词（`sentences[].words`），按小写词形去重后共 2587 个词，保留首次出现的批注释义并附所在真题原句作为例句。
- **`pwa/vocab.html`**：`BUILTIN_DECKS` 置顶新增 `bd_realexam`，点击「内置词书」即可按需导入。
- **`pwa/sw.js`**：PRECACHE 加入 `data/deck_realexam.json`，离线可导入；CACHE_VER 升 `en2-v22`。

## [en2-v21] 2026-07-28

### 背单词页工具栏瘦身：选项全收进设置窗，删重开；单词本新增「重学本书」

- **`pwa/js/study.js`**：顶部工具栏只保留「↶ 回退」与「⚙ 设置」；删除「重开」按钮；「每日新词量」「自动读词」「自动读例句」全部移入设置窗新增的「背词选项」区（每日量为数字输入，两个自动读为开/关切换）；删除已无用的 `editPlan`。
- **`pwa/vocab.html`**：词书工具栏新增「重学本书」（全部视图为「重学全部」）：清空该词书内所有词的记忆进度 srs、变回新词从头背；执行前二次确认并展示影响词数，同步清掉本轮会话避免恢复旧队列。
- **`pwa/css/style.css`**：新增 `.ss-num`（数字输入）与 `.ss-toggle`/`.ss-toggle.on`（开关按钮）样式。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v21`。

## [en2-v20] 2026-07-28

### 背单词页：自定义快捷键悬浮设置窗 + 收藏统一归入收藏目标生词本

- **`pwa/js/study.js`**：新增悬浮设置窗（⇢ 设置按钮）——可自定义「显示释义/认识/不认识/回退/收藏」5 个动作的键位（存 localStorage `en2_keymap`，默认 空格/→/←/⌫/F），可一键恢复默认；绑定时独占下一次按键，Esc 取消、重复键位拒绝。设置窗内可直接切换收藏目标词书。keydown 重写为读 keymap 派发，输入框内不拦截。
- **收藏语义统一**：★ 不再是独立 `v.fav` 星标，而是「当前词是否在收藏目标生词本（`getActiveDeck`）」。`toggleFav` 改为切换归属（`toggleWordInDeck`），移空时回退内置词书、绝不删记录，避免背词途中单词消失。
- **`pwa/js/storage.js`**：新增 `toggleWordInDeck(word, deckId)`；`migrateVocabDecks` 一次性把历史 `v.fav` 词并入当前收藏目标并清 fav 字段（`en2_favMigrated` 防重）；`deckCounts` 移除 `__fav__` 计数；删 `toggleFavWord`。
- **`pwa/vocab.html`**：移除单词本「★ 收藏」独立标签页及 `__fav__` 分支；per-card ★ 改为“是否在收藏目标词书”开关，点击即归入/移出当前收藏目标。
- **`pwa/css/style.css`**：新增 `#studySettings` 及 `.ss-title/.ss-row/.ss-key/.ss-key.binding/.ss-reset/.ss-target` 等设置窗样式（复用现有变量，z-index 400）。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v20`。

## [en2-v19] 2026-07-27

### 文章页：手动荧光高亮 + 文字批注（移植自数学笔记）

- **`pwa/js/annotate.js`（新增）**：移植数学笔记的批注系统。选中正文英文即弹浮动条，可打 3 色荧光（黄/绿/蓝）、整句块高亮、写文字批注（批注框支持 Ctrl+V 直接贴图）。标注以每句 `data-sid` 为锚点、文章 `AID` 分桶，存 localStorage（`enReadAnnot`）+ IndexedDB（`enReadAnnotImg` 存贴图）。点已有荧光/整块高亮可改色或清除。
- **`pwa/js/article.js`**：首次渲染与完形「清除重做」重绘后调用 `Annot.apply(AID)` 恢复标注；`onWordClick`/`onDictWordClick`/`onPhraseClick` 加选区守卫，划词标注时不误弹词卡。
- **`pwa/article.html`**：引入 `js/annotate.js`；导航栏新增「导出标注 / 导入标注」（JSON 备份，含贴图 base64，导入为合并）。
- **`pwa/css/style.css`**：新增 `--mk-*`/`--hl-*`/`--ann-*` 变量（亮/暗）及 `mark.mk`、`.sent-en.hl-*`、`.ann-box`、`#annBar` 等样式；整块高亮挂 `.sent-en` 避开题目定位黄色，`#annBar` z-index 400 高于词卡。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v19`；PRECACHE 加入 `js/annotate.js`。

## [en2-v18] 2026-07-27

### 文章页：生词记录后不再自动高亮

- **`pwa/js/article.js`**：移除加入生词本 / 一键记录后对正文同词的即时 `.in-vocab` 高亮（`onAddVocab`、`onAddDictVocab`、词组加入、`recordArticleWords` 共 4 处）。默认不高亮生词，跨文章渲染本就不高亮，现在记录后也保持不高亮。
- **`pwa/sw.js`**：CACHE_VER 升 `en2-v18`。

## [en2-v17] 2026-07-27

### 导入词书：内置详细格式模板 + 一键下载示例

- **`pwa/vocab.html`**：点「导入词书」不再直接弹文件选择框，改为先展示一个引导面板：JSON 格式说明、各字段（`word`/`meaning`/`phonetic`/`example_en`/`example_cn`）含义与必填/可选、以及一份带真实例子的完整模板代码块；面板内可直接「⬇ 下载模板文件」（`词书模板.json`）或「选择文件导入」。
- **`pwa/css/style.css`**：新增 `.import-help` 系列样式（标题/说明/字段列表/代码块/操作区），均用 CSS 变量适配深色模式。
- **`pwa/sw.js`**：`CACHE_VER` 升 `en2-v17`。

## [en2-v16] 2026-07-27

### 精读页：简单词改纯文本 + 导航栏「记单词」入口

- **`pwa/js/article.js`**：正文里离线词典未命中的「简单词」不再包成可点 span，改为直接输出纯文本——只有有离线释义的难词/词组/预标注词才可点、才弹卡，去掉了大量「（无离线释义）」空弹卡；每篇文章可点 DOM 节点显著减少。
- **`pwa/article.html`**：导航栏在「记录生词」后新增「记单词」按钮，一键跳转背单词卡片页 `study.html`。
- **`pwa/css/style.css`**：清理「高亮难词」规则中已失效的 `:not(.plain)`（简单词已是纯文本，天然不参与高亮）。
- **`pwa/sw.js`**：`CACHE_VER` 升 `en2-v16`。
- 行为变化：此前被加入生词本的简单词，正文不再显示 in-vocab 底色（生词本/背单词页数据不受影响）。

## [en2-v15] 2026-07-27

### 背单词：可选自动播放（读词 / 读例句）

- **`pwa/js/study.js`**：新增两个开关——「🔊 自动读词」（卡片出现时自动朗读单词）与「📖 自动读例句」（点开释义时自动朗读例句），状态存 localStorage，默认关；复用现有发音通道（有道美音优先 + TTS 回退）。
- **`pwa/css/style.css`**：新增 `.sb-btn.on` 开关激活态样式。
- **`pwa/sw.js`**：`CACHE_VER` 升 `en2-v15`。

## [en2-v14] 2026-07-27

### 背单词卡片：字体现代化 + 自然美声发音

- **`pwa/css/style.css`**：`.fc-word` 单词字体由 Georgia 衬线改为现代无衬线栈（Inter / 系统无衬线），更清晰。
- **`pwa/js/study.js`**：重写 `speak()`——朗读优先用有道 dictvoice 在线自然美音（type=2 美式），断网或加载失败自动回退浏览器 TTS；复用单个 Audio 实例防连点叠音。
- **`pwa/sw.js`**：`CACHE_VER` 升 `en2-v14`（在线音频为跨域 URL，不入缓存，PRECACHE 无变更）。

## [en2-v13] 2026-07-27

### 新增内置词书：唐迟·20年高分词组 / 熟词僻义（OCR 自动流水线）

- **`tools/ocr_kb.py`**（新增）：对扫描版词库 PDF 逐页渲染 + RapidOCR 识别，按「绿色粗体词条 / 黑色正文 / 真题出处」版面结构解析成中间词条 `_kb_data/kb_entries.json`（另出 `kb_raw.txt` 供人工校对）。绿/黑靠框内笔画平均色判定；小节标题「重难点词组 / 熟词僻义」切换词条类型。
- **`tools/build_tc_decks.py`**（新增）：读中间词条，按类型拆成两个内置词书 `pwa/data/deck_tc_phrases.json`（词组）/ `deck_tc_senses.json`（熟词僻义），出处并入例句中文译文，按 word 去重。
- **`pwa/vocab.html`**：`BUILTIN_DECKS` 新增两本（`bd_tc_phrases` / `bd_tc_senses`），按需导入。
- **`pwa/sw.js`**：`PRECACHE` 加两个 deck，`CACHE_VER` 升 `en2-v13`。
- 数据由用户在本地对自有 PDF 运行流水线生成并人工核对，释义/例句 100% 照抄、无 AI 生成。

## [en2-v12] 2026-07-27

### 背单词系统与文章交互整体升级

**A. 单词本卡顿根治（分页渲染）**
- **`pwa/vocab.html`**：`renderList` 重构为分页渲染——每次只渲染 `PAGE=60` 张词卡，底部「加载更多（剩 N）」按钮 `insertAdjacentHTML` 追加、不重绘已渲染项，避免大词书全量塞 DOM 卡顿。
- **`pwa/css/style.css`**：新增 `.load-more` 虚线按钮样式。

**B. 背单词新词/复习分离（三模式）**
- **`pwa/js/study.js`**：新增 `getStudyMode/setStudyMode`（存 `localStorage.en2_studyMode`）与顶部 `.mode-switch` 切换——`mix` 复习优先（到期复习+当日新词，默认）/ `review` 只复习到期词 / `new` 只学新词；`buildQueue` 由 `(includeAll)` 改为 `(mode, includeFuture)`，按模式构建队列并返回 `future` 计数；空态文案按模式区分，仅有未到期词时才给「提前背」入口。
- **`pwa/css/style.css`**：新增 `.mode-switch` / `.mode-btn` 样式。

**C. 进度不重置（会话续存）**
- **`pwa/js/study.js`**：新增 `getSession/saveSession/clearSession`（存 `localStorage.en2_studySession`：日期/词书/模式/词表/光标/已背）；`judge`、`undo` 后写入会话，`renderDone` 与切模式/切词书/重开时清空会话；`init` 新增 `resumeSession()`——同日/同词书/同模式且未完成则从当前词书重建队列续存，跨页返回不再进度归零。
- **查看原文改新开页**：背词卡「查看原文语境 →」链接加 `target="_blank"`，不打断当前背词进度。

**D. 学习统计**
- **`pwa/js/storage.js`**：新增 `deckStats(deckId)`，返回 `{total, newCount, learning, mastered, dueToday}`（新=无 srs、已掌握=interval≥21、其余为学习中、到期=due≤今日；自包含今日计算不依赖 dayStr）。
- **`pwa/js/study.js`**：`start`/`resumeSession` 计算 `deckStat`，背词卡顶部新增统计条（共/新词/学习中/已掌握/今日待复习）。
- **`pwa/vocab.html`**：词书工具栏新增迷你进度行。
- **`pwa/css/style.css`**：新增 `.deck-stat-bar` / `.deck-mini-stat` 样式。

**E. 真题考频「出现 N 次」**
- **`tools/build_freq.py`**（新增）：离线遍历 16 年题库 `sentences[].en`，单词经 `dict.json` `forms` 归一、词组复用 `phrases.json` key 最长优先非重叠匹配（与运行时 `annotatePhrases` 同口径），产出 `pwa/data/freq.json`（`{key:{c:次数, a:文章数}}`，6473 键 / 171KB）。
- **`pwa/js/dict.js`**：新增 `loadFreq/freqLookup/freqBadge`——三级查找（原始小写→`normWord`→`forms` 变形还原），生成「真题考频 · 出现 N 次（M 篇）」徽标。
- **接入各弹卡**：文章弹卡（预标注词/词典难词/词组）、背词卡背面、单词本词卡均显示考频徽标；`study.html` 补加载 `js/dict.js`，`vocab.html`/`article.js` 初始化调用 `loadFreq`（失败静默降级不显示徽标）。
- **`pwa/css/style.css`**：新增 `.wp-freq` 徽标样式。

**F. 文章全部可点 + 仅生词本高亮 + 上下文义**
- **`pwa/js/article.js`**：`annotatePlain` 让每个单词 token 都可点——词典命中标 `dict-hard`，未命中标 `plain`（点开显「（无离线释义）」，仍可加入生词本）。
- **`pwa/css/style.css`**：`.word` 去掉常驻虚线下划线改为 hover 才提示；`.in-vocab` 保留琥珀高亮；`show-hard` 高亮改为 `.word:not(.plain)`（普通词不参与）。

**G. 记忆算法升级（学习步 + 状态机）**
- **`pwa/js/study.js`**：`grade()` 新增 `state` 字段（`new`→`learning`→`review`）——新词首次认识 1 天、二次 3 天，之后 ×ease；不认识回 `learning`、1 天后重来，避免新词一次就被拉到长间隔。

- **`pwa/sw.js`**：`PRECACHE` 新增 `data/freq.json`；`CACHE_VER` `en2-v11` → `en2-v12`。
- **验证**：全部 JS `node --check` 通过；`tools/validate.py` 16 文件 0 警告 0 错误。

### 文章页：取消生词本词的常驻高亮
- **不再自动高亮**：`article.js` 三处标注（预标注词 `annotate`、词典难词 / 词组 `annotatePlain` / `annotatePhrases`）渲染时不再根据 `vocabSet` 加 `.in-vocab` 类，避免生词本里的词/词组在所有（含未学过的）文章里被琥珀底色高亮。单词仍可点查释义、加入/移出生词本的交互不变。
- **`pwa/sw.js`**：`CACHE_VER` `en2-v11` → `en2-v12`。

## [en2-v11] 2026-07-27

### 背单词：回退（防误点） + 每日计划 + 单词收藏
- **回退按钮**：`study.js` 新增判定历史栈，`judge` 前快照（光标/进度/该词原 `srs`/是否压回队尾）；`undo()` 撤销最近一次认识/不认识，恢复记忆状态与队列，防止误点（顶栏「↶ 回退」按钮 + `Backspace` 快捷键，无历史时置灰）。
- **每日计划**：新增 `getDailyPlan/setDailyPlan`（存 `localStorage.en2_dailyPlan`，默认 20），`buildQueue` 的新词引入上限改为可设置；顶栏「📅 每日 N」按钮可改。
- **单词收藏**：`storage.js` 新增 `toggleFavWord`（`vocab.fav` 标记，跨词书全局，随备份导出）；背词卡片右上角 ☆/★ 切换；单词本新增「★ 收藏」筛选页与每张词卡星标；`deckCounts` 同步统计收藏数。
- **`pwa/css/style.css`**：新增 `.study-bar .sb-btn`（回退/计划胶囊按钮）、`.fc-fav`（卡片星标）、`.item-card .ic-fav`（词卡星标）。
- **`pwa/sw.js`**：`CACHE_VER` `en2-v10` → `en2-v11`。

## [en2-v10] 2026-07-27

### 背单词页改版：消除翻卡跳动（墨墨 / 扇贝式固定结构）
- **问题**：点击「认识 / 不认识」及翻面时卡片高度与按钮位置抖动——`.fc-back` 由 `max-height:0→1200` 展开、`.fc-front` 有 `min-height`，且底部判定按钮在翻面后才注入，导致整卡高与按钮条弹入弹出。
- **`pwa/js/study.js`**：`renderCard` 重写为固定结构——卡片头（单词/音标/朗读）常驻顶部、释义区为固定预留高的滚动容器（例句异步填入 `fcBackContent`，不改卡外高）、底部操作条常驻（翻面前「显示释义」，翻面后「不认识 / 认识」两个等高按钮）；`onFlip` 改单向翻面（已翻面再点卡片不收起，避免误触抖动）。
- **`pwa/css/style.css`**：`.flashcard` 改 flex 纵向布局；`.fc-back` 固定高 `clamp(230px,40vh,360px)` + `overflow-y:auto`，翻面仅在区内 `opacity` 淡入内容；新增 `.fc-reveal-hint` / `.fc-back-content` / `.sa-btn.reveal`。
- **验证**：翻面前后卡片高度、底部按钮位置在亚像素级完全恒定（浏览器几何采样），切卡多轮稳定，零跳动。
- **`pwa/sw.js`**：`CACHE_VER` `en2-v9` → `en2-v10`。

## [en2-v9] 2026-07-27

### 文章词组自动识别高亮 + 可点翻译
- **新增词组词典**：`tools/build_phrases.py` 从《英（二）2014-2024 真题词组-背诵版 PDF》（坐标分列重建，释义 100% 照抄）叠加 16 年题库人工词组，产出 `pwa/data/phrases.json`（扁平映射 + `maxWords`）。
- **`pwa/js/dict.js`**：追加 `loadPhrases()` 一次加载并构建内存索引（首词 → 候选，按词数降序），新增 `phraseLookup`/`phraseCandidates`/`maxPhraseWords`；加载失败静默降级为无词组高亮。
- **`pwa/js/article.js`**：新增 `annotatePhrases()`，对人工预标注切段后的纯文本做左→右、最长优先的词组匹配，命中区间包成可点 span（`onPhraseClick` 弹卡 + 加入生词本）；与人工标注、单词天然无重叠。

### 内置词书：真题词组 + 3 本考研词表随应用发布
- **新增** `tools/build_decks.py` 从 3 个考研词表（真题核心 2230 / 考纲乱序 5551 / 形近易混 1013）产出 `deck_core/syllabus/confusable.json`；真题词组词书 `deck_phrases.json` 由 `build_phrases.py` 一并产出（226 词条，含例句）。
- **词组 PDF 解析**：按列（序号/短语/含义/例句）重建——短语/含义列先按行距聚块再以块中心就近归属序号（避免多行含义被切碎），例句列逐词归属到最近的已定位短语/含义块；例句若检出跨条残句/拆散数字等污染信号则丢弃例句（宁缺勿错），词条仍保留正确的 word+meaning。
- **`pwa/js/storage.js`**：新增 `ensureDeck(id, name)`（固定 id、可删、重导幂等）。
- **`pwa/vocab.html`**：词书区新增「内置词书」入口，4 本词书按需 `fetch` → `ensureDeck` + `addWordsBulk` 导入（已有词仅并入、不覆盖进度，已导入二次确认），不在启动时自动灌库。

### 难度判定校准
- **`tools/build_dict.py`**：加载 3 个考研词表为 `EXAM_WORDS`；`is_simple` 保留 zk/gk、长度≤3、停用词三道基础闸门在前，在词频闸门之前插入「考研重点词即便高频也保留为难词」；重建 `dict.json`（1731 难词，208.8KB）。

### 词组释义去「词组：」前缀
- **`tools/strip_phrase_prefix.py`** 窄替换去掉16 个年份 JSON 里释义的「词组：」前缀；`pwa/js/study.js` `renderMeaning` 静默剥离前缀（兼容已存旧记录）。

### 发布
- **`pwa/css/style.css`**：`.word.phrase` 叠加一条极轻波浪下划线（复用 `.word`/`.dict-hard` 高亮与点击态）。
- **`pwa/sw.js`**：`PRECACHE` 追加 `phrases.json` 与 4 个 `deck_*.json`；`CACHE_VER` `en2-v8` → `en2-v9`。

### 校验
- `tools/validate.py` 16 个 JSON 均合法；`node --check` 全部 JS 通过。

## [en2-v8] 2026-07-27

### 多词书系统：一个词可归属多本词书
- **数据模型升级**：`vocab` 记录新增 `decks: string[]` 字段（记忆进度 `srs` 仍按词全局共享一份），不升级 IndexedDB 版本；词书元数据（id/名称/内置标记/排序）存 `localStorage`（`en2_decks`），并随备份导出/导入，双端迁移不丢词书名。
- **内置「我的生词本」**：`default` 词书不可删除，首次加载自动确保存在；一次性迁移 `migrateVocabDecks()` 给历史生词补 `decks:['default']`，计数准确。
- **收藏目标（当前词书）**：文章点词收藏、一键记录默认进「当前词书」（默认「我的生词本」），可在单词本页切换。

### 精读页：一键记录难词
- 顶栏「高亮难词」旁新增**「记录生词」**按钮：`recordArticleWords()` 把本篇所有词典命中且尚未收录的较难词（按词形去重）一键批量加入当前词书，释义/音标取自离线词典，例句取该词首次出现句。

### 背单词页：按词书背
- `study.html` 顶部新增**词书选择条**（全部 + 各词书含计数）；`buildQueue` 改为按所选词书过滤（`en2_studyDeck`），记忆进度跨词书天然一致；支持从单词本「背这本 →」带 `?deck=` 直达。

### 单词本页：词书管理 + 导入
- 生词本升级为**单词本**：顶部词书标签（计数、设为收藏目标、每本「背这本 →」、重命名/删除自建词书）、「＋ 新建词书」；列表按所选词书过滤。
- **导入词书**：选择单文件 UTF-8 JSON（`{ name, words:[{word,meaning,phonetic?,example_en?,example_cn?}] }`）→ 新建同名词书并批量入库；同名词已存在只并入词书、不覆盖释义与进度。

### 导航与清单
- 全站导航「生词本」文案改为**「单词本」**（仍指向 `vocab.html`）。
- `pwa/sw.js`：`CACHE_VER` 升级为 `en2-v8`（无新增文件，逻辑均落在既有 js 内）。

### 校验
- `node --check` 全部 JS 通过；各页含 `viewport` meta，词书选择条/标签样式含夜间模式与 ≤600px 适配。

## [en2-v7] 2026-07-27

### 离线词典：正文任意难词可点查释义
- **新增离线词典基础设施**：`tools/build_dict.py` 从 ECDICT 词库抽取本站语料中的较难词/词组，产出 `pwa/data/dict.json`（1396 难词 + 346 词形变形，约 158.5KB），运行时由新增的 `pwa/js/dict.js` 加载并做词形还原查询（`0:lemma`）。
- **精读页任意难词可点**：正文中命中词典的较难词均可点击，弹窗显示音标+释义并支持「加入生词本」，不再局限于预标注的词组；词典加载失败时自动降级为仅预标注词可点。
- **高亮难词开关**：顶栏新增「高亮难词」开关（`localStorage` 记忆状态），一键为正文较难词加琥珀底色，方便快速扫读生词。

### 背单词卡：翻面改点击展开
- 单词卡由 3D 翻面改为**点击/空格原位展开释义**（`max-height` 过渡动画），在手机上更稳定、无翻转闪烁；卡片文案同步为「点击卡片 / 空格 展开释义」。

### 做题面板：清除重做
- 做题头部新增**「清除重做」**按钮：`storage.js` 新增 `clearAnswers(articleId)` 清空本篇作答记录，完形题重渲染选项、阅读题重置作答，便于二刷。

### 全站移动端响应式
- 仅调整 `css/style.css`：新增 **≤600px 手机端**断点——导航栏窄屏换行（品牌+工具占一行、链接整行可横滑，避免溢出丢链接）、首页留白收紧、精读页阅读区与底部抽屉高度优化、背单词卡与评分按钮触屏适配（隐藏键盘提示 `kbd`）；单词释义弹窗 `max-width` 防超出视口。

### 清单与缓存
- `pwa/sw.js`：PRECACHE 补入 `js/dict.js`、`data/dict.json`，`CACHE_VER` 升级为 `en2-v7`（客户端自动换新缓存）。

### 校验
- 词典产物抽查：难词命中与词形还原正确（少量专有名词属可接受权衡）；`js/dict.js`、`data/dict.json` 均存在且被 `article.html` 正确引用。
- 全部页面含 `viewport` meta，响应式规则在窄屏生效。

## [en2-v6] 2026-07-27

### 题库扩充：补齐 2023–2025 三年真题
- **新增 2023、2024、2025 共 3 年**真题精翻数据（`pwa/data/2023.json`–`2025.json`），每年 4 篇阅读（Text1–4），本批共 12 篇、60 题；至此题库覆盖 **2010–2025 共 16 年、64 篇、320 题**。
  - 2023/2024 解析、2025 真题与解析 PDF 均为扫描图片（无文本层），经 OCR 识别后逐句校对英汉对照与逐题细解。
  - 原文/题干/选项照抄真题；`answer` 以解析 PDF 公布答案为准并逐题核对，`explanation` 依据解析提炼，`related_sentences` 对应标注。
  - 2025 答案键：21B22C23A24D25A · 26B27C28C29B30C · 31A32B33A34B35D · 36C37D38A39D40D。

### 新增「背单词」模块（单词卡 + 间隔重复）
- **新页面 `study.html` + `js/study.js`**：以生词本为队列的单词卡背诵，完全离线、纯前端。
  - **间隔重复**（SM-2 简化版）：复习状态写入 `vocab` 记录的 `srs` 字段（间隔/复习次数/难度系数），随备份一并导出；「认识」按记忆曲线拉长间隔，「不认识」打回 1 天并本轮补考。
  - **释义加粗规则**：词性斜体主色、核心义加粗主色、次要义弱化；例句中目标词加粗高亮。
  - 单词卡翻面（3D）、🔊 浏览器发音、键盘快捷键（空格翻面 / ← 不认识 / → 认识）、待复习/新词/剩余计数与进度条。
  - 生词本页新增「开始背单词」入口条（显示今日待背数量）。

### 阅读体验：封面不再剧透概要
- **首页卡片改显英文标题**（原展示中文概要，易剧透）；「本文概要」中文摘要移至精读页，**默认隐藏，仅在打开顶栏「全文翻译」时显示**。
- **正文高亮**：已加入生词本的词在原文中以琥珀色背景高亮，便于复习时定位。

### 清单与缓存
- `pwa/data/index.json`：新增 2023–2025 年份条目（降序，counts 与年份文件严格一致）。
- `pwa/sw.js`：PRECACHE 补入 `2023–2025.json`、`study.html`、`js/study.js`，`CACHE_VER` 升级为 `en2-v6`（客户端自动换新缓存）。

### 校验
- 全量 `python -X utf8 tools/validate.py`：**16 个年份文件、64 篇，共 0 错误 0 警告**。
- 本地 8410 端到端走查通过：封面显英文标题（无概要）→ 精读页概要随「全文翻译」显隐 → 点词加入生词本（正文琥珀高亮）→ 背单词卡翻面/加粗/发音/判定/完成态 → 生词本 CTA 计数 → 控制台无报错。

## [en2-v5] 2026-07-27

### 题库扩充：2015–2022 八年真题
- **新增 2015–2022 共 8 年**真题精翻数据（`pwa/data/2015.json`–`2022.json`），每年 4 篇阅读（Text1–4），本批共 32 篇、160 题；至此题库覆盖 **2010–2022 共 13 年、52 篇、260 题**。
  - 英文原文：从真题 PDF 提取并逐句校对、修复 OCR 噪点（如 `agricultoal→agricultural`、`fhistrated→frustrated`、`Brigmill→Brignull` 等）。
  - 题干/选项照抄真题 PDF；`answer` 以官方解析 PDF 公布答案为准；`explanation` 依据解析 PDF 提炼简明中文（含定位依据），`related_sentences` 对应标注。
  - 中文精翻参考解析 PDF 逐句对齐润色；词汇沿用"词组优先"规约（`w` 为原句大小写精确文本）。
- **2023–2025 暂缺**：经甄别，2023–2024 解析 PDF、2025 真题与解析 PDF 均为扫描版（无文本层），无法保证原文/答案准确，暂不制作。

### 清单与缓存
- `pwa/data/index.json`：新增 2015–2022 年份条目（降序排列，counts 与年份文件严格一致）。
- `pwa/sw.js`：PRECACHE 数据清单补入 `2015–2022.json`，`CACHE_VER` 升级为 `en2-v5`（客户端自动换新缓存）。

### 校验
- 全量 `python -X utf8 tools/validate.py`：**13 个年份文件、52 篇，共 0 错误 0 警告**；index 与年份文件计数、标题、主题逐项交叉核对，**0 处不一致**。

## [en2-v3] 2026-07-28

### 精读页交互微调
- **定位黄框可取消**：再次点击题目解析中的"定位原文依据"按钮即可清除关联句的黄色高亮（按钮变为红色"✕ 取消定位"）。
- **题目译文受"全文翻译"开关控制**：题干与选项的中文默认隐藏，由顶栏"全文翻译"开关统一显示/隐藏。
- **占位条图标更换**：句下"点击查看翻译"占位条图标由 ☝ 手指改为简洁下三角 ▾。
- `pwa/sw.js`：`CACHE_VER` 升级为 `en2-v3`（客户端自动拉取新代码）。

## [en2-v2] 2026-07-28

### 重大数据来源变更
- **下架全部 AI 编造题库**：删除 `pwa/data/2022.json`、`2023.json`、`2024.json`（此前由 AI 编造，原文/题目/答案均有误，经用户确认作废）。
- **改用真题 PDF 原文重做数据**：首批上线 **2010–2014 五年**真题，每年 4 篇阅读（Text1–4），共 20 篇。
  - 英文原文：从真题 PDF 提取并逐句校对、修复 OCR 噪点。
  - 题干/选项：照抄真题 PDF；`answer` 以官方解析 PDF 公布答案为准；`explanation` 依据解析 PDF 解题思路提炼为简明中文（含定位依据），`related_sentences` 对应标注。
  - 中文精翻：参考解析 PDF 全文翻译逐句对齐润色；词汇标注沿用"词组优先"规约（`w` 为原句精确文本）。
  - 各篇 `source` 统一标注："20XX 年考研英语（二）Text N · 原文与答案依据真题及解析 PDF"。
- **新增提取工具** `tools/extract_pdf.py`（基于 PyMuPDF）：按年份提取真题与解析 PDF 全文文本到 `tools/extracted/`，供制作 JSON 时对照。

### 界面改版（对标精读类 App）
- **逐句"点击查看翻译"占位条**：每句英文下方常驻浅青色占位条，点击原位展开中文译文，再点击收回；顶栏"全文翻译"开关改为批量展开/收起所有译文。
- **右侧题目面板可收缩**：面板顶部新增"» 收起"按钮，收起后正文占满宽度、右缘保留悬浮"题目"竖条可再展开；状态存 localStorage（`quizCollapsed`）。窄屏（≤768px）底部抽屉形态下同样生效。

### 清单与缓存
- 重写 `pwa/data/index.json` 为 2010–2014 五年（counts 与年份文件严格一致）。
- `pwa/sw.js`：PRECACHE 数据清单更新为 `index.json` + `2010–2014.json`，`CACHE_VER` 升级为 `en2-v2`（客户端自动换新缓存）。

### 校验与走查
- 全量 `python -X utf8 tools/validate.py`：5 个年份文件、20 篇、共 **0 错误 0 警告**（含 index 一致性校验）。
- 本地 8410 预览走查通过：年份列表（2010–2014）→ 精读页占位条点击翻译 / 全文翻译开关 → 词组下划线弹卡 → 右侧面板收缩/展开 → 做题判分与定位原文 → 无控制台报错。

### 后续计划
- 完形/新题型（Part B）仍留后续批次（代码已支持）。
- 2015–2025 分批补齐：每批只新增 JSON + 更新 PRECACHE + `CACHE_VER` 递增。
