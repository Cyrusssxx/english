/* 小作文（英语二 A 节 · 应用文）功能句库
   数据：pwa/data/small_writing.json（tools/build_small_writing.py 生成）
   两种视图：按段落（第一/二/三段） · 按信件类型（建议/邀请/道歉/祝贺/介绍/通知）
   正文可划词高亮 + 行批注（浮条交互，模块与作文页同源，见文件末尾） */
let SW = null;                 // 数据
let swView = 'part';           // part | type
const SW_VIEW_KEY = 'sw_view_v1';

function swEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 先把 {{token}} 抽出来做成占位符芯片，再转义其余文本 */
function swPh(s) {
    return String(s == null ? '' : s).split(/(\{\{[^}]+\}\})/g).map(seg => {
        const m = /^\{\{([^}]+)\}\}$/.exec(seg);
        return m ? '<span class="sw-ph">{{' + swEsc(m[1]) + '}}</span>' : swEsc(seg);
    }).join('');
}

function swBank(id) { return (SW.banks || []).find(b => b.id === id); }

/* 高亮块编号：与「视图」无关的稳定索引（key = 组id#序号），
   否则切「按段落 / 按类型」时 DOM 顺序变了、高亮会跳到别的句子上 */
const swKeyMap = new Map();
let swKeyNext = 0;

function swKeyIdxOf(key) {
    if (!swKeyMap.has(key)) swKeyMap.set(key, swKeyNext++);
    return swKeyMap.get(key);
}

function swBuildKeyMap() {
    swKeyMap.clear();
    swKeyNext = 0;
    (SW.banks || []).forEach(b => (b.items || []).forEach((_, i) => swKeyIdxOf(b.id + '#' + i)));
    ['note1', 'note2', 'note3', 'noteType'].forEach(swKeyIdxOf);
}

/* ---------- 渲染 ---------- */

function swLine(it, no, key) {
    const ex = (it.ex || []).map(e => `
        <div class="sw-ex">
            <div class="sw-ex-tag">✍ 真题示例${e.src ? ' · ' + swEsc(e.src) : ''}</div>
            <div class="sw-ex-en">${swPh(e.en)}</div>
            ${e.cn ? `<div class="sw-ex-cn">${swPh(e.cn)}</div>` : ''}
        </div>`).join('');
    return `<li class="sw-line" data-k="${key}">
        <div class="sw-en"><span class="sw-no">${no}</span><span class="sw-en-txt">${swPh(it.en)}</span></div>
        ${it.cn ? `<div class="sw-cn">${swPh(it.cn)}</div>` : ''}
        ${ex}
    </li>`;
}

function swCard(bank, order) {
    const n = bank.items.length;
    const opened = n <= 14;
    return `<details class="sw-card"${opened ? ' open' : ''} data-bank="${swEsc(bank.id)}">
        <summary class="sw-card-head">
            <span class="sw-card-title">${order ? `<span class="sw-ord">${order}</span>` : ''}${swEsc(bank.label)}</span>
            <span class="sw-card-n">${n} 句</span>
            <button type="button" class="sw-copy" data-copy="${swEsc(bank.id)}" title="复制这一组句子">复制</button>
        </summary>
        <ol class="sw-list">${bank.items.map((it, i) => swLine(it, i + 1, bank.id + '#' + i)).join('')}</ol>
    </details>`;
}

function swPartNote(part) {
    const ns = (SW.notes || []).filter(n => n.part === part).map(n => n.text);
    return ns.length ? `<div class="sw-note" data-k="note${part}">💡 ${ns.map(swEsc).join('<br>')}</div>` : '';
}

function swRender() {
    const box = document.getElementById('swContent');
    if (!box || !SW) return;
    let html = '';
    if (swView === 'part') {
        const heads = { 1: '第一段 · 开头（问候 + 来意）', 2: '第二段 · 主体（展开内容）', 3: '第三段 · 收尾（客套 / 期待回复）' };
        [1, 2, 3].forEach(p => {
            const bs = SW.banks.filter(b => b.part === p);
            if (!bs.length) return;
            html += `<section class="sw-part"><h2 class="sw-h2">${heads[p]}</h2>`
                + swPartNote(p) + bs.map(b => swCard(b)).join('') + '</section>';
        });
    } else {
        html += `<div class="sw-note" data-k="noteType">💡 小作文第二段极其灵活：可以<b>跨类型混搭</b>——比如从「建议类」挑 2 句、从「祝贺类」挑 1 句。下面每一类按<b>拼装顺序</b>排好了（首句 / 来意 / 通用首句 → 该类型二三四句 → 收尾），照着从上往下挑 2~4 句即可。</div>`;
        SW.types.forEach(t => {
            const bs = (t.banks || []).map(swBank).filter(Boolean);
            if (!bs.length) return;
            html += `<section class="sw-part"><h2 class="sw-h2">${swEsc(t.name)}</h2>
                <div class="sw-path">${bs.map(b => `<span class="sw-path-node">${swEsc(b.label.replace('第一段 · ', '').replace('第二段 · ', '').replace('第三段 · ', ''))}</span>`).join('<span class="sw-path-arrow">→</span>')}</div>
                ${bs.map(b => swCard(b, b.id === 'p1s1' || b.id === 'p2s1' || b.id === 'p3' ? '共用' : '本类')).join('')}</section>`;
        });
    }
    box.innerHTML = html;
    swRestoreAll();
    swSyncOpenBtn();
}

