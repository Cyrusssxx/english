/* 作文押题页：加载 data/yati.json，卡片网格 + 弹层阅读器（原题图 / 范文并排）。
   规则沿用：左侧目录、每个题型默认收起、单图表→小作文→其它图表→图画 排序（数据侧已排好）。 */
let YT = null;
let YT_FLAT = [];          // 全部题目（按渲染顺序），供弹层上/下一题
let YT_CUR = -1;

const YT_GROUP_META = {
    t0: { desc: '一幅图表：柱状 · 折线 · 饼图，客观描述数据', color: '#0d9488' },
    t1: { desc: '书信 · 通知 · 纪要，格式与称谓优先', color: '#7c3aed' },
    t2: { desc: '图画 + 数据：先描述画面，再引数据佐证', color: '#2563eb' },
    t3: { desc: '两张图表：先分述，再比较与结论', color: '#0891b2' },
    t4: { desc: '一幅漫画：描述画面，点出寓意', color: '#ea580c' },
    t5: { desc: '两幅对比图：对比差异，再作评论', color: '#db2777' },
};

function ytEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function ytPad(n) { return String(n).padStart(2, '0'); }

/* ==================== 渲染 ==================== */
/* 卡片缩略图不直接给 src：默认整页 0 张图请求，展开哪组才载哪组（见 ytActivateGroup）。 */
function ytRender() {
    const host = document.getElementById('ytGroups');
    if (!host || !YT) return;
    const groups = YT.groups || [];
    YT_FLAT = [];
    host.innerHTML = groups.map((g, gi) => {
        const meta = YT_GROUP_META[g.id] || { desc: '', color: '#0d9488' };
        const cards = (g.items || []).map(it => {
            YT_FLAT.push(it);
            const key = (ytPad(it.no) + ' ' + it.title + ' ' + (it.en || '')).toLowerCase();
            const en = it.en ? `<span class="yt-card-en" title="${ytEsc(it.en)}">${ytEsc(it.en)}</span>` : '';
            return `<button type="button" class="yt-card" data-no="${it.no}" data-k="${ytEsc(key)}">
                <span class="yt-thumb"><img data-src="${ytEsc(it.img)}" alt="第 ${it.no} 题：${ytEsc(it.title)}" loading="lazy" decoding="async"></span>
                <span class="yt-card-foot">
                    <span class="yt-no">${ytPad(it.no)}</span>
                    <span class="yt-words">${it.words || ''} 词</span>
                    <span class="yt-card-title">${ytEsc(it.title)}</span>
                    ${en}
                </span>
            </button>`;
        }).join('');
        return `<details class="yt-grp" id="ytG_${ytEsc(g.id)}" data-cnt="${(g.items || []).length}" style="--ga:${meta.color}">
            <summary class="yt-grp-h">
                <span class="yt-grp-idx">${gi + 1}</span>
                <span class="yt-grp-name">${ytEsc(g.name)}</span>
                <span class="yt-grp-desc">${ytEsc(meta.desc)}</span>
                <span class="yt-grp-n">${(g.items || []).length} 题</span>
                <svg class="yt-chev" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6.5 L8 10.5 L12 6.5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </summary>
            <div class="yt-grid">${cards}</div>
        </details>`;
    }).join('');
    host.dataset.bound = '';        // innerHTML 重建 → 事件需重新绑定

    const stats = document.getElementById('ytStats');
    if (stats) {
        const total = YT_FLAT.length;
        const big = YT_FLAT.filter(it => !/书信|通知|纪要/.test(it.title) && (it.words || 0) >= 130).length;
        const wc = YT_FLAT.map(it => it.words || 0).filter(Boolean);
        const lo = Math.min.apply(null, wc), hi = Math.max.apply(null, wc);
        stats.innerHTML = [
            `<span class="yt-chip"><b>${total}</b> 篇</span>`,
            `<span class="yt-chip"><b>${groups.length}</b> 个题型</span>`,
            `<span class="yt-chip"><b>${big}</b> 大作文 · <b>${total - big}</b> 小作文</span>`,
            `<span class="yt-chip">范文 <b>${lo}–${hi}</b> 词</span>`,
        ].join('');
    }
    ytBindCards();
    ytTocBuild();
}

/* ==================== 按需加载：展开哪组载哪组，滚到哪张载哪张 ==================== */
const YT_IO = ('IntersectionObserver' in window)
    ? new IntersectionObserver(entries => {
        entries.forEach(en => {
            if (!en.isIntersecting) return;
            YT_IO.unobserve(en.target);
            ytLoadImg(en.target);
        });
    }, { rootMargin: '400px 0px' })
    : null;

