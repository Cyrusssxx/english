/* 作文模板库：大作文（图表作文）与小作文通用模板 + 图表适配指南 */
let WR = null;

const WR_PH = /\{\{(.+?)\}\}/g;

function wrEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 转义 + 占位符高亮（{{xxx}} → 蓝色可替换标记） */
function wrHl(s) {
    if (!s) return '';
    return wrEsc(s).replace(WR_PH, '<span class="wr-ph">$1</span>');
}

/** 纯文本版（去掉 {{ }}，供复制） */
function wrPlain(s) {
    return (s || '').replace(WR_PH, '$1');
}

function wrCopy(btn, text) {
    const done = () => {
        const old = btn.textContent;
        btn.textContent = '✓ 已复制';
        setTimeout(() => { btn.textContent = old; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(wrPlain(text)).then(done).catch(() => wrFallback(text, done));
    } else {
        wrFallback(text, done);
    }
}

function wrFallback(text, done) {
    const ta = document.createElement('textarea');
    ta.value = wrPlain(text);
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
}

/* ==================== 划词查词：精翻页同款，词组优先 ==================== */
let wrVocabSet = new Set();

async function wrInitVocab() {
    try {
        const rows = await dbAll('vocab');
        wrVocabSet = new Set((rows || []).map(r => r.word));
    } catch (e) { /* IndexedDB 不可用时降级为空 */ }
}

/** 词组 token 匹配：精确相等或词形还原后相等（draws=draw） */
function wrTokEq(tok, candWord) {
    if (tok.low === candWord) return true;
    if (typeof stemCandidates !== 'function') return false;
    const cands = stemCandidates(candWord);
    if (cands.includes(tok.low)) return true;
    const lows = stemCandidates(tok.low);
    return cands.some(c => lows.includes(c)) || cands.includes(tok.low) || lows.includes(candWord);
}

/** 高频功能词：单独出现时不进入划词（词组命中不受影响，仍整体可点） */
const WR_STOP = new Set(('a an the and or of in on to from with by as at for while that this these those it its is are was were be been being ' +
    'their they them we our you your him her his not no nor but so if then than when which who whom whose what where how ' +
    'will would can could shall should may might must do does did have has had more most less least very just only also too ' +
    'there here such own one two three over under between among about against during through across after before because ' +
    'although though since until unless whether either neither both each every any some all').split(' '));

/** 非占位符文本的词组优先标注：词组（真题词组表）→ 词组 span；其余每个单词 → 词 span（全部可点查） */
function wrAnnotatePlain(t) {
    if (!t) return '';
    if (typeof maxPhraseWords !== 'function' || maxPhraseWords() < 1 || typeof dictLookup !== 'function') {
        return wrEsc(t);   // 词典未加载/为空：纯文本
    }
    const TOK = /[A-Za-z][A-Za-z'\-]*/g;
    const toks = [];
    let m;
    while ((m = TOK.exec(t)) !== null) {
        toks.push({ s: m.index, e: m.index + m[0].length, low: m[0].toLowerCase(), raw: m[0] });
    }
    let out = '', last = 0, i = 0;
    while (i < toks.length) {
        let matched = null;
        const cands = phraseCandidates(toks[i].low);
        if (cands) {
            for (const c of cands) {                 // 候选已按 token 数降序 → 最长优先
                const n = c.tokens.length;
                if (i + n > toks.length) continue;
                let ok = true;
                for (let k = 1; k < n; k++) {
                    if (!wrTokEq(toks[i + k], c.tokens[k])) { ok = false; break; }
                    if (!/^[\s\-]*$/.test(t.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                }
                if (ok) { matched = c; break; }
            }
        }
        if (!matched) {                              // 首词未命中 → 词形还原后再试（draws out→draw out）
            for (const stem of stemCandidates(toks[i].low)) {
                const c2 = phraseCandidates(stem);
                if (!c2) continue;
                for (const c of c2) {
                    const n = c.tokens.length;
                    if (i + n > toks.length) continue;
                    let ok = true;
                    for (let k = 1; k < n; k++) {
                        if (!wrTokEq(toks[i + k], c.tokens[k])) { ok = false; break; }
                        if (!/^[\s\-]*$/.test(t.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                    }
                    if (ok) { matched = c; break; }
                }
                if (matched) break;
            }
        }
        if (matched) {
            const n = matched.tokens.length;
            const s0 = toks[i].s, e0 = toks[i + n - 1].e;
            out += wrEsc(t.slice(last, s0));
            out += `<span class="word phrase" data-w="${wrEsc(matched.key)}" data-ph="1">${wrEsc(t.slice(s0, e0))}</span>`;
            last = e0;
            i += n;
        } else if (!WR_STOP.has(toks[i].low)) {
            out += wrEsc(t.slice(last, toks[i].s));
            out += `<span class="word" data-w="${wrEsc(toks[i].low)}">${wrEsc(toks[i].raw)}</span>`;
            last = toks[i].e;
            i++;
        } else {
            i++;   // 高频功能词：跳过不标（词组命中的整组不受影响）
        }
    }
    out += wrEsc(t.slice(last));
    return out;
}

/** 划词标注入口：先按 {{占位符}} 切段（占位符只高亮不可点），段内做词组优先标注 */
function wrAnnotate(text) {
    if (!text) return '';
    let out = '', last = 0;
    const re = /\{\{(.+?)\}\}/g;
    let m;
    while ((m = re.exec(text)) !== null) {
        out += wrAnnotatePlain(text.slice(last, m.index));
        out += `<span class="wr-ph">${wrEsc(m[1])}</span>`;
        last = m.index + m[0].length;
    }
    out += wrAnnotatePlain(text.slice(last));
    return out;
}

/* ---- 释义弹卡（精翻页 word-pop 同款样式，自备定位与开关） ---- */
let wrPopEl = null;

function wrCloseWordPop() {
    if (wrPopEl) { wrPopEl.remove(); wrPopEl = null; }
}

function wrOpenPop(targetEl, html) {
    wrCloseWordPop();
    wrPopEl = document.createElement('div');
    wrPopEl.className = 'word-pop wr-pop-c';
    wrPopEl.innerHTML = html;
    document.body.appendChild(wrPopEl);
    const r = targetEl.getBoundingClientRect();
    const pw = wrPopEl.offsetWidth, ph = wrPopEl.offsetHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    let top = r.bottom + window.scrollY + 6;
    if (top + ph > window.scrollY + document.documentElement.clientHeight - 12) {
        top = Math.max(window.scrollY + 6, r.top + window.scrollY - ph - 6);
    }
    wrPopEl.style.left = left + 'px';
    wrPopEl.style.top = top + 'px';
}

/** 一个词可能的查表键：原词 / 归一形 / 去复数 / 词形还原候选（figures ↔ figure） */
function wrWordKeys(key, base) {
    const out = [];
    const push = x => { x = String(x || '').toLowerCase().trim(); if (x && !out.includes(x)) out.push(x); };
    push(key); push(base);
    [key, base].forEach(w => {
        if (/ies$/.test(w)) push(w.slice(0, -3) + 'y');
        if (/es$/.test(w)) push(w.slice(0, -2));
        if (/s$/.test(w) && !/ss$/.test(w)) push(w.slice(0, -1));
        push(w + 's');                                  // 表里可能收的是复数（wordnotes 有 figures 无 figure）
        push(w + 'es');
        if (/y$/.test(w)) push(w.slice(0, -1) + 'ies');
        if (typeof stemCandidates === 'function') stemCandidates(w).forEach(push);
    });
    return out;
}

/* ── 本句语境义（writing_senses.json）与真题熟词僻义（wordnotes.json） ── */
let WR_SENSES = null;    // { word: [本句义, 说明, U/C] }
let WR_WN = null;        // { word: wordnotes 行 }

async function wrLoadSenses() {
    const grab = u => fetch(u).then(r => (r.ok ? r.json() : null)).catch(() => null);
    try {
        const [s, w] = await Promise.all([grab('data/writing_senses.json'), grab('data/wordnotes.json')]);
        WR_SENSES = (s && s.words) || {};
        WR_WN = {};
        (((w && w.rows) || [])).forEach(r => { if (r && r.w) WR_WN[String(r.w).toLowerCase()] = r; });
    } catch (e) { WR_SENSES = WR_SENSES || {}; WR_WN = WR_WN || {}; }
}

/** 取消「弹卡所在位置」的高亮（点高亮里的词 → 弹卡 → 一键取消） */
function wrUnhlFromPop() {
    const mk = wrPopEl && wrPopEl.__mk;
    wrCloseWordPop();
    if (mk) wrHlRemoveMark(mk);
}

/** 点击词/词组：本句义 → 词典义 → 熟词僻义；均可加入生词本 */
function wrWordPop(el) {
    const key = el.getAttribute('data-w') || '';
    const isPhrase = el.getAttribute('data-ph') === '1';
    const base = (typeof normWord === 'function') ? normWord(key) : String(key).toLowerCase();
    const pick = map => {
        if (!map) return null;
        for (const c of wrWordKeys(key, base)) { if (map[c]) return map[c]; }
        return null;
    };
    const sense = pick(WR_SENSES);
    const wn = pick(WR_WN);
    let html = '';
    if (sense) {                       // 词典义项常常对不上本句，先给「本句义」
        html += `<div class="wp-sense"><span class="wp-sense-tag">📌 本句义</span>`
            + `<span class="wp-sense-cn">${wrEsc(sense[0])}</span>`
            + (sense[1] ? `<div class="wp-sense-note">${wrEsc(sense[1])}</div>` : '') + `</div>`;
    }
    if (isPhrase) {
        const meaning = phraseLookup(key);
        if (!meaning) return;
        html += `<div class="wp-phrase">${wrEsc(key)}</div><div class="wp-meaning">${wrEsc(meaning)}</div>`;
        html += key.split(/\s+/).map(w => {
            const entry = dictLookup(w);
            return `<div class="wpw"><span class="wpw-word word" data-w="${wrEsc(normWord(w))}">${wrEsc(w)}</span>` +
                (entry ? `<span class="wpw-mean">${wrEsc(entry.t)}</span>` : `<span class="wpw-mean wpw-none">（离线无释义）</span>`) + `</div>`;
        }).join('');
    } else {
        const entry = dictLookup(key);
        html += `<span class="wp-word">${wrEsc(key)}</span><span class="wp-phonetic">${wrEsc(entry ? entry.p || '' : '')}</span>` +
            `<div class="wp-meaning">${entry ? wrEsc(entry.t) : '（无离线释义）'}</div>`;
    }
    if (wn) {                          // 真题考过的熟词僻义（含真题例句）
        html += `<div class="wp-wn"><div class="wp-wn-t">⚡ 熟词僻义`
            + (wn.tier ? `<span class="wp-wn-tier">${wrEsc(wn.tier)}频</span>` : '')
            + (sense && sense[2] === 'U' ? `<span class="wp-wn-flag u">本句用的正是僻义</span>`
               : (sense && sense[2] === 'C' ? `<span class="wp-wn-flag">本句是熟义</span>` : ''))
            + `</div>`
            + `<div class="wp-wn-row"><b>熟义</b>${wrEsc(wn.common || '')}</div>`
            + `<div class="wp-wn-row"><b>僻义</b>${wrEsc(wn.uncommon || '')}</div>`
            + (wn.en ? `<div class="wp-wn-ex">${wrEsc(wn.en)}</div>` : '')
            + (wn.cn ? `<div class="wp-wn-excn">${wrEsc(wn.cn)}</div>` : '')
            + (wn.src ? `<div class="wp-wn-src">${wrEsc(wn.src)}</div>` : '') + `</div>`;
    }
    const inV = wrVocabSet.has(key);
    html += `<button class="${inV ? 'added' : ''}" data-w="${wrEsc(key)}" onclick="wrAddVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`;
    const mk = (el.closest && el.closest('mark.note-hl')) || null;
    if (mk) html += `<button class="wp-unhl" onclick="wrUnhlFromPop()">✕ 取消该处高亮</button>`;
    wrOpenPop(el, html);
    if (wrPopEl) wrPopEl.__mk = mk;    // 记住这处高亮，供上面的按钮取消
}

/** 加入/移出生词本（例句 = 当前模板句） */
async function wrAddVocab(btn) {
    const word = btn.getAttribute('data-w');
    if (!word) return;
    try {
        if (wrVocabSet.has(word)) {
            await dbDelete('vocab', word);
            wrVocabSet.delete(word);
            btn.textContent = '+ 加入生词本';
            btn.classList.remove('added');
        } else {
            const entry = dictLookup(word);
            const card = btn.closest('.word-pop');
            const exEn = card ? (card.getAttribute('data-ex') || '') : '';
            await addVocab(word, entry ? entry.t : '', entry ? entry.p : '', '', '', exEn, '', getVocabTarget());
            wrVocabSet.add(word);
            btn.textContent = '已加入 ✓';
            btn.classList.add('added');
        }
    } catch (e) { /* IndexedDB 不可用时静默 */ }
}

/** 全局委托：点词弹卡；点空白/其他区域关卡（卡内点击除外） */
function wrWordBind() {
    document.addEventListener('click', e => {
        const w = e.target.closest('.word');
        if (w && !e.target.closest('.wr-pop-c')) {   // 高亮里的词也要能查（取消高亮走弹卡内按钮 / 划选）
            e.stopPropagation();
            const line = w.closest('.wr-line, .wr-sent');
            wrWordPop(w);
            if (wrPopEl && line) wrPopEl.setAttribute('data-ex', line.textContent.replace(/\s+/g, ' ').trim());
            return;
        }
        if (!e.target.closest('.wr-pop-c')) wrCloseWordPop();
    }, true);   // 捕获阶段先执行，stopPropagation 避免与卡片其他点击冲突
}

/* ==================== 正文划词高亮 + 行批注（浮条交互，照搬 408 notes 页） ==================== */
const WR_MK_KEY = 'wr_mk_v1';
const WR_ANNO_KEY = 'wr_anno_v1';
const WR_HL_COLORS = ['yellow', 'green', 'blue', 'pink'];
const WR_HL_CN = { yellow: '黄色', green: '绿色', blue: '蓝色', pink: '粉色' };
const WR_MK_SEL = '.wr-line, .wr-line-cn, .wr-sent-txt, .wr-sent-cn, .wr-note-inline, .wr-note, .wr-tips li, .apply-para, .ap-tpl-en, .ap-tpl-cn';
/* 追加可高亮块：选句决策 / 数据描述语言 / 流程 / 错误清单——追加在注册表【尾部】，不插在卡片前，避免老高亮（按块序号存）错位 */
const WR_MK_EXTRA_SEL = '.wr-decision-v, .wr-decision-k, .wr-dl-name, .wr-dl-words, .wr-dl-how, .wr-mist-v, .wr-mist-k, .wr-flow-body, .wr-flow-head, .wr-frame-en, .wr-frame-trans, .wr-frame-cn, .wr-demo, #wrChecklist li, #wrChartTable td, .wr-rule, .wr-desc';
let wrMarks = [];        // 高亮 [{ c: 正文块序号, s: 起, e: 止, k: 颜色名 }]
let wrAnnos = {};        // 行批注 { 正文块序号: 文本 }
let wrHlBar = null;      // 划词浮条
let wrHlTimer = null;

function wrMkLoad() {
    try { wrMarks = JSON.parse(localStorage.getItem(WR_MK_KEY) || '[]') || []; }
    catch (e) { wrMarks = []; }
    if (!Array.isArray(wrMarks)) wrMarks = [];
    const LEGACY = { y: 'yellow', g: 'green', b: 'blue', p: 'pink' };
    wrMarks = wrMarks.filter(m => m && typeof m.c === 'number')
        .map(m => ({ c: m.c, s: m.s, e: m.e, k: WR_HL_COLORS.includes(m.k) ? m.k : (LEGACY[m.k] || 'yellow') }));
    try { wrAnnos = JSON.parse(localStorage.getItem(WR_ANNO_KEY) || '{}') || {}; }
    catch (e) { wrAnnos = {}; }
    if (!wrAnnos || typeof wrAnnos !== 'object' || Array.isArray(wrAnnos)) wrAnnos = {};
    try { localStorage.removeItem('wr_notes_hl_v1'); } catch (e) { /* 清掉更早一版的批注残留 */ }
}

function wrMkSave() {
    try { localStorage.setItem(WR_MK_KEY, JSON.stringify(wrMarks)); } catch (e) { /* ignore */ }
    const c = document.getElementById('wrMkCount');
    if (c) c.textContent = String(wrMarks.length);
    const b = document.getElementById('wrMkClearBtn');
    if (b) b.hidden = !wrMarks.length;
}

function wrAnnoSave() {
    try { localStorage.setItem(WR_ANNO_KEY, JSON.stringify(wrAnnos)); } catch (e) { /* ignore */ }
}

/** 可高亮正文块：一次 DFS 收集（命中即收、不再下钻，天然去掉嵌套），按文档序编号 data-mk */
function wrMkBlocks() {
    const out = [];
    (function walk(node) {
        for (const el of node.children) {
            if (el.matches(WR_MK_SEL)) { out.push(el); continue; }
            walk(el);
        }
    })(document.body);
    document.querySelectorAll(WR_MK_EXTRA_SEL).forEach(el => { if (!out.includes(el)) out.push(el); });
    for (let i = 0; i < out.length; i++) out[i].setAttribute('data-mk', String(i));
    return out;
}

function wrMkBlockOf(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return (el && el.closest) ? el.closest('[data-mk]') : null;
}

function wrInAnno(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return !!(el && el.closest && el.closest('.wr-anno, .hl-toolbar'));
}

/** 块内全部 Text 节点 → [{node, start, len}]（按文档序，start = 块内字符偏移） */
function wrMkTexts(el) {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const out = []; let acc = 0;
    while (tw.nextNode()) {
        const n = tw.currentNode;
        out.push({ node: n, start: acc, len: n.data.length });
        acc += n.data.length;
    }
    return out;
}

function wrMkOffset(texts, node, off) {
    for (const t of texts) if (t.node === node) return t.start + off;
    return null;
}

function wrMkAt(texts, off) {
    for (const t of texts) {
        if (off <= t.start + t.len) return { node: t.node, off: off - t.start };
    }
    const last = texts[texts.length - 1];
    return last ? { node: last.node, off: last.len } : null;
}

function wrMkRange(el, s, e) {
    const texts = wrMkTexts(el);
    const a = wrMkAt(texts, s), b = wrMkAt(texts, e);
    if (!a || !b) return null;
    if (a.node === b.node && a.off === b.off) return null;
    const r = document.createRange();
    r.setStart(a.node, a.off);
    r.setEnd(b.node, b.off);
    return r;
}

/** 当前选区 → { block, i, s, e }；失败时返回 { err } */
function wrMkSelInfo() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return { err: 'none' };
    const r = sel.getRangeAt(0);
    const b1 = wrMkBlockOf(r.startContainer), b2 = wrMkBlockOf(r.endContainer);
    if (!b1 || !b2 || b1 !== b2) return { err: 'none' };
    const texts = wrMkTexts(b1);
    const s = wrMkOffset(texts, r.startContainer, r.startOffset);
    const e = wrMkOffset(texts, r.endContainer, r.endOffset);
    if (s == null || e == null || e <= s) return { err: 'none' };
    return { block: b1, i: parseInt(b1.getAttribute('data-mk'), 10), s, e, range: r };
}

function wrMkUnwrap(mk) {
    const f = document.createDocumentFragment();
    while (mk.firstChild) f.appendChild(mk.firstChild);
    if (mk.parentNode) mk.replaceWith(f);
}

/** 重建单个块内的高亮 */
function wrMkPaint(block, i) {
    block.querySelectorAll('mark.note-hl').forEach(wrMkUnwrap);
    wrMarks.filter(m => m.c === i).sort((a, b) => a.s - b.s).forEach(m => {
        const r = wrMkRange(block, m.s, m.e);
        if (!r) return;
        const mk = document.createElement('mark');
        mk.className = 'note-hl note-hl-' + m.k;
        mk.dataset.start = String(m.s);
        mk.dataset.color = m.k;
        mk.title = '点击可取消这处高亮';
        try { mk.appendChild(r.extractContents()); r.insertNode(mk); } catch (e) { /* 越界忽略 */ }
    });
}

/** 全页重建：高亮 + 批注（渲染后 / 载入时调用） */
function wrRestoreAll() {
    document.querySelectorAll('mark.note-hl').forEach(wrMkUnwrap);
    document.querySelectorAll('.wr-anno').forEach(x => x.remove());
    const blocks = wrMkBlocks();
    const dirty = {};
    wrMarks.forEach(m => { dirty[m.c] = 1; });
    blocks.forEach((b, i) => { if (dirty[i]) wrMkPaint(b, i); });
    Object.keys(wrAnnos).forEach(k => {
        const i = parseInt(k, 10);
        if (blocks[i] && wrAnnos[k]) wrAnnoRender(i, blocks[i], wrAnnos[k]);
    });
    wrMkSave();
}

/* ---------- 上色 / 取消 ---------- */

function wrHlApply(color) {
    const sr = wrMkSelInfo();
    if (sr.err) { hideHlToolbar(); return; }
    wrMarks = wrMarks.filter(m => !(m.c === sr.i && m.s < sr.e && sr.s < m.e));   // 重叠的先去掉
    wrMarks.push({ c: sr.i, s: sr.s, e: sr.e, k: color });
    wrMkPaint(sr.block, sr.i);
    wrMkSave();
    hideHlToolbar();
    const s = window.getSelection(); if (s) s.removeAllRanges();
}

/** 取消选区起点所在那处高亮 */
function wrHlCancelAt(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    const mk = (el && el.closest) ? el.closest('mark.note-hl') : null;
    if (!mk) return false;
    wrHlRemoveMark(mk);
    return true;
}

function wrHlRemoveMark(mk) {
    const block = mk.closest('[data-mk]');
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    const s = parseInt(mk.dataset.start, 10);
    const k = mk.dataset.color;
    wrMarks = wrMarks.filter(m => !(m.c === i && m.s === s && m.k === k));
    wrMkPaint(block, i);
    wrMkSave();
}

async function wrMkClearAll() {
    if (!wrMarks.length) return;
    if (typeof confirmAsync === 'function' && !(await confirmAsync('清除本页全部划词高亮？', { danger: true }))) return;
    wrMarks = [];
    try { localStorage.removeItem(WR_MK_KEY); } catch (e) { /* ignore */ }
    document.querySelectorAll('mark.note-hl').forEach(wrMkUnwrap);
    wrMkSave();
}

/* ---------- 划词浮条（408 同款：4 色 + 📝批注 + ✕） ---------- */

function hideHlToolbar() { if (wrHlBar) { wrHlBar.remove(); wrHlBar = null; } }

/** 取选区位置：优先 Range 自带 rect，取不到（如 jsdom / 空选区）就退回起点元素 */
function wrRectOf(range) {
    let rect = null;
    try { rect = range.getBoundingClientRect(); } catch (e) { rect = null; }
    if (!rect || (!rect.width && !rect.height)) {
        const n = range.startContainer;
        const el = n && n.nodeType === 1 ? n : (n && n.parentElement);
        if (el && el.getBoundingClientRect) rect = el.getBoundingClientRect();
    }
    return rect || { top: 0, bottom: 0, left: 0, width: 0, height: 0 };
}

/** 浮条定位：默认放选区上方，撞到导航栏/视口顶就翻到选区下方 */
function wrHlBarPlace(bar, rect) {
    const bh = bar.offsetHeight, bw = bar.offsetWidth;
    const navH = wrNavH();
    let top = window.scrollY + rect.top - bh - 8;
    if (rect.top - bh - 8 < navH + 6) top = window.scrollY + rect.bottom + 8;
    let left = window.scrollX + rect.left;
    const maxLeft = window.scrollX + document.documentElement.clientWidth - bw - 8;
    if (left > maxLeft) left = Math.max(window.scrollX + 8, maxLeft);
    bar.style.top = top + 'px';
    bar.style.left = left + 'px';
}

function wrHlShowForSelection() {
    if (wrHlBar && wrHlBar.classList.contains('hl-cancel-only')) return;   // 别把「取消高亮」条顶掉
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { hideHlToolbar(); return; }
    const r = sel.getRangeAt(0);
    if (wrInAnno(r.startContainer) || wrInAnno(r.endContainer)) { hideHlToolbar(); return; }
    const sr = wrMkSelInfo();
    if (sr.err) { hideHlToolbar(); return; }
    hideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar';
    bar.innerHTML = WR_HL_COLORS.map(c =>
        '<span class="hl-dot hl-dot-' + c + '" data-color="' + c + '" title="' + WR_HL_CN[c] + '高亮"></span>').join('') +
        '<span class="hl-anno-btn" title="为这一行写批注">📝批注</span>' +
        '<span class="hl-cancel" title="取消这处高亮">✕</span>';
    document.body.appendChild(bar);
    wrHlBar = bar;
    wrHlBarPlace(bar, wrRectOf(r));
    bar.addEventListener('mousedown', e => e.preventDefault());   // 按住不丢选区
    bar.querySelectorAll('.hl-dot').forEach(dot =>
        dot.addEventListener('click', () => wrHlApply(dot.dataset.color)));
    bar.querySelector('.hl-anno-btn').addEventListener('click', () => wrAnnoOpenFrom(r));
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        wrHlCancelAt(r.startContainer);
        hideHlToolbar();
    });
}

/** 点已有高亮 → 只显示「✕ 取消高亮」 */
function wrHlShowCancelFor(mk) {
    clearTimeout(wrHlTimer);
    hideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar hl-cancel-only';
    bar.innerHTML = '<span class="hl-cancel" title="取消高亮">✕ 取消高亮</span>';
    document.body.appendChild(bar);
    wrHlBar = bar;
    wrHlBarPlace(bar, mk.getBoundingClientRect());
    bar.addEventListener('mousedown', e => e.preventDefault());
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        wrHlRemoveMark(mk);
        hideHlToolbar();
    });
}

function wrHlBind() {
    document.addEventListener('mouseup', () => {
        clearTimeout(wrHlTimer);
        wrHlTimer = setTimeout(wrHlShowForSelection, 0);
    });
    document.addEventListener('mousedown', e => {
        if (wrHlBar && !wrHlBar.contains(e.target)) hideHlToolbar();
    });
    document.addEventListener('click', e => {
        if (wrInAnno(e.target)) return;
        const mk = e.target.closest ? e.target.closest('mark.note-hl') : null;
        if (mk && !(e.target.closest && e.target.closest('.word'))) { e.stopPropagation(); wrHlShowCancelFor(mk); }
    });
    window.addEventListener('scroll', () => { if (wrHlBar) hideHlToolbar(); }, { passive: true });
}

/* ---------- 行批注（点 📝批注：在该行正下方开编辑框，自动保存） ---------- */

/** 批注框挂到"行级"元素之后（避免插进 flex 行/表格单元格里破坏布局） */
function wrAnnoAnchor(block) {
    if (block.matches('.wr-sent-txt, .wr-sent-cn')) return block.closest('.wr-sent') || block;
    if (block.matches('.ap-tpl-en, .ap-tpl-cn')) return block.closest('.ap-tpl-row') || block;
    return block;
}

function wrAnnoRender(i, block, text) {
    const box = document.createElement('div');
    box.className = 'wr-anno';
    box.dataset.anno = String(i);
    box.innerHTML = '<div class="wr-anno-head">📝 我的批注<span class="wr-anno-hint">自动保存</span></div>' +
        '<textarea class="wr-anno-input" rows="2" placeholder="写给这一行的批注…（留空即删除）"></textarea>' +
        '<div class="wr-anno-ops"><button type="button" class="wr-anno-del">删除批注</button></div>';
    const ta = box.querySelector('textarea');
    ta.value = text || '';
    let timer = null;
    const commit = () => {
        const v = ta.value.trim();
        if (v) wrAnnos[i] = v; else delete wrAnnos[i];
        wrAnnoSave();
    };
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(commit, 600); });
    ta.addEventListener('blur', () => { clearTimeout(timer); commit(); });
    box.querySelector('.wr-anno-del').addEventListener('click', () => {
        delete wrAnnos[i];
        wrAnnoSave();
        box.remove();
    });
    wrAnnoAnchor(block).insertAdjacentElement('afterend', box);
    return box;
}

