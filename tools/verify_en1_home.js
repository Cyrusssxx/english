/* jsdom 实跑 en1.html 首页：新题型分类筛选 + 与话题筛选互斥 + 备份栏。
 * 用法: node tools/verify_en1_home.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');

const html = fs.readFileSync(path.join(PWA, 'en1.html'), 'utf8');
const dom = new JSDOM(html, { url: 'http://localhost/en1.html', runScripts: 'outside-only', pretendToBeVisual: true });
const w = dom.window;
w.fetch = (p) => Promise.resolve({
  ok: true,
  json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
  text: () => Promise.resolve(fs.readFileSync(path.join(PWA, p), 'utf8')),
});
// 内联脚本（runScripts:'outside-only' 不会执行它）+ 两个外链 js，
// 必须拼成一次 eval——storage.js 的 `const TYPE_NAMES` 是顶层词法声明，
// 分次 eval 时内联脚本看不见它。
const inline = [...dom.window.document.querySelectorAll('script:not([src])')]
  .map(s => s.textContent).join('\n;\n');
const libs = ['common.js', 'storage.js']
  .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
w.eval(libs + '\n;\n' + inline);
// jsdom 无 IndexedDB：答题统计那一步 stub 成空，其余逻辑照跑
w.dbAll = async () => [];

const problems = [];
const d = w.document;

function cards() { return [...d.querySelectorAll('.article-card')]; }
function years() {
  return cards().map(c => (c.querySelector('.ac-year') || {}).textContent).filter(Boolean);
}

(async () => {
  await w.init();
  await new Promise(r => setTimeout(r, 30));

  // 1. 新题型 chip 行
  const chips = [...d.querySelectorAll('#ntTabs .topic-tab')];
  const labels = chips.map(c => c.textContent.replace(/\d+$/, ''));
  const want = ['全部', '段落排序', '小标题对应', '七选五', '多项对应'];
  if (JSON.stringify(labels) !== JSON.stringify(want)) {
    problems.push('chip 标签 ' + labels.join('/') + ' != ' + want.join('/'));
  }
  const map = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'en1_newtype_map.json'), 'utf8'));
  const wantCount = map.types.reduce((s, t) => s + t.count, 0);
  if (wantCount !== 10) problems.push('分类总篇数 ' + wantCount + ' != 10');
  console.log('chip 行:', labels.join(' | '), '| 总篇数', wantCount);

  // 2. 逐个类型筛选
  for (const t of map.types) {
    w.pickNt(t.id);
    await new Promise(r => setTimeout(r, 10));
    const ys = years().map(Number);
    const exp = [...t.years].sort((a, b) => b - a);
    if (ys.length !== t.count) problems.push(t.id + ' 卡片数 ' + ys.length + ' != ' + t.count);
    if (JSON.stringify(ys) !== JSON.stringify(exp)) {
      problems.push(t.id + ' 年份 ' + ys.join(',') + ' != ' + exp.join(','));
    }
    const hid = d.getElementById('yearTabs').style.display === 'none';
    if (!hid) problems.push(t.id + ' 筛选时年份 tab 未隐藏');
    const hintOn = d.getElementById('ntHint').style.display !== 'none';
    if (!hintOn) problems.push(t.id + ' 提示行未显示');
    console.log('  %s → %s (%d 篇) %s', t.id, ys.join('·'), ys.length,
      ys.length === t.count ? 'OK' : 'BAD');
  }

  // 3. 取消筛选回到年份模式
  w.pickNt('');
  await new Promise(r => setTimeout(r, 10));
  if (d.getElementById('yearTabs').style.display === 'none') problems.push('取消后年份 tab 仍隐藏');
  if (cards().length === 0) problems.push('取消后列表为空');
  if (years().length !== 0) problems.push('按年份浏览时不应出现年份徽标');

  // 4. 与话题筛选互斥
  // 注意：curNt/curTopic 是内联脚本里的顶层 let，eval 的 let/const 不会泄漏到 window，
  // 所以只能靠 DOM 与 localStorage 断言，不能 w.curNt 直接读。
  w.pickNt('段落排序');
  await new Promise(r => setTimeout(r, 10));
  w.pickTopic('政法');
  await new Promise(r => setTimeout(r, 10));
  if (w.localStorage.getItem('en1_lastNtype') !== '') problems.push('选话题后 lastNtype 未清空');
  if (w.localStorage.getItem('en1_lastTopic') !== '政法') problems.push('lastTopic 未写入');
  const active = [...d.querySelectorAll('#ntTabs .topic-tab.active')].map(c => c.textContent);
  // 话题模式激活时新题型 chip 应全部不高亮（与英二 index.html 同逻辑）
  if (active.length) problems.push('选话题后新题型仍有高亮: ' + active.join(','));
  // 话题列表只收 text1-4，不应出现新题型卡片
  const types = cards().map(c => (c.querySelector('.ac-type') || {}).textContent);
  if (types.some(t => /新题型/.test(t))) problems.push('话题模式下混入新题型卡片');
  const topicActive = [...d.querySelectorAll('#topicTabs .topic-tab.active')].map(c => c.textContent);
  if (topicActive.join(',') !== '政法') problems.push('话题 chip 未高亮: ' + topicActive.join(','));
  console.log('互斥: lastNtype="%s" lastTopic="%s"，卡片类型=%s',
    w.localStorage.getItem('en1_lastNtype'), w.localStorage.getItem('en1_lastTopic'),
    [...new Set(types)].join('/') || '(无)');

  // 5. 备份栏（与英二首页一致）
  const bar = d.querySelector('.backup-bar');
  if (!bar) problems.push('缺备份栏');
  else {
    for (const fn of ['backupExport', 'backupImport', 'exportWrong']) {
      if (typeof w[fn] !== 'function') problems.push('备份函数缺失: ' + fn);
    }
    const btns = [...bar.querySelectorAll('button')].map(b => b.textContent.trim());
    if (btns.length !== 3) problems.push('备份按钮数 ' + btns.length);
  }

  // 6. localStorage 记忆
  w.pickNt('七选五');
  await new Promise(r => setTimeout(r, 10));
  if (w.localStorage.getItem('en1_lastNtype') !== '七选五') problems.push('lastNtype 未写入');
  if (w.localStorage.getItem('en1_lastTopic') !== '') problems.push('选新题型后话题未清空');
  if (cards().length !== 1) problems.push('七选五卡片数 ' + cards().length + ' != 1');

  if (problems.length) {
    console.log('\nFAIL ' + problems.length + ' 处:');
    problems.forEach(p => console.log('  - ' + p));
    process.exit(1);
  }
  console.log('\nen1.html 首页 OK：新题型分类筛选 / 互斥 / 记忆 / 备份栏');
  process.exit(0);
})().catch(e => { console.log('ERROR', e.message); process.exit(1); });
