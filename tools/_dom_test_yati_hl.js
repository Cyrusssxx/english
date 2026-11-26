/* 押题页范文划词高亮回归
   运行：NODE_PATH=E:/deps_cache/jsdom-test/node_modules node tools/_dom_test_yati_hl.js
   验：① 划词上色生成 mark.note-hl（不带 data-mk），localStorage 按题号存；
       ② 切到别的题不串色，切回来自动恢复；
       ③ 词典就绪重渲染后高亮仍在；
       ④ 点高亮弹取消条、点取消后消失；
       ⑤ 清除按钮随高亮数显隐。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const raw = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');
const data = JSON.parse(raw);

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window: w } = dom;
const d = w.document;
w.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(raw)) });
w.eval(`
  var KW_BY_KEY = new Map();
  function kwLoad(){ return Promise.resolve(); }
  function kwBind(){}
  function kwOpen(){}
  function kwSplit(){ return null; }
  function dictLookup(w){ return { p: '/test/', t: '桩:' + w }; }
  function loadDict(){ return Promise.resolve(); }
`);
d.querySelector('.navbar').dataset.collapsed = '0';
try { w.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) {}
try { w.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本异常 ' + e.message); }
const wait = ms => new Promise(r => setTimeout(r, ms));

function firstSentence() {
    const s = d.querySelector('#ytMEssay .yt-jsent');
    if (!s) return null;
    const tw = d.createTreeWalker(s, 4 /* SHOW_TEXT */);
    while (tw.nextNode()) {
        const n = tw.currentNode;
        if (n.data.trim().length >= 6) return n;
    }
    return null;
}
function selectChars(tn, from, to) {
    const r = d.createRange();
    r.setStart(tn, from); r.setEnd(tn, to);
    const sel = w.getSelection();
    sel.removeAllRanges(); sel.addRange(r);
    return r;
}

(async () => {
    await wait(150);
    const clearBtn = d.getElementById('ytHlClearBtn');
    if (!clearBtn) fail('工具栏缺清除高亮按钮');
    else pass('清除高亮按钮就位');

    w.ytOpen(8);
    const tn = firstSentence();
    if (!tn) { fail('NO8 找不到可划词文本节点'); return; }
    const original = tn.data;
    selectChars(tn, 0, 5);
    w.ytHlApply('yellow');
    let mk = d.querySelector('#ytMEssay mark.note-hl');
    if (!mk) fail('划词后未生成 mark.note-hl');
    else {
        pass('划词上色生成 mark.note-hl');
        if (mk.hasAttribute('data-mk')) fail('mark.note-hl 误带 data-mk（会破坏块编号）');
        else pass('高亮 mark 不带 data-mk');
        if (mk.className !== 'note-hl note-hl-yellow') fail('颜色 class 错误：' + mk.className);
        else pass('颜色 class = note-hl-yellow');
    }
    let saved = JSON.parse(w.localStorage.getItem('yt_mk_v1') || '[]');
    if (saved.length !== 1 || !/^8:/.test(saved[0].b)) fail('localStorage 未按题号存：' + JSON.stringify(saved));
    else pass('高亮按题号 8 隔离存储');
    if (clearBtn.hidden) fail('有高亮时清除按钮仍隐藏');
    else pass('有高亮时清除按钮显示');

    // 切题不串色
    w.ytOpen(9);
    if (d.querySelector('#ytMEssay mark.note-hl')) fail('切到 NO9 串色了');
    else pass('切题不串色');
    w.ytOpen(8);
    mk = d.querySelector('#ytMEssay mark.note-hl');
    if (!mk || mk.textContent !== original.slice(0, 5)) fail('切回 NO8 高亮未恢复');
    else pass('切回本题高亮自动恢复');

    // 词典就绪重渲染（kwLoad.then 里那次 innerHTML 重建）后恢复
    const essay = d.getElementById('ytMEssay');
    const it8 = data.groups.flatMap(g => g.items).find(x => x.no === 8);
    essay.innerHTML = w.ytEssayHtml(it8);   // 从干净 HTML 重建，等价词典就绪那次 innerHTML
    essay.querySelectorAll('.yt-jsent-cn').forEach(b => { b.hidden = true; });
    w.ytRestoreAll();
    if (!d.querySelector('#ytMEssay mark.note-hl')) fail('重渲染后高亮丢失');
    else pass('词典就绪重渲染后高亮仍在');

    // 点高亮 → 取消条 → 点取消
    mk = d.querySelector('#ytMEssay mark.note-hl');
    mk.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));
    await wait(5);
    const cancelBar = d.querySelector('.hl-toolbar.hl-cancel-only');
    if (!cancelBar) fail('点高亮未弹取消条');
    else {
        pass('点高亮弹「取消高亮」条');
        cancelBar.querySelector('.hl-cancel').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
        await wait(5);
        if (d.querySelector('#ytMEssay mark.note-hl')) fail('点取消后高亮未消失');
        else pass('点取消后高亮消失');
    }
    saved = JSON.parse(w.localStorage.getItem('yt_mk_v1') || '[]');
    if (saved.length) fail('取消后 localStorage 仍有残留：' + JSON.stringify(saved));
    else pass('取消后存储清空');
    if (!clearBtn.hidden) fail('高亮清空后清除按钮仍显示');
    else pass('高亮清空后清除按钮隐藏');

    console.log(ok ? '\nALL PASS' : '\nHAS FAIL');
    process.exit(ok ? 0 : 1);
})();
