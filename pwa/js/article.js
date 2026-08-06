/* 英语二精翻 - 精读页：逐句渲染 + 词组优先下划线 + 释义弹卡 + 句子收藏 + 做题面板 */

const AID = new URLSearchParams(location.search).get('id') || '';
let article = null;
let vocabSet = new Set();      // 已在生词本的词
let favSet = new Set();        // 已收藏句子
let answerMap = {};            // {question_id: {user_answer, is_correct}}
let popEl = null;              // 当前释义弹卡

// ============ 正文文章标题：默认隐藏（防剧透），点击标题处才显示 ============
function toggleReadTitle() {
    const t = document.querySelector('.read-title');
    if (!t) return;
    showReadTitle(t.hidden);
}

/** 显示/隐藏正文文章标题（force=true 展开，false 收起） */
function showReadTitle(show) {
    const t = document.querySelector('.read-title');
    const ph = document.querySelector('.read-title-placeholder');
    if (!t) return;
    t.hidden = !show;
    if (ph) ph.style.display = show ? 'none' : '';
}

/** 作文范文中英切换 */
function toggleWritingCn(btn) {
    const box = btn.closest('.writing-sample');
    const cn = box.querySelector('.writing-sample-cn');
    const show = cn.hidden;
    cn.hidden = !show;
    btn.textContent = show ? '隐藏中文译文' : '显示中文译文';
}

/** 作文储备板块折叠切换 */
function toggleReserve(btn) {
    const body = btn.closest('.writing-reserve-sec').querySelector('.writing-reserve-body');
    const collapsed = body.classList.toggle('collapsed');
    btn.textContent = collapsed ? '展开' : '收起';
}

/** 渲染作文储备板块（亮点词汇/必备表达/话题词汇等） */
function analysisHtml(r) {
    if (!r) return '';
    let html = '<div class="writing-analysis"><div class="rs-label">官方解析 · 审题与模板</div>';
    if (r.prompt) {
        html += reserveSec('解读要点', `<div class="reserve-text">${esc(r.prompt)}</div>`);
    }
    if (r.framework) {
        html += reserveSec('思路框架', `<div class="reserve-text">${esc(r.framework)}</div>`);
    }
    if (r.template) {
        html += reserveSec('应用模板', `<div class="reserve-text reserve-template">${esc(r.template)}</div>`);
    }
    html += '</div>';
    return html;
}

function reserveHtml(r) {
    if (!r || !Object.keys(r).length) return '';
    let html = '<div class="writing-reserve"><div class="rs-label">词汇储备</div>';
    if (r.highlights) {
        if (r.highlights.words && r.highlights.words.length) {
            html += reserveSec('亮点词汇', '<div class="reserve-grid">' + r.highlights.words.map(w =>
                `<span class="reserve-item"><span class="reserve-en">${esc(w[0])}</span><span class="reserve-cn">${esc(w[1])}</span></span>`).join('') + '</div>');
        }
        if (r.highlights.collocations && r.highlights.collocations.length) {
            html += reserveSec('必备搭配', '<div class="reserve-grid">' + r.highlights.collocations.map(w =>
                `<span class="reserve-item"><span class="reserve-en">${esc(w[0])}</span><span class="reserve-cn">${esc(w[1])}</span></span>`).join('') + '</div>');
        }
    }
    if (r.expressions && r.expressions.length) {
        html += reserveSec('必备表达', '<div class="reserve-grid">' + r.expressions.map(w =>
            `<span class="reserve-item"><span class="reserve-en">${esc(w[0])}</span><span class="reserve-cn">${esc(w[1])}</span></span>`).join('') + '</div>');
    }
    if (r.topic_notes) {
        html += reserveSec('话题表述补充', `<div class="reserve-text">${esc(r.topic_notes)}</div>`);
    }
    if (r.topic_vocab && r.topic_vocab.length) {
        html += reserveSec('话题词汇', '<div class="reserve-grid">' + r.topic_vocab.map(w =>
            `<span class="reserve-item"><span class="reserve-en">${esc(w[0])}</span><span class="reserve-cn">${esc(w[1])}</span></span>`).join('') + '</div>');
    }
    if (r.materials && r.materials.length) {
        html += reserveSec('写作素材积累', r.materials.map(m =>
            `<div class="reserve-material"><div class="reserve-en">${esc(m[0])}</div><div class="reserve-cn">${esc(m[1])}</div></div>`).join(''));
    }
    html += '</div>';
    return html;
}

/** 单个储备板块（带折叠标题栏） */
function reserveSec(title, inner) {
    return `<div class="writing-reserve-sec"><button class="writing-reserve-toggle" onclick="toggleReserve(this)">${title}<span class="reserve-caret">收起</span></button><div class="writing-reserve-body">${inner}</div></div>`;
}

// ============ 模式开关：精读 / 做题（存 localStorage） ============
function isQuizMode() {
    return localStorage.getItem('readMode') === 'quiz';
}

function renderModeSwitch() {
    const on = isQuizMode();
    document.body.classList.toggle('mode-read', !on);
    const btn = document.getElementById('modeSwitch');
    btn.classList.toggle('on', on);
    document.getElementById('modeState').textContent = on ? '开' : '关';
}

function toggleMode() {
    localStorage.setItem('readMode', isQuizMode() ? 'read' : 'quiz');
    renderModeSwitch();
}

// ============ 高亮难词开关（存 localStorage） ============
function isShowHard() {
    return localStorage.getItem('showHard') === '1';
}

function renderHardSwitch() {
    const on = isShowHard();
    document.body.classList.toggle('show-hard', on);
    const btn = document.getElementById('hardSwitch');
    if (btn) {
        btn.classList.toggle('on', on);
        document.getElementById('hardState').textContent = on ? '开' : '关';
    }
}

function toggleHard() {
    localStorage.setItem('showHard', isShowHard() ? '0' : '1');
    renderHardSwitch();
}

// ============ 题目面板收缩（存 localStorage） ============
function isQuizCollapsed() {
    return localStorage.getItem('quizCollapsed') === '1';
}

