/* 作文速记页：从 writing_templates.json 抽出「必背骨架 + 主体句池」，排版成可打印的一页 */
let RC = null;

function rcEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function rcPh(s) {
    return rcEsc(s).replace(/\{\{(.+?)\}\}/g, '<span class="rc-ph">$1</span>');
}
function rcWords(t) {
    return ((t || '').match(/[A-Za-z0-9][A-Za-z0-9'’%.,:_-]*/g) || []).length;
}
function rcSplitEn(t) {
    return ((t || '').match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g) || []).map(x => x.trim()).filter(Boolean);
}
function rcSplitCn(t) {
    return ((t || '').match(/[^。！？]*[。！？]|[^。！？]+$/g) || []).map(x => x.trim()).filter(Boolean);
}

/** 英文逐句 + 中文逐句（句数相等就对齐，否则整段跟在后面） */
function rcPairs(en, cn) {
    const es = rcSplitEn(en);
    const cs = rcSplitCn(cn);
    const aligned = es.length && es.length === cs.length;
    return es.map((s, i) => ({ en: s, cn: aligned ? cs[i] : i === 0 ? cn : '' }));
}

const RC_AGENTS = ['政府', '学校', '家庭', '企业/平台', '媒体', '个人'];

function rcCard(id, title, sub) {
    return `<div class="rc-card"><div class="rc-card-head"><span class="rc-card-title">${rcEsc(title)}</span>${sub ? `<span class="rc-card-sub">${rcEsc(sub)}</span>` : ''}</div>`;
}

async function rcInit() {
    try {
        const res = await fetch('data/writing_templates.json', { cache: 'no-cache' });
        RC = await res.json();
    } catch (e) {
        document.getElementById('rcDesc').textContent = '加载失败：' + e.message;
        return;
    }
    const secs = RC.sections || [];
    const S = {};
    secs.forEach(s => { S[s.id] = s; });

    const mustWords = secs.reduce((a, s) => a + rcWords(s.en) + rcWords(s.negative_en), 0);
    const ammoN = secs.reduce((a, s) => a + (s.sentences || []).length, 0);
    const mustSent = secs.reduce((a, s) => a + rcSplitEn(s.en).length + rcSplitEn(s.negative_en).length, 0);

    document.getElementById('rcDesc').innerHTML =
        '一整页 = 全部要背的东西。<b>只背骨架（⭐），句池（⚡）不用背</b>——写的时候现挑现抄。';
    document.getElementById('rcStats').innerHTML = `
        <div class="rc-stat"><span class="rc-stat-n">${mustSent}</span><span class="rc-stat-k">⭐ 必背句子</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${mustWords}</span><span class="rc-stat-k">⭐ 必背词数</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${ammoN}</span><span class="rc-stat-k">⚡ 句池（选背）</span></div>
        <div class="rc-stat"><span class="rc-stat-n">30</span><span class="rc-stat-k">天完成</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${Math.ceil(mustWords / 30)}</span><span class="rc-stat-k">平均词/天</span></div>`;

    // 一、拼装顺序
    document.getElementById('rcOrder').innerHTML = `
        <div class="rc-order">
            <div class="rc-order-step"><span class="rc-order-no">1</span><b>第一段 · 描述图表</b>
                <div class="rc-order-body">静态图用「静态骨架」（38 词）；动态图用「动态骨架」（34 词）。<br>
                再从句池挑 0~1 句补一句趋势/分组，本段约 40~55 词。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">2</span><b>第二段 · 原因分析</b>
                <div class="rc-order-body">按话题挑 1 个骨架（经济 33 / 校园 34 / 环保 32 / 体育 35 / 文化 33 词），<br>
                再接 1~2 句句池，本段约 55~65 词。优先背<b>经济</b>和<b>校园</b>这两段。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">3</span><b>第三段 · 建议总结</b>
                <div class="rc-order-body">正面题用「正面骨架」（31 词），负面题用「负面骨架」（25 词）；<br>
                再从 6 组主体句池里挑 <b>2 个主体各 1 句</b>，本段约 50~60 词。</div></div>
            <div class="rc-total">三段合计 <b>150~180 词</b>（考研要求 150+）· 超了就少接一句句池</div>
        </div>`;

    // 二、必背骨架
    const groups = [
        ['大作文 · 第一段（图表描述）', ['chart_static', 'chart_dynamic']],
        ['大作文 · 第二段（原因分析）', ['para2_economy', 'para2_campus', 'para2_social', 'para2_sports', 'para2_culture']],
        ['大作文 · 第三段（总结建议）', ['para3_positive', 'para3_negative']]
    ];
    let sk = '';
    groups.forEach(([gname, ids]) => {
        sk += `<div class="rc-group">${rcEsc(gname)}</div>`;
        ids.forEach(id => {
            const s = S[id];
            if (!s) return;
            const w = rcWords(s.en);
            sk += rcCard(id, s.title, `⭐ ${w} 词${s.priority ? ' · 优先背' : ''}`)
                + '<div class="rc-lines">'
                + rcPairs(s.en, s.cn).map(p => `<div class="rc-line"><div class="rc-en">${rcPh(p.en)}</div>${p.cn ? `<div class="rc-cn">${rcPh(p.cn)}</div>` : ''}</div>`).join('')
                + '</div>';
            if (s.negative_en) {
                sk += '<div class="rc-sub">负面版（危害类题目用）</div><div class="rc-lines rc-lines-neg">'
                    + rcPairs(s.negative_en, s.negative_cn).map(p => `<div class="rc-line"><div class="rc-en">${rcPh(p.en)}</div>${p.cn ? `<div class="rc-cn">${rcPh(p.cn)}</div>` : ''}</div>`).join('')
                    + '</div>';
            }
            sk += '</div>';
        });
    });
    document.getElementById('rcSkeleton').innerHTML = sk;

    // 三、第三段主体句池
    let ag = '';
    [['para3_positive', '正面版（建议怎么做）'], ['para3_negative', '负面版（怎么控制危害）']].forEach(([id, label]) => {
        const s = S[id];
        if (!s) return;
        ag += `<div class="rc-group">${rcEsc(label)} · 骨架 ${rcWords(s.en)} 词 · 挑 2 个主体各 1 句</div>`;
        ag += '<div class="rc-agent-grid">';
        RC_AGENTS.forEach(a => {
            const hit = (s.sentences || []).filter(x => (x.tag || '').indexOf(a) === 0);
            if (!hit.length) return;
            ag += `<div class="rc-agent"><div class="rc-agent-name">${rcEsc(a)}<span class="rc-agent-yrs">${rcEsc((hit[0].tag || '').split('·')[1] || '')}</span></div>`
                + hit.map(x => `<div class="rc-agent-s"><div class="rc-en"><span class="rc-freq">${'★'.repeat(x.freq || 3)}</span>${rcPh(x.en)}</div><div class="rc-cn">${rcPh(x.cn)}</div></div>`).join('')
                + '</div>';
        });
        ag += '</div>';
    });
    ag += `<div class="rc-note"><b>主体怎么挑：</b>题目问的是学生的事 → 学校 + 家庭；是社会风气 → 媒体 + 个人；
        是基础设施/规则 → 政府 + 企业；是平台/产品 → 企业 + 个人。<b>不要 6 个主体全写</b>，那是模板味最重的地方。</div>`;
    document.getElementById('rcAgents').innerHTML = ag;
}

/** 夜间模式（本页不依赖 common.js，自带一份最小实现） */
function toggleDark() {
    const on = !document.documentElement.classList.contains('dark');
    document.documentElement.classList.toggle('dark', on);
    try { localStorage.setItem('darkMode', on ? '1' : '0'); } catch (e) { /* ignore */ }
    const s = document.getElementById('darkState');
    if (s) s.textContent = on ? '开' : '关';
}

/** 目录（吸顶横条）：点击跳转 + 滚动高亮当前节 */
function rcToc() {
    const items = [
        ['rcSecOrder', '① 三段怎么拼'],
        ['rcSecSkeleton', '② ⭐ 必背骨架'],
        ['rcSecAgents', '③ ⚡ 主体句池'],
        ['rcSecPlan', '④ 30 天计划']
    ].filter(x => document.getElementById(x[0]));
    const toc = document.getElementById('rcToc');
    if (!toc || !items.length) return;
    toc.innerHTML = items.map(x => `<a href="#${x[0]}" data-t="${x[0]}">${x[1]}</a>`).join('');
    const navH = () => {
        const n = document.querySelector('.navbar');
        const h = n ? n.getBoundingClientRect().height : 56;
        return h >= 20 ? h : 56;
    };
    document.documentElement.style.setProperty('--nav-h', navH() + 'px');
    window.addEventListener('resize', () => document.documentElement.style.setProperty('--nav-h', navH() + 'px'));
    toc.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-t]');
        if (!a) return;
        e.preventDefault();
        const el = document.getElementById(a.dataset.t);
        if (!el) return;
        const y = el.getBoundingClientRect().top + window.scrollY - navH() - 62;
        window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
    });
    const links = [...toc.querySelectorAll('a[data-t]')];
    const spy = () => {
        const top = navH() + 80;
        let cur = links[0];
        links.forEach(a => {
            const el = document.getElementById(a.dataset.t);
            if (el && el.getBoundingClientRect().top <= top) cur = a;
        });
        links.forEach(a => a.classList.toggle('on', a === cur));
    };
    window.addEventListener('scroll', spy, { passive: true });
    spy();
}

document.addEventListener('DOMContentLoaded', () => {
    const s = document.getElementById('darkState');
    if (s) s.textContent = document.documentElement.classList.contains('dark') ? '开' : '关';
    rcToc();
    rcInit();
});
