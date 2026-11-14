// tools/verify_timer_reset.js
// 计时器：每次打开新页面自动归零（2026-11-09 起，取代原「今日学习时长按天累计」）
// 覆盖：旧秒数清零 / 暂停态清零 / 无计时器页面不受影响 / 每秒累加仍工作 / 按钮全局接线 / 跨页再次归零
const path = require('path');
const fs = require('fs');
const { JSDOM, VirtualConsole } = require('jsdom');

const ROOT = path.join(__dirname, '..', 'pwa');
const COMMON = fs.readFileSync(path.join(ROOT, 'js', 'common.js'), 'utf8');
let pass = 0, fail = 0;
const errors = [];

function ok(name, cond, extra) {
    if (cond) { pass++; console.log('  PASS  ' + name); }
    else { fail++; console.log('  FAIL  ' + name + (extra != null ? '  ->  ' + extra : '')); }
}

function loadPage(htmlFile, seed) {
    const html = fs.readFileSync(path.join(ROOT, htmlFile), 'utf8');
    const vc = new VirtualConsole();
    vc.on('jsdomError', e => errors.push(htmlFile + ': ' + (e && e.message)));
    const dom = new JSDOM(html, {
        url: 'https://local.test/' + htmlFile,
        runScripts: 'outside-only',
        pretendToBeVisual: true,
        virtualConsole: vc,
    });
    const w = dom.window;
    for (const k of Object.keys(seed || {})) w.localStorage.setItem(k, seed[k]);
    try { w.eval(COMMON); } catch (e) { errors.push(htmlFile + ' eval: ' + e.message); }
    return w;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
    console.log('[1] 打开页面：遗留秒数 + 暂停态 -> 归零并重新开始计时');
    const w = loadPage('index.html', { studyTimerSec: '999', studyTimerPaused: '1', studyTimerDate: '2026-11-08' });
    const el = w.document.getElementById('navTimer');
    ok('navTimer 存在', !!el);
    ok('studyTimerSec 归零', w.localStorage.getItem('studyTimerSec') === '0', w.localStorage.getItem('studyTimerSec'));
    ok('暂停态被清零', w.localStorage.getItem('studyTimerPaused') === '0', w.localStorage.getItem('studyTimerPaused'));
    ok('显示 ⏱ 00:00:00', !!el && el.textContent.trim() === '⏱ 00:00:00', el && el.textContent);
    const pb = w.document.getElementById('timerPause');
    ok('暂停按钮显示 ⏸（未暂停）', !!pb && pb.textContent === '⏸', pb && pb.textContent);
    ok('全局 resetTimer 已挂载', typeof w.resetTimer === 'function');
    ok('全局 togglePauseTimer 已挂载', typeof w.togglePauseTimer === 'function');

    console.log('[2] 每秒累加仍工作');
    await sleep(1250);
    const sec = parseInt(w.localStorage.getItem('studyTimerSec'), 10);
    ok('约 1 秒后累加 >= 1', sec >= 1, 'sec=' + sec);

    console.log('[3] 手动暂停 -> 停止累加');
    w.togglePauseTimer();
    ok('暂停态写入 studyTimerPaused=1', w.localStorage.getItem('studyTimerPaused') === '1');
    const before = w.localStorage.getItem('studyTimerSec');
    await sleep(1250);
    ok('暂停期间秒数不变', w.localStorage.getItem('studyTimerSec') === before, before + ' -> ' + w.localStorage.getItem('studyTimerSec'));
    w.togglePauseTimer(); // 恢复，避免影响后续断言

    console.log('[4] 没有计时器的页面：不碰 localStorage');
    const w2 = loadPage('en1.html', { studyTimerSec: '777' });
    ok('en1.html 无 navTimer', !w2.document.getElementById('navTimer'));
    ok('en1.html 不重置秒数', w2.localStorage.getItem('studyTimerSec') === '777', w2.localStorage.getItem('studyTimerSec'));

    console.log('[5] 跨页语义：再次打开页面依旧归零');
    const w3 = loadPage('study.html', { studyTimerSec: '1234' });
    ok('study.html 打开即归零', w3.localStorage.getItem('studyTimerSec') === '0', w3.localStorage.getItem('studyTimerSec'));

    console.log('[6] 文案一致性：不再出现「今日学习」旧口径');
    const pages = ['index.html', 'article.html', 'favorites.html', 'stats.html', 'study.html', 'mistakes.html', 'suggestions.html', 'vocab.html'];
    for (const p of pages) {
        const html = fs.readFileSync(path.join(ROOT, p), 'utf8');
        const bad = html.includes('重置今日计时') || html.includes('今日学习时长');
        ok(p + ' 文案已更新', !bad);
    }

    console.log('[7] 顶栏收起按钮：点一下收起 / 再点展开，并通知吸顶条');
    const w4 = loadPage('recite.html', {});
    const nav = w4.document.querySelector('.navbar');
    const btn = w4.document.querySelector('.nav-toggle-btn');
    ok('收起按钮已注入 body', !!btn);
    let events = 0;
    w4.addEventListener('navheightchange', () => { events++; });
    ok('初始未收起', !nav || nav.dataset.collapsed !== '1');
    btn.click();
    ok('点一次 -> navbar.dataset.collapsed=1', nav.dataset.collapsed === '1');
    ok('html 上写了 data-nav-collapsed（供 CSS 让位）',
        w4.document.documentElement.dataset.navCollapsed === '1',
        w4.document.documentElement.dataset.navCollapsed);
    ok('按钮变 ▼（提示可展开）', btn.textContent === '▼', btn.textContent);
    ok('派发 navheightchange', events >= 1, events);
    btn.click();
    ok('再点一次 -> 恢复展开', nav.dataset.collapsed !== '1');
    ok('html 属性已清除', !w4.document.documentElement.dataset.navCollapsed);
    ok('按钮变回 ▲', btn.textContent === '▲', btn.textContent);
    ok('收起态写入 localStorage（跨页保持）', w4.localStorage.getItem('navCollapsed') === '0', w4.localStorage.getItem('navCollapsed'));

    ok('无 jsdom 执行错误', errors.length === 0, errors.join(' | '));
    console.log('\nRESULT  ' + pass + '/' + (pass + fail) + (fail ? '  FAILED' : '  ALL GREEN'));
    process.exit(fail ? 1 : 0);
})();