function wrAnnoOpenFrom(range) {
    const block = wrMkBlockOf(range.startContainer);
    const sel = window.getSelection(); if (sel) sel.removeAllRanges();
    hideHlToolbar();
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    let box = document.querySelector('.wr-anno[data-anno="' + i + '"]');
    if (!box) box = wrAnnoRender(i, block, wrAnnos[i] || '');
    if (box.scrollIntoView) box.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    const ta = box.querySelector('textarea');
    if (ta) ta.focus();
}

/** 数字换字体：Georgia 是「旧式数字」（3/4/5/7/9 掉基线），包 span 走衬线 lining 数字 */
function wrNumWrap(html) {
    if (!html) return html;
    return html.replace(/(^|>)([^<]*)/g, (m, pre, seg) => pre + seg.replace(/\d+(?:[.,:]\d+)*%?/g, d => '<span class="wr-num">' + d + '</span>'));
}

/* ==================== ✨ 精句弹窗：本卡有用词组/短句（英中对照） ==================== */
function wrShowPhrases(secId) {
    const sec = (WR.sections || []).find(s => s.id === secId);
    if (!sec || !(sec.phrases || []).length) return;
    document.getElementById('wrPopTitle').textContent = (sec.title || '') + ' · 精句词组';
    const sub = document.getElementById('wrPopSub');
    if (sub) sub.textContent = '共 ' + sec.phrases.length + ' 条 · 点英文里的单词可查释义';
    document.getElementById('wrPopBody').innerHTML = wrNumWrap(sec.phrases.map((p, i) =>
        `<div class="wr-pop-row"><span class="wr-pop-no">${i + 1}</span><div class="wr-pop-txt">` +
        `<div class="wr-pop-en">${wrAnnotate(p[0])}</div><div class="wr-pop-cn">${wrEsc(p[1])}</div></div></div>`).join(''));
    document.getElementById('wrPopMask').hidden = false;
    document.getElementById('wrPop').hidden = false;
}

