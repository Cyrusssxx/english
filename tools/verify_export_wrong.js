/* 验证 exportWrong()：英一（en1_ 前缀，走 data/en1/）与英二错题都要能导出来。
 * storage.js 原来只认 ^\d{4} 的 article_id，英一错题会整份漏掉。
 * 用法: node tools/verify_export_wrong.js
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
});
// 英一 2 题 + 英二 2 题，全部答错
const FAKE = [
  { article_id: 'en1_2022_newtype', question_id: 'en1_2022_newtype_q41', user_answer: 'A', is_correct: false },
  { article_id: 'en1_2022_cloze', question_id: 'en1_2022_cloze_q01', user_answer: 'B', is_correct: false },
  { article_id: '2022_text1', question_id: '2022_text1_q1', user_answer: 'C', is_correct: false },
  { article_id: '2022_newtype', question_id: '2022_newtype_q41', user_answer: 'D', is_correct: false },
];
w.eval(['common.js', 'storage.js']
  .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n'));
w.dbAll = async (store) => (store === 'quiz_answers' ? FAKE.slice() : []);

let csv = '';
class FakeBlob {
  constructor(parts) { this.text = parts.join(''); }
}
w.Blob = FakeBlob;
w.URL.createObjectURL = (b) => { csv = b.text; return 'blob:fake'; };
w.URL.revokeObjectURL = () => {};
w.HTMLAnchorElement.prototype.click = function () {};
w.alert = () => {};
if (!w.navigator.clipboard) Object.defineProperty(w.navigator, 'clipboard', { value: null });

(async () => {
  await w.exportWrong();
  const want = ['英一2022新题型-41', '英一2022完形-01', '2022T1-1', '2022新题型-41'];
  const miss = want.filter(t => !csv.includes(t));
  const lines = csv.split('\n').filter(Boolean);
  console.log('CSV 行数（含表头）:', lines.length);
  lines.slice(1).forEach(l => console.log('  ', l.slice(0, 90)));
  if (miss.length) {
    console.log('\nFAIL 缺题号: ' + miss.join(', '));
    process.exit(1);
  }
  if (lines.length !== want.length + 1) {
    console.log('\nFAIL 行数 ' + lines.length + ' != ' + (want.length + 1));
    process.exit(1);
  }
  console.log('\nEXPORT WRONG OK：英一/英二错题均能导出');
  process.exit(0);
})().catch(e => { console.log('ERROR', e.message); process.exit(1); });
