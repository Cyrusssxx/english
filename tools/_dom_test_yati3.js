/* 押题页新呈现回归：无图片新标签 + 词典脚本 + 逐句点开中文 + 词可点。
   运行：node tools/_dom_test_yati3.js */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const css = fs.readFileSync(path.join(PWA, 'css/style.css'), 'utf8');
const raw = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

/* 1. 静态结构断言 */
if (/ytMOpen|target="_blank"|新标签页看原图|yt-mzoom-tip/.test(html)) fail('图片新标签功能未清干净');
else pass('图片点击新标签功能已去掉（无 target=_blank / 无提示文字）');
if (!/js\/dict\.js/.test(html)) fail('未引入 dict.js'); else pass('已引入 dict.js（词可点依赖）');
if (!/js\/kwpop\.js/.test(html)) fail('未引入 kwpop.js'); else pass('已引入 kwpop.js（词卡弹层）');
if (!/\.yt-jsent-cn\[hidden\] \{ display: none/.test(css)) fail('缺逐句译块隐藏样式');
else pass('逐句译块默认隐藏样式就位');
if (/\.yt-essay \.yt-jsent(\.on|:hover) \{[^}]*(background|box-shadow)/.test(css)) fail('当前句仍有下划线/高亮样式');
else pass('点译时当前句无下划线、无高亮（.on 仅状态标记）');
if (!/\.yt-sent-tr\s*\{[^}]*opacity:\s*\.\d/.test(css)) fail('句末译标记未设半透明');
else pass('句末译标记半透明样式就位');
// 高亮口径：只清填槽浅底，骨架蓝底 + 数字金底必须仍在（防未来整段误删）
const tail = css.slice(css.lastIndexOf('.yt-en .yt-fill'));
if (!/\.yt-skel\s*\{[^}]*background[^}]*border-bottom/.test(css)) fail('骨架蓝底被清掉了');
else pass('骨架蓝底保留');
if (!/\.yt-essay mark\.ap-own\s*\{[^}]*background:\s*rgba\(252, 211, 77/.test(css)) fail('数字金底被清掉了');
else pass('数字金底保留');
if (!/\.yt-en \.yt-fill\s*\{[^}]*background:\s*none/.test(tail)) fail('填槽浅底未清');
else pass('范文原句（填槽）浅底已清');
if (!/ytWordHtml/.test(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8'))) fail('缺词可点标注函数');
else pass('英文用词可点标注函数 ytWordHtml');

/* 2. DOM 交互 */
const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(raw)) });
// 词典桩：让逐词标注与骨架切分走真实分支（词库用真实 writing_keywords.json）
const kwRaw = fs.readFileSync(path.join(PWA, 'data/writing_keywords.json'), 'utf8');
window.eval(`
  var KW_BY_KEY = new Map(JSON.parse(${JSON.stringify(JSON.stringify(
      (JSON.parse(kwRaw).items || []).map(i => [i.k.toLowerCase(), i])
  ))}) );
  function kwLoad(){ return Promise.resolve(); }
  function kwBind(){}
  function kwOpen(){}
  // 与 kwpop.js 同语义的简化版（长词优先 + 词边界 + 不重叠）
  function kwSplit(text){
    const low = String(text).toLowerCase();
    const hits = [];
    KW_BY_KEY.forEach(function(it, k){
      let p = 0;
      while ((p = low.indexOf(k, p)) !== -1) {
        const b = p > 0 ? low[p-1] : '';
        const a = low[p + k.length] || '';
        if (!/[a-z0-9]/.test(b) && !/[a-z0-9]/.test(a)) hits.push({ s:p, e:p+k.length, it:it });
        p += k.length;
      }
    });
    if (!hits.length) return null;
    hits.sort(function(x,y){ return x.s - y.s || (y.e-y.s) - (x.e-x.s); });
    const out = []; let end = -1;
    hits.forEach(function(h){ if (h.s >= end) { out.push(h); end = h.e; } });
    return out;
  }
  function dictLookup(w){ return { p: '/test/', t: '桩释义:' + w }; }
`);
window.document.querySelector('.navbar').dataset.collapsed = '0';
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) {}
try { window.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本异常 ' + e.message); }
const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(150);
  window.ytOpen(6);
  await wait(30);
  const sents = d.querySelectorAll('#ytMEssay .yt-jsent');
  if (!sents.length) fail('未生成逐句 .yt-jsent');
  else pass(`逐句结构生成 ${sents.length} 句`);
  const cn = d.querySelector('#ytMEssay .yt-jsent-cn[data-for="0"]');
  if (!cn) fail('缺首句译块'); else if (!cn.hidden) fail('首句译块应默认隐藏');
  else pass('逐句译块默认隐藏: ' + cn.textContent.slice(0, 20));

  // 句末「译」标记：每句一个、文字为「译」、与句子同为一段的兄弟节点（不并入句子 textContent）
  const trs = d.querySelectorAll('#ytMEssay .yt-sent-tr');
  if (trs.length !== sents.length) fail(`译标记数量不符: ${trs.length}/${sents.length}`);
  else pass(`每句一个「译」标记（${trs.length} 个）`);
  if ([...trs].some(x => x.textContent !== '译')) fail('译标记文字不是「译」');
  else pass('译标记文字为「译」');
  if (trs[0].parentElement !== sents[0].parentElement) fail('译标记未与句子同段');
  else pass('译标记是句子兄弟节点（不并入句子原文）');

  // 点句子正文不再展开；只有点「译」标记才开合
  sents[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (!cn.hidden) fail('点句正文仍误展开中文'); else pass('点句正文不触发展开');
  trs[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (cn.hidden) fail('点译标记未展开中文'); else pass('点「译」展开该句中文');
  if (!trs[0].classList.contains('on')) fail('展开后译标记未点亮'); else pass('展开后译标记点亮(.on)');
  trs[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (!cn.hidden) fail('再点译标记未收起'); else pass('再点「译」收起该句中文');

  // 词可点：真实词库命中 .kw（如 clearly illustrates / bar chart）
  if (!d.querySelector('#ytMEssay .yt-en .kw')) fail('英文重点词未被标注为可点 .kw');
  else pass('英文重点词标注为可点 .kw');

  // 逐词可点：骨架/填槽之外每个实词都包 .yt-w；虚词不包
  const ws = [...d.querySelectorAll('#ytMEssay .yt-en .yt-w')];
  if (ws.length < 60) fail(`逐词可点太少: ${ws.length}`);
  else pass(`逐词可点 ${ws.length} 个实词`);
  if (ws.some(x => ['the', 'and', 'of'].includes(x.dataset.w))) fail('虚词不应包成可点词');
  else pass('虚词不参与点词');

  // 骨架 / 填槽染色 + 图例
  const skels = d.querySelectorAll('#ytMEssay .yt-skel');
  const fills = d.querySelectorAll('#ytMEssay .yt-fill');
  if (!skels.length) fail('未标出骨架片段 .yt-skel'); else pass(`骨架片段 ${skels.length} 处`);
  if (!fills.length) fail('未标出填槽片段 .yt-fill'); else pass(`填槽片段 ${fills.length} 处`);
  if (!d.querySelector('#ytMEssay .yt-legend')) fail('缺骨架图例');
  else if (/范文原句/.test(d.querySelector('#ytMEssay .yt-legend').textContent)) fail('图例仍含已取消的范文原句项');
  else pass('图例已显示（骨架 / 数据 / 词组，无范文原句项）');
  if (!/clearly illustrates$/.test(skels[0].textContent.trim())) fail('首句骨架片段切错: ' + skels[0].textContent);
  else pass('首句骨架片段切在 clearly illustrates');

  // 句内拼接必须还原原文（染色不能吞字/多字）
  const raw6 = JSON.parse(raw);
  const flat6 = []; (raw6.groups || []).forEach(g => (g.items || []).forEach(x => flat6.push(x)));
  const it6 = flat6.find(x => x.no === 6);
  const origSlices = [];
  (it6.blocks || []).forEach(b => (b.sents || []).forEach(s => origSlices.push(s.en)));
  let bad = [];
  [...d.querySelectorAll('#ytMEssay .yt-jsent')].forEach(el => {
    const i = +el.dataset.i;
    if (origSlices[i] != null && el.textContent !== origSlices[i]) bad.push(i);
  });
  if (bad.length) fail(`染色后文字与原文不一致 ${bad.length} 句: ${bad.slice(0, 3)}`);
  else pass('染色后逐句文字与原文完全一致');

  // 点普通词 → 弹释义卡（.yt-wpop），且不展开句译
  const plainW = ws.find(x => !x.closest('.kw'));
  const cnBefore = [...d.querySelectorAll('.yt-jsent-cn')].filter(x => !x.hidden).length;
  if (plainW) {
    plainW.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    const pop = d.querySelector('.yt-wpop');
    if (!pop) fail('点普通词未弹释义卡');
    else pass('点普通词弹释义卡: ' + pop.textContent.replace(/\s+/g, ' ').slice(0, 24));
    if ([...d.querySelectorAll('.yt-jsent-cn')].filter(x => !x.hidden).length !== cnBefore) fail('点词误连带展开句译');
    else pass('点词不连带展开句译');
    window.ytWClose();
  } else pass('（无普通词，跳过点词弹卡检查）');

  // 点词不触发句译（kw Capture 让位）：点 .kw 不应打开该句中文
  const cn2 = d.querySelector('.yt-jsent-cn[data-for="1"]');
  const s2 = d.querySelectorAll('.yt-jsent')[1];
  const kw = s2 && s2.querySelector('.kw');
  if (kw && cn2 && cn2.hidden) {
    kw.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (!cn2.hidden) fail('点词误触发句译'); else pass('点词不触发句译');
  } else pass('（该句无重点词，跳过点词隔离检查）');

  // 整篇中文块仍在、工具栏按钮可切换
  if (!d.querySelector('#ytMEssay .yt-cn')) fail('整篇中文块丢失');
  else pass('整篇中文对照块仍在');

  // 两个译文按钮互不干扰：逐句按钮只管逐句译块，全文按钮只管整篇对照块
  const sentBtn = d.getElementById('ytSentBtn');
  const cnBtn = d.getElementById('ytCnBtn');
  const boxes = d.querySelectorAll('#ytMEssay .yt-jsent-cn');
  const cnBlock = d.querySelector('#ytMEssay .yt-cn');
  if (!sentBtn || !cnBtn) fail('缺逐句/全文两个独立按钮');
  else pass('逐句译文 / 全文译文 两个独立按钮都在');
  if (sentBtn.textContent !== '显示逐句译文' || cnBtn.textContent !== '显示全文译文') fail('按钮初始文案错');
  else pass('按钮初始文案：显示逐句译文 / 显示全文译文');

  sentBtn.click();
  const opened = [...boxes].filter(x => !x.hidden).length;
  if (opened !== boxes.length) fail(`逐句按钮展开不全: 译块 ${opened}/${boxes.length}`);
  else pass(`逐句按钮一键展开全部逐句译文（${opened} 句）`);
  if (!cnBlock.hidden) fail('逐句按钮误展开了整篇中文（按钮间相互干扰）');
  else pass('逐句按钮不碰整篇中文对照块');
  if (sentBtn.textContent !== '隐藏逐句译文') fail('逐句按钮展开后文案未变');
  else pass('逐句按钮展开后变「隐藏逐句译文」');

  sentBtn.click();
  const closed = [...boxes].filter(x => x.hidden).length;
  if (closed !== boxes.length) fail(`逐句按钮收起不全: 译块 ${closed}/${boxes.length}`);
  else pass('逐句按钮一键收起全部逐句译文');

  cnBtn.click();
  if (cnBlock.hidden) fail('全文按钮未展开整篇中文');
  else pass('全文按钮展开整篇中文对照块');
  if ([...boxes].some(x => !x.hidden)) fail('全文按钮误展开了逐句译块（按钮间相互干扰）');
  else pass('全文按钮不碰逐句译块');
  if (cnBtn.textContent !== '隐藏全文译文') fail('全文按钮展开后文案未变');
  else pass('全文按钮展开后变「隐藏全文译文」');
  cnBtn.click();
  console.log(ok ? '\nYATI3 ALL PASS' : '\nYATI3 FAIL');
  process.exit(ok ? 0 : 1);
})();
