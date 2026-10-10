/* 完形·翻译词库视图（wordnotes.html ② 号视图）
   数据：data/wnlex.json（tools/build_wnlex.py 生成）
   功能：三组筛选 chips + 搜索 + 综合分排序 + 标记分层（不会→不熟→无标记→熟）
        + 分段折叠（每 50 条）+ 进度统计 + 自测模式（隐藏释义点行验证）+ 例句展开
   标记存储：localStorage 'wnLex_marks_v1'（{id: 1不会|2不熟|3熟}），不与背单词页联动 */
let LX_ROWS = [];
const LX_MARKS_KEY = 'wnLex_marks_v1';
const LX_MODE_KEY = 'wnLex_selftest_v1';
const LX_F = { part: 'all', cat: 'all', mark: 'all' };
let LX_Q = '';
const LX_CAT_LABEL = { '衔接': '逻辑衔接', '实词': '核心实词', '搭配': '固定搭配', '僻义': '熟词僻义' };
const LX_SEG = 50;

function lxEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function lxMarks() {
    try { return JSON.parse(localStorage.getItem(LX_MARKS_KEY)) || {}; } catch (e) { return {}; }
}
function lxSaveMarks(m) {
    try { localStorage.setItem(LX_MARKS_KEY, JSON.stringify(m)); } catch (e) { /* ignore */ }
}
function lxMode() {
    try { return localStorage.getItem(LX_MODE_KEY) === '1'; } catch (e) { return false; }
}
function lxToggleMode() {
    const on = !lxMode();
    try { localStorage.setItem(LX_MODE_KEY, on ? '1' : '0'); } catch (e) { /* ignore */ }
    const btn = document.getElementById('lexModeBtn');
    if (btn) {
        btn.textContent = '自测模式：' + (on ? '开' : '关');
        btn.classList.toggle('on', on);
    }
    const sec = document.getElementById('viewLex');
    if (sec) sec.classList.toggle('selftest', on);
    lxRender();
}

/** 默认展开例句开关：非自测模式下，例句详情默认可见（随 50 条分段折叠，不会一次铺开 985 条） */
const LX_EXPAND_KEY = 'wnLex_expand_v1';
function lxExpand() {
    try { return localStorage.getItem(LX_EXPAND_KEY) === '1'; } catch (e) { return false; }
}
function lxToggleExpand() {
    const on = !lxExpand();
    try { localStorage.setItem(LX_EXPAND_KEY, on ? '1' : '0'); } catch (e) { /* ignore */ }
    const btn = document.getElementById('lexExpandBtn');
    if (btn) {
        btn.textContent = '展开例句：' + (on ? '开' : '关');
        btn.classList.toggle('on', on);
    }
    lxRender();
}

/** 标记分层排序键：不会=0 → 不熟=1 → 无标记=2 → 熟=3 */
function lxMarkRank(m) {
    if (m === 1) return 0;
    if (m === 2) return 1;
    if (m === 3) return 3;
    return 2;
}

/** 三组筛选 chips */
function lxChips() {
    const box = document.getElementById('lexFilters');
    if (!box) return;
    const groups = [
        { k: 'part', label: '题型', items: [['all', '全部'], ['cloze', '完形'], ['trans', '翻译']] },
        { k: 'cat', label: '类别', items: [['all', '全部'], ['衔接', '逻辑衔接'], ['实词', '核心实词'], ['搭配', '固定搭配'], ['僻义', '熟词僻义']] },
        { k: 'mark', label: '标记', items: [['all', '全部'], ['none', '未标记'], ['1', '不会'], ['2', '不熟'], ['3', '熟']] },
    ];
    box.innerHTML = groups.map(g =>
        `<div class="lex-fgroup"><span class="lex-flabel">${g.label}</span>` +
        g.items.map(([v, t]) =>
            `<button class="wn-chip${String(LX_F[g.k]) === String(v) ? ' on' : ''}" data-k="${g.k}" data-v="${v}">${t}</button>`).join('') +
        '</div>').join('');
    box.querySelectorAll('.wn-chip').forEach(c => {
        c.onclick = () => {
            const k = c.dataset.k, v = c.dataset.v;
            LX_F[k] = v;
            lxChips();
            lxRender();
        };
    });
}

