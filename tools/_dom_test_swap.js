/* DOM 验证「整句可替换」气泡（2026-11-21）
   A. 押题范文：模板句带 .yt-swap + data-swap，悬停弹出替换列表，当前表达＝句子原文；
      大作文只做第三段（立场 / 收尾），小作文做寒暄 / 来意 / 结尾
   B. 模板骨架：第一段 / 第三段骨架行、第二段引入句也挂了替换；占位符集合必须与原句相同
   C. 衔接逻辑：替换句与紧邻句不共用同一连接词（followed by / by contrast 之类）
   两页共用 common.js 的 .wr-upg-pop.wr-swap-pop，这里走真实事件（mouseover + 延迟）。 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const read = p => fs.readFileSync(path.join(PWA, p), 'utf8');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);
const wait = ms => new Promise(r => setTimeout(r, ms));

function boot(htmlName, scripts, datas) {
    const html = fs.readFileSync(path.join(PWA, htmlName), 'utf8');
    const dom = new JSDOM(html, { runScripts: 'outside-only', url: 'http://localhost/' + htmlName, pretendToBeVisual: true });
    const { window } = dom;
    window.fetch = url => {
        const key = String(url).split('?')[0];
        const body = datas[key];
        return Promise.resolve({
            ok: body != null, status: body != null ? 200 : 404,
            json: () => Promise.resolve(body != null ? JSON.parse(body) : {}),
            text: () => Promise.resolve(body || ''),
        });
    };
    for (const f of scripts) {
        try { window.eval(read(f)); } catch (e) { fail(`${f} 执行异常: ${e.message}`); }
    }
    return window;
}

function checkData(d, label, hasPh) {
    let bad = 0;
    const attrs = [...d.querySelectorAll('[data-swap]')];
    attrs.forEach(el => {
        let j = null;
        try { j = JSON.parse(el.getAttribute('data-swap')); } catch (e) { bad++; return; }
        if (!j.tag || !(j.alts || []).length) bad++;
        j.alts.forEach(a => {
            if (!a.en || !a.cn) bad++;
            if (!hasPh && (a.en.indexOf('{{') >= 0 || a.en.indexOf('—') >= 0)) bad++;
        });
    });
    if (bad) fail(`${label} 有 ${bad} 处 data-swap 不合法`);
    else pass(`${label} ${attrs.length} 处 data-swap 均可解析、alts 完整`);
    return attrs;
}

(async () => {
    /* ========== A. 押题范文 ========== */
    const YJ = read('data/yati.json');
    const YDATA = { 'data/yati.json': YJ, 'data/dict.json': read('data/dict.json'),
                    'data/phrases.json': read('data/phrases.json'), 'data/hardwords.json': read('data/hardwords.json') };
    const W1 = boot('yati.html', ['js/common.js', 'js/dict.js', 'js/kwpop.js', 'js/yati.js'], YDATA);
    await wait(500);
    const D1 = W1.document;
    const Y = JSON.parse(YJ);
    const byNo = {};
    Y.groups.forEach(g => g.items.forEach(it => { byNo[it.no] = it; }));

    // 数据侧：54 句挂了 swap，且只挂在大作文图表 10 篇 + 小作文 8 篇
    let swSents = 0, swAlts = 0;
    const nos = [];
    const perNo = {};
    Y.groups.forEach(g => g.items.forEach(it => {
        let n = 0;
        (it.blocks || []).forEach(b => (b.sents || []).forEach(s => {
            if (s.swap) { swSents++; n++; swAlts += (s.swap.alts || []).length; }
        }));
        if (n) { nos.push(it.no); perNo[it.no] = { n, big: g.id !== 't1' }; }
    }));
    if (swSents !== 44) fail(`可替换句 ${swSents} 条，应为 44（大作文 10×2 + 小作文 8×3）`);
    else pass(`可替换句 ${swSents} 条 / 替换句 ${swAlts} 条，覆盖 ${nos.length} 篇`);
    const wantNos = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 20, 21, 22, 23, 24, 25, 26];
    if (nos.slice().sort((a, b) => a - b).join(',') !== wantNos.join(',')) fail('覆盖篇号不符: ' + nos.join(','));
    else pass('覆盖篇号 = 图表 10 篇 + 小作文 8 篇');

    // 大作文只替换第三段：每篇 2 句，且都落在最后一个 p 块（第三段）
    let bigBad = [];
    Y.groups.filter(g => g.id !== 't1').forEach(g => g.items.forEach(it => {
        const pBlocks = (it.blocks || []).filter(b => b.k === 'p');
        const lastP = pBlocks[pBlocks.length - 1];
        const inLast = (lastP.sents || []).filter(s => s.swap).length;
        const total = (it.blocks || []).reduce((a, b) => a + (b.sents || []).filter(s => s.swap).length, 0);
        if (!total) return;                      // 图画/名言类没挂替换，跳过
        if (total !== 2 || inLast !== total) bigBad.push(`NO${it.no}(${inLast}/${total})`);
    }));
    if (bigBad.length) fail('大作文替换句越出第三段或数量不对: ' + bigBad.join(' '));
    else pass('大作文 10 篇各 2 句，全部落在第三段（前两段不换）');
    const smallBad = Object.keys(perNo).filter(k => !perNo[k].big && perNo[k].n !== 3);
    if (smallBad.length) fail('小作文每篇应为 3 句，异常: ' + smallBad.join(','));
    else pass('小作文 8 篇各 3 句（寒暄 / 来意 / 结尾或过渡）');

    // 打开 NO6：渲染出的 .yt-swap 与数据一致
    W1.ytOpen(6);
    const pane = D1.getElementById('ytMEssay');
    const want6 = (byNo[6].blocks || []).reduce((a, b) => a + (b.sents || []).filter(s => s.swap).length, 0);
    const got6 = pane.querySelectorAll('.yt-jsent.yt-swap').length;
    if (got6 !== want6) fail(`NO6 渲染 ${got6} 个 .yt-swap，应为 ${want6}`);
    else pass(`NO6 渲染 ${got6} 个可替换句，与数据一致`);
    checkData(pane, 'NO6');

    // 悬停 → 弹气泡，内容 = tag / 原文 / alts
    const el = pane.querySelector('.yt-jsent.yt-swap');
    el.dispatchEvent(new W1.MouseEvent('mouseover', { bubbles: true }));
    await wait(240);
    const pop = D1.querySelector('.wr-swap-pop');
    if (!pop) { fail('悬停后未弹出替换气泡'); }
    else {
        pass('悬停 140ms 后弹出替换气泡');
        const tag = (pop.querySelector('.wup-tag') || {}).textContent || '';
        if (!tag) fail('气泡缺分类标签'); else pass('气泡分类标签：' + tag);
        const orig = (pop.querySelector('.wup-orig b') || {}).textContent || '';
        const src = (el.textContent || '').replace(/\s+/g, ' ').trim();
        if (orig !== src) fail(`当前表达与原文不一致：${orig.slice(0, 30)} ≠ ${src.slice(0, 30)}`);
        else pass('当前表达 = 句子原文（未被替换，默认仍显示模板句）');
        const items = pop.querySelectorAll('.wup-item').length;
        let want = 0;
        try { want = JSON.parse(el.getAttribute('data-swap')).alts.length; } catch (e) { /* ignore */ }
        if (items !== want) fail(`气泡 ${items} 条替换，数据 ${want} 条`);
        else pass(`列出 ${items} 条替换句（含中文）`);
    }

    // 移开 → 收起
    el.dispatchEvent(new W1.MouseEvent('mouseout', { bubbles: true, relatedTarget: D1.body }));
    await wait(320);
    if (D1.querySelector('.wr-swap-pop')) fail('移开鼠标后气泡未收起');
    else pass('鼠标移开 220ms 后气泡收起');

    // 图例：有替换的篇目多一条说明
    if (pane.querySelector('.yt-lg-swap')) pass('图例含「替换」说明项');
    else fail('图例缺「替换」说明项');

    // 小作文同样生效
    W1.ytOpen(19);
    const pane2 = D1.getElementById('ytMEssay');
    const want19 = (byNo[19].blocks || []).reduce((a, b) => a + (b.sents || []).filter(s => s.swap).length, 0);
    const got19 = pane2.querySelectorAll('.yt-jsent.yt-swap').length;
    if (got19 !== want19 || !got19) fail(`NO19 渲染 ${got19} 个 .yt-swap，应为 ${want19}`);
    else pass(`NO19 小作文渲染 ${got19} 个可替换句`);

    // 没有 swap 的篇目（如图画类 NO27+）不能凭空多出标记
    const plainNo = Y.groups.flatMap(g => g.items).find(it => !(it.blocks || []).some(b => (b.sents || []).some(s => s.swap)));
    if (plainNo) {
        W1.ytOpen(plainNo.no);
        const n = D1.getElementById('ytMEssay').querySelectorAll('.yt-swap').length;
        if (n) fail(`NO${plainNo.no} 无替换数据却渲染了 ${n} 个 .yt-swap`);
        else pass(`NO${plainNo.no} 无替换数据 → 零标记（不多余打扰）`);
    }

    /* ========== B. 模板骨架 ========== */
    const TPLJ = read('data/writing_templates.json');
    const TDATA = { 'data/writing_templates.json': TPLJ, 'data/writing_apply.json': read('data/writing_apply.json'),
        'data/writing_keywords.json': read('data/writing_keywords.json'), 'data/dict.json': read('data/dict.json'),
        'data/wordnotes.json': read('data/wordnotes.json'), 'data/writing_apply_marks.json': read('data/writing_apply_marks.json'),
        'data/writing_words.json': read('data/writing_words.json') };
    const W2 = boot('writing.html', ['js/common.js', 'js/dict.js', 'js/storage.js', 'js/kwpop.js', 'js/writing.js'], TDATA);
    await wait(700);
    const D2 = W2.document;
    const TPL = JSON.parse(TPLJ);
    const sec = id => TPL.sections.find(s => s.id === id);

    // 数据侧：三套骨架 6 句、第一段、第二段引入句
    const p3 = sec('para3_positive').skeletons;
    const p3rows = p3.reduce((a, v) => a + (v.sents_alt || []).length, 0);
    if (p3rows !== 6) fail(`第三段骨架可替换句 ${p3rows}，应为 6（三套 × 首尾）`);
    else pass('第三段三套骨架各 2 句均有整句替换');
    const staticRows = (sec('chart_static').skeletons || []).reduce((a, v) => a + (v.sents_alt || []).length, 0);
    if (staticRows < 3) fail(`第一段静态骨架可替换句 ${staticRows}，偏少`);
    else pass(`第一段骨架 ${staticRows} 句可替换（开篇 + 数据句 + 双图开篇）`);
    const dynRows = (sec('chart_dynamic').skeletons || []).reduce((a, v) => a + (v.sents_alt || []).length, 0);
    if (dynRows < 4) fail(`第一段动态骨架可替换句 ${dynRows}，偏少`);
    else pass(`第一段动态骨架 ${dynRows} 句可替换（各套开篇 + 走势句）`);
    if (!(sec('para2_why').framework || [])[0].swap) fail('第二段引入句缺整句替换');
    else pass('第二段引入句挂上整句替换');

    // DOM 侧：第三段卡片三套骨架逐行
    const card3 = D2.getElementById('para3_positive');
    const skels3 = card3 ? card3.querySelectorAll('.wr-skel') : [];
    if (skels3.length !== 3) fail(`第三段骨架渲染 ${skels3.length} 套，应为 3`);
    else pass('第三段三套骨架已渲染');
    let lineBad = 0, phBad = 0;
    skels3.forEach((sk, i) => {
        const lines = sk.querySelectorAll('.wr-en .wr-line');
        const sw = sk.querySelectorAll('.wr-line.wr-swap');
        if (sw.length !== 2) lineBad++;
        sw.forEach(l => {
            let j = null;
            try { j = JSON.parse(l.getAttribute('data-swap')); } catch (e) { return; }
            // 原句的占位符集合必须与替换句完全相同：少一个换题会漏填，多一个会泄漏上一篇的槽
            const phSet = t => new Set((String(t).match(/\{\{(.+?)\}\}/g) || []).map(x => x.replace(/[{}]/g, '')));
            const o = phSet(j.orig || '');
            j.alts.forEach(a => {
                const p = phSet(a.en);
                if (o.size !== p.size || [...o].some(k => !p.has(k))) phBad++;
            });
        });
    });
    if (lineBad) fail(`${lineBad} 套骨架的可替换行数不是 2（首尾各一）`);
    else pass('每套骨架首尾两句都可替换（共 6 行）');
    if (phBad) fail(`${phBad} 条替换句丢了占位符（换题会失效）`);
    else pass('替换句保留 {{槽位}}，换题照常填');
    checkData(card3, '第三段骨架', true);

    // 第二段引入句
    const p2frame = D2.getElementById('para2_why');
    const fwSw = p2frame ? p2frame.querySelector('.wr-frame-en.wr-swap') : null;
    if (!fwSw) fail('第二段引入句未挂 .wr-swap');
    else pass('第二段引入句可悬停看替换');

    // 悬停骨架行 → 弹气泡
    const row = card3.querySelector('.wr-line.wr-swap');
    row.dispatchEvent(new W2.MouseEvent('mouseover', { bubbles: true }));
    await wait(240);
    const pop2 = D2.querySelector('.wr-swap-pop');
    if (!pop2) fail('骨架行悬停未弹气泡');
    else {
        const tag = (pop2.querySelector('.wup-tag') || {}).textContent || '';
        if (!tag) fail('骨架气泡缺分类标签');
        else pass('骨架行悬停弹气泡，标签：' + tag + ' · ' + pop2.querySelectorAll('.wup-item').length + ' 条替换');
    }

    /* ========== C. 衔接逻辑：换句后不能和邻句「撞连接词」 ========== */
    const CONN = ['followed by', 'by contrast', 'on balance', 'in addition', 'however',
        'therefore', 'thus', 'meanwhile', 'for example', 'as a result',
        'taken together', 'taken as a whole', 'in this way', 'overall'];
    const low = t => String(t || '').toLowerCase();
    const shared = (a, b) => CONN.filter(c => low(a).indexOf(c) >= 0 && low(b).indexOf(c) >= 0);
    let connBad = [];

    // 押题：按篇内句序，比对替换句与前后一句
    Y.groups.forEach(g => g.items.forEach(it => {
        const flat = [];
        (it.blocks || []).forEach(b => (b.sents || []).forEach(s => flat.push(s.en)));
        flat.forEach((en, i) => {
            const sw = (it.blocks || []).flatMap(b => b.sents || [])[i] && (it.blocks || []).flatMap(b => b.sents || [])[i].swap;
            if (!sw) return;
            const nbr = [flat[i - 1], flat[i + 1]].filter(Boolean).join(' ');
            (sw.alts || []).forEach(a => {
                const c = shared(a.en, nbr);
                if (c.length) connBad.push(`NO${it.no} 与邻句共用「${c.join('/')}」`);
            });
        });
    }));

    // 模板骨架：句内按 wrSplitEn 切，比对同行前后句
    TPL.sections.forEach(sec => (sec.skeletons || []).forEach(v => {
        if (!v.sents_alt) return;
        const sents = W2.wrSplitEn(v.en);
        v.sents_alt.forEach(r => {
            const nbr = [sents[r.idx - 1], sents[r.idx + 1]].filter(Boolean).join(' ');
            r.alts.forEach(a => {
                const c = shared(a.en, nbr);
                if (c.length) connBad.push(`[${sec.id}] ${v.label} 与邻句共用「${c.join('/')}」`);
            });
        });
    }));

    if (connBad.length) fail('替换句与邻句撞连接词 ' + connBad.length + ' 处：' + connBad.slice(0, 4).join('；'));
    else pass('所有替换句与前后句不共用连接词（换完仍读得通）');

    console.log(ok ? '\nSWAP ALL PASS' : '\nSWAP HAS FAILURES');
    process.exit(ok ? 0 : 1);
})();
