/* 押题页回归：范文结构（原始 26 篇，3 段）+ 逐句中英完备 + 「显示中文译文」交互。
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
/* 范文已回退为 ai归来版原始范文（用户 2026-11-20 定，不再硬套机制句）。
   断言只验「3 段 + 每段成句 + 逐句中英齐备 + 词数合理」，不再要求模板句式。 */
const CJK = /[\u4e00-\u9fff]/;

let bigN = 0, smallN = 0, sentN = 0, noCn = 0, enOnly = 0, badShape = [], wcBad = [];
for (const g of data.groups) {
  for (const it of g.items) {
    const isSmall = g.id === 't1';
    isSmall ? smallN++ : bigN++;
    const bs = it.blocks || [];
    const words = bs.map(b => b.v).join(' ').match(/[A-Za-z][A-Za-z'-]*/g) || [];
    if (isSmall) { if (words.length < 85 || words.length > 125) wcBad.push([it.no, words.length, 'small']); }
    else {
      if (words.length < 130 || words.length > 200) wcBad.push([it.no, words.length, 'big']);
      // 大作文 3 段正文，每段都有逐句
      const ps = bs.filter(b => b.k === 'p');
      if (ps.length !== 3) badShape.push([it.no, '正文段数 ' + ps.length]);
      else if (ps.some(b => !Array.isArray(b.sents) || b.sents.length < 2)) badShape.push([it.no, '段内缺逐句']);
    }
    // 所有块（含 meta/sign）均应有逐句；每段逐句 en 拼回 = v
    for (const b of bs) {
      if (!Array.isArray(b.sents) || !b.sents.length) { badShape.push([it.no, '块缺 sents']); continue; }
      const joined = b.sents.map(s => s.en).join(' ').replace(/\s+/g, ' ').trim();
      const v = (b.v || '').replace(/\s+/g, ' ').trim();
      if (joined !== v) badShape.push([it.no, '逐句拼回与段落原文不符: ' + b.k]);
      for (const s of b.sents) {
        sentN++;
        if (!s.cn || !s.cn.trim()) noCn++;
        else if (!CJK.test(s.cn)) enOnly++;
        else if (/\{\{/.test(s.en) || /\{\{/.test(s.cn)) enOnly++;
      }
    }
  }
}
if (bigN !== 18 || smallN !== 8) fail(`题数不符 大${bigN} 小${smallN}`);
else pass(`26 篇：大作文 ${bigN} + 小作文 ${smallN}`);
if (badShape.length) fail('结构不符: ' + JSON.stringify(badShape.slice(0, 4)));
else pass('18 篇大作文均 3 段、逐句齐备且拼回段落原文一致');
if (noCn || enOnly) fail(`译文异常: 空 ${noCn}，无中文或残留占位符 ${enOnly}`);
else pass(`逐句中英 ${sentN} 句齐备，无漏译/占位符`);
if (wcBad.length) fail('词数越界: ' + JSON.stringify(wcBad));
else pass('词数全部落在大作文 130–200 / 小作文 85–125');

/* 图表类 NO6–15：首段用用户骨架，第二段用 P2_FRAMEWORK（用户 2026-11-20 定） */
const flat = data.groups.reduce((a, g) => a.concat(g.items), []);
const badChart = [];
for (let no = 6; no <= 15; no++) {
  const it = flat.find(x => x.no === no);
  const p1 = (it && it.blocks[0].v) || '', p2 = (it && it.blocks[1].v) || '';
  if (!/clearly illustrat/.test(p1)) badChart.push([no, '首段未用 clearly illustrate(s) 骨架']);
  if (!/^This phenomenon can be attributed to a combination of factors\./.test(p2)) badChart.push([no, 'P2 引入句不符']);
  if (!/Primary among these is /.test(p2) || !/Equally important, /.test(p2)) badChart.push([no, 'P2 衔接词不全']);
  if (/First and foremost|Furthermore|Several factors|A variety of reasons/.test(p2)) badChart.push([no, 'P2 残留旧衔接词']);
}
if (badChart.length) fail('图表骨架不符: ' + JSON.stringify(badChart.slice(0, 4)));
else pass('NO6–15 图表类：首段 clearly illustrates + P2 引入句/Primary/Equally 全部就位，无旧衔接词');
// 第三段：立场句换成模板骨架（用户 2026-11-20 定：拆开用 + 按趋势分套）
const P3_POS_OPEN = 'On balance, this is a positive trend worth welcoming.';
const P3_POS_CLOSE = 'Given the momentum behind it, there is every reason to believe that it will continue in the years ahead.';
const P3_NEU_OPEN = 'On balance, what the figures reveal is a pattern that deserves careful judgment rather than simple praise or blame.';
const P3_NEU_CLOSE_RE = /depends on how well it is managed|By considering their abilities|Combining dependable online/;
const badP3 = [];
[6, 7, 8, 9, 10, 11, 12, 13, 14, 15].forEach(no => {
  const it = flat.find(x => x.no === no);
  const ss = ((it && it.blocks[2] && it.blocks[2].sents) || []).map(s => s.en);
  if (!ss.length) { badP3.push([no, '第三段缺失']); return; }
  const isPos = [7, 11, 12, 13].includes(no);
  if (ss[0] !== (isPos ? P3_POS_OPEN : P3_NEU_OPEN)) badP3.push([no, 'P3 首句未换模板骨架']);
  const last = ss[ss.length - 1];
  if (isPos && last !== P3_POS_CLOSE) badP3.push([no, 'P3 尾句缺 momentum 展望']);
  if (!isPos && !P3_NEU_CLOSE_RE.test(last)) badP3.push([no, 'P3 尾句中性与收束不符']);
  if (ss.some(s => /We should bear in mind/.test(s))) badP3.push([no, 'P3 残留旧立场句']);
});
if (badP3.length) fail('第三段骨架不符: ' + JSON.stringify(badP3.slice(0, 4)));
else pass('NO6–15 第三段：立场句换模板骨架（7/11/12/13 正面 + 6/8/9/10/14/15 中性），旧句已清');

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