/** 进度统计条 */
function lxProgress() {
    const box = document.getElementById('lexProgress');
    if (!box) return;
    const total = LX_ROWS.length;
    let m1 = 0, m2 = 0, m3 = 0;
    const marks = lxMarks();
    for (const r of LX_ROWS) {
        const m = marks[r.id];
        if (m === 1) m1++;
        else if (m === 2) m2++;
        else if (m === 3) m3++;
    }
    const done = m1 + m2 + m3;
    box.innerHTML =
        `<span class="lp-total">共 ${total} 词</span>` +
        `<span class="lp-done">已标记 <b>${done}</b>/${total}</span>` +
        `<span class="lp-dot d1"></span>不会 <b>${m1}</b>` +
        `<span class="lp-dot d2"></span>不熟 <b>${m2}</b>` +
        `<span class="lp-dot d3"></span>熟 <b>${m3}</b>` +
        (total ? `<span class="lp-bar"><i style="width:${Math.round(done * 100 / total)}%"></i></span>` : '');
}

/** 主渲染：筛选 → 排序 → 分段 → 表格 */
function lxRender() {
    const box = document.getElementById('lexContent');
    if (!box) return;
    const marks = lxMarks();
    const selftest = lxMode();
    const q = LX_Q.trim().toLowerCase();

    let rows = LX_ROWS.filter(r => {
        if (LX_F.part !== 'all' && r.part !== LX_F.part) return false;
        if (LX_F.cat !== 'all' && r.cat !== LX_F.cat) return false;
        const m = marks[r.id] || 0;
        if (LX_F.mark === 'none' && m) return false;
        if (LX_F.mark !== 'all' && LX_F.mark !== 'none' && m !== Number(LX_F.mark)) return false;
        if (q) {
            const hay = (r.w + ' ' + (r.cn || '') + ' ' + (r.common || '') + ' ' + (r.uncommon || '')).toLowerCase();
            if (!hay.includes(q)) return false;
        }
        return true;
    });

    rows.sort((a, b) => {
        const ra = lxMarkRank(marks[a.id]), rb = lxMarkRank(marks[b.id]);
        if (ra !== rb) return ra - rb;
        return (b.score || 0) - (a.score || 0);
    });

    const cnt = document.getElementById('lexCount');
    if (cnt) {
        cnt.textContent = `${rows.length} 条` + ((q || LX_F.part !== 'all' || LX_F.cat !== 'all' || LX_F.mark !== 'all') ? `（在 ${LX_ROWS.length} 条中筛选）` : '') +
            (selftest ? ' · 自测中：看词回想，点击行验证' : '');
    }

    if (!rows.length) {
        box.innerHTML = '<p style="color:var(--text-light)">没有匹配的条目——换个筛选或搜索试试</p>';
        lxProgress();
        return;
    }

    const segs = Math.ceil(rows.length / LX_SEG);
    let html = '';
    for (let s = 0; s < segs; s++) {
        const chunk = rows.slice(s * LX_SEG, (s + 1) * LX_SEG);
        const marked = chunk.filter(r => marks[r.id]).length;
        html += `<details class="lex-seg"${s === 0 ? ' open' : ''}>
        <summary>第 ${s * LX_SEG + 1}–${s * LX_SEG + chunk.length} 条 · 已标记 ${marked}/${chunk.length}</summary>
        <div class="wn-table-wrap"><table class="wn-table lex-table">
        <thead><tr><th>词 / 词组</th><th>释义</th><th>标记</th></tr></thead>
        <tbody>${chunk.map(r => lxRow(r, marks, selftest)).join('')}</tbody></table></div>
        </details>`;
    }
    box.innerHTML = html;
    lxProgress();
}