function renderQuizCollapse() {
    document.body.classList.toggle('quiz-collapsed', isQuizCollapsed());
}

function toggleQuizPane() {
    localStorage.setItem('quizCollapsed', isQuizCollapsed() ? '0' : '1');
    renderQuizCollapse();
}

// ============ 全文翻译开关（仅本页会话，不持久化） ============
let cnAll = false;

function toggleCnAll() {
    cnAll = !cnAll;
    const btn = document.getElementById('cnAllSwitch');
    btn.classList.toggle('on', cnAll);
    document.getElementById('cnAllState').textContent = cnAll ? '开' : '关';
    document.querySelectorAll('.sent-cn').forEach(el => el.classList.toggle('open', cnAll));
    // 同步控制题目区（题干/选项）译文显示
    document.body.classList.toggle('show-quiz-cn', cnAll);
    // 展开全部译文时自动显示标题
    if (cnAll) showReadTitle(true);
}

// ============ 初始化 ============
async function init() {
    if (!AID) {
        document.getElementById('readPane').innerHTML = '<div class="error">缺少文章参数</div>';
        return;
    }
    try {
        article = await getArticle(AID);
    } catch (e) {
        document.getElementById('readPane').innerHTML =
            `<div class="error">加载失败: ${esc(e.message)}<br>请用 start.bat 启动后访问 http://localhost:8410</div>`;
        return;
    }
    if (!article) {
        document.getElementById('readPane').innerHTML = '<div class="error">文章不存在</div>';
        return;
    }
    const year = AID.slice(0, 4);
    document.title = `${year} ${TYPE_NAMES[article.type] || article.type} - 英语二精翻`;
    document.getElementById('navTitle').textContent = `${year} ${TYPE_NAMES[article.type] || article.type}`;
    localStorage.setItem('lastArticle', AID);

    // 用户数据
    await migrateVocabDecks();
    vocabSet = new Set((await dbAll('vocab')).map(v => v.word));
    favSet = new Set((await dbAll('fav_sentences')).map(f => f.sentence_id));
    for (const a of await dbAll('quiz_answers')) if (a.article_id === AID) answerMap[a.question_id] = a;

    // 离线词典：失败静默降级为仅预标注词可点
    await loadDict();
    // 词组词典：失败静默降级为无词组高亮
    await loadPhrases();
    // 真题考频：失败静默降级为不显示徽标
    if (typeof loadFreq === 'function') { try { await loadFreq(); } catch (e) { /* 徽标降级 */ } }
    // 精选难词集合：失败静默降级为不额外高亮
    if (typeof loadHardwords === 'function') { try { await loadHardwords(); } catch (e) { /* 精选降级 */ } }

    renderModeSwitch();
    renderHardSwitch();
    renderQuizCollapse();
    renderArticle();
    if (window.Annot) Annot.apply(AID);
    renderQuiz();
    await restoreScroll();
    watchScroll();
}

// ============ 正文渲染 ============
function renderArticle() {
    // 作文模块：无逐句正文，渲染范文（中英对照可切换）
    if (article.type === 'writing_a' || article.type === 'writing_b') {
        document.getElementById('readPane').innerHTML = `
            <div class="read-title" onclick="toggleReadTitle()" title="点击显示/隐藏文章标题" hidden>${esc(article.title || '')}</div>
            <div class="read-title-placeholder" onclick="toggleReadTitle()" title="点击显示文章标题">…</div>
            <div class="read-source">${esc(article.source || '')} · 写作练习：先自行构思，再对照官方范文</div>
            ${article.directions ? `<div class="writing-directions"><span class="rs-label">题目要求</span><div class="writing-directions-text">${esc(article.directions)}</div></div>` : ''}
            ${article.chart_img ? `<div class="writing-chart"><img src="${esc(article.chart_img)}" alt="图表" loading="lazy"></div>` : ''}
            <div class="writing-sample">
                <div class="rs-label">参考范文</div>
                <button class="writing-toggle" onclick="toggleWritingCn(this)">显示中文译文</button>
                <div class="writing-sample-en">${esc(article.sample_en || '')}</div>
                <div class="writing-sample-cn" hidden>${esc(article.sample_cn || '')}</div>
            </div>
            ${analysisHtml(article.writing_analysis)}
            ${reserveHtml(article.reserve)}`;
        return;
    }
    // 翻译模块：正文下方提供官方全文译文（可展开）
    if (article.type === 'translation') {
        document.getElementById('readPane').innerHTML = `
            <div class="read-title" onclick="toggleReadTitle()" title="点击显示/隐藏文章标题" hidden>${esc(article.title || '')}</div>
            <div class="read-title-placeholder" onclick="toggleReadTitle()" title="点击显示文章标题">…</div>
            <div class="read-source">${esc(article.source || '')} · 点句下占位条显示译文，点下划线词查释义</div>
            ${article.topic ? `<div class="read-summary"><span class="rs-label">本文概要</span>${esc(article.topic)}</div>` : ''}
            <div class="para"><div class="para-tag">P1</div>${article.sentences.map(s => sentenceHtml(s)).join('')}</div>
            ${article.ref_cn ? `<div class="translation-ref">
                <button class="writing-toggle" onclick="toggleWritingCn(this)">显示全文参考译文</button>
                <div class="translation-ref-cn" hidden>${esc(article.ref_cn)}</div>
            </div>` : ''}`;
        return;
    }
    const paras = [];   // [[sent,...], ...] 按 para 分组（缺省视为一段）
    for (const s of article.sentences) {
        const p = (s.para || 1) - 1;
        (paras[p] || (paras[p] = [])).push(s);
    }
    let html = `<div class="read-title" onclick="toggleReadTitle()" title="点击显示/隐藏文章标题" hidden>${esc(article.title || '')}</div>`;
    html += `<div class="read-title-placeholder" onclick="toggleReadTitle()" title="点击显示文章标题">…</div>`;
    html += `<div class="read-source">${esc(article.source || '')} · 点句下占位条显示译文，点下划线词查释义</div>`;
    if (article.topic) {
        html += `<div class="read-summary"><span class="rs-label">本文概要</span>${esc(article.topic)}</div>`;
    }
    paras.forEach((sents, i) => {
        html += `<div class="para"><div class="para-tag">P${i + 1}</div>`;
        for (const s of sents) html += sentenceHtml(s);
        html += '</div>';
    });
    document.getElementById('readPane').innerHTML = html;
}

