/* 翻译页「本篇词组」回归（article.html?type=translation）：
 * 阅读精翻页在 renderArticle() 末尾调用 renderPhraseZone()，而翻译类型走独立 early-return 分支，
 * 该调用被绕过——翻译页词组区是否出现，取决于 enrichRender() 那条补挂链。
 * 本测试实跑翻译页与阅读页对照，断言：
 *   A. 词典就绪后 #phraseZone 确实挂进 #readPane（DOM 存在）
 *   B. 精读开 → display 恢复、词组 15-25 条、长难句 1-3 句（与阅读页同款）
 *   C. 精读关 → 隐藏（display:none），不残留
 *   D. 阅读页（2022_text1）行为一致，证明翻译与阅读同款
 *
 * 用法: node tools/verify_translation_phrasezone.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const problems = [];

function ok(name, cond, extra) {
    if (!cond) problems.push(name + (extra != null ? '  ->  ' + extra : ''));
    console.log('  ' + (cond ? 'PASS  ' : 'FAIL  ') + name + (cond || extra == null ? '' : '  ->  ' + extra));
}

function makeDom(aid) {
    const html = fs.readFileSync(path.join(PWA, 'article.html'), 'utf8');
    const dom = new JSDOM(html, {
        url: 'http://localhost/article.html?id=' + aid,
        runScripts: 'outside-only', pretendToBeVisual: true,
    });
    const w = dom.window;
    w.fetch = (p) => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
        text: () => Promise.resolve(fs.readFileSync(path.join(PWA, p), 'utf8')),
    });
    const inline = [...w.document.querySelectorAll('script:not([src])')].map(s => s.textContent).join('\n;\n');
    const libs = ['common.js', 'storage.js', 'dict.js', 'annotate.js', 'article.js']
        .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
    w.eval(libs + '\n;\n' + inline);
    // jsdom 无 IndexedDB：整层桩掉（init 的本地用户数据段走这些函数）
    w.dbAll = async () => [];
    w.dbGet = async () => null;
    w.dbPut = async () => undefined;
    w.dbPutMany = async () => undefined;
    w.dbDelete = async () => undefined;
    w.getArtNote = async () => '';
    w.saveArtNote = async () => true;
    w.confirm = () => true;
    w.alert = () => {};
    w.scrollTo = () => {};
    w.toast = (m) => { (w.__toasts = w.__toasts || []).push(m); };
    w.__toasts = [];
    return dom;
}

async function runCase(aid, label, minItems) {
    console.log('\n[' + label + '] id=' + aid + '  词组下限=' + minItems);
    const dom = makeDom(aid);
    const w = dom.window;
    const d = w.document;
    // 等 enrichRender 后的词组区（词典+词组约 3.6MB，jsdom 解析较慢）
    let zone = null;
    for (let i = 0; i < 240; i++) {
        zone = d.getElementById('phraseZone');
        if (zone) break;
        await sleep(50);
    }
    ok('A1 词组区已挂入 DOM', !!zone, zone ? '' : '等待 12s 仍未出现 #phraseZone');
    if (!zone) return null;

    // A2 挂载位置：readPane 内、正文之后
    const pane = d.getElementById('readPane');
    ok('A2 位于 readPane 内', !!pane && pane.contains(zone));
    const firstSent = d.querySelector('.sent');
    // DOCUMENT_POSITION_PRECEDING = 4：firstSent 在 zone 之前 → 词组区位于正文之后
    ok('A3 位于正文之后', !!firstSent && !!(firstSent.compareDocumentPosition(zone) & 4));

    // B 精读开：显示 + 条数
    w.toggleCnAll();
    ok('B1 精读开后词组区可见', zone.style.display !== 'none', JSON.stringify(zone.style.display));
    const items = zone.querySelectorAll('.pz-item').length;
    // 翻译篇幅仅 ~150 词（词典候选上限约 14），下限按篇幅自适应；阅读 ~400 词保 15 条下限
    ok('B2 词组 ' + minItems + '-25 条（实为 ' + items + '）', items >= minItems && items <= 25, items);
    const firstKey = (zone.querySelector('.pz-item b') || {}).textContent || '';
    ok('B3 首条词组非空且带释义', firstKey.trim().length > 0 && !!zone.querySelector('.pz-meaning'), firstKey);
    const ls = zone.querySelectorAll('.ls-item').length;
    ok('B4 长难句 1-3 句（实为 ' + ls + '）', ls >= 1 && ls <= 3, ls);
    ok('B5 长难句带原文', !!zone.querySelector('.ls-en .word') || (zone.querySelector('.ls-en') || { textContent: '' }).textContent.trim().length > 20);

    // C 精读关：隐藏
    w.toggleCnAll();
    ok('C1 精读关后隐藏', zone.style.display === 'none', JSON.stringify(zone.style.display));

    // C2 重开仍在（幂等，不重复挂载）
    w.toggleCnAll();
    ok('C2 重开仍同一节点（不重复挂载）', d.querySelectorAll('#phraseZone').length === 1, d.querySelectorAll('#phraseZone').length);

    return { items, ls };
}

(async () => {
    const t = await runCase('2011_translation', '翻译页', 10);
    const r = await runCase('2022_text1', '阅读页对照', 15);
    if (t && r) {
        ok('D 两页词组区同款且均达各自篇幅下限（翻译=' + t.items + ' 阅读=' + r.items + '）',
            t.items >= 10 && r.items >= 15, '翻译=' + t.items + ' 阅读=' + r.items);
    }
    if (problems.length) {
        console.log('\nFAIL ' + problems.length + ' 处:');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('\nTRANSLATION PHRASEZONE OK：翻译页与阅读页同款词组区（挂载/条数/长难句/精读联动/幂等）');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 4).join('\n')); process.exit(1); });