function wrClosePhrases() {
    document.getElementById('wrPopMask').hidden = true;
    document.getElementById('wrPop').hidden = true;
}

/* ==================== 结构染色开关 ==================== */
function wrToggleStruct() {
    localStorage.setItem(WR_STRUCT_KEY, wrStructOn() ? '0' : '1');
    wrRenderCards();
    wrTocSpy();
}

/** 重渲染模板卡（开关切换后调用），并恢复已点亮状态 */
function wrRenderCards() {
    if (!WR) return;
    const groups = {};
    for (const s of WR.sections || []) {
        (groups[s.group] || (groups[s.group] = [])).push(s);
    }
    const html = Object.keys(groups).map((gname, gi) => `
        <h2 class="wr-h2" id="wrGroup${gi}">${wrEsc(gname)}</h2>
        ${groups[gname].map(wrSectionCard).join('')}`).join('');
    document.getElementById('wrContent').innerHTML = wrNumWrap(html);
    for (const id of ('wrStructState wrStructNavState').split(' ')) {
        const st = document.getElementById(id);
        if (st) st.textContent = wrStructOn() ? '开' : '关';
    }
    wrRestoreAll();
}

/* ==================== 模板正文：按句拆行（英文行 + 对齐的中文行） ==================== */
function wrSplitEn(t) {
    const m = (t || '').match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g) || [];
    return m.map(x => x.trim()).filter(Boolean);
}