function sentenceHtml(s) {
    const { html: enHtml, missed } = annotate(s);
    const favOn = favSet.has(s.id);
    let out = `<div class="sent" id="s-${s.id}" data-sid="${s.id}">
        <div class="sent-en">${enHtml}
            <button class="fav-btn ${favOn ? 'on' : ''}" onclick="onFav(event,'${s.id}')" title="收藏句子">${favOn ? '★' : '☆'}</button>
        </div>
        <div class="sent-cn" onclick="onCnClick(event,'${s.id}')">
            <span class="cn-placeholder">▾ 点击查看翻译</span>
            <span class="cn-text">${esc(s.cn || '')}</span>
        </div>`;
    // 匹配失败降级：句尾词汇列表
    if (missed.length) {
        out += `<div class="sent-words-fallback">${missed.map(w =>
            `<span class="word" onclick="onWordClick(event,'${s.id}',${w._i})">${esc(w.w)}</span> ${esc(w.meaning)}`).join('　')}</div>`;
    }
    return out + '</div>';
}

/** 词汇下划线标注：按 w 长度降序匹配（词组优先于单词命中），全词边界，首次出现 */
function annotate(s) {
    const words = (s.words || []).map((w, i) => ({ ...w, _i: i }));
    words.sort((a, b) => b.w.length - a.w.length);
    // 分段结构：{text} 为纯文本段，{text, wi} 为已命中的预标注词段，{text, dictFallback, word} 为词典兜底段
    let segs = [{ text: s.en }];
    const missed = [];
    for (const w of words) {
        let hit = false;
        for (let i = 0; i < segs.length; i++) {
            const seg = segs[i];
            if (seg.wi !== undefined || seg.dictFallback) continue;
            const pos = findWord(seg.text, w.w);
            if (pos < 0) continue;
            const before = seg.text.slice(0, pos);
            const after = seg.text.slice(pos + w.w.length);
            const mid = { text: seg.text.slice(pos, pos + w.w.length), wi: w._i };
            const repl = [];
            if (before) repl.push({ text: before });
            repl.push(mid);
            if (after) repl.push({ text: after });
            segs.splice(i, 1, ...repl);
            hit = true;
            break;
        }
        if (!hit) missed.push(w);
    }
    // 🔑 兜底：missed 词中词典命中的，在纯文本段中标为可点（dictFallback），并从 missed 移除
    for (const w of missed) {
        if (!dictLookup(w.w)) continue;
        for (let i = 0; i < segs.length; i++) {
            const seg = segs[i];
            if (seg.wi !== undefined || seg.dictFallback) continue;
            const pos = findWord(seg.text, w.w);
            if (pos < 0) continue;
            const before = seg.text.slice(0, pos);
            const after = seg.text.slice(pos + w.w.length);
            const mid = { text: seg.text.slice(pos, pos + w.w.length), dictFallback: true, word: w };
            const repl = [];
            if (before) repl.push({ text: before });
            repl.push(mid);
            if (after) repl.push({ text: after });
            segs.splice(i, 1, ...repl);
            missed.splice(missed.indexOf(w), 1);
            break;
        }
    }
    const html = segs.map(seg => {
        if (seg.wi !== undefined) {
            const w = s.words[seg.wi];
            const hard = isHard(w.w) ? ' hard' : '';
            return `<span class="word${hard}" data-w="${esc(w.w)}" onclick="onWordClick(event,'${s.id}',${seg.wi})">${esc(seg.text)}</span>`;
        }
        if (seg.dictFallback) {
            const w = seg.word;
            const hard = isHard(w.w) ? ' hard' : '';
            return `<span class="word dict-hard${hard}" data-w="${esc(w.w)}" onclick="onDictWordClick(event,'${s.id}')">${esc(seg.text)}</span>`;
        }
        // 纯文本段：先试词组扫描，其余回落难词/空格/转义
        return annotatePhrases(seg.text, s.id);
    }).join('');
    return { html, missed };
}

/** 纯文本段渲染：词典命中的难词→可点 span；完形空格 [n]→blank；其余转义 */
function annotatePlain(text, sid) {
    const RE = /\[(\d+)\]|[A-Za-z][A-Za-z'\-]*/g;
    let out = '', last = 0, m;
    while ((m = RE.exec(text)) !== null) {
        out += esc(text.slice(last, m.index));
        if (m[1] !== undefined) {
            out += `<span class="blank" id="blank-${m[1]}" onclick="onBlankClick(event,${m[1]})">[${m[1]}]</span>`;
        } else {
            const tok = m[0];
            // 词典命中→可点难词（有离线释义）；未命中即简单词→纯文本、不可点
            if (dictLookup(tok)) {
                const hard = isHard(tok) ? ' hard' : '';
                out += `<span class="word dict-hard${hard}" data-w="${esc(tok)}" onclick="onDictWordClick(event,'${sid}')">${esc(tok)}</span>`;
            } else {
                out += esc(tok);
            }
        }
        last = m.index + m[0].length;
    }
    out += esc(text.slice(last));
    return out;
}

/** 词组扫描：左→右逐 token，首词查 _phraseIndex 最长优先匹配连续词组；
    命中区间包成可点 span，命中前/剩余文本回落 annotatePlain。与人工预标注、单词天然无重叠。 */
function annotatePhrases(text, sid) {
    if (maxPhraseWords() < 2) return annotatePlain(text, sid);   // 词典未加载/为空时直接回落
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
            for (const c of cands) {                 // 候选已按 token 数降序→最长优先
                const n = c.tokens.length;
                if (i + n > toks.length) continue;
                let ok = true;
                for (let k = 1; k < n; k++) {
                    if (toks[i + k].low !== c.tokens[k]) { ok = false; break; }
                    // 两 token 之间只允许空白/连字符，否则不是连续词组
                    if (!/^[\s\-]*$/.test(text.slice(toks[i + k - 1].e, toks[i + k].s))) { ok = false; break; }
                }
                if (ok) { matched = c; break; }
            }
        }
        if (matched) {
            const n = matched.tokens.length;
            const segStart = toks[i].s, segEnd = toks[i + n - 1].e;
            out += annotatePlain(text.slice(last, segStart), sid);
            const hard = isHard(matched.key) ? ' hard' : '';
            out += `<span class="word phrase dict-hard${hard}" data-w="${esc(matched.key)}" onclick="onPhraseClick(event,'${sid}')">${esc(text.slice(segStart, segEnd))}</span>`;
            last = segEnd;
            i += n;
        } else {
            i++;
        }
    }
    out += annotatePlain(text.slice(last), sid);
    return out;
}

