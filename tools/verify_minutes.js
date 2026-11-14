/* 小作文「会议纪要（minutes）」回归：
 * 1) 数据层：新增 4 句 + 第 11 类，但不得改变 ⭐必背/⭐⭐骨架 口径（24 句额度不动）；
 * 2) 拼装层：标题 = Minutes、无称呼、落款 = Minutes recorder: Li Ming（不出现 Yours sincerely）；
 * 3) 回归：10 类原有书信的称呼/落款不受影响；
 * 4) 稳定性：新句追加在 banks 末尾，既有高亮键（bank#idx → 稳定序号）不得位移。
 * 注：smallwriting.js 的 SW 是 let 声明，不挂 window；故数据走文件、渲染走 window 上的函数。
 * 用法: node tools/verify_minutes.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');
const problems = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- 数据层：直接读 JSON ----------
const DATA = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'small_writing.json'), 'utf8'));
const types = DATA.types || [];
const t = types.find(x => x.id === 'minutes');
if (!t) problems.push('缺少 minutes 类型');
else {
    if (types[types.length - 1].id !== 'minutes') problems.push('minutes 不是第 11 类（应追加在末尾）');
    if ((t.banks || []).length !== 4) problems.push('minutes 句组数应为 4，实际 ' + (t.banks || []).length);
    if (!t.note || !/大纲/.test(t.note)) problems.push('minutes 类型缺少「大纲」说明 note');
}
const mBanks = (DATA.banks || []).filter(b => String(b.id).indexOf('m_s') === 0);
if (mBanks.length !== 4) problems.push('纪要句组应为 4 组，实际 ' + mBanks.length);
const mItems = mBanks.flatMap(b => b.items || []);
if (mItems.length !== 4) problems.push('纪要句数应为 4，实际 ' + mItems.length);
if (mItems.some(x => x.tier === 'must' || x.tier === 'core')) problems.push('纪要句不得标 must/core（会挤占 24 句额度）');
const S = DATA.stats || {};
if (S.core !== 4 || S.must !== 20 || S.core_words !== 43 || S.must_words !== 355) problems.push('必背/骨架口径被改动: ' + JSON.stringify(S));
if (S.items !== 63 || S.banks !== 33 || S.types !== 11 || S.ammo !== 39) problems.push('指标未同步: ' + JSON.stringify(S));
// 旧句顺序未被打乱（追加式写入）
const oldIds = (DATA.banks || []).slice(0, 29).map(b => b.id);
if (oldIds[0] !== 'p1s1' || oldIds[28] !== 'p2_opinion_s3') problems.push('既有句组顺序被改动（应为追加式）');

// ---------- 渲染层：jsdom ----------
const html = fs.readFileSync(path.join(PWA, 'smallwriting.html'), 'utf8');
const dom = new JSDOM(html, { url: 'http://localhost/smallwriting.html', runScripts: 'outside-only', pretendToBeVisual: true });
const w = dom.window;
const d = w.document;
w.fetch = (p) => Promise.resolve({
    ok: true,
    json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
});
const libs = ['common.js', 'smallwriting.js'].map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
w.eval(libs);

(async () => {
    await w.swInit();

    // 1. 拼装：纪要
    const L = w.swLetterLines('minutes');
    const kinds = L.map(x => x.kind);
    if (kinds[0] !== 'title' || L[0].text !== 'Minutes') problems.push('首行应为标题 Minutes，实际 ' + JSON.stringify(L[0]));
    if (kinds.indexOf('sal') >= 0) problems.push('会议纪要不应出现称呼（sal）');
    const sents = L.filter(x => x.kind === 'sent');
    if (sents.length !== 4) problems.push('正文句应为 4，实际 ' + sents.length);
    if (sents.some(x => !x.item || !x.item.en)) problems.push('存在空正文句');
    const last = L[L.length - 1];
    if (last.kind !== 'sig' || last.text !== 'Minutes recorder: Li Ming') problems.push('落款应为 Minutes recorder: Li Ming，实际 ' + JSON.stringify(last));
    if (L.some(x => (x.text || '').indexOf('Yours sincerely') >= 0)) problems.push('会议纪要不应出现 Yours sincerely');
    const body = sents.map(x => x.item.en).join(' ');
    if (!/\bwas\b/.test(body) || !/\bbegan\b/.test(body)) problems.push('会议要素句应使用过去时（was/began）');

    // 2. 回归：原有类型格式不变
    const adv = w.swLetterLines('advice');
    if (!adv.some(x => x.kind === 'sal' && x.text === 'Dear Sir or Madam,')) problems.push('建议信称呼被破坏');
    if (!adv.some(x => x.kind === 'sig' && x.text === 'Yours sincerely,')) problems.push('建议信落款被破坏');
    const ntc = w.swLetterLines('notice');
    if (!ntc.some(x => x.kind === 'title' && x.text === 'NOTICE')) problems.push('通知标题被破坏');
    if (!ntc.some(x => x.kind === 'signote')) problems.push('通知「不写人名落款」提示被破坏');

    // 3. 高亮键不位移（swKeyIdxOf 对已存在键只读返回）
    const kFirst = w.swKeyIdxOf('p1s1#0');
    const kLastOld = w.swKeyIdxOf('p2_opinion_s3#0');
    const kNew = w.swKeyIdxOf('m_s1#0');
    if (kFirst !== 0) problems.push('首个句子的高亮键位移: ' + kFirst);
    if (kLastOld !== 58) problems.push('末尾旧句高亮键应为 58，实际 ' + kLastOld);
    if (kNew !== 59) problems.push('新增句应从 59 起编号，实际 ' + kNew);

    // 4. 实际渲染（走真实用户路径：点类型 tab，而不是改内部变量）
    const tabBtn = [...d.querySelectorAll('.sw-ttab')].find(b => b.textContent === '会议纪要');
    if (!tabBtn) problems.push('类型 tab 中没有「会议纪要」');
    else tabBtn.click();
    await sleep(80);
    const txt = (d.getElementById('swLetter') || {}).textContent || '';
    if (!/Minutes/.test(txt)) problems.push('整信区未渲染标题 Minutes');
    if (!/Minutes recorder: Li Ming/.test(txt)) problems.push('整信区未渲染纪要落款');
    if (/Dear Sir or Madam/.test(txt)) problems.push('整信区不应出现称呼');
    if (!/participants|conclusion/i.test(txt)) problems.push('整信区缺少纪要正文');

    // 5. 指标与类型说明（点「按信件类型」视图）
    const statsTxt = (d.getElementById('swStats') || {}).textContent || '';
    if (!/63 句/.test(statsTxt) || !/必背 20 句/.test(statsTxt)) problems.push('顶部指标异常: ' + statsTxt);
    const viewBtn = [...d.querySelectorAll('.sw-vbtn')].find(b => b.dataset.view === 'type');
    if (viewBtn) viewBtn.click();
    await sleep(80);
    const content = (d.getElementById('swContent') || {}).textContent || '';
    if (!/2024 年起列入大纲/.test(content)) problems.push('类型视图未显示「大纲」说明');
    const tabs = [...d.querySelectorAll('.sw-ttab')].map(b => b.textContent);
    if (tabs[tabs.length - 1] !== '会议纪要') problems.push('类型 tab 末位不是会议纪要: ' + JSON.stringify(tabs.slice(-2)));

    if (problems.length) {
        console.log('FAIL ' + problems.length + ' 处:');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('MINUTES OK：第 11 类 / 4 句 / 标题 Minutes / 落款 Minutes recorder / 必背口径 24 句不变 / 旧高亮键不位移');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 4).join('\n')); process.exit(1); });