function swExpandAll(on) {
    document.querySelectorAll('#swContent details.sw-card').forEach(d => { d.open = !!on; });
    swSyncOpenBtn();
}

function swSyncOpenBtn() {
    const all = [...document.querySelectorAll('#swContent details.sw-card')];
    const b = document.getElementById('swExpandBtn');
    if (!b) return;
    const allOpen = all.length && all.every(d => d.open);
    b.textContent = allOpen ? '收起全部' : '展开全部';
}

/* ---------- 初始化 ---------- */

function swRenderLegend() {
    const ph = (SW.placeholders || []);
    const box = document.getElementById('swLegend');
    if (!box) return;
    box.innerHTML = `
        <summary class="wr-legend-head">占位符图例<span class="wr-legend-tip">模板里 <b>{{ }}</b> 包住的英文，按你的题目替换；词句本身不要动（共 ${ph.length} 个 · 点开查看）</span></summary>
        <div class="wr-legend-grid">${ph.map(x => `
            <div class="wr-legend-row">
                <code class="wr-legend-tok">{{${swEsc(x[0])}}}</code>
                <span class="wr-legend-cn">${swEsc(x[1])}</span>
            </div>`).join('')}</div>`;
}

function swRenderSteps() {
    const box = document.getElementById('swSteps');
    if (!box) return;
    box.innerHTML = (SW.steps || []).map(s => `
        <div class="sw-step">
            <div class="sw-step-no">${s.no}</div>
            <div class="sw-step-body"><b>${s.name}</b>${s.body}</div>
        </div>`).join('');
}

function swSyncViewBtns() {
    document.querySelectorAll('.sw-vbtn').forEach(b => b.classList.toggle('on', b.dataset.view === swView));
}

function swBind() {
    document.querySelectorAll('.sw-vbtn').forEach(b => {
        b.addEventListener('click', () => {
            swView = b.dataset.view;
            try { localStorage.setItem(SW_VIEW_KEY, swView); } catch (e) { /* ignore */ }
            swSyncViewBtns();
            swRender();
        });
    });
    const eb = document.getElementById('swExpandBtn');
    if (eb) eb.addEventListener('click', () => {
        const all = [...document.querySelectorAll('#swContent details.sw-card')];
        swExpandAll(!(all.length && all.every(d => d.open)));
    });
    document.addEventListener('click', e => {
        const c = e.target.closest ? e.target.closest('.sw-copy') : null;
        if (!c) return;
        e.preventDefault();
        e.stopPropagation();
        const b = swBank(c.dataset.copy);
        if (!b) return;
        const txt = b.items.map((it, i) => (i + 1) + '. ' + it.en).join('\n');
        const done = () => { c.textContent = '已复制'; setTimeout(() => { c.textContent = '复制'; }, 1200); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(txt).then(done, done);
        } else {
            const ta = document.createElement('textarea');
            ta.value = txt; document.body.appendChild(ta); ta.select();
            try { document.execCommand('copy'); } catch (err) { /* ignore */ }
            ta.remove(); done();
        }
    });
}

