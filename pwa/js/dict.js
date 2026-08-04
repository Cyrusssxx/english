/* 离线精简词典：一次 fetch data/dict.json，供精读页「难词可点 / 高亮」共用。
   仿 storage.js 内存缓存范式：模块级 _dict 只加载一次。 */
let _dict = null;

/** 加载词典（只发一次 fetch）。失败静默降级为空词典，不阻断页面。 */
async function loadDict() {
    if (_dict) return _dict;
    try {
        const res = await fetch('data/dict.json');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        _dict = await res.json();
    } catch (e) {
        _dict = { version: '', words: {}, forms: {} };  // 降级：仅预标注词可点
        console.warn('[dict] 词典加载失败，降级为仅预标注词可点：', e.message);
    }
    return _dict;
}

/** 归一化：小写 + 去首尾非字母（保留内部连字符/撇号）。 */
function normWord(word) {
    return String(word || '').toLowerCase().replace(/^[^a-z]+/, '').replace(/[^a-z]+$/, '');
}

/** 查词：小写 → forms 变形还原 → words。命中返回 {p,t,frq,tag}，否则 null。 */
function dictLookup(word) {
    if (!_dict) return null;
    const w = normWord(word);
    if (!w) return null;
    if (_dict.words[w]) return _dict.words[w];
    const base = _dict.forms[w];
    if (base && _dict.words[base]) return _dict.words[base];
    return null;
}

/** 是否难词（词典可查即为难词，简单词构建期已剔除）。 */
function isHardWord(word) {
    return dictLookup(word) !== null;
}

/* ── 精选难词集合：一次 fetch data/hardwords.json（熟词僻义 + 真题较难词），
    供精读页「高亮难词」只标真难词/易错词，而非所有词典命中词。 ── */
let _hard = null;   // Set<小写词/词组>

/** 加载精选难词集合（只发一次 fetch）。失败静默降级为空，不高亮任何词。 */
async function loadHardwords() {
    if (_hard) return _hard;
    try {
        const res = await fetch('data/hardwords.json');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        _hard = new Set((data.words || []).map(w => String(w).toLowerCase()));
    } catch (e) {
        _hard = new Set();
        console.warn('[dict] 精选难词集合加载失败，降级为空：', e.message);
    }
    return _hard;
}

/** 精选集合是否加载成功（非空）。失败降级时返回 false，调用方可回退旧逻辑。 */
function isHardLoaded() {
    return !!_hard && _hard.size > 0;
}

/** 制作考频徽标 HTML */

/* ── 中文反查：按中文释义找英文单词/词组（词典 words + 词组 phrases 合建索引） ── */
let _cnIndex = null;   // [{ en, meaning, isPhrase }]，懒构建

/** 构建中文→英文反查索引（words 的 t 字段 + phrases 的中文含义）。未加载词典时返回空。 */
function cnIndex() {
    if (_cnIndex) return _cnIndex;
    const arr = [];
    if (_dict && _dict.words) {
        for (const w of Object.keys(_dict.words)) {
            const t = _dict.words[w].t;
            if (t) arr.push({ en: w, meaning: t, isPhrase: false });
        }
    }
    if (_phrases) {
        for (const k of Object.keys(_phrases)) {
            arr.push({ en: k, meaning: _phrases[k], isPhrase: true });
        }
    }
    _cnIndex = arr;
    return _cnIndex;
}

/** 中文查英语：遍历释义含 query 的词/词组，返回 {en, meaning, isPhrase}[]，最多 limit 条。 */
function cnLookup(query, limit) {
    if (!_dict && !_phrases) return [];
    const q = String(query || '').trim().toLowerCase();
    if (!q) return [];
    const out = [];
    for (const it of cnIndex()) {
        if (!it.meaning) continue;
        if (it.meaning.toLowerCase().indexOf(q) !== -1) {
            out.push(it);
            if (out.length >= (limit || 10)) break;
        }
    }
    return out;
}

