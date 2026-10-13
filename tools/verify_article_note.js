/* jsdom 实跑 article.html：顶栏「备注」小块 + 浮窗输入保存链路。
 * 用法: node tools/verify_article_note.js [article_id]
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');
const AID = process.argv[2] || '2022_text1';

const html = fs.readFileSync(path.join(PWA, 'article.html'), 'utf8');
const dom = new JSDOM(html, {
  url: 'http://localhost/article.html?id=' + AID,
  runScripts: 'outside-only', pretendToBeVisual: true,
});
const w = dom.window;
const d = w.document;

w.fetch = (p) => Promise.resolve({
  ok: true,
  json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
  text: () => Promise.resolve(fs.readFileSync(path.join(PWA, p), 'utf8')),
});

// 用内存替掉 IndexedDB 层的备注读写（article.js 调的是 storage.js 的这两个函数）
const noteStore = {};
const inline = [...d.querySelectorAll('script:not([src])')].map(s => s.textContent).join('\n;\n');
const libs = ['common.js', 'storage.js', 'dict.js', 'annotate.js', 'article.js']
  .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
w.eval(libs + '\n;\n' + inline);
// jsdom 没有 IndexedDB：整层 stub 掉（init 里有 restoreScroll → dbGet(article_progress)）
w.dbAll = async () => [];
w.dbGet = async () => null;
w.dbPut = async () => undefined;
w.dbPutMany = async () => undefined;
w.dbDelete = async () => undefined;
w.getArtNote = async (aid) => noteStore[aid] || '';
w.saveArtNote = async (aid, text) => { noteStore[aid] = text || ''; return true; };
w.confirm = () => true;
w.toast = () => {};
w.alert = () => {};
w.scrollTo = () => {};      // jsdom 未实现，避免噪音堆栈

const problems = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  // init() 已在 article.js 末尾自动跑，等它把正文渲染完
  for (let i = 0; i < 40 && !d.querySelector('.sent, .para, .read-body, .article-body'); i++) await sleep(50);
  await sleep(120);

  const btn = d.getElementById('artNoteBtn');
  const pop = d.getElementById('artNotePop');
  const area = d.getElementById('artNoteArea');
  const dot = d.getElementById('artNoteDot');
  if (!btn) problems.push('顶栏缺少「备注」小块');
  if (!pop) problems.push('缺少备注浮窗');
  if (!area) problems.push('缺少备注输入框');

  // 1. 位置：必须紧跟 .nav-brand（同一个 nav-container 内的下一个元素）
  if (btn) {
    const prev = btn.previousElementSibling;
    if (!prev || !prev.classList.contains('nav-brand')) {
      problems.push('「备注」没有紧贴文章标题，前一个元素是 ' + (prev ? prev.className : '(无)'));
    }
    const navC = btn.parentElement;
    if (!navC || !navC.classList.contains('nav-container')) problems.push('「备注」不在顶栏容器内');
  }

  // 2. 初始：无备注 → 浮窗隐藏、无圆点
  if (pop && !pop.hidden) problems.push('初始浮窗不该展开');
  if (dot && !dot.hidden) problems.push('无备注时不该显示圆点');

  // 3. 点开 → 浮窗可见且锚在按钮下方
  w.toggleArtNote();
  await sleep(20);
  if (pop.hidden) problems.push('点击后浮窗未展开');
  if (pop.style.top) {
    const top = parseFloat(pop.style.top);
    const r = btn.getBoundingClientRect();
    if (!(top > r.top)) problems.push('浮窗未定位在按钮下方: top=' + top);
  }
  if (d.activeElement !== area) problems.push('展开后未自动聚焦输入框');

  // 4. 输入 → 防抖自动保存 + 圆点出现 + 按钮高亮
  area.value = '第 3 段长难句要回看；set sth. aside 是熟词僻义';
  w.onArtNoteInput();
  await sleep(900);
  if (noteStore[AID] !== area.value) problems.push('自动保存未落库: ' + JSON.stringify(noteStore[AID]));
  if (dot.hidden) problems.push('有备注后圆点未显示');
  if (!btn.classList.contains('has-note')) problems.push('有备注后按钮未高亮');

  // 5. 手动保存（Ctrl+Enter 之外）
  w.saveArtNoteNow();
  await sleep(30);
  const meta = d.getElementById('artNoteMeta').textContent;
  if (!/已保存/.test(meta)) problems.push('保存后状态文案异常: ' + meta);

  // 6. 关闭：Esc
  w.artNoteKey({ key: 'Escape', preventDefault() {} });
  await sleep(20);
  if (!pop.hidden) problems.push('Esc 未关闭浮窗');

  // 7. 重开 → 内容回填
  w.toggleArtNote();
  await sleep(20);
  if (area.value !== noteStore[AID]) problems.push('重开后内容未回填');

  // 8. 点面板外关闭
  d.body.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await sleep(20);
  if (!pop.hidden) problems.push('点击面板外未关闭');

  // 9. 清空
  w.toggleArtNote();
  await sleep(20);
  await w.clearArtNote();
  await sleep(30);
  if (noteStore[AID] !== '') problems.push('清空后仍有内容: ' + JSON.stringify(noteStore[AID]));
  if (!dot.hidden) problems.push('清空后圆点未消失');

  // 10. 按文章独立：本篇的能回填，别的篇的不能串进来
  noteStore[AID] = '本篇自己的备注';
  noteStore['en1_2023_cloze'] = '别的文章的备注，不该被读到';
  await w.refreshArtNote();
  if (area.value !== '本篇自己的备注') problems.push('本篇备注未回填: ' + JSON.stringify(area.value));
  if (/别的文章/.test(area.value)) problems.push('回填串号：读到了别的文章的备注');
  if (dot.hidden) problems.push('回填后圆点未显示');
  noteStore[AID] = '';

  if (problems.length) {
    console.log('FAIL ' + problems.length + ' 处:');
    problems.forEach(p => console.log('  - ' + p));
    process.exit(1);
  }
  console.log('article.html 备注 OK：小块紧贴标题 / 浮窗展开·定位·聚焦 / 自动保存 / ' +
    '圆点与高亮 / Esc 与点外关闭 / 重开回填 / 清空 / 按文章独立');
  process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 3).join('\n')); process.exit(1); });