async function swInit() {
    const box = document.getElementById('swContent');
    try {
        const res = await fetch('data/small_writing.json', { cache: 'no-cache' });
        SW = await res.json();
    } catch (e) {
        if (box) box.innerHTML = '<p style="color:var(--text-light)">数据加载失败，请刷新重试</p>';
        return;
    }
    const m = SW.meta || {};
    const t = document.getElementById('swTitle');
    if (t && m.title) t.textContent = '📝 ' + m.title;
    const d = document.getElementById('swDesc');
    if (d) d.innerHTML = swEsc(m.desc || '');
    document.title = (m.title || '小作文') + ' - 英语真题精翻';
    try { swView = localStorage.getItem(SW_VIEW_KEY) || 'part'; } catch (e) { swView = 'part'; }
    if (swView !== 'type') swView = 'part';
    swBuildKeyMap();
    swRenderLegend();
    swRenderSteps();
    swSyncViewBtns();
    swRender();
    swBind();
    const st = document.getElementById('swStudy');
    if (st && SW.study) st.innerHTML = '📌 <b>怎么用</b>：' + swEsc(SW.study);
    const n = document.getElementById('swMkCount');
    if (n) n.textContent = String(swMarks.length);
    swHlBind();
    swNavHVar();
    window.addEventListener('resize', swNavHVar);
}

/* ==================== 正文划词高亮 + 行批注（浮条交互，照搬 408 notes 页） ==================== */
const SW_MK_KEY = 'sw_mk_v1';
const SW_ANNO_KEY = 'sw_anno_v1';
const SW_HL_COLORS = ['yellow', 'green', 'blue', 'pink'];
const SW_HL_CN = { yellow: '黄色', green: '绿色', blue: '蓝色', pink: '粉色' };
const SW_MK_SEL = '.sw-line, .sw-note';
let swMarks = [];        // 高亮 [{ c: 正文块序号, s: 起, e: 止, k: 颜色名 }]
let swAnnos = {};        // 行批注 { 正文块序号: 文本 }
let swHlBar = null;      // 划词浮条
let swHlTimer = null;

function swMkLoad() {
    try { swMarks = JSON.parse(localStorage.getItem(SW_MK_KEY) || '[]') || []; }
    catch (e) { swMarks = []; }
    if (!Array.isArray(swMarks)) swMarks = [];
    const LEGACY = { y: 'yellow', g: 'green', b: 'blue', p: 'pink' };
    swMarks = swMarks.filter(m => m && typeof m.c === 'number')
        .map(m => ({ c: m.c, s: m.s, e: m.e, k: SW_HL_COLORS.includes(m.k) ? m.k : (LEGACY[m.k] || 'yellow') }));
    try { swAnnos = JSON.parse(localStorage.getItem(SW_ANNO_KEY) || '{}') || {}; }
    catch (e) { swAnnos = {}; }
    if (!swAnnos || typeof swAnnos !== 'object' || Array.isArray(swAnnos)) swAnnos = {};
}

function swMkSave() {
    try { localStorage.setItem(SW_MK_KEY, JSON.stringify(swMarks)); } catch (e) { /* ignore */ }
    const c = document.getElementById('swMkCount');
    if (c) c.textContent = String(swMarks.length);
    const b = document.getElementById('swMkClearBtn');
    if (b) b.hidden = !swMarks.length;
}

function swAnnoSave() {
    try { localStorage.setItem(SW_ANNO_KEY, JSON.stringify(swAnnos)); } catch (e) { /* ignore */ }
}

/** 可高亮正文块：一次 DFS 收集（命中即收、不再下钻，天然去掉嵌套），按文档序编号 data-mk */
function swMkBlocks() {
    const out = [];
    (function walk(node) {
        for (const el of node.children) {
            if (el.matches(SW_MK_SEL)) { out.push(el); continue; }
            walk(el);
        }
    })(document.body);
    for (const el of out) {
        const k = (el.dataset && el.dataset.k) || null;
        el.setAttribute('data-mk', String(k ? swKeyIdxOf(k) : swKeyNext++));
    }
    return out;
}

function swMkBlockOf(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return (el && el.closest) ? el.closest('[data-mk]') : null;
}

function swInAnno(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return !!(el && el.closest && el.closest('.wr-anno, .hl-toolbar'));
}

/** 块内全部 Text 节点 → [{node, start, len}]（按文档序，start = 块内字符偏移） */
function swMkTexts(el) {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const out = []; let acc = 0;
    while (tw.nextNode()) {
        const n = tw.currentNode;
        out.push({ node: n, start: acc, len: n.data.length });
        acc += n.data.length;
    }
    return out;
}

function swMkOffset(texts, node, off) {
    for (const t of texts) if (t.node === node) return t.start + off;
    return null;
}

function swMkAt(texts, off) {
    for (const t of texts) {
        if (off <= t.start + t.len) return { node: t.node, off: off - t.start };
    }
    const last = texts[texts.length - 1];
    return last ? { node: last.node, off: last.len } : null;
}

