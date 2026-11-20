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

try { window.eval(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')); } catch (e) { /* common 可能依赖 DOM API */ }
try { window.eval(fs.readFileSync(path.join(PWA, 'js/yati.js'), 'utf8')); } catch (e) { fail('脚本执行异常: ' + e.message + '\n' + e.stack); }

const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  await wait(200);
  const data = JSON.parse(yati);
  const total = data.groups.reduce((s, g) => s + g.items.length, 0);

  // 1. 分组
  const grps = [...d.querySelectorAll('.yt-grp')];
  if (grps.length !== data.groups.length) fail('分组数 ' + grps.length + ' != ' + data.groups.length);
  else pass('分组 ' + grps.length + ' 个');

  // 2. 分组顺序（用户要求：单图表→小作文→其它图表→图画）
  const names = grps.map(g => g.querySelector('.yt-grp-name').textContent.trim());
  const expect = ['单图表', '小作文', '图画+图表', '双图表', '单图画', '双图画'];
  if (JSON.stringify(names) !== JSON.stringify(expect)) fail('分组顺序 ' + JSON.stringify(names));
  else pass('分组顺序正确: ' + expect.join(' → '));

  // 3. 默认全部收起
  const openedGrp = grps.filter(g => g.open).length;
  if (openedGrp) fail('默认展开的分组数 ' + openedGrp);
  else pass('6 组默认全部收起');

  // 4. 按需加载：收起状态整页 0 张图请求，展开哪组才载哪组
  const cards = [...d.querySelectorAll('.yt-card')];
  if (cards.length !== total) fail('题卡数 ' + cards.length + ' != ' + total);
  else pass('题卡 ' + total + ' 张');
  const imgs = [...d.querySelectorAll('.yt-thumb img')];
  const withSrc = imgs.filter(i => i.getAttribute('src'));
  const withData = imgs.filter(i => i.getAttribute('data-src'));
  if (withSrc.length) fail('初始就有 ' + withSrc.length + ' 张图发请求（应 0）');
  else if (withData.length !== total) fail('data-src 覆盖 ' + withData.length + ' != ' + total);
  else pass('初始 0 张图请求，' + total + ' 张全部待加载（data-src）');

  const g0 = grps[0];
  g0.open = true;
  window.ytActivateGroup(g0);
  await wait(60);
  const g0src = [...g0.querySelectorAll('.yt-thumb img')].filter(i => i.getAttribute('src'));
  const otherSrc = grps.slice(1).flatMap(g => [...g.querySelectorAll('.yt-thumb img')]).filter(i => i.getAttribute('src'));
  if (g0src.length !== g0src.length || !g0src.length) fail('展开组未加载图片');
  else if (otherSrc.length) fail('未展开组也加载了 ' + otherSrc.length + ' 张');
  else pass(`按需加载：展开「${names[0]}」只载该组 ${g0src.length} 张，其余 ${total - g0src.length} 张未请求`);
  g0.open = false;

  const enCards = cards.filter(c => c.querySelector('.yt-card-en'));
  if (enCards.length !== total) fail('英文题名卡片数 ' + enCards.length + ' != ' + total);
  else pass('每张卡都带英文题名');
  const noWord = cards.filter(c => !/\d+\s*词/.test(c.querySelector('.yt-words').textContent));
  if (noWord.length) fail('词数缺失 ' + noWord.length); else pass('每张卡都有词数');

  // 5. 范文：段落块（非 PDF 硬换行）。大作文必须 3 段且每段成句；小作文按书信/通知格式
  const allItems = data.groups.flatMap(g => g.items);
  const isLetter = it => /Dear |Notice|Minutes/.test((it.blocks[0] || {}).v || '');
  const badBlocks = allItems.filter(it => {
    const ps = (it.blocks || []).filter(b => b.k === 'p');
    if (/\n/.test(it.blocks.map(b => b.v).join(''))) return true;      // 硬换行残留
    if (isLetter(it)) return ps.length < 2;
    return ps.length !== 3 || ps.some(b => b.v.length < 60 || !/[.!?]$/.test(b.v));
  });
  if (badBlocks.length) fail('段落块异常 ' + badBlocks.map(b => b.no).join(','));
  else pass('26 篇范文段落整理正确（大作文均 3 段，无硬换行残留）');

  // 6. 左侧目录
  const toc = d.getElementById('ytToc');
  const links = [...d.querySelectorAll('#ytTocList a[data-t]')];
  if (!toc || !/wr-toc/.test(toc.className)) fail('左侧目录骨架缺失');
  else if (links.length !== data.groups.length) fail('目录链接数 ' + links.length);
  else {
    const bad = links.filter(a => !d.getElementById(a.dataset.t));
    if (bad.length) fail('目录锚点失效 ' + bad.length);
    else pass('左侧目录 ' + links.length + ' 链接均有效');
  }

  // 7. 搜索过滤
  const search = d.getElementById('ytSearch');
  search.value = '绿色';
  search.dispatchEvent(new window.Event('input'));
  await wait(200);
  const visCards = cards.filter(c => !c.hidden);
  const visGrps = grps.filter(g => !g.hidden);
  const expectHit = cards.filter(c => c.dataset.k.indexOf('绿色') >= 0).length;
  if (!expectHit) fail('测试词「绿色」无命中');
  else if (visCards.length !== expectHit) fail('搜索命中卡片 ' + visCards.length + ' != ' + expectHit);
  else if (visGrps.some(g => !g.open)) fail('搜索时命中分组未自动展开');
  else pass(`搜索「绿色」命中 ${expectHit} 题并自动展开分组`);
  search.value = '';
  search.dispatchEvent(new window.Event('input'));
  await wait(200);
  if (cards.some(c => c.hidden)) fail('清空搜索后卡片仍隐藏');
  else if (grps.some(g => g.open)) fail('清空搜索后分组未回到收起');
  else pass('清空搜索：全部恢复且默认收起');

  // 8. 弹层阅读器：打开 → 内容 → 上一题/下一题 → Esc
  const card17 = cards.find(c => c.dataset.no === '17');
  card17.dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  const modal = d.getElementById('ytModal');
  if (modal.hidden) fail('点击卡片未打开弹层');
  else pass('点击卡片打开弹层');
  const it17 = data.groups.flatMap(g => g.items).find(i => i.no === 17);
  if (d.getElementById('ytMTitle').textContent !== it17.title) fail('弹层标题不符');
  else pass('弹层标题 = ' + it17.title);
  if (d.getElementById('ytMImg').getAttribute('src') !== it17.img) fail('弹层图片不符');
  else pass('弹层图片与数据一致');
  if (d.getElementById('ytMEn').textContent !== it17.en) fail('弹层英文题名不符: ' + d.getElementById('ytMEn').textContent);
  else pass('弹层英文题名 = ' + it17.en);
  const noteEls = d.querySelectorAll('.yt-notes .yt-note');
  if (noteEls.length !== it17.notes.length) fail('图注对照条数 ' + noteEls.length + ' != ' + it17.notes.length);
  else pass(`图内中文 → 英文对照 ${noteEls.length} 条`);
  const ps = d.querySelectorAll('#ytMEssay .yt-en > p');
  const expectP = it17.blocks.filter(b => b.k === 'p').length;
  if (ps.length !== it17.blocks.length) fail('弹层段落数 ' + ps.length + ' != ' + it17.blocks.length);
  else pass(`弹层范文 ${ps.length} 段（其中正文 ${expectP} 段）`);
  if (/^\s*\d+\s*\/\s*26/.test(d.getElementById('ytMCnt').textContent) === false) fail('计数显示 ' + d.getElementById('ytMCnt').textContent);
  else pass('计数器 ' + d.getElementById('ytMCnt').textContent);
  d.getElementById('ytNext').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  if (d.getElementById('ytMTitle').textContent !== data.groups.flatMap(g => g.items).find(i => i.no === 18).title) fail('下一题跳转错误');
  else pass('下一题 → 第 18 题');
  d.getElementById('ytPrev').dispatchEvent(new window.MouseEvent('click', { bubbles: true }));
  d.dispatchEvent(new window.KeyboardEvent('keydown', { key: 'Escape' }));
  if (!modal.hidden) fail('Esc 未关闭弹层'); else pass('Esc 关闭弹层');

  // 9. 导航
  const navYati = d.querySelector('.nav-link[href="yati.html"]');
  if (!navYati || !navYati.classList.contains('active')) fail('顶栏押题入口缺失/未高亮');
  else pass('顶栏押题入口存在且当前页高亮');

  console.log(ok ? '\nYATI DOM ALL PASS' : '\nYATI DOM HAS FAILURES');
  process.exit(ok ? 0 : 1);
})();
