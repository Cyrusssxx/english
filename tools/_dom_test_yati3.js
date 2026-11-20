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
if (!/ytWordHtml/.test(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8'))) fail('缺词可点标注函数');
else pass('英文用词可点标注函数 ytWordHtml');

/* 2. DOM 交互 */
const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = () => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(raw)) });
// 词典桩：让 kwMarkText 走真实分支，验证词被 .kw 标注
window.eval(`
  // 桩词取原始 NO6 范文里确实出现的词：首句 education、第二句 skills
  // （回退原文后 technology 不再出现，桩须跟着内容走）
  var KW_BY_KEY = new Map([['education', {en:'education',cn:'教育',use:'教育',ex:'',exCn:''}],['skills', {en:'skills',cn:'技能',use:'技能',ex:'',exCn:''}]]);
  function kwMarkText(text, esc){
    return text.replace(/\\b(education|skills)\\b/g, (m)=>'<span class="kw">'+m+'</span>');
  }
  function kwLoad(){ return Promise.resolve(); }
  function kwBind(){}
  function kwOpen(){}
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

  // 点句展开
  sents[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (cn.hidden) fail('点句未展开中文'); else pass('点句展开该句中文');
  sents[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (!cn.hidden) fail('再点未收起'); else pass('再点收起该句中文');

  // 词可点：education 应被 .kw 标注（词典就绪桩）
  if (!d.querySelector('#ytMEssay .yt-en .kw')) fail('英文重点词未被标注为可点 .kw');
  else pass('英文重点词标注为可点 .kw');

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

  // 「显示中文译文」一键展开/收起所有逐句译块
  const btn = d.getElementById('ytCnBtn');
  const boxes = d.querySelectorAll('#ytMEssay .yt-jsent-cn');
  btn.click();
  const opened = [...boxes].filter(x => !x.hidden).length;
  if (opened !== boxes.length) fail(`一键展开不全: 译块 ${opened}/${boxes.length}`);
  else pass(`按钮一键展开全部逐句译文（${opened} 句）`);
  btn.click();
  const closed = [...boxes].filter(x => x.hidden).length;
  if (closed !== boxes.length) fail(`一键收起不全: 译块 ${closed}/${boxes.length}`);
  else pass('按钮再点一键收起全部逐句译文');
  console.log(ok ? '\nYATI3 ALL PASS' : '\nYATI3 FAIL');
  process.exit(ok ? 0 : 1);
})();
