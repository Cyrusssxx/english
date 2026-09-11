/* 学习统计页：实时正确率 / 错误率最高的文章置顶 / 按题型·题目类型·年份统计 / 并入个人建议 */
const QTYPE_CN = {
    detail: '细节题', viewpoint: '观点题', inference: '推断题', main_idea: '主旨题',
    attitude: '态度题', vocabulary: '词义题', example: '例证题', opinion: '观点题',
    sentence: '句意题', cloze: '完形', '小标题': '小标题', '判断': '判断题'
};

function stQtype(t) { return QTYPE_CN[t] || t || '未分类'; }

function stRateCls(rate) { return rate <= 0.4 ? 'b-red' : (rate < 1 ? 'b-yellow' : 'b-green'); }
function stRateColor(rate) { return rate <= 0.4 ? 'r-red' : (rate < 1 ? 'r-yellow' : 'r-green'); }

function stBar(ok, n) {
    const rate = n ? ok / n : 0;
    return `<span class="rate-txt">${Math.round(rate * 100)}%</span> <span class="st-bar ${stRateCls(rate)}"><i style="width:${Math.round(rate * 100)}%"></i></span>`;
}

async function stInit() {
    const [i2, i1] = await Promise.all([loadIndex(), loadEn1Index()]);
    const dir = {};
    (i2.years || []).forEach(y => (y.articles || []).forEach(a => dir[a.id] = { year: y.year, book: '英语二', type: a.type, title: a.title || '' }));
    (i1.years || []).forEach(y => (y.articles || []).forEach(a => dir[a.id] = { year: y.year, book: '英语一', type: a.type, title: a.title || '' }));

    const all = await dbAll('quiz_answers');
    const byArt = {};       // article_id -> [answer]
    let totalN = 0, totalOk = 0;
    for (const z of all) {
        if (!dir[z.article_id]) continue;
        (byArt[z.article_id] || (byArt[z.article_id] = [])).push(z);
        totalN++;
        if (z.is_correct) totalOk++;
    }
    const artIds = Object.keys(byArt);

    function typeSel(t) {
        return /^text\d$/.test(t) ? '阅读' : (t === 'cloze' ? '完形' : (t === 'newtype' ? '新题型' : (t === 'translation' ? '翻译' : t)));
    }

    const perArt = {};      // id -> {ok, n, info}
    const perType = {};     // '阅读' -> {ok,n}
    const perQtype = {};    // '细节题' -> {ok,n}
    const perYear = {};     // '2021 英语二' -> {ok,n}
    const qmapCache = {};   // article_id -> {qid: qtype}

    for (const id of artIds) {
        const info = dir[id];
        const arr = byArt[id];
        const ok = arr.filter(x => x.is_correct).length;
        perArt[id] = { id, ok, n: arr.length, info };
        const ts = typeSel(info.type);
        (perType[ts] || (perType[ts] = { ok: 0, n: 0 })).ok += ok; perType[ts].n += arr.length;
        const yk = info.year + ' ' + info.book;
        (perYear[yk] || (perYear[yk] = { ok: 0, n: 0 })).ok += ok; perYear[yk].n += arr.length;
        // qtype 统计：加载该篇文章的题目定义
        try {
            const data = info.book === '英语一' ? await loadEn1Year(info.year) : await loadYear(info.year);
            const article = (data.articles || []).find(a => a.id === id);
            if (!article) continue;
            const qm = {};
            (article.questions || []).forEach(q => qm[q.id] = stQtype(q.qtype));
            for (const z of arr) {
                const t = qm[z.question_id] || '未分类';
                (perQtype[t] || (perQtype[t] = { ok: 0, n: 0 })).n++;
                if (z.is_correct) perQtype[t].ok++;
            }
        } catch (e) { /* 单篇加载失败跳过 qtype 统计 */ }
    }

    // ---------- 总览 tiles ----------
    const wrongN = totalN - totalOk;
    const redN = artIds.filter(id => { const p = perArt[id]; return p.n && p.ok / p.n <= 0.4; }).length;
    const pctStr = totalN ? (Math.round(totalOk * 100 / totalN) + '%') : '0%';
    const ratioStr = totalN ? (totalOk + '/' + totalN) : '';
    const tiles = [
        ['已答文章', String(artIds.length), ''],
        ['答题总数', String(totalN), ''],
        ['总正确率', pctStr, ratioStr],
        ['答错题数', String(wrongN), ''],
        ['红区文章(≤2/5)', String(redN), '篇'],
    ];
    document.getElementById('stTiles').innerHTML = tiles.map(t =>
        `<div class="st-tile"><div class="k">${t[0]}</div><div class="v">${typeof t[1] === 'number' ? t[1] : esc(t[1])}<small>${t[2]}</small></div></div>`).join('');
    document.getElementById('stHeroTotal').textContent =
        totalN ? `已答 ${totalN} 题（对 ${totalOk} / 错 ${wrongN}，总正确率 ${Math.round(totalOk * 100 / totalN)}%）` : '暂无答题数据';

    // ---------- 错误率最高的文章（置顶，错误率降序） ----------
    const wrongList = artIds.map(id => perArt[id]).filter(p => p.n).sort((a, b) => (a.ok / a.n) - (b.ok / b.n));
    let wrongHtml = '';
    if (!wrongList.length) {
        wrongHtml = '<div class="st-empty">还没有答题记录，去 <a href="index.html">真题文章</a> 做一套题吧。</div>';
    } else {
        const rows = wrongList.map(p => {
            const r = p.ok / p.n;
            const cls = stRateColor(r);
            return `<tr>
                <td><span class="st-tag ${p.info.book === '英语一' ? 'en1' : 'en2'}">${p.info.book}</span>${p.info.year} · ${typeSel(p.info.type)}</td>
                <td class="art-title">${esc(p.info.title)}</td>
                <td><span class="ac-rate ${cls}">${p.ok}/${p.n} · ${Math.round(r * 100)}%</span></td>
                <td>${stBar(p.ok, p.n)}</td>
                <td><a href="article.html?id=${p.id}">重做 →</a></td>
            </tr>`;
        });
        wrongHtml = `<div class="st-table-wrap"><table class="st-table">
            <thead><tr><th>文章</th><th>标题</th><th>正确率</th><th>分布</th><th></th></tr></thead>
            <tbody>${rows.join('')}</tbody></table></div>`;
    }
    document.getElementById('stWrongList').innerHTML = wrongHtml;

    // ---------- 按题型 ----------
    const typeHtml = Object.keys(perType).map(t => {
        const p = perType[t];
        return `<tr><td>${esc(t)}</td><td>${p.n}</td><td>${p.ok}</td><td>${stBar(p.ok, p.n)}</td></tr>`;
    }).join('');
    document.getElementById('stTypeTable').innerHTML = typeHtml ?
        `<div class="st-table-wrap"><table class="st-table"><thead><tr><th>题型</th><th>已答</th><th>正确</th><th>正确率</th></tr></thead><tbody>${typeHtml}</tbody></table></div>`
        : '<div class="st-empty">暂无数据</div>';

    // ---------- 按题目类型（错题画像） ----------
    const qtRows = Object.keys(perQtype).sort((a, b) => perQtype[b].n - perQtype[a].n).map(t => {
        const p = perQtype[t];
        return `<tr><td>${esc(t)}</td><td>${p.n}</td><td>${p.ok}</td><td>${p.n - p.ok}</td><td>${stBar(p.ok, p.n)}</td></tr>`;
    }).join('');
    document.getElementById('stQtypeTable').innerHTML = qtRows ?
        `<div class="st-table-wrap"><table class="st-table"><thead><tr><th>题目类型</th><th>已答</th><th>正确</th><th>错误</th><th>正确率</th></tr></thead><tbody>${qtRows}</tbody></table></div>`
        : '<div class="st-empty">暂无数据</div>';

    // ---------- 按年份 ----------
    const yrRows = Object.keys(perYear).sort().reverse().map(t => {
        const p = perYear[t];
        return `<tr><td>${esc(t)}</td><td>${p.n}</td><td>${p.ok}</td><td>${stBar(p.ok, p.n)}</td></tr>`;
    }).join('');
    document.getElementById('stYearTable').innerHTML = yrRows ?
        `<div class="st-table-wrap"><table class="st-table"><thead><tr><th>年份 · 卷别</th><th>已答</th><th>正确</th><th>正确率</th></tr></thead><tbody>${yrRows}</tbody></table></div>`
        : '<div class="st-empty">暂无数据</div>';

    // ---------- 建议画像（动态） ----------
    const img = Object.keys(perQtype)
        .map(t => ({ t, n: perQtype[t].n - perQtype[t].ok }))
        .filter(x => x.n > 0)
        .sort((a, b) => b.n - a.n)
        .map(x => `${x.t} ${x.n}`).join(' / ');
    document.getElementById('stImg').textContent =
        (wrongN ? `你当前共错 ${wrongN} 题（${img}）` : '你最近没有错题') +
        (wrongN > 0 ? '，细节题和推断题一般占总错误一半以上' : '，继续保持');
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', stInit);
else stInit();