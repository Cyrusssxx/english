/* 写作词库速查页：加载 data/writing_words.json，渲染分类词条 + 目录折叠/高亮。
   英文词条可点查词（复用 dict.js 的词典/词组 + writing_senses + wordnotes）。
   旧的作文速记（骨架/句池/30天计划/划词高亮）已全部移除——功能并入大/小作文页。 */
let RC = null;

function rcEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 夜间模式（本页不依赖 common.js，自带一份最小实现） */
function toggleDark() {
    const on = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', on);
    try { localStorage.setItem('darkMode', on ? '1' : '0'); } catch (e) { /* ignore */ }
    const s = document.getElementById('darkState');
    if (s) s.textContent = on ? '开' : '关';
}

/* ==================== 词条渲染 ==================== */
/** 英文短语：整组做成可点词条；组内的实词也能点换查（复用 .word）。
    clickable=false 用于人名地名/专名（词典无释义，本身已有中文对照）。 */
function rcWordSpan(text, clickable) {
    if (clickable === false) return `<span class="rcw rcw-plain">${rcEsc(text)}</span>`;
    // key 去掉括号注释（如 artificial intelligence (AI) → 主体词组），显示保留原文
    const key = String(text).replace(/\([^)]*\)/g, '').trim().toLowerCase();
    return `<span class="rcw word" data-w="${rcEsc(key)}" data-ph="1">${rcEsc(text)}</span>`;
}

function rcRender() {
    const host = document.getElementById('rcGroups');
    const links = document.getElementById('rcDirLinks');
    if (!host || !RC) return;
    const groups = RC.groups || [];
    host.innerHTML = groups.map((g, gi) => {
        const rows = (g.items || []).map(it => {
            const tag = it.tag ? `<span class="rcw-tag">${rcEsc(it.tag)}</span>` : '';
            // 人名地名/专名组不做词典查词（词典无收录）
            const clickable = g.id !== 'name';
            return `<div class="rcw-row">${rcWordSpan(it.en, clickable)}${tag}<span class="rcw-cn">${rcEsc(it.cn)}</span></div>`;
        }).join('');
        return `<section class="rc-sec rc-wg" id="rcG_${rcEsc(g.id)}">
            <h2 class="rc-h2"><span class="rc-wg-icon">${rcEsc(g.icon || '')}</span>${rcEsc(g.name)}<span class="rc-wg-n">${(g.items || []).length}</span></h2>
            <p class="rc-wg-desc">${rcEsc(g.desc || '')}</p>
            <div class="rcw-grid">${rows}</div>
        </section>`;
    }).join('');
    if (links) {
        links.innerHTML = groups.map(g =>
            `<a href="#rcG_${rcEsc(g.id)}" data-t="rcG_${rcEsc(g.id)}">${rcEsc(g.icon || '')} ${rcEsc(g.name)}</a>`
        ).join('');
    }
    const foot = document.getElementById('rcFoot');
    if (foot) {
        const n = groups.reduce((s, g) => s + (g.items || []).length, 0);
        foot.textContent = `共 ${groups.length} 类 · ${n} 条 · 数据源：押题预测 + 历年真题范文 + 模板库`;
    }
    rcTocBind();
}

/* ==================== 目录：点击跳转 + 滚动高亮 ==================== */
let RC_LINKS = [];
function rcNavH() {
    const n = document.querySelector('.navbar');
    if (n && n.dataset.collapsed === '1') return 0;
    const h = n ? n.getBoundingClientRect().height : 56;
    return h >= 20 ? h : 56;
}
function rcTocBind() {
    const toc = document.getElementById('rcDirLinks');
    if (!toc) return;
    document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px');
    window.addEventListener('resize', () => document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px'));
    window.addEventListener('navheightchange', () => document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px'));
    toc.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-t]');
        if (!a) return;
        e.preventDefault();
        const el = document.getElementById(a.dataset.t);
        if (!el) return;
        const y = el.getBoundingClientRect().top + window.scrollY - rcNavH() - 70;
        window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
    });
    RC_LINKS = [...toc.querySelectorAll('a[data-t]')];
    window.addEventListener('scroll', rcSpy, { passive: true });
    rcSpy();
}
function rcSpy() {
    if (!RC_LINKS.length) return;
    const top = rcNavH() + 90;
    let cur = RC_LINKS[0];
    RC_LINKS.forEach(a => {
        const el = document.getElementById(a.dataset.t);
        if (el && el.getBoundingClientRect().top <= top) cur = a;
    });
    RC_LINKS.forEach(a => a.classList.toggle('on', a === cur));
}

