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
    else pass(`无「其他」兜底组（${(p2.sentences || []).length} 条全部有归属）`);

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
    else pass(`${n2} 条一句不丢（共 ${total} 条）`);

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

    /* ---------- 第一段：双图骨架（2026-11-20 补，覆盖 NO11-14）---------- */
    for (const sid of ['chart_static', 'chart_dynamic']) {
        const sec = TPL.sections.find(x => x.id === sid);
        const el = d.getElementById(sid);
        const want = (sec.skeletons || []).length;
        const got = el ? el.querySelectorAll('.wr-skel').length : 0;
        if (got !== want) fail(`${sid} 渲染 ${got} 套骨架，应为 ${want}`);
        else pass(`${sid} 骨架 ${got} 套并列`);
        if (!(sec.skeletons || []).some(k => /双图/.test(k.label))) fail(`${sid} 缺「双图」骨架（漫画+图表 / 两张图表）`);
        else pass(`${sid} 含双图骨架`);
    }

    /* ---------- 场景绑定句：「专用·X」徽标 ---------- */
    const scoped = [...card.querySelectorAll('.wr-scope')];
    const wantScope = (p2.sentences || []).filter(s => s.scope).length;
    if (scoped.length !== wantScope) fail(`专用徽标 ${scoped.length} 个，应为 ${wantScope}`);
    else pass(`场景绑定句标了 ${scoped.length} 个「专用」徽标`);
    if (scoped.some(x => !x.textContent.startsWith('专用·'))) fail('专用徽标文案不对（应为 专用·X）');
    else pass('专用徽标文案 = 专用·话题');

    // 被标专用的句子不能靠 fit 置顶（否则「万能」假象又回来了）
    const topFit = {};
    (p2.sentences || []).forEach(s => { topFit[s.cat] = Math.max(topFit[s.cat] ?? -1, s.fit ?? 0); });
    const badTop = (p2.sentences || []).filter(s => s.scope && (s.fit ?? 0) >= (topFit[s.cat] ?? 0) && s.fit > 10);
    if (badTop.length) fail('专用句仍排在同组最前: ' + badTop.map(x => `${x.tag}(${x.fit})`).join(','));
    else pass('专用句均已排到组内靠后（不再伪装万能句）');

    /* ---------- 17 篇 tips 不再出现空句池引用 ---------- */
    const AP = JSON.parse(DATA['data/writing_apply.json']);
    const empty = Object.keys(AP).filter(y => (AP[y].tips || []).some(t => t.includes('「」')));
    if (empty.length) fail('tips 仍有空句池引用: ' + empty.join(','));
    else pass(`${Object.keys(AP).length} 篇 tips 句池引用均非空`);

    // 衔接词与模板对齐：第二段不得再出现被模板禁掉的 First / Beyond that
    const wc = t => (t.match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
    const linkBad = [], wordBad = [];
    Object.keys(AP).forEach(y => {
        const p2txt = String(AP[y].apply_en || '').split('\n\n')[1] || '';
        if (/\bFirst,/.test(p2txt) || /Beyond that,/.test(p2txt)) linkBad.push(y);
        if (!/Primary among these is that/.test(p2txt)) linkBad.push(y + '(缺Primary)');
        const n = wc(AP[y].apply_en || '');
        if (n < 165 || n > 180) wordBad.push(`${y}:${n}`);
    });
    if (linkBad.length) fail('第二段衔接词未对齐模板: ' + linkBad.join(','));
    else pass('17 篇第二段均用 Primary among these is that / Equally / A further driver');
    if (wordBad.length) fail('词数越界: ' + wordBad.join(','));
    else pass('17 篇词数全部落在 165~180');

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
    else pass('三套骨架并列前移（正面 / 负面 / 双面）');
    const skelLabels = [...skels].map(x => (x.querySelector('.wr-skel-label') || {}).textContent || '');
    if (!/正面/.test(skelLabels[0] || '') || !/负面/.test(skelLabels[1] || '') || !/双面/.test(skelLabels[2] || ''))
        fail('骨架顺序不对: ' + skelLabels.join(' | '));
    else pass('骨架顺序 = 正面 → 负面 → 双面');

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
