/* 熟词僻义 v2：逐词回真题语料核对义项，只收「义项 ≠ 常用义」的词
   列：单词 | 熟义 | 僻义 | 原句（英+中）｜出处 · 年份筛选（不分题型） */
let WN_ROWS = [];
let WN_YEARS = new Set();
const WN_YEARS_ON = new Set();

function wnEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

const WN_TIER = { '高': 't-hi', '中': 't-mid', '低': 't-lo' };

function wnYearsOf(r) {
    return (r.years && r.years.length ? r.years : [r.year]).filter(Boolean);
}

function wnYearChips() {
    const years = [...WN_YEARS].sort().reverse();
    const box = document.getElementById('wnYears');
    if (!box) return;
    box.innerHTML = '<span class="wn-chip-lb">按年份：</span><button class="wn-chip on" data-y="all">全部</button>' +
        years.map(y => `<button class="wn-chip" data-y="${y}">${y}</button>`).join('');
    box.querySelectorAll('.wn-chip').forEach(c => {
        c.onclick = () => {
            const y = c.dataset.y;
            if (y === 'all') WN_YEARS_ON.clear();
            else if (WN_YEARS_ON.has(y)) WN_YEARS_ON.delete(y); else WN_YEARS_ON.add(y);
            box.querySelectorAll('.wn-chip').forEach(x => {
                x.classList.toggle('on', (x.dataset.y === 'all' && WN_YEARS_ON.size === 0) || WN_YEARS_ON.has(x.dataset.y));
            });
            wnRender();
        };
    });
}

function wnRow(r) {
    const years = wnYearsOf(r);
    const cn = r.cn ? `<div class="wn-cn">${wnEsc(r.cn)}</div>`
        : `<div class="wn-cn na">（该来源译文数据不可靠，仅保留英文原句）</div>`;
    return `<tr data-year="${wnEsc(years.join(','))}" data-tier="${wnEsc(r.tier)}">
        <td class="wn-w" data-label="单词"><b>${wnEsc(r.w)}</b><span class="wn-tier ${WN_TIER[r.tier] || ''}">${wnEsc(r.tier)}</span></td>
        <td class="wn-common" data-label="熟义">${wnEsc(r.common)}</td>
        <td class="wn-uncommon" data-label="僻义">${wnEsc(r.uncommon)}</td>
        <td class="wn-en-cell" data-label="原句">
            <div class="wn-en">${wnEsc(r.en)}</div>${cn}
            <div class="wn-src">${wnEsc(r.src)}${years.length ? ' · ' + wnEsc(years.join(' · ')) : ''}</div>
        </td></tr>`;
}

function wnRender() {
    const sEl = document.getElementById('wnSearch');
    const q = (sEl ? sEl.value : '').trim().toLowerCase();
    const rows = WN_ROWS.filter(r => {
        const ys = wnYearsOf(r);
        if (WN_YEARS_ON.size && !ys.some(y => WN_YEARS_ON.has(y))) return false;
        if (!q) return true;
        return (r.w + ' ' + r.common + ' ' + r.uncommon + ' ' + r.en + ' ' + (r.cn || '')).toLowerCase().includes(q);
    });
    const cnt = document.getElementById('wnCount');
    if (cnt) cnt.textContent = `共 ${rows.length} 条` + ((WN_YEARS_ON.size || q) ? `（在 ${WN_ROWS.length} 条中筛选）` : '');
    const box = document.getElementById('wnContent');
    if (!rows.length) {
        box.innerHTML = '<p style="color:var(--text-light)">没有匹配的条目</p>';
        return;
    }
    const groups = [['高', '高价值 · 完全想不到'], ['中', '中价值 · 有距离但能猜'], ['低', '低价值 · 近义，沉底']];
    let html = '';
    for (const [t, label] of groups) {
        const sub = rows.filter(r => r.tier === t);
        if (!sub.length) continue;
        html += `<h2 class="wn-h2">${label}<small>${sub.length} 条</small></h2>
        <div class="wn-table-wrap"><table class="wn-table">
        <thead><tr><th>单词</th><th>熟义</th><th>僻义</th><th>原句（含中文译文 / 出处）</th></tr></thead>
        <tbody>${sub.map(wnRow).join('')}</tbody></table></div>`;
    }
    box.innerHTML = html;
}

async function wnInit() {
    try {
        const res = await fetch('data/wordnotes.json', { cache: 'no-cache' });
        const data = await res.json();
        WN_ROWS = data.rows || [];
        WN_ROWS.forEach(r => wnYearsOf(r).forEach(y => WN_YEARS.add(y)));
        wnYearChips();
        wnRender();
        const s = document.getElementById('wnSearch');
        if (s) s.addEventListener('input', wnRender);
    } catch (e) {
        document.getElementById('wnContent').innerHTML =
            '<p style="color:var(--text-light)">数据加载失败，请刷新重试</p>';
    }
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wnInit);
else wnInit();
