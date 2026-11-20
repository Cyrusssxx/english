/* 小作文（英语二 A 节 · 应用文）功能句库
   数据：pwa/data/small_writing.json（tools/build_small_writing.py 生成）
   两种视图：按段落（第一/二/三段） · 按信件类型（建议/邀请/道歉/祝贺/介绍/通知）
   正文可划词高亮 + 行批注（浮条交互，模块与作文页同源，见文件末尾） */
let SW = null;                 // 数据
let swView = 'part';           // part | type
const SW_VIEW_KEY = 'sw_view_v1';

function swEsc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

/** 先把 {{token}} 抽出来做成占位符芯片，再转义其余文本 */
function swPh(s) {
    return String(s == null ? '' : s).split(/(\{\{[^}]+\}\})/g).map(seg => {
        const m = /^\{\{([^}]+)\}\}$/.exec(seg);
        return m ? '<span class="sw-ph">{{' + swEsc(m[1]) + '}}</span>' : swEsc(seg);
    }).join('');
}

/** 重点短语版：占位符照旧成芯片，其余片段交给范文重点词库标 .kw（点击弹释义/用法/例句） */
function swKwPh(s) {
    if (typeof kwMarkText !== 'function' || typeof KW_BY_KEY === 'undefined' || !KW_BY_KEY || !KW_BY_KEY.size) return swPh(s);
    return String(s == null ? '' : s).split(/(\{\{[^}]+\}\})/g).map(seg => {
        const m = /^\{\{([^}]+)\}\}$/.exec(seg);
        return m ? '<span class="sw-ph">{{' + swEsc(m[1]) + '}}</span>' : kwMarkText(seg, swEsc);
    }).join('');
}

function swBank(id) { return (SW.banks || []).find(b => b.id === id); }

