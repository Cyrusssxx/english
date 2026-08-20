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
