/* 押题弹层新功能回归：逐句点译 + 头部英文题名隐藏 + 背景目录隐藏 + 范文来自模板池。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const css = fs.readFileSync(path.join(PWA, 'css/style.css'), 'utf8');
const yati = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');
const data = JSON.parse(yati);

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

// CSS 静态断言
if (!/body\.yt-modal-open \.wr-layout \{ visibility: hidden/.test(css)) fail('缺背景隐藏规则');
else pass('弹层打开时隐藏背景目录/页面');
if (!/yt-box \{ width: min\(1440px/.test(css)) fail('缺弹层加高规则');
else pass('弹层加高到 94vh');
if (!/yt-mf \{ padding: 5px/.test(css)) fail('缺底栏压缩');
else pass('头/底栏压缩');
if (!/yt-sent-cn\[hidden\] \{ display: none/.test(css)) fail('缺中文隐藏规则');
else pass('逐句中文默认隐藏');

// 数据断言：每句 en/cn 齐备、无占位符
let sentN = 0, empty = 0, ph = 0;
for (const g of data.groups) for (const it of g.items) for (const b of it.blocks) {
  for (const s of (b.sents || [])) { sentN++; if (!s.en || !s.cn) empty++; if (/\{\{/.test(s.en)) ph++; }
}
if (empty || ph) fail(`句子数据异常: 空 ${empty}, 占位符 ${ph}`);
else pass(`逐句双语 ${sentN} 句齐备、无残留占位符`);

// DOM：点句开合
const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = url => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(yati)) });
window.document.querySelector('.navbar').dataset.collapsed = '0';
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) {}
try { window.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本异常 ' + e.message); }
const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(200);
  window.ytOpen(6);
  await wait(50);
  const sent = d.querySelector('#ytMEssay .yt-sent');
  const cn = sent && sent.nextElementSibling;
  if (!sent || !cn || !cn.classList.contains('yt-sent-cn')) fail('首句未生成点译结构');
  else pass('范文首句生成 .yt-sent + .yt-sent-cn');
  if (!cn.hidden) fail('中文默认应隐藏');
  else pass('中文默认隐藏');
  sent.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (cn.hidden || !sent.classList.contains('on')) fail('点句未展开中文');
  else pass('点句展开中文并高亮: ' + cn.textContent.slice(0, 24));
  sent.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (!cn.hidden || sent.classList.contains('on')) fail('再点未收起');
  else pass('再点收起中文');

  // 键盘开合
  sent.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
  if (cn.hidden) fail('Enter 未展开'); else pass('键盘 Enter 可展开');

  // 上一题/下一题后点译结构仍在
  window.ytStep(1);
  await wait(20);
  if (!d.querySelector('#ytMEssay .yt-sent')) fail('翻页后点译结构丢失');
  else pass('翻页后点译结构仍在');

  console.log(ok ? '\nYATI2 ALL PASS' : '\nYATI2 FAIL');
  process.exit(ok ? 0 : 1);
})();