/** 考研口径词数 */
function swWords(t) {
    return ((t || '').match(/[A-Za-z0-9][A-Za-z0-9'’%.,:_-]*/g) || []).length;
}

/** 星级：⭐⭐ 骨架（任何信都用）/ ⭐ 必背（每类型 2 句）/ ★★★ 通用 · ★★ 常用 · ★ 专场 */
function swStars(it) {
    if (it.tier === 'core') return '<span class="sw-star s-core" title="骨架句：任何一封信都要用">⭐⭐</span>';
    if (it.tier === 'must') return '<span class="sw-star s-must" title="必背：这一类题最万能的一句">⭐</span>';
    const f = it.freq || 2;
    return '<span class="sw-star" title="通用度：★★★ 任何题都能接 · ★★ 常用 · ★ 专场">'
        + '★'.repeat(f) + '</span>';
}

/** 允许 <b> 的富文本：先转义/包占位符，再把 &lt;b&gt; 还原 */
function swRich(s) {
    return swPh(s).replace(/&lt;(\/?b)&gt;/g, '<$1>');
}

/** 组内分层统计 */
function swBankTier(bank) {
    let core = 0, must = 0, ammo = 0, cw = 0, mw = 0;
    (bank.items || []).forEach(it => {
        if (it.tier === 'core') { core++; cw += swWords(it.en); }
        else if (it.tier === 'must') { must++; mw += swWords(it.en); }
        else ammo++;
    });
    return { core: core, must: must, ammo: ammo, cw: cw, mw: mw };
}

/* 高亮块编号：与「视图」无关的稳定索引（key = 组id#序号），
   否则切「按段落 / 按类型」时 DOM 顺序变了、高亮会跳到别的句子上 */
const swKeyMap = new Map();
let swKeyNext = 0;

function swKeyIdxOf(key) {
    if (!swKeyMap.has(key)) swKeyMap.set(key, swKeyNext++);
    return swKeyMap.get(key);
}

function swBuildKeyMap() {
    swKeyMap.clear();
    swKeyNext = 0;
    (SW.banks || []).forEach(b => (b.items || []).forEach((_, i) => swKeyIdxOf(b.id + '#' + i)));
    ['note1', 'note2', 'note3', 'noteType'].forEach(swKeyIdxOf);
    // 精选范文里润色过的句子用独立键 L:类型#序（放在既有键之后，保证老高亮索引不移位）
    // letters 值为 {rows, cn_paras}（兼容旧的纯 list 结构）
    Object.keys(SW.letters || {}).forEach(t => {
        const v = SW.letters[t];
        const rows = (v && v.rows) || (Array.isArray(v) ? v : []);
        rows.forEach((_, i) => swKeyIdxOf('L:' + t + '#' + i));
    });
    // 场景范文（letters[t].variants）的改写句用带变体名的键：L:类型:变体#序。
    // 必须追加在最后 —— 老键索引一个都不动，本地已存的高亮/批注才不会错位。
    Object.keys(SW.letters || {}).forEach(t => {
        const v = SW.letters[t];
        ((v && v.variants) || []).forEach(vr => {
            (vr.rows || []).forEach((_, i) => swKeyIdxOf('L:' + t + ':' + vr.id + '#' + i));
        });
    });
}

/* ---------- 渲染 ---------- */

function swLine(it, no, key) {
    const ex = (it.ex || []).map(e => `
        <div class="sw-ex">
            <div class="sw-ex-tag">✍ 真题示例${e.src ? ' · ' + swEsc(e.src) : ''}</div>
            <div class="sw-ex-en">${swKwPh(e.en)}</div>
            ${e.cn ? `<div class="sw-ex-cn">${swPh(e.cn)}</div>` : ''}
        </div>`).join('');
    return `<li class="sw-line" data-k="${key}">
        <div class="sw-en"><span class="sw-no">${no}</span>${swStars(it)}${it.tag ? `<span class="sw-tag">${swEsc(it.tag)}</span>` : ''}<span class="sw-en-txt">${swKwPh(it.en)}</span></div>
        ${it.cn ? `<div class="sw-cn">${swPh(it.cn)}</div>` : ''}
        ${it.alts ? swAlts(it.alts) : ''}
        ${ex}
    </li>`;
}

function swAlts(alts) {
    if (!alts) return '';
    return `<div class="wr-alts">✎ 同义升级：${swEsc(alts)}</div>`;
}

function swFrameHtml(fw) {
    if (!fw || !fw.length) return '';
    return `<div class="wr-frame"><div class="wr-frame-title">🧩 信件拼装框架（${fw.length} 步 · 所有信都这么拼）</div>`
        + fw.map((f, i) => `<div class="wr-frame-step"><span class="wr-frame-no">${i + 1}</span><span class="wr-frame-txt"><span class="wr-frame-en">${swEsc(f.en)}</span>${f.trans ? `<span class="wr-frame-trans">${swEsc(f.trans)}</span>` : ''}<span class="wr-frame-cn">${swEsc(f.cn)}</span></span></div>`).join('')
        + '</div>';
}

function swLinkersHtml(lk) {
    if (!lk || !lk.length) return '';
    return `<div class="wr-alts">✎ 高级衔接词：${lk.map(x => `<span class="wr-alt"><b>${swEsc(x.banned)}</b> → ${swEsc(x.better)}</span>`).join('<span class="wr-alt-sep">｜</span>')}</div>`;
}

function swCard(bank, order, uid) {
    const items = (bank.items || []).filter(x => !x.hidden);   // hidden = 数据层判定的不实用句，检索页不渲染
    const n = items.length;
    const tb = swBankTier(bank);
    const opened = n <= 14 || tb.core > 0;
    const badges = (tb.core ? `<span class="sw-badge b-core">⭐⭐ 骨架 ${tb.core} 句 · ${tb.cw} 词</span>` : '')
        + (tb.must ? `<span class="sw-badge b-must">⭐ 必背 ${tb.must} 句 · ${tb.mw} 词</span>` : '')
        + `<span class="sw-badge b-ammo">⚡ 弹药 ${tb.ammo} 句</span>`;
    return `<details class="sw-card"${opened ? ' open' : ''} id="${swEsc(uid)}" data-bank="${swEsc(bank.id)}">
        <summary class="sw-card-head">
            <span class="sw-card-title">${order ? `<span class="sw-ord">${order}</span>` : ''}${swEsc(bank.label)}</span>
            ${badges}
            <span class="sw-card-n">${n} 句</span>
            <button type="button" class="sw-copy" data-copy="${swEsc(bank.id)}" title="复制这一组句子">复制</button>
        </summary>
        <ol class="sw-list">${bank.items.map((it, i) => it.hidden ? '' : swLine(it, i + 1, bank.id + '#' + i)).join('')}</ol>
    </details>`;
}

function swPartNote(part) {
    const ns = (SW.notes || []).filter(n => n.part === part).map(n => n.text);
    return ns.length ? `<div class="sw-note" data-k="note${part}">💡 ${ns.map(swEsc).join('<br>')}</div>` : '';
}

function swRender() {
    const box = document.getElementById('swContent');
    if (!box || !SW) return;
    let html = '';
    html += swFrameHtml(SW.framework) + swLinkersHtml(SW.linkers);
    if (swView === 'part') {
        const heads = { 1: '第一段 · 开头（问候 + 来意）', 2: '第二段 · 主体（展开内容）', 3: '第三段 · 收尾（客套 / 期待回复）' };
        [1, 2, 3].forEach(p => {
            const bs = SW.banks.filter(b => b.part === p);
            if (!bs.length) return;
            html += `<section class="sw-part"><h2 class="sw-h2" id="swP${p}">${heads[p]}</h2>`
                + swPartNote(p) + bs.map(b => swCard(b, '', 'swB-p-' + b.id)).join('') + '</section>';
        });
    } else {
        html += `<div class="sw-note" data-k="noteType">💡 小作文第二段极其灵活：可以<b>跨类型混搭</b>——比如从「建议类」挑 2 句、从「祝贺类」挑 1 句。下面每一类按<b>拼装顺序</b>排好了（首句 / 来意 / 通用首句 → 该类型二三四句 → 收尾），照着从上往下挑 2~4 句即可。</div>`;
        SW.types.forEach(t => {
            const bs = (t.banks || []).map(swBank).filter(Boolean);
            if (!bs.length) return;
            html += `<section class="sw-part"><h2 class="sw-h2" id="swT-${swEsc(t.id)}">${swEsc(t.name)}</h2>
                ${t.note ? `<div class="sw-note">⚠ ${swEsc(t.note)}</div>` : ''}
                <div class="sw-path">${bs.map(b => `<span class="sw-path-node">${swEsc(b.label.replace('第一段 · ', '').replace('第二段 · ', '').replace('第三段 · ', ''))}</span>`).join('<span class="sw-path-arrow">→</span>')}</div>
                ${bs.map(b => swCard(b, b.id === 'p1s1' || b.id === 'p2s1' || b.id === 'p3' ? '共用' : '本类', 'swB-t-' + t.id + '-' + b.id)).join('')}</section>`;
        });
    }
    box.innerHTML = html;
    swRestoreAll();
    swSyncOpenBtn();
    swTocBuild();
}

function swExpandAll(on) {
    document.querySelectorAll('#swContent details.sw-card').forEach(d => { d.open = !!on; });
    swSyncOpenBtn();
}

function swSyncOpenBtn() {
    const all = [...document.querySelectorAll('#swContent details.sw-card')];
    const b = document.getElementById('swExpandBtn');
    if (!b) return;
    const allOpen = all.length && all.every(d => d.open);
    b.textContent = allOpen ? '收起全部' : '展开全部';
}

/* ==================== 整信背诵（主区） ====================
   一次拼一封完整信（称呼/标题 → P1 问候+来意 → P2 引出+本类句 → P3 收尾 → 落款），
   点句子切换当前句（展开该句译文/示例），← → 键翻句；译文默认遮住方便自背。 */
const SW_TYPE_KEY = 'sw_type_v1';
let swType = 'advice';            // 当前信件类型 id
let swVariant = '';               // 当前类型的场景范文 id（'' = 通用范文）
let swAllCn = false;              // 「显示全部译文」开关
let swLetterCache = [];           // 当前信的行结构（复制整封用）
let swLetterCnParas = [];         // 当前信的分三段译文（段末按钮展开）
let swLetterBound = false;

/** 各类型来意句（p1s2）与引出句（p2s1）的 tag 匹配词 */
const SW_TYPE_KW = {
    advice: '建议', invite: '邀请', thanks: '感谢', congrats: '祝贺', apology: '道歉',
    complaint: '投诉', intro: '介绍', notice: '通知', inquire: '询问', opinion: '观点',
    minutes: '纪要'
};

/** 当前类型的场景范文对象（letters[类型].variants 里按 id 取；空 = 通用范文） */
function swVariantOf(typeId) {
    if (!swVariant) return null;
    const raw = (SW.letters || {})[typeId];
    const vs = (raw && raw.variants) || [];
    return vs.filter(v => v.id === swVariant)[0] || null;
}

/** 从 bank 里挑一句：kw 非空按 tag 匹配 → 否则 core → 兜底第一句 */
function swPick(bankId, kw) {
    const b = swBank(bankId);
    const items = (b && b.items) || [];
    if (!items.length) return null;
    if (kw) { const hit = items.find(it => (it.tag || '').indexOf(kw) >= 0); if (hit) return hit; }
    return items.find(it => it.tier === 'core') || items[0];
}

/** 拼一封完整信 → 行结构数组（kind: title/sal/sent/br/sig/signame/signote）
 *  优先用数据层精选润色范文 SW.letters[类型]（行 = [src, en, cn]，src=来源 bank#idx）；
 *  缺失时回落机械拼装（tag 匹配 + must 优先）。 */
function swLetterLines(typeId) {
    const types = SW.types || [];
    const t = types.find(x => x.id === typeId) || types[0];
    if (!t) return [];
    const kw = SW_TYPE_KW[t.id] || '';
    const isNotice = t.id === 'notice';
    const isMinutes = t.id === 'minutes';   // 会议纪要：标题 Minutes，无称呼，落款 Minutes recorder
    const V = swVariantOf(t.id);            // 场景范文（招募志愿者 / 推荐信）；无则走通用整信
    const kscope = V ? (t.id + ':' + V.id) : t.id;   // 改写句的高亮键前缀，避免与通用整信撞键
    const out = [];
    let sentIdx = 0;
    /** src 来源句未改动 → 共享句库高亮键；润色过的句子 → 独立 L:类型#序 键 */
    const pushSent = (en, cn, src, orig) => {
        const same = !!orig && orig.en === en;
        const parts = String(src || '').split('#');
        out.push({
            kind: 'sent',
            bank: same ? parts[0] : null,
            idx: same ? Number(parts[1]) : -1,
            k: same ? src : ('L:' + kscope + '#' + sentIdx),
            item: {
                en: en, cn: cn,
                alts: same ? (orig.alts || '') : '',
                ex: same ? (orig.ex || []) : [],
                tier: '', tag: ''
            }
        });
        sentIdx++;
    };
    const srcOrig = src => {
        const p = String(src || '').split('#');
        const items = ((swBank(p[0]) || {}).items) || [];
        return items[Number(p[1])] || null;
    };
    const emitBank = (bankId, item) => {
        if (!item) return;
        const items = ((swBank(bankId) || {}).items) || [];
        const i = items.indexOf(item);
        pushSent(item.en, item.cn, bankId + '#' + i, item);
    };
    // 格式行：会议纪要 = 标题 Minutes（无称呼）；通知 = 居中标题 NOTICE；其余 = 称呼顶格
    // 场景范文可覆盖标题 / 称呼（如推荐信写给朋友 = Dear Jack,）
    if (isMinutes) out.push({ kind: 'title', text: (V && V.title) || 'Minutes' });
    else if (isNotice) out.push({ kind: 'title', text: (V && V.title) || 'NOTICE' });
    else out.push({ kind: 'sal', text: (V && V.sal) || 'Dear Sir or Madam,' });
    const Lraw = V || (SW.letters || {})[t.id];
    const L = Lraw && (Lraw.rows || (Array.isArray(Lraw) ? Lraw : null));
    swLetterCnParas = (Lraw && Lraw.cn_paras) || [];
    if (L && L.length) {
        // 精选范文：按来源 bank 的 part 自动分段（p1* / p2* / p3 之间插 br）
        let lastPart = null;
        L.forEach(row => {
            const src = String(row[0] || '');
            const bank = swBank(src.split('#')[0]);
            // 空 src = 整信专用句（letters 里新增的通用收尾等）→ 默认归第三段收尾，避免错分段
            const part = bank ? bank.part : 3;
            if (lastPart !== null && part !== lastPart) out.push({ kind: 'br' });
            lastPart = part;
            pushSent(row[1], row[2], src, srcOrig(src));
        });
    } else if (isMinutes) {
        // 会议纪要兜底拼装（数据层缺 letters.minutes 时）：目的 | 要素+讨论 | 结论
        emitBank('m_s1', swPick('m_s1', ''));
        out.push({ kind: 'br' });
        emitBank('m_s2', swPick('m_s2', ''));
        emitBank('m_s3', swPick('m_s3', ''));
        out.push({ kind: 'br' });
        emitBank('m_s4', swPick('m_s4', ''));
    } else {
        // 机械拼装（fallback）：问候 + 来意 | 引出 + 本类 must | 收尾
        emitBank('p1s1', swPick('p1s1', ''));
        emitBank('p1s2', swPick('p1s2', kw));
        out.push({ kind: 'br' });
        emitBank('p2s1', swPick('p2s1', t.id === 'advice' ? '建议' : (t.id === 'invite' ? '活动安排' : '')));
        const mid = (t.banks || []).filter(id => ['p1s1', 'p1s2', 'p2s1', 'p3'].indexOf(id) < 0);
        mid.forEach(id => {
            const items = ((swBank(id) || {}).items) || [];
            if (items.length) emitBank(id, items.find(it => it.tier === 'must') || items[0]);
        });
        out.push({ kind: 'br' });
        const p3items = ((swBank('p3') || {}).items) || [];
        emitBank('p3', (isNotice && p3items.find(it => /notice/i.test(it.en || ''))) || swPick('p3', ''));
    }
    // 落款：会议纪要 = Minutes recorder: Li Ming（不写 Yours sincerely）；通知不写人名落款
    if (isMinutes) out.push({ kind: 'sig', text: 'Minutes recorder: Li Ming' });
    else if (isNotice) out.push({ kind: 'signote', text: '（通知类不写人名落款 · 落款按题目写组织名）' });
    else { out.push({ kind: 'sig', text: 'Yours sincerely,' }); out.push({ kind: 'signame', text: 'Li Ming' }); }
    return out;
}

/** 渲染整封信到 #swLetter —— 作文排版 + 分三段翻译：
 *  正文句为 inline span 连排成段（首行缩进、无序号/星星/标签），段末带「📖 本段译文」按钮，
 *  点击展开该段整体中文（三段分开，替代逐句翻译）。data-k：来源未改 = 句库键（共享高亮），润色句 = L:键。 */
function swLetterRender() {
    const box = document.getElementById('swLetter');
    if (!box || !SW) return;
    swLetterCache = swLetterLines(swType);
    // 分段：br 断段；称呼/标题/落款各自成段
    const groups = [];
    let cur = null;
    swLetterCache.forEach(l => {
        if (l.kind === 'br') { cur = null; return; }
        if (l.kind === 'title' || l.kind === 'sal') { groups.push({ cls: 'sw-para', lines: [l] }); cur = null; return; }
        if (l.kind === 'sig' || l.kind === 'signame' || l.kind === 'signote') {
            if (!cur || cur.cls.indexOf('sw-para-sig') < 0) { cur = { cls: 'sw-para sw-para-sig', lines: [] }; groups.push(cur); }
            cur.lines.push(l); return;
        }
        if (!cur || cur.cls.indexOf('sw-para-body') < 0) { cur = { cls: 'sw-para sw-para-body', lines: [] }; groups.push(cur); }
        cur.lines.push(l);
    });
    let no = 0, bodyNo = 0;
    box.innerHTML = groups.map(g => {
        const isBody = g.cls.indexOf('sw-para-body') >= 0;
        const pi = isBody ? bodyNo++ : -1;
        let html = g.lines.map(l => {
            if (l.kind === 'title') return `<div class="sw-title-line">${swEsc(l.text)}</div>`;
            if (l.kind === 'sal') return `<div class="sw-sal">${swEsc(l.text)}</div>`;
            if (l.kind === 'sig') return `<div class="sw-sig">${swEsc(l.text)}</div>`;
            if (l.kind === 'signame') return `<div class="sw-signame">${swEsc(l.text)}</div>`;
            if (l.kind === 'signote') return `<div class="sw-signote">${swEsc(l.text)}</div>`;
            const it = l.item;
            const i = no++;
            // 句译块：默认 hidden（不打断段落流），点句子开合（移植阅读页的点句翻译）
            return `<span class="sw-ls" data-k="${swEsc(l.k)}" data-i="${i}" title="点句看该句中文">${swKwPh(it.en)}</span>`
                + `<div class="sw-ls-cn" data-for="${i}" hidden>${it.cn ? swPh(it.cn) : ''}</div>`;
        }).join('');
        if (isBody && swLetterCnParas[pi]) {
            html += `<button type="button" class="sw-para-cn-btn" data-para="${pi}">📖 本段译文 ▾</button>`
                + `<div class="sw-para-cn" data-para="${pi}" hidden>${swPh(swLetterCnParas[pi])}</div>`;
        }
        return `<div class="${g.cls}">${html}</div>`;
    }).join('');
    swApplyAllCn();   // 「显示全部译文」状态跨类型保持
    swLetterSync();
    swRestoreAll();   // 高亮/批注按 data-k 重建（来源句与句子库视图共享，润色句走 L:键）
}

/** 同步「显示全部译文」按钮态 */
function swLetterSync() {
    const ab = document.getElementById('swAllCnBtn');
    if (ab) { ab.textContent = swAllCn ? '收起全部译文' : '显示全部译文'; ab.setAttribute('aria-pressed', swAllCn ? 'true' : 'false'); }
}

/** 按 swAllCn 状态铺开/收起三段译文（连带段末按钮文案） */
function swApplyAllCn() {
    const box = document.getElementById('swLetter');
    if (!box) return;
    box.querySelectorAll('.sw-para-cn').forEach(d => { d.hidden = !swAllCn; });
    box.querySelectorAll('.sw-para-cn-btn').forEach(b => { b.textContent = swAllCn ? '📖 收起本段译文 ▴' : '📖 本段译文 ▾'; });
}

/** 点段末按钮：单独展开/收起该段译文 */
function swParaToggle(pi) {
    const box = document.getElementById('swLetter');
    if (!box) return;
    const d = box.querySelector('.sw-para-cn[data-para="' + pi + '"]');
    const b = box.querySelector('.sw-para-cn-btn[data-para="' + pi + '"]');
    if (!d) return;
    d.hidden = !d.hidden;
    if (b) b.textContent = d.hidden ? '📖 本段译文 ▾' : '📖 收起本段译文 ▴';
}

/** 复制整封（占位符 {{}} 保留原文，直接当模板） */
function swLetterCopy() {
    const txt = [];
    let prev = null;
    swLetterCache.forEach(l => {
        if (l.kind === 'br') { txt.push(''); prev = 'br'; return; }
        if (l.kind === 'sent') { txt.push(l.item.en); prev = 'sent'; return; }
        if (l.kind === 'sig') { if (prev !== 'br' && txt.length) txt.push(''); txt.push(l.text); prev = 'sig'; return; }
        if (txt.length && prev !== 'br') txt.push('');
        txt.push(l.text); prev = l.kind;
    });
    const body = txt.join('\n');
    const btn = document.getElementById('swCopyLetter');
    const done = () => { if (btn) { btn.textContent = '已复制'; setTimeout(() => { btn.textContent = '复制整封'; }, 1200); } };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(body).then(done, done);
    else {
        const ta = document.createElement('textarea');
        ta.value = body; document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); } catch (e) { /* ignore */ }
        ta.remove(); done();
    }
}

/** 类型 tab + 初始化（swInit 调用一次） */
function swLetterTabs() {
    const box = document.getElementById('swTypeTabs');
    if (!box || !SW) return;
    box.innerHTML = (SW.types || []).map(t =>
        `<button type="button" class="sw-ttab${t.id === swType ? ' on' : ''}" data-t="${swEsc(t.id)}">${swEsc(t.name)}</button>`).join('');
}

/** 场景范文切换条（仅当当前类型有 variants 时显示；无则整条隐藏） */
function swVariantTabs() {
    const box = document.getElementById('swVarTabs');
    const note = document.getElementById('swVarNote');
    if (!box || !SW) return;
    const raw = (SW.letters || {})[swType];
    const vs = (raw && raw.variants) || [];
    if (!vs.length) {
        swVariant = '';
        box.hidden = true;
        box.innerHTML = '';
        if (note) { note.hidden = true; note.innerHTML = ''; }
        return;
    }
    box.hidden = false;
    box.innerHTML = '<span class="sw-var-tip">范文</span>'
        + [{ id: '', name: '通用' }].concat(vs).map(v =>
            `<button type="button" class="sw-vtab${(v.id || '') === swVariant ? ' on' : ''}" data-v="${swEsc(v.id || '')}">${swEsc(v.name)}</button>`
        ).join('');
    const cur = swVariantOf(swType);
    if (note) {
        note.hidden = !(cur && cur.note);
        note.innerHTML = (cur && cur.note) ? '💡 ' + swPh(cur.note) : '';
    }
}

function swLetterInit() {
    try { swType = localStorage.getItem(SW_TYPE_KEY) || 'advice'; } catch (e) { swType = 'advice'; }
    if (!(SW.types || []).some(t => t.id === swType)) swType = ((SW.types || [])[0] || {}).id || 'advice';
    swLetterTabs();
    swVariantTabs();
    swLetterRender();
    if (swLetterBound) return;
    swLetterBound = true;
    // 段末「本段译文」按钮（委托，重渲染后仍有效）
    // 点击委托（重渲染后仍有效）：段末译文按钮 / 点句开合该句中文 / 点译块关闭
    const lbox = document.getElementById('swLetter');
    if (lbox) lbox.addEventListener('click', e => {
        if (!e.target.closest) return;
        const pb = e.target.closest('.sw-para-cn-btn');
        if (pb && pb.dataset.para != null) { swParaToggle(Number(pb.dataset.para)); return; }
        const cnBox = e.target.closest('.sw-ls-cn');
        if (cnBox) { cnBox.hidden = true; return; }
        const s = e.target.closest('.sw-ls');
        if (s && s.dataset.i != null) {
            // 划词选中文字 / 点已有高亮时不触发（避免选词高亮误开译文）
            const sel = typeof window.getSelection === 'function' ? window.getSelection() : null;
            if (sel && String(sel).length) return;
            if (e.target.closest('mark.note-hl')) return;
            const cn = lbox.querySelector('.sw-ls-cn[data-for="' + s.dataset.i + '"]');
            if (cn) cn.hidden = !cn.hidden;
        }
    });
    const tbox = document.getElementById('swTypeTabs');
    if (tbox) tbox.addEventListener('click', e => {
        const b = e.target.closest ? e.target.closest('.sw-ttab') : null;
        if (!b || b.dataset.t === swType) return;
        swType = b.dataset.t;
        swVariant = '';                    // 换类型 → 回到「通用」范文
        try { localStorage.setItem(SW_TYPE_KEY, swType); } catch (e2) { /* ignore */ }
        swLetterTabs();
        swVariantTabs();
        swLetterRender();
    });
    const vbox = document.getElementById('swVarTabs');
    if (vbox) vbox.addEventListener('click', e => {
        const b = e.target.closest ? e.target.closest('.sw-vtab') : null;
        if (!b || b.dataset.v === swVariant) return;
        swVariant = b.dataset.v || '';
        swVariantTabs();
        swLetterRender();
    });
    const ab = document.getElementById('swAllCnBtn');
    if (ab) ab.addEventListener('click', () => { swAllCn = !swAllCn; swApplyAllCn(); swLetterSync(); });
    const cb = document.getElementById('swCopyLetter');
    if (cb) cb.addEventListener('click', swLetterCopy);
}

/* ---------- 初始化 ---------- */

function swRenderLegend() {
    const ph = (SW.placeholders || []);
    const box = document.getElementById('swLegend');
    if (!box) return;
    box.innerHTML = `
        <summary class="wr-legend-head">占位符图例<span class="wr-legend-tip">模板里 <b>{{ }}</b> 包住的英文，按你的题目替换；词句本身不要动（共 ${ph.length} 个 · 点开查看）</span></summary>
        <div class="wr-legend-grid">${ph.map(x => `
            <div class="wr-legend-row">
                <code class="wr-legend-tok">{{${swEsc(x[0])}}}</code>
                <span class="wr-legend-cn">${swEsc(x[1])}</span>
            </div>`).join('')}</div>`;
}

function swRenderSteps() {
    const box = document.getElementById('swSteps');
    if (!box) return;
    box.innerHTML = (SW.steps || []).map(s => `
        <div class="sw-step">
            <div class="sw-step-no">${s.no}</div>
            <div class="sw-step-body"><b>${swEsc(s.name)}</b>${swRich(s.body)}</div>
        </div>`).join('');
}

function swSyncViewBtns() {
    document.querySelectorAll('.sw-vbtn').forEach(b => b.classList.toggle('on', b.dataset.view === swView));
}

function swBind() {
    document.querySelectorAll('.sw-vbtn').forEach(b => {
        b.addEventListener('click', () => {
            swView = b.dataset.view;
            try { localStorage.setItem(SW_VIEW_KEY, swView); } catch (e) { /* ignore */ }
            swSyncViewBtns();
            swRender();
        });
    });
    const eb = document.getElementById('swExpandBtn');
    if (eb) eb.addEventListener('click', () => {
        const all = [...document.querySelectorAll('#swContent details.sw-card')];
        swExpandAll(!(all.length && all.every(d => d.open)));
    });
    document.addEventListener('click', e => {
        const c = e.target.closest ? e.target.closest('.sw-copy') : null;
        if (!c) return;
        e.preventDefault();
        e.stopPropagation();
        const b = swBank(c.dataset.copy);
        if (!b) return;
        const txt = b.items.map((it, i) => (i + 1) + '. ' + it.en).join('\n');
        const done = () => { c.textContent = '已复制'; setTimeout(() => { c.textContent = '复制'; }, 1200); };
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(txt).then(done, done);
        } else {
            const ta = document.createElement('textarea');
            ta.value = txt; document.body.appendChild(ta); ta.select();
            try { document.execCommand('copy'); } catch (err) { /* ignore */ }
            ta.remove(); done();
        }
    });
}

