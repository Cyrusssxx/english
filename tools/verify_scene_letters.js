/* 场景范文回归（招募志愿者 / 推荐信，方案 A：不新增类型、不新增句库）
 * 1) 数据层：notice/intro 各挂 1 封场景范文；每封 ≥100 词、三段译文；rows 的 src 全部指向既有句库；
 * 2) 不变量：banks / types / stats / 通用整信零改动（不新增必背句，不位移句库索引）；
 * 3) 渲染层（jsdom 实跑）：类型 tab 下出现「通用 / 招募志愿者」切换条，切换后整信内容、称呼/标题、
 *    分段、高亮键全部正确，且改写句的键一律为 L:类型:变体#序（不与通用整信撞键）。
 * 用法: node tools/verify_scene_letters.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const PWA = path.resolve(__dirname, '..', 'pwa');
const DATA = JSON.parse(fs.readFileSync(path.join(PWA, 'data', 'small_writing.json'), 'utf8'));
const problems = [];
const ok = (name, cond, extra) => {
    if (!cond) problems.push(name + (extra != null ? ' -> ' + extra : ''));
    console.log('  ' + (cond ? 'PASS  ' : 'FAIL  ') + name + (!cond && extra != null ? ' -> ' + extra : ''));
};
const words = t => ((t || '').match(/[A-Za-z0-9][A-Za-z0-9'’%.,:_-]*/g) || []).length;

const V = {
    notice: (DATA.letters.notice.variants || [])[0],
    intro: (DATA.letters.intro.variants || [])[0],
};

