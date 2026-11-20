/* 押题页回归：范文结构（模板三段）+ 逐句中英完备 + 「显示中文译文」交互。
   运行：node tools/_dom_test_yati2.js   （jsdom 装在 E:/deps_cache/jsdom-test） */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const css = fs.readFileSync(path.join(PWA, 'css/style.css'), 'utf8');
const raw = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');
const data = JSON.parse(raw);

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

/* ---------- 1. 数据：结构与译文 ---------- */
const CJK = /[\u4e00-\u9fff]/;
const BIG_INTRO = 'This phenomenon can be attributed to a combination of factors.';
const NEG_OPEN = /^On balance, the (figures|picture|two pictures) point(s)? to a problem worth taking seriously\.$/;
const POS_OPEN = /^On balance, (this is a positive trend worth welcoming|interest deserves at least as much weight as market demand)\.$/;
const NEG_CLOSE = /^Unless effective measures are taken, it may well get worse\.$/;
const POS_CLOSE = /^(Given the momentum behind it|A choice that balances both)/;

let bigN = 0, smallN = 0, sentN = 0, noCn = 0, enOnly = 0, badShape = [], wcBad = [];
for (const g of data.groups) {
  for (const it of g.items) {
    const isSmall = g.id === 't1';
    isSmall ? smallN++ : bigN++;
    const bs = it.blocks || [];
    const words = bs.map(b => b.v).join(' ').match(/[A-Za-z][A-Za-z'-]*/g) || [];
    if (isSmall) { if (words.length < 85 || words.length > 125) wcBad.push([it.no, words.length, 'small']); }
    else {
      if (words.length < 145 || words.length > 200) wcBad.push([it.no, words.length, 'big']);
      if (bs.length !== 3) badShape.push([it.no, '段数 ' + bs.length]);
      else {
        const p2 = bs[1].sents || [], p3 = bs[2].sents || [];
        if (p2[0].en !== BIG_INTRO) badShape.push([it.no, 'P2 引入句不符']);
        if (p2.length !== 4) badShape.push([it.no, 'P2 原因数 ' + (p2.length - 1)]);
        if (!(NEG_OPEN.test(p3[0].en) || POS_OPEN.test(p3[0].en))) badShape.push([it.no, 'P3 立场句不符: ' + p3[0].en]);
        if (!(NEG_CLOSE.test(p3[p3.length - 1].en) || POS_CLOSE.test(p3[p3.length - 1].en))) badShape.push([it.no, 'P3 收尾句不符: ' + p3[p3.length - 1].en]);
        if (p3.length < 5) badShape.push([it.no, 'P3 对策不足 ' + (p3.length - 2)]);
      }
    }
    for (const b of bs) for (const s of (b.sents || [])) {
      sentN++;
      if (!s.cn || !s.cn.trim()) noCn++;
      else if (!CJK.test(s.cn)) enOnly++;
      else if (/\{\{/.test(s.en) || /\{\{/.test(s.cn)) enOnly++;
    }
  }
}
if (bigN !== 18 || smallN !== 8) fail(`题数不符 大${bigN} 小${smallN}`);
else pass(`26 篇：大作文 ${bigN} + 小作文 ${smallN}`);
if (badShape.length) fail('结构不符: ' + JSON.stringify(badShape.slice(0, 4)));
else pass('18 篇大作文均为 首段 / 引入+三原因 / 立场+对策+收尾');
if (noCn || enOnly) fail(`译文异常: 空 ${noCn}，无中文或残留占位符 ${enOnly}`);
else pass(`逐句中英 ${sentN} 句齐备，无漏译/占位符`);
if (wcBad.length) fail('词数越界: ' + JSON.stringify(wcBad));
else pass('词数全部落在大作文 145–200 / 小作文 85–125');

/* ---------- 2. 静态样式 ---------- */
if (!/\.yt-cn \{[^}]*border-top: 1px dashed/.test(css)) fail('缺中文块样式（与真题示范一致的虚线分隔）');
else pass('中文块沿用真题示范样式（虚线分隔 + 缩进 + 浅色字）');
if (!/\.yt-en p \{ text-indent: 2em/.test(css)) fail('缺英文段首缩进');
else pass('英文段首缩进 2em');
if (/\.yt-sent-cn/.test(css)) fail('旧逐句内联样式残留');
else pass('旧逐句内联样式已清除');

/* ---------- 3. DOM 交互 ---------- */
const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(raw)) });
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) { /* 导航脚本与本题无关 */ }
try { window.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本异常 ' + e.message); }
const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(150);
  window.ytOpen(6);
  await wait(50);
  const en = d.querySelector('#ytMEssay .yt-en');
  const cn = d.querySelector('#ytMEssay .yt-cn');
  const btn = d.getElementById('ytCnBtn');
  if (!en || !cn) fail('未生成 .yt-en / .yt-cn');
  else pass('英文段与中文段分别生成');
  if (!cn.hidden) fail('中文应默认隐藏'); else pass('中文默认隐藏');
  if (btn.textContent !== '显示中文译文') fail('按钮初始文案错: ' + btn.textContent);
  else pass('按钮初始为「显示中文译文」');

  btn.click();
  if (cn.hidden) fail('点按钮未展开中文');
  else pass('点按钮展开整篇中文');
  if (btn.textContent !== '隐藏中文译文') fail('展开后按钮文案未变');
  else pass('展开后按钮变「隐藏中文译文」');
  const cnText = cn.textContent;
  if (!CJK.test(cnText) || /[A-Za-z]{4,}/.test(cnText.replace(/AI|GDP|CPR/g, ''))) fail('中文区含英文残留: ' + cnText.slice(0, 40));
  else pass('中文区为纯中文译文（' + cnText.length + ' 字）');
  const cnParas = cn.querySelectorAll('p').length;
  if (cnParas !== 3) fail('中文段数 ' + cnParas); else pass('中文按 3 段呈现，与英文一一对应');

  btn.click();
  if (!cn.hidden) fail('再点未收起'); else pass('再点收起中文');

  const marks = d.querySelectorAll('#ytMEssay .yt-en mark.ap-own').length;
  if (!marks) fail('英文数字未标注'); else pass('英文数字标注 ' + marks + ' 处');

  btn.click();
  window.ytStep(1);
  await wait(30);
  const cn2 = d.querySelector('#ytMEssay .yt-cn');
  const btn2 = d.getElementById('ytCnBtn');
  if (!cn2.hidden || btn2.textContent !== '显示中文译文') fail('翻页未复位中文状态');
  else pass('翻到下一题后中文自动收起、按钮复位');

  console.log(ok ? '\nYATI2 ALL PASS' : '\nYATI2 FAIL');
  process.exit(ok ? 0 : 1);
})();