function swMkRange(el, s, e) {
    const texts = swMkTexts(el);
    const a = swMkAt(texts, s), b = swMkAt(texts, e);
    if (!a || !b) return null;
    if (a.node === b.node && a.off === b.off) return null;
    const r = document.createRange();
    r.setStart(a.node, a.off);
    r.setEnd(b.node, b.off);
    return r;
}

/** 当前选区 → { block, i, s, e }；失败时返回 { err } */
function swMkSelInfo() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return { err: 'none' };
    const r = sel.getRangeAt(0);
    const b1 = swMkBlockOf(r.startContainer), b2 = swMkBlockOf(r.endContainer);
    if (!b1 || !b2 || b1 !== b2) return { err: 'none' };
    const texts = swMkTexts(b1);
    const s = swMkOffset(texts, r.startContainer, r.startOffset);
    const e = swMkOffset(texts, r.endContainer, r.endOffset);
    if (s == null || e == null || e <= s) return { err: 'none' };
    return { block: b1, i: parseInt(b1.getAttribute('data-mk'), 10), s, e, range: r };
}

function swMkUnwrap(mk) {
    const f = document.createDocumentFragment();
    while (mk.firstChild) f.appendChild(mk.firstChild);
    if (mk.parentNode) mk.replaceWith(f);
}

/** 重建单个块内的高亮 */
function swMkPaint(block, i) {
    block.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    swMarks.filter(m => m.c === i).sort((a, b) => a.s - b.s).forEach(m => {
        const r = swMkRange(block, m.s, m.e);
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
function swRestoreAll() {
    document.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    document.querySelectorAll('.wr-anno').forEach(x => x.remove());
    const blocks = swMkBlocks();
    const dirty = {};
    swMarks.forEach(m => { dirty[m.c] = 1; });
    blocks.forEach(b => {
        const i = parseInt(b.getAttribute('data-mk'), 10);
        if (dirty[i]) swMkPaint(b, i);
    });
    const byIdx = {};
    blocks.forEach(b => { byIdx[b.getAttribute('data-mk')] = b; });
    Object.keys(swAnnos).forEach(k => {
        if (swAnnos[k] && byIdx[k]) swAnnoRender(parseInt(k, 10), byIdx[k], swAnnos[k]);
    });
    swMkSave();
}

/* ---------- 上色 / 取消 ---------- */

function swHlApply(color) {
    const sr = swMkSelInfo();
    if (sr.err) { swHlBarHide(); return; }
    swMarks = swMarks.filter(m => !(m.c === sr.i && m.s < sr.e && sr.s < m.e));   // 重叠的先去掉
    swMarks.push({ c: sr.i, s: sr.s, e: sr.e, k: color });
    swRestoreAll();   // 同一句可能在多处渲染（按类型视图的共用卡），整页重绘保证一致
    swMkSave();
    swHideHlToolbar();
    const s = window.getSelection(); if (s) s.removeAllRanges();
}

/** 取消选区起点所在那处高亮 */
function swHlCancelAt(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    const mk = (el && el.closest) ? el.closest('mark.note-hl') : null;
    if (!mk) return false;
    swHlRemoveMark(mk);
    return true;
}

function swHlRemoveMark(mk) {
    const block = mk.closest('[data-mk]');
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    const s = parseInt(mk.dataset.start, 10);
    const k = mk.dataset.color;
    swMarks = swMarks.filter(m => !(m.c === i && m.s === s && m.k === k));
    swRestoreAll();   // 同上：整页重绘
    swMkSave();
}

async function swMkClearAll() {
    if (!swMarks.length) return;
    if (typeof confirmAsync === 'function' && !(await confirmAsync('清除本页全部划词高亮？', { danger: true }))) return;
    swMarks = [];
    try { localStorage.removeItem(SW_MK_KEY); } catch (e) { /* ignore */ }
    document.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    swMkSave();
}

/* ---------- 划词浮条（408 同款：4 色 + 📝批注 + ✕） ---------- */

function swHideHlToolbar() { if (swHlBar) { swHlBar.remove(); swHlBar = null; } }

/** 取选区位置：优先 Range 自带 rect，取不到（如 jsdom / 空选区）就退回起点元素 */
function swRectOf(range) {
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
function swHlBarPlace(bar, rect) {
    const bh = bar.offsetHeight, bw = bar.offsetWidth;
    const navH = swNavH();
    let top = window.scrollY + rect.top - bh - 8;
    if (rect.top - bh - 8 < navH + 6) top = window.scrollY + rect.bottom + 8;
    let left = window.scrollX + rect.left;
    const maxLeft = window.scrollX + document.documentElement.clientWidth - bw - 8;
    if (left > maxLeft) left = Math.max(window.scrollX + 8, maxLeft);
    bar.style.top = top + 'px';
    bar.style.left = left + 'px';
}

function swHlShowForSelection() {
    if (swHlBar && swHlBar.classList.contains('hl-cancel-only')) return;   // 别把「取消高亮」条顶掉
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { swHideHlToolbar(); return; }
    const r = sel.getRangeAt(0);
    if (swInAnno(r.startContainer) || swInAnno(r.endContainer)) { swHideHlToolbar(); return; }
    const sr = swMkSelInfo();
    if (sr.err) { swHideHlToolbar(); return; }
    swHideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar';
    bar.innerHTML = SW_HL_COLORS.map(c =>
        '<span class="hl-dot hl-dot-' + c + '" data-color="' + c + '" title="' + SW_HL_CN[c] + '高亮"></span>').join('') +
        '<span class="hl-anno-btn" title="为这一行写批注">📝批注</span>' +
        '<span class="hl-cancel" title="取消这处高亮">✕</span>';
    document.body.appendChild(bar);
    swHlBar = bar;
    swHlBarPlace(bar, swRectOf(r));
    bar.addEventListener('mousedown', e => e.preventDefault());   // 按住不丢选区
    bar.querySelectorAll('.hl-dot').forEach(dot =>
        dot.addEventListener('click', () => swHlApply(dot.dataset.color)));
    bar.querySelector('.hl-anno-btn').addEventListener('click', () => swAnnoOpenFrom(r));
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        swHlCancelAt(r.startContainer);
        swHideHlToolbar();
    });
}

/** 点已有高亮 → 只显示「✕ 取消高亮」 */
function swHlShowCancelFor(mk) {
    clearTimeout(swHlTimer);
    swHideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar hl-cancel-only';
    bar.innerHTML = '<span class="hl-cancel" title="取消高亮">✕ 取消高亮</span>';
    document.body.appendChild(bar);
    swHlBar = bar;
    swHlBarPlace(bar, mk.getBoundingClientRect());
    bar.addEventListener('mousedown', e => e.preventDefault());
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        swHlRemoveMark(mk);
        swHideHlToolbar();
    });
}