function ytLoadImg(img) {
    const src = img.dataset.src;
    if (!src) return;
    delete img.dataset.src;
    img.classList.add('is-loading');
    img.addEventListener('load', () => {
        img.classList.remove('is-loading');
        img.classList.add('is-in');
        const th = img.closest('.yt-thumb');
        if (th) th.classList.add('is-ready');
    }, { once: true });
    img.addEventListener('error', () => {
        img.classList.remove('is-loading');
        img.classList.add('is-err');
        const th = img.closest('.yt-thumb');
        if (th) th.classList.add('is-ready');
    }, { once: true });
    img.src = src;
}

/* 展开一组：该组前 4 张立刻加载（基本就是首屏），其余的滚到接近视口再加载。
   默认收起状态下整页一张图都不请求。 */
function ytActivateGroup(g) {
    if (!g) return;
    const imgs = [...g.querySelectorAll('img[data-src]')];
    if (!imgs.length) return;
    imgs.slice(0, 4).forEach((img, i) => {
        if (i === 0) img.fetchPriority = 'high';
        ytLoadImg(img);
    });
    imgs.slice(4).forEach(img => {
        if (YT_IO) YT_IO.observe(img); else ytLoadImg(img);
    });
}

function ytBindCards() {
    const host = document.getElementById('ytGroups');
    if (!host || host.dataset.bound === '1') return;
    host.dataset.bound = '1';
    host.addEventListener('click', e => {
        const card = e.target.closest && e.target.closest('.yt-card');
        if (!card) return;
        ytOpen(Number(card.dataset.no), card);
    });
    // toggle 不冒泡，逐组绑定（程序化设置 open 也会触发 → 搜索/展开全部同样会载图）
    host.querySelectorAll('details.yt-grp').forEach(g => {
        g.addEventListener('toggle', () => { if (g.open) ytActivateGroup(g); });
    });
}

/* 弹层里预取上/下一题，翻页时不卡 */
function ytPrefetch(i) {
    [-1, 1].forEach(d => {
        const n = YT_FLAT[i + d];
        if (n && n.img) { const im = new Image(); im.src = n.img; }
    });
}

/* ==================== 弹层阅读器 ==================== */
function ytIndex(no) { return YT_FLAT.findIndex(it => it.no === no); }

/* 图内中文标注 → 英文写法（放范文顶部，写的时候直接抄） */
function ytNotesHtml(it) {
    const ns = it.notes || [];
    if (!ns.length) return '';
    return `<div class="yt-notes"><p class="yt-notes-h">图内文字 · 英文写法</p>` +
        ns.map(n => `<div class="yt-note"><span class="yt-note-zh">${ytEsc(n.zh)}</span><span class="yt-note-en">${ytEsc(n.en)}</span></div>`).join('') +
        `</div>`;
}

/* 范文渲染：英文整段在上，中文整段在下（默认隐藏，点工具栏按钮展开）。
   呈现方式与真题「套用示范」一致：英文衬线体、段首缩进；中文浅色块、虚线分隔、
   数字统一上金色底（.ap-own），与英文里的数字标注一一对应。 */
function ytMarkNums(html) {
    return String(html).replace(/(\d+(?:[.,]\d+)?%?)/g, '<mark class="ap-own">$1</mark>');
}

/* ---------- 骨架 / 填槽 ----------
   图表类范文前两段是按「骨架 + 填槽」写的：骨架＝固定句式（背死、原样搬），
   填槽＝每篇要换的数据和机制句。这里把骨架片段单独染色，句子剩下的成段实词
   自动判为填槽（浅琥珀），一眼能看出哪些字必须换掉。 */
const YT_SKEL_SEGS = [
    /\bThe (?:[A-Za-z]+ )?(?:charts?|graphs?|table|pictures?|diagrams?) (?:above|below) clearly illustrates?/i,
    /\bThe (?:two |three )?(?:images|materials|pictures) (?:above )?(?:clearly )?(?:illustrate|highlight|show)/i,
    /\bThis phenomenon can be attributed to a combination of factors\./i,
    /\bPrimary among these is(?: that)?/i,
    /\bEqually important,/i,
    /\bA further driver is(?: that)?/i,
    /\bDuring this period,/i,
    /\bBy contrast,/i,
    /\bIn contrast,/i,
    /\bNevertheless,/i,
    /\bTogether,/i,
    /\btakes? the lead\b/i,
    /\baccounting for\b/i,
    /\bfollowed by\b/i,
    /\bcomes? last at\b/i,
    /\brespectively\b/i,
    /\bThe findings therefore suggest(?: that)?/i,
    /\bThe figures (?:thus |therefore )?suggest(?: that)?/i,
    /\bThe figures thus reflect\b/i,
    /\bWe should bear in mind that\b/i,
    /\bof great importance\b/i,
    /\bIn this way,/i,
    // 第三段模板骨架（2026-11-20）：整句匹配，否则后半截会被误判成填槽
    // 2026-11-21：十篇第三段首尾句改为按题材定制，原三条整句规则只剩 NO8 这一句还在用，
    // 「positive trend worth welcoming」「Given the momentum…」等已成死规则，删掉。
    /\bWhether it proves to be a blessing or a burden depends on how well it is managed in the years ahead\./i,
];

