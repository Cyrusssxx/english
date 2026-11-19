/* 真实 DOM 验证 recite 页：用 jsdom 加载 HTML + 执行 recite.js，mock fetch 提供真实数据。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'recite.html'), 'utf8');
const words = fs.readFileSync(path.join(PWA, 'data/writing_words.json'), 'utf8');
const dict = fs.readFileSync(path.join(PWA, 'data/dict.json'), 'utf8');
const wn = fs.readFileSync(path.join(PWA, 'data/wordnotes.json'), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/recite.html', pretendToBeVisual: true });
const { window } = dom;
// mock fetch：按 URL 返回真实数据
window.fetch = url => {
  let body = null;
  if (url === 'data/writing_words.json') body = words;
  else if (url === 'data/dict.json') body = dict;
  else if (url === 'data/wordnotes.json') body = wn;
  else if (url === 'data/writing_senses.json') body = JSON.stringify({ words: {} });
  return Promise.resolve({ ok: body !== null, status: body !== null ? 200 : 404, json: () => Promise.resolve(JSON.parse(body || '{}')) });
};
// dataset.collapsed 等
window.document.querySelector('.navbar').dataset.collapsed = '0';

const js = fs.readFileSync(path.join(PWA, 'js/recite.js'), 'utf8');
const dictJs = fs.readFileSync(path.join(PWA, 'js/dict.js'), 'utf8');
try {
  window.eval(dictJs);
  window.eval(js);
} catch (e) {
  fail('脚本执行异常: ' + e.message + '\n' + e.stack);
}

const d = window.document;
function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

(async () => {
  await wait(200); // 等 async rcInit 完成
  // 1. 词条渲染
  const rows = d.querySelectorAll('.rcw-row');
  const expect = JSON.parse(words).groups.reduce((s, g) => s + g.items.length, 0);
  if (rows.length !== expect) fail(`词条渲染数 ${rows.length} != ${expect}`);
  else pass(`词条渲染 ${rows.length} 条`);
  // 2. 分区
  const secs = d.querySelectorAll('.rc-wg');
  if (secs.length !== 6) fail('分区数 ' + secs.length); else pass('分区 6 个');
  // 3. 目录链接与锚点对应
  const links = [...d.querySelectorAll('#rcDirLinks a[data-t]')];
  if (links.length !== 6) fail('目录链接数 ' + links.length);
  else {
    const bad = links.filter(a => !d.getElementById(a.dataset.t));
    if (bad.length) fail('目录锚点失效 ' + bad.length);
    else pass('目录 6 链接均指向有效分区');
  }
  // 4. 英文词条可点（人名地名组除外，专名无词典释义）
  const parsed = JSON.parse(words);
  const nameN = parsed.groups.find(g => g.id === 'name').items.length;
  const ws = d.querySelectorAll('.rcw.word[data-w][data-ph="1"]');
  const expectClick = expect - nameN;
  if (ws.length !== expectClick) fail(`可点词条 ${ws.length} != ${expectClick}`); else pass(`可点词条 ${ws.length} 条（专名 ${nameN} 条不可点）`);
  // 括号注释已从 key 去掉（显示保留）
  const ai = [...ws].find(x => x.textContent.includes('artificial intelligence'));
  if (ai && /\(/.test(ai.dataset.w)) fail('词组 key 仍含括号'); else pass('词组 key 已去括号注释');
  // 5. 目录折叠：默认展开，点 summary 后 open 翻转（jsdom 对 details toggle 支持有限，直接校验初始态 + 结构）
  const dir = d.getElementById('rcDir');
  if (!dir) fail('目录卡片缺失');
  else if (!dir.hasAttribute('open')) fail('目录默认应展开');
  else pass('目录默认展开');
  const toggle = d.querySelector('.rc-dir-toggle');
  if (!toggle || toggle.textContent.trim() !== '收起') fail('右侧收起按钮文案'); else pass('收起按钮文案正确');
  // 6. 无旧内容
  if (d.getElementById('rcBig') || d.getElementById('rcSmall')) fail('旧视图容器残留');
  else pass('无旧速记视图');

  console.log(ok ? '\nDOM ALL PASS' : '\nDOM HAS FAILURES');
  process.exit(ok ? 0 : 1);
})();
