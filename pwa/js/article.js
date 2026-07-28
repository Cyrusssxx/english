/* 英语二精翻 - 精读页：逐句渲染 + 词组优先下划线 + 释义弹卡 + 句子收藏 + 做题面板 */

const AID = new URLSearchParams(location.search).get('id') || '';
let article = null;
let vocabSet = new Set();      // 已在生词本的词
let favSet = new Set();        // 已收藏句子
let answerMap = {};            // {question_id: {user_answer, is_correct}}
let popEl = null;              // 当前释义弹卡

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
    vocabSet = new Set((await dbAll('vocab')).map(v => v.word));
    favSet = new Set((await dbAll('fav_sentences')).map(f => f.sentence_id));
    for (const a of await dbAll('quiz_answers')) if (a.article_id === AID) answerMap[a.question_id] = a;

    renderModeSwitch();
    renderQuizCollapse();
    renderArticle();
    renderQuiz();
    await restoreScroll();
    watchScroll();
}

// ============ 正文渲染 ============
function renderArticle() {
    const paras = [];   // [[sent,...], ...] 按 para 分组（缺省视为一段）
    for (const s of article.sentences) {
        const p = (s.para || 1) - 1;
        (paras[p] || (paras[p] = [])).push(s);
    }
    let html = `<div class="read-title">${esc(article.title || '')}</div>`;
    html += `<div class="read-source">${esc(article.source || '')} · 点句下占位条显示译文，点下划线词查释义</div>`;
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
    // 分段结构：{text} 为纯文本段，{text, wi} 为已命中的词段
    let segs = [{ text: s.en }];
    const missed = [];
    for (const w of words) {
        let hit = false;
        for (let i = 0; i < segs.length; i++) {
            const seg = segs[i];
            if (seg.wi !== undefined) continue;
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
    const html = segs.map(seg => {
        if (seg.wi !== undefined) {
            const w = s.words[seg.wi];
            const inV = vocabSet.has(w.w);
            return `<span class="word ${inV ? 'in-vocab' : ''}" data-w="${esc(w.w)}" onclick="onWordClick(event,'${s.id}',${seg.wi})">${esc(seg.text)}</span>`;
        }
        // 纯文本段：转义后替换完形空格 [n]
        return esc(seg.text).replace(/\[(\d+)\]/g, (_, n) =>
            `<span class="blank" id="blank-${n}" onclick="onBlankClick(event,${n})">[${n}]</span>`);
    }).join('');
    return { html, missed };
}

/** 全词匹配（前后均非字母才算命中），返回位置或 -1 */
function findWord(text, w) {
    let from = 0;
    while (true) {
        const pos = text.indexOf(w, from);
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
function onWordClick(e, sid, wi) {
    e.stopPropagation();
    closePop();
    const sent = article.sentences.find(x => x.id === sid);
    const w = sent && sent.words[wi];
    if (!w) return;
    const inV = vocabSet.has(w.w);
    popEl = document.createElement('div');
    popEl.className = 'word-pop';
    popEl.innerHTML = `
        <span class="wp-word">${esc(w.w)}</span><span class="wp-phonetic">${esc(w.phonetic || '')}</span>
        <div class="wp-meaning">${esc(w.meaning || '')}</div>
        <button class="${inV ? 'added' : ''}" onclick="onAddVocab(this,'${sid}',${wi})">${inV ? '移出生词本' : '+ 加入生词本'}</button>`;
    document.body.appendChild(popEl);
    const r = e.target.getBoundingClientRect();
    const pw = popEl.offsetWidth;
    let left = r.left + window.scrollX;
    if (left + pw > window.scrollX + document.documentElement.clientWidth - 12) {
        left = window.scrollX + document.documentElement.clientWidth - pw - 12;
    }
    popEl.style.left = left + 'px';
    popEl.style.top = (r.bottom + window.scrollY + 6) + 'px';
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
        await addVocab(w.w, w.meaning, w.phonetic, sid, AID);
        vocabSet.add(w.w);
        btn.textContent = '已加入 ✓';
        btn.classList.add('added');
    }
    // 同步正文中该词的下划线样式
    document.querySelectorAll(`.word[data-w="${CSS.escape(w.w)}"]`)
        .forEach(el => el.classList.toggle('in-vocab', vocabSet.has(w.w)));
}

function closePop() {
    if (popEl) { popEl.remove(); popEl = null; }
}

document.addEventListener('click', (e) => {
    if (popEl && !e.target.closest('.word-pop') && !e.target.closest('.word')) closePop();
});

// ============ 做题面板 ============
function renderQuiz() {
    const qs = article.questions || [];
    const scroll = document.getElementById('quizScroll');
    if (!qs.length) {
        scroll.innerHTML = '<div class="empty">本篇暂无题目</div>';
        return;
    }
    let html = '';
    // 新题型：共享选项池
    if (article.pool) {
        html += '<div class="pool-box"><b>选项池</b>' + Object.entries(article.pool).map(([k, v]) =>
            `<div class="pool-item">[${k}] ${esc(v)}${article.pool_cn && article.pool_cn[k] ? `<br><small style="color:var(--text-light)">${esc(article.pool_cn[k])}</small>` : ''}</div>`).join('') + '</div>';
    }
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

function questionHtml(q) {
    const opts = q.options || article.pool || {};
    const optsCn = q.options_cn || article.pool_cn || {};
    return `<div class="qblock" id="q-${q.id}">
        <div class="q-head"><span class="q-no">Q${q.number}</span>${q.qtype ? `<span class="q-type-badge">${esc(q.qtype)}</span>` : ''}</div>
        <div class="q-stem">${esc(q.stem || '')}</div>
        ${q.stem_cn ? `<div class="q-stem-cn">${esc(q.stem_cn)}</div>` : ''}
        ${Object.keys(opts).map(k => `
        <div class="q-opt" id="opt-${q.id}-${k}" onclick="onPick('${q.id}','${k}')">
            <div class="opt-en">${k}. ${esc(opts[k])}</div>
            ${optsCn[k] ? `<div class="opt-cn">${esc(optsCn[k])}</div>` : ''}
        </div>`).join('')}
        <div id="expl-${q.id}"></div>
    </div>`;
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
    const opts = q.options || article.pool || {};
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
        target.scrollIntoView({ block: 'center' });
        target.classList.add('related');
        setTimeout(() => target.classList.remove('related'), 2000);
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

init();