function swHlBind() {
    document.addEventListener('mouseup', () => {
        clearTimeout(swHlTimer);
        swHlTimer = setTimeout(swHlShowForSelection, 0);
    });
    document.addEventListener('mousedown', e => {
        if (swHlBar && !swHlBar.contains(e.target)) swHideHlToolbar();
    });
    document.addEventListener('click', e => {
        if (swInAnno(e.target)) return;
        const mk = e.target.closest ? e.target.closest('mark.note-hl') : null;
        if (mk) { e.stopPropagation(); swHlShowCancelFor(mk); }
    });
    window.addEventListener('scroll', () => { if (swHlBar) swHideHlToolbar(); }, { passive: true });
}

/* ---------- 行批注（点 📝批注：在该行正下方开编辑框，自动保存） ---------- */

/** 批注框挂到"行级"元素之后（避免插进 flex 行/表格单元格里破坏布局） */
function swAnnoAnchor(block) {
    return block;
}

function swAnnoRender(i, block, text) {
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
        if (v) swAnnos[i] = v; else delete swAnnos[i];
        swAnnoSave();
    };
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(commit, 600); });
    ta.addEventListener('blur', () => { clearTimeout(timer); commit(); });
    box.querySelector('.wr-anno-del').addEventListener('click', () => {
        delete swAnnos[i];
        swAnnoSave();
        box.remove();
    });
    swAnnoAnchor(block).insertAdjacentElement('afterend', box);
    return box;
}

function swAnnoOpenFrom(range) {
    const block = swMkBlockOf(range.startContainer);
    const sel = window.getSelection(); if (sel) sel.removeAllRanges();
    swHideHlToolbar();
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    let box = document.querySelector('.wr-anno[data-anno="' + i + '"]');
    if (!box) box = swAnnoRender(i, block, swAnnos[i] || '');
    if (box.scrollIntoView) box.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    const ta = box.querySelector('textarea');
    if (ta) ta.focus();
}


function swNavH() {
    const n = document.querySelector('.navbar');
    return n ? n.getBoundingClientRect().height : 56;
}

/** 顶栏实测高度写进 --nav-h（吸顶的视图切换条用它做 top） */
function swNavHVar() {
    const h = swNavH();
    document.documentElement.style.setProperty('--nav-h', (h < 20 ? 56 : h) + 'px');
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', swInit);
else swInit();

