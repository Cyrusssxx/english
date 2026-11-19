/* 静态验证 recite 页：数据完整性 + HTML/JS 引用一致性。 */
const fs = require('fs');
const path = require('path');
const PWA = path.join(__dirname, '..', 'pwa');
let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

// 1. 词库数据
const data = JSON.parse(fs.readFileSync(path.join(PWA, 'data/writing_words.json'), 'utf8'));
if (!data.groups || data.groups.length < 5) fail('groups 数量'); else pass('groups = ' + data.groups.length);
let total = 0;
const ids = new Set();
data.groups.forEach((g, i) => {
  if (!g.id || ids.has(g.id)) fail('group id 重复/缺失: ' + g.id);
  ids.add(g.id);
  if (!g.items || !g.items.length) fail('group 无 items: ' + g.id);
  g.items.forEach(it => {
    total++;
    if (!it.en || !it.cn) fail('词条缺 en/cn: ' + JSON.stringify(it));
    if (/^\s|\s$/.test(it.en)) fail('词条 en 有首尾空格: ' + it.en);
    if (/[<>"]/.test(it.en + it.cn)) fail('词条含未转义尖括号/引号: ' + it.en);
  });
});
pass('items 总数 = ' + total);

// 2. HTML 引用
const html = fs.readFileSync(path.join(PWA, 'recite.html'), 'utf8');
['js/dict.js', 'js/recite.js', 'css/style.css'].forEach(f => {
  if (!html.includes(f)) fail('HTML 未引用 ' + f);
  if (!fs.existsSync(path.join(PWA, f))) fail('引用文件不存在 ' + f);
});
pass('HTML 资源引用齐全');
if (html.includes('rcBig') || html.includes('rcSmall') || html.includes('30 天') || html.includes('句池'))
  fail('HTML 仍残留旧速记内容');
else pass('旧速记内容已从 HTML 移除');
if (!html.includes('wr-toc') || !html.includes('rcTocList')) fail('缺左侧目录 wr-toc 骨架');
else pass('左侧目录骨架存在');
// 导航 10 项
const navCount = (html.match(/class="nav-link(?: active)?"/g) || []).length;
if (navCount !== 11) fail('导航项数量 = ' + navCount); else pass('导航 11 项（含押题）');

// 3. JS 关键函数存在 + 无旧逻辑残留
const js = fs.readFileSync(path.join(PWA, 'js/recite.js'), 'utf8');
['rcRender', 'rcTocBuild', 'rcTocToggleFold', 'rcTocOpen', 'rcWordPop', 'toggleDark', 'writing_words.json'].forEach(s => {
  if (!js.includes(s)) fail('JS 缺 ' + s);
});
// 剥离注释后再判断，避免"已移除"的说明注释造成误报
const jsCode = js.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
if (/'rc_mk_v1'|rcToc\(\)|rcBuild|rcSecSkeleton|30 天背诵计划|RC_MK_SEL/.test(jsCode))
  fail('JS 仍残留旧逻辑代码');
else pass('JS 旧逻辑已清理');

// 4. 数据文件会被 SW 收录（build_sw 收 data/**/*.json）
const sw = fs.readFileSync(path.join(PWA, 'sw.js'), 'utf8');
if (!sw.includes('writing_words.json')) fail('SW 未缓存词库数据');
else pass('SW 已缓存词库数据');

// 5. CSS 新类
const css = fs.readFileSync(path.join(PWA, 'css/style.css'), 'utf8');
['.wr-toc', '.wr-toc-fold', '.wr-toc-list', '.wr-layout', '.rcw-grid', '.rcw-row'].forEach(s => {
  if (!css.includes(s)) fail('CSS 缺 ' + s);
});
pass('CSS 词库样式齐全');

console.log(ok ? '\nALL PASS' : '\nHAS FAILURES');
process.exit(ok ? 0 : 1);