async function swInit() {
    const box = document.getElementById('swContent');
    await kwLoad();            // 范文重点短语：先就绪，首帧渲染就能点
    kwBind();
    try {
        const res = await fetch('data/small_writing.json', { cache: 'no-cache' });
        SW = await res.json();
    } catch (e) {
        if (box) box.innerHTML = '<p style="color:var(--text-light)">数据加载失败，请刷新重试</p>';
        return;
    }
    const m = SW.meta || {};
    const t = document.getElementById('swTitle');
    if (t && m.title) t.textContent = '📝 ' + m.title;
    const d = document.getElementById('swDesc');
    if (d) d.innerHTML = swEsc(m.desc || '');
    document.title = (m.title || '小作文') + ' - 英语真题精翻';
    try { swView = localStorage.getItem(SW_VIEW_KEY) || 'part'; } catch (e) { swView = 'part'; }
    if (swView !== 'type') swView = 'part';
    swMkLoad();          // 载入已存的划词高亮 + 行批注（此前漏调会被空数组覆盖，2026-09-22 修复）
    swBuildKeyMap();
    swRenderLegend();
    swRenderSteps();
    swDrillRender();
    swDrillBind();
    swRenderStats();
    swRenderGuide();
    swRenderDecisions();
    swSyncViewBtns();
    swRender();
    swLetterInit();
    swBind();
    swTocBind();
    swTocSpy();
    const st = document.getElementById('swStudy');
    if (st && SW.study) st.innerHTML = '📌 <b>怎么用</b>：' + swEsc(SW.study);
    const n = document.getElementById('swMkCount');
    if (n) n.textContent = String(swMarks.length);
    swHlBind();
    swNavHVar();
    window.addEventListener('resize', swNavHVar);
    window.addEventListener('navheightchange', () => { swNavHVar(); swTocSpy(); });
}


