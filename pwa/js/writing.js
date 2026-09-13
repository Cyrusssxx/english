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

/* ==================== 批注高亮：点句点亮、localStorage 持久化 ==================== */
const WR_HL_KEY = 'wr_highlights_v1';

function wrHlGet() {
    try { return new Set(JSON.parse(localStorage.getItem(WR_HL_KEY) || '[]')); }
    catch (e) { return new Set(); }
}

function wrHlSave(set) {
    try { localStorage.setItem(WR_HL_KEY, JSON.stringify(Array.from(set))); } catch (e) { /* ignore */ }
    wrHlCount();
}

function wrHlCount() {
    const n = wrHlGet().size;
    const c = document.getElementById('wrHlCount');
    const b = document.getElementById('wrHlClear');
    if (c) c.textContent = n ? `已亮 ${n} 句` : '';
    if (b) b.hidden = !n;
}

/** 点击切换高亮：同 key 的英文行与中文行联动 */
function wrToggleHl(el) {
    const key = el.dataset.k;
    if (!key) return;
    const set = wrHlGet();
    const on = !set.has(key);
    if (on) set.add(key); else set.delete(key);
    document.querySelectorAll(`#wrContent [data-k]`).forEach(x => {
        if (x.dataset.k === key) x.classList.toggle('hl', on);
    });
    wrHlSave(set);
}

/** 渲染后按存储恢复高亮 */
function wrHlRestore() {
    const set = wrHlGet();
    document.querySelectorAll('#wrContent [data-k]').forEach(el => {
        if (set.has(el.dataset.k)) el.classList.add('hl');
    });
    wrHlCount();
}

async function wrClearHl() {
    if (wrHlGet().size === 0) return;
    if (typeof confirmAsync === 'function' && !(await confirmAsync('清除全部批注高亮？', { danger: true }))) return;
    try { localStorage.removeItem(WR_HL_KEY); } catch (e) { /* ignore */ }
    document.querySelectorAll('#wrContent .hl').forEach(el => el.classList.remove('hl'));
    wrHlCount();
}

/** 事件委托：点模板行 / 功能句切换高亮（点按钮不触发；点查词 span 不触发点亮） */
function wrHlBind() {
    const c = document.getElementById('wrContent');
    if (!c) return;
    c.addEventListener('click', e => {
        if (e.target.closest('button')) return;
        if (e.target.closest('.word')) return;   // 划词查词，不点亮
        const t = e.target.closest('.wr-line, .wr-sent, .wr-line-cn[data-k]');
        if (t) wrToggleHl(t);
    });
}

/* ==================== 划词查词：精翻页同款，词组优先 ==================== */
let wrVocabSet = new Set();

async function wrInitVocab() {
    try {
        const rows = await dbAll('vocab');
        wrVocabSet = new Set((rows || []).map(r => r.word));
    } catch (e) { /* IndexedDB 不可用时降级为空 */ }
}

/** 词组 token 匹配：精确相等或词形还原后相等（draws=draw） */
function wrTokEq(tok, candWord) {
    if (tok.low === candWord) return true;
    if (typeof stemCandidates !== 'function') return false;
    const cands = stemCandidates(candWord);
    if (cands.includes(tok.low)) return true;
    const lows = stemCandidates(tok.low);
    return cands.some(c => lows.includes(c)) || cands.includes(tok.low) || lows.includes(candWord);
}

