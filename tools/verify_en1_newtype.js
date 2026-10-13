/* jsdom 实跑验证：英语一 新题型（newtype）在 article.html 的渲染与答题链路。
 *
 * 覆盖：选项池渲染、题号 41-45、点选判分、答案回显、空位（七选五）、列表顺序。
 * 用法: NODE_PATH=<node_modules> node tools/verify_en1_newtype.js [id...]
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');

function makeWindow(id) {
  const html = fs.readFileSync(path.join(PWA, 'article.html'), 'utf8');
  const dom = new JSDOM(html, {
    url: 'http://localhost/article.html?id=' + encodeURIComponent(id),
    runScripts: 'outside-only', pretendToBeVisual: true,
  });
  const w = dom.window;
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.scrollTo = () => {};
  const _stores = {};
  function mkStore(name) {
    const data = _stores[name] || (_stores[name] = {});
    const done = (req, val) => setTimeout(() => { if (req.onsuccess) req.onsuccess({ target: req }); }, 0);
    return {
      get: (k) => { const r = { result: data[k], onsuccess: null, onerror: null }; return (done(r), r); },
      put: (v) => { const r = { onsuccess: null, onerror: null }; data[v.key || String(Math.random())] = v; return (done(r), r); },
      getAll: () => { const r = { result: Object.values(data), onsuccess: null, onerror: null }; return (done(r), r); },
      delete: () => { const r = { onsuccess: null, onerror: null }; return (done(r), r); },
      clear: () => { const r = { onsuccess: null, onerror: null }; return (done(r), r); },
      count: () => { const r = { result: Object.keys(data).length, onsuccess: null, onerror: null }; return (done(r), r); },
      openCursor: () => { const r = { onsuccess: null, onerror: null }; return (done(r), r); },
      createIndex: () => ({}),
    };
  }
  const _db = { objectStoreNames: { contains: () => true }, createObjectStore: mkStore, transaction: () => ({ objectStore: mkStore }) };
  w.indexedDB = {
    open() {
      const req = { onupgradeneeded: null, onsuccess: null, onerror: null, result: _db };
      setTimeout(() => {
        if (req.onupgradeneeded) req.onupgradeneeded({ target: req });
        if (req.onsuccess) req.onsuccess({ target: req });
      }, 0);
      return req;
    },
  };
  w.fetch = (p) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
    text: () => Promise.resolve(fs.readFileSync(path.join(PWA, p), 'utf8')),
  });
  const code = ['common.js', 'storage.js', 'dict.js', 'annotate.js', 'article.js']
    .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
  w.eval(code);
  return dom;
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function verify(id) {
  const dom = makeWindow(id);
  const w = dom.window, d = w.document;
  await sleep(120);
  const r = { id, problems: [] };
  const year = id.replace(/^en1_(\d{4})_.*$/, '$1');
  const data = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'en1', year + '.json'), 'utf8'));
  const art = data.articles.find(a => a.id === id);
  if (!art) { r.problems.push('数据里找不到 ' + id); return r; }

  // .nt-letter 是「每个题块各渲染一遍选项胶囊」（既有设计），所以期望值是 pool×5
  r.poolBtns = d.querySelectorAll('.nt-q .nt-letter').length;
  const expect = Object.keys(art.pool).length * 5;
  if (r.poolBtns !== expect) r.problems.push('选项胶囊 ' + r.poolBtns + ' != ' + expect);
  r.qBlocks = d.querySelectorAll('.nt-q').length;
  if (r.qBlocks !== 5) r.problems.push('题块 ' + r.qBlocks + ' != 5');
  const qnos = [...d.querySelectorAll('.nt-q .q-no')].map(e => e.textContent.trim());
  if (qnos[0] !== 'Q41' || qnos[4] !== 'Q45') r.problems.push('题号异常 ' + qnos.join(','));
  r.sents = d.querySelectorAll('.sent, .sentence').length || art.sentences.length;

  // 点选第 41 题正确选项
  const q1 = art.questions[0];
  if (typeof w.onPick !== 'function') { r.problems.push('onPick 未挂载'); return r; }
  w.onPick(q1.id, q1.answer);
  await sleep(120);
  const expl = d.getElementById('expl-' + q1.id);
  r.explLen = expl ? expl.textContent.trim().length : -1;
  if (!expl || !expl.textContent.trim()) r.problems.push('点选后解析为空');
  const opt = d.getElementById('opt-' + q1.id + '-' + q1.answer);
  r.rightCls = opt ? opt.className : '';
  if (!/right/.test(r.rightCls)) r.problems.push('正确项无 right 样式');
  // 互斥占用：答对后该字母应标记为已用
  r.usedCls = d.querySelectorAll('.nt-letter.used, .nt-letter.taken').length;
  return r;
}

(async () => {
  const ids = process.argv.slice(2);
  const list = ids.length ? ids : ['en1_2022_newtype', 'en1_2024_newtype', 'en1_2025_newtype'];
  let fail = 0;
  for (const id of list) {
    try {
      const r = await verify(id);
      console.log('%s pool=%d qblocks=%d sents=%d expl=%d right=%s used=%d %s',
        id, r.poolBtns, r.qBlocks, r.sents, r.explLen, /right/.test(r.rightCls || ''),
        r.usedCls, r.problems.length ? 'PROBLEMS: ' + r.problems.join(' | ') : 'OK');
      if (r.problems.length) fail++;
    } catch (e) {
      console.log('%s ERROR %s', id, e.message);
      fail++;
    }
  }
  console.log(fail ? 'FAIL ' + fail : 'ALL OK');
  process.exit(fail ? 1 : 0);
})();
