/* 英语二精翻 - 前端通用JS：夜间模式 + 今日学习计时器（改自 408 刷题 common.js） */

// ============ 夜间模式：尽早给 <html> 加 .dark，减少闪白 ============
function isDarkOn() {
    return localStorage.getItem('darkMode') === '1';
}

function applyDark() {
    document.documentElement.classList.toggle('dark', isDarkOn());
}

applyDark();

function renderDarkSwitch() {
    const btn = document.getElementById('darkSwitch');
    const state = document.getElementById('darkState');
    if (!btn || !state) return;
    const on = isDarkOn();
    btn.classList.toggle('on', on);
    state.textContent = on ? '开' : '关';
}

function toggleDark() {
    localStorage.setItem('darkMode', isDarkOn() ? '0' : '1');
    applyDark();
    renderDarkSwitch();
}

renderDarkSwitch();

// ============ 今日学习计时器（按天累计，存localStorage，页面不可见时暂停） ============
// 支持手动「暂停/继续」与「重置」：按钮 id 为 timerPause / timerReset（各页可选），
// 暂停状态存 localStorage.studyTimerPaused（'1'=暂停），刷新/换页后保持。
(function () {
    const el = document.getElementById('navTimer');
    if (!el) return;

    const today = new Date().toISOString().slice(0, 10);
    if (localStorage.getItem('studyTimerDate') !== today) {
        localStorage.setItem('studyTimerDate', today);
        localStorage.setItem('studyTimerSec', '0');
        localStorage.setItem('studyTimerPaused', '0');
    }

    function isPaused() {
        return localStorage.getItem('studyTimerPaused') === '1';
    }

    function fmt(sec) {
        const h = String(Math.floor(sec / 3600)).padStart(2, '0');
        const m = String(Math.floor(sec % 3600 / 60)).padStart(2, '0');
        const s = String(sec % 60).padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function renderPauseBtn() {
        const pb = document.getElementById('timerPause');
        if (!pb) return;
        const on = isPaused();
        pb.textContent = on ? '▶' : '⏸';
        pb.classList.toggle('on', on);
        pb.title = on ? '继续计时' : '暂停计时';
    }

    function render() {
        el.textContent = '⏱ ' + fmt(parseInt(localStorage.getItem('studyTimerSec') || '0', 10));
        el.classList.toggle('paused', isPaused());
        renderPauseBtn();
    }

    window.togglePauseTimer = function () {
        localStorage.setItem('studyTimerPaused', isPaused() ? '0' : '1');
        render();
    };

    window.resetTimer = async function () {
        const ok = await confirmAsync('确定重置今日学习计时为 0？此操作不可撤销。', { danger: true });
        if (!ok) return;
        localStorage.setItem('studyTimerSec', '0');
        localStorage.setItem('studyTimerPaused', '0');
        render();
    };

    render();
    setInterval(() => {
        if (document.hidden) return;            // 切走标签页/窗口时暂停
        if (isPaused()) return;                 // 手动暂停
        const sec = parseInt(localStorage.getItem('studyTimerSec') || '0', 10) + 1;
        localStorage.setItem('studyTimerSec', String(sec));
        render();
    }, 1000);
})();

// ============ HTML 转义（各页面共用） ============
function esc(s) {
    return String(s == null ? '' : s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ============ 非阻塞弹层：替换原生 confirm/alert/prompt（根治 PWA 独立窗口弹到后台的"冻结感"） ============
// 原生 confirm()/alert() 是同步阻塞弹窗，在 PWA 独立窗口里常被弹出到后台，导致页面"假死"。
// 这里用统一的非阻塞组件替代，所有弹窗都落在当前页面 DOM 上。
function _uiModalRoot() {
    let el = document.getElementById('uiModalRoot');
    if (!el) {
        el = document.createElement('div');
        el.id = 'uiModalRoot';
        document.body.appendChild(el);
    }
    return el;
}

/** 轻提示（非阻塞，默认 2.2s 自动消失） */
function toast(msg, ms = 2200) {
    const root = _uiModalRoot();
    const t = document.createElement('div');
    t.className = 'ui-toast';
    t.textContent = msg;
    root.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    setTimeout(() => {
        t.classList.remove('show');
        setTimeout(() => t.remove(), 250);
    }, ms);
}

/** 确认弹层（Promise<boolean>）。opts: {title, okText, cancelText, danger} */
function confirmAsync(message, opts = {}) {
    return new Promise(resolve => {
        const root = _uiModalRoot();
        const { title = '请确认', okText = '确定', cancelText = '取消', danger = false } = opts;
        const wrap = document.createElement('div');
        wrap.className = 'ui-overlay';
        wrap.innerHTML = `
            <div class="ui-dialog${danger ? ' danger' : ''}">
                <div class="ui-dialog-title">${esc(title)}</div>
                <div class="ui-dialog-body">${esc(message)}</div>
                <div class="ui-dialog-actions">
                    <button class="ui-btn ui-cancel" data-act="cancel">${esc(cancelText)}</button>
                    <button class="ui-btn ui-ok${danger ? ' danger' : ''}" data-act="ok">${esc(okText)}</button>
                </div>
            </div>`;
        root.appendChild(wrap);
        const close = (val) => { wrap.classList.remove('show'); setTimeout(() => wrap.remove(), 180); resolve(val); };
        wrap.addEventListener('click', (e) => {
            const b = e.target.closest('[data-act]');
            if (b) close(b.dataset.act === 'ok');
            else if (e.target === wrap) close(false);   // 点遮罩取消
        });
        requestAnimationFrame(() => { wrap.classList.add('show'); wrap.querySelector('.ui-cancel').focus(); });
    });
}

/** 提示弹层（Promise，点确定或遮罩关闭）。用于原 alert 场景 */
function alertAsync(message, opts = {}) {
    return new Promise(resolve => {
        const root = _uiModalRoot();
        const { title = '提示', okText = '知道了' } = opts;
        const wrap = document.createElement('div');
        wrap.className = 'ui-overlay';
        wrap.innerHTML = `
            <div class="ui-dialog">
                <div class="ui-dialog-title">${esc(title)}</div>
                <div class="ui-dialog-body">${esc(message)}</div>
                <div class="ui-dialog-actions">
                    <button class="ui-btn ui-ok" data-act="ok">${esc(okText)}</button>
                </div>
            </div>`;
        root.appendChild(wrap);
        const close = () => { wrap.classList.remove('show'); setTimeout(() => wrap.remove(), 180); resolve(); };
        wrap.addEventListener('click', (e) => { if (e.target.closest('[data-act]') || e.target === wrap) close(); });
        requestAnimationFrame(() => { wrap.classList.add('show'); wrap.querySelector('.ui-ok').focus(); });
    });
}

/** 输入弹层（Promise<string|null>）。用于原 prompt 场景 */
function promptAsync(message, defaultValue = '', opts = {}) {
    return new Promise(resolve => {
        const root = _uiModalRoot();
        const { title = '请输入', okText = '确定', cancelText = '取消' } = opts;
        const wrap = document.createElement('div');
        wrap.className = 'ui-overlay';
        wrap.innerHTML = `
            <div class="ui-dialog">
                <div class="ui-dialog-title">${esc(title)}</div>
                <div class="ui-dialog-body">
                    <div class="ui-prompt-msg">${esc(message)}</div>
                    <input class="ui-input" type="text" value="${esc(defaultValue)}">
                </div>
                <div class="ui-dialog-actions">
                    <button class="ui-btn ui-cancel" data-act="cancel">${esc(cancelText)}</button>
                    <button class="ui-btn ui-ok" data-act="ok">${esc(okText)}</button>
                </div>
            </div>`;
        root.appendChild(wrap);
        const input = wrap.querySelector('.ui-input');
        requestAnimationFrame(() => { wrap.classList.add('show'); input.focus(); input.select(); });
        const close = (val) => { wrap.classList.remove('show'); setTimeout(() => wrap.remove(), 180); resolve(val); };
        wrap.addEventListener('click', (e) => {
            const b = e.target.closest ? e.target.closest('[data-act]') : null;
            if (b) close(b.dataset.act === 'ok' ? input.value.trim() : null);
            else if (e.target === wrap) close(null);
        });
        wrap.addEventListener('keydown', (e) => {
            if (e.code === 'Enter') { e.preventDefault(); close(input.value.trim()); }
            else if (e.code === 'Escape') { e.preventDefault(); close(null); }
        });
    });
}

// ============ 顶栏收起/展开（右上角单按钮，固定最右，全局生效） ============
// 单一固定按钮：▲收起 / ▼展开 同一位置；状态存 localStorage.navCollapsed。
(function () {
    const KEY = 'navCollapsed';
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const btn = document.createElement('button');
    btn.className = 'nav-toggle-btn';
    btn.type = 'button';
    btn.addEventListener('click', () => apply(navbar.dataset.collapsed !== '1', true));
    document.body.appendChild(btn);
    document.body.classList.add('nav-toggle-on'); // 让 .nav-tools 预留按钮位，避免窄屏遮挡

    function apply(collapsed, animate) {
        if (animate) navbar.classList.add('nav-anim');
        if (collapsed) {
            // JS 量高：负 margin 抵消布局占位 + 上移隐藏，动画同时进行
            navbar.style.marginTop = -navbar.offsetHeight + 'px';
            navbar.style.transform = 'translateY(-100%)';
            navbar.dataset.collapsed = '1';
        } else {
            navbar.style.marginTop = '';
            navbar.style.transform = '';
            navbar.dataset.collapsed = '';
        }
        btn.textContent = collapsed ? '▼' : '▲';
        btn.title = collapsed ? '展开顶栏' : '收起顶栏';
        localStorage.setItem(KEY, collapsed ? '1' : '0');
    }

    // 初始恢复（不加动画类，避免刷新闪动）
    apply(localStorage.getItem(KEY) === '1', false);

    // 视口变化时重算收起态的负 margin（顶栏可能在窄屏换行变高）
    window.addEventListener('resize', () => {
        if (navbar.dataset.collapsed !== '1') return;
        navbar.classList.remove('nav-anim');
        navbar.style.marginTop = -navbar.offsetHeight + 'px';
        requestAnimationFrame(() => navbar.classList.add('nav-anim'));
    });
})();

/* ===== 作文「套用示范」标注：逐句来源 / 可替换词 / 非模板词 / 词数 =====
   数据：pwa/data/writing_apply_marks.json（tools/annotate_writing_apply.py 生成）
   · spans 里 t=模板固定（不高亮）、s=模板槽位（可替换）、o=模板外自写     */
let APPLY_MARKS = null;

async function loadApplyMarks() {
    if (APPLY_MARKS) return APPLY_MARKS;
    try {
        const res = await fetch('data/writing_apply_marks.json', { cache: 'no-cache' });
        if (res.ok) APPLY_MARKS = await res.json();
    } catch (e) { /* 离线或缺失时退化为纯文本 */ }
    return APPLY_MARKS;
}

function apEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 示范文正文：模板部分原样，槽位词与自写部分分别高亮 */
function renderApplyBody(mk) {
    if (!mk || !mk.paras) return '';
    return mk.paras.map(p => '<p class="apply-para">' + p.sents.map(s =>
        (s.spans || []).map(sp => sp.t === 't'
            ? apEsc(sp.x)
            : `<mark class="${sp.t === 's' ? 'ap-slot' : 'ap-own'}">${apEsc(sp.x)}</mark>`).join('')
    ).join(' ') + '</p>').join('');
}

/** 展开/收起逐句标注 */
function apToggleMarks(btn) {
    const box = btn.closest('.ap-marks');
    const list = box.querySelector('.ap-sent-list');
    const show = list.hidden;
    list.hidden = !show;
    btn.textContent = show ? '收起逐句标注 ▴' : '展开逐句标注 ▾';
}

/** 标注面板：词数 + 图例 + 逐句来源/可替换词/非模板词/功能句（默认收起） */
function renderApplyMarks(mk) {
    if (!mk || !mk.paras) return '';
    const ok = mk.wc >= 150;
    const nSent = mk.paras.reduce((n, p) => n + p.sents.length, 0);
    let html = '<div class="ap-marks">';
    html += `<div class="ap-marks-head"><span class="ap-wc">📊 全文 <b>${mk.wc}</b> 词`
        + `<span class="ap-wc-req">要求 ≥150，${ok ? '达标' : '偏少'}</span>`
        + `<span class="ap-wc-seg">三段 ${mk.paras.map(p => p.wc).join(' / ')}</span></span>`
        + `<button class="ap-exp-btn2" onclick="apToggleMarks(this)">展开逐句标注 ▾</button></div>`;
    html += '<div class="ap-legend"><mark class="ap-slot">槽位词</mark>＝模板里留空处，按题替换　'
        + '<mark class="ap-own">自写/改写</mark>＝模板之外，需自己组织语言</div>';
    html += `<div class="ap-sent-list" hidden><div class="ap-list-cap">逐句来源与可替换词（共 ${nSent} 句）</div>`;
    mk.paras.forEach((p, pi) => {
        p.sents.forEach((s, si) => {
            const slots = [], own = [];
            (s.spans || []).forEach(sp => {
                const x = (sp.x || '').trim();
                if (!x) return;
                if (sp.t === 's') slots.push(x);
                else if (sp.t === 'o') own.push(x);
            });
            const head = s.kind === 'own'
                ? '<span class="ap-k ap-k-own">自写句</span><span class="ap-src">模板未覆盖</span>'
                : `<span class="ap-k ap-k-tpl">模板</span><span class="ap-src">${apEsc(s.src)}</span>`
                  + (s.cov ? `<span class="ap-cov">覆盖 ${Math.round(s.cov * 100)}%</span>` : '');
            html += `<div class="ap-sent-row"><div class="ap-sent-head"><span class="ap-no">P${pi + 1}.${si + 1}</span>${head}</div>`;
            if (s.cn) html += `<div class="ap-line ap-line-cn"><span class="ap-tag ap-tag-cn">中译</span><span>${apEsc(s.cn)}</span></div>`;
            if (slots.length) html += `<div class="ap-line"><span class="ap-tag ap-tag-s">可替换词</span><span>${apEsc(slots.join('　/　'))}</span></div>`;
            if (own.length) html += `<div class="ap-line"><span class="ap-tag ap-tag-o">非模板词</span><span>${apEsc(own.join('　/　'))}</span></div>`;
            if (s.keys && s.keys.length) html += `<div class="ap-line"><span class="ap-tag ap-tag-k">功能句</span><span>${s.keys.map(apEsc).join('；')}</span></div>`;
            html += '</div>';
        });
    });
    return html + '</div></div>';
}
