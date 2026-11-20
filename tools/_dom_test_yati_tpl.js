/* 押题页小作文「模板功能句」角标回归。
   运行：node tools/_dom_test_yati_tpl.js
   验：① 小作文 8 篇模板句有紫色「模板」角标，且角标不进句子 textContent；
       ② 大作文 18 篇不出现角标（避免通用句式误标）；
       ③ 模板句判定随风句话覆盖（开头寒暄/来意/收尾/通知纪要格式）。 */
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

/* 1. JS / CSS 就位 */
if (!/ytIsTplSent/.test(js) || !/yt-tpl-tag/.test(js)) fail('缺模板句判定/渲染逻辑');
else pass('模板句判定与渲染逻辑就位');
if (!/\.yt-tpl-tag\s*\{[^}]*color:\s*#7c3aed/.test(css)) fail('缺模板角标样式');
else pass('模板角标样式就位（紫色，区别于骨架蓝）');
if (!/html\.dark \.yt-tpl-tag/.test(css)) fail('缺模板角标深色样式');
else pass('模板角标深色主题适配');

/* 2. DOM 实跑：逐篇开弹层，数角标 */
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
const flat = data.groups.flatMap(g => g.items);

(async () => {
  await wait(150);
  let smallTagged = 0, bigTagged = 0, textBad = [];
  const smallTplNos = [];
  for (const g of data.groups) {
    const isSmall = g.id === 't1';
    for (const it of g.items) {
      window.ytOpen(it.no);
      const essay = d.getElementById('ytMEssay');
      const tags = essay.querySelectorAll('.yt-tpl-tag');
      const sents = [...essay.querySelectorAll('.yt-jsent')];
      if (isSmall) {
        smallTagged += tags.length;
        if (tags.length) smallTplNos.push(it.no);
      } else {
        bigTagged += tags.length;
      }
      // 角标是句首兄弟节点，句子 textContent 必须严格等于原文（拼接校验不吞字）。
      // 注意 meta 块走 metaLines 分支不产生 .yt-jsent，其余（h/p/sign）都走逐句分支。
      const orig = [];
      (it.blocks || []).filter(b => b.k !== 'meta').forEach(b => (b.sents || []).forEach(s => orig.push(s.en)));
      sents.forEach((el, i) => {
        if (orig[i] != null && el.textContent !== orig[i]) textBad.push([it.no, i, el.textContent.slice(0, 30)]);
      });
    }
  }
  if (bigTagged) fail('大作文出现模板角标（误标）: ' + bigTagged);
  else pass('大作文 18 篇零角标');
  if (!smallTagged) fail('小作文没有模板角标');
  else pass(`小作文模板角标 ${smallTagged} 个，分布篇号 ${smallTplNos.join(',')}`);
  if (textBad.length) fail('角标吞了句子文字: ' + JSON.stringify(textBad.slice(0, 3)));
  else pass('所有句子 textContent 严格等于原文');

  /* 3. 关键句式覆盖：每类至少一句被打标 */
  const need = ['I hope this message finds you well.', 'I am writing to', 'Looking forward to your early reply.', 'The meeting concluded with'];
  const allSmallEn = data.groups.filter(g => g.id === 't1').flatMap(g => g.items)
      .flatMap(it => (it.blocks || []).flatMap(b => (b.sents || []).map(s => s.en)));
  const taggedEn = allSmallEn.filter(en => window.ytIsTplSent(en, 20));
  need.forEach(pat => {
    if (!taggedEn.some(en => en.indexOf(pat) >= 0)) fail('模板句式未覆盖: ' + pat);
  });
  pass('寒暄/来意/收尾/纪要四类句式均覆盖');

  console.log(ok ? '\n全部通过' : '\n有失败');
  process.exit(ok ? 0 : 1);
})();
