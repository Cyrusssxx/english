/* 速记页「占位符芯片 + 可点词」回归（recite.html + recite.js + style.css）
 * 背景（2026-11-15 定位）：词典就绪后 rcAnnoAll() 用 el.textContent 重标整段，
 * 而 {{槽}} 转芯片时花括号已被吃掉 → 芯片被降级成普通可点词，蓝底 + 斜体全丢。
 * 修法：rcEn() 渲染时把「带 {{}} 的原文」写进 data-src，重标一律据它。
 *
 * 覆盖：
 *  A) 静态：rcEn 出口唯一、rcAnnoAll 优先读 data-src、无旧写法残留、.rc-ph 样式口径；
 *  B) 渲染（jsdom + 真词典）：芯片在重标后仍在、占位符与可点词共存、重标幂等；
 *  C) 划词高亮安全：新增「七、句池」追加在文末，已有块编号零位移；
 *  D) 新增句池：三组齐全（4 + 8 + 16），每句都进了 .rc-en。
 * 用法: node tools/verify_recite_anno.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const PWA = path.resolve(__dirname, '..', 'pwa');
const read = f => fs.readFileSync(path.join(PWA, f), 'utf8');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const problems = [];
const ok = (name, cond, extra) => {
    if (!cond) problems.push(name + (extra != null ? '  ->  ' + extra : ''));
    console.log('  ' + (cond ? 'PASS  ' : 'FAIL  ') + name + (!cond && extra != null ? '  ->  ' + extra : ''));
};
const countPh = t => ((String(t || '').match(/\{\{.+?\}\}/g) || []).length);

(async () => {
    const html = read('recite.html');
    const js = read('js/recite.js');
    const css = read('css/style.css');
    const TPL = JSON.parse(read('data/writing_templates.json'));
    const SW = JSON.parse(read('data/small_writing.json'));
    const sec = id => (TPL.sections || []).find(s => s.id === id) || {};

    /* ---------------- A. 静态：写法与样式口径 ---------------- */
    console.log('静态：出口与样式：');
    ok('rcEn 辅助函数存在（{{槽}} 芯片 + data-src 原文）',
        /function rcEn\(text, tag, cls\)/.test(js) && /data-src="\$\{rcEsc\(text\)\}"/.test(js));
    ok('rcAnnoAll 优先读 data-src（不再拿 textContent 重标）',
        /const src = el\.getAttribute\('data-src'\)/.test(js) && /rcAnno\(src != null \? src : el\.textContent\)/.test(js));
    const legacy = [...js.matchAll(/class="rc-en"[^>]*>\$\{rc(?:Anno|Ph)\(/g)].length;
    ok('源码里不再有绕开 rcEn 的旧写法', legacy === 0, '命中 ' + legacy + ' 处');
    ok('英文块全部经 rcEn 渲染（rc-en 字面量只剩 rcEn 内部一处）',
        (js.match(/['"]rc-en['"]/g) || []).length === 1, (js.match(/['"]rc-en['"]/g) || []).length);

    ok('.rc-ph 保留斜体 + 底色（与写作页 .wr-ph 同观感）',
        /\.rc-ph \{[^}]*font-style: italic/.test(css) && /\.rc-ph \{[^}]*background: rgba\(29, 111, 208/.test(css));
    ok('.rc-ph 加虚线底边（扫读时能看出「这里要换词」）',
        /\.rc-ph \{[^}]*border-bottom: 1px dashed/.test(css));
    ok('.rc-ph 深色主题配色齐全',
        /html\.dark \.rc-ph \{[^}]*color: #8fb4d8/.test(css) && /html\.dark \.rc-ph \{[^}]*border-bottom-color/.test(css));
    ok('图例说明两视图都有（点单词查词 / 蓝底斜体 = 槽）',
        (js.match(/class="rc-legend"/g) || []).length === 2
        && /点任意单词查释义/.test(js) && /考场上要换掉的槽/.test(js));

    const mkSel = (/const RC_MK_SEL\s*=\s*'([^']+)'/.exec(js) || [])[1] || '';
    ok('已取到 RC_MK_SEL', !!mkSel, mkSel);
    const selParts = mkSel.split(',').map(s => s.trim());
    ok('.rc-hint / .rc-legend 不在划词高亮块选择器内（插提示不位移老高亮）',
        !selParts.includes('.rc-hint') && !selParts.includes('.rc-legend')
        && /\.rc-hint \{[^}]*font-size/.test(css));

    ok('「七、句池」版块存在且排在考场章之后（追加在文末 → 老块编号零位移）',
        html.indexOf('id="rcSecPools"') > html.indexOf('id="rcSecExam"')
        && html.indexOf('id="rcSecPools"') < html.indexOf('/rcBig'));

    /* ---------------- B. 渲染层：真词典 ---------------- */
    console.log('渲染层（jsdom + 真词典）：');
    const dom = new JSDOM(html, { url: 'http://localhost/recite.html', runScripts: 'outside-only', pretendToBeVisual: true });
    const w = dom.window, d = w.document;
    w.fetch = p => {
        try {
            const body = read(String(p).replace(/^\.?\//, ''));
            return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(body)), text: () => Promise.resolve(body) });
        } catch (e) { return Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve(null), text: () => Promise.resolve('') }); }
    };
    w.scrollTo = () => {};
    w.eval(['dict.js', 'common.js', 'recite.js'].map(f => read('js/' + f)).join('\n;\n'));
    d.dispatchEvent(new w.Event('DOMContentLoaded', { bubbles: true }));
    for (let i = 0; i < 120; i++) {
        if (typeof w.maxPhraseWords === 'function' && w.maxPhraseWords() >= 1
            && d.getElementById('rcSkeleton').children.length > 0) break;
        await sleep(50);
    }
    await sleep(400);
    ok('词典就绪（词组最大词数 > 0）', w.maxPhraseWords() >= 1, w.maxPhraseWords());

    const staticCard = [...d.querySelectorAll('#rcSkeleton .rc-card')]
        .find(c => /第一段/.test(c.textContent) && !/动态/.test(c.querySelector('.rc-card-title').textContent));
    const stEn = sec('chart_static').en || '';
    const stPh = staticCard ? staticCard.querySelectorAll('.rc-en .rc-ph').length : -1;
    ok('静态骨架：芯片数 = 原文 {{槽}} 数（' + countPh(stEn) + '）', stPh === countPh(stEn), '实为 ' + stPh);
    ok('静态骨架：可点词仍然存在（芯片与单词共存）',
        staticCard && staticCard.querySelectorAll('.rc-en .word').length > 10,
        staticCard ? staticCard.querySelectorAll('.rc-en .word').length : 'no card');
    const phTexts = staticCard ? [...staticCard.querySelectorAll('.rc-en .rc-ph')].map(e => e.textContent) : [];
    ok('静态骨架：槽名完整（chart / topic / item1 / percent1）',
        ['chart', 'topic', 'item1', 'percent1'].every(x => phTexts.includes(x)), phTexts.slice(0, 6).join(','));
    ok('芯片不会被误标成可点词（.rc-ph 内无 .word）',
        staticCard && staticCard.querySelectorAll('.rc-ph .word').length === 0);

    const dynSkels = (sec('chart_dynamic').skeletons || []);
    const dynCards = [...d.querySelectorAll('#rcSkeleton .rc-skel')];
    const dynOk = dynCards.every((c, i) => {
        const want = countPh((dynSkels[i] || {}).en || '');
        return c.querySelectorAll('.rc-en .rc-ph').length === want;
    });
    ok('动态骨架 4 套：每套芯片数 = 该套 {{槽}} 数（' + dynCards.length + ' 套）', dynOk && dynCards.length === dynSkels.length);

    const allEnBlocks = [...d.querySelectorAll('.rc-en')];
    const missSrc = allEnBlocks.filter(e => e.getAttribute('data-src') == null);
    ok('.rc-en 全部带 data-src（重标有据可依）', missSrc.length === 0, '缺 ' + missSrc.length);
    const enChips = d.querySelectorAll('.rc-en .rc-ph').length;
    ok('大作文视图：英文块内芯片总数 > 60（修前为 0）', enChips > 60, enChips);

    const smallChips = d.querySelectorAll('#rcSCore .rc-en .rc-ph').length;
    ok('小作文视图：英文块内也有芯片（骨架来信意句含 {{topic}}）', smallChips > 0, smallChips);

    // 幂等：重复重标不得改文本、不得叠加
    const before = allEnBlocks.map(e => e.textContent).join('|');
    w.eval('rcAnnoAll()');
    const after = [...d.querySelectorAll('.rc-en')].map(e => e.textContent).join('|');
    ok('重复调用 rcAnnoAll 文本不变（幂等，不会重复叠词）', before === after);

    /* ---------------- C. 划词高亮块编号安全 ---------------- */
    console.log('划词高亮安全：');
    const mkEls = [...d.querySelectorAll(mkSel)];
    const idxOf = el => parseInt(el.getAttribute('data-mk'), 10);
    const poolsSec = d.getElementById('rcSecPools');
    const examSec = d.getElementById('rcSecExam');
    const examMax = Math.max(-1, ...[...examSec.querySelectorAll('[data-mk]')].map(idxOf));
    const poolsMin = Math.min(...[...poolsSec.querySelectorAll('[data-mk]')].map(idxOf));
    ok('新句池块编号全部 > 考场章最大编号（老块零位移）',
        examMax >= 0 && poolsMin > examMax, 'examMax=' + examMax + ' poolsMin=' + poolsMin);
    const hintInMk = [...d.querySelectorAll('.rc-hint, .rc-legend')].filter(el => mkEls.includes(el));
    ok('提示行 / 图例未被纳入高亮块', hintInMk.length === 0, hintInMk.length);

    /* ---------------- D. 新增句池内容 ---------------- */
    console.log('新增「七、句池」：');
    const poolGroups = [...d.querySelectorAll('#rcPools .rc-group')].map(e => e.textContent);
    ok('三组齐全（静态补句 / 动态补句 / 机制句池）', poolGroups.length === 3, poolGroups.join(' | '));
    const pools = d.getElementById('rcPools');
    const nPh = pools.querySelectorAll('.rc-en .rc-ph').length;
    ok('句池句子也有芯片（含 {{topic}} 的机制句 16 条）', nPh > 15, nPh);
    const wantTotal = ['chart_static', 'chart_dynamic', 'para2_why']
        .reduce((a, id) => a + ((sec(id).sentences || []).length), 0);
    ok('句池句数 = 数据句数（' + wantTotal + '）', pools.querySelectorAll('.rc-line').length === wantTotal,
        pools.querySelectorAll('.rc-line').length);
    ok('句池句子按考频降序（每组内 ★ 数不递增）', (() => {
        const groups = [];
        let cur = null;
        [...pools.children].forEach(ch => {
            if (ch.classList.contains('rc-group')) { cur = []; groups.push(cur); }
            else if (cur && ch.classList.contains('rc-lines')) {
                [...ch.querySelectorAll('.rc-line')].forEach(l => {
                    const s = l.querySelector('.rc-freq');
                    cur.push(s ? (s.textContent.match(/★/g) || []).length : 0);
                });
            }
        });
        return groups.length === 3 && groups.every(g =>
            g.length > 0 && g.every((v, i) => i === 0 || g[i - 1] >= v));
    })(), '有分组未按 ★ 降序');
    ok('目录新增「⑦ ⚡ 句池」项', /'rcSecPools', '⑦ ⚡ 句池'/.test(js));
    ok('大作文目录项数 = 章节数（7）', d.querySelectorAll('#rcToc a').length === 7,
        d.querySelectorAll('#rcToc a').length);

    console.log('\n' + (problems.length ? 'FAIL x' + problems.length + '\n' + problems.join('\n') : 'ALL PASS'));
    process.exit(problems.length ? 1 : 0);
})();
