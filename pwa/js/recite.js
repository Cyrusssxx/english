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

    const allEn = secs.reduce((a, s) => {
        if (s.skeletons && s.skeletons.length) {               // 有走势变体的段：只算变体（s.en 就是其中一套，别重复计）
            return a.concat(s.negative_en ? [s.negative_en] : [], s.skeletons.map(v => v.en));
        }
        return a.concat([s.en], s.negative_en ? [s.negative_en] : []);
    }, []);
    const mustWords = allEn.reduce((a, x) => a + rcWords(x), 0);
    const mustSent = allEn.reduce((a, x) => a + rcSplitEn(x).length, 0);
    const ammoN = secs.reduce((a, s) => a + (s.sentences || []).length, 0);

    document.getElementById('rcDesc').innerHTML =
        '一整页 = 全部要背的东西。<b>只背骨架（⭐），句池（⚡）不用背</b>——写的时候现挑现抄。';
    document.getElementById('rcStats').innerHTML = `
        <div class="rc-stat"><span class="rc-stat-n">${mustSent}</span><span class="rc-stat-k">⭐ 必背句子</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${mustWords}</span><span class="rc-stat-k">⭐ 必背词数</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${ammoN}</span><span class="rc-stat-k">⚡ 句池（选背）</span></div>
        <div class="rc-stat"><span class="rc-stat-n">30</span><span class="rc-stat-k">天完成</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${Math.ceil(mustWords / 30)}</span><span class="rc-stat-k">平均词/天</span></div>`;

    // 一、拼装顺序（词数从数据算，改骨架不用改这里）
    const W1 = Math.max(rcWords(S.chart_static ? S.chart_static.en : ''), 23);
    const W2 = rcWords(S.para2_why ? S.para2_why.en : '');
    const dyn = ['① 一条线在走', '② 两条都在涨', '③ 一升一降'].map(x => {
        const hit = ((S.chart_dynamic || {}).skeletons || []).find(v => v.label === x);
        return hit ? rcWords(hit.en) : 0;
    });
    document.getElementById('rcOrder').innerHTML = `
        <div class="rc-order">
            <div class="rc-order-step"><span class="rc-order-no">1</span><b>第一段 · 描述图</b>
                <div class="rc-order-body">静态分布图用「静态骨架」（${W1} 词）；动态图先看走势，从 3 套里<b>选一套</b>：
                ${rcEsc(dyn[0])} / ${rcEsc(dyn[1])} / ${rcEsc(dyn[2])} 词。再按需补 1 句句池，本段约 40~55 词。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">2</span><b>第二段 · 说原因</b>
                <div class="rc-order-body">引入句 ${W2} 词 + 从机制句池<b>挑 3 条</b>（每条都是一个完整原因），本段约 55~65 词。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">3</span><b>第三段 · 评论</b>
                <div class="rc-order-body"><b>立场句</b>（正面 ${rcWords(S.para3_positive ? S.para3_positive.en : '')} 词 / 负面 ${rcWords(S.para3_negative ? S.para3_negative.en : '')} 词，含收束句）
                ＋ 从主体句池挑 1~2 句，本段约 45~55 词。</div></div>
            <div class="rc-total">三段合计 <b>150~180 词</b>（考研要求 150+）· 超了就少接一句句池</div>
        </div>`;

    // 二、必背骨架
    const groups = [
        ['大作文 · 第一段（图表描述）', ['chart_static', 'chart_dynamic']],
        ['大作文 · 第二段（原因）', ['para2_why']],
        ['大作文 · 第三段（总结建议）', ['para3_positive', 'para3_negative']]
    ];
    let sk = '';
    groups.forEach(([gname, ids]) => {
        sk += `<div class="rc-group">${rcEsc(gname)}</div>`;
        ids.forEach(id => {
            const s = S[id];
            if (!s) return;
            const skels = s.skeletons || null;
            const w = skels ? skels.reduce((a, v) => a + rcWords(v.en), 0) : rcWords(s.en);
            const wTxt = skels ? `${skels.length} 选 1 · 共 ${w} 词` : `${w} 词`;
            sk += rcCard(id, s.title, `⭐ ${wTxt}${s.priority ? ' · 优先背' : ''}`);
            if (skels) {
                sk += skels.map(v => `<div class="rc-skel">
                    <div class="rc-skel-head"><b>${rcEsc(v.label)}</b><span>适用 ${rcEsc(v.years)}</span></div>`
                    + rcPairs(v.en, v.cn).map(p => `<div class="rc-line"><div class="rc-en">${rcPh(p.en)}</div>${p.cn ? `<div class="rc-cn">${rcPh(p.cn)}</div>` : ''}</div>`).join('')
                    + '</div>').join('');
            } else {
                sk += '<div class="rc-lines">'
                    + rcPairs(s.en, s.cn).map(p => `<div class="rc-line"><div class="rc-en">${rcPh(p.en)}</div>${p.cn ? `<div class="rc-cn">${rcPh(p.cn)}</div>` : ''}</div>`).join('')
                    + '</div>';
            }
            if (s.negative_en) {
                sk += '<div class="rc-sub">负面版（危害类题目用）</div><div class="rc-lines rc-lines-neg">'
                    + rcPairs(s.negative_en, s.negative_cn).map(p => `<div class="rc-line"><div class="rc-en">${rcPh(p.en)}</div>${p.cn ? `<div class="rc-cn">${rcPh(p.cn)}</div>` : ''}</div>`).join('')
                    + '</div>';
            }
            sk += '</div>';
        });
    });
    document.getElementById('rcSkeleton').innerHTML = sk;

    // 五、考场流程 + 交卷自查（来自 writing_templates.json 的 flow / checklist / data_lang）
    (function () {
        const box = document.getElementById('rcExam');
        if (!box) return;
        const flow = RC.flow || [], ck = RC.checklist || [];
        const dl = RC.data_lang || [];
        box.innerHTML = '<div class="rc-order">'
            + flow.map((x, i) => `<div class="rc-order-step"><span class="rc-order-no">${i + 1}</span><b>${rcEsc(x[0].replace(/^[①-⑥]\s*/, ''))} · ${rcEsc(x[1])}</b>
                <div class="rc-order-body">${rcPh(x[2])}</div></div>`).join('')
            + '</div>'
            + '<div class="rc-group">📐 数据说法速查（第一段全靠它）</div>'
            + '<div class="rc-plan"><table class="rc-table"><tbody>'
            + dl.map(x => `<tr><td>${rcEsc(x[0])}</td><td>${rcEsc(x[1])}</td></tr>`).join('')
            + '</tbody></table></div>'
            + '<div class="rc-group">✅ 交卷前自查（逐条过）</div>'
            + '<div class="rc-plan"><table class="rc-table"><tbody>'
            + ck.map((x, i) => `<tr><td>${i + 1}</td><td>${rcPh(x)}</td></tr>`).join('')
            + '</tbody></table></div>'
            + '<div class="rc-note"><b>时间分配：</b>审题 3 分钟 → 定骨架与归因 3 分钟 → 写 22 分钟 → 检查 5 分钟。'
            + '最后 5 分钟只做三件事：<b>核对数字、查时态、数字数</b>。</div>';
    })();

    // 三、第三段主体句池
    let ag = '';
    [['para3_positive', '正面版（立场 + 建议）'], ['para3_negative', '负面版（立场 + 对策）']].forEach(([id, label]) => {
        const s = S[id];
        if (!s) return;
        ag += `<div class="rc-group">${rcEsc(label)} · 立场句 + 收束句 ${rcWords(s.en)} 词 · 主体句挑 1~2 句</div>`;
        ag += '<div class="rc-agent-grid">';
        const RC_AGENTS = [...new Set((s.sentences || []).map(x => (x.tag || '').split('·')[0].trim()).filter(Boolean))];
        RC_AGENTS.forEach(a => {
            const hit = (s.sentences || []).filter(x => (x.tag || '').split('·')[0].trim() === a);
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
    rcTocBuild('rcToc', [
        ['rcSecOrder', '① 三段怎么拼'],
        ['rcSecSkeleton', '② ⭐ 必背骨架'],
        ['rcSecAgents', '③ ⚡ 主体句池'],
        ['rcSecPlan', '④ 30 天计划'],
        ['rcSecExam', '⑤ 考场 30 分钟']
    ]);
    rcTocBuild('rcTocS', [
        ['rcSecSOrder', '① 怎么拼（5 步）'],
        ['rcSecSCore', '② ⭐ 骨架 + 必背'],
        ['rcSecSGuide', '③ 17 年真题挑句'],
        ['rcSecSPlan', '④ 30 天计划']
    ]);
}

function rcTocBuild(tocId, rawItems) {
    const items = rawItems.filter(x => document.getElementById(x[0]));
    const toc = document.getElementById(tocId);
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

/* ==================== 视图切换（大作文 / 小作文，同页） ==================== */
const RC_VW_KEY = 'rc_view_v1';

function rcView(v) {
    const big = document.getElementById('rcBig'), small = document.getElementById('rcSmall');
    if (!big || !small) return;
    big.hidden = v !== 'big';
    small.hidden = v !== 'small';
    document.querySelectorAll('.rc-vw-btn').forEach(b => b.classList.toggle('on', b.dataset.v === v));
    try { localStorage.setItem(RC_VW_KEY, v); } catch (e) { /* ignore */ }
}

function rcVwBind() {
    document.querySelectorAll('.rc-vw-btn').forEach(b =>
        b.addEventListener('click', () => { rcView(b.dataset.v); window.scrollTo({ top: 0 }); }));
    let v = 'big';
    try { v = localStorage.getItem(RC_VW_KEY) || 'big'; } catch (e) { /* ignore */ }
    rcView(v === 'small' ? 'small' : 'big');
}

/* ==================== 小作文速记 ==================== */
function rcSTier(it) {
    if (it.tier === 'core') return '⭐⭐';
    if (it.tier === 'must') return '⭐';
    return '';
}

async function rcSmallInit() {
    let D = null;
    try {
        const res = await fetch('data/small_writing.json', { cache: 'no-cache' });
        D = await res.json();
    } catch (e) {
        document.getElementById('rcDescS').textContent = '加载失败：' + e.message;
        return;
    }
    const st = D.stats || {};
    const core = [], must = [];
    (D.banks || []).forEach(b => (b.items || []).forEach(it => {
        if (it.tier === 'core') core.push({ b: b, it: it });
        else if (it.tier === 'must') must.push({ b: b, it: it });
    }));
    const mustTotal = st.core_words + st.must_words;
    document.getElementById('rcDescS').innerHTML =
        '一页背完小作文：<b>⭐⭐ 骨架 4 句（任何一封信都要用）+ ⭐ 每类型 2 句</b>，' + st.ammo + ' 句弹药（现挑现抄，不用背）。';
    document.getElementById('rcStatsS').innerHTML = `
        <div class="rc-stat"><span class="rc-stat-n">${st.core + st.must}</span><span class="rc-stat-k">⭐ 要背的句子</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${mustTotal}</span><span class="rc-stat-k">⭐ 要背的词数</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${st.ammo}</span><span class="rc-stat-k">⚡ 弹药（选抄）</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${D.types.length}</span><span class="rc-stat-k">个信件类型</span></div>
        <div class="rc-stat"><span class="rc-stat-n">${(mustTotal / 30).toFixed(1)}</span><span class="rc-stat-k">平均词/天</span></div>`;

    // 一、怎么拼
    document.getElementById('rcSOrder').innerHTML = `
        <div class="rc-order">
            <div class="rc-order-step"><span class="rc-order-no">1</span><b>称呼</b>
                <div class="rc-order-body">不知道收信人：<b>Dear Sir or Madam,</b>；知道姓名：<b>Dear Jack,</b> / <b>Dear Prof. Smith,</b>。顶格写、以逗号结尾。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">2</span><b>第一段 · 问候 + 来意（2 句，约 25 词）</b>
                <div class="rc-order-body">⭐⭐ 骨架首句问候 ＋ 来意句点明目的（I am writing to…）。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">3</span><b>第二段 · 展开（2 句，约 50 词）</b>
                <div class="rc-order-body">先用通用引出句，再按<b>题干动词</b>选类型，挑该类型的 ⭐ 2 句（做法 + 理由/要求）。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">4</span><b>第三段 · 收尾（1 句，约 15 词）</b>
                <div class="rc-order-body">客套 / 期待回复（I would appreciate it very much if…）。</div></div>
            <div class="rc-order-step"><span class="rc-order-no">5</span><b>落款</b>
                <div class="rc-order-body">正式 <b>Yours sincerely,</b>；朋友 <b>Best wishes,</b>。下一行写题目给的名字（Li Ming）。通知不用落款人名。</div></div>
            <div class="rc-total">全文合计 <b>90~110 词</b>（英语二 A 节要求约 100 词）</div>
        </div>`;

    // 二、要背的句子
    const line = (x, star) => `<div class="rc-line"><div class="rc-en"><span class="rc-freq">${star}</span>${rcPh(x.it.en)}</div>`
        + `<div class="rc-cn">${rcPh(x.it.cn || '')}</div></div>`;
    let sk = '<div class="rc-group">⭐⭐ 骨架（4 句 · ' + st.core_words + ' 词）— 任何一封信都要用</div>';
    sk += '<div class="rc-card"><div class="rc-card-head"><span class="rc-card-title">首句 / 来意 / 通用引出 / 收尾</span>'
        + `<span class="rc-card-sub">⭐ ${st.core_words} 词</span></div><div class="rc-lines">`
        + core.map(x => line(x, '⭐⭐')).join('') + '</div></div>';

    sk += '<div class="rc-group">⭐ 必背（每个类型 2 句 · 共 ' + st.must + ' 句 / ' + st.must_words + ' 词）</div>';
    (D.types || []).forEach(tp => {
        // 按类型视图里声明的 bank 归属取句（别按 type 名字匹配：'建议' ≠ '建议信'）
        const list = [];
        (tp.banks || []).forEach(bid => {
            const b = (D.banks || []).find(x => x.id === bid);
            if (!b) return;
            (b.items || []).forEach(it => { if (it.tier === 'must') list.push({ b: b, it: it }); });
        });
        if (!list.length) return;
        const w = list.reduce((a, x) => a + rcWords(x.it.en), 0);
        sk += rcCard(tp.id, tp.name, '⭐ ' + list.length + ' 句 · ' + w + ' 词');
        sk += '<div class="rc-lines">' + list.map(x => line(x, '⭐')).join('') + '</div></div>';
    });
    sk += `<div class="rc-note"><b>觉得多？最省路径：</b>只背 ⭐⭐ 骨架 4 句（${st.core_words} 词）+ 真题最常考的
        <b>建议 / 邀请 / 介绍</b> 三类各 2 句（共 6 句）——这样 10 句、约 ${st.core_words + 60} 词就能应付绝大多数年份；
        其余类型等考到再补。</div>`;
    document.getElementById('rcSCore').innerHTML = sk;

    // 三、真题适配表
    document.getElementById('rcSGuide').innerHTML = '<div class="rc-plan"><table class="rc-table">'
        + '<thead><tr><th>年份</th><th>题型</th><th>该挑哪些句</th></tr></thead><tbody>'
        + (D.guide || []).map(r => `<tr><td>${rcEsc(r.year)}</td><td>${rcEsc(r.type)}</td><td>${rcPh(r.hint)}</td></tr>`).join('')
        + '</tbody></table></div>';

    // 四、30 天计划
    document.getElementById('rcSPlan').innerHTML = `
        <div class="rc-plan">
            <table class="rc-table">
                <thead><tr><th>阶段</th><th>天数</th><th>背什么</th><th>验收</th></tr></thead>
                <tbody>
                    <tr><td rowspan="2">第 1 周</td><td>D1–D3</td><td>⭐⭐ 骨架 4 句（${st.core_words} 词）+ 来信/去信的称呼与落款</td><td>能默写骨架</td></tr>
                    <tr><td>D4–D7</td><td>建议 / 邀请 / 介绍 三类各 2 句（最常考）</td><td>能各写一段第二段</td></tr>
                    <tr><td rowspan="2">第 2 周</td><td>D8–D14</td><td>感谢 / 道歉 / 通知 / 祝贺 四类各 2 句</td><td>看题干能选对类型</td></tr>
                    <tr><td>D15–D17</td><td>投诉 / 询问 / 观点 三类各 2 句 + 回滚复习</td><td>10 类全覆盖</td></tr>
                    <tr><td>第 3 周</td><td>D18–D24</td><td>每天套写一篇真题（按适配表挑句），限时 15 分钟</td><td>连写 7 年不卡壳</td></tr>
                    <tr><td>第 4 周</td><td>D25–D30</td><td>剩余年份套写 + 只看中文默写必背句</td><td>必背句全默写正确</td></tr>
                </tbody>
            </table>
            <div class="rc-day">
                <b>每天 0.5 小时怎么分（小作文用不了 1 小时）</b>
                <div class="rc-day-row"><span class="rc-day-t">3 min</span>默写昨天背的 2 句，错的抄 3 遍</div>
                <div class="rc-day-row"><span class="rc-day-t">8 min</span>背 2 句新的（读中文 → 读英文 → 遮住中文复述）</div>
                <div class="rc-day-row"><span class="rc-day-t">4 min</span>合上书写这 2 句</div>
                <div class="rc-day-row"><span class="rc-day-t">剩下</span>第 3 周开始，隔天套写一篇真题</div>
            </div>
            <div class="rc-note"><b>小作文占 10 分，别把时间全给它。</b>先把大作文骨架背完（那个 15 分），
                小作文用「隔天 15 分钟」的节奏穿插进去就行。</div>
        </div>`;
}

document.addEventListener('DOMContentLoaded', () => {
    const s = document.getElementById('darkState');
    if (s) s.textContent = document.documentElement.classList.contains('dark') ? '开' : '关';
    rcVwBind();
    rcToc();
    rcInit();
    rcSmallInit();
});