/* ==================== 24 句必背 · 集中清单（背诵主入口） ====================
   只读 tier=core/must 的句子，按「第一段 / 第二段 / 第三段」分类，段内保留细分小节。
   纯展示：不写 swKeyMap、不挂 data-k，故不影响既有划词高亮/批注的键位。 */
const SW_DRILL_CN_KEY = 'sw_drill_cn_v1';
const SW_DRILL_FILL_KEY = 'sw_drill_fill_v1';
let swDrillCn = false, swDrillFill = false;

/** 把英文里的 {{token}} 变成可点填空（默认遮住，点开显示）；非填空态正常显示芯片 */
function swDrillEn(en) {
    return String(en == null ? '' : en).split(/(\{\{[^}]+\}\})/g).map(seg => {
        const m = /^\{\{([^}]+)\}\}$/.exec(seg);
        if (!m) return swEsc(seg);
        return '<span class="sw-drill-ph" tabindex="0" role="button" title="点开看填什么">' + swEsc(m[1]) + '</span>';
    }).join('');
}

/** 按段落取必背句，分三段；每段内保留细分小节（小节只是标题，不再各自折叠） */
function swDrillGroups() {
    const pick = (bankId) => {
        const b = swBank(bankId);
        if (!b) return [];
        return (b.items || []).map((it, i) => ({ it: it, key: bankId + '#' + i }))
            .filter(x => x.it.tier === 'core' || x.it.tier === 'must');
    };
    const sub = (title, bankIds) => {
        const rows = bankIds.flatMap(pick);
        return rows.length ? { title: title, rows: rows } : null;
    };
    // 第一段：问候 + 来意
    const p1 = [sub('问候 / 自我介绍', ['p1s1']), sub('表明来意', ['p1s2'])].filter(Boolean);
    // 第二段：通用引出 + 各类型 s2/s3
    const p2 = [sub('通用引出', ['p2s1'])];
    (SW.types || []).forEach(t => {
        const s = sub(t.name, (t.banks || []).filter(id => /^p2_/.test(id)));
        if (s) p2.push(s);
    });
    // 第三段：收尾
    const p3 = [sub('收尾 / 客套', ['p3'])].filter(Boolean);
    return [
        { title: '第一段 · 开头', core: true, subs: p1 },
        { title: '第二段 · 主体', core: false, subs: p2.filter(Boolean) },
        { title: '第三段 · 收尾', core: true, subs: p3 },
    ];
}

