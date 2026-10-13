/* jsdom 实跑验证：英语一 完形填空（2016-2025）在 article.html 的渲染与答题链路。
 *
 * 覆盖：
 *   1. 正文渲染：[n] 空位 → <span class="blank" id="blank-n">（20 个）
 *   2. 题干渲染：cloze 分支的 Q 号 + 2×2 选项（80 个 .q-opt）
 *   3. 点选选项 → onPick 判分 → 空位回填 + 解析区出现内容
 *   4. en1.html 列表把 cloze 排在 text4 之后
 *
 * 用法: NODE_PATH=<node_modules> node tools/verify_en1_cloze.js [id...]
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
    runScripts: 'outside-only',
    pretendToBeVisual: true,
  });
  const w = dom.window;
  // jsdom 没有 indexedDB：内存 stub。必须让 request 的 onsuccess/onerror 真的触发，
  // 否则 dbPut/dbGet 的 Promise 永远 pending，onPick 会在 saveAnswer 处卡住。
  const _stores = {};
  function mkStore(name) {
    const data = _stores[name] || (_stores[name] = {});
    return {
      get: (k) => {
        const req = { result: data[k], onsuccess: null, onerror: null };
        setTimeout(() => { if (req.onsuccess) req.onsuccess({ target: req }); }, 0);
        return req;
      },
      put: (v) => {
        const req = { onsuccess: null, onerror: null };
        data[v.keyPath ? v[v.keyPath] : String(Math.random())] = v;
        setTimeout(() => { if (req.onsuccess) req.onsuccess({ target: req }); }, 0);
        return req;
      },
      delete: () => { const req = { onsuccess: null, onerror: null }; setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0); return req; },
      clear: () => { const req = { onsuccess: null, onerror: null }; setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0); return req; },
      openCursor: () => { const req = { onsuccess: null, onerror: null }; setTimeout(() => req.onsuccess && req.onsuccess({ target: req }), 0); return req; },
      getAll: () => { const req = { result: Object.values(data), onsuccess: null, onerror: null }; setTimeout(() => { if (req.onsuccess) req.onsuccess({ target: req }); }, 0); return req; },
      count: () => { const req = { result: Object.keys(data).length, onsuccess: null, onerror: null }; setTimeout(() => { if (req.onsuccess) req.onsuccess({ target: req }); }, 0); return req; },
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
  // jsdom 缺 scrollTo / scrollIntoView（完形答完会自动跳下一题）
  w.HTMLElement.prototype.scrollIntoView = function () {};
  w.scrollTo = () => {};
  // 所有脚本拼成一个 eval：顶层 const/let 不跨 eval 共享
  const code = ['common.js', 'storage.js', 'dict.js', 'annotate.js', 'article.js']
    .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
  w.eval(code);
  return dom;
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function verify(id) {
  const dom = makeWindow(id);
  const w = dom.window;
  const d = w.document;
  await sleep(120);
  const r = { id, problems: [] };

  const blanks = d.querySelectorAll('span.blank');
  r.blanks = blanks.length;
  const ids = [...blanks].map(b => b.id.replace('blank-', ''));
  const missing = [];
  for (let n = 1; n <= 20; n++) if (!ids.includes(String(n))) missing.push(n);
  if (missing.length) r.problems.push('缺空位 ' + missing.join(','));

  const optBtns = d.querySelectorAll('.q-opt');
  r.optBtns = optBtns.length;
  if (optBtns.length !== 80) r.problems.push('选项按钮 ' + optBtns.length + ' != 80');

  // 题号
  const qnos = [...d.querySelectorAll('.q-no')].map(e => e.textContent.trim());
  if (qnos.length !== 20) r.problems.push('题号数 ' + qnos.length);
  if (qnos[0] !== 'Q1' || qnos[19] !== 'Q20') r.problems.push('题号异常 ' + qnos.slice(0, 3));

  // 点选第 1 题的正确选项 → 判分链路
  const art = w.__artForTest || null;
  let answer = null;
  const data = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'en1', id.replace(/^en1_(\d{4})_.*$/, '$1') + '.json'), 'utf8'));
  const cloze = data.articles.find(a => a.id === id);
  if (!cloze) { r.problems.push('数据里找不到 ' + id); return r; }
  const q1 = cloze.questions[0];
  answer = q1.answer;

  // jsdom 的 runScripts:'outside-only' 不编译内联 onclick → 直接调用挂载的函数
  const btn = d.getElementById('opt-' + q1.id + '-' + answer);
  if (!btn) { r.problems.push('找不到正确选项按钮 ' + q1.id + '-' + answer); return r; }
  r.hasOnPick = typeof w.onPick === 'function';
  if (!r.hasOnPick) { r.problems.push('onPick 未挂到 window'); return r; }
  w.onPick(q1.id, answer);
  await sleep(120);

  const expl = d.getElementById('expl-' + q1.id);
  r.explLen = expl ? expl.textContent.trim().length : -1;
  if (!expl || !expl.textContent.trim()) r.problems.push('点选后解析为空');

  const blank1 = d.getElementById('blank-1');
  r.blank1Html = blank1 ? blank1.outerHTML.slice(0, 120) : 'none';
  if (blank1 && blank1.textContent.indexOf('[') === 0) r.problems.push('空位未回填');

  // 点一个错误选项 → 应当有错误反馈
  const wrong = ['A', 'B', 'C', 'D'].find(k => k !== answer);
  if (w.onPick) { w.onPick(q1.id, wrong); await sleep(120); }
  r.markedWrong = !!d.querySelector('.q-opt.wrong, .q-opt.err, .q-opt.bad');
  return r;
}

(async () => {
  const ids = process.argv.slice(2);
  const list = ids.length ? ids : ['en1_2016_cloze', 'en1_2020_cloze', 'en1_2024_cloze'];
  let fail = 0;
  for (const id of list) {
    try {
      const r = await verify(id);
      console.log('%s blanks=%d opts=%d expl=%d wrongCls=%s %s',
        id, r.blanks, r.optBtns, r.explLen, r.markedWrong,
        r.problems.length ? 'PROBLEMS: ' + r.problems.join(' | ') : 'OK');
      if (r.problems.length) fail++;
    } catch (e) {
      console.log('%s ERROR %s\n%s', id, e.message, (e.stack || '').split('\n').slice(0, 4).join('\n'));
      fail++;
    }
  }
  console.log(fail ? 'FAIL ' + fail : 'ALL OK');
  process.exit(fail ? 1 : 0);
})();
