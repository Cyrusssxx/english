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

    window.resetTimer = function () {
        if (!confirm('确定重置今日学习计时为 0？此操作不可撤销。')) return;
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
