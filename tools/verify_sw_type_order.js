/* 小作文类型顺序回归（2026-11-11 备考优先级：建议 → 邀请 → 通知前置）
 * 1) 数据层：types 前 3 = advice / invite / notice，其余相对顺序不变，minutes 仍为第 11 类；
 * 2) 不变量：11 类齐全、letters 键与 types 一一对应、必背口径不动（重跑生成器丢 minutes 的坑）；
 * 3) 渲染层：jsdom 实跑 smallwriting.html，#swTypeTabs 的 tab 顺序必须与 types 数组一致。
 * 用法: node tools/verify_sw_type_order.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const PWA = path.resolve(__dirname, '..', 'pwa');
const DATA = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'small_writing.json'), 'utf8'));
const problems = [];
const ok = (name, cond, extra) => {
    if (!cond) problems.push(name + (extra != null ? ' -> ' + extra : ''));
    console.log('  ' + (cond ? 'PASS  ' : 'FAIL  ') + name + (!cond && extra != null ? ' -> ' + extra : ''));
};

(async () => {
    const ids = (DATA.types || []).map(t => t.id);
    console.log('数据层：types = ' + ids.join(' / '));
    ok('前 3 为 advice / invite / notice', ids.slice(0, 3).join(',') === 'advice,invite,notice', ids.slice(0, 3).join(','));
    ok('仍为 11 类', ids.length === 11, ids.length);
    ok('minutes 仍在末尾（手工追加的第 11 类未丢）', ids[10] === 'minutes', ids[10]);
    ok('其余 8 类相对顺序不变',
        ids.slice(3, 10).join(',') === 'thanks,congrats,apology,complaint,intro,inquire,opinion', ids.slice(3, 10).join(','));
    ok('letters 与 types 一一对应',
        Object.keys(DATA.letters).length === 11 && ids.every(x => x in DATA.letters));
    ok('必背口径 4/20 与 24 句额度不变', DATA.stats.core === 4 && DATA.stats.must === 20 && DATA.stats.items === 63);

    const html = fs.readFileSync(path.join(PWA, 'smallwriting.html'), 'utf8');
    const dom = new JSDOM(html, {
        url: 'http://localhost/smallwriting.html',
        runScripts: 'outside-only', pretendToBeVisual: true,
    });
    const w = dom.window, d = w.document;
    w.fetch = (p) => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
    });
    const libs = ['common.js', 'smallwriting.js']
        .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
    w.eval(libs);
    await w.swInit();

    const tabs = [...d.querySelectorAll('#swTypeTabs .sw-ttab')].map(b => ({ id: b.dataset.t, name: b.textContent }));
    console.log('渲染层：tabs = ' + tabs.map(x => x.name).join(' / '));
    ok('tab 数量 = 11', tabs.length === 11, tabs.length);
    ok('tab 顺序与 types 完全一致', tabs.map(x => x.id).join(',') === ids.join(','), tabs.map(x => x.id).join(','));
    ok('第 3 个 tab 是「通知」', tabs[2] && tabs[2].id === 'notice' && tabs[2].name === '通知', JSON.stringify(tabs[2]));

    if (problems.length) {
        console.log('\nFAIL ' + problems.length + ' 处');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('\nSW TYPE ORDER OK：建议 → 邀请 → 通知 前置，第 11 类会议纪要保持，tab 渲染顺序同步');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 4).join('\n')); process.exit(1); });