/** 非占位符文本的词组优先标注：词组（真题词组表）→ 词组 span；其余每个单词 → 词 span（全部可点查） */
function wrAnnotatePlain(t) {
    if (!t) return '';
    if (typeof maxPhraseWords !== 'function' || maxPhraseWords() < 1 || typeof dictLookup !== 'function') {
        return wrEsc(t);   // 词典未加载/为空：纯文本
    }
    const TOK = /[A-Za-z][A-Za-z'\-]*/g;
    const toks = [];
    let m;
    while ((m = TOK.exec(t)) !== null) {
        toks.push({ s: m.index, e: m.index + m[0].length, low: m[0].toLowerCase(), raw: m[0] });
    }
    let out = '', last = 0, i = 0;
    while (i < toks.length) {
        let matched = null;
        const cands = phraseCandidates(toks[i].low);
        if (cands) {
            for (const c of cands) {                 // 候选已按 token 数降序 → 最长优先
                const n = c.tokens.length;
                if (i + n > toks.length) continue;
                let ok = true;
                for (let k = 1; k < n; k++) {
                    if (!wrTokEq(toks[i + k], c.tokens[k])) { ok = false; break; }
                    if (!/^[\s\-]*$/.test(t.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                }
                if (ok) { matched = c; break; }
            }
        }
        if (!matched) {                              // 首词未命中 → 词形还原后再试（draws out→draw out）
            for (const stem of stemCandidates(toks[i].low)) {
                const c2 = phraseCandidates(stem);
                if (!c2) continue;
                for (const c of c2) {
                    const n = c.tokens.length;
                    if (i + n > toks.length) continue;
                    let ok = true;
                    for (let k = 1; k < n; k++) {
                        if (!wrTokEq(toks[i + k], c.tokens[k])) { ok = false; break; }
                        if (!/^[\s\-]*$/.test(t.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                    }
                    if (ok) { matched = c; break; }
                }
                if (matched) break;
            }
        }
        if (matched) {
            const n = matched.tokens.length;
            const s0 = toks[i].s, e0 = toks[i + n - 1].e;
            out += wrEsc(t.slice(last, s0));
            out += `<span class="word phrase" data-w="${wrEsc(matched.key)}" data-ph="1">${wrEsc(t.slice(s0, e0))}</span>`;
            last = e0;
            i += n;
        } else {
            out += wrEsc(t.slice(last, toks[i].s));
            out += `<span class="word" data-w="${wrEsc(toks[i].low)}">${wrEsc(toks[i].raw)}</span>`;
            last = toks[i].e;
            i++;
        }
    }
    out += wrEsc(t.slice(last));
    return out;
}

/** 划词标注入口：先按 {{占位符}} 切段（占位符只高亮不可点），段内做词组优先标注 */
function wrAnnotate(text) {
    if (!text) return '';
    let out = '', last = 0;
    const re = /\{\{(.+?)\}\}/g;
    let m;
    while ((m = re.exec(text)) !== null) {
        out += wrAnnotatePlain(text.slice(last, m.index));
        out += `<span class="wr-ph">${wrEsc(m[1])}</span>`;
        last = m.index + m[0].length;
    }
    out += wrAnnotatePlain(text.slice(last));
    return out;
}

/* ---- 释义弹卡（精翻页 word-pop 同款样式，自备定位与开关） ---- */
let wrPopEl = null;

function wrCloseWordPop() {
    if (wrPopEl) { wrPopEl.remove(); wrPopEl = null; }
}

function wrOpenPop(targetEl, html) {
    wrCloseWordPop();
    wrPopEl = document.createElement('div');
    wrPopEl.className = 'word-pop wr-pop-c';
    wrPopEl.innerHTML = html;
    document.body.appendChild(wrPopEl);
    const r = targetEl.getBoundingClientRect();
    const pw = wrPopEl.offsetWidth, ph = wrPopEl.offsetHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    let top = r.bottom + window.scrollY + 6;
    if (top + ph > window.scrollY + document.documentElement.clientHeight - 12) {
        top = Math.max(window.scrollY + 6, r.top + window.scrollY - ph - 6);
    }
    wrPopEl.style.left = left + 'px';
    wrPopEl.style.top = top + 'px';
}

/** 点击词/词组：词组优先显示整组释义 + 组成词分释；单词显示词典释义；均可加入生词本 */
function wrWordPop(el) {
    const key = el.getAttribute('data-w') || '';
    const isPhrase = el.getAttribute('data-ph') === '1';
    let html = '';
    if (isPhrase) {
        const meaning = phraseLookup(key);
        if (!meaning) return;
        html += `<div class="wp-phrase">${wrEsc(key)}</div><div class="wp-meaning">${wrEsc(meaning)}</div>`;
        html += key.split(/\s+/).map(w => {
            const entry = dictLookup(w);
            return `<div class="wpw"><span class="wpw-word word" data-w="${wrEsc(normWord(w))}">${wrEsc(w)}</span>` +
                (entry ? `<span class="wpw-mean">${wrEsc(entry.t)}</span>` : `<span class="wpw-mean wpw-none">（离线无释义）</span>`) + `</div>`;
        }).join('');
    } else {
        const entry = dictLookup(key);
        html += `<span class="wp-word">${wrEsc(key)}</span><span class="wp-phonetic">${wrEsc(entry ? entry.p || '' : '')}</span>` +
            `<div class="wp-meaning">${entry ? wrEsc(entry.t) : '（无离线释义）'}</div>`;
    }
    const inV = wrVocabSet.has(key);
    html += `<button class="${inV ? 'added' : ''}" data-w="${wrEsc(key)}" onclick="wrAddVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`;
    wrOpenPop(el, html);
}

/** 加入/移出生词本（例句 = 当前模板句） */
async function wrAddVocab(btn) {
    const word = btn.getAttribute('data-w');
    if (!word) return;
    try {
        if (wrVocabSet.has(word)) {
            await dbDelete('vocab', word);
            wrVocabSet.delete(word);
            btn.textContent = '+ 加入生词本';
            btn.classList.remove('added');
        } else {
            const entry = dictLookup(word);
            const card = btn.closest('.word-pop');
            const exEn = card ? (card.getAttribute('data-ex') || '') : '';
            await addVocab(word, entry ? entry.t : '', entry ? entry.p : '', '', '', exEn, '', getVocabTarget());
            wrVocabSet.add(word);
            btn.textContent = '已加入 ✓';
            btn.classList.add('added');
        }
    } catch (e) { /* IndexedDB 不可用时静默 */ }
}

/** 全局委托：点词弹卡；点空白/其他区域关卡（卡内点击除外） */
function wrWordBind() {
    document.addEventListener('click', e => {
        const w = e.target.closest('.word');
        if (w && !e.target.closest('.wr-pop-c')) {
            e.stopPropagation();
            const line = w.closest('.wr-line, .wr-sent');
            wrWordPop(w);
            if (wrPopEl && line) wrPopEl.setAttribute('data-ex', line.textContent.replace(/\s+/g, ' ').trim());
            return;
        }
        if (!e.target.closest('.wr-pop-c')) wrCloseWordPop();
    }, true);   // 捕获阶段：先于 wrHlBind（冒泡）执行，stopPropagation 阻断点亮
}

/* ==================== ✨ 精句弹窗：本卡有用词组/短句（英中对照） ==================== */
function wrShowPhrases(secId) {
    const sec = (WR.sections || []).find(s => s.id === secId);
    if (!sec || !(sec.phrases || []).length) return;
    document.getElementById('wrPopTitle').textContent = (sec.title || '') + ' · 精句词组';
    document.getElementById('wrPopBody').innerHTML = sec.phrases.map(p =>
        `<div class="wr-pop-row"><div class="wr-pop-en">${wrAnnotate(p[0])}</div><div class="wr-pop-cn">${wrEsc(p[1])}</div></div>`).join('');
    document.getElementById('wrPopMask').hidden = false;
    document.getElementById('wrPop').hidden = false;
}

function wrClosePhrases() {
    document.getElementById('wrPopMask').hidden = true;
    document.getElementById('wrPop').hidden = true;
}

/* ==================== 结构染色开关 ==================== */
function wrToggleStruct() {
    localStorage.setItem(WR_STRUCT_KEY, wrStructOn() ? '0' : '1');
    wrRenderCards();
    wrTocSpy();
}

/** 重渲染模板卡（开关切换后调用），并恢复已点亮状态 */
function wrRenderCards() {
    if (!WR) return;
    const groups = {};
    for (const s of WR.sections || []) {
        (groups[s.group] || (groups[s.group] = [])).push(s);
    }
    document.getElementById('wrContent').innerHTML = Object.keys(groups).map((gname, gi) => `
        <h2 class="wr-h2" id="wrGroup${gi}">${wrEsc(gname)}</h2>
        ${groups[gname].map(wrSectionCard).join('')}`).join('');
    for (const id of ('wrStructState wrStructNavState').split(' ')) {
        const st = document.getElementById(id);
        if (st) st.textContent = wrStructOn() ? '开' : '关';
    }
    wrHlRestore();
}

/* ==================== 模板正文：按句拆行（英文行 + 对齐的中文行，共享 data-k） ==================== */
function wrSplitEn(t) {
    const m = (t || '').match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g) || [];
    return m.map(x => x.trim()).filter(Boolean);
}

function wrSplitCn(t) {
    const m = (t || '').match(/[^。！？]*[。！？]|[^。！？]+$/g) || [];
    return m.map(x => x.trim()).filter(Boolean);
}

/** 英文按句拆行；中文句数对齐时逐句配对（同 data-k 联动高亮），不齐则整段；
 *  struct = 每句的片段标注（[[text, role], ...]），开启「结构染色」时**划词式**染色（下划线着色，非色块） */
const WR_ROLE_CLS = { t: 'wr-subj', p: 'wr-pred', o: 'wr-obj', lead: 'wr-lead', trans: 'wr-trans', caus: 'wr-caus' };
const WR_STRUCT_KEY = 'wr_struct_on';

function wrStructOn() { return localStorage.getItem(WR_STRUCT_KEY) !== '0'; }

function wrSentenceHtml(s, struct) {
    if (wrStructOn() && struct && struct.length) {
        return struct.map(seg => {
            const cls = WR_ROLE_CLS[seg[1]] || '';
            const inner = wrAnnotate(seg[0]);
            return cls ? `<span class="${cls}">${inner}</span>` : inner;
        }).join('');
    }
    return wrAnnotate(s);
}

function wrTplBody(en, cn, struct) {
    const es = wrSplitEn(en);
    const cs = wrSplitCn(cn);
    const aligned = es.length > 0 && es.length === cs.length;
    const enHtml = es.map((s, i) =>
        `<div class="wr-line" data-k="${wrEsc(s)}" title="点击点亮/取消">${wrSentenceHtml(s, struct && struct[i])}</div>`).join('');
    const cnHtml = aligned
        ? cs.map((s, i) => `<div class="wr-line-cn" data-k="${wrEsc(es[i])}">${wrHl(s)}</div>`).join('')
        : `<div class="wr-line-cn">${wrHl(cn || '')}</div>`;
    return { enHtml, cnHtml };
}

/** 复制整段英文（行 div 的 textContent 无空格，需按行拼接） */
function wrCopyLines(btn) {
    const en = btn.closest('.wr-tpl').querySelector('.wr-en');
    const t = Array.from(en.querySelectorAll('.wr-line')).map(x => x.textContent).join(' ');
    wrCopy(btn, t);
}

function wrSectionCard(sec) {
    const sents = (sec.sentences || []).map((s, i) => `
        <li class="wr-sent" data-k="${wrEsc(s.en || '')}" title="点击点亮/取消">
            <div class="wr-sent-en"><span class="wr-sent-no">${i + 1}</span>${wrAnnotate(s.en)}</div>
            <div class="wr-sent-cn">${wrEsc(s.cn)}</div>
        </li>`).join('');

    const tips = (sec.tips || []).map(x => `<li>${wrEsc(x)}</li>`).join('');
    const body = wrTplBody(sec.en, sec.cn, sec.en_struct);
    const neg = sec.negative_en ? wrTplBody(sec.negative_en, sec.negative_cn, sec.negative_struct) : null;

    return `
    <section class="wr-card" id="${sec.id}">
        <div class="wr-card-head">
            <div class="wr-card-head-txt">
                <h3 class="wr-card-title">${wrEsc(sec.title)}</h3>
                ${sec.subtitle ? `<div class="wr-card-sub">${wrEsc(sec.subtitle)}</div>` : ''}
            </div>
            <button class="wr-copy" onclick="wrShowPhrases('${wrEsc(sec.id)}')" title="本段有用词组/短句（英中对照）">✨ 精句</button>
        </div>
        <div class="wr-tpl">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag">英文模板</span>
                <button class="wr-copy" onclick="wrCopyLines(this)">复制</button>
            </div>
            <div class="wr-en">${body.enHtml}</div>
            <div class="wr-cn">${body.cnHtml}</div>
        </div>
        ${neg ? `
        <div class="wr-tpl wr-tpl-neg">
            <div class="wr-tpl-bar">
                <span class="wr-tpl-tag wr-tag-neg">负面版（选一）</span>
                <button class="wr-copy" onclick="wrCopyLines(this)">复制</button>
            </div>
            <div class="wr-en">${neg.enHtml}</div>
            <div class="wr-cn">${neg.cnHtml}</div>
        </div>` : ''}
        ${sents ? `<div class="wr-sents"><div class="wr-sents-title">功能句挑选（自行选 2~4 句拼接，控制字数）</div><ol class="wr-sent-list">${sents}</ol></div>` : ''}
        ${sec.note ? `<div class="wr-note-inline">💡 ${wrHl(sec.note)}</div>` : ''}
        ${tips ? `<ul class="wr-tips">${tips}</ul>` : ''}
    </section>`;
}

/** 展开行的真题套用示范内容（示范文 + 建议 + 关键句型） */
function wrApplyHtml(year, ap) {
    const mk = (typeof APPLY_MARKS !== 'undefined' && APPLY_MARKS) ? APPLY_MARKS[year] : null;
    const bodyHtml = renderApplyBody(mk) || `<div class="apply-en">${wrEsc(ap.apply_en || '')}</div>`;
    const tips = (ap.tips || []).map(x => `<li>${wrEsc(x)}</li>`).join('');

    return `<div class="wr-apply-detail">
        <div class="wr-apply-title">${wrEsc(year)} 真题套用示范${ap.title ? ' · ' + wrEsc(ap.title) : ''}</div>
        <div class="apply-en">${bodyHtml}</div>
        ${ap.apply_cn ? `<div class="apply-cn">${renderApplyCn(mk, ap.apply_cn)}</div>` : ''}
        ${renderApplyMarks(mk)}
        ${tips ? `<div class="ap-sub">📝 套用建议</div><ul class="apply-tips">${tips}</ul>` : ''}
        ${renderSlotPhrases((mk && mk.slot_phrases) || ap.slot_phrases)}
        ${renderKeyPhrases((mk && mk.key_phrases) || ap.key_phrases)}
    </div>`;
}

/** 展开/收起某年份的套用示范 */
function wrToggleApply(i) {
    const row = document.getElementById('wrApplyRow' + i);
    if (!row) return;
    const btn = event && event.target;
    const show = row.hidden;
    row.hidden = !show;
    if (btn) btn.textContent = show ? '收起示范 ▴' : '展开示范 ▾';
}

/* ==================== 悬浮目录（左侧） ==================== */
const WR_TOC_KEY = 'wr_toc_fold';
const WR_TOC_NARROW = 1180;

function wrNavH() {
    const n = document.querySelector('.navbar');
    return n ? n.getBoundingClientRect().height : 56;
}

/** 收集目录条目：适配表 → 选句决策 → 各分区（一级）+ 各模板卡（二级） */
function wrTocItems() {
    const items = [];
    if (document.getElementById('wrGuideBlock')) items.push({ lv: 1, id: 'wrGuideBlock', text: '图表适配表' });
    if (document.getElementById('wrDecisionsTitle')) items.push({ lv: 2, id: 'wrDecisionsTitle', text: '选句决策' });
    document.querySelectorAll('#wrContent h2.wr-h2').forEach(h => {
        items.push({ lv: 1, id: h.id, text: h.textContent.trim() });
        let n = h.nextElementSibling;
        while (n && n.tagName === 'SECTION') {
            const t = n.querySelector('.wr-card-title');
            if (n.id && t) items.push({ lv: 2, id: n.id, text: t.textContent.trim() });
            n = n.nextElementSibling;
        }
    });
    return items;
}

function wrTocBuild() {
    const list = document.getElementById('wrTocList');
    if (!list) return;
    const items = wrTocItems();
    list.innerHTML = items.map(x =>
        `<a class="lv${x.lv}" href="#${wrEsc(x.id)}" data-target="${wrEsc(x.id)}">${wrEsc(x.text)}</a>`).join('');
    wrTocApplyFold(localStorage.getItem(WR_TOC_KEY) === '1' || window.innerWidth <= WR_TOC_NARROW);
    wrTocSpy();
}

/** 滚动高亮当前所在章节 */
function wrTocSpy() {
    const list = document.getElementById('wrTocList');
    if (!list || document.body.classList.contains('wr-toc-folded') && window.innerWidth > WR_TOC_NARROW) return;
    const links = Array.prototype.slice.call(list.querySelectorAll('a[data-target]'));
    const top = wrNavH() + 24;
    let cur = null;
    for (const a of links) {
        const el = document.getElementById(a.dataset.target);
        if (!el) continue;
        if (el.getBoundingClientRect().top <= top) cur = a; else break;
    }
    if (!cur) cur = links[0];
    links.forEach(a => a.classList.toggle('on', a === cur));
    if (cur && list.scrollHeight > list.clientHeight + 4) {
        const r = cur.getBoundingClientRect(), lr = list.getBoundingClientRect();
        if (r.top < lr.top || r.bottom > lr.bottom) list.scrollTop += r.top - lr.top - 24;
    }
}

function wrTocApplyFold(folded) {
    document.body.classList.toggle('wr-toc-folded', !!folded);
    try { localStorage.setItem(WR_TOC_KEY, folded ? '1' : '0'); } catch (e) { /* ignore */ }
    if (folded && !document.body.classList.contains('wr-toc-open')) wrTocClose();
}

function wrTocToggleFold() {
    wrTocApplyFold(!document.body.classList.contains('wr-toc-folded'));
}

function wrTocOpen() {
    if (window.innerWidth <= WR_TOC_NARROW) {
        document.body.classList.add('wr-toc-open');
        const m = document.getElementById('wrTocMask');
        if (m) m.hidden = false;
    } else {
        wrTocApplyFold(false);
    }
    wrTocSpy();
}

function wrTocClose() {
    document.body.classList.remove('wr-toc-open');
    const m = document.getElementById('wrTocMask');
    if (m) m.hidden = true;
}

function wrTocGo(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - wrNavH() - 12;
    window.scrollTo({ top: y < 0 ? 0 : y, behavior: 'smooth' });
    try { history.replaceState(null, '', '#' + id); } catch (e) { /* ignore */ }
    if (window.innerWidth <= WR_TOC_NARROW) wrTocClose();
}

function wrTocBind() {
    const list = document.getElementById('wrTocList');
    if (!list) return;
    list.addEventListener('click', e => {
        const a = e.target.closest && e.target.closest('a[data-target]');
        if (!a) return;
        e.preventDefault();
        wrTocGo(a.dataset.target);
    });
    window.addEventListener('scroll', wrTocSpy, { passive: true });
    window.addEventListener('resize', () => {
        if (window.innerWidth > WR_TOC_NARROW) wrTocClose();
    });
    document.addEventListener('keydown', e => {
        if (e.key !== 'Escape') return;
        if (!document.getElementById('wrPop').hidden) { wrClosePhrases(); return; }
        wrTocClose();
    });
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
    await Promise.all([loadDict(), loadPhrases()]);   // 离线词典 + 真题词组表（划词查词，词组优先）
    wrInitVocab();                                     // 生词本集合（弹卡按钮状态）
    // 真题套用示范（按年份汇总，可空）
    let APPLY = {};
    try {
        const ra = await fetch('data/writing_apply.json', { cache: 'no-cache' });
        if (ra.ok) APPLY = await ra.json();
    } catch (e) { APPLY = {}; }
    await loadApplyMarks();   // 套用示范的逐句标注
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
    let lastGroup = null;
    document.querySelector('#wrChartTable tbody').innerHTML = (g.table || []).map((row, i) => {
        const ap = APPLY[row.year];
        const cell = ap
            ? `<button class="wr-exp-btn" onclick="wrToggleApply(${i})">展开示范 ▾</button>`
            : `<span class="wr-t-hint">—</span>`;
        let head = '';
        if (row.group && row.group !== lastGroup) {
            lastGroup = row.group;
            head = `<tr class="wr-group-row"><td colspan="7">${wrEsc(row.group)}</td></tr>`;
        }
        return `${head}
        <tr>
            <td class="wr-t-year">${wrEsc(row.year)}</td>
            <td>${wrEsc(row.chart)}</td>
            <td class="wr-t-num">${row.items || '—'}</td>
            <td>${wrEsc(row.trend)}</td>
            <td><span class="wr-type ${row.type === '动态' ? 'wr-type-dyn' : (row.type === '静态' ? 'wr-type-sta' : '')}">${wrEsc(row.type) || '—'}</span></td>
            <td class="wr-t-hint">${wrEsc(row.hint)}</td>
            <td class="wr-t-apply">${cell}</td>
        </tr>
        ${ap ? `<tr class="wr-apply-row" id="wrApplyRow${i}" hidden><td colspan="7">${wrApplyHtml(row.year, ap)}</td></tr>` : ''}`;
    }).join('');
    document.getElementById('wrDecisions').innerHTML = (g.decisions || []).map(d => `
        <div class="wr-decision">
            <div class="wr-decision-k">${wrEsc(d.k)}</div>
            <div class="wr-decision-v">${wrEsc(d.v)}</div>
        </div>`).join('');

    // 模板分区（按 group 分组）
    wrRenderCards();

    wrHlRestore();
    wrTocBuild();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => { wrTocBind(); wrHlBind(); wrWordBind(); initWriting(); });
} else {
    wrTocBind();
    wrHlBind();
    wrWordBind();
    initWriting();
}
