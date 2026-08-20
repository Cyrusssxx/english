/* 轻量标注引擎：供「单词本 / 背单词」页的例句复用精翻界面的交互
 *   - 词典难词 / 真题词组 → 可点 <span class="word">，点击弹释义卡（含「加入/移出生词本」）
 *   - 例句中文 → 仿精翻界面的 .sent-cn：默认占位条，点击展开译文
 * 仅依赖 dict.js 全局函数：dictLookup / phraseLookup / isHard / stemCandidates /
 *   phraseCandidates / phraseTokenEq / normWord；以及 storage.js 的 addVocab /
 *   dbGet / dbDelete / getActiveDeck。与 article.js 互不干扰（不同页面加载）。
 */

let _litePop = null;   // 当前释义弹卡

/** 标注一段英文：词典命中词/词组包成可点 span，目标词额外加 .tgt 加粗。
 *  text: 英文文本；tgt: 可选，需加粗的目标词原词（如当前背的单词）。 */
function annotateLite(text, tgt) {
    if (!text) return '';
    const tgtN = tgt ? normWord(tgt) : '';
    const TOK = /[A-Za-z][A-Za-z'\-]*/g;
    const toks = [];
    let m;
    while ((m = TOK.exec(text)) !== null) {
        toks.push({ s: m.index, e: m.index + m[0].length, low: m[0].toLowerCase() });
    }
    let out = '', last = 0, i = 0;
    while (i < toks.length) {
        const cands = phraseCandidates(toks[i].low);
        let matched = null;
        if (cands) {
            for (const c of cands) {                 // 候选已按 token 数降序 → 最长优先
                const n = c.tokens.length;
                if (i + n > toks.length) continue;
                let ok = true;
                for (let k = 1; k < n; k++) {
                    if (!phraseTokenEq(toks[i + k], c.tokens[k])) { ok = false; break; }
                    if (!/^[\s\-]*$/.test(text.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                }
                if (ok) { matched = c; break; }
            }
        }
        if (matched) {
            const n = matched.tokens.length;
            const segStart = toks[i].s, segEnd = toks[i + n - 1].e;
            out += esc(text.slice(last, segStart));
            const isTgt = tgtN && normWord(matched.key) === tgtN;
            const hard = isHard(matched.key) ? ' hard' : '';
            const tgtCls = isTgt ? ' tgt' : '';
            out += `<span class="word phrase dict-hard${hard}${tgtCls}" data-w="${esc(matched.key)}" onclick="onLiteWordClick(event,this)">${esc(text.slice(segStart, segEnd))}</span>`;
            last = segEnd; i += n;
        } else {
            const tok = toks[i];
            const w = text.slice(tok.s, tok.e);
            if (dictLookup(w)) {
                const isTgt = tgtN && normWord(w) === tgtN;
                const hard = isHard(w) ? ' hard' : '';
                const tgtCls = isTgt ? ' tgt' : '';
                out += esc(text.slice(last, tok.s));
                out += `<span class="word dict-hard${hard}${tgtCls}" data-w="${esc(w)}" onclick="onLiteWordClick(event,this)">${esc(w)}</span>`;
            } else {
                out += esc(text.slice(last, tok.e));
            }
            last = tok.e; i++;
        }
    }
    out += esc(text.slice(last));
    return out;
}

/** 点击译文占位条：展开/收起中文（仿精翻 .sent-cn）。 */
function onLiteCnClick(e, el) {
    e.stopPropagation();
    closeLitePop();
    el.classList.toggle('open');
}

/** 点词：弹释义卡。 */
async function onLiteWordClick(e, el) {
    e.stopPropagation();
    const sel = getSelection();
    if (sel && !sel.isCollapsed) return;   // 划词时不弹
    const word = el.getAttribute('data-w');
    const inV = !!(await dbGet('vocab', word));
    openLitePop(el, word, inV);
}

/** 建卡 + 视口防溢出定位（逻辑与精翻界面 openPop 一致）。 */
function openLitePop(targetEl, word, inV) {
    closeLitePop();
    const entry = dictLookup(word);
    const phr = phraseLookup(word);
    const meaning = entry ? entry.t : (phr || '');
    const ph = entry ? entry.p : '';
    _litePop = document.createElement('div');
    _litePop.className = 'word-pop';
    _litePop.innerHTML = `
        <span class="wp-word">${esc(word)}</span><span class="wp-phonetic">${esc(ph || '')}</span>
        <div class="wp-meaning">${esc(meaning || '（无离线释义）')}</div>
        ${typeof freqBadge === 'function' ? freqBadge(word) : ''}
        ${inV
            ? `<button class="added" data-w="${esc(word)}" onclick="onLiteRemoveVocab(this)">移出生词本</button>`
            : `<button data-w="${esc(word)}" onclick="onLiteAddVocab(this)">+ 加入生词本</button>`}`;
    document.body.appendChild(_litePop);
    const r = targetEl.getBoundingClientRect();
    const pw = _litePop.offsetWidth, phh = _litePop.offsetHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    let top = r.bottom + window.scrollY + 6;
    if (top + phh > window.scrollY + document.documentElement.clientHeight - 12) {
        top = Math.max(window.scrollY + 6, r.top + window.scrollY - phh - 6);
    }
    _litePop.style.left = left + 'px';
    _litePop.style.top = top + 'px';
}

async function onLiteAddVocab(btn) {
    const word = btn.getAttribute('data-w');
    const entry = dictLookup(word);
    const phr = phraseLookup(word);
    const meaning = entry ? entry.t : (phr || '');
    const ph = entry ? entry.p : '';
    await addVocab(word, meaning, ph, '', '', '', '', getActiveDeck());
    btn.textContent = '已加入 ✓';
    btn.classList.add('added');
    btn.setAttribute('onclick', 'onLiteRemoveVocab(this)');
}

async function onLiteRemoveVocab(btn) {
    const word = btn.getAttribute('data-w');
    await dbDelete('vocab', word);
    btn.textContent = '+ 加入生词本';
    btn.classList.remove('added');
    btn.setAttribute('onclick', 'onLiteAddVocab(this)');
}

function closeLitePop() {
    if (_litePop) { _litePop.remove(); _litePop = null; }
}

// 点击面板外 / 非词处收起弹卡
document.addEventListener('click', (e) => {
    if (_litePop && !e.target.closest('.word-pop') && !e.target.closest('.word')) closeLitePop();
});
