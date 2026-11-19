/* 范文重点词验证：
   ① kwMarkText 纯逻辑（长词组优先、词边界、转义）
   ② 小作文整信范文里出现 .kw，点击弹卡有释义/用法/例句，Esc 关闭
   ③ 大作文页 renderApplyBody 里的范文也带 .kw（能渲染则查，渲染失败只警告） */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');

const PWA = path.join(__dirname, '..', 'pwa');
const read = p => fs.readFileSync(path.join(PWA, p), 'utf8');
const KW = read('data/writing_keywords.json');
const SMALL = read('data/small_writing.json');

let ok = true;
const fail = m => { ok = false; console.log('FAIL ' + m); };
const pass = m => console.log('OK   ' + m);
const wait = ms => new Promise(r => setTimeout(r, ms));

function makeDom(page) {
    const dom = new JSDOM(read(page), { runScripts: 'outside-only', url: 'http://localhost/' + page, pretendToBeVisual: true });
    const w = dom.window;
    w.fetch = url => {
        const u = String(url);
        let body = null;
        if (u.indexOf('writing_keywords.json') >= 0) body = KW;
        else if (u.indexOf('small_writing.json') >= 0) body = SMALL;
        else if (u.indexOf('writing_templates.json') >= 0) body = read('data/writing_templates.json');
        else if (u.indexOf('writing_apply.json') >= 0) body = read('data/writing_apply.json');
        else if (u.indexOf('.json') >= 0) body = '{}';
        return Promise.resolve({
            ok: body !== null, status: body !== null ? 200 : 404,
            json: () => Promise.resolve(JSON.parse(body || '{}')),
        });
    };
    const nav = w.document.querySelector('.navbar');
    if (nav) nav.dataset.collapsed = '0';
    return dom;
}

(async () => {
    /* ---------- ① 纯逻辑 ---------- */
    {
        const dom = makeDom('smallwriting.html');
        const w = dom.window;
        try { w.eval(read('js/kwpop.js')); } catch (e) { fail('kwpop.js 执行异常 ' + e.message); }
        const kwData = await w.kwLoad();
        const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

        const n = (kwData.items || []).length;
        if (n < 30) fail('词库条数 ' + n); else pass('词库加载 ' + n + ' 条');

        const html = w.kwMarkText('We should bear in mind that this is of great importance.', esc);
        if ((html.match(/class="kw"/g) || []).length !== 2) fail('一条句子里命中数不对: ' + html);
        else pass('两个重点短语都标成 .kw');

        const neg = w.kwMarkText('The bearing is imported.', esc);   // 不能把 bearing 当 bear in mind
        if (neg.indexOf('class="kw"') >= 0) fail('词边界失效: ' + neg);
        else pass('词边界正确（bearing 不命中 bear in mind）');

        const lt = w.kwMarkText('use <b> tags', esc);
        if (lt.indexOf('&lt;b&gt;') < 0) fail('未转义 HTML: ' + lt);
        else pass('转义正常（<b> 不被当标签）');

        const longFirst = w.kwMarkText('a combination of factors matter', esc);
        if (longFirst.indexOf('data-kw="a combination of factors"') < 0) fail('长词组未优先: ' + longFirst);
        else pass('长词组优先匹配');
    }

    /* ---------- ② 小作文整信 ---------- */
    {
        const dom = makeDom('smallwriting.html');
        const w = dom.window;
        const d = w.document;
        try { w.eval(read('js/common.js')); } catch (e) { /* common 依赖少量 API，忽略 */ }
        try { w.eval(read('js/kwpop.js')); } catch (e) { fail('kwpop.js 异常 ' + e.message); }
        try { w.eval(read('js/smallwriting.js')); } catch (e) { fail('smallwriting.js 异常 ' + e.message + '\n' + e.stack); }
        await wait(400);

        const letter = d.getElementById('swLetter');
        const kws = letter ? [...letter.querySelectorAll('.kw')] : [];
        if (!kws.length) fail('小作文整信里没有 .kw（重点词未接入）');
        else pass('小作文整信范文出现 ' + kws.length + ' 处可点重点词');

        if (kws.length) {
            const first = kws[0];
            const key = first.getAttribute('data-kw');
            first.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));
            await wait(30);
            const pop = d.querySelector('.kw-pop');
            if (!pop) fail('点击 .kw 未弹出卡');
            else {
                const hasKey = pop.textContent.toLowerCase().indexOf(key.toLowerCase()) >= 0;
                const hasCn = !!pop.querySelector('.kw-cn');
                const hasUse = !!pop.querySelector('.kw-use');
                const hasEx = !!pop.querySelector('.kw-ex');
                if (!hasKey || !hasCn || !hasUse || !hasEx) {
                    fail(`弹卡内容不全 key=${hasKey} 释义=${hasCn} 用法=${hasUse} 例句=${hasEx}`);
                } else pass('点击弹卡：词条 + 释义 + 用法 + 例句齐全');

                // 点句看译文不应被同时触发（capture 阶段应已拦下）
                const cnOpen = [...letter.querySelectorAll('.sw-ls-cn')].filter(x => !x.hidden).length;
                if (cnOpen > 1) fail('点重点词时误触发了句译展开 ' + cnOpen);
                else pass('点重点词不误触「点句看译文」');

                d.dispatchEvent(new w.KeyboardEvent('keydown', { key: 'Escape' }));
                if (d.querySelector('.kw-pop')) fail('Esc 未关闭弹卡'); else pass('Esc 关闭弹卡');
            }
        }

        // 占位符芯片仍在，且没有把芯片文字包进 .kw
        const ph = letter ? letter.querySelectorAll('.sw-ph') : [];
        if (!ph.length) fail('整信里占位符芯片丢失');
        else pass('占位符芯片保留 ' + ph.length + ' 个');
        const badPh = [...ph].filter(x => x.querySelector('.kw'));
        if (badPh.length) fail('占位符芯片内被塞了 .kw'); else pass('芯片内无 .kw 污染');

        // 每种题型（书信/通知/致谢/会议纪要…）的整信都要有可点重点词
        const tabs = [...d.querySelectorAll('#swTypeTabs button[data-t]')];
        const empty = [];
        for (const t of tabs) {
            t.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
            await wait(70);
            const n2 = d.querySelectorAll('#swLetter .kw').length;
            if (!n2) empty.push(t.textContent.trim());
        }
        if (!tabs.length) fail('题型页签缺失');
        else if (empty.length) fail('这些题型整信无重点词：' + empty.join(' / '));
        else pass(tabs.length + ' 种题型的整信都有可点重点词');
    }

    /* ---------- ③ 大作文页 ---------- */
    {
        const dom = makeDom('writing.html');
        const w = dom.window;
        const d = w.document;
        ['js/common.js', 'js/dict.js', 'js/storage.js', 'js/kwpop.js', 'js/writing.js'].forEach(f => {
            try { w.eval(read(f)); } catch (e) { /* 词典/存储等依赖浏览器 API，失败不影响渲染检查 */ }
        });
        await wait(900);
        const content = d.getElementById('wrContent');
        const kws = content ? [...content.querySelectorAll('.kw')] : [];
        if (!kws.length) fail('大作文页范文/模板里没有 .kw');
        else pass('大作文页出现 ' + kws.length + ' 处可点重点词');
    }

    console.log(ok ? '\nKW ALL PASS' : '\nKW HAS FAILURES');
    process.exit(ok ? 0 : 1);
})();