function swDrillRender() {
    const box = document.getElementById('swDrill');
    if (!box || !SW) return;
    const groups = swDrillGroups();
    const total = groups.reduce((n, g) => n + g.subs.reduce((s, x) => s + x.rows.length, 0), 0);
    let h = '<div class="sw-drill-sum">共 <b>' + total + '</b> 句 · ⭐⭐ 骨架 4 句全信通用 + ⭐ 必背每类型 2 句'
        + ' · <b>' + (SW.stats ? (SW.stats.core_words + SW.stats.must_words) : 398) + '</b> 词，30 天约 '
        + (SW.stats ? ((SW.stats.core_words + SW.stats.must_words) / 30).toFixed(1) : '13.3') + ' 词/天</div>';
    h += groups.map(g => {
        const n = g.subs.reduce((s, x) => s + x.rows.length, 0);
        return '<details class="sw-drill-grp" open>'
            + '<summary><span class="sw-drill-gt">' + swEsc(g.title) + '</span>'
            + '<span class="sw-drill-gn">' + n + ' 句</span></summary>'
            + g.subs.map(s => '<div class="sw-drill-sub">'
                + '<div class="sw-drill-sub-t">' + swEsc(s.title) + '</div>'
                + '<ol class="sw-drill-list">' + s.rows.map(r => '<li class="sw-drill-line">'
                    + '<div class="sw-drill-en">' + swDrillEn(r.it.en) + '</div>'
                    + '<div class="sw-drill-cn">' + swPh(r.it.cn || '') + '</div>'
                    + '</li>').join('') + '</ol></div>').join('')
            + '</details>';
    }).join('');
    box.innerHTML = h;
    swDrillApply();
}

/** 应用中文显隐 + 填空遮罩状态（纯 class 切换，不重写 DOM，保留已点开的填空） */
function swDrillApply() {
    const box = document.getElementById('swDrill');
    if (box) box.classList.toggle('show-cn', swDrillCn);
    document.body.classList.toggle('sw-drill-on', swDrillFill);
    const cb = document.getElementById('swDrillCnBtn');
    const fb = document.getElementById('swDrillFillBtn');
    if (cb) { cb.textContent = swDrillCn ? '隐藏中文' : '显示中文'; cb.classList.toggle('on', swDrillCn); cb.setAttribute('aria-pressed', String(swDrillCn)); }
    if (fb) { fb.textContent = swDrillFill ? '退出填空' : '填空自测'; fb.classList.toggle('on', swDrillFill); fb.setAttribute('aria-pressed', String(swDrillFill)); }
}