function wrSplitCn(t) {
    const m = (t || '').match(/[^。！？]*[。！？]|[^。！？]+$/g) || [];
    return m.map(x => x.trim()).filter(Boolean);
}

/** 英文按句拆行；中文句数对齐时逐句配对，不齐则整段；
 *  struct = 每句的片段标注（[[text, role], ...]），开启「结构染色」时**划词式**染色（下划线着色，非色块） */
/* 主干染色：只标主谓宾表（单色浅黄高亮，不再多色划线），信号词不再上色 */
const WR_ROLE_CLS = { t: 'wr-trunk', p: 'wr-trunk', o: 'wr-trunk' };
const WR_STRUCT_KEY = 'wr_struct_on';

function wrStructOn() { return localStorage.getItem(WR_STRUCT_KEY) !== '0'; }

function wrSentenceHtml(s, struct) {
    if (wrStructOn() && struct && struct.length) {
        return struct.map(seg => {
            const cls = WR_ROLE_CLS[seg[1]] || '';
            const inner = wrAnnotate(seg[0]);
            return cls ? `<span class="${cls}">${inner}</span>` : inner;
        }).join('');
    }
    return wrAnnotate(s);
}

function wrTplBody(en, cn, struct) {
    const es = wrSplitEn(en);
    const cs = wrSplitCn(cn);
    const aligned = es.length > 0 && es.length === cs.length;
    const enHtml = es.map((s, i) =>
        `<div class="wr-line">${wrSentenceHtml(s, struct && struct[i])}</div>`).join('');
    const cnHtml = aligned
        ? cs.map((s, i) => `<div class="wr-line-cn">${wrHl(s)}</div>`).join('')
        : `<div class="wr-line-cn">${wrHl(cn || '')}</div>`;
    return { enHtml, cnHtml };
}

