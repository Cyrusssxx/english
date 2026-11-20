/* DOM 验证写作页：第二段弹药句池「分类」渲染
   - 8 个分组全部渲染、无「其他」兜底组
   - 40 条一句不丢，组内按 fit 降序
   - 组头带用途说明与条数徽标
   - 其他段落（无 pool_groups）仍平铺，不被误分组 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const html = fs.readFileSync(path.join(PWA, 'writing.html'), 'utf8');
const read = p => fs.readFileSync(path.join(PWA, p), 'utf8');
const DATA = {
  'data/writing_templates.json': read('data/writing_templates.json'),
  'data/writing_apply.json': read('data/writing_apply.json'),
  'data/writing_keywords.json': read('data/writing_keywords.json'),
  'data/dict.json': read('data/dict.json'),
  'data/wordnotes.json': read('data/wordnotes.json'),
  'data/writing_apply_marks.json': read('data/writing_apply_marks.json'),
  'data/writing_words.json': read('data/writing_words.json'),
};
const TPL = JSON.parse(DATA['data/writing_templates.json']);

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);

const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/writing.html', pretendToBeVisual: true });
const { window } = dom;
window.fetch = url => {
    const key = String(url).split('?')[0];
    const body = DATA[key];
    return Promise.resolve({
        ok: body != null,
        status: body != null ? 200 : 404,
        json: () => Promise.resolve(body != null ? JSON.parse(body) : {}),
        text: () => Promise.resolve(body || ''),
    });
};
const nav = window.document.querySelector('.navbar');
if (nav) nav.dataset.collapsed = '0';

for (const f of ['js/common.js', 'js/dict.js', 'js/storage.js', 'js/kwpop.js', 'js/writing.js']) {
    try { window.eval(read(f)); } catch (e) { fail(`${f} 执行异常: ${e.message}`); }
}

const d = window.document;
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
    await wait(600);                       // 等 initWriting 异步完成

    const p2 = TPL.sections.find(s => s.id === 'para2_why');
    const card = d.getElementById('para2_why');
    if (!card) { fail('第二段卡片未渲染（#para2_why）'); }
    else pass('第二段卡片已渲染');

    const groups = card ? card.querySelectorAll('.wr-pool-group') : [];
    const expectG = (p2.pool_groups || []).length;
    if (groups.length !== expectG) fail(`分组数 ${groups.length}，应为 ${expectG}`);
    else pass(`句池分 ${groups.length} 组，与真源一致`);

    // 组名顺序与真源一致
    const names = [...groups].map(g => (g.querySelector('.wr-pool-name') || {}).textContent || '');
    const want = (p2.pool_groups || []).map(g => g.name);
    if (names.join('|') !== want.join('|')) fail('组顺序不符: ' + names.join('|') + ' ≠ ' + want.join('|'));
    else pass('组顺序 = ' + names.join(' → '));

    // 无「其他」兜底组
    if (names.includes('其他')) fail('出现「其他」兜底组，说明有句子没归类');
    else pass('无「其他」兜底组（40 条全部有归属）');

    // 每组的条数徽标与实际句子数一致
    const cntBad = [];
    let total = 0;
    groups.forEach((g, i) => {
        const n = g.querySelectorAll('.wr-sent').length;
        const badge = (g.querySelector('.wr-pool-n') || {}).textContent || '';
        total += n;
        if (String(n) !== badge.trim()) cntBad.push(`${names[i]}: 渲染 ${n} / 徽标 ${badge}`);
        if (!(g.querySelector('.wr-pool-desc') || {}).textContent) cntBad.push(`${names[i]}: 缺用途说明`);
    });
    if (cntBad.length) fail('组头/条数不符: ' + cntBad.join('; '));
    else pass('每组条数徽标与用途说明齐备');

    const n2 = (p2.sentences || []).length;
    if (total !== n2) fail(`句池渲染 ${total} 条，应为 ${n2}`);
    else pass(`40 条一句不丢（共 ${total} 条）`);

    // 组内 fit 降序
    const orderBad = [];
    groups.forEach((g, i) => {
        const tagOfNo = {};
        (p2.sentences || []).forEach(s => { tagOfNo[s.tag] = s.fit ?? 0; });
        const fits = [...g.querySelectorAll('.wr-tag')].map(t => tagOfNo[t.textContent] ?? -1);
        for (let k = 1; k < fits.length; k++) if (fits[k] > fits[k - 1]) orderBad.push(`${names[i]} 第${k + 1}条 fit ${fits[k]} > 上一条 ${fits[k - 1]}`);
    });
    if (orderBad.length) fail('组内未按 fit 降序: ' + orderBad.join('; '));
    else pass('各组组内均按 fit 降序');

    // 全局编号连续不重复（分组后不能每组都从 1 开始）
    const nos = [...card.querySelectorAll('.wr-sent-no')].map(x => x.textContent.trim());
    const uniq = new Set(nos);
    if (nos.length !== uniq.size) fail(`编号重复：${nos.length} 个编号只有 ${uniq.size} 个不同`);
    else pass(`编号全局连续 1~${nos.length}`);

    // 没有 pool_groups 的段落仍平铺
    const flat = d.getElementById('chart_static');
    if (!flat) fail('#chart_static 未渲染');
    else if (flat.querySelector('.wr-pool-group')) fail('chart_static 被误分组');
    else pass('第一段句池仍平铺（无 pool_groups 不分组）');

    console.log(ok ? '\nWRITING ALL PASS' : '\nWRITING FAIL');
    process.exit(ok ? 0 : 1);
})();