function swDrillBind() {
    const cb = document.getElementById('swDrillCnBtn');
    const fb = document.getElementById('swDrillFillBtn');
    if (cb) cb.addEventListener('click', () => {
        swDrillCn = !swDrillCn;
        try { localStorage.setItem(SW_DRILL_CN_KEY, swDrillCn ? '1' : '0'); } catch (e) {}
        swDrillApply();
    });
    if (fb) fb.addEventListener('click', () => {
        swDrillFill = !swDrillFill;
        try { localStorage.setItem(SW_DRILL_FILL_KEY, swDrillFill ? '1' : '0'); } catch (e) {}
        if (!swDrillFill) document.querySelectorAll('#swDrill .sw-drill-ph.on').forEach(x => x.classList.remove('on'));
        swDrillApply();
    });
    const box = document.getElementById('swDrill');
    if (box) box.addEventListener('click', e => {
        const ph = e.target.closest && e.target.closest('.sw-drill-ph');
        if (ph && swDrillFill) ph.classList.toggle('on');
    });
    try { swDrillCn = localStorage.getItem(SW_DRILL_CN_KEY) === '1'; } catch (e) {}
    try { swDrillFill = localStorage.getItem(SW_DRILL_FILL_KEY) === '1'; } catch (e) {}
}

/* ==================== 顶部指标 ==================== */
function swRenderStats() {
    const box = document.getElementById('swStats');
    const s = SW.stats;
    if (!box || !s) return;
    const chips = [
        ['total', s.items + ' 句', '句库总量（' + s.banks + ' 组）'],
        ['core', '⭐⭐ 骨架 ' + s.core + ' 句', '任何一封信都要用 · 共 ' + s.core_words + ' 词'],
        ['must', '⭐ 必背 ' + s.must + ' 句', '每类型 2 句 · 共 ' + s.must_words + ' 词'],
        ['ammo', '⚡ 弹药 ' + s.ammo + ' 句', '不用背，写的时候现挑'],
        ['days', ((s.core_words + s.must_words) / 30).toFixed(1) + ' 词/天', '按 30 天背完 ⭐/⭐⭐ 算'],
        ['guide', s.guide + ' 年真题', '2010–2026 英语二 A 节'],
    ];
    box.innerHTML = chips.map(c =>
        '<div class="sw-chip c-' + c[0] + '" title="' + swEsc(c[2]) + '">' + swEsc(c[1]) + '</div>').join('');
}

/* ==================== 真题适配表 ==================== */
function swRenderGuide() {
    const box = document.getElementById('swGuide');
    if (!box || !SW.guide) return;
    box.innerHTML = '<table class="sw-gtable"><thead><tr>'
        + '<th>年份</th><th>题型</th><th>题目主题</th><th>该挑哪些句</th></tr></thead><tbody>'
        + SW.guide.map(r => '<tr>'
            + '<td class="sw-gy">' + swEsc(r.year) + '</td>'
            + '<td><span class="sw-gtag">' + swEsc(r.type) + '</span></td>'
            + '<td class="sw-gtop">' + swEsc(r.topic)
            + (r.aid ? ' <a class="sw-glink" href="article.html?id=' + encodeURIComponent(r.aid) + '" title="看题目原文">原文</a>' : '')
            + '</td>'
            + '<td class="sw-ghint">' + swRich(r.hint) + '</td>'
            + '</tr>').join('')
        + '</tbody></table>';
}

/* ==================== 选句决策 ==================== */
function swRenderDecisions() {
    const box = document.getElementById('swDecisions');
    if (!box || !SW.decisions) return;
    box.innerHTML = SW.decisions.map((x, i) => '<div class="sw-dec">'
        + '<div class="sw-dec-q"><span class="sw-dec-no">' + (i + 1) + '</span>' + swEsc(x.q) + '</div>'
        + '<div class="sw-dec-a">' + swRich(x.a) + '</div>'
        + '</div>').join('');
}

/* ==================== 悬浮目录（左侧，同大作文） ==================== */
const SW_TOC_KEY = 'sw_toc_fold';
const SW_TOC_NARROW = 1180;

function swTocItems() {
    const items = [];
    const push = (lv, id, text) => { if (document.getElementById(id)) items.push({ lv: lv, id: id, text: text }); };
    push(1, 'swLetterBlock', '整信背诵');
    push(1, 'swDrillBlock', '24 句必背');
    push(1, 'swLegend', '占位符图例');
    push(1, 'swStepsTitle', '小作文怎么拼');
    push(1, 'swGuideBlock', '真题适配表');
    push(1, 'swDecisionsTitle', '选句决策');
    push(1, 'swBankBlock', '句子库 · 拆分检索');
    document.querySelectorAll('#swContent h2.sw-h2').forEach(h => {
        if (swTocHidden(h)) return;   // 在收起的折叠区里 → 不进目录
        items.push({ lv: 1, id: h.id, text: h.textContent.trim() });
        let n = h.nextElementSibling;
        while (n && n.tagName !== 'H2') {
            if (n.classList && n.classList.contains('sw-card') && n.id && !swTocHidden(n)) {
                const ct = n.querySelector('.sw-card-title');
                if (ct) items.push({ lv: 2, id: n.id, text: ct.textContent.trim() });
            }
            n = n.nextElementSibling;
        }
    });
    return items;
}

/** 元素是否被收起的 <details> 藏住（details 自身与其 summary 永远可见，不算） */
function swTocHidden(el) {
    const cd = el.closest ? el.closest('details:not([open])') : null;
    if (!cd || cd === el) return false;
    return !(el.tagName === 'SUMMARY' && el.parentElement === cd);
}

function swTocBuild() {
    const list = document.getElementById('swTocList');
    if (!list) return;
    const items = swTocItems();
    list.innerHTML = items.map(x =>
        '<a class="lv' + x.lv + '" href="#' + swEsc(x.id) + '" data-target="' + swEsc(x.id) + '">' + swEsc(x.text) + '</a>').join('');
    swTocApplyFold(localStorage.getItem(SW_TOC_KEY) === '1' || window.innerWidth <= SW_TOC_NARROW);
    swTocSpy();
}

function swTocSpy() {
    const list = document.getElementById('swTocList');
    if (!list) return;
    const links = Array.prototype.slice.call(list.querySelectorAll('a[data-target]'));
    const top = swNavH() + 24;
    let cur = null;
    for (const a of links) {
        const el = document.getElementById(a.dataset.target);
        if (!el || swTocHidden(el)) continue;   // 收起的目标不参与高亮
        if (el.getBoundingClientRect().top <= top) cur = a; else break;
    }
    if (!cur) cur = links[0];
    links.forEach(a => a.classList.toggle('on', a === cur));
    if (cur && list.scrollHeight > list.clientHeight + 4) {
        const r = cur.getBoundingClientRect(), lr = list.getBoundingClientRect();
        if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - 24;
    }
}

function swTocApplyFold(folded) {
    document.body.classList.toggle('wr-toc-folded', !!folded);
    try { localStorage.setItem(SW_TOC_KEY, folded ? '1' : '0'); } catch (e) { /* ignore */ }
    if (folded) swTocClose();
}

function swTocToggleFold() { swTocApplyFold(!document.body.classList.contains('wr-toc-folded')); }

function swTocOpen() {
    if (window.innerWidth <= SW_TOC_NARROW) {
        document.body.classList.add('wr-toc-open');
        const m = document.getElementById('swTocMask');
        if (m) m.hidden = false;
    } else {
        swTocApplyFold(false);
    }
}

function swTocClose() {
    document.body.classList.remove('wr-toc-open');
    const m = document.getElementById('swTocMask');
    if (m) m.hidden = true;
}

function swTocGo(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - swNavH() - 12;
    window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
    try { history.replaceState(null, '', '#' + id); } catch (e) { /* ignore */ }
    if (window.innerWidth <= SW_TOC_NARROW) swTocClose();
}