/* ==================== 目录折叠：记住用户选择 ==================== */
const RC_DIR_KEY = 'rc_dir_open_v1';
function rcDirBind() {
    const d = document.getElementById('rcDir');
    if (!d) return;
    let saved = null;
    try { saved = localStorage.getItem(RC_DIR_KEY); } catch (e) { /* ignore */ }
    if (saved === '0') d.open = false;
    d.addEventListener('toggle', () => {
        try { localStorage.setItem(RC_DIR_KEY, d.open ? '1' : '0'); } catch (e) { /* ignore */ }
    });
}

/* ==================== 查词弹卡（复用 writing/recite 的 .word-pop） ==================== */
let rcPopEl = null;
let RC_SENSES = null;   // { word: [本句义, 说明, U/C] }
let RC_WN = null;       // { word: wordnotes 行 }

const RC_STOP = new Set(('a an the and or of in on to from with by as at for while that this these those it its is are was were be been being ' +
    'their they them we our you your him her his not no nor but so if then than when which who whom whose what where how ' +
    'will would can could shall should may might must do does did have has had more most less least very just only also too ' +
    'there here such own one two three over under between among about against during through across after before because ' +
    'although though since until unless whether either neither both each every any some all').split(' '));

async function rcLoadSense() {
    const grab = u => fetch(u).then(r => (r.ok ? r.json() : null)).catch(() => null);
    try {
        const [s, w] = await Promise.all([grab('data/writing_senses.json'), grab('data/wordnotes.json')]);
        RC_SENSES = (s && s.words) || {};
        RC_WN = {};
        (((w && w.rows) || [])).forEach(r => { if (r && r.w) RC_WN[String(r.w).toLowerCase()] = r; });
    } catch (e) { RC_SENSES = RC_SENSES || {}; RC_WN = RC_WN || {}; }
}

function rcWordKeys(key, base) {
    const out = [];
    const push = x => { x = String(x || '').toLowerCase().trim(); if (x && !out.includes(x)) out.push(x); };
    push(key); push(base);
    [key, base].forEach(w => {
        if (/ies$/.test(w)) push(w.slice(0, -3) + 'y');
        if (/es$/.test(w)) push(w.slice(0, -2));
        if (/s$/.test(w) && !/ss$/.test(w)) push(w.slice(0, -1));
        push(w + 's'); push(w + 'es');
        if (/y$/.test(w)) push(w.slice(0, -1) + 'ies');
        if (typeof stemCandidates === 'function') stemCandidates(w).forEach(push);
    });
    return out;
}

function rcOpenPop(targetEl, html) {
    rcClosePop();
    rcPopEl = document.createElement('div');
    rcPopEl.className = 'word-pop wr-pop-c';
    rcPopEl.innerHTML = html;
    document.body.appendChild(rcPopEl);
    const r = targetEl.getBoundingClientRect();
    const pw = rcPopEl.offsetWidth, ph = rcPopEl.offsetHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    let top = r.bottom + window.scrollY + 6;
    if (top + ph > window.scrollY + document.documentElement.clientHeight - 12) {
        top = Math.max(window.scrollY + 6, r.top + window.scrollY - ph - 6);
    }
    rcPopEl.style.left = left + 'px';
    rcPopEl.style.top = top + 'px';
}
function rcClosePop() {
    if (rcPopEl) { rcPopEl.remove(); rcPopEl = null; }
}

/** 词卡：词组整组释义（组成词可点换查）→ 词典 → 熟词僻义 */
function rcWordPop(el) {
    const key = el.getAttribute('data-w') || '';
    const isPhrase = el.getAttribute('data-ph') === '1';
    const base = (typeof normWord === 'function') ? normWord(key) : String(key).toLowerCase();
    const pick = map => {
        if (!map) return null;
        for (const c of rcWordKeys(key, base)) { if (map[c]) return map[c]; }
        return null;
    };
    const wn = pick(RC_WN);
    let html = '';
    if (isPhrase) {
        const meaning = (typeof phraseLookup === 'function') ? phraseLookup(key) : null;
        if (meaning) {
            html += `<div class="wp-phrase">${rcEsc(key)}</div><div class="wp-meaning">${rcEsc(meaning)}</div>`;
            html += key.split(/\s+/).filter(w => !RC_STOP.has(w.replace(/[^a-z]/gi, '').toLowerCase())).slice(0, 5).map(w => {
                const cw = w.replace(/[^A-Za-z'-]/g, '');
                const entry = (typeof dictLookup === 'function') ? dictLookup(cw.toLowerCase()) : null;
                return `<div class="wpw"><span class="wpw-word word" data-w="${rcEsc(cw.toLowerCase())}">${rcEsc(cw)}</span>` +
                    (entry ? `<span class="wpw-mean">${rcEsc(entry.t)}</span>` : `<span class="wpw-mean wpw-none">（离线无释义）</span>`) + `</div>`;
            }).join('');
        } else {
            // 词组词典没收录：逐词给释义
            html += `<div class="wp-phrase">${rcEsc(key)}</div>`;
            html += key.split(/\s+/).filter(w => !RC_STOP.has(w.replace(/[^a-z]/gi, '').toLowerCase())).slice(0, 6).map(w => {
                const cw = w.replace(/[^A-Za-z'-]/g, '');
                const entry = (typeof dictLookup === 'function') ? dictLookup(cw.toLowerCase()) : null;
                return `<div class="wpw"><span class="wpw-word">${rcEsc(cw)}</span>` +
                    (entry ? `<span class="wpw-mean">${rcEsc(entry.t)}</span>` : `<span class="wpw-mean wpw-none">—</span>`) + `</div>`;
            }).join('');
        }
    } else {
        const entry = (typeof dictLookup === 'function') ? dictLookup(key) : null;
        html += `<span class="wp-word">${rcEsc(key)}</span><span class="wp-phonetic">${rcEsc(entry ? entry.p || '' : '')}</span>` +
            `<div class="wp-meaning">${entry ? rcEsc(entry.t) : '（无离线释义）'}</div>`;
    }
    if (wn) {
        html += `<div class="wp-wn"><div class="wp-wn-t">⚡ 熟词僻义`
            + (wn.tier ? `<span class="wp-wn-tier">${rcEsc(wn.tier)}频</span>` : '') + `</div>`
            + `<div class="wp-wn-row"><b>熟义</b>${rcEsc(wn.common || '')}</div>`
            + `<div class="wp-wn-row"><b>僻义</b>${rcEsc(wn.uncommon || '')}</div>`
            + (wn.src ? `<div class="wp-wn-src">${rcEsc(wn.src)}</div>` : '') + `</div>`;
    }
    rcOpenPop(el, html);
}

function rcAnnoBind() {
    document.addEventListener('click', e => {
        const w = e.target.closest && e.target.closest('.word');
        if (w) { e.stopPropagation(); rcWordPop(w); return; }
        if (!e.target.closest || !e.target.closest('.wr-pop-c')) rcClosePop();
    }, true);
}

/* ==================== 启动 ==================== */
async function rcInit() {
    rcDirBind();
    rcAnnoBind();
    const s = document.getElementById('darkState');
    if (s && document.documentElement.classList.contains('dark')) s.textContent = '开';
    try {
        const res = await fetch('data/writing_words.json');
        if (!res.ok) throw new Error('HTTP ' + res.status);
        RC = await res.json();
    } catch (e) {
        const h = document.getElementById('rcGroups');
        if (h) h.innerHTML = '<p class="rc-desc">词库加载失败，请刷新重试。</p>';
        return;
    }
    rcRender();
    Promise.all([loadDict(), rcLoadSense()]).catch(() => {});
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', rcInit);
else rcInit();