/** 句中骨架片段 → 不重叠区间（同起点取最长） */
function ytSkelSpans(text) {
    const hit = [];
    YT_SKEL_SEGS.forEach(re => {
        const g = new RegExp(re.source, 'gi');
        let m;
        while ((m = g.exec(text))) {
            if (!m[0].length) { g.lastIndex++; continue; }
            hit.push({ s: m.index, e: m.index + m[0].length });
        }
    });
    if (!hit.length) return [];
    hit.sort((a, b) => a.s - b.s || (b.e - b.s) - (a.e - a.s));
    const out = [];
    let end = -1;
    hit.forEach(h => { if (h.s >= end) { out.push(h); end = h.e; } });
    return out;
}

/** 一段非骨架文本是否算「填槽」：够长且有两个以上实词（介词碎屑不算） */
function ytFillOk(t) {
    const words = (String(t).match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
    return words >= 3 && String(t).replace(/[^A-Za-z]/g, '').length >= 10;
}

/** 文本 → [{t, k:'skel'|'fill'}]，首尾拼接必须等于原文。
    有骨架：骨架蓝色高亮 + 其余浅底（fill）；
    无骨架的整句（范文原句）：整句浅底，不再是纯白底。 */
function ytSegments(text) {
    const sp = ytSkelSpans(text);
    if (!sp.length) return ytFillOk(text) ? [{ t: text, k: 'fill' }] : [{ t: text, k: '' }];
    const segs = [];
    let cur = 0;
    sp.forEach(h => {
        if (h.s > cur) { const t = text.slice(cur, h.s); segs.push({ t, k: ytFillOk(t) ? 'fill' : '' }); }
        segs.push({ t: text.slice(h.s, h.e), k: 'skel' });
        cur = h.e;
    });
    if (cur < text.length) { const t = text.slice(cur); segs.push({ t, k: ytFillOk(t) ? 'fill' : '' }); }
    return segs;
}

/* 虚词不包可点：点了也只有「这个/那个」这类没信息的释义，反而干扰点句 */
const YT_STOP = new Set(('a an the and or but of to in on at for as by with from into over under '
    + 'is are was were be been being it its this that these those there here their they them we our us '
    + 'he she his her you your i my me not no nor so than then thus such can could may might must should would will').split(' '));

/** 段内：重点短语走 .kw（弹短语卡），其余逐词包 .yt-w（点任意词查释义） */
function ytInline(text) {
    const ready = typeof kwSplit === 'function' && typeof KW_BY_KEY !== 'undefined' && KW_BY_KEY && KW_BY_KEY.size;
    const hits = ready ? (kwSplit(text) || []) : [];
    const WORD = /[A-Za-z][A-Za-z'’-]*/g;
    const plain = s => {
        let out = '', last = 0, m;
        WORD.lastIndex = 0;
        while ((m = WORD.exec(s))) {
            out += ytEsc(s.slice(last, m.index));
            const low = m[0].toLowerCase();
            out += YT_STOP.has(low) ? ytEsc(m[0])
                : `<span class="yt-w" data-w="${ytEsc(low)}">${ytEsc(m[0])}</span>`;
            last = m.index + m[0].length;
        }
        return out + ytEsc(s.slice(last));
    };
    const out = [];
    let cur = 0;
    hits.forEach(h => {
        if (h.s > cur) out.push(plain(text.slice(cur, h.s)));
        out.push(`<span class="kw" data-kw="${ytEsc(h.it.k)}">${ytEsc(text.slice(h.s, h.e))}</span>`);
        cur = h.e;
    });
    if (cur < text.length) out.push(plain(text.slice(cur)));
    return out.join('');
}

/** 英文文本 → 骨架/填槽染色 + 可点词 + 数字金底 */
function ytWordHtml(text) {
    const segs = ytSegments(String(text == null ? '' : text));
    const html = segs.map(s => s.k ? `<span class="yt-${s.k}">${ytInline(s.t)}</span>` : ytInline(s.t)).join('');
    return ytMarkNums(html);
}

/* 小作文范文里的「模板功能句」标记（2026-11-20）：
   小作文 8 篇（NO19–26）的范文中，能整句背下来套用的功能句（开头寒暄 / 来意 /
   分点过渡 / 收尾请求 / 通知纪要格式句）打上可见标记，跟每篇独有的内容血肉句区分。
   判定用句式正则——不手改数据，yati.json 由生成器产出，这里纯前端派生，幂等。
   范围锁 no>=19（小作文组），大作文图表句不参与，避免 "Thank you for" 之类误标。 */
const YT_TPL_PATTERNS = [
    /\bI hope this (?:message|email) finds you well\./i,
    /\bThanks for your (?:email|message)\./i,
    /\bI was delighted to receive your email\b/i,
    /\bWe are pleased to announce that\b/i,
    /\bI am writing to\b/i,
    /\bI believe I am well qualified\b/i,
    /\bcan be listed as follows\b/i,
    /\bPlease accept my sincere apology\b/i,
    /\bApplicants should\b/i,
    /\bPlease register\b/i,
    /\bLooking forward to your early reply\./i,
    /\bI am looking forward to hearing from you\b/i,
    /\bI look forward to seeing you\b/i,
    /\bI would appreciate it\b/i,
    /\bI would be grateful\b/i,
    /\bThank you for\b/i,
    /\bI hope you will find\b/i,
    /\bPlease let me know\b/i,
    /\bdo not hesitate to contact me\b/i,
    /\bWe are looking forward to\b/i,
    /\bI wonder if you could\b/i,
    /\bbe convenient for you\b/i,
    /\bThis is an ideal opportunity\b/i,
    /\bThe meeting aimed to\b/i,
    /\bthe meeting decided that\b/i,
    /\bThe meeting concluded with\b/i,
];
function ytIsTplSent(text, no) {
    if (!(no >= 19)) return false;
    return YT_TPL_PATTERNS.some(re => re.test(String(text || '')));
}

/** 图例：只列本篇真的出现的标记；空图例不渲染 */
function ytLegendHtml(hasSkel, hasTpl, hasSwap) {
    return `<div class="yt-legend">`
        + (hasSkel ? `<span class="yt-lg"><i class="yt-lg-skel">骨架</i>固定句式，原样背</span>` : '')
        + (hasTpl ? `<span class="yt-lg"><i class="yt-lg-tpl">模板</i>可整句套用的功能句</span>` : '')
        + (hasSwap ? `<span class="yt-lg"><i class="yt-lg-swap">替换</i>悬停看整句换法</span>` : '')
        + `<span class="yt-lg"><i class="yt-lg-num">65%</i>数据</span>`
        + `<span class="yt-lg"><i class="yt-lg-kw">词组</i>可点查释义</span>`
        + `</div>`;
}

/* ---------- 点词查释义（全文逐词可点，与阅读页同一份词典） ---------- */
let YT_WPOP = null;

function ytWClose() {
    if (YT_WPOP) { YT_WPOP.remove(); YT_WPOP = null; }
    document.querySelectorAll('.yt-w.on').forEach(el => el.classList.remove('on'));
}

function ytWOpen(el) {
    const word = el.getAttribute('data-w') || '';
    const entry = (typeof dictLookup === 'function') ? dictLookup(word) : null;
    if (typeof wrSwClose === 'function') wrSwClose();   // 点词时先收起整句替换气泡
    ytWClose();
    const pop = document.createElement('div');
    pop.className = 'word-pop kw-pop yt-wpop';
    pop.innerHTML = `<span class="wp-word">${ytEsc(el.textContent)}</span>`
        + `<span class="wp-phonetic">${ytEsc(entry ? (entry.p || '') : '')}</span>`
        + `<div class="wp-meaning">${entry ? ytEsc(entry.t || '') : '（常用词，离线词典只收难词）'}</div>`
        + (entry && typeof freqBadge === 'function' ? freqBadge(word) : '');
    document.body.appendChild(pop);
    YT_WPOP = pop;
    el.classList.add('on');
    const r = el.getBoundingClientRect();
    const pw = pop.offsetWidth, ph = pop.offsetHeight;
    const vw = document.documentElement.clientWidth, vh = document.documentElement.clientHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + vw - 12) left = window.scrollX + vw - pw - 12;
    if (left < window.scrollX + 8) left = window.scrollX + 8;
    let top = r.bottom + window.scrollY + 7;
    if (top + ph > window.scrollY + vh - 12) {
        const up = r.top + window.scrollY - ph - 7;
        top = up > window.scrollY + 8 ? up : Math.max(window.scrollY + 8, window.scrollY + vh - ph - 12);
    }
    pop.style.left = left + 'px';
    pop.style.top = top + 'px';
}

function ytWBind() {
    if (document.body.dataset.ytWBound === '1') return;
    document.body.dataset.ytWBound = '1';
    document.addEventListener('keydown', e => { if (e.key === 'Escape') ytWClose(); });
    document.addEventListener('click', e => {
        if (!e.target.closest) return;
        if (e.target.closest('.yt-w, .yt-wpop')) return;
        ytWClose();
    });
    window.addEventListener('resize', ytWClose, { passive: true });
    window.addEventListener('scroll', ytWClose, { passive: true });
}

/* 范文渲染（完全对齐真题「套用示范」）：
   · 英文衬线体 + 段首缩进，数字金底，重点词/短语可点查释义（复用词典）；
   · 每句包 .yt-jsent，句末独立「译」标记（.yt-sent-tr）点开该句中文（.yt-jsent-cn）；
     句子正文与点词都不触发展开，只有点「译」才翻译整句——两套交互互不抢；
   · 工具栏「显示逐句译文」/「显示全文译文」两个按钮各自独立；
   · 三套中文互不冲突：逐句（句末译标记）/ 一键逐句 / 整篇。 */
function ytEssayHtml(it) {
    const blocks = it.blocks || [];
    if (!blocks.length) return '<p class="ye-empty">暂无范文。</p>';
    const clsOf = b => ({ h: 'ye-h', meta: 'ye-meta', sign: 'ye-sign', p: '' }[b.k] || '');
    const sentsOf = b => (Array.isArray(b.sents) && b.sents.length) ? b.sents : null;
    const para = (cls, inner) => `<p${cls ? ` class="${cls}"` : ''}>${inner}</p>`;
    let n = 0;   // 全局句号，句译块按号定位
    /* 小作文 meta 块（日期 / 时间 / 地点 / 记录人）一行一条，不挤成一段 */
    const metaLines = (ss, pick) => ss.map(s => para('ye-meta', ytMarkNums(ytEsc(pick(s))))).join('');

    const enParts = [], cnParts = [];
    let skelN = 0;   // 有骨架片段才显示对应图例项
    let tplN = 0;    // 模板功能句（小作文）数量
    const hasSwap = blocks.some(b => (b.sents || []).some(s => s.swap && (s.swap.alts || []).length));
    blocks.forEach((b, bi) => {
        const ss = sentsOf(b);
        if (!ss) {
            enParts.push(para(clsOf(b), ytWordHtml(b.v || '')));
            cnParts.push(para(clsOf(b), ytMarkNums(ytEsc(b.cn || ''))));
            return;
        }
        if (b.k === 'meta') {
            enParts.push(metaLines(ss, s => s.en));
            cnParts.push(metaLines(ss, s => s.cn || ''));
            return;
        }
        // 英文段：逐句可点 + 句译块（点句看该句中文；整篇中文由工具栏按钮控制）
        let inner = ss.map(s => {
            const i = n++;
            const h = ytWordHtml(s.en);
            // 图例「骨架」只认真骨架片段；.yt-fill 是小作文整句当填槽用的容器，不算骨架
            if (h.indexOf('class="yt-skel"') >= 0) skelN++;
            // 模板功能句：整句加高亮（与骨架同一套视觉），不再逐句插「模板」角标——
            // 每句前面挂一个徽章太碎，用户 2026-11-21 要求「参考骨架打高亮就行」。
            const isTpl = ytIsTplSent(s.en, it.no);
            if (isTpl) tplN++;
            // 整句可替换：默认仍显示原句，悬停/点击看「更贴这道题」的写法（气泡由 common.js 统一渲染）
            const cls = 'yt-jsent' + (isTpl ? ' yt-tpl' : '')
                + ((s.swap && s.swap.alts && s.swap.alts.length) ? ' yt-swap' : '');
            const swapAttr = (s.swap && s.swap.alts && s.swap.alts.length)
                // 附上本句译文：气泡里「当前表达」下面直接给中文，不用再点「译」
                ? ` class="${cls}" data-swap="${ytEsc(JSON.stringify(Object.assign({}, s.swap, { orig: s.en, cn: s.cn || '' })))}"`
                : ` class="${cls}"`;
            // 「译」标记放在 .yt-jsent 之外做兄弟节点：句子 textContent 仍严格等于原文（校验不吞字），
            // 又能独立按 data-tr 触发该句译文；句子正文/单词都不响应翻译。
            return `<span${swapAttr} data-i="${i}">${h}</span>`
                + `<button type="button" class="yt-sent-tr" data-tr="${i}" title="看本句中文">译</button>`
                + `<span class="yt-jsent-cn" data-for="${i}" hidden>${ytMarkNums(ytEsc(s.cn || ''))}</span>`;
        }).join(' ');
        const cnText = ss.map(s => s.cn || '').join('');
        enParts.push(para(clsOf(b), inner));
        cnParts.push(para(clsOf(b), ytMarkNums(ytEsc(cnText))));
    });
    const showLegend = skelN || tplN || hasSwap;
    return `<div class="yt-en">${showLegend ? ytLegendHtml(skelN, tplN, hasSwap) : ''}${enParts.join('')}</div><div class="yt-cn" hidden>${cnParts.join('')}</div>`;
}

/** 单句译块开合（同步 .yt-jsent.on 状态标记；按用户要求不渲染高亮/下划线）；cnBox 为 .yt-jsent-cn */
function ytSentCnShow(cnBox, show) {
    if (!cnBox) return;
    cnBox.hidden = !show;
    const i = cnBox.dataset.for;
    const p = cnBox.parentElement;
    const s = p && p.querySelector('.yt-jsent[data-i="' + i + '"]');
    if (s) s.classList.toggle('on', show);
    const tr = p && p.querySelector('.yt-sent-tr[data-tr="' + i + '"]');
    if (tr) { tr.classList.toggle('on', show); tr.title = show ? '收起本句中文' : '看本句中文'; }
}

/** 全文翻译：只切整篇中文对照块 .yt-cn，不碰逐句译块（两个按钮互不干扰） */
function ytToggleCn(btn) {
    const pane = btn.closest('.yt-pane-txt');
    if (!pane) return;
    const cn = pane.querySelector('.yt-cn');
    if (!cn) return;
    const show = cn.hidden;
    cn.hidden = !show;
    btn.textContent = show ? '隐藏全文译文' : '显示全文译文';
    btn.classList.toggle('on', show);
}

/** 逐句翻译：一键展开 / 收起所有逐句译块，不碰整篇对照块（与全文按钮互不干扰） */
function ytToggleSentCn(btn) {
    const pane = btn.closest('.yt-pane-txt');
    if (!pane) return;
    const boxes = [...pane.querySelectorAll('.yt-jsent-cn')];
    if (!boxes.length) return;
    // 有收起的就全部展开；已经全展开才收起——与单句点开的状态也合得来
    const show = boxes.some(b => b.hidden);
    boxes.forEach(box => ytSentCnShow(box, show));
    btn.textContent = show ? '隐藏逐句译文' : '显示逐句译文';
    btn.classList.toggle('on', show);
}

function ytOpen(no, fromEl) {
    const idx = ytIndex(no);
    if (idx < 0) return;
    if (typeof wrSwClose === 'function') wrSwClose();   // 换题先收起上一题的替换气泡
    YT_CUR = idx;
    const it = YT_FLAT[idx];
    const box = document.getElementById('ytModal');
    if (!box) return;
    document.getElementById('ytMNo').textContent = ytPad(it.no);
    document.getElementById('ytMTitle').textContent = it.title;
    let typeName = '';
    (YT.groups || []).forEach(g => { if ((g.items || []).some(x => x.no === it.no)) typeName = g.name; });
    document.getElementById('ytMSub').textContent = `${typeName} · ${it.words || 0} 词`;
    const enEl = document.getElementById('ytMEn');
    if (enEl) {
        enEl.textContent = it.en || '';
        enEl.hidden = !it.en;
    }
    const img = document.getElementById('ytMImg');
    img.classList.remove('is-in', 'is-err', 'is-loading');
    img.src = it.img;
    img.alt = `第 ${it.no} 题：${it.title}`;
    const essayEl = document.getElementById('ytMEssay');
    essayEl.innerHTML = ytNotesHtml(it) + ytEssayHtml(it);
    essayEl.scrollTop = 0;
    const cnBtn = document.getElementById('ytCnBtn');
    if (cnBtn) { cnBtn.textContent = '显示全文译文'; cnBtn.classList.remove('on'); }
    const sentBtn = document.getElementById('ytSentBtn');
    if (sentBtn) { sentBtn.textContent = '显示逐句译文'; sentBtn.classList.remove('on'); }
    ytPrefetch(idx);
    document.getElementById('ytMCnt').textContent = `${idx + 1} / ${YT_FLAT.length}`;
    document.getElementById('ytPrev').disabled = idx === 0;
    document.getElementById('ytNext').disabled = idx === YT_FLAT.length - 1;
    const essayPane = box.querySelector('.yt-pane-txt');
    if (essayPane) essayPane.scrollTop = 0;
    box.hidden = false;
    document.body.classList.add('yt-modal-open');
    if (fromEl) ytLastFocus = fromEl;
    ytSetPane(window.innerWidth <= 900 ? 'img' : 'both');
}

let ytLastFocus = null;
function ytClose() {
    const box = document.getElementById('ytModal');
    if (!box || box.hidden) return;
    box.hidden = true;
    document.body.classList.remove('yt-modal-open');
    if (ytLastFocus && ytLastFocus.focus) ytLastFocus.focus();
    ytLastFocus = null;
    YT_CUR = -1;
}
function ytStep(d) {
    if (YT_CUR < 0) return;
    const n = YT_CUR + d;
    if (n < 0 || n >= YT_FLAT.length) return;
    ytOpen(YT_FLAT[n].no);
}
function ytSetPane(p) {
    const box = document.getElementById('ytModal');
    if (!box) return;
    box.dataset.pane = p;
    box.querySelectorAll('#ytMTabs button').forEach(b => b.classList.toggle('on', b.dataset.pane === p));
}

/* ==================== 搜索 / 展开全部 ==================== */
function ytFilter(q) {
    q = (q || '').trim().toLowerCase();
    const grps = [...document.querySelectorAll('.yt-grp')];
    let total = 0;
    grps.forEach(g => {
        let shown = 0;
        g.querySelectorAll('.yt-card').forEach(c => {
            const hit = !q || (c.dataset.k || '').indexOf(q) >= 0;
            c.hidden = !hit;
            if (hit) shown++;
        });
        g.hidden = shown === 0;
        g.querySelector('.yt-grp-n').textContent = shown + ' 题';
        if (q) g.open = shown > 0;
        else g.open = false;                       // 清空搜索回到「默认全部收起」
        total += shown;
    });
    const empty = document.getElementById('ytEmpty');
    if (empty) empty.hidden = total > 0;
}

function ytToggleAll() {
    const grps = [...document.querySelectorAll('.yt-grp')].filter(g => !g.hidden);
    const open = grps.some(g => !g.open);
    grps.forEach(g => { g.open = open; });
    const btn = document.getElementById('ytToggleAll');
    if (btn) btn.textContent = open ? '收起全部' : '展开全部';
}

/* ==================== 左侧悬浮目录（复用大作文页 .wr-toc） ==================== */
const YT_TOC_KEY = 'yt_toc_fold_v1';
const YT_TOC_NARROW = 1180;
let YT_LINKS = [];

function ytNavH() {
    const n = document.querySelector('.navbar');
    if (n && n.dataset.collapsed === '1') return 0;
    const h = n ? n.getBoundingClientRect().height : 56;
    return h >= 20 ? h : 56;
}
function ytTocBuild() {
    const list = document.getElementById('ytTocList');
    if (!list) return;
    document.documentElement.style.setProperty('--nav-h', ytNavH() + 'px');
    list.innerHTML = (YT.groups || []).map(g => {
        const meta = YT_GROUP_META[g.id] || {};
        return `<a class="lv1" href="#ytG_${ytEsc(g.id)}" data-t="ytG_${ytEsc(g.id)}" style="--ga:${meta.color || '#0d9488'}">${ytEsc(g.name)} <span class="yt-toc-n">${(g.items || []).length}</span></a>`;
    }).join('');
    let folded = false;
    try { folded = localStorage.getItem(YT_TOC_KEY) === '1'; } catch (e) { /* ignore */ }
    ytTocApplyFold(folded || window.innerWidth <= YT_TOC_NARROW);
    YT_LINKS = [...list.querySelectorAll('a[data-t]')];
    list.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-t]');
        if (!a) return;
        e.preventDefault();
        const el = document.getElementById(a.dataset.t);
        if (!el) return;
        if (el.tagName === 'DETAILS' && !el.open) el.open = true;
        const y = el.getBoundingClientRect().top + window.scrollY - ytNavH() - 12;
        window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
        if (window.innerWidth <= YT_TOC_NARROW) ytTocClose();
    });
    window.addEventListener('scroll', ytSpy, { passive: true });
    window.addEventListener('resize', () => {
        document.documentElement.style.setProperty('--nav-h', ytNavH() + 'px');
        if (window.innerWidth > YT_TOC_NARROW) ytTocClose();
    });
    window.addEventListener('navheightchange', () => document.documentElement.style.setProperty('--nav-h', ytNavH() + 'px'));
    ytSpy();
}
function ytSpy() {
    const list = document.getElementById('ytTocList');
    if (!list || !YT_LINKS.length) return;
    if (document.body.classList.contains('wr-toc-folded') && window.innerWidth > YT_TOC_NARROW) return;
    const top = ytNavH() + 24;
    let cur = YT_LINKS[0];
    for (const a of YT_LINKS) {
        const el = document.getElementById(a.dataset.t);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= top) cur = a; else break;
    }
    YT_LINKS.forEach(a => a.classList.toggle('on', a === cur));
    if (cur && list.scrollHeight > list.clientHeight + 4) {
        const r = cur.getBoundingClientRect(), lr = list.getBoundingClientRect();
        if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - 24;
    }
}
function ytTocApplyFold(folded) {
    document.body.classList.toggle('wr-toc-folded', !!folded);
    try { localStorage.setItem(YT_TOC_KEY, folded ? '1' : '0'); } catch (e) { /* ignore */ }
    if (folded && !document.body.classList.contains('wr-toc-open')) ytTocClose();
}
function ytTocToggleFold() { ytTocApplyFold(!document.body.classList.contains('wr-toc-folded')); }
function ytTocOpen() {
    if (window.innerWidth <= YT_TOC_NARROW) {
        document.body.classList.add('wr-toc-open');
        const m = document.getElementById('ytTocMask');
        if (m) m.hidden = false;
    } else { ytTocApplyFold(false); }
    ytSpy();
}
function ytTocClose() {
    document.body.classList.remove('wr-toc-open');
    const m = document.getElementById('ytTocMask');
    if (m) m.hidden = true;
}