function lxRow(r, marks, selftest) {
    const m = marks[r.id] || 0;
    const expand = lxExpand() && !selftest;      // 自测模式优先：自测时例句也要点行才显示
    const catTag = `<span class="lx-cat c-${r.cat}">${LX_CAT_LABEL[r.cat] || r.cat}</span>`;
    const diffTag = `<span class="lx-diff d${r.diff_val}">${r.diff}</span>`;
    const freqTag = r.freq_note ? `<span class="lx-freq">${lxEsc(r.freq_note)}</span>` : '';
    const mkCls = m ? ' mked' : '';
    const detail = lxDetailHtml(r, selftest, expand);
    return `<tr class="lex-row mk${m}${mkCls}${expand ? ' expanded' : ''}" data-id="${lxEsc(r.id)}">
        <td class="lx-w" data-label="词">
            <div class="lx-w-main">${lxEsc(r.w)}</div>
            <div class="lx-w-tags">${catTag}${diffTag}${freqTag || ''}</div>
        </td>
        <td class="lx-cn" data-label="释义"><div class="lx-cn-main">${lxEsc(r.cn || '')}</div></td>
        <td class="lx-mark" data-label="标记">
            <button class="mk mk1${m === 1 ? ' on' : ''}" data-act="mark" data-v="1">不会</button>
            <button class="mk mk2${m === 2 ? ' on' : ''}" data-act="mark" data-v="2">不熟</button>
            <button class="mk mk3${m === 3 ? ' on' : ''}" data-act="mark" data-v="3">熟</button>
        </td>
    </tr>${detail}`;
}

function lxDetailHtml(r, selftest, expand) {
    let inner = '';
    if (selftest) inner += `<div class="lx-d-cn">${lxEsc(r.cn || '')}</div>`;
    if (r.cat === '僻义' && r.common) {
        inner += `<div class="lx-d-common">熟义　${lxEsc(r.common)}</div>`;
        inner += `<div class="lx-d-uncommon">僻义　<b>${lxEsc(r.uncommon || r.cn || '')}</b></div>`;
    }
    if (r.sent) {
        inner += `<div class="lx-d-sent">${lxEsc(r.sent)}</div>`;
        if (r.sent_cn) inner += `<div class="lx-d-sentcn">${lxEsc(r.sent_cn)}</div>`;
    }
    if (r.src) inner += `<div class="lx-d-src">${lxEsc(r.src)}</div>`;
    if (!inner) return '';
    return `<tr class="lex-detail" data-for="${lxEsc(r.id)}"${expand ? '' : ' hidden'}><td colspan="3">${inner}</td></tr>`;
}

/** 事件委托：点标记按钮 / 点行展开例句 */
function lxBindEvents() {
    const box = document.getElementById('lexContent');
    if (!box || box._lxBound) return;
    box._lxBound = true;
    box.addEventListener('click', e => {
        const mkBtn = e.target.closest('.mk');
        if (mkBtn) {
            const tr = mkBtn.closest('.lex-row');
            if (!tr) return;
            lxMark(tr.dataset.id, Number(mkBtn.dataset.v));
            return;
        }
        const tr = e.target.closest('.lex-row');
        if (!tr) return;
        const det = box.querySelector('.lex-detail[data-for="' + tr.dataset.id + '"]');
        if (det) det.hidden = !det.hidden;
        tr.classList.toggle('open');
    });
}

function lxMark(id, v) {
    const marks = lxMarks();
    if (marks[id] === v) delete marks[id];      // 再点同档取消
    else marks[id] = v;
    lxSaveMarks(marks);
    // 不重排：只更新该行按钮态 + 行色 + 进度
    document.querySelectorAll(`.lex-row[data-id="${id}"]`).forEach(tr => {
        tr.classList.remove('mk1', 'mk2', 'mk3', 'mked');
        if (marks[id]) tr.classList.add('mk' + marks[id], 'mked');
        tr.querySelectorAll('.mk').forEach(b => b.classList.toggle('on', Number(b.dataset.v) === marks[id]));
    });
    lxProgress();
}

async function lxInit() {
    try {
        const res = await fetch('data/wnlex.json', { cache: 'no-cache' });
        const data = await res.json();
        LX_ROWS = data.rows || [];
        lxChips();
        lxBindEvents();
        const btn = document.getElementById('lexModeBtn');
        if (btn && lxMode()) { btn.textContent = '自测模式：开'; btn.classList.add('on'); }
        const ebtn = document.getElementById('lexExpandBtn');
        if (ebtn && lxExpand()) { ebtn.textContent = '展开例句：开'; ebtn.classList.add('on'); }
        const sec = document.getElementById('viewLex');
        if (sec) sec.classList.toggle('selftest', lxMode());
        lxRender();
        const s = document.getElementById('lexSearch');
        if (s) s.addEventListener('input', () => { LX_Q = s.value; lxRender(); });
    } catch (e) {
        const box = document.getElementById('lexContent');
        if (box) box.innerHTML = '<p style="color:var(--text-light)">词库数据加载失败，请刷新重试</p>';
    }
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', lxInit);
else lxInit();