/** 全词匹配（大小写不敏感，前后均非字母才算命中），返回位置或 -1 */
function findWord(text, w) {
    const lowerText = text.toLowerCase();
    const lowerW = w.toLowerCase();
    let from = 0;
    while (true) {
        const pos = lowerText.indexOf(lowerW, from);
        if (pos < 0) return -1;
        const b = pos === 0 ? '' : text[pos - 1];
        const a = pos + w.length >= text.length ? '' : text[pos + w.length];
        if (!/[A-Za-z]/.test(b) && !/[A-Za-z]/.test(a)) return pos;
        from = pos + 1;
    }
}

// ============ 句子交互 ============
/** 点占位条展开译文，再点译文收回占位条 */
function onCnClick(e, sid) {
    closePop();
    const cn = document.querySelector(`#s-${CSS.escape(sid)} .sent-cn`);
    if (cn) cn.classList.toggle('open');
}

async function onFav(e, sid) {
    e.stopPropagation();
    const sent = article.sentences.find(x => x.id === sid);
    if (!sent) return;
    const on = await toggleFavSentence(sent, AID);
    if (on) favSet.add(sid); else favSet.delete(sid);
    const btn = e.target;
    btn.classList.toggle('on', on);
    btn.textContent = on ? '★' : '☆';
}

// ============ 释义弹卡 ============
/** 建卡 + 视口右/下缘防溢出定位（正文与题目词共用） */
function openPop(targetEl, innerHtml) {
    closePop();
    popEl = document.createElement('div');
    popEl.className = 'word-pop';
    popEl.innerHTML = innerHtml;
    document.body.appendChild(popEl);
    const r = targetEl.getBoundingClientRect();
    const pw = popEl.offsetWidth;
    const ph = popEl.offsetHeight;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    // 默认在词下方；若溢出视口底部则翻到词上方
    let top = r.bottom + window.scrollY + 6;
    if (top + ph > window.scrollY + document.documentElement.clientHeight - 12) {
        top = Math.max(window.scrollY + 6, r.top + window.scrollY - ph - 6);
    }
    popEl.style.left = left + 'px';
    popEl.style.top = top + 'px';
}

/** 预标注词：手写释义优先（wi>=0 原路径） */
function onWordClick(e, sid, wi) {
    e.stopPropagation();
    const _sel = getSelection(); if (_sel && !_sel.isCollapsed) return;  // 划词标注时不弹词卡
    const sent = article.sentences.find(x => x.id === sid);
    const w = sent && sent.words[wi];
    if (!w) return;
    const inV = vocabSet.has(w.w);
    openPop(e.target, `
        <span class="wp-word">${esc(w.w)}</span><span class="wp-phonetic">${esc(w.phonetic || '')}</span>
        <div class="wp-meaning">${esc(w.meaning || '')}</div>
        ${typeof freqBadge === 'function' ? freqBadge(w.w) : ''}
        <button class="${inV ? 'added' : ''}" onclick="onAddVocab(this,'${sid}',${wi})">${inV ? '移出生词本' : '+ 加入生词本'}</button>`);
}

/** 词典难词：未预标注词，词形取自 data-w，释义走 dictLookup（未命中显「无离线释义」，仍可加入生词本） */
function onDictWordClick(e, sid) {
    e.stopPropagation();
    const _sel = getSelection(); if (_sel && !_sel.isCollapsed) return;  // 划词标注时不弹词卡
    const el = e.currentTarget;
    const word = el.getAttribute('data-w');
    const entry = dictLookup(word);
    const inV = vocabSet.has(word);
    openPop(el, `
        <span class="wp-word">${esc(word)}</span><span class="wp-phonetic">${esc(entry ? entry.p || '' : '')}</span>
        <div class="wp-meaning">${entry ? esc(entry.t || '') : '（无离线释义）'}</div>
        ${typeof freqBadge === 'function' ? freqBadge(word) : ''}
        <button class="${inV ? 'added' : ''}" data-w="${esc(word)}" data-sid="${esc(sid)}" onclick="onAddDictVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`);
}

async function onAddVocab(btn, sid, wi) {
    const sent = article.sentences.find(x => x.id === sid);
    const w = sent.words[wi];
    if (vocabSet.has(w.w)) {
        await dbDelete('vocab', w.w);
        vocabSet.delete(w.w);
        btn.textContent = '+ 加入生词本';
        btn.classList.remove('added');
    } else {
        await addVocab(w.w, w.meaning, w.phonetic, sid, AID, sent.en, sent.cn);
        vocabSet.add(w.w);
        btn.textContent = '已加入 ✓';
        btn.classList.add('added');
    }
}

