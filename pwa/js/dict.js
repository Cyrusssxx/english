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