/* ==================== 启动 ==================== */
function ytBindUi() {
    const modal = document.getElementById('ytModal');
    if (modal) {
        modal.addEventListener('click', e => {
            if (e.target.closest && e.target.closest('[data-close]')) ytClose();
        });
        modal.querySelectorAll('#ytMTabs button').forEach(btn => {
            btn.addEventListener('click', () => ytSetPane(btn.dataset.pane));
        });
        const cnBtn = document.getElementById('ytCnBtn');
        if (cnBtn) cnBtn.addEventListener('click', () => ytToggleCn(cnBtn));
        const sentBtn = document.getElementById('ytSentBtn');
        if (sentBtn) sentBtn.addEventListener('click', () => ytToggleSentCn(sentBtn));
        // 范文点击委托（重渲染后仍有效）：点词查释义 / 点句末「译」翻译整句 / 点译块收起——三者互不抢
        const essay = document.getElementById('ytMEssay');
        if (essay) essay.addEventListener('click', e => {
            if (!e.target.closest) return;
            const cnBox = e.target.closest('.yt-jsent-cn');
            if (cnBox) { ytSentCnShow(cnBox, false); return; }       // 点打开的译块 → 收起
            const tr = e.target.closest('.yt-sent-tr');
            if (tr && tr.dataset.tr != null) {                      // 只认句末「译」标记 → 开合该句译文
                const cn = essay.querySelector('.yt-jsent-cn[data-for="' + tr.dataset.tr + '"]');
                if (cn) ytSentCnShow(cn, cn.hidden);
                return;
            }
            const w = e.target.closest('.yt-w');
            if (w) { e.stopPropagation(); ytWOpen(w); return; }     // 点词查释义，不展开句译
            // 点句子正文不再触发展开：翻译只走「译」标记，避免与点词抢事件
        });
        const prev = document.getElementById('ytPrev'), next = document.getElementById('ytNext');
        if (prev) prev.addEventListener('click', () => ytStep(-1));
        if (next) next.addEventListener('click', () => ytStep(1));
    }
    const search = document.getElementById('ytSearch');
    if (search) {
        let tm = null;
        search.addEventListener('input', () => {
            clearTimeout(tm);
            tm = setTimeout(() => ytFilter(search.value), 120);
        });
    }
    const all = document.getElementById('ytToggleAll');
    if (all) all.addEventListener('click', ytToggleAll);
    document.addEventListener('keydown', e => {
        const box = document.getElementById('ytModal');
        const open = box && !box.hidden;
        if (e.key === 'Escape') {
            if (open) ytClose(); else ytTocClose();
            return;
        }
        if (!open) return;
        if (e.key === 'ArrowLeft') { e.preventDefault(); ytStep(-1); }
        if (e.key === 'ArrowRight') { e.preventDefault(); ytStep(1); }
    });
}

