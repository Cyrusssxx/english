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

