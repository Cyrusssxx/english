/* 27 押题作文页：加载 data/yati.json，按类型分组渲染原题图 + 配套范文。
   左侧目录复用大作文页 .wr-toc 骨架；各组默认收起。 */
let YT = null;

function ytEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/* ==================== 渲染 ==================== */
function ytRender() {
    const host = document.getElementById('ytGroups');
    if (!host || !YT) return;
    const groups = YT.groups || [];
    host.innerHTML = groups.map((g, gi) => {
        const cards = (g.items || []).map(it => {
            const src = it.src ? `<span class="yt-src">${ytEsc(it.src)}</span>` : '';
            const essay = (it.essay || '').trim();
            return `<details class="yt-card" id="ytQ_${it.no}">
                <summary class="yt-card-h">
                    <span class="yt-no">${String(it.no).padStart(2, '0')}</span>
                    <span class="yt-card-title">${ytEsc(it.title)}</span>${src}
                    <span class="yt-card-arrow">▾</span>
                </summary>
                <div class="yt-card-body">
                    <figure class="yt-fig">
                        <a href="${ytEsc(it.img)}" target="_blank" rel="noopener" title="点击查看大图">
                            <img data-src="${ytEsc(it.img)}" loading="lazy" alt="第${it.no}题：${ytEsc(it.title)}">
                        </a>
                        <figcaption>第 ${it.no} 题原题图 · 点击查看大图</figcaption>
                    </figure>
                    <details class="yt-essay">
                        <summary class="yt-essay-h">📖 配套范文 <span>（点开查看，先自己写再看）</span></summary>
                        <pre class="yt-essay-body">${ytEsc(essay)}</pre>
                    </details>
                </div>
            </details>`;
        }).join('');
        return `<section class="yt-group yt-wg" id="ytG_${ytEsc(g.id)}">
            <h2 class="wr-h2 yt-group-h"><span class="yt-group-icon">${gi + 1}</span>${ytEsc(g.name)}<span class="yt-group-n">${(g.items || []).length} 题</span></h2>
            <div class="yt-cards">${cards}</div>
        </section>`;
    }).join('');
    // 图片懒加载：Observer 或立即替换（简单起见直接把 data-src 赋给 src）
    host.querySelectorAll('img[data-src]').forEach(img => { img.src = img.getAttribute('data-src'); });
    const tip = document.getElementById('ytTip');
    if (tip) tip.textContent = '共 26 题 · 18 大作文 + 8 小作文 · 默认全部收起';
    const foot = document.getElementById('ytFoot');
    if (foot) foot.textContent = '数据来源：27考研英语作文押题精选（题目原图）+ 配套范文（AI归来版模板改写）';
    ytTocBuild();
}

/* ==================== 展开/收起全部 ==================== */
function ytToggleAll() {
    const cards = [...document.querySelectorAll('#ytGroups details.yt-card')];
    const open = cards.some(c => !c.open);
    cards.forEach(c => { c.open = open; });
    const btn = document.getElementById('ytExpandAll');
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
    list.innerHTML = (YT.groups || []).map(g =>
        `<a class="lv1" href="#ytG_${ytEsc(g.id)}" data-t="ytG_${ytEsc(g.id)}">${ytEsc(g.name)} <span class="yt-toc-n">${(g.items || []).length}</span></a>`
    ).join('');
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
async function ytInit() {
    document.addEventListener('keydown', e => { if (e.key === 'Escape') ytTocClose(); });
    const s = document.getElementById('darkState');
    if (s && document.documentElement.classList.contains('dark')) s.textContent = '开';
    try {
        const res = await fetch('data/yati.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        YT = await res.json();
    } catch (e) {
        const h = document.getElementById('ytGroups');
        if (h) h.innerHTML = '<p class="wr-loading">押题数据加载失败，请刷新重试。</p>';
        return;
    }
    ytRender();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ytInit);
else ytInit();
