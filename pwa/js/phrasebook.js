/* 熟词短语：按出处文章主题分 5 类（政法 / 商业经济 / 科学科技 / 教育文化历史 / 社会生活）
   数据：pwa/data/phrasebook.json（tools/wn2.py build 生成） */
let PH_DATA = null;
let PH_YEARS = new Set();
const PH_YEARS_ON = new Set();

function phEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function phAll() {
    if (!PH_DATA) return [];
    return (PH_DATA.cats || []).flatMap(c => (PH_DATA.groups[c] || []).map(x => Object.assign({ cat: c }, x)));
}

function phYearChips() {
    const box = document.getElementById('phYears');
    if (!box) return;
    const years = [...PH_YEARS].sort().reverse();
    box.innerHTML = '<span class="wn-chip-lb">按年份：</span><button class="wn-chip on" data-y="all">全部</button>' +
        years.map(y => `<button class="wn-chip" data-y="${y}">${y}</button>`).join('');
    box.querySelectorAll('.wn-chip').forEach(c => {
        c.onclick = () => {
            const y = c.dataset.y;
            if (y === 'all') PH_YEARS_ON.clear();
            else if (PH_YEARS_ON.has(y)) PH_YEARS_ON.delete(y); else PH_YEARS_ON.add(y);
            box.querySelectorAll('.wn-chip').forEach(x => {
                x.classList.toggle('on', (x.dataset.y === 'all' && PH_YEARS_ON.size === 0) || PH_YEARS_ON.has(x.dataset.y));
            });
            phRender();
        };
    });
}

function phRender() {
    const sEl = document.getElementById('phSearch');
    const q = (sEl ? sEl.value : '').trim().toLowerCase();
    const cats = (PH_DATA && PH_DATA.cats) || [];
    let total = 0;
    let html = '';
    for (const c of cats) {
        const items = ((PH_DATA.groups[c]) || []).filter(x => {
            const ys = x.years || (x.year ? [x.year] : []);
            if (PH_YEARS_ON.size && !ys.some(y => PH_YEARS_ON.has(y))) return false;
            if (!q) return true;
            const hay = [x.w, x.meaning, x.en, x.cn, x.func, ys.join(' '), (x.variants || []).join(' ')]
                .join(' ').toLowerCase();
            return hay.includes(q);
        });
        if (!items.length) continue;
        total += items.length;
        html += `<div class="ph-card"><h3>${phEsc(c)}<span class="ph-n">${items.length}</span></h3>` +
            items.map(x => {
                const ys = x.years || (x.year ? [x.year] : []);
                const freq = x.freq > 1
                    ? `<span class="ph-freq" title="在 ${ys.join(' / ')} 年的套用示范中都用到">★ 高频 · ${x.freq} 年</span>` : '';
                const vars = (x.variants || []).length > 1
                    ? `<div class="ph-var">变体：${(x.variants || []).filter(v => v !== x.w).map(phEsc).join(' ／ ')}</div>` : '';
                const link = x.aid
                    ? `<a class="ph-go" href="article.html?id=${encodeURIComponent(x.aid)}">→ 看套用示范</a>` : '';
                return `<div class="ph-item">
                <div class="ph-w">${phEsc(x.w)}${freq}</div>
                <div class="ph-m">${x.func ? `<span class="ph-func">${phEsc(x.func)}</span>` : ''}${phEsc(x.meaning)}</div>
                ${x.en ? `<div class="ph-e">${phEsc(x.en)}</div>` : ''}
                ${x.cn ? `<div class="ph-cn">${phEsc(x.cn)}</div>` : ''}
                ${vars}
                <div class="ph-src">${phEsc(x.src)}${link}</div></div>`;
            }).join('') + '</div>';
    }
    const cnt = document.getElementById('phCount');
    if (cnt) cnt.textContent = `共 ${total} 条 / ${cats.length} 类`;
    const box = document.getElementById('phContent');
    box.innerHTML = total ? `<div class="ph-grid">${html}</div>`
        : '<p style="color:var(--text-light)">没有匹配的短语</p>';
}

async function phInit() {
    try {
        const res = await fetch('data/phrasebook.json', { cache: 'no-cache' });
        PH_DATA = await res.json();
        phAll().forEach(x => (x.years || [x.year]).forEach(y => y && PH_YEARS.add(y)));
        phYearChips();
        phRender();
        const s = document.getElementById('phSearch');
        if (s) s.addEventListener('input', phRender);
    } catch (e) {
        document.getElementById('phContent').innerHTML =
            '<p style="color:var(--text-light)">数据加载失败，请刷新重试</p>';
    }
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', phInit);
else phInit();
