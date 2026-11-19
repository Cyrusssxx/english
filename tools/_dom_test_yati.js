/* 真实 DOM 验证 yati 押题页：jsdom 加载 HTML + 执行 yati.js，mock fetch 返回真实 yati.json。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'yati.html'), 'utf8');
const yati = fs.readFileSync(path.join(PWA, 'data/yati.json'), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/yati.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = url => {
  let body = null;
  if (url.indexOf('yati.json') >= 0) body = yati;
  return Promise.resolve({ ok: body !== null, status: body !== null ? 200 : 404, json: () => Promise.resolve(JSON.parse(body || '{}')) });
};
window.document.querySelector('.navbar').dataset.collapsed = '0';

const js = fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8');
try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) { /* common 可能依赖 DOM API */ }
try { window.eval(js); } catch (e) { fail('脚本执行异常: ' + e.message + '\n' + e.stack); }

const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(200);
  const data = JSON.parse(yati);
  const total = data.groups.reduce((s, g) => s + g.items.length, 0);
  // 1. 分组与卡片
  const groups = d.querySelectorAll('.yt-group');
  if (groups.length !== data.groups.length) fail('分组数 ' + groups.length + ' != ' + data.groups.length);
  else pass('分组 ' + groups.length + ' 个');
  const cards = d.querySelectorAll('details.yt-card');
  if (cards.length !== total) fail('题卡数 ' + cards.length + ' != ' + total);
  else pass('题卡 ' + total + ' 张');
  // 2. 分组顺序（用户要求）
  const order = [...groups].map(g => g.querySelector('.yt-group-h').textContent.replace(/\d|题|\s/g, '').trim());
  const expect = ['单图表', '小作文', '图画+图表', '双图表', '单图画', '双图画'];
  if (JSON.stringify(order) !== JSON.stringify(expect)) fail('分组顺序 ' + JSON.stringify(order));
  else pass('分组顺序正确: ' + expect.join(' → '));
  // 3. 默认全部收起
  const opened = [...cards].filter(c => c.open).length;
  if (opened) fail('默认展开题卡数 ' + opened);
  else pass('26 题卡默认全部收起');
  // 4. 图片与范文
  const imgs = d.querySelectorAll('.yt-fig img[data-src]');
  if (imgs.length !== total) fail('图片数 ' + imgs.length);
  else pass('图片 ' + imgs.length + ' 张（含 src）');
  const essays = [...d.querySelectorAll('.yt-essay-body')].filter(e => e.textContent.trim().length > 50);
  if (essays.length !== total) fail('范文数 ' + essays.length);
  else pass('范文 ' + essays.length + ' 篇（均 >50 字符）');
  // 5. 左侧目录
  const toc = d.getElementById('ytToc');
  const links = [...d.querySelectorAll('#ytTocList a[data-t]')];
  if (!toc || !/wr-toc/.test(toc.className)) fail('左侧目录骨架缺失');
  else if (links.length !== data.groups.length) fail('目录链接数 ' + links.length);
  else {
    const bad = links.filter(a => !d.getElementById(a.dataset.t));
    if (bad.length) fail('目录锚点失效 ' + bad.length);
    else pass('左侧目录 ' + links.length + ' 链接均有效');
  }
  // 6. 导航含押题
  const navYati = d.querySelector('.nav-link[href="yati.html"]');
  if (!navYati || !navYati.classList.contains('active')) fail('顶栏押题入口缺失/未高亮');
  else pass('顶栏押题入口存在且当前页高亮');

  console.log(ok ? '\nYATI DOM ALL PASS' : '\nYATI DOM HAS FAILURES');
  process.exit(ok ? 0 : 1);
})();
