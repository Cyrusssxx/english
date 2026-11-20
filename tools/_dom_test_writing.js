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

    /* ---------- 第三段：三套骨架并入一卡 + 一份共用句池 ---------- */
    const p3 = TPL.sections.find(s => s.id === 'para3_positive');
    const p3card = d.getElementById('para3_positive');
    if (!p3card) fail('第三段主卡未渲染（#para3_positive）');
    else pass('第三段主卡已渲染');

    // 负面/中性不再单独出卡，但数据仍在（apply 链路要按 id 取句）
    for (const sid of ['para3_negative', 'para3_neutral']) {
        if (d.getElementById(sid)) fail(`${sid} 仍单独出卡（应并入主卡）`);
        if (!TPL.sections.some(s => s.id === sid)) fail(`${sid} 被从数据里删掉了（apply 链路会断）`);
    }
    if (!d.getElementById('para3_negative') && !d.getElementById('para3_neutral')
        && TPL.sections.some(s => s.id === 'para3_neutral')) {
        pass('负面 / 中性版不再单独出卡，数据保留给套用链路');
    }

    // 三套骨架前移并列
    const skels = p3card ? p3card.querySelectorAll('.wr-skel') : [];
    if (skels.length !== 3) fail(`第三段骨架卡 ${skels.length} 套，应为 3`);
    else pass('三套骨架并列前移（正面 / 负面 / 中性）');
    const skelLabels = [...skels].map(x => (x.querySelector('.wr-skel-label') || {}).textContent || '');
    if (!/正面/.test(skelLabels[0] || '') || !/负面/.test(skelLabels[1] || '') || !/中性/.test(skelLabels[2] || ''))
        fail('骨架顺序不对: ' + skelLabels.join(' | '));
    else pass('骨架顺序 = 正面 → 负面 → 中性');

    // 句池只有一份（主卡），条数 = pool_all
    const p3groups = p3card ? p3card.querySelectorAll('.wr-pool-group') : [];
    const want3 = (p3.pool_groups || []).length;
    if (p3groups.length !== want3) fail(`第三段句池分 ${p3groups.length} 组，应为 ${want3}`);
    else pass(`第三段句池分 ${p3groups.length} 组`);
    const p3total = p3card ? p3card.querySelectorAll('.wr-sent').length : 0;
    if (p3total !== (p3.pool_all || []).length) fail(`第三段句池 ${p3total} 条，应为 ${(p3.pool_all || []).length}`);
    else pass(`第三段只有一份句池，共 ${p3total} 条（不再三份重复）`);
    const p3names = [...p3groups].map(g => (g.querySelector('.wr-pool-name') || {}).textContent || '');
    if (p3names.includes('其他')) fail('第三段出现「其他」兜底组');
    else pass('第三段无「其他」兜底组');
    if (p3names.join('|') !== (p3.pool_groups || []).map(g => g.name).join('|'))
        fail('第三段组顺序不符: ' + p3names.join('|'));
    else pass('第三段组顺序 = ' + p3names.join(' → '));

    // 语气徽标：正 / 负 / 通用，且与数据一致
    const sides = [...(p3card ? p3card.querySelectorAll('.wr-side') : [])].map(x => x.textContent.trim());
    const wantSides = (p3.pool_all || []).map(x => x.side);
    if (sides.length !== wantSides.length) fail(`语气徽标 ${sides.length} 个，应为 ${wantSides.length}`);
    else if (sides.slice().sort().join('') !== wantSides.slice().sort().join(''))
        fail('语气徽标与数据 side 不一致');
    else pass('每条句都标了语气（正 / 负 / 通用）');

    console.log(ok ? '\nWRITING ALL PASS' : '\nWRITING FAIL');
    process.exit(ok ? 0 : 1);
})();