/** 词典难词加入/移出生词本（词形与释义来自 data-* + dictLookup，例句按 sid 作用域解析） */
async function onAddDictVocab(btn) {
    const word = btn.getAttribute('data-w');
    const sid = btn.getAttribute('data-sid');
    const entry = dictLookup(word);
    const ex = resolveExample(sid);
    if (vocabSet.has(word)) {
        await dbDelete('vocab', word);
        vocabSet.delete(word);
        btn.textContent = '+ 加入生词本';
        btn.classList.remove('added');
    } else {
        await addVocab(word, entry ? entry.t : '', entry ? entry.p : '', sid, AID, ex.en, ex.cn);
        vocabSet.add(word);
        btn.textContent = '已加入 ✓';
        btn.classList.add('added');
    }
}

/** 词组下划线点击：phraseLookup 取释义 → 弹卡（含加入生词本） */
function onPhraseClick(e, sid) {
    e.stopPropagation();
    const _sel = getSelection(); if (_sel && !_sel.isCollapsed) return;  // 划词标注时不弹词卡
    const el = e.currentTarget;
    const key = el.getAttribute('data-w');
    const meaning = phraseLookup(key);
    if (!meaning) return;
    const inV = vocabSet.has(key);
    openPop(el, `
        <span class="wp-word">${esc(key)}</span>
        <div class="wp-meaning">${esc(meaning)}</div>
        ${typeof freqBadge === 'function' ? freqBadge(key) : ''}
        <button class="${inV ? 'added' : ''}" data-w="${esc(key)}" data-sid="${esc(sid)}" onclick="onAddPhraseVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`);
}

/** 词组加入/移出生词本（word=词组 key，meaning=phraseLookup，例句按 sid 作用域解析） */
async function onAddPhraseVocab(btn) {
    const key = btn.getAttribute('data-w');
    const sid = btn.getAttribute('data-sid');
    const meaning = phraseLookup(key) || '';
    const ex = resolveExample(sid);
    if (vocabSet.has(key)) {
        await dbDelete('vocab', key);
        vocabSet.delete(key);
        btn.textContent = '+ 加入生词本';
        btn.classList.remove('added');
    } else {
        await addVocab(key, meaning, '', sid, AID, ex.en, ex.cn);
        vocabSet.add(key);
        btn.textContent = '已加入 ✓';
        btn.classList.add('added');
    }
}

/** 一键记录：本篇词典命中且尚未收录的「精选难词」→ 批量加入当前词书
 *  （词典 v26 扩到 8525 词后含大量简单词，故按 hardwords 精选集合过滤；
 *    精选集合未加载成功时回退为旧逻辑——词典命中即记录，避免降级为空）。 */