/** 复制整段英文（行 div 的 textContent 无空格，需按行拼接） */
function wrCopyLines(btn) {
    const en = btn.closest('.wr-tpl').querySelector('.wr-en, .wr-frame');
    const t = Array.from(en.querySelectorAll('.wr-line, .wr-frame-en')).map(x => x.textContent).join(' ');
    wrCopy(btn, t);
}

/** 骨架同义升级提示：{原词: '替换词 / 替换词'} → 一行小字 */
function wrAlts(alts) {
    if (!alts) return '';
    const rows = Object.entries(alts).map(([k, v]) => `<span class="wr-alt"><b>${wrEsc(k)}</b> → ${wrEsc(v)}</span>`);
    return rows.join('<span class="wr-alt-sep">｜</span>');
}

/** 高级衔接词提示：[{banned:'烂大街', better:'高级替换'}] → 一行小字 */
function wrLinkers(linkers) {
    if (!linkers || !linkers.length) return '';
    return linkers.map(x => `<span class="wr-alt"><b>${wrEsc(x.banned)}</b> → ${wrEsc(x.better)}</span>`).join('<span class="wr-alt-sep">｜</span>');
}

/** 考研口径词数：含字母或数字的空白串才算一个词（占位符 {{x}} 算 1 个） */
function wrWords(t) {
    return ((t || '').match(/[A-Za-z0-9][A-Za-z0-9'’%.,:_-]*/g) || []).length;
}

function wrSectionCard(sec) {
    // 考频优先展示（数据里新句追加在池尾，但不能让 ★ 排在 ★★★ 前面）
    const pool = (sec.sentences || []).slice().sort((a, b) => (b.freq || 2) - (a.freq || 2));
    const sents = pool.map((s, i) => `
        <li class="wr-sent">
            <div class="wr-sent-en"><span class="wr-sent-no">${i + 1}</span>${s.freq ? `<span class="wr-freq" title="考频：★★★ 通用（跨话题都能接）/ ★★ 常用 / ★ 专场">${'★'.repeat(s.freq)}</span>` : ''}${s.tag ? `<span class="wr-tag">${wrEsc(s.tag)}</span>` : ''}<span class="wr-sent-txt">${wrAnnotate(s.en)}</span></div>
            <div class="wr-sent-cn">${wrHl(s.cn)}</div>
        </li>`).join('');

    const tips = (sec.tips || []).map(x => `<li>${wrEsc(x)}</li>`).join('');
    const body = wrTplBody(sec.en, sec.cn, sec.en_struct);
    const skels = sec.skeletons || null;
    const skW = skels ? skels.map(v => wrWords(v.en)) : null;
    const neg = sec.negative_en ? wrTplBody(sec.negative_en, sec.negative_cn, sec.negative_struct) : null;

    const nS = (sec.sentences || []).length;
    const mustBadge = skels
        ? `⭐ 必背 ${skels.length} 选 1 · 每套 ${Math.min.apply(null, skW)}~${Math.max.apply(null, skW)} 词`
        : sec.framework
        ? `⭐ 必背框架 · ${sec.framework.length} 步拼装 · 引入句 ${wrWords(sec.en)} 词`
        : `⭐ 必背 ${wrWords(sec.en)} 词`;
    const fwHtml = sec.framework
        ? `<div class="wr-frame"><div class="wr-frame-title">🧩 第二段框架（${sec.framework.length} 步拼装 · 必背就这 ${sec.framework.length} 步）</div>${sec.framework.map((f, i) => `
            <div class="wr-frame-step"><span class="wr-frame-no">${i + 1}</span><span class="wr-frame-txt"><span class="wr-frame-en">${wrEsc(f.en)}</span>${f.trans ? `<span class="wr-frame-trans">${wrEsc(f.trans)}</span>` : ''}<span class="wr-frame-cn">${wrEsc(f.cn)}</span></span></div>`).join('')}</div>`
        : '';
    const tailRows = (sec.alts ? `<div class="wr-alts">✎ 同义升级：${wrAlts(sec.alts)}</div>` : '')
        + (sec.linkers ? `<div class="wr-alts">✎ 高级衔接词：${wrLinkers(sec.linkers)}</div>` : '')
        + (sec.demo ? `<div class="wr-demo"><b>例</b>${wrAnnotate(sec.demo)}</div>` : '');
    const tplBody = skels
        ? skels.map(v => {
            const b2 = wrTplBody(v.en, v.cn, v.struct);
            return `<div class="wr-skel">
                <div class="wr-skel-head"><span class="wr-skel-label">${wrEsc(v.label)}</span>
                    <span class="wr-skel-years">适用 ${wrEsc(v.years)}</span>
                    <span class="wr-skel-w">${wrWords(v.en)} 词</span></div>
                <div class="wr-en">${b2.enHtml}</div>
                <div class="wr-cn">${b2.cnHtml}</div>
                ${v.alts ? `<div class="wr-alts">✎ 同义升级：${wrAlts(v.alts)}</div>` : ''}
                ${v.demo ? `<div class="wr-demo"><b>例</b>${wrAnnotate(v.demo)}</div>` : ''}
            </div>`;
        }).join('')
        : fwHtml ? fwHtml + tailRows
        : `<div class="wr-en">${body.enHtml}</div>
            <div class="wr-cn">${body.cnHtml}</div>` + tailRows;
    return `
    <section class="wr-card" id="${sec.id}">
        <div class="wr-card-head">
            <div class="wr-card-head-txt">
                <h3 class="wr-card-title">${wrEsc(sec.title)}</h3>
                ${sec.subtitle ? `<div class="wr-card-sub">${wrEsc(sec.subtitle)}</div>` : ''}
                <div class="wr-badges">
                    <span class="wr-badge wr-badge-must">${mustBadge}</span>
                    ${nS ? `<span class="wr-badge wr-badge-ammo">⚡ 弹药 ${nS} 句</span>` : ''}
                    ${sec.priority ? '<span class="wr-badge wr-badge-top">优先背</span>' : ''}
                </div>
            </div>
            <button class="wr-copy" onclick="wrShowPhrases('${wrEsc(sec.id)}')" title="本段有用词组/短句（英中对照）">✨ 精句</button>
        </div>
        <div class="wr-tpl">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag">${skels ? '⭐ 必背骨架（先看走势，选一套）' : '⭐ 必背骨架（背熟这段，结构就稳了）'}</span>
                <button class="wr-copy" onclick="wrCopyLines(this)">复制</button>
            </div>
            ${tplBody}
        </div>
        ${neg ? `
        <div class="wr-tpl wr-tpl-neg">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag wr-tag-neg">负面版（选一）</span>
                <button class="wr-copy" onclick="wrCopyLines(this)">复制</button>
            </div>
            <div class="wr-en">${neg.enHtml}</div>
            <div class="wr-cn">${neg.cnHtml}</div>
        </div>` : ''}
        ${sents ? `<div class="wr-sents"><div class="wr-sents-title">⚡ 弹药句池（挑 1~2 句接在骨架后面，共 ${nS} 句可选）
                    <span class="wr-sents-legend"><b>★★★</b> 通用 · 跨话题都能接，优先挑；<b>★★</b> 常用；<b>★</b> 专场</span></div><ol class="wr-sent-list">${sents}</ol></div>` : ''}
        ${sec.note ? `<div class="wr-note-inline">💡 ${wrHl(sec.note)}</div>` : ''}
        ${tips ? `<ul class="wr-tips">${tips}</ul>` : ''}
    </section>`;
}

/** 展开行的真题套用示范内容（示范文 + 建议 + 关键句型） */
function wrApplyHtml(year, ap) {
    const mk = (typeof APPLY_MARKS !== 'undefined' && APPLY_MARKS) ? APPLY_MARKS[year] : null;
    const bodyHtml = renderApplyBody(mk, wrAnnotatePlain)     // 示范文的词也可点（同一套词典）
        || `<div class="apply-en">${wrAnnotatePlain(ap.apply_en || '')}</div>`;
    const tips = (ap.tips || []).map(x => `<li>${wrEsc(x)}</li>`).join('');

    return wrNumWrap(`<div class="wr-apply-detail">
        <div class="wr-apply-title">${wrEsc(year)} 真题套用示范${ap.title ? ' · ' + wrEsc(ap.title) : ''}</div>
        <div class="apply-en">${bodyHtml}</div>
        ${ap.apply_cn ? `<div class="apply-cn">${renderApplyCn(mk, ap.apply_cn)}</div>` : ''}
        ${renderApplyMarks(mk)}
        ${tips ? `<div class="ap-sub">📝 套用建议</div><ul class="apply-tips">${tips}</ul>` : ''}
        ${renderSlotPhrases((mk && mk.slot_phrases) || ap.slot_phrases)}
        ${renderKeyPhrases((mk && mk.key_phrases) || ap.key_phrases)}
    </div>`);
}

/** 展开/收起某年份的套用示范 */
function wrToggleApply(i) {
    const row = document.getElementById('wrApplyRow' + i);
    if (!row) return;
    const btn = event && event.target;
    const show = row.hidden;
    row.hidden = !show;
    if (btn) btn.textContent = show ? '收起示范 ▴' : '展开示范 ▾';
}

/** 允许 <b> 的富文本：转义 → 包 {{}} 占位符 → 还原 <b> */
function wrRich(s) {
    return wrEsc(s)
        .replace(/\{\{(.+?)\}\}/g, '<span class="wr-ph">{{$1}}</span>')
        .replace(/&lt;(\/?b)&gt;/g, '<$1>');
}

/* ==================== 🎓 评分老师视角 / ✍️ 答题动线 / 📐 数据语言 / ✅ 自查表 ==================== */

function wrRenderFlow() {
    const box = document.getElementById('wrFlow');
    if (!box) return;
    box.innerHTML = (WR.flow || []).map((x, i) => `
        <div class="wr-flow-step">
            <div class="wr-flow-head"><span class="wr-flow-no">${i + 1}</span><b>${wrEsc(x[0].replace(/^[①-⑥]\s*/, ''))}</b>
                <span class="wr-flow-time">${wrEsc(x[1])}</span></div>
            <div class="wr-flow-body">${wrRich(x[2])}</div>
        </div>`).join('');
}

function wrRenderDataLang() {
    const box = document.getElementById('wrDataLang');
    if (!box) return;
    box.innerHTML = (WR.data_lang || []).map(x => `
        <div class="wr-dl-card">
            <div class="wr-dl-name">${wrEsc(x[0])}</div>
            <div class="wr-dl-words">${wrEsc(x[1])}</div>
            <div class="wr-dl-how">${wrRich(x[2])}</div>
        </div>`).join('');
    const mb = document.getElementById('wrMistakes');
    if (mb) mb.innerHTML = (WR.mistakes || []).map(x => `
        <div class="wr-mist-row"><span class="wr-mist-k">${wrEsc(x[0])}</span>
        <span class="wr-mist-v">${wrRich(x[1])}</span></div>`).join('');
}

function wrRenderChecklist() {
    const box = document.getElementById('wrChecklist');
    if (!box) return;
    box.innerHTML = (WR.checklist || []).map(x => `<li>${wrRich(x)}</li>`).join('');
}

/* ==================== 悬浮目录（左侧） ==================== */
const WR_TOC_KEY = 'wr_toc_fold';
const WR_TOC_NARROW = 1180;

function wrNavH() {
    const n = document.querySelector('.navbar');
    return n ? n.getBoundingClientRect().height : 56;
}

/** 收集目录条目：适配表 → 选句决策 → 各分区（一级）+ 各模板卡（二级） */
function wrTocItems() {
    const items = [];
    if (document.getElementById('wrFlowTitle')) items.push({ lv: 1, id: 'wrFlowTitle', text: '答题动线' });
    if (document.getElementById('wrGuideBlock')) items.push({ lv: 1, id: 'wrGuideBlock', text: '图表适配表' });
    if (document.getElementById('wrChartsTitle')) items.push({ lv: 1, id: 'wrChartsTitle', text: '真题图表' });
    if (document.getElementById('wrDecisionsTitle')) items.push({ lv: 2, id: 'wrDecisionsTitle', text: '选句决策' });
    if (document.getElementById('wrDataTitle')) items.push({ lv: 1, id: 'wrDataTitle', text: '数据描述语言工具' });
    document.querySelectorAll('#wrContent h2.wr-h2').forEach(h => {
        items.push({ lv: 1, id: h.id, text: h.textContent.trim() });
        let n = h.nextElementSibling;
        while (n && n.tagName === 'SECTION') {
            const t = n.querySelector('.wr-card-title');
            if (n.id && t) items.push({ lv: 2, id: n.id, text: t.textContent.trim() });
            n = n.nextElementSibling;
        }
    });
    if (document.getElementById('wrCheckTitle')) items.push({ lv: 1, id: 'wrCheckTitle', text: '交卷前自查表' });
    return items;
}

function wrTocBuild() {
    const list = document.getElementById('wrTocList');
    if (!list) return;
    const items = wrTocItems();
    list.innerHTML = items.map(x =>
        `<a class="lv${x.lv}" href="#${wrEsc(x.id)}" data-target="${wrEsc(x.id)}">${wrEsc(x.text)}</a>`).join('');
    wrTocApplyFold(localStorage.getItem(WR_TOC_KEY) === '1' || window.innerWidth <= WR_TOC_NARROW);
    wrTocSpy();
}

/** 滚动高亮当前所在章节 */
function wrTocSpy() {
    const list = document.getElementById('wrTocList');
    if (!list || document.body.classList.contains('wr-toc-folded') && window.innerWidth > WR_TOC_NARROW) return;
    const links = Array.prototype.slice.call(list.querySelectorAll('a[data-target]'));
    const top = wrNavH() + 24;
    let cur = null;
    for (const a of links) {
        const el = document.getElementById(a.dataset.target);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= top) cur = a; else break;
    }
    if (!cur) cur = links[0];
    links.forEach(a => a.classList.toggle('on', a === cur));
    if (cur && list.scrollHeight > list.clientHeight + 4) {
        const r = cur.getBoundingClientRect(), lr = list.getBoundingClientRect();
        if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - 24;
    }
}

function wrTocApplyFold(folded) {
    document.body.classList.toggle('wr-toc-folded', !!folded);
    try { localStorage.setItem(WR_TOC_KEY, folded ? '1' : '0'); } catch (e) { /* ignore */ }
    if (folded && !document.body.classList.contains('wr-toc-open')) wrTocClose();
}

function wrTocToggleFold() {
    wrTocApplyFold(!document.body.classList.contains('wr-toc-folded'));
}

function wrTocOpen() {
    if (window.innerWidth <= WR_TOC_NARROW) {
        document.body.classList.add('wr-toc-open');
        const m = document.getElementById('wrTocMask');
        if (m) m.hidden = false;
    } else {
        wrTocApplyFold(false);
    }
    wrTocSpy();
}

function wrTocClose() {
    document.body.classList.remove('wr-toc-open');
    const m = document.getElementById('wrTocMask');
    if (m) m.hidden = true;
}

function wrTocGo(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - wrNavH() - 12;
    window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
    try { history.replaceState(null, '', '#' + id); } catch (e) { /* ignore */ }
    if (window.innerWidth <= WR_TOC_NARROW) wrTocClose();
}

function wrTocBind() {
    const list = document.getElementById('wrTocList');
    if (!list) return;
    list.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-target]');
        if (!a) return;
        e.preventDefault();
        wrTocGo(a.dataset.target);
    });
    window.addEventListener('scroll', wrTocSpy, { passive: true });
    window.addEventListener('resize', () => {
        if (window.innerWidth > WR_TOC_NARROW) wrTocClose();
    });
    document.addEventListener('keydown', e => {
        if (e.key !== 'Escape') return;
        if (!document.getElementById('wrPop').hidden) { wrClosePhrases(); return; }
        wrTocClose();
    });
}

