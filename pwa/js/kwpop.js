/* 范文重点词：把范文里反复出现的提分短语标成可点项 .kw，点击弹卡看释义/用法/例句。
   样式复用查词弹卡的 .word-pop（与大作文模板里的词点同一套视觉反馈）。

   用法：
     await kwLoad();                    // 两页初始化时先加载
     kwMarkText('plain text', escFn)    // → HTML，命中片段包 .kw，其余交给 escFn
     kwBind();                          // 一次委托点击/Esc/点外部关闭
*/
/* 用 var：两个页面各自的脚本要共享同一份状态（也让 jsdom 回归能直接读到） */
var KW = null;
var KW_BY_KEY = null;
var KW_PROMISE = null;
var KW_POP = null;

const KW_LABEL = { chart: '图表描述', argue: '论证说理', advice: '建议收束', letter: '书信套语' };

async function kwLoad() {
    if (KW_PROMISE) return KW_PROMISE;
    KW_PROMISE = (async () => {
        try {
            const res = await fetch('data/writing_keywords.json', { cache: 'no-cache' });
            if (!res.ok) throw new Error('HTTP ' + res.status);
            const data = await res.json();
            KW = data;
            KW_BY_KEY = new Map();
            (data.items || []).forEach(it => KW_BY_KEY.set(it.k.toLowerCase(), it));
        } catch (e) {
            KW = { meta: {}, items: [] };
            KW_BY_KEY = new Map();
        }
        return KW;
    })();
    return KW_PROMISE;
}

/** 在纯文本里找重点短语：长词组优先、不区分大小写、两侧必须是词边界 → [{s,e,it}] */
function kwSplit(text) {
    if (!KW_BY_KEY || !KW_BY_KEY.size || !text) return null;
    const low = text.toLowerCase();
    const hits = [];
    KW_BY_KEY.forEach((it, k) => {
        let pos = 0;
        while ((pos = low.indexOf(k, pos)) !== -1) {
            const before = pos > 0 ? low[pos - 1] : '';
            const after = low[pos + k.length] || '';
            const okBefore = !/[a-z0-9]/.test(before);
            const okAfter = !/[a-z0-9]/.test(after);
            if (okBefore && okAfter) hits.push({ s: pos, e: pos + k.length, it });
            pos += k.length;
        }
    });
    if (!hits.length) return null;
    hits.sort((a, b) => a.s - b.s || (b.e - b.s) - (a.e - a.s));
    const merged = [];
    let end = -1;
    hits.forEach(h => {
        if (h.s >= end) { merged.push(h); end = h.e; }
    });
    return merged;
}

/** 纯文本 → HTML：命中的重点短语包 .kw，其余片段交给 fallback（通常是原有的标注/转义函数） */
function kwMarkText(text, fallback) {
    const esc = fallback || (s => String(s));
    if (!text) return '';
    const hits = kwSplit(text);
    if (!hits) return esc(text);
    const out = [];
    let cur = 0;
    hits.forEach(h => {
        if (h.s > cur) out.push(esc(text.slice(cur, h.s)));
        out.push('<span class="kw" data-kw="' + kwEsc(h.it.k) + '">' + kwEsc(text.slice(h.s, h.e)) + '</span>');
        cur = h.e;
    });
    if (cur < text.length) out.push(esc(text.slice(cur)));
    return out.join('');
}

function kwEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/* ==================== 弹卡 ==================== */
function kwClose() {
    if (KW_POP) { KW_POP.remove(); KW_POP = null; }
    document.querySelectorAll('.kw.on').forEach(el => el.classList.remove('on'));
}

function kwCardHtml(it) {
    const label = KW_LABEL[it.g] || '重点表达';
    return `<span class="kw-tag kw-tag-${kwEsc(it.g)}">${kwEsc(label)}</span>`
        + `<div class="wp-word kw-word">${kwEsc(it.k)}</div>`
        + `<div class="kw-cn">${kwEsc(it.cn)}</div>`
        + (it.use ? `<div class="kw-use"><b>怎么用</b>${kwEsc(it.use)}</div>` : '')
        + (it.ex ? `<div class="kw-ex"><b>例</b><span>${kwEsc(it.ex)}</span></div>` : '')
        + (it.exCn ? `<div class="kw-ex-cn">${kwEsc(it.exCn)}</div>` : '');
}

function kwOpen(el) {
    const key = (el.getAttribute('data-kw') || '').toLowerCase();
    const it = KW_BY_KEY && KW_BY_KEY.get(key);
    if (!it) return;
    kwClose();
    el.classList.add('on');
    KW_POP = document.createElement('div');
    KW_POP.className = 'word-pop kw-pop';
    KW_POP.innerHTML = kwCardHtml(it);
    document.body.appendChild(KW_POP);

    // 固定视口底部（.kw-pop CSS 定 bottom），与顶部悬浮替换卡位置分开；只算水平位置
    const r = el.getBoundingClientRect();
    const pw = KW_POP.offsetWidth;
    const vw = document.documentElement.clientWidth;
    let left = r.left;
    if (left + pw > vw - 12) left = vw - pw - 12;
    if (left < 8) left = 8;
    KW_POP.style.left = left + 'px';
}

function kwBind() {
    if (document.body.dataset.kwBound === '1') return;
    document.body.dataset.kwBound = '1';
    // 捕获阶段拦下点击：小作文的「点句看译文」也绑在祖先上，必须先停住
    document.addEventListener('click', e => {
        const el = e.target && e.target.closest ? e.target.closest('.kw') : null;
        if (el) {
            e.preventDefault();
            e.stopPropagation();
            kwOpen(el);
            return;
        }
        if (KW_POP && !(e.target.closest && e.target.closest('.kw-pop'))) kwClose();
    }, true);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') kwClose(); });
    window.addEventListener('resize', kwClose, { passive: true });
    window.addEventListener('scroll', kwClose, { passive: true });
}
