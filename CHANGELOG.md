# 更新日志 — 考研英语二真题精翻 PWA

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
