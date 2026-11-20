/* 真实 DOM 验证小作文页：jsdom 加载 HTML + 执行 smallwriting.js，mock fetch 返回真实 small_writing.json。
   守：24 句必背集中清单 / 填空自测 / 中文切换 / 衔接词口径一致。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'smallwriting.html'), 'utf8');
const swjson = fs.readFileSync(path.join(PWA, 'data/small_writing.json'), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/smallwriting.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = url => {
  let body = null;
  if (url.indexOf('small_writing.json') >= 0) body = swjson;
  return Promise.resolve({ ok: body !== null, status: body !== null ? 200 : 404, json: () => Promise.resolve(JSON.parse(body || '{}')) });
};
const nav = window.document.querySelector('.navbar');
if (nav) nav.dataset.collapsed = '0';
// kwLoad 走 kwpop.js，若无重点词库也须 resolve；common 里可能有 DOM 依赖，按需吞掉
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) {}
try { window.eval(fs.readFileSync(path.join(PWA, 'js/kwpop.js'), 'utf8')); } catch (e) {}
try { window.eval(fs.readFileSync(path.join(PWA, 'js/smallwriting.js'), 'utf8')); } catch (e) { fail('脚本执行异常: ' + e.message + '\n' + e.stack); }

const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(250);
  const data = JSON.parse(swjson);

  // 1. 集中清单渲染出全部必背句
  const lines = [...d.querySelectorAll('#swDrill .sw-drill-line')];
  const expected = data.banks.reduce((n, b) => n + (b.items || []).filter(x => x.tier === 'core' || x.tier === 'must').length, 0);
  if (lines.length !== expected) fail('必背句 DOM 数 ' + lines.length + ' != 数据 ' + expected);
  else pass('集中清单渲染 ' + lines.length + ' 句必背（core+must）');

  // 2. 按段落分三组（第一段/第二段/第三段），默认全展开
  const grps = [...d.querySelectorAll('#swDrill .sw-drill-grp')];
  const gtitles = grps.map(g => (g.querySelector('.sw-drill-gt') || {}).textContent || '');
  if (grps.length !== 3) fail('段落分组数错: ' + grps.length + '（应 3）');
  else pass('按段落分 3 组');
  ['第一段', '第二段', '第三段'].forEach(t => {
    if (!gtitles.some(x => x.indexOf(t) >= 0)) fail('缺段落组标题: ' + t);
  });
  if (grps.some(g => !g.hasAttribute('open'))) fail('段落组未全部默认展开');
  else pass('三组标题齐全（第一段/第二段/第三段）且默认全展开');
  const subs = d.querySelectorAll('#swDrill .sw-drill-sub-t');
  if (!subs.length) fail('段内缺细分小节标题');
  else pass('段内保留细分小节 ' + subs.length + ' 个');

  // 3. 中文默认隐藏、按钮可切换
  const box = d.getElementById('swDrill');
  if (!box || box.classList.contains('show-cn')) fail('中文默认未隐藏');
  else pass('中文默认隐藏（先自己背）');
  const cnBtn = d.getElementById('swDrillCnBtn');
  if (!cnBtn) fail('缺显示中文按钮');
  else {
    cnBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (!box.classList.contains('show-cn') || cnBtn.textContent !== '隐藏中文') fail('点显示中文未生效');
    else pass('点显示中文：中文展开 + 按钮文案切换');
    cnBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (box.classList.contains('show-cn')) fail('再点未隐藏中文');
    else pass('再点隐藏中文');
  }

  // 4. 占位符芯片渲染 + 填空自测开关
  const phs = [...d.querySelectorAll('#swDrill .sw-drill-ph')];
  if (!phs.length) fail('占位符未渲染成可点芯片');
  else pass('占位符芯片 ' + phs.length + ' 个');
  const fillBtn = d.getElementById('swDrillFillBtn');
  if (!fillBtn) fail('缺填空自测按钮');
  else {
    fillBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (!d.body.classList.contains('sw-drill-on')) fail('填空自测未开启');
    else pass('填空自测开启（占位符变空白）');
    phs[0].dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (!phs[0].classList.contains('on')) fail('点填空空白未显示答案');
    else pass('点填空空白：显示填什么');
    fillBtn.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
    if (d.body.classList.contains('sw-drill-on') || phs[0].classList.contains('on')) fail('退出填空未复位');
    else pass('退出填空：状态复位');
  }

  // 5. 清单不污染划词高亮键位（无 data-k）
  if (d.querySelector('#swDrill [data-k]')) fail('集中清单误挂 data-k，会打乱高亮键位');
  else pass('集中清单纯展示，不进高亮键位');

  // 6. 衔接词口径：禁用栏不再列必背句在用的词
  const banned = data.linkers.map(x => x.banned).join(' | ');
  ['In addition', 'Furthermore', 'To be more specific'].forEach(w => {
    if (banned.indexOf(w) >= 0) fail('衔接词禁用栏仍列必背句在用的 ' + w);
  });
  if (!/简单正确 > 华丽套话/.test(data.linkers.map(x => x.better).join(' '))) fail('缺「简单正确 > 华丽套话」原则');
  else pass('衔接词口径统一：禁用栏不含必背句用词，含简单正确原则');

  // 7. 拼装框架第 4 步与真实必背句衔接词一致
  const fw = (data.framework || []).map(x => x.en).join(' ');
  if (!/In addition,/.test(fw)) fail('拼装框架第4步衔接词未与必背句对齐');
  else pass('拼装框架衔接词与必背句一致（In addition）');

  // 8. 结合型口径：框架含双动词来意句 + 第二功能取 s2 的规则；p1s2 末尾有 ammo 双动词句
  const fwCn = (data.framework || []).map(x => x.cn || '').join(' ');
  if (!/结合型/.test(fwCn) || !/第二个功能/.test(fwCn)) fail('拼装框架未写入结合型组织规则');
  else pass('拼装框架含结合型规则（双动词来意 + 第二功能取 s2）');
  const p1s2 = (data.banks || []).find(b => b.id === 'p1s2') || { items: [] };
  const last = p1s2.items[p1s2.items.length - 1] || {};
  if (!/introduce .* and invite/.test(last.en || '') || last.tier !== 'ammo' || last.must !== false)
    fail('p1s2 末尾缺双动词来意句（或误设为必背）');
  else pass('p1s2 末尾双动词来意句就位（ammo，不动必背数）');

  console.log(ok ? '\nALL PASS' : '\nSOME FAILED');
  process.exit(ok ? 0 : 1);
})();