(async () => {
    /* ---------------- 数据层 ---------------- */
    console.log('数据层：');
    ok('notice 挂了招募志愿者范文', !!V.notice && V.notice.id === 'recruit', V.notice && V.notice.id);
    ok('intro 挂了推荐信范文', !!V.intro && V.intro.id === 'recommend', V.intro && V.intro.id);

    const bankIds = new Set((DATA.banks || []).map(b => b.id));
    [['notice', V.notice], ['intro', V.intro]].forEach(([tid, v]) => {
        if (!v) return;
        const en = v.rows.map(r => r[1]).join(' ');
        const wc = words(en);
        ok(tid + ' 范文 ≥100 词（实为 ' + wc + '）', wc >= 100, wc);
        ok(tid + ' 范文三段译文', (v.cn_paras || []).length === 3, (v.cn_paras || []).length);
        const badSrc = v.rows.filter(r => r[0] && !bankIds.has(String(r[0]).split('#')[0])).map(r => r[0]);
        ok(tid + ' 每行 src 都指向既有句库（无新银行）', badSrc.length === 0, badSrc.join(','));
        const badLine = v.rows.filter(r => r.length !== 3 || !r[1] || !r[2]);
        ok(tid + ' 每行 = [src, en, cn] 且中英齐全', badLine.length === 0, badLine.length + ' 行异常');
        ok(tid + ' 行数与 cn_paras 段落一致（7 行 / 3 段）', v.rows.length === 7 && v.cn_paras.length === 3, v.rows.length + '/' + v.cn_paras.length);
    });

    const decQ = (DATA.decisions || []).map(x => x.q);
    ok('选句决策含「招募志愿者」指引', decQ.some(q => q.indexOf('招募志愿者') >= 0));
    ok('选句决策含「推荐信」指引', decQ.some(q => q.indexOf('推荐信') >= 0));

    console.log('不变量（防回退）：');
    ok('句库组数仍 33（未新增 bank）', (DATA.banks || []).length === 33, (DATA.banks || []).length);
    ok('类型仍 11 类（未新增类型）', (DATA.types || []).length === 11, (DATA.types || []).length);
    ok('必背口径不变 4/20/63', DATA.stats.core === 4 && DATA.stats.must === 20 && DATA.stats.items === 63,
        DATA.stats.core + '/' + DATA.stats.must + '/' + DATA.stats.items);
    ok('通用整信未被替换（notice 仍是原来那封）',
        DATA.letters.notice.rows[0][0] === 'p1s2#2' && /issue the following notice/.test(DATA.letters.notice.rows[0][1]));

    /* ---------------- 渲染层 ---------------- */
    const html = fs.readFileSync(path.join(PWA, 'smallwriting.html'), 'utf8');
    const dom = new JSDOM(html, {
        url: 'http://localhost/smallwriting.html',
        runScripts: 'outside-only', pretendToBeVisual: true,
    });
    const w = dom.window, d = w.document;
    w.fetch = p => Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))) });
    const libs = ['common.js', 'smallwriting.js']
        .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
    w.eval(libs);
    await w.swInit();

    const gotoType = id => d.querySelector('#swTypeTabs .sw-ttab[data-t="' + id + '"]').click();
    const varBtns = () => [...d.querySelectorAll('#swVarTabs .sw-vtab')];
    const bodyText = () => d.querySelector('#swLetter').textContent;
    const bodyParas = () => d.querySelectorAll('#swLetter .sw-para-body').length;
    const sentKeys = () => [...d.querySelectorAll('#swLetter .sw-ls')].map(x => x.dataset.k);

    console.log('渲染层：');
    ok('默认类型（建议信）不显示范文切换条', d.getElementById('swVarTabs').hidden === true);

    gotoType('notice');
    ok('通知类出现 2 个范文按钮', varBtns().length === 2, varBtns().map(b => b.textContent).join('|'));
    ok('按钮文案 = 通用 / 招募志愿者', varBtns().map(b => b.textContent).join('|') === '通用|招募志愿者', varBtns().map(b => b.textContent).join('|'));
    ok('默认停在「通用」', varBtns()[0] && varBtns()[0].classList.contains('on'));
    ok('通用通知仍在（未含 recruit volunteers）', !/recruit volunteers/.test(bodyText()));

    varBtns()[1].click();
    let t = bodyText();
    ok('切到招募范文：正文出现 recruit volunteers', /recruit volunteers/.test(t));
    ok('招募范文：标题 NOTICE 居中显示', /NOTICE/.test(t) && !!d.querySelector('#swLetter .sw-title-line'));
    ok('招募范文：三段正文', bodyParas() === 3, bodyParas());
    ok('招募范文：段末译文按钮 3 个', d.querySelectorAll('#swLetter .sw-para-cn-btn').length === 3,
        d.querySelectorAll('#swLetter .sw-para-cn-btn').length);
    ok('招募范文：备注条出现并说明「不新增必背句」', d.getElementById('swVarNote').hidden === false && /不新增/.test(d.getElementById('swVarNote').textContent));
    ok('招募范文 ≥100 词（整封）', words(t) >= 100, words(t));

    let keys = sentKeys();
    ok('招募范文 7 句', keys.length === 7, keys.length);
    ok('招募范文：改写句挂 L:notice:recruit#N，未改写的沿用句库共享键',
        keys.every(k => /^L:notice:recruit#\d+$/.test(k) || bankIds.has(String(k).split('#')[0])), keys.join(','));
    ok('招募范文：不占用通用整信的 L:notice#N 键', keys.every(k => !/^L:notice#\d+$/.test(k)), keys.join(','));
    ok('招募范文：独立键 ≥5 条（确实逐句改写）', keys.filter(k => /^L:notice:recruit#/.test(k)).length >= 5,
        keys.filter(k => /^L:notice:recruit#/.test(k)).length);
    ok('招募范文句键无重复', new Set(keys).size === keys.length);

    varBtns()[0].click();
    ok('切回通用：恢复原通知、备注条收起', /issue the following notice/.test(bodyText())
        && !/recruit volunteers/.test(bodyText()) && d.getElementById('swVarNote').hidden === true);

    gotoType('intro');
    ok('介绍信出现 2 个范文按钮（通用 / 推荐信）', varBtns().map(b => b.textContent).join('|') === '通用|推荐信', varBtns().map(b => b.textContent).join('|'));
    ok('换类型后自动回到「通用」（未残留招募选中态）', varBtns()[0].classList.contains('on'));
    varBtns()[1].click();
    t = bodyText();
    ok('推荐信：正文出现 The Old Man and the Sea', /The Old Man and the Sea/.test(t));
    ok('推荐信：称呼为 Dear Jack,', /Dear Jack,/.test(t));
    ok('推荐信：三段正文', bodyParas() === 3, bodyParas());
    ok('推荐信 ≥100 词（整封）', words(t) >= 100, words(t));
    keys = sentKeys();
    ok('推荐信：改写句挂 L:intro:recommend#N，未改写的沿用句库共享键',
        keys.every(k => /^L:intro:recommend#\d+$/.test(k) || bankIds.has(String(k).split('#')[0])), keys.join(','));
    ok('推荐信：不占用通用整信的 L:intro#N 键', keys.every(k => !/^L:intro#\d+$/.test(k)), keys.join(','));
    ok('推荐信：独立键 ≥5 条', keys.filter(k => /^L:intro:recommend#/.test(k)).length >= 5,
        keys.filter(k => /^L:intro:recommend#/.test(k)).length);
    ok('推荐信句键无重复', new Set(keys).size === keys.length);

    /* 键位安全：变体键必须追加在句库键与通用整信键之后，老键索引一个都不动 */
    const idxOf = k => w.swKeyIdxOf(k);
    let maxBank = -1;
    (DATA.banks || []).forEach(b => (b.items || []).forEach((_, i) => {
        const v = idxOf(b.id + '#' + i);
        if (v != null && v > maxBank) maxBank = v;
    }));
    let maxBaseL = -1;
    Object.keys(DATA.letters || {}).forEach(t => ((DATA.letters[t] || {}).rows || []).forEach((_, i) => {
        const v = idxOf('L:' + t + '#' + i);
        if (v != null && v > maxBaseL) maxBaseL = v;
    }));
    const vIdx = keys.filter(k => /^L:/.test(k)).map(k => idxOf(k));
    ok('变体键索引全部 > 通用整信最大键（追加在尾部，老键不移位）',
        vIdx.every(i => i > maxBaseL), 'baseLMax=' + maxBaseL + ' variant=' + vIdx.join(','));
    ok('句库首键 p1s1#0 索引仍为 0', idxOf('p1s1#0') === 0, idxOf('p1s1#0'));
    ok('句库最大键索引 < 通用整信起键（句库键位未被动过）', maxBank < idxOf('L:advice#0'), maxBank + ' vs ' + idxOf('L:advice#0'));

    if (problems.length) {
        console.log('\nFAIL ' + problems.length + ' 处');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('\nSCENE LETTERS OK：招募 / 推荐各 1 封场景范文，切条渲染、键位隔离、句库零改动');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 5).join('\n')); process.exit(1); });
