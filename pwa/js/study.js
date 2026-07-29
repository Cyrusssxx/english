/* 英语二精翻 - 背单词模块：以生词本为队列的单词卡 + 间隔重复（SM-2 简化版）
 * 复习状态写入 vocab 记录的 srs 字段（不改 IndexedDB schema，随备份一并导出）。
 * 例句从对应年份题库解析（离线缓存），目标词加粗；释义按“核心义加粗”规则渲染。
 */

const NEW_LIMIT = 20;          // 每轮最多引入的新词数
let queue = [];                // 本轮队列（元素为 vocab 记录）
let cur = 0;                   // 当前卡索引
let flipped = false;           // 是否已翻面
let done = 0;                  // 本轮已判定数
const _artCache = {};          // {article_id: article} 例句解析缓存

// ============ 日期工具（ISO 字符串，字典序即时间序） ============
function dayStr(offset = 0) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return d.toISOString().slice(0, 10);
}

// ============ 间隔重复评分 ============
function grade(v, known) {
    const s = v.srs || { interval: 0, reps: 0, ease: 2.5, lapses: 0 };
    if (known) {
        s.reps = (s.reps || 0) + 1;
        if (s.reps === 1) s.interval = 1;
        else if (s.reps === 2) s.interval = 3;
        else s.interval = Math.max(1, Math.round((s.interval || 1) * (s.ease || 2.5)));
        s.ease = Math.min(3.0, (s.ease || 2.5) + 0.05);
    } else {
        s.reps = 0;
        s.lapses = (s.lapses || 0) + 1;
        s.ease = Math.max(1.3, (s.ease || 2.5) - 0.2);
        s.interval = 1;
    }
    s.due = dayStr(s.interval);
    s.last = dayStr(0);
    v.srs = s;
    return v;
}

// ============ 全词边界匹配（与精读页一致，w 为原句精确词形） ============
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

/** 例句：目标词加粗 + 主色 */
function highlightExample(en, w) {
    if (!en) return '';
    const pos = findWord(en, w);
    if (pos < 0) return esc(en);
    return esc(en.slice(0, pos)) + '<b class="tgt">' + esc(en.slice(pos, pos + w.length)) +
        '</b>' + esc(en.slice(pos + w.length));
}