async function recordArticleWords() {
    const seen = new Set();
    const items = [];
    const useHard = typeof isHard === 'function' && typeof isHardLoaded === 'function' && isHardLoaded();
    for (const s of article.sentences) {
        const RE = /[A-Za-z][A-Za-z'\-]*/g;
        let m;
        while ((m = RE.exec(s.en || '')) !== null) {
            const tok = m[0];
            const entry = dictLookup(tok);
            if (!entry) continue;
            if (useHard && !isHard(tok)) continue;   // 只收精选难词
            const base = normWord(tok);
            if (!base || seen.has(base)) continue;
            seen.add(base);
            if (vocabSet.has(tok) || vocabSet.has(base)) continue;
            items.push({
                word: tok, meaning: entry.t || '', phonetic: entry.p || '',
                sentence_id: s.id, article_id: AID, example_en: s.en, example_cn: s.cn || ''
            });
        }
    }
    if (!items.length) { alert('本篇没有可新增的难词（可能都已在生词本）'); return; }
    const dname = deckName(getActiveDeck());
    if (!confirm(`将本篇 ${items.length} 个较难词加入「${dname}」？`)) return;
    const added = await addWordsBulk(items, getActiveDeck());
    vocabSet = new Set((await dbAll('vocab')).map(v => v.word));
    alert(`已加入「${dname}」${added} 个词`);
}

function closePop() {
    if (popEl) { popEl.remove(); popEl = null; }
}

/** 中文查询：遍历释义含该中文的英文词/词组并弹卡列表；点击某条 → 转去查对应英文词。 */
let cnHits = [];   // 最近一次中文反查结果，供内联点击取词
function navCnLookup(q) {
    const inp = document.getElementById('navSearch');
    cnHits = (typeof cnLookup === 'function') ? cnLookup(q, 10) : [];
    if (!cnHits.length) {
        openPop(inp, `<span class="wp-word">${esc(q)}</span>
            <div class="wp-meaning">词典与词组库均未收录这个中文释义</div>`);
        return;
    }
    const rows = cnHits.map((h, i) =>
        `<div class="cn-row" onclick="cnPick(${i})"><b>${esc(h.isPhrase ? '<词组> ' : '')}${esc(h.en)}</b>
            <span class="cn-mean">${esc(h.meaning)}</span></div>`).join('');
    openPop(inp, `
        <span class="wp-word">「${esc(q)}」相关</span>
        <div class="cn-list">${rows}<div class="cn-tip">点击上方词条查看详情并可加入生词本</div></div>`);
    inp.select();
}

/** 中文反查结果点击：跳转去查对应英文词/词组详情。 */
function cnPick(i) {
    const h = cnHits[i];
    if (!h) return;
    const inp = document.getElementById('navSearch');
    closePop();
    navLookupWith(h.en);
}

/** 实际执行查词（供回车 / 历史 / 中文结果点击共用），并把查询写入历史。 */
function navLookupWith(q) {
    const inp = document.getElementById('navSearch');
    if (!inp) return;
    inp.value = q;
    if (q) pushSearchHist(q);
    if (/[\u4e00-\u9fff]/.test(q)) { navCnLookup(q); return; }   // 含中文 → 反查
    const entry = dictLookup(q);
    const phr = phraseLookup(q);
    if (!entry && !phr) {
        openPop(inp, `
            <span class="wp-word">${esc(q)}</span>
            <div class="wp-meaning">词典与词组库均未收录</div>`);
        return;
    }
    const word = phr || q;   // 词组命中用词组 key，否则用原文
    const inV = vocabSet.has(word);
    const btn = phr
        ? `<button class="${inV ? 'added' : ''}" data-w="${esc(word)}" data-sid="" onclick="onAddPhraseVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`
        : `<button class="${inV ? 'added' : ''}" data-w="${esc(word)}" data-sid="" onclick="onAddDictVocab(this)">${inV ? '移出生词本' : '+ 加入生词本'}</button>`;
    openPop(inp, `
        <span class="wp-word">${esc(word)}</span><span class="wp-phonetic">${esc(entry ? entry.p || '' : '')}</span>
        <div class="wp-meaning">${esc(entry ? entry.t || '' : phr)}</div>
        ${typeof freqBadge === 'function' ? freqBadge(word) : ''}
        ${btn}`);
    inp.select();
}

function navLookup() {
    const q = (document.getElementById('navSearch').value || '').trim();
    if (!q) return;
    navLookupWith(q);
}

/* ---- 查询历史（localStorage 持久化，最近优先，去重，上限 12 条） ---- */
function getSearchHist() {
    try { return JSON.parse(localStorage.getItem('en2_hist') || '[]'); }
    catch (e) { return []; }
}
function setSearchHist(h) { localStorage.setItem('en2_hist', JSON.stringify(h.slice(0, 12))); }
function pushSearchHist(q) {
    const h = getSearchHist().filter(x => x !== q);
    h.unshift(q);
    setSearchHist(h);
}
function showSearchHist() {
    const box = document.getElementById('navSearchHist');
    if (!box || !getSearchHist().length) return;
    box.innerHTML = getSearchHist().map(q =>
        `<div class="hist-item" data-q="${esc(q)}" onclick="histPick(this)">${esc(q)}</div>`).join('')
        + `<div class="hist-clear" onclick="clearSearchHist()">清空历史</div>`;
    box.hidden = false;
}
function hideSearchHist() {
    const box = document.getElementById('navSearchHist');
    if (box) box.hidden = true;
}
function histPick(el) { const q = el.getAttribute('data-q'); hideSearchHist(); navLookupWith(q); }
function clearSearchHist() { setSearchHist([]); hideSearchHist(); }

/** 解析例句作用域：sid 可能是句子 id（正文词）或题目 id（题目词）。
 *  句子直接取；题目取 related_sentences 首句，无则用题干/选项文本兜底。 */
function resolveExample(sid) {
    const sent = article.sentences.find(x => x.id === sid);
    if (sent) return { en: sent.en || '', cn: sent.cn || '' };
    const q = (article.questions || []).find(x => x.id === sid);
    if (q) {
        for (const rs of q.related_sentences || []) {
            const rsSent = article.sentences.find(x => x.id === rs);
            if (rsSent) return { en: rsSent.en || '', cn: rsSent.cn || '' };
        }
        return { en: q.stem || '', cn: q.stem_cn || '' };
    }
    return { en: '', cn: '' };
}

document.addEventListener('click', (e) => {
    if (popEl && !e.target.closest('.word-pop') && !e.target.closest('.word')) closePop();
});

// ============ 做题面板 ============
// 翻译/作文等无客观题模块：整块做题面板隐藏（题目区无意义）
const NO_QUIZ_TYPES = ['translation', 'writing_a', 'writing_b'];

function renderQuiz() {
    if (NO_QUIZ_TYPES.includes(article.type)) {
        const qp = document.getElementById('quizPane');
        if (qp) qp.style.display = 'none';
        document.querySelector('.quiz-expand-tab') && (document.querySelector('.quiz-expand-tab').style.display = 'none');
        document.body.classList.remove('quiz-collapsed');
        return;
    }
    const qs = article.questions || [];
    const scroll = document.getElementById('quizScroll');
    if (!qs.length) {
        scroll.innerHTML = '<div class="empty">本篇暂无题目</div>';
        return;
    }
    let html = '';
    for (const q of qs) html += questionHtml(q);
    scroll.innerHTML = html;
    document.getElementById('quizJumpbar').innerHTML = qs.map(q => {
        const a = answerMap[q.id];
        const cls = a ? (a.is_correct ? 'answered-right' : 'answered-wrong') : '';
        return `<button class="qj-btn ${cls}" id="qj-${q.id}" onclick="jumpQ('${q.id}')">Q${q.number}</button>`;
    }).join('');
    // 恢复历史作答显示
    for (const q of qs) if (answerMap[q.id]) showResult(q, answerMap[q.id].user_answer, false);
}

/** 清除本篇全部作答记录并复位面板 */
async function resetQuiz() {
    const qs = article.questions || [];
    if (!qs.length) return;
    if (!confirm('清除本篇全部作答记录？')) return;
    await clearAnswers(AID);
    answerMap = {};
    // 完形题：blank 文本已填入正文，需整篇重绘还原为 [n] 占位
    if (article.type === 'cloze') { renderArticle(); if (window.Annot) Annot.apply(AID); }
    renderQuiz();
}

function questionHtml(q) {
    const opts = (q.options && Object.keys(q.options).length) ? q.options : (article.pool || {});
    const optsCn = (q.options_cn && Object.keys(q.options_cn).length) ? q.options_cn : (article.pool_cn || {});
    return `<div class="qblock" id="q-${q.id}">
        <div class="q-head"><span class="q-no">Q${q.number}</span>${q.qtype ? `<span class="q-type-badge">${esc(q.qtype)}</span>` : ''}</div>
        <div class="q-stem">${quizTextHtml(q.stem || '', q.id)}</div>
        ${q.stem_cn ? `<div class="q-stem-cn">${esc(q.stem_cn)}</div>` : ''}
        ${Object.keys(opts).map(k => `
        <div class="q-opt" id="opt-${q.id}-${k}" onclick="onPick('${q.id}','${k}')">
            <div class="opt-en">${k}. ${quizTextHtml(opts[k], q.id)}</div>
            ${optsCn[k] ? `<div class="opt-cn">${esc(optsCn[k])}</div>` : ''}
        </div>`).join('')}
        <div id="expl-${q.id}"></div>
    </div>`;
}

/** 题目文本渲染：英文词/词组可点查释义（点词 stopPropagation 不触达答题，点空白/字母处仍选答案） */
function quizTextHtml(text, sid) {
    return annotatePhrases(text, sid);
}

async function onPick(qid, key) {
    const q = article.questions.find(x => x.id === qid);
    if (!q) return;
    const ok = key === q.answer;
    answerMap[qid] = { question_id: qid, user_answer: key, is_correct: ok ? 1 : 0 };
    await saveAnswer(qid, AID, key, ok);
    showResult(q, key, true);
}

/** 显示某题的作答结果（restore=false 时也用于页面加载恢复） */
function showResult(q, userKey, scrollToRelated) {
    const ok = userKey === q.answer;
    const opts = (q.options && Object.keys(q.options).length) ? q.options : (article.pool || {});
    for (const k of Object.keys(opts)) {
        const el = document.getElementById(`opt-${q.id}-${k}`);
        if (!el) continue;
        el.classList.remove('picked', 'right', 'wrong');
        if (k === q.answer) el.classList.add('right');
        else if (k === userKey) el.classList.add('wrong');
    }
    const expl = document.getElementById(`expl-${q.id}`);
    if (expl) {
        expl.innerHTML = `<div class="q-expl">
            <span class="expl-tag">${ok ? '✔ 回答正确' : '✘ 回答错误'} · 答案 ${q.answer}</span>
            <div>${esc(q.explanation || '')}</div>
            ${(q.related_sentences || []).length ? `<button class="q-locate" onclick="locateRelated('${q.id}')">↖ 定位原文依据</button>` : ''}
        </div>`;
    }
    const jb = document.getElementById(`qj-${q.id}`);
    if (jb) { jb.classList.remove('answered-right', 'answered-wrong'); jb.classList.add(ok ? 'answered-right' : 'answered-wrong'); }
    // 完形空格联动
    if (article.type === 'cloze') {
        const blank = document.getElementById(`blank-${q.number}`);
        if (blank) {
            blank.textContent = opts[userKey] || `[${q.number}]`;
            blank.classList.remove('filled-right', 'filled-wrong');
            blank.classList.add(ok ? 'filled-right' : 'filled-wrong');
        }
    }
    if (scrollToRelated && (q.related_sentences || []).length) locateRelated(q.id);
}

/** 高亮题目关联句并滚动定位；再次点击同题按钮则取消高亮 */
let locatedQid = null;

function clearRelated() {
    document.querySelectorAll('.sent.related').forEach(el => el.classList.remove('related'));
    document.querySelectorAll('.q-locate.active').forEach(b => {
        b.classList.remove('active');
        b.textContent = '↖ 定位原文依据';
    });
    locatedQid = null;
}

function locateRelated(qid) {
    const q = article.questions.find(x => x.id === qid);
    if (!q) return;
    // 再次点击同一题的定位按钮 → 取消黄色高亮
    if (locatedQid === qid) { clearRelated(); return; }
    clearRelated();
    let first = null;
    for (const sid of q.related_sentences || []) {
        const el = document.getElementById('s-' + sid);
        if (el) {
            el.classList.add('related');
            if (!first) first = el;
            // 顺带展开关联句译文
            const cn = el.querySelector('.sent-cn');
            if (cn) cn.classList.add('open');
        }
    }
    locatedQid = qid;
    const btn = document.querySelector(`#expl-${CSS.escape(qid)} .q-locate`);
    if (btn) { btn.classList.add('active'); btn.textContent = '✕ 取消定位'; }
    if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function jumpQ(qid) {
    const el = document.getElementById('q-' + qid);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function onBlankClick(e, n) {
    e.stopPropagation();
    // 点完形空格：切到做题模式并跳到对应题
    if (!isQuizMode()) toggleMode();
    const q = (article.questions || []).find(x => x.number === n);
    if (q) jumpQ(q.id);
}

// ============ 学习进度：滚动节流记录 + 恢复 ============
async function restoreScroll() {
    // URL hash（生词本/收藏跳回）优先
    const hash = decodeURIComponent(location.hash.replace(/^#/, ''));
    let target = hash ? document.getElementById('s-' + hash) : null;
    if (!target) {
        const prog = await dbGet('article_progress', AID);
        if (prog && prog.last_sentence_id) target = document.getElementById('s-' + prog.last_sentence_id);
    }
    if (target) {
        // 仅续读滚动到上次位置，不做短暂高亮，避免每次点入文章闪现黄色
        target.scrollIntoView({ block: 'center' });
    }
}

function watchScroll() {
    let timer = null;
    window.addEventListener('scroll', () => {
        if (timer) return;
        timer = setTimeout(() => {
            timer = null;
            // 取视口上部 1/3 处最近的句子
            const sents = document.querySelectorAll('.sent');
            let cur = null;
            for (const el of sents) {
                if (el.getBoundingClientRect().top <= window.innerHeight / 3) cur = el;
                else break;
            }
            if (cur) saveProgress(AID, cur.dataset.sid);
        }, 500);
    }, { passive: true });
}

// ============ 悬浮设置面板（自定义查词快捷键 + 夜间 + 标注备份入口） ============
// 仿 study.js 的悬浮设置窗：localStorage 存自定义按键，绑定态独占一次按键输入。
let artBindAction = null;   // 正在等待按键绑定的动作

/** 查词快捷键动作（可自定义）。默认 Alt+C 聚焦查词框。 */
const ART_KEYS_DEFAULT = { navSearch: 'Alt+KeyC' };
const ART_KEY_ACTIONS = [['navSearch', '聚焦查词框']];

function getArtKeyMap() {
    try { return { ...ART_KEYS_DEFAULT, ...(JSON.parse(localStorage.getItem('en2_artkeys') || '{}')) }; }
    catch (e) { return { ...ART_KEYS_DEFAULT }; }
}
function setArtKeyMap(m) { localStorage.setItem('en2_artkeys', JSON.stringify(m)); }

/** 把 e.code 格式化为含修饰键的可读控件串：e.g. Alt+KeyC → 'Alt + C' */
function artKeyLabel(code) {
    const M = { Space: '空格', AltLeft: 'Alt', CtrlLeft: 'Ctrl', ShiftLeft: 'Shift', AltRight: 'Alt', CtrlRight: 'Ctrl', ShiftRight: 'Shift', Backspace: '⌫', Enter: '↵', Escape: 'Esc' };
    if (M[code]) return M[code];
    if (code && code.startsWith('Key')) return code.slice(3);
    if (code && code.startsWith('Digit')) return code.slice(5);
    if (code && code.startsWith('F') && /^F\d+$/.test(code)) return code;
    return code || '—';
}

/** 将事件转为规范 key 串（含修饰符前缀），用于绑定与匹配：e.g. Alt+KeyC。 */
function eventKeyStr(e) {
    const mods = [];
    if (e.altKey) mods.push('Alt');
    if (e.ctrlKey) mods.push('Ctrl');
    if (e.shiftKey) mods.push('Shift');
    return (mods.length ? mods.join('+') + '+' : '') + e.code;
}

/** 匹配：事件命中某动作绑定的快捷键（e.code 相同且修饰键组合一致）。 */
function artMatch(e, combo) {
    if (!combo) return false;
    return eventKeyStr(e) === combo;
}

function buildArtPanel() {
    if (document.getElementById('artSettings')) return;
    const p = document.createElement('div');
    p.id = 'artSettings';
    p.className = 'float-panel';
    p.hidden = true;
    p.addEventListener('click', e => e.stopPropagation());   // 面板内点击不冒泡触发外部关闭
    document.body.appendChild(p);
}

function toggleArtSettings() {
    buildArtPanel();
    const p = document.getElementById('artSettings');
    if (p.hidden) { renderArtSettings(); p.hidden = false; }
    else hideArtSettings();
}

function hideArtSettings() {
    const p = document.getElementById('artSettings');
    if (p && !p.hidden) { p.hidden = true; artBindAction = null; }
}

function renderArtSettings() {
    const p = document.getElementById('artSettings');
    if (!p) return;
    const km = getArtKeyMap();
    const rows = ART_KEY_ACTIONS.map(([act, label]) => {
        const binding = artBindAction === act;
        return `<div class="ss-row"><span class="ss-act">${label}</span>
            <button class="ss-key${binding ? ' binding' : ''}" onclick="startArtBind('${act}')">${binding ? '按键…' : esc(artKeyLabel(km[act]))}</button></div>`;
    }).join('');
    const darkOn = localStorage.getItem('darkMode') === '1';
    p.innerHTML = `
        <div class="ss-title">快捷键 <span class="ss-tip">点键位后按新键</span></div>
        ${rows}
        <button class="ss-reset" onclick="resetArtKeys()">恢复默认</button>
        <div class="ss-title">夜间模式</div>
        <div class="ss-row"><span class="ss-act">深色护眼</span>
            <button class="ss-toggle${darkOn ? ' on' : ''}" onclick="toggleArtDark()">${darkOn ? '开' : '关'}</button></div>
        <div class="ss-title">标注备份</div>
        <div class="ss-row"><button class="ss-key" onclick="Annot.exportAnnot()">导出标注</button></div>
        <div class="ss-row"><button class="ss-key" onclick="document.getElementById('annImport').click()">导入标注</button></div>
        <div class="ss-title">查词历史</div>
        <div class="ss-row"><button class="ss-key" onclick="clearSearchHist()">清空历史</button></div>`;
}

function startArtBind(act) { artBindAction = act; renderArtSettings(); }
function resetArtKeys() { setArtKeyMap({ ...ART_KEYS_DEFAULT }); artBindAction = null; renderArtSettings(); }
function toggleArtDark() {
    const on = localStorage.getItem('darkMode') !== '1';
    localStorage.setItem('darkMode', on ? '1' : '0');
    applyDark();
    renderDarkSwitch();
    renderArtSettings();
    hideArtSettings();
}

// 查词快捷键：聚焦 / 点击历史弹出时也聚焦
function focusNavSearch() {
    const inp = document.getElementById('navSearch');
    if (inp) { inp.focus(); inp.select(); showSearchHist(); }
}

// 全局键盘：绑定态 → 写入快捷键；否则匹配查词快捷键聚焦
document.addEventListener('keydown', (e) => {
    if (artBindAction) {
        e.preventDefault();
        if (e.code === 'Escape') { artBindAction = null; renderArtSettings(); return; }
        const combo = eventKeyStr(e);
        // 忽略纯修饰键按下（如单独按 Alt/Ctrl/Shift），避免绑定失效
        if (e.code === 'AltLeft' || e.code === 'AltRight' || e.code === 'ControlLeft' ||
            e.code === 'ControlRight' || e.code === 'ShiftLeft' || e.code === 'ShiftRight' ||
            e.code === 'MetaLeft' || e.code === 'MetaRight') return;
        if (!combo) return;
        const dup = ART_KEY_ACTIONS.find(([a]) => a !== artBindAction && getArtKeyMap()[a] === combo);
        if (dup) { alert('「' + artKeyLabel(combo) + '」已绑定给「' + dup[1] + '」，请换一个键'); return; }
        const km2 = getArtKeyMap();
        km2[artBindAction] = combo;
        setArtKeyMap(km2);
        artBindAction = null;
        renderArtSettings();
        return;
    }
    // 输入框/下拉框内不拦截（查词框里 Alt+C 也要能触发，故单独豁免）
    const t = e.target;
    const inInput = t && /^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName);
    if (e.code === 'Escape') { hideArtSettings(); hideSearchHist(); return; }
    const km = getArtKeyMap();
    if (artMatch(e, km.navSearch)) { e.preventDefault(); focusNavSearch(); return; }
    if (inInput && t) return;   // 其余输入框内不拦截快捷键
});

// 点击面板外或滚动时收起设置
document.addEventListener('click', () => hideArtSettings());
window.addEventListener('scroll', () => hideArtSettings(), { passive: true });

init();