async function initWriting() {
    try {
        const res = await fetch('data/writing_templates.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('加载失败: ' + res.status);
        WR = await res.json();
    } catch (e) {
        document.getElementById('wrContent').innerHTML =
            `<p class="wr-loading">加载失败：${wrEsc(e.message)}</p>`;
        return;
    }
    await Promise.all([loadDict(), loadPhrases(), wrLoadSenses()]);   // 词典 + 词组表 + 本句语境义/熟词僻义
    wrMkLoad();                       // 划词高亮 + 行批注数据
    wrInitVocab();                                     // 生词本集合（弹卡按钮状态）
    // 真题套用示范（按年份汇总，可空）
    let APPLY = {};
    try {
        const ra = await fetch('data/writing_apply.json', { cache: 'no-cache' });
        if (ra.ok) APPLY = await ra.json();
    } catch (e) { APPLY = {}; }
    await loadApplyMarks();   // 套用示范的逐句标注
    const it = WR.intro || {};
    document.title = (it.title || '作文模板') + ' - 英语真题精翻';
    document.getElementById('wrTitle').textContent = it.title || '作文模板库';
    document.getElementById('wrDesc').textContent = it.desc || '';
    document.getElementById('wrRules').innerHTML = (it.rules || [])
        .map((r, i) => `<div class="wr-rule"><span class="wr-rule-no">${i + 1}</span>${wrEsc(r)}</div>`).join('');
    // 占位符图例（{{ }} 里那些英文 token 分别代表什么）
    const ph = it.placeholders || [];
    document.getElementById('wrLegend').innerHTML = ph.length ? `
        <summary class="wr-legend-head">占位符图例<span class="wr-legend-tip">模板里 <b>{{ }}</b> 包住的英文，按你的题目替换；词句本身不要动（点开查看）</span></summary>
        <div class="wr-legend-grid">${ph.map(x => `
            <div class="wr-legend-row">
                <code class="wr-legend-tok">{{${wrEsc(x[0])}}}</code>
                <span class="wr-legend-cn">${wrEsc(x[1])}</span>
                <span class="wr-legend-eg">${wrEsc(x[2] || '')}</span>
            </div>`).join('')}</div>` : '';

    // 图表适配表
    const g = WR.chart_guide || {};
    document.getElementById('wrGuideTitle').textContent = g.title || '图表适配表';
    document.getElementById('wrGuideDesc').textContent = g.desc || '';
    let lastGroup = null;
    document.querySelector('#wrChartTable tbody').innerHTML = (g.table || []).map((row, i) => {
        const ap = APPLY[row.year];
        const cell = ap
            ? `<button class="wr-exp-btn" onclick="wrToggleApply(${i})">展开示范 ▾</button>`
            : `<span class="wr-t-hint">—</span>`;
        let head = '';
        if (row.group && row.group !== lastGroup) {
            lastGroup = row.group;
            head = `<tr class="wr-group-row"><td colspan="7">${wrEsc(row.group)}</td></tr>`;
        }
        return `${head}
        <tr>
            <td class="wr-t-year">${wrEsc(row.year)}</td>
            <td>${wrEsc(row.chart)}</td>
            <td class="wr-t-num">${row.items || '—'}</td>
            <td>${wrEsc(row.trend)}</td>
            <td><span class="wr-type ${row.type === '动态' ? 'wr-type-dyn' : (row.type === '静态' ? 'wr-type-sta' : '')}">${wrEsc(row.type) || '—'}</span></td>
            <td class="wr-t-hint">${wrEsc(row.hint)}</td>
            <td class="wr-t-apply">${cell}</td>
        </tr>
        ${ap ? `<tr class="wr-apply-row" id="wrApplyRow${i}" hidden><td colspan="7">${wrApplyHtml(row.year, ap)}</td></tr>` : ''}`;
    }).join('');
    document.getElementById('wrDecisions').innerHTML = (g.decisions || []).map(d => `
        <div class="wr-decision">
            <div class="wr-decision-k">${wrEsc(d.k)}</div>
            <div class="wr-decision-v">${wrEsc(d.v)}</div>
        </div>`).join('');

    // 评分标准 / 答题动线 / 数据语言 / 自查表
    wrRenderFlow();
    wrRenderDataLang();
    wrRenderChecklist();

    // 模板分区（按 group 分组）
    wrRenderCards();
    wrTocBuild();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { wrTocBind(); wrWordBind(); wrHlBind(); initWriting(); });
} else {
    wrTocBind();
    wrWordBind();
    wrHlBind();
    initWriting();
}
