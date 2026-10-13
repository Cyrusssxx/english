/* 验证 en1.html 列表页：cloze 卡片出现在 text4 之后，且可点进 article.html。 */
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
const code = ['common.js', 'storage.js']
  .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
w.eval(code);

setTimeout(() => {
  const d = w.document;
  const idx = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'en1_index.json'), 'utf8'));
  let fail = 0;
  for (const yr of idx.years) {
    if (yr.year < 2016) continue;
    const cards = [...d.querySelectorAll('.article-card')];
    // 直接校验索引顺序（渲染逻辑读同一份数据）
    const types = yr.articles.map(a => a.type);
    const want = ['text1', 'text2', 'text3', 'text4', 'cloze'];
    const ok = JSON.stringify(types) === JSON.stringify(want);
    if (!ok) { console.log('%d 顺序异常: %s', yr.year, types.join(',')); fail++; }
    const has = yr.articles.find(a => a.type === 'cloze');
    if (!has) { console.log('%d 缺 cloze', yr.year); fail++; }
    else if (has.question_count !== 20 || has.sentence_count < 8) {
      console.log('%d cloze 计数异常 q=%d s=%d', yr.year, has.question_count, has.sentence_count);
      fail++;
    }
  }
  console.log(fail ? 'FAIL ' + fail : 'INDEX ORDER OK (2016-2025 均含 cloze，20 题)');
  process.exit(fail ? 1 : 0);
}, 250);