function swTocBind() {
    const list = document.getElementById('swTocList');
    if (list) {
        list.addEventListener('click', e => {
            const a = e.target.closest ? e.target.closest('a[data-target]') : null;
            if (!a) return;
            e.preventDefault();
            swTocGo(a.dataset.target);
        });
    }
    window.addEventListener('scroll', () => { swTocSpy(); }, { passive: true });
    window.addEventListener('resize', () => { swTocSpy(); });
    // 参考区/句子库的 <details> 展开收起时，目录随之增删条目
    document.querySelectorAll('.sw-page details').forEach(d =>
        d.addEventListener('toggle', () => swTocBuild()));
}

/* ==================== 正文划词高亮 + 行批注（浮条交互，照搬 408 notes 页） ==================== */
const SW_MK_KEY = 'sw_mk_v1';
const SW_ANNO_KEY = 'sw_anno_v1';
const SW_HL_COLORS = ['yellow', 'green', 'blue', 'pink'];
const SW_HL_CN = { yellow: '黄色', green: '绿色', blue: '蓝色', pink: '粉色' };
const SW_MK_SEL = '.sw-line, .sw-note, .sw-ls';   // .sw-ls = 整信正文的句 span（作文排版）
let swMarks = [];        // 高亮 [{ c: 正文块序号, s: 起, e: 止, k: 颜色名 }]
let swAnnos = {};        // 行批注 { 正文块序号: 文本 }
let swHlBar = null;      // 划词浮条
let swHlTimer = null;

function swMkLoad() {
    try { swMarks = JSON.parse(localStorage.getItem(SW_MK_KEY) || '[]') || []; }
    catch (e) { swMarks = []; }
    if (!Array.isArray(swMarks)) swMarks = [];
    const LEGACY = { y: 'yellow', g: 'green', b: 'blue', p: 'pink' };
    swMarks = swMarks.filter(m => m && typeof m.c === 'number')
        .map(m => ({ c: m.c, s: m.s, e: m.e, k: SW_HL_COLORS.includes(m.k) ? m.k : (LEGACY[m.k] || 'yellow') }));
    try { swAnnos = JSON.parse(localStorage.getItem(SW_ANNO_KEY) || '{}') || {}; }
    catch (e) { swAnnos = {}; }
    if (!swAnnos || typeof swAnnos !== 'object' || Array.isArray(swAnnos)) swAnnos = {};
}

function swMkSave() {
    try { localStorage.setItem(SW_MK_KEY, JSON.stringify(swMarks)); } catch (e) { /* ignore */ }
    const c = document.getElementById('swMkCount');
    if (c) c.textContent = String(swMarks.length);
    const b = document.getElementById('swMkClearBtn');
    if (b) b.hidden = !swMarks.length;
}

function swAnnoSave() {
    try { localStorage.setItem(SW_ANNO_KEY, JSON.stringify(swAnnos)); } catch (e) { /* ignore */ }
}

/** 可高亮正文块：一次 DFS 收集（命中即收、不再下钻，天然去掉嵌套），按文档序编号 data-mk */
function swMkBlocks() {
    const out = [];
    (function walk(node) {
        for (const el of node.children) {
            if (el.matches(SW_MK_SEL)) { out.push(el); continue; }
            walk(el);
        }
    })(document.body);
    for (const el of out) {
        const k = (el.dataset && el.dataset.k) || null;
        el.setAttribute('data-mk', String(k ? swKeyIdxOf(k) : swKeyNext++));
    }
    return out;
}

function swMkBlockOf(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return (el && el.closest) ? el.closest('[data-mk]') : null;
}

function swInAnno(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    return !!(el && el.closest && el.closest('.wr-anno, .hl-toolbar'));
}

/** 块内全部 Text 节点 → [{node, start, len}]（按文档序，start = 块内字符偏移） */
function swMkTexts(el) {
    const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const out = []; let acc = 0;
    while (tw.nextNode()) {
        const n = tw.currentNode;
        out.push({ node: n, start: acc, len: n.data.length });
        acc += n.data.length;
    }
    return out;
}

function swMkOffset(texts, node, off) {
    for (const t of texts) if (t.node === node) return t.start + off;
    return null;
}

function swMkAt(texts, off) {
    for (const t of texts) {
        if (off <= t.start + t.len) return { node: t.node, off: off - t.start };
    }
    const last = texts[texts.length - 1];
    return last ? { node: last.node, off: last.len } : null;
}

function swMkRange(el, s, e) {
    const texts = swMkTexts(el);
    const a = swMkAt(texts, s), b = swMkAt(texts, e);
    if (!a || !b) return null;
    if (a.node === b.node && a.off === b.off) return null;
    const r = document.createRange();
    r.setStart(a.node, a.off);
    r.setEnd(b.node, b.off);
    return r;
}

/** 当前选区 → { block, i, s, e }；失败时返回 { err } */
function swMkSelInfo() {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return { err: 'none' };
    const r = sel.getRangeAt(0);
    const b1 = swMkBlockOf(r.startContainer), b2 = swMkBlockOf(r.endContainer);
    if (!b1 || !b2 || b1 !== b2) return { err: 'none' };
    const texts = swMkTexts(b1);
    const s = swMkOffset(texts, r.startContainer, r.startOffset);
    const e = swMkOffset(texts, r.endContainer, r.endOffset);
    if (s == null || e == null || e <= s) return { err: 'none' };
    return { block: b1, i: parseInt(b1.getAttribute('data-mk'), 10), s, e, range: r };
}

function swMkUnwrap(mk) {
    const f = document.createDocumentFragment();
    while (mk.firstChild) f.appendChild(mk.firstChild);
    if (mk.parentNode) mk.replaceWith(f);
}

/** 重建单个块内的高亮 */
function swMkPaint(block, i) {
    block.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    swMarks.filter(m => m.c === i).sort((a, b) => a.s - b.s).forEach(m => {
        const r = swMkRange(block, m.s, m.e);
        if (!r) return;
        const mk = document.createElement('mark');
        mk.className = 'note-hl note-hl-' + m.k;
        mk.dataset.start = String(m.s);
        mk.dataset.color = m.k;
        mk.title = '点击可取消这处高亮';
        try { mk.appendChild(r.extractContents()); r.insertNode(mk); } catch (e) { /* 越界忽略 */ }
    });
}

/** 全页重建：高亮 + 批注（渲染后 / 载入时调用） */
function swRestoreAll() {
    document.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    document.querySelectorAll('.wr-anno').forEach(x => x.remove());
    const blocks = swMkBlocks();
    const dirty = {};
    swMarks.forEach(m => { dirty[m.c] = 1; });
    blocks.forEach(b => {
        const i = parseInt(b.getAttribute('data-mk'), 10);
        if (dirty[i]) swMkPaint(b, i);
    });
    const byIdx = {};
    blocks.forEach(b => { byIdx[b.getAttribute('data-mk')] = b; });
    Object.keys(swAnnos).forEach(k => {
        if (swAnnos[k] && byIdx[k]) swAnnoRender(parseInt(k, 10), byIdx[k], swAnnos[k]);
    });
    swMkSave();
}

/* ---------- 上色 / 取消 ---------- */

function swHlApply(color) {
    const sr = swMkSelInfo();
    if (sr.err) { swHlBarHide(); return; }
    swMarks = swMarks.filter(m => !(m.c === sr.i && m.s < sr.e && sr.s < m.e));   // 重叠的先去掉
    swMarks.push({ c: sr.i, s: sr.s, e: sr.e, k: color });
    swRestoreAll();   // 同一句可能在多处渲染（按类型视图的共用卡），整页重绘保证一致
    swMkSave();
    swHideHlToolbar();
    const s = window.getSelection(); if (s) s.removeAllRanges();
}

/** 取消选区起点所在那处高亮 */
function swHlCancelAt(node) {
    const el = node && node.nodeType === 3 ? node.parentElement : node;
    const mk = (el && el.closest) ? el.closest('mark.note-hl') : null;
    if (!mk) return false;
    swHlRemoveMark(mk);
    return true;
}

