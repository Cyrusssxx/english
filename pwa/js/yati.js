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
function ytRender() {
    const host = document.getElementById('ytGroups');
    if (!host || !YT) return;
    const groups = YT.groups || [];
    YT_FLAT = [];
    host.innerHTML = groups.map((g, gi) => {
        const meta = YT_GROUP_META[g.id] || { desc: '', color: '#0d9488' };
        const cards = (g.items || []).map(it => {
            YT_FLAT.push(it);
            const key = (ytPad(it.no) + ' ' + it.title).toLowerCase();
            return `<button type="button" class="yt-card" data-no="${it.no}" data-k="${ytEsc(key)}">
                <span class="yt-thumb"><img src="${ytEsc(it.img)}" alt="第 ${it.no} 题：${ytEsc(it.title)}" loading="lazy" decoding="async"></span>
                <span class="yt-card-foot">
                    <span class="yt-no">${ytPad(it.no)}</span>
                    <span class="yt-card-title">${ytEsc(it.title)}</span>
                    <span class="yt-words">${it.words || ''} 词</span>
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

function ytBindCards() {
    const host = document.getElementById('ytGroups');
    if (!host || host.dataset.bound === '1') return;
    host.dataset.bound = '1';
    host.addEventListener('click', e => {
        const card = e.target.closest && e.target.closest('.yt-card');
        if (!card) return;
        ytOpen(Number(card.dataset.no), card);
    });
}

/* ==================== 弹层阅读器 ==================== */
function ytIndex(no) { return YT_FLAT.findIndex(it => it.no === no); }

function ytEssayHtml(it) {
    const blocks = it.blocks || [];
    if (!blocks.length) return '<p class="ye-empty">暂无范文。</p>';
    return blocks.map(b => {
        const cls = { h: 'ye-h', meta: 'ye-meta', sign: 'ye-sign', p: '' }[b.k] || '';
        return `<p${cls ? ` class="${cls}"` : ''}>${ytEsc(b.v)}</p>`;
    }).join('');
}

function ytOpen(no, fromEl) {
    const idx = ytIndex(no);
    if (idx < 0) return;
    YT_CUR = idx;
    const it = YT_FLAT[idx];
    const box = document.getElementById('ytModal');
    if (!box) return;
    document.getElementById('ytMNo').textContent = ytPad(it.no);
    document.getElementById('ytMTitle').textContent = it.title;
    let typeName = '';
    (YT.groups || []).forEach(g => { if ((g.items || []).some(x => x.no === it.no)) typeName = g.name; });
    document.getElementById('ytMSub').textContent = `${typeName} · ${it.words || 0} 词`;
    const img = document.getElementById('ytMImg');
    img.src = it.img;
    img.alt = `第 ${it.no} 题：${it.title}`;
    document.getElementById('ytMOpen').href = it.img;
    document.getElementById('ytMEssay').innerHTML = ytEssayHtml(it);
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