/** 释义按记忆层级渲染：词性斜体主色 · 核心义加粗主色 · 次要义弱化 */
function renderMeaning(raw) {
    raw = raw || '';
    let html = '';
    const pm = raw.match(/^\s*(词组[：:]|[A-Za-z]+\.)\s*/);
    let rest = raw;
    if (pm) { html += `<span class="mp-pos">${esc(pm[1])}</span> `; rest = raw.slice(pm[0].length); }
    const m = rest.match(/^([^，,；;、（(]+)([\s\S]*)$/);
    if (m) {
        html += `<b class="mp-core">${esc(m[1].trim())}</b>`;
        if (m[2]) html += `<span class="mp-sec">${esc(m[2])}</span>`;
    } else {
        html += esc(rest);
    }
    return html;
}

// ============ 例句解析（从题库离线取原句） ============
async function resolveExample(v) {
    if (v.example_en) return { en: v.example_en, cn: v.example_cn || '' };
    if (!v.article_id || !v.sentence_id) return null;
    try {
        let art = _artCache[v.article_id];
        if (!art) { art = await getArticle(v.article_id); _artCache[v.article_id] = art; }
        const s = art && art.sentences.find(x => x.id === v.sentence_id);
        return s ? { en: s.en, cn: s.cn || '' } : null;
    } catch (e) { return null; }
}

// ============ 发音（浏览器 TTS，离线可用） ============
function speak(word) {
    try {
        const u = new SpeechSynthesisUtterance(word);
        u.lang = 'en-US'; u.rate = 0.9;
        speechSynthesis.cancel();
        speechSynthesis.speak(u);
    } catch (e) { /* 不支持则静默 */ }
}

// ============ 队列构建 ============
async function buildQueue(includeAll) {
    const all = (await dbAll('vocab'));
    const today = dayStr(0);
    const reviews = all.filter(v => v.srs && v.srs.due && v.srs.due <= today);
    const news = all.filter(v => !v.srs);
    const future = all.filter(v => v.srs && v.srs.due && v.srs.due > today);
    let q;
    if (includeAll) {
        // 提前学：到期复习 + 新词 + 未到期（未到期按 due 升序）
        future.sort((a, b) => (a.srs.due || '').localeCompare(b.srs.due || ''));
        q = [...reviews, ...news.slice(0, NEW_LIMIT), ...future];
    } else {
        q = [...reviews, ...news.slice(0, NEW_LIMIT)];
    }
    return { q, total: all.length, reviews: reviews.length, news: news.length };
}

// ============ 渲染 ============
async function start(includeAll) {
    const info = await buildQueue(includeAll);
    queue = info.q; cur = 0; done = 0; flipped = false;
    const root = document.getElementById('studyRoot');
    if (!info.total) {
        root.innerHTML = `<div class="study-empty">
            <div class="se-emoji">📖</div>
            <p>生词本还是空的。</p>
            <p class="se-hint">精读真题时，点原文里带下划线的词，在弹卡中「加入生词本」，这里就能背它们。</p>
            <a class="se-btn" href="index.html">去精读真题 →</a></div>`;
        return;
    }
    if (!queue.length) {
        root.innerHTML = `<div class="study-empty">
            <div class="se-emoji">🎉</div>
            <p>今日待复习已清空！</p>
            <p class="se-hint">共 ${info.total} 个词，均已安排到未来的复习日。</p>
            <button class="se-btn" onclick="start(true)">提前背未到期的词 →</button></div>`;
        return;
    }
    renderCard();
}

async function renderCard() {
    const root = document.getElementById('studyRoot');
    if (cur >= queue.length) { renderDone(); return; }
    const v = queue[cur];
    flipped = false;
    const remain = queue.length - cur;
    const tag = (v.srs && v.srs.reps) ? '<span class="ct-tag review">复习</span>'
        : '<span class="ct-tag new">新词</span>';
    root.innerHTML = `
        <div class="study-bar">
            <div class="sb-stat"><b>${done}</b> 已背</div>
            <div class="sb-stat"><b>${remain}</b> 本轮剩余</div>
            <div class="sb-prog"><span style="width:${queue.length ? (cur / queue.length * 100) : 0}%"></span></div>
        </div>
        <div class="flashcard" id="flashcard" onclick="onFlip()">
            <div class="fc-face fc-front">
                ${tag}
                <div class="fc-word">${esc(v.word)}</div>
                <div class="fc-phonetic">${esc(v.phonetic || '')}</div>
                <button class="fc-play" onclick="event.stopPropagation();speak('${esc(v.word).replace(/'/g, "\\'")}')" title="朗读">🔊</button>
                <div class="fc-hint">点击卡片 / 空格 展开释义</div>
            </div>
            <div class="fc-face fc-back" id="fcBack"><div class="loading">…</div></div>
        </div>
        <div class="study-actions" id="studyActions"></div>`;
    // 异步填充背面例句
    const ex = await resolveExample(v);
    const back = document.getElementById('fcBack');
    if (back) {
        back.innerHTML = `
            <div class="fc-word sm">${esc(v.word)}
                <button class="fc-play" onclick="event.stopPropagation();speak('${esc(v.word).replace(/'/g, "\\'")}')" title="朗读">🔊</button>
            </div>
            <div class="fc-meaning">${renderMeaning(v.meaning)}</div>
            ${ex ? `<div class="fc-example">
                <div class="fe-en">${highlightExample(ex.en, v.word)}</div>
                <div class="fe-cn">${esc(ex.cn)}</div>
            </div>` : ''}
            <div class="fc-src"><a href="article.html?id=${esc(v.article_id || '')}#${esc(v.sentence_id || '')}" onclick="event.stopPropagation()">查看原文语境 →</a></div>`;
    }
}

function onFlip() {
    const card = document.getElementById('flashcard');
    if (!card) return;
    flipped = !flipped;
    card.classList.toggle('flipped', flipped);
    // 翻到背面才出现判定按钮
    const act = document.getElementById('studyActions');
    if (flipped && act && !act.innerHTML) {
        act.innerHTML = `
            <button class="sa-btn again" onclick="judge(false)">✕ 不认识 <kbd>←</kbd></button>
            <button class="sa-btn good" onclick="judge(true)">✓ 认识 <kbd>→</kbd></button>`;
    }
}

async function judge(known) {
    if (cur >= queue.length) return;
    const v = grade(queue[cur], known);
    await dbPut('vocab', v);
    done++;
    if (!known) queue.push({ ...v });   // 不认识：本轮末尾再来一次
    cur++;
    renderCard();
}

function renderDone() {
    document.getElementById('studyRoot').innerHTML = `<div class="study-empty">
        <div class="se-emoji">✅</div>
        <p>本轮完成，共判定 ${done} 次！</p>
        <p class="se-hint">认识的词已按记忆曲线拉长复习间隔，不认识的会明天再来。</p>
        <button class="se-btn" onclick="start(false)">再来一轮 →</button>
        <a class="se-btn ghost" href="vocab.html">回生词本</a></div>`;
}

// ============ 键盘快捷键 ============
document.addEventListener('keydown', (e) => {
    if (!queue.length || cur >= queue.length) return;
    if (e.code === 'Space') { e.preventDefault(); onFlip(); }
    else if (flipped && e.code === 'ArrowLeft') { e.preventDefault(); judge(false); }
    else if (flipped && e.code === 'ArrowRight') { e.preventDefault(); judge(true); }
});

start(false);