function swHlRemoveMark(mk) {
    const block = mk.closest('[data-mk]');
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    const s = parseInt(mk.dataset.start, 10);
    const k = mk.dataset.color;
    swMarks = swMarks.filter(m => !(m.c === i && m.s === s && m.k === k));
    swRestoreAll();   // 同上：整页重绘
    swMkSave();
}

async function swMkClearAll() {
    if (!swMarks.length) return;
    if (typeof confirmAsync === 'function' && !(await confirmAsync('清除本页全部划词高亮？', { danger: true }))) return;
    swMarks = [];
    try { localStorage.removeItem(SW_MK_KEY); } catch (e) { /* ignore */ }
    document.querySelectorAll('mark.note-hl').forEach(swMkUnwrap);
    swMkSave();
}

/* ---------- 划词浮条（408 同款：4 色 + 📝批注 + ✕） ---------- */

function swHideHlToolbar() { if (swHlBar) { swHlBar.remove(); swHlBar = null; } }

/** 取选区位置：优先 Range 自带 rect，取不到（如 jsdom / 空选区）就退回起点元素 */
function swRectOf(range) {
    let rect = null;
    try { rect = range.getBoundingClientRect(); } catch (e) { rect = null; }
    if (!rect || (!rect.width && !rect.height)) {
        const n = range.startContainer;
        const el = n && n.nodeType === 1 ? n : (n && n.parentElement);
        if (el && el.getBoundingClientRect) rect = el.getBoundingClientRect();
    }
    return rect || { top: 0, bottom: 0, left: 0, width: 0, height: 0 };
}

/** 浮条定位：默认放选区上方，撞到导航栏/视口顶就翻到选区下方 */
function swHlBarPlace(bar, rect) {
    const bh = bar.offsetHeight, bw = bar.offsetWidth;
    const navH = swNavH();
    let top = window.scrollY + rect.top - bh - 8;
    if (rect.top - bh - 8 < navH + 6) top = window.scrollY + rect.bottom + 8;
    let left = window.scrollX + rect.left;
    const maxLeft = window.scrollX + document.documentElement.clientWidth - bw - 8;
    if (left > maxLeft) left = Math.max(window.scrollX + 8, maxLeft);
    bar.style.top = top + 'px';
    bar.style.left = left + 'px';
}

function swHlShowForSelection() {
    if (swHlBar && swHlBar.classList.contains('hl-cancel-only')) return;   // 别把「取消高亮」条顶掉
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) { swHideHlToolbar(); return; }
    const r = sel.getRangeAt(0);
    if (swInAnno(r.startContainer) || swInAnno(r.endContainer)) { swHideHlToolbar(); return; }
    const sr = swMkSelInfo();
    if (sr.err) { swHideHlToolbar(); return; }
    swHideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar';
    bar.innerHTML = SW_HL_COLORS.map(c =>
        '<span class="hl-dot hl-dot-' + c + '" data-color="' + c + '" title="' + SW_HL_CN[c] + '高亮"></span>').join('') +
        '<span class="hl-anno-btn" title="为这一行写批注">📝批注</span>' +
        '<span class="hl-cancel" title="取消这处高亮">✕</span>';
    document.body.appendChild(bar);
    swHlBar = bar;
    swHlBarPlace(bar, swRectOf(r));
    bar.addEventListener('mousedown', e => e.preventDefault());   // 按住不丢选区
    bar.querySelectorAll('.hl-dot').forEach(dot =>
        dot.addEventListener('click', () => swHlApply(dot.dataset.color)));
    bar.querySelector('.hl-anno-btn').addEventListener('click', () => swAnnoOpenFrom(r));
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        swHlCancelAt(r.startContainer);
        swHideHlToolbar();
    });
}

/** 点已有高亮 → 只显示「✕ 取消高亮」 */
function swHlShowCancelFor(mk) {
    clearTimeout(swHlTimer);
    swHideHlToolbar();
    const bar = document.createElement('div');
    bar.className = 'hl-toolbar hl-cancel-only';
    bar.innerHTML = '<span class="hl-cancel" title="取消高亮">✕ 取消高亮</span>';
    document.body.appendChild(bar);
    swHlBar = bar;
    swHlBarPlace(bar, mk.getBoundingClientRect());
    bar.addEventListener('mousedown', e => e.preventDefault());
    bar.querySelector('.hl-cancel').addEventListener('click', () => {
        swHlRemoveMark(mk);
        swHideHlToolbar();
    });
}

function swHlBind() {
    document.addEventListener('mouseup', () => {
        clearTimeout(swHlTimer);
        swHlTimer = setTimeout(swHlShowForSelection, 0);
    });
    document.addEventListener('mousedown', e => {
        if (swHlBar && !swHlBar.contains(e.target)) swHideHlToolbar();
    });
    document.addEventListener('click', e => {
        if (swInAnno(e.target)) return;
        const mk = e.target.closest ? e.target.closest('mark.note-hl') : null;
        if (mk) { e.stopPropagation(); swHlShowCancelFor(mk); }
    });
    window.addEventListener('scroll', () => { if (swHlBar) swHideHlToolbar(); }, { passive: true });
}

/* ---------- 行批注（点 📝批注：在该行正下方开编辑框，自动保存） ---------- */

/** 批注框挂到"行级"元素之后（避免插进 flex 行/表格单元格里破坏布局） */
function swAnnoAnchor(block) {
    return block;
}

function swAnnoRender(i, block, text) {
    const box = document.createElement('div');
    box.className = 'wr-anno';
    box.dataset.anno = String(i);
    box.innerHTML = '<div class="wr-anno-head">📝 我的批注<span class="wr-anno-hint">自动保存</span></div>' +
        '<textarea class="wr-anno-input" rows="2" placeholder="写给这一行的批注…（留空即删除）"></textarea>' +
        '<div class="wr-anno-ops"><button type="button" class="wr-anno-del">删除批注</button></div>';
    const ta = box.querySelector('textarea');
    ta.value = text || '';
    let timer = null;
    const commit = () => {
        const v = ta.value.trim();
        if (v) swAnnos[i] = v; else delete swAnnos[i];
        swAnnoSave();
    };
    ta.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(commit, 600); });
    ta.addEventListener('blur', () => { clearTimeout(timer); commit(); });
    box.querySelector('.wr-anno-del').addEventListener('click', () => {
        delete swAnnos[i];
        swAnnoSave();
        box.remove();
    });
    swAnnoAnchor(block).insertAdjacentElement('afterend', box);
    return box;
}

function swAnnoOpenFrom(range) {
    const block = swMkBlockOf(range.startContainer);
    const sel = window.getSelection(); if (sel) sel.removeAllRanges();
    swHideHlToolbar();
    if (!block) return;
    const i = parseInt(block.getAttribute('data-mk'), 10);
    let box = document.querySelector('.wr-anno[data-anno="' + i + '"]');
    if (!box) box = swAnnoRender(i, block, swAnnos[i] || '');
    if (box.scrollIntoView) box.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    const ta = box.querySelector('textarea');
    if (ta) ta.focus();
}


function swNavH() {
    const n = document.querySelector('.navbar');
    if (n && n.dataset.collapsed === '1') return 0;   // 顶栏收起后吸顶条贴顶，不留白带
    return n ? n.getBoundingClientRect().height : 56;
}

/** 顶栏实测高度写进 --nav-h（吸顶的视图切换条用它做 top） */
function swNavHVar() {
    const h = swNavH();
    document.documentElement.style.setProperty('--nav-h', (h < 20 ? 56 : h) + 'px');
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', swInit);
else swInit();