/** 是否精选难词（原始小写 → normWord → forms 原形三级命中）。 */
function isHard(word) {
    if (!isHardLoaded()) return false;
    const raw = String(word || '').toLowerCase().trim();
    if (_hard.has(raw)) return true;   // 词组 key / 原样命中
    const w = normWord(word);
    if (!w) return false;
    if (_hard.has(w)) return true;
    const base = _dict && _dict.forms && _dict.forms[w];
    if (base && _hard.has(base)) return true;
    return false;
}

/* ── 词组词典：一次 fetch data/phrases.json，供精读页「文章词组高亮/翻译」使用。 ── */
let _phrases = null;        // 扁平映射 { "phrase(小写单空格)": "中文含义" }
let _phraseIndex = null;    // Map(首词 → [{tokens:[...], key, meaning}]，按 token 数降序)
let _maxPhraseWords = 0;    // 最长词组的 token 数，供扫描时限定前瞻窗口

/** 加载词组词典（只发一次 fetch），并构建内存索引。失败静默降级为空。 */
async function loadPhrases() {
    if (_phrases) return _phrases;
    try {
        const res = await fetch('data/phrases.json');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        _phrases = data.phrases || {};
        _maxPhraseWords = data.maxWords || 0;
    } catch (e) {
        _phrases = {};
        _maxPhraseWords = 0;
        console.warn('[dict] 词组词典加载失败，降级为无词组高亮：', e.message);
    }
    _phraseIndex = new Map();
    for (const key in _phrases) {
        const tokens = key.split(' ');
        const first = tokens[0];
        let list = _phraseIndex.get(first);
        if (!list) { list = []; _phraseIndex.set(first, list); }
        list.push({ tokens, key, meaning: _phrases[key] });
    }
    // 同首词的候选按 token 数降序，扫描时可最长优先匹配
    for (const list of _phraseIndex.values()) {
        list.sort((a, b) => b.tokens.length - a.tokens.length);
    }
    return _phrases;
}

/** 查词组：key 为小写单空格短语。命中返回中文含义，否则 null。 */
function phraseLookup(key) {
    if (!_phrases) return null;
    const m = _phrases[String(key || '').toLowerCase()];
    return m || null;
}

/** 取以 firstWord 为首词的候选词组（已按 token 数降序），供扫描时最长优先匹配。 */
function phraseCandidates(firstWord) {
    return (_phraseIndex && _phraseIndex.get(firstWord)) || null;
}

/** 最长词组的 token 数（未加载时为 0）。 */
function maxPhraseWords() {
    return _maxPhraseWords;
}

/* ── 真题考频：一次 fetch data/freq.json，供弹卡/背词卡/单词本显示「出现 N 次」。 ── */
let _freq = null;   // { "词/词组key": {c:次数, a:文章数} }

/** 加载考频（只发一次 fetch）。失败静默降级为空，不显示徽标。 */
async function loadFreq() {
    if (_freq) return _freq;
    try {
        const res = await fetch('data/freq.json');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        _freq = await res.json();
    } catch (e) {
        _freq = {};
        console.warn('[dict] 考频加载失败，降级为不显示徽标：', e.message);
    }
    return _freq;
}

/** 查考频：单词按 normWord + forms 还原归一，词组按小写 key。命中返回 {c,a}，否则 null。 */
function freqLookup(word) {
    if (!_freq) return null;
    const raw = String(word || '').toLowerCase().trim();
    if (_freq[raw]) return _freq[raw];   // 词组 key（含空格）直接命中
    const w = normWord(word);
    if (!w) return null;
    if (_freq[w]) return _freq[w];
    const base = _dict && _dict.forms && _dict.forms[w];
    if (base && _freq[base]) return _freq[base];
    return null;
}

/** 生成考频徽标 HTML（供各弹卡/卡片复用）；无数据返回空串，绝不编造。 */
function freqBadge(word) {
    const f = freqLookup(word);
    if (!f || !f.c) return '';
    return `<span class="wp-freq">真题考频 · 出现 ${f.c} 次（${f.a} 篇）</span>`;
}