async function ytInit() {
    ytBindUi();
    // 范文重点词可点查释义：先加载词库再绑定（词典就绪后需重渲染一次，让词标注生效）
    if (typeof kwBind === 'function') kwBind();
    ytWBind();
    // 逐词可点依赖难词词典（dict.js），与阅读页同一份，延迟加载
    if (typeof loadDict === 'function') loadDict().catch(() => {});
    if (typeof kwLoad === 'function') {
        kwLoad().then(() => {
            if (YT_CUR >= 0 && YT_FLAT[YT_CUR]) {
                const e = document.getElementById('ytMEssay');
                if (e) {
                    e.innerHTML = ytNotesHtml(YT_FLAT[YT_CUR]) + ytEssayHtml(YT_FLAT[YT_CUR]);
                    // 重渲染会新建译块与对照块；按钮若已开，按按钮状态恢复，避免文案与内容脱节
                    const sentBtn = document.getElementById('ytSentBtn');
                    const cnBtn = document.getElementById('ytCnBtn');
                    if (sentBtn && sentBtn.classList.contains('on'))
                        e.querySelectorAll('.yt-jsent-cn').forEach(box => ytSentCnShow(box, true));
                    if (cnBtn && cnBtn.classList.contains('on')) {
                        const cn = e.querySelector('.yt-cn');
                        if (cn) cn.hidden = false;
                    }
                }
            }
        }).catch(() => {});
    }
    const s = document.getElementById('darkState');
    if (s && document.documentElement.classList.contains('dark')) s.textContent = '开';
    try {
        const res = await fetch('data/yati.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        YT = await res.json();
    } catch (e) {
        const h = document.getElementById('ytGroups');
        if (h) h.innerHTML = '<p class="yt-err">押题数据加载失败，请刷新重试。</p>';
        return;
    }
    ytRender();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ytInit);
else ytInit();
