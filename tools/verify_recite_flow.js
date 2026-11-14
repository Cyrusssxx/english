/* 速记页「背诵动线」回归（recite.html + recite.js + style.css）
 * 覆盖：
 *  1) 页面第一段 = 三步法，大/小作文各一份、各 3 步，且位于 rc-desc 之前；
 *  2) 高亮安全：三步法用独立 .rc-how* 类名，不与 RC_MK_SEL 任何选择器相交
 *     （往正文前插块会位移已保存的划词高亮，这是本站反复踩过的坑）；
 *  3) 动线一致性：动态走势套数与数据同步、目录编号与正文对齐、视图切换后目录高亮正确；
 *  4) 口径一致：30 天表不再含旧模板的按话题分类与过期词数，考场时间合计 30 分钟。
 * 用法: node tools/verify_recite_flow.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const PWA = path.resolve(__dirname, '..', 'pwa');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const problems = [];
const ok = (name, cond, extra) => {
    if (!cond) problems.push(name + (extra != null ? '  ->  ' + extra : ''));
    console.log('  ' + (cond ? 'PASS  ' : 'FAIL  ') + name + (!cond && extra != null ? '  ->  ' + extra : ''));
};
const read = f => fs.readFileSync(path.join(PWA, f), 'utf8');

(async () => {
    const html = read('recite.html');
    const js = read('js/recite.js');
    const css = read('css/style.css');
    const TPL = JSON.parse(read('data/writing_templates.json'));
    const SW = JSON.parse(read('data/small_writing.json'));

    /* ---------------- 静态：三步法与高亮安全 ---------------- */
    console.log('页面第一段（静态）：');
    for (const id of ['rcHowBig', 'rcHowSmall']) {
        ok(id + ' 存在', html.indexOf('id="' + id + '"') >= 0);
    }
    const mkSel = (/const RC_MK_SEL\s*=\s*'([^']+)'/.exec(js) || [])[1] || '';
    ok('已从源码取到 RC_MK_SEL', !!mkSel, mkSel);
    ok('三步法类名全部不在 RC_MK_SEL 内（不会位移老高亮）',
        !/\.rc-how|\.rc-step|\.rc-order-body|\.rc-note|\.rc-table/.test(
            (html.match(/<details class="rc-how[\s\S]*?<\/details>/g) || []).join('')),
        '三步法区块里出现了 RC_MK_SEL 选择器类名');
    // 精确：三步法区块（<details class="rc-how"> … </details>）
    const howBlocks = [...html.matchAll(/<details class="rc-how"[\s\S]*?<\/details>/g)].map(m => m[0]);
    ok('大/小作文各有一段三步法区块', howBlocks.length === 2, howBlocks.length);
    const howClasses = new Set();
    howBlocks.forEach(b => [...b.matchAll(/class="([^"]+)"/g)].forEach(m => m[1].split(/\s+/).forEach(c => howClasses.add('.' + c))));
    const selParts = mkSel.split(',').map(s => s.trim().split(/\s+/)[0]).filter(Boolean);
    const overlap = [...howClasses].filter(c => selParts.includes(c));
    ok('三步法 DOM 与划词高亮块零交集', overlap.length === 0, overlap.join(','));
    ok('每段三步法恰好 3 步', howBlocks.every(b => (b.match(/class="rc-how-i"/g) || []).length === 3),
        howBlocks.map(b => (b.match(/class="rc-how-i"/g) || []).length).join('/'));
    ok('三步法在各自 rc-desc 之前（是页面第一段）',
        html.indexOf('id="rcHowBig"') < html.indexOf('id="rcDesc"')
        && html.indexOf('id="rcHowSmall"') < html.indexOf('id="rcDescS"'));

    console.log('样式与打印：');
    ok('#rcBig/#rcSmall 的 hidden 防御规则', /#rcBig\[hidden\], #rcSmall\[hidden\] \{ display: none; \}/.test(css));
    ok('.rc-how 样式存在且用 --card-bg', /\.rc-how \{[^}]*var\(--card-bg\)/.test(css));
    ok('.rc-how-i 三格布局', /\.rc-how-steps \{[^}]*grid/.test(css));
    ok('打印样式含 .rc-how', /@media print \{[\s\S]*?\.rc-how, \.rc-how-i/.test(css));

    console.log('手机端（≤640px）压紧：');
    const mq640 = (css.match(/@media \(max-width: 640px\) \{[\s\S]*?\n\}/g) || []).join('\n');
    ok('手机端目录改单行横滑（不再换行成 2~3 行）',
        /\.rc-toc \{[^}]*flex-wrap: nowrap/.test(mq640) && /\.rc-toc \{[^}]*overflow-x: auto/.test(mq640));
    ok('手机端目录 chip 不收缩（横滑可读）', /\.rc-toc a \{ flex: 0 0 auto/.test(mq640));
    ok('手机端三步法默认收起时有「三步关键词」一行', /rc-how-mini \{ display: block/.test(mq640)
        && /rc-how-mini \{ display: none/.test(mq640));
    ok('手机端收起按钮加大到 34px（28px 太难点中）', /\.nav-toggle-btn \{[^}]*width: 34px/.test(mq640)
        && /\.nav-toggle-btn \{[^}]*touch-action: manipulation/.test(mq640));
    ok('common.js 顶栏收起/展开后派发 navheightchange',
        /navheightchange/.test(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')));
    ok('顶栏收起时吸顶条给 ▼ 按钮让位（padding-right）',
        /html\[data-nav-collapsed="1"\] \.rc-toc/.test(css)
        && /dataset\.navCollapsed/.test(fs.readFileSync(path.join(PWA, 'js/common.js'), 'utf8')));

    /* ---------------- 静态：口径一致性 ---------------- */
    console.log('口径一致性（静态）：');
    const planTable = (html.match(/<section class="rc-sec" id="rcSecPlan">[\s\S]*?<\/section>/) || [])[0] || '';
    const stale = ['334', '共 72 词', '经济类', '校园类', '环保类', '体育健康类', '文化类', '限时 25 分钟'];
    const hit = stale.filter(k => planTable.includes(k));
    ok('30 天表已清除旧模板的按话题分类与过期词数', hit.length === 0, hit.join(','));
    ok('30 天表验收改为 30 分钟', /限时 30 分钟成篇/.test(planTable));
    ok('考场时间分配合计 30（2+3+20+5）', /审题 2 分钟 → 定骨架与归因 3 分钟 → 写 20 分钟 → 检查 5 分钟/.test(js));
    ok('小作文计划不再裸写「10 类全覆盖」', !/<td>10 类全覆盖<\/td>/.test(js));
    ok('动态走势套数改为从数据取（无写死 3 个 label）',
        /const dynSkels = \(\(S\.chart_dynamic \|\| \{\}\)\.skeletons\) \|\| \[\]/.test(js)
        && !/\['① 一条线在走', '② 两条都在涨', '③ 一升一降'\]/.test(js));
    ok('目录第一项补了 ①（两个视图）', (js.match(/'① ✨ 精选好句'/g) || []).length === 2);
    ok('目录 spy 会跳过隐藏视图并暴露给 rcView',
        /host && host\.hidden/.test(js) && /RC_SPIES\.push\(spy\)/.test(js) && /RC_SPIES\.forEach/.test(js));

    /* ---------------- 渲染层：jsdom 实跑 ---------------- */
    console.log('渲染层（jsdom 实跑）：');
    const dom = new JSDOM(html, { url: 'http://localhost/recite.html', runScripts: 'outside-only', pretendToBeVisual: true });
    const w = dom.window, d = w.document;
    w.fetch = p => {
        try { return Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(read(p))), text: () => Promise.resolve(read(p)) }); }
        catch (e) { return Promise.reject(e); }
    };
    w.loadDict = async () => ({});
    w.loadPhrases = async () => ({});
    w.scrollTo = () => {};
    w.eval(['dict.js', 'recite.js'].map(f => read('js/' + f)).join('\n;\n'));
    d.dispatchEvent(new w.Event('DOMContentLoaded', { bubbles: true }));
    for (let i = 0; i < 80; i++) {
        if (d.getElementById('rcDesc').textContent !== '加载中…' && d.getElementById('rcDescS').textContent !== '加载中…') break;
        await sleep(50);
    }
    await sleep(250);

    ok('大作文第一段说明正常渲染（新增区块未打断 rcInit）', /只背骨架/.test(d.getElementById('rcDesc').textContent));
    ok('小作文第一段说明正常渲染', /骨架 4 句/.test(d.getElementById('rcDescS').textContent));

    const skels = ((TPL.sections || []).find(s => s.id === 'chart_dynamic') || {}).skeletons || [];
    const orderTxt = d.getElementById('rcOrder').textContent.replace(/\s+/g, ' ');
    ok('「怎么拼」写的套数 = 数据里的走势骨架数（' + skels.length + '）',
        orderTxt.includes('从 ' + skels.length + ' 套里选一套'), orderTxt.slice(0, 130));
    const wordList = (orderTxt.match(/从 \d+ 套里选一套：\s*([^（]+)/) || [])[1] || '';
    ok('词数列表条数 = 走势骨架数', (wordList.match(/\d+/g) || []).length === skels.length, wordList.trim());
    ok('第三节骨架卡片数 = 走势骨架数', d.querySelectorAll('#rcSkeleton .rc-skel').length === skels.length,
        d.querySelectorAll('#rcSkeleton .rc-skel').length);

    const tocBig = [...d.querySelectorAll('#rcToc a')];
    const tocSmall = [...d.querySelectorAll('#rcTocS a')];
    const secBig = d.querySelectorAll('#rcBig section.rc-sec').length;
    const secSmall = d.querySelectorAll('#rcSmall section.rc-sec').length;
    ok('大作文目录项数 = 正文章节数（' + secBig + '）', tocBig.length === secBig, tocBig.length);
    ok('小作文目录项数 = 正文章节数（' + secSmall + '）', tocSmall.length === secSmall, tocSmall.length);
    ok('两个目录第一项都是 ①', tocBig[0].textContent.includes('①') && tocSmall[0].textContent.includes('①'));

    // 划词高亮块：三步法元素不应被 RC_MK_SEL 选中
    const mkEls = [...d.querySelectorAll(mkSel)];
    const howEls = [...d.querySelectorAll('.rc-how, .rc-how-h, .rc-how-steps, .rc-how-i, .rc-how-n')];
    ok('DOM 实查：三步法元素不在划词高亮块集合内', howEls.length > 0 && howEls.every(el => !mkEls.includes(el)),
        'howEls=' + howEls.length + ' mkEls=' + mkEls.length);

    // 视图切换：隐藏视图目录不应残留 .on
    // jsdom 不排版，所有 rect 恒为 0；按 DOM 顺序给一个模拟布局，让 scroll spy 反映真实浏览器行为。
    [...d.querySelectorAll('#rcBig section.rc-sec')].forEach((el, i) => {
        el.getBoundingClientRect = () => ({ top: 200 + i * 400, bottom: 0, left: 0, right: 0, width: 0, height: 0 });
    });
    [...d.querySelectorAll('#rcSmall section.rc-sec')].forEach((el, i) => {
        el.getBoundingClientRect = () => ({ top: 200 + i * 400, bottom: 0, left: 0, right: 0, width: 0, height: 0 });
    });
    ok('初始 big 可见 / small 隐藏', !d.getElementById('rcBig').hidden && d.getElementById('rcSmall').hidden);
    d.querySelector('.rc-vw-btn[data-v="small"]').click();
    ok('切到小作文后 hidden 状态互换', d.getElementById('rcBig').hidden && !d.getElementById('rcSmall').hidden);
    const bigOn = [...d.querySelectorAll('#rcToc a.on')];
    const smallOn = [...d.querySelectorAll('#rcTocS a.on')];
    ok('隐藏的大作文目录无 .on（旧版会停在末项）', bigOn.length === 0, bigOn.map(a => a.textContent).join(','));
    ok('显示的小作文目录有且仅有一个 .on', smallOn.length === 1, smallOn.length);
    ok('该 .on 是第一项', smallOn.length === 1 && smallOn[0] === tocSmall[0], smallOn[0] && smallOn[0].textContent);
    d.querySelector('.rc-vw-btn[data-v="big"]').click();
    ok('切回大作文后隐藏的小作文目录无 .on', d.querySelectorAll('#rcTocS a.on').length === 0);

    // 小作文数据口径
    const sPlan = d.getElementById('rcSPlan').textContent;
    ok('小作文计划说明「会议纪要单独看句库」', /会议纪要单独看句库/.test(sPlan));
    ok('小作文类型数与数据一致（' + SW.types.length + '）',
        d.getElementById('rcStatsS').textContent.includes(String(SW.types.length) + '个信件类型'));

    /* ---------------- 三步法折叠：桌面展开 / 手机收起 / 用户选择优先 ---------------- */
    console.log('三步法折叠（jsdom）：');
    const howBoxes = [...d.querySelectorAll('details.rc-how')];
    ok('三步法已改为 <details> 可折叠，且都有 summary',
        howBoxes.length === 2 && howBoxes.every(b => !!b.querySelector('summary.rc-how-h')), howBoxes.length);
    ok('桌面（>640px）默认展开', howBoxes.every(b => b.open));
    // 模拟窄屏 + 清掉用户选择 → 默认收起
    w.eval(`
        window.matchMedia = q => ({ matches: /max-width/.test(q), addEventListener(){}, removeEventListener(){}, addListener(){}, removeListener(){} });
        try { localStorage.removeItem('rc_how_open_v1'); } catch (e) {}
        rcHowInit();
    `);
    ok('手机端（≤640px）默认收起，只留一栏标题', howBoxes.every(b => !b.open));
    // 用户选择优先：存 '1' → 手机端也展开
    w.eval(`try { localStorage.setItem('rc_how_open_v1','1'); } catch (e) {} rcHowInit();`);
    ok('用户手动展开过则记住（手机端也展开）', howBoxes.every(b => b.open));
    w.eval(`try { localStorage.setItem('rc_how_open_v1','0'); } catch (e) {} rcHowInit();`);
    ok('用户手动收起过则记住（桌面也收起）', howBoxes.every(b => !b.open));

    /* ---------------- 顶栏收起 → 吸顶偏移归零 ---------------- */
    console.log('顶栏收起联动（jsdom）：');
    const nav = d.querySelector('.navbar');
    nav.dataset.collapsed = '1';
    w.dispatchEvent(new w.Event('navheightchange'));
    ok('顶栏收起后 --nav-h = 0px（吸顶目录不留白带）',
        d.documentElement.style.getPropertyValue('--nav-h') === '0px',
        d.documentElement.style.getPropertyValue('--nav-h'));
    nav.dataset.collapsed = '';
    w.dispatchEvent(new w.Event('navheightchange'));
    ok('顶栏展开后 --nav-h 恢复（jsdom 无布局 → 兜底 56px）',
        d.documentElement.style.getPropertyValue('--nav-h') === '56px',
        d.documentElement.style.getPropertyValue('--nav-h'));

    if (problems.length) {
        console.log('\nFAIL ' + problems.length + ' 处');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('\nRECITE FLOW OK：第一段三步法就位 · 走势套数/目录/编号/时间口径全对齐 · 高亮块零位移');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 5).join('\n')); process.exit(1); });
