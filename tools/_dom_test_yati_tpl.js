/* 押题页小作文「模板功能句」高亮回归（2026-11-21 改版：角标 → 整句高亮）
   运行：node tools/_dom_test_yati_tpl.js
   验：① 模板句是 .yt-jsent.yt-tpl（整句淡底 + 底部虚线），**不再**插「模板」角标；
       ② 大作文 18 篇零高亮（避免通用句式误标）；
       ③ 高亮不吞字：句子 textContent 严格等于原文；
       ④ 小作文图例出现「模板」项，大作文图例不出现；
       ⑤ 句式覆盖：寒暄/来意/收尾/纪要四类都能命中。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const raw = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');
const data = JSON.parse(raw);
const css = fs.readFileSync(path.join(PWA, 'css/style.css'), 'utf8');
const js = fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

/* 1. JS / CSS 就位：高亮取代角标 */
if (!/ytIsTplSent/.test(js) || !/yt-tpl/.test(js)) fail('缺模板句判定/高亮逻辑');
else pass('模板句判定与高亮逻辑就位');
if (/yt-tpl-tag/.test(js)) fail('yati.js 仍在渲染「模板」角标');
else pass('不再逐句插「模板」角标');
if (!/\.yt-jsent\.yt-tpl\s*\{[^}]*background:/.test(css)) fail('缺模板句高亮样式');
else pass('模板句高亮样式就位（整句淡底，与骨架同套视觉）');
if (!/html\.dark \.yt-jsent\.yt-tpl/.test(css)) fail('缺模板句高亮深色样式');
else pass('模板句高亮深色主题适配');
if (/\.yt-tpl-tag\s*\{/.test(css)) fail('CSS 里还留着废弃的 .yt-tpl-tag');
else pass('废弃的角标样式已清掉');

/* 2. DOM 实跑：逐篇开弹层，数高亮 */
const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(raw)) });
window.eval(`
  var KW_BY_KEY = new Map();
  function kwLoad(){ return Promise.resolve(); }
  function kwBind(){}
  function kwOpen(){}
  function kwSplit(){ return null; }
  function dictLookup(w){ return { p: '/test/', t: '桩:' + w }; }
  function loadDict(){ return Promise.resolve(); }
`);
window.document.querySelector('.navbar').dataset.collapsed = '0';
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) {}
try { window.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本异常 ' + e.message); }
const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(150);
  let smallHi = 0, bigHi = 0, textBad = [];
  const smallNos = [];
  for (const g of data.groups) {
    const isSmall = g.id === 't1';
    for (const it of g.items) {
      window.ytOpen(it.no);
      const essay = d.getElementById('ytMEssay');
      const his = essay.querySelectorAll('.yt-jsent.yt-tpl');
      const tags = essay.querySelectorAll('.yt-tpl-tag');
      const sents = [...essay.querySelectorAll('.yt-jsent')];
      if (isSmall) {
        smallHi += his.length;
        if (his.length) smallNos.push(it.no);
      } else {
        bigHi += his.length;
      }
      if (tags.length) fail(`NO${it.no} 仍渲染了 ${tags.length} 个模板角标`);
      // meta 块（日期/记录人）走 metaLines，不产生 .yt-jsent；其余 h/p/sign 逐句
      const orig = [];
      (it.blocks || []).filter(b => b.k !== 'meta').forEach(b => (b.sents || []).forEach(s => orig.push(s.en)));
      sents.forEach((el, i) => {
        if (orig[i] != null && el.textContent !== orig[i]) textBad.push([it.no, i, el.textContent.slice(0, 30)]);
      });
    }
  }
  if (bigHi) fail('大作文出现模板高亮（误标）: ' + bigHi);
  else pass('大作文 18 篇零模板高亮');
  if (!smallHi) fail('小作文没有模板高亮');
  else pass(`小作文模板句高亮 ${smallHi} 句，分布篇号 ${smallNos.join(',')}`);
  if (smallNos.length !== 8) fail(`只有 ${smallNos.length} 篇有小作文模板高亮，应为 8 篇`);
  else pass('小作文 8 篇都有模板句高亮');
  if (textBad.length) fail('高亮吞了句子文字: ' + JSON.stringify(textBad.slice(0, 3)));
  else pass('所有句子 textContent 严格等于原文');

  /* 3. 图例：小作文有「模板」项，大作文没有 */
  window.ytOpen(19);
  const lg19 = d.getElementById('ytMEssay').querySelector('.yt-legend');
  if (!lg19) fail('小作文缺图例');
  else if (!lg19.querySelector('.yt-lg-tpl')) fail('小作文图例缺「模板」项');
  else pass('小作文图例含「模板」项：' + lg19.querySelector('.yt-lg-tpl').parentNode.textContent.trim());
  window.ytOpen(6);
  const lg6 = d.getElementById('ytMEssay').querySelector('.yt-legend');
  if (lg6 && lg6.querySelector('.yt-lg-tpl')) fail('大作文图例错显「模板」项');
  else pass('大作文图例不含「模板」项');

  /* 4. 关键句式覆盖：每类至少一句被高亮 */
  const need = ['I hope this message finds you well.', 'I am writing to', 'I am looking forward to hearing from you soon.', 'The meeting concluded with'];
  const allSmallEn = data.groups.filter(g => g.id === 't1').flatMap(g => g.items)
      .flatMap(it => (it.blocks || []).flatMap(b => (b.sents || []).map(s => s.en)));
  const hitEn = allSmallEn.filter(en => window.ytIsTplSent(en, 20));
  need.forEach(pat => {
    if (!hitEn.some(en => en.indexOf(pat) >= 0)) fail('模板句式未覆盖: ' + pat);
  });
  pass('寒暄/来意/收尾/纪要四类句式均覆盖');

  console.log(ok ? '\n全部通过' : '\n有失败');
  process.exit(ok ? 0 : 1);
})();
