/* 作文模板库：大作文（图表作文）与小作文通用模板 + 图表适配指南 */
let WR = null;

const WR_PH = /\{\{(.+?)\}\}/g;

function wrEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 转义 + 占位符高亮（{{xxx}} → 蓝色可替换标记） */
function wrHl(s) {
    if (!s) return '';
    return wrEsc(s).replace(WR_PH, '<span class="wr-ph">$1</span>');
}

/** 纯文本版（去掉 {{ }}，供复制） */
function wrPlain(s) {
    return (s || '').replace(WR_PH, '$1');
}

function wrCopy(btn, text) {
    const done = () => {
        const old = btn.textContent;
        btn.textContent = '✓ 已复制';
        setTimeout(() => { btn.textContent = old; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(wrPlain(text)).then(done).catch(() => wrFallback(text, done));
    } else {
        wrFallback(text, done);
    }
}

function wrFallback(text, done) {
    const ta = document.createElement('textarea');
    ta.value = wrPlain(text);
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
}

function wrSectionCard(sec) {
    const sents = (sec.sentences || []).map((s, i) => `
        <li class="wr-sent">
            <div class="wr-sent-en"><span class="wr-sent-no">${i + 1}</span>${wrHl(s.en)}</div>
            <div class="wr-sent-cn">${wrEsc(s.cn)}</div>
        </li>`).join('');

    const tips = (sec.tips || []).map(x => `<li>${wrEsc(x)}</li>`).join('');

    return `
    <section class="wr-card" id="${sec.id}">
        <div class="wr-card-head">
            <h3 class="wr-card-title">${wrEsc(sec.title)}</h3>
            ${sec.subtitle ? `<div class="wr-card-sub">${wrEsc(sec.subtitle)}</div>` : ''}
        </div>
        <div class="wr-tpl">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag">英文模板</span>
                <button class="wr-copy" onclick="wrCopy(this, this.closest('.wr-tpl').querySelector('.wr-en').textContent)">复制</button>
            </div>
            <div class="wr-en">${wrHl(sec.en)}</div>
            <div class="wr-cn">${wrHl(sec.cn)}</div>
        </div>
        ${sec.negative_en ? `
        <div class="wr-tpl wr-tpl-neg">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag wr-tag-neg">负面版（选一）</span>
                <button class="wr-copy" onclick="wrCopy(this, this.closest('.wr-tpl').querySelector('.wr-en').textContent)">复制</button>
            </div>
            <div class="wr-en">${wrHl(sec.negative_en)}</div>
            <div class="wr-cn">${wrHl(sec.negative_cn)}</div>
        </div>` : ''}
        ${sents ? `<div class="wr-sents"><div class="wr-sents-title">功能句挑选（自行选 2~4 句拼接，控制字数）</div><ol class="wr-sent-list">${sents}</ol></div>` : ''}
        ${sec.note ? `<div class="wr-note-inline">💡 ${wrHl(sec.note)}</div>` : ''}
        ${tips ? `<ul class="wr-tips">${tips}</ul>` : ''}
    </section>`;
}

async function initWriting() {
    try {
        const res = await fetch('data/writing_templates.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error('加载失败: ' + res.status);
        WR = await res.json();
    } catch (e) {
        document.getElementById('wrContent').innerHTML =
            `<p class="wr-loading">加载失败：${wrEsc(e.message)}</p>`;
        return;
    }
    const it = WR.intro || {};
    document.title = (it.title || '作文模板') + ' - 英语真题精翻';
    document.getElementById('wrTitle').textContent = it.title || '作文模板库';
    document.getElementById('wrDesc').textContent = it.desc || '';
    document.getElementById('wrRules').innerHTML = (it.rules || [])
        .map((r, i) => `<div class="wr-rule"><span class="wr-rule-no">${i + 1}</span>${wrEsc(r)}</div>`).join('');

    // 图表适配表
    const g = WR.chart_guide || {};
    document.getElementById('wrGuideTitle').textContent = g.title || '图表适配表';
    document.getElementById('wrGuideDesc').textContent = g.desc || '';
    document.querySelector('#wrChartTable tbody').innerHTML = (g.table || []).map(row => `
        <tr>
            <td class="wr-t-year">${wrEsc(row.year)}</td>
            <td>${wrEsc(row.chart)}</td>
            <td class="wr-t-num">${row.items || '—'}</td>
            <td>${wrEsc(row.trend)}</td>
            <td><span class="wr-type ${row.type === '动态' ? 'wr-type-dyn' : (row.type === '静态' ? 'wr-type-sta' : '')}">${wrEsc(row.type) || '—'}</span></td>
            <td class="wr-t-hint">${wrEsc(row.hint)}</td>
        </tr>`).join('');
    document.getElementById('wrDecisions').innerHTML = (g.decisions || []).map(d => `
        <div class="wr-decision">
            <div class="wr-decision-k">${wrEsc(d.k)}</div>
            <div class="wr-decision-v">${wrEsc(d.v)}</div>
        </div>`).join('');

    // 模板分区（按 group 分组）
    const groups = {};
    for (const s of WR.sections || []) {
        (groups[s.group] || (groups[s.group] = [])).push(s);
    }
    document.getElementById('wrContent').innerHTML = Object.keys(groups).map(gname => `
        <h2 class="wr-h2">${wrEsc(gname)}</h2>
        ${groups[gname].map(wrSectionCard).join('')}`).join('');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWriting);
} else {
    initWriting();
}
