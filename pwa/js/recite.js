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
    const links = document.getElementById('rcTocList');
    if (!host || !RC) return;
    const groups = RC.groups || [];
    // 题行公共渲染（保持 .rcw-row 结构与计数不变）
    const rowHtml = (it, clickable) => {
        const tag = it.tag ? `<span class="rcw-tag">${rcEsc(it.tag)}</span>` : '';
        return `<div class="rcw-row">${rcWordSpan(it.en, clickable)}${tag}<span class="rcw-cn">${rcEsc(it.cn)}</span></div>`;
    };
    host.innerHTML = groups.map((g, gi) => {
        // 人名地名/专名组不做词典查词（词典无收录）
        const clickable = g.id !== 'name';
        let body;
        if (g.blocks && g.blocks.length) {
            // 分块组（如押题话题 26 题）：每块 = 小标题 + 高频词 chips + 该类题行
            body = g.blocks.map((b, bi) => {
                const its = (g.items || []).filter(it => it.sub === b.name);
                const rows = its.map(it => rowHtml(it, clickable)).join('');
                const hws = (b.words || []).map(w =>
                    `<span class="rc-hw word" data-w="${rcEsc(String(w.en).replace(/\([^)]*\)/g, '').trim().toLowerCase())}" data-ph="1">${rcEsc(w.en)}<span class="rc-hw-cn">${rcEsc(w.cn)}</span></span>`
                ).join('');
                return `<div class="rc-hw-block" id="rcB_${rcEsc(g.id)}_${bi}">
                    <h3 class="rc-hw-title">${rcEsc(b.name)}<span class="rc-hw-n">${its.length} 条</span></h3>
                    ${hws ? `<div class="rc-hw-words">${hws}</div>` : ''}
                    <div class="rcw-grid">${rows}</div>
                </div>`;
            }).join('');
        } else {
            const rows = (g.items || []).map(it => rowHtml(it, clickable)).join('');
            body = `<div class="rcw-grid">${rows}</div>`;
        }
        return `<section class="rc-sec rc-wg" id="rcG_${rcEsc(g.id)}">
            <h2 class="rc-h2"><span class="rc-wg-icon">${rcEsc(g.icon || '')}</span>${rcEsc(g.name)}<span class="rc-wg-n">${(g.items || []).length}</span></h2>
            <p class="rc-wg-desc">${rcEsc(g.desc || '')}</p>
            ${body}
        </section>`;
    }).join('');
    if (links) {
        links.innerHTML = groups.map(g =>
            `<a class="lv1" href="#rcG_${rcEsc(g.id)}" data-t="rcG_${rcEsc(g.id)}">${rcEsc(g.icon || '')} ${rcEsc(g.name)}</a>`
        ).join('');
    }
    const foot = document.getElementById('rcFoot');
    if (foot) {
        const n = groups.reduce((s, g) => s + (g.items || []).length, 0);
        foot.textContent = `共 ${groups.length} 类 · ${n} 条 · 数据源：押题预测 + 历年真题范文 + 押题精选PDF + 模板库`;
    }
    rcTocBuild();
}

/* ==================== 左侧悬浮目录（复用大作文页 .wr-toc 骨架） ==================== */
const RC_TOC_KEY = 'rc_toc_fold_v1';
const RC_TOC_NARROW = 1180;
let RC_LINKS = [];

function rcNavH() {
    const n = document.querySelector('.navbar');
    if (n && n.dataset.collapsed === '1') return 0;
    const h = n ? n.getBoundingClientRect().height : 56;
    return h >= 20 ? h : 56;
}

function rcTocBuild() {
    const list = document.getElementById('rcTocList');
    if (!list) return;
    document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px');
    let folded = false;
    try { folded = localStorage.getItem(RC_TOC_KEY) === '1'; } catch (e) { /* ignore */ }
    rcTocApplyFold(folded || window.innerWidth <= RC_TOC_NARROW);
    RC_LINKS = [...list.querySelectorAll('a[data-t]')];
    list.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-t]');
        if (!a) return;
        e.preventDefault();
        const el = document.getElementById(a.dataset.t);
        if (!el) return;
        const y = el.getBoundingClientRect().top + window.scrollY - rcNavH() - 12;
        window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
        if (window.innerWidth <= RC_TOC_NARROW) rcTocClose();
    });
    window.addEventListener('scroll', rcSpy, { passive: true });
    window.addEventListener('resize', () => {
        document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px');
        if (window.innerWidth > RC_TOC_NARROW) rcTocClose();
    });
    window.addEventListener('navheightchange', () => document.documentElement.style.setProperty('--nav-h', rcNavH() + 'px'));
    rcSpy();
}

/** 滚动高亮当前分类 */
function rcSpy() {
    const list = document.getElementById('rcTocList');
    if (!list || !RC_LINKS.length) return;
    if (document.body.classList.contains('wr-toc-folded') && window.innerWidth > RC_TOC_NARROW) return;
    const top = rcNavH() + 24;
    let cur = RC_LINKS[0];
    for (const a of RC_LINKS) {
        const el = document.getElementById(a.dataset.t);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= top) cur = a; else break;
    }
    RC_LINKS.forEach(a => a.classList.toggle('on', a === cur));
    if (cur && list.scrollHeight > list.clientHeight + 4) {
        const r = cur.getBoundingClientRect(), lr = list.getBoundingClientRect();
        if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - 24;
    }
}

function rcTocApplyFold(folded) {
    document.body.classList.toggle('wr-toc-folded', !!folded);
    try { localStorage.setItem(RC_TOC_KEY, folded ? '1' : '0'); } catch (e) { /* ignore */ }
    if (folded && !document.body.classList.contains('wr-toc-open')) rcTocClose();
}
function rcTocToggleFold() { rcTocApplyFold(!document.body.classList.contains('wr-toc-folded')); }
function rcTocOpen() {
    if (window.innerWidth <= RC_TOC_NARROW) {
        document.body.classList.add('wr-toc-open');
        const m = document.getElementById('rcTocMask');
        if (m) m.hidden = false;
    } else {
        rcTocApplyFold(false);
    }
    rcSpy();
}
function rcTocClose() {
    document.body.classList.remove('wr-toc-open');
    const m = document.getElementById('rcTocMask');
    if (m) m.hidden = true;
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
    if (typeof wrCancelPopTimers === 'function') wrCancelPopTimers();   // 先撤掉待弹计时，别把词卡顶掉
    if (typeof wrCloseUpgPop === 'function') wrCloseUpgPop();
    if (typeof wrSwClose === 'function') wrSwClose();
    if (typeof wrTopicClose === 'function') wrTopicClose();
    rcPopEl = document.createElement('div');
    rcPopEl.className = 'word-pop wr-pop-c';
    rcPopEl.innerHTML = html;
    document.body.appendChild(rcPopEl);
    // 统一贴词定位（与写作/押题/小作文同一套）：紧贴被点的词
    if (typeof popNear === 'function') popNear(targetEl, rcPopEl, 6);
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
    rcAnnoBind();
    document.addEventListener('keydown', e => { if (e.key === 'Escape') rcTocClose(); });
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
