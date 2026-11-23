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
  const groups = JSON.parse(words).groups;
  const secs = d.querySelectorAll('.rc-wg');
  if (secs.length !== groups.length) fail('分区数 ' + secs.length + ' != ' + groups.length); else pass('分区 ' + groups.length + ' 个');
  // 3. 目录链接与锚点对应（左侧 wr-toc）
  const links = [...d.querySelectorAll('#rcTocList a[data-t]')];
  if (links.length !== groups.length) fail('目录链接数 ' + links.length);
  else {
    const bad = links.filter(a => !d.getElementById(a.dataset.t));
    if (bad.length) fail('目录锚点失效 ' + bad.length);
    else pass('目录 ' + groups.length + ' 链接均指向有效分区');
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
  // 4b. 押题话题分块渲染：5 块题材 + 高频词 chips + 26 题行不丢 + 紧跟主题词组
  const t26 = d.getElementById('rcG_topics26');
  const t26secs = [...d.querySelectorAll('.rc-wg')].map(s => s.id);
  if (t26secs[1] !== 'rcG_topics26') fail('topics26 未紧跟主题词组: ' + t26secs.slice(0, 3));
  else pass('topics26 紧跟主题词组');
  const blocks = t26 ? [...t26.querySelectorAll('.rc-hw-block')] : [];
  if (blocks.length !== 5) fail('押题分块数 ' + blocks.length + ' != 5');
  else pass('押题话题分 5 块');
  const t26rows = t26 ? t26.querySelectorAll('.rcw-row').length : 0;
  if (t26rows !== 26) fail('押题 26 题行 ' + t26rows);
  else pass('押题 26 题行全渲染');
  const hws = t26 ? t26.querySelectorAll('.rc-hw.word[data-w]') : [];
  if (!hws.length || hws.length !== (parsed.groups.find(g => g.id === 'topics26').blocks || []).reduce((s, b) => s + b.words.length, 0))
    fail('分块高频词 chips 数不符 ' + hws.length);
  else pass('分块高频词 ' + hws.length + ' 个均可点查词');
  // 4c. 主题词组也分块（4 块、无空块、词条总数不丢）
  const topicG = d.getElementById('rcG_topic');
  const topicBlocks = topicG ? [...topicG.querySelectorAll('.rc-hw-block')] : [];
  const topicData = parsed.groups.find(g => g.id === 'topic');
  if (topicBlocks.length !== (topicData.blocks || []).length) fail('主题词分块数 ' + topicBlocks.length + ' != ' + (topicData.blocks || []).length);
  else pass('主题词分 ' + topicBlocks.length + ' 块');
  const emptyBlock = topicBlocks.find(b => b.querySelectorAll('.rcw-row').length === 0);
  if (emptyBlock) fail('主题词存在空块: ' + emptyBlock.querySelector('.rc-hw-title').textContent);
  else pass('主题词无空块');
  const topicRows = topicG ? topicG.querySelectorAll('.rcw-row').length : 0;
  if (topicRows !== topicData.items.length) fail('主题词行 ' + topicRows + ' != ' + topicData.items.length);
  else pass('主题词 ' + topicRows + ' 条全渲染');
  // 4d. 连接词组只收骨架真词：on balance 在、to begin with/admittedly 不在
  const linkG = d.getElementById('rcG_link');
  const linkText = linkG ? linkG.textContent : '';
  if (!/on balance/i.test(linkText)) fail('连接词缺 On balance（骨架立场句）');
  else pass('连接词含骨架立场句 On balance');
  if (!/Primary among these is/i.test(linkText) || !/Equally important/i.test(linkText) || !/A further driver is/i.test(linkText))
    fail('连接词缺第二段机制句引入语');
  else pass('连接词含三条机制句引入语');
  if (/to begin with|admittedly|therefore/i.test(linkText)) fail('连接词混入非骨架词');
  else pass('连接词无骨架外词');
  // 5. 左侧目录 wrapper + 折叠按钮 + 竖条抽屉 tab
  const toc = d.getElementById('rcToc');
  const tocList = d.getElementById('rcTocList');
  const foldBtn = d.getElementById('rcTocFold');
  const tab = d.getElementById('rcTocTab');
  const mask = d.getElementById('rcTocMask');
  if (!toc || !tocList || !foldBtn || !tab || !mask) fail('左侧目录骨架缺失');
  else pass('左侧目录骨架完整');
  if (!/wr-toc/.test(toc.className)) fail('目录未复用 wr-toc 样式类');
  else if (foldBtn.textContent.trim() !== '‹ 收起') fail('收起按钮文案: ' + foldBtn.textContent.trim());
  else pass('目录复用大作文样式 + 收起按钮正确');
  // 6. 无旧内容
  if (d.getElementById('rcBig') || d.getElementById('rcSmall')) fail('旧视图容器残留');
  else pass('无旧速记视图');

  console.log(ok ? '\nDOM ALL PASS' : '\nDOM HAS FAILURES');
  process.exit(ok ? 0 : 1);
})();
