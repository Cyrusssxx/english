/* 英语二精翻 - 背单词模块：以生词本为队列的单词卡 + 间隔重复（SM-2 简化版）
 * 复习状态写入 vocab 记录的 srs 字段（不改 IndexedDB schema，随备份一并导出）。
 * 例句从对应年份题库解析（离线缓存），目标词加粗；释义按“核心义加粗”规则渲染。
 */

const DEFAULT_DAILY = 20;      // 每日新词量默认值
let queue = [];                // 本轮队列（元素为 vocab 记录）
let cur = 0;                   // 当前卡索引
let flipped = false;           // 是否已翻面
let done = 0;                  // 本轮已判定数
let history = [];              // 判定历史栈（供「回退」撤销误点）
let deckStat = null;           // 本轮词书统计快照（start/resume 时计算，供统计条展示）
const _artCache = {};          // {article_id: article} 例句解析缓存

// 每日计划：每轮最多引入的新词数（可在背词页设置，存 localStorage）
function getDailyPlan() { return parseInt(localStorage.getItem('en2_dailyPlan') || '', 10) || DEFAULT_DAILY; }
function setDailyPlan(n) { localStorage.setItem('en2_dailyPlan', String(n)); }

// 学习模式：mix=复习优先(到期复习+当日新词) / review=只复习旧词 / new=只学新词
function getStudyMode() {
    const m = localStorage.getItem('en2_studyMode');
    return (m === 'review' || m === 'new') ? m : 'mix';
}
function setStudyMode(m) { localStorage.setItem('en2_studyMode', m); }

// 自动播放：卡片出现自动读单词 / 翻面显示释义时自动读例句（默认关）
function getAutoWord() { return localStorage.getItem('en2_autoWord') === '1'; }
function setAutoWord(v) { localStorage.setItem('en2_autoWord', v ? '1' : '0'); }
function getAutoExample() { return localStorage.getItem('en2_autoExample') === '1'; }
function setAutoExample(v) { localStorage.setItem('en2_autoExample', v ? '1' : '0'); }

// 自定义快捷键：动作 -> KeyboardEvent.code，存 localStorage
const DEFAULT_KEYS = { flip: 'Space', known: 'ArrowRight', unknown: 'ArrowLeft', undo: 'Backspace', fav: 'KeyF' };
const KEY_ACTIONS = [['flip', '显示释义'], ['known', '认识'], ['unknown', '不认识'], ['undo', '回退'], ['fav', '收藏到目标词书']];
function getKeyMap() { try { return { ...DEFAULT_KEYS, ...(JSON.parse(localStorage.getItem('en2_keymap') || '{}')) }; } catch (e) { return { ...DEFAULT_KEYS }; } }
function setKeyMap(m) { localStorage.setItem('en2_keymap', JSON.stringify(m)); }
function keyLabel(code) {
    const M = { Space: '空格', ArrowLeft: '←', ArrowRight: '→', ArrowUp: '↑', ArrowDown: '↓', Backspace: '⌫', Enter: '↵', Escape: 'Esc' };
    if (M[code]) return M[code];
    if (code && code.startsWith('Key')) return code.slice(3);
    if (code && code.startsWith('Digit')) return code.slice(5);
    return code || '—';
}

// 会话续存：同一天/同词书/同模式的未完成本轮，跨页返回后可恢复，避免进度归零
function getSession() {
    try { return JSON.parse(localStorage.getItem('en2_studySession') || 'null'); } catch (e) { return null; }
}
function saveSession() {
    localStorage.setItem('en2_studySession', JSON.stringify({
        date: dayStr(0), deck: getStudyDeck(), mode: getStudyMode(),
        words: queue.map(v => v.word), cur, done
    }));
}
function clearSession() { localStorage.removeItem('en2_studySession'); }

// ============ 日期工具（ISO 字符串，字典序即时间序） ============
function dayStr(offset = 0) {
    const d = new Date();
    d.setDate(d.getDate() + offset);
    return d.toISOString().slice(0, 10);
}

// ============ 间隔重复评分（简化 SM-2 + new→learning→review 状态） ============
function grade(v, known) {
    const s = v.srs || { interval: 0, reps: 0, ease: 2.5, lapses: 0, state: 'new' };
    if (known) {
        s.reps = (s.reps || 0) + 1;
        // 学习步：新词首次认识 1 天、二次 3 天，之后 ×ease，避免新词一次就被拉到长间隔
        if (s.reps === 1) { s.interval = 1; s.state = 'learning'; }
        else if (s.reps === 2) { s.interval = 3; s.state = 'learning'; }
        else { s.interval = Math.max(1, Math.round((s.interval || 1) * (s.ease || 2.5))); s.state = 'review'; }
        s.ease = Math.min(3.0, (s.ease || 2.5) + 0.05);
    } else {
        s.reps = 0;
        s.lapses = (s.lapses || 0) + 1;
        s.ease = Math.max(1.3, (s.ease || 2.5) - 0.2);
        s.interval = 1;
        s.state = 'learning';
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
    // 兼容历史数据：静默剥离「词组：」前缀（不再作为标签显示）
    let rest = raw.replace(/^\s*词组[：:]\s*/, '');
    const pm = rest.match(/^([A-Za-z]+\.)\s*/);
    if (pm) { html += `<span class="mp-pos">${esc(pm[1])}</span> `; rest = rest.slice(pm[0].length); }
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

// ============ 发音（有道在线美音优先，断网/失败回退浏览器 TTS） ============
let _voiceAudio = null;             // 复用单个 Audio 实例，避免连点叠音
let _curExampleEn = '';             // 当前卡片例句英文（供翻面自动朗读）

function speakLocal(word) {         // 回退：浏览器语音合成，离线可用
    try {
        const u = new SpeechSynthesisUtterance(word);
        u.lang = 'en-US'; u.rate = 0.9;
        speechSynthesis.cancel();
        speechSynthesis.speak(u);
    } catch (e) { /* 不支持则静默 */ }
}

function speak(word) {
    try {
        // 先停掉上一次的播放与合成，避免叠音
        if (_voiceAudio) { try { _voiceAudio.pause(); _voiceAudio.currentTime = 0; } catch (e) {} }
        try { speechSynthesis.cancel(); } catch (e) {}
        // 离线直接走本地 TTS，省一次必失败的请求
        if (navigator.onLine === false) { speakLocal(word); return; }
        // 在线：有道 dictvoice 自然美音（type=2=美音）
        const url = 'https://dict.youdao.com/dictvoice?audio=' + encodeURIComponent(word) + '&type=2';
        if (!_voiceAudio) _voiceAudio = new Audio();
        _voiceAudio.onerror = () => speakLocal(word);
        _voiceAudio.src = url;
        const p = _voiceAudio.play();
        if (p && typeof p.catch === 'function') p.catch(() => speakLocal(word));
    } catch (e) {
        speakLocal(word);
    }
}

// 自动播放开关：切换设置并就地更新按钮激活态（不重绘卡片，避免误触发朗读）
function toggleAutoWord() {
    setAutoWord(!getAutoWord());
    const b = document.getElementById('btnAutoWord');
    if (b) b.classList.toggle('on', getAutoWord());
}
function toggleAutoExample() {
    setAutoExample(!getAutoExample());
    const b = document.getElementById('btnAutoExample');
    if (b) b.classList.toggle('on', getAutoExample());
}

// ============ 队列构建 ============
// mode: mix=到期复习+当日新词 / review=仅到期复习 / new=仅新词；includeFuture=提前背未到期词
async function buildQueue(mode, includeFuture) {
    const all = (await vocabByDeck(getStudyDeck()));
    const today = dayStr(0);
    const reviews = all.filter(v => v.srs && v.srs.due && v.srs.due <= today);
    const news = all.filter(v => !v.srs);
    const future = all.filter(v => v.srs && v.srs.due && v.srs.due > today);
    future.sort((a, b) => (a.srs.due || '').localeCompare(b.srs.due || ''));
    let q;
    if (mode === 'review') {
        q = includeFuture ? [...reviews, ...future] : [...reviews];
    } else if (mode === 'new') {
        q = news.slice(0, getDailyPlan());
    } else {   // mix
        q = includeFuture
            ? [...reviews, ...news.slice(0, getDailyPlan()), ...future]
            : [...reviews, ...news.slice(0, getDailyPlan())];
    }
    return { q, total: all.length, reviews: reviews.length, news: news.length, future: future.length };
}

// ============ 词书选择条 ============
async function renderDeckBar() {
    const bar = document.getElementById('studyDeckBar');
    if (!bar) return;
    const counts = await deckCounts();
    const sel = getStudyDeck();
    const opts = [`<option value="__all__"${sel === '__all__' ? ' selected' : ''}>全部词书 (${counts['__all__'] || 0})</option>`];
    for (const d of getDecks()) {
        opts.push(`<option value="${esc(d.id)}"${sel === d.id ? ' selected' : ''}>${esc(d.name)} (${counts[d.id] || 0})</option>`);
    }
    const mode = getStudyMode();
    const mbtn = (m, label) => `<button class="mode-btn${mode === m ? ' active' : ''}" onclick="setMode('${m}')">${label}</button>`;
    bar.innerHTML = `<label class="deck-bar-label">背词范围</label>
        <select class="deck-select" id="studyDeckSelect" onchange="onStudyDeckChange(this.value)">${opts.join('')}</select>
        <div class="mode-switch">${mbtn('mix', '复习优先')}${mbtn('review', '只复习')}${mbtn('new', '只学新词')}</div>`;
}

async function onStudyDeckChange(id) {
    setStudyDeck(id);
    clearSession();
    await start(false);
}

/** 切换学习模式：清掉旧会话、重绘选择条、按新模式开新一轮 */
function setMode(m) {
    setStudyMode(m);
    clearSession();
    renderDeckBar();
    start(false);
}

// ============ 渲染 ============
// includeFuture: 待背为空时是否把未到期词也提前拉进本轮
async function start(includeFuture) {
    clearSession();
    const mode = getStudyMode();
    const info = await buildQueue(mode, includeFuture);
    queue = info.q; cur = 0; done = 0; flipped = false; history = [];
    deckStat = await deckStats(getStudyDeck());
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
        const emptyMsg = mode === 'new' ? '这个范围没有可学的新词了！'
            : mode === 'review' ? '当前没有到期待复习的词！' : '今日待背已清空！';
        root.innerHTML = `<div class="study-empty">
            <div class="se-emoji">🎉</div>
            <p>${emptyMsg}</p>
            <p class="se-hint">共 ${info.total} 个词，其中 ${info.future} 个已安排到未来复习日。</p>
            ${info.future ? `<button class="se-btn" onclick="start(true)">提前背未到期的词 →</button>` : ''}
            <a class="se-btn ghost" href="vocab.html">回生词本</a></div>`;
        return;
    }
    renderCard();
}

/** 恢复未完成的本轮（同日/同词书/同模式），成功则直接渲染当前卡，返回是否恢复成功 */
async function resumeSession() {
    const s = getSession();
    if (!s || s.date !== dayStr(0) || s.deck !== getStudyDeck() || s.mode !== getStudyMode()) return false;
    if (!Array.isArray(s.words) || !s.words.length || (s.cur || 0) >= s.words.length) return false;
    const byWord = {};
    for (const v of await vocabByDeck(getStudyDeck())) byWord[v.word] = v;
    const q = [];
    for (const w of s.words) { if (byWord[w]) q.push(byWord[w]); }
    if (!q.length || (s.cur || 0) >= q.length) return false;
    queue = q; cur = Math.min(s.cur || 0, q.length); done = s.done || 0; flipped = false; history = [];
    deckStat = await deckStats(getStudyDeck());
    renderCard();
    return true;
}

async function renderCard() {
    const root = document.getElementById('studyRoot');
    if (cur >= queue.length) { renderDone(); return; }
    const v = queue[cur];
    flipped = false;
    const remain = queue.length - cur;
    const tag = (v.srs && v.srs.reps) ? '<span class="ct-tag review">复习</span>'
        : '<span class="ct-tag new">新词</span>';
    const wsafe = esc(v.word).replace(/'/g, "\\'");
    const favTarget = getActiveDeck();
    const inTarget = (Array.isArray(v.decks) ? v.decks : ['default']).includes(favTarget);
    // 结构固定：卡片头(单词)常驻顶部 + 释义区高度预留 + 底部操作条常驻，
    // 翻面只是在预留区内淡入内容，卡片外高不变 → 判定/翻面均无页面跳动。
    const ds = deckStat ? `<div class="deck-stat-bar">
            <span class="dsb-item">共 <b>${deckStat.total}</b></span>
            <span class="dsb-item is-new">新词 <b>${deckStat.newCount}</b></span>
            <span class="dsb-item is-learning">学习中 <b>${deckStat.learning}</b></span>
            <span class="dsb-item is-mastered">已掌握 <b>${deckStat.mastered}</b></span>
            <span class="dsb-item is-due">今日待复习 <b>${deckStat.dueToday}</b></span>
        </div>` : '';
    root.innerHTML = `
        ${ds}
        <div class="study-bar">
            <div class="sb-stat"><b>${done}</b> 已背</div>
            <div class="sb-stat"><b>${remain}</b> 剩余</div>
            <div class="sb-prog"><span style="width:${queue.length ? (cur / queue.length * 100) : 0}%"></span></div>
            <button class="sb-btn" onclick="undo()" ${history.length ? '' : 'disabled'} title="撤销上一次判定">↶ 回退</button>
            <button class="sb-btn" onclick="start(false)" title="重新开始本轮">⟳ 重开</button>
            <button class="sb-btn" onclick="editPlan()" title="设置每日新词量">📅 每日 ${getDailyPlan()}</button>
            <button class="sb-btn${getAutoWord() ? ' on' : ''}" id="btnAutoWord" onclick="toggleAutoWord()" title="卡片出现时自动读单词">🔊 自动读词</button>
            <button class="sb-btn${getAutoExample() ? ' on' : ''}" id="btnAutoExample" onclick="toggleAutoExample()" title="显示释义时自动读例句">📖 自动读例句</button>
            <button class="sb-btn" onclick="event.stopPropagation();toggleSettings()" title="设置快捷键与收藏目标">⚙ 设置</button>
        </div>
        <div class="flashcard" id="flashcard" onclick="onFlip()">
            <div class="fc-front">
                ${tag}
                <button class="fc-fav ${inTarget ? 'on' : ''}" onclick="event.stopPropagation();toggleFav()" title="收藏到「${esc(deckName(favTarget))}」">${inTarget ? '★' : '☆'}</button>
                <div class="fc-word">${esc(v.word)}</div>
                <div class="fc-phonetic">${esc(v.phonetic || '')}</div>
                <button class="fc-play" onclick="event.stopPropagation();speak('${wsafe}')" title="朗读">🔊 朗读</button>
            </div>
            <div class="fc-back" id="fcBack">
                <div class="fc-reveal-hint">点击卡片或按 <kbd>空格</kbd> 显示释义</div>
                <div class="fc-back-content" id="fcBackContent"><div class="loading">…</div></div>
            </div>
        </div>
        <div class="study-actions" id="studyActions">
            <button class="sa-btn reveal" onclick="event.stopPropagation();onFlip()">显示释义 <kbd>空格</kbd></button>
        </div>`;
    if (getAutoWord()) speak(v.word);              // 开关开启：卡片出现自动读单词
    // 异步填充背面例句（在预留区内，不影响卡片外高）
    const ex = await resolveExample(v);
    _curExampleEn = ex ? ex.en : '';               // 缓存供翻面自动读例句
    const c = document.getElementById('fcBackContent');
    if (c) {
        c.innerHTML = `
            <div class="fc-meaning">${renderMeaning(v.meaning)}</div>
            ${typeof freqBadge === 'function' ? freqBadge(v.word) : ''}
            ${ex ? `<div class="fc-example">
                <div class="fe-en">${highlightExample(ex.en, v.word)}</div>
                <div class="fe-cn">${esc(ex.cn)}</div>
            </div>` : ''}
            <div class="fc-src"><a href="article.html?id=${esc(v.article_id || '')}#${esc(v.sentence_id || '')}" target="_blank" onclick="event.stopPropagation()">查看原文语境 →</a></div>`;
    }
}

function onFlip() {
    const card = document.getElementById('flashcard');
    if (!card || cur >= queue.length) return;
    if (flipped) return;                 // 单向翻面：已显示释义后点击卡片不再收起，避免误触跳动
    flipped = true;
    card.classList.add('flipped');
    if (getAutoExample() && _curExampleEn) speak(_curExampleEn);   // 开关开启：显示释义时自动读例句
    const act = document.getElementById('studyActions');
    if (act) act.innerHTML = `
        <button class="sa-btn again" onclick="judge(false)">✕ 不认识 <kbd>←</kbd></button>
        <button class="sa-btn good" onclick="judge(true)">✓ 认识 <kbd>→</kbd></button>`;
}

async function judge(known) {
    if (cur >= queue.length) return;
    const v0 = queue[cur];
    // 判定前快照，供「回退」撤销误点：记录光标/进度/该词原 srs/是否被压回队尾
    history.push({
        cur, done, word: v0.word,
        prevSrs: v0.srs ? JSON.parse(JSON.stringify(v0.srs)) : undefined,
        pushedBack: !known
    });
    const v = grade(queue[cur], known);
    await dbPut('vocab', v);
    done++;
    if (!known) queue.push({ ...v });   // 不认识：本轮末尾再来一次
    cur++;
    saveSession();
    renderCard();
}

/** 回退：撤销最近一次判定，恢复该词记忆状态与本轮进度（防误点） */
async function undo() {
    if (!history.length) return;
    const h = history.pop();
    if (h.pushedBack && queue.length && queue[queue.length - 1].word === h.word) {
        queue.pop();                    // 撤掉「不认识」压回队尾的副本
    }
    cur = h.cur; done = h.done;
    const rec = (await dbGet('vocab', h.word)) || queue[cur];
    if (rec) {
        if (h.prevSrs === undefined) delete rec.srs; else rec.srs = h.prevSrs;
        await dbPut('vocab', rec);
        if (queue[cur] && queue[cur].word === h.word) queue[cur].srs = rec.srs;
    }
    saveSession();
    renderCard();
}

/** 收藏当前词 = 切换其在「收藏目标词书」的归属（复用 getActiveDeck，全站一致） */
async function toggleFav() {
    const v = queue[cur];
    if (!v) return;
    const target = getActiveDeck();
    const on = await toggleWordInDeck(v.word, target);
    const rec = await dbGet('vocab', v.word);
    if (rec) v.decks = rec.decks;      // 同步内存，回退/续存状态一致
    refreshFavBtn(on, target);
}

/** 就地刷新当前卡 ★ 按钮（on 省略时按当前词是否在目标词书重算） */
function refreshFavBtn(on, target) {
    const b = document.querySelector('.fc-fav');
    if (!b) return;
    target = target || getActiveDeck();
    if (on === undefined) {
        const v = queue[cur];
        on = !!(v && (Array.isArray(v.decks) ? v.decks : ['default']).includes(target));
    }
    b.classList.toggle('on', on);
    b.textContent = on ? '★' : '☆';
    b.title = '收藏到「' + deckName(target) + '」';
}

/** 设置每日新词量（每轮最多引入的新词数） */
function editPlan() {
    const s = prompt('每日新词量（每轮最多引入多少个新词）：', getDailyPlan());
    if (s === null) return;
    const n = parseInt(s, 10);
    if (!n || n < 1) { alert('请输入正整数'); return; }
    setDailyPlan(n);
    start(false);
}

function renderDone() {
    clearSession();
    document.getElementById('studyRoot').innerHTML = `<div class="study-empty">
        <div class="se-emoji">✅</div>
        <p>本轮完成，共判定 ${done} 次！</p>
        <p class="se-hint">认识的词已按记忆曲线拉长复习间隔，不认识的会明天再来。</p>
        <button class="se-btn" onclick="start(false)">再来一轮 →</button>
        <a class="se-btn ghost" href="vocab.html">回生词本</a></div>`;
}

// ============ 悬浮设置窗（自定义快捷键 + 收藏目标词书） ============
let bindingAction = null;   // 正在等待按键绑定的动作，null = 非绑定态

function buildSettingsPanel() {
    if (document.getElementById('studySettings')) return;
    const p = document.createElement('div');
    p.id = 'studySettings';
    p.hidden = true;
    p.addEventListener('click', e => e.stopPropagation());   // 面板内点击不冒泡触发外部关闭
    document.body.appendChild(p);
}

function toggleSettings() {
    buildSettingsPanel();
    const p = document.getElementById('studySettings');
    if (p.hidden) { renderSettings(); p.hidden = false; }
    else hideSettings();
}

function hideSettings() {
    const p = document.getElementById('studySettings');
    if (p && !p.hidden) { p.hidden = true; bindingAction = null; }
}

function renderSettings() {
    const p = document.getElementById('studySettings');
    if (!p) return;
    const km = getKeyMap();
    const rows = KEY_ACTIONS.map(([act, label]) => {
        const binding = bindingAction === act;
        return `<div class="ss-row"><span class="ss-act">${label}</span>
            <button class="ss-key${binding ? ' binding' : ''}" onclick="startBind('${act}')">${binding ? '按键…' : esc(keyLabel(km[act]))}</button></div>`;
    }).join('');
    const active = getActiveDeck();
    const opts = getDecks().map(d => `<option value="${esc(d.id)}"${d.id === active ? ' selected' : ''}>${esc(d.name)}</option>`).join('');
    p.innerHTML = `
        <div class="ss-title">快捷键 <span class="ss-tip">点键位后按下新键</span></div>
        ${rows}
        <button class="ss-reset" onclick="resetKeys()">恢复默认</button>
        <div class="ss-title">收藏目标词书</div>
        <div class="ss-target"><select onchange="onSettingsTarget(this.value)">${opts}</select></div>`;
}

function startBind(act) { bindingAction = act; renderSettings(); }
function resetKeys() { setKeyMap({ ...DEFAULT_KEYS }); bindingAction = null; renderSettings(); }
function onSettingsTarget(id) { setActiveDeck(id); renderSettings(); refreshFavBtn(); }

// ============ 键盘快捷键（可在设置窗自定义） ============
document.addEventListener('keydown', (e) => {
    // 绑定态：独占下一次按键写入 keymap（Esc 取消，重复键位拒绝）
    if (bindingAction) {
        e.preventDefault();
        if (e.code === 'Escape') { bindingAction = null; renderSettings(); return; }
        const km = getKeyMap();
        const dup = KEY_ACTIONS.find(([a]) => a !== bindingAction && km[a] === e.code);
        if (dup) { alert('「' + keyLabel(e.code) + '」已绑定给「' + dup[1] + '」，请换一个键'); return; }
        km[bindingAction] = e.code;
        setKeyMap(km);
        bindingAction = null;
        renderSettings();
        return;
    }
    // 输入框/下拉框内不拦截
    const t = e.target;
    if (t && /^(INPUT|SELECT|TEXTAREA)$/.test(t.tagName)) return;
    if (e.code === 'Escape') { hideSettings(); return; }   // Esc 关闭设置窗
    const km = getKeyMap();
    const active = queue.length && cur < queue.length;      // 做题动作需有队列
    if (km.undo === e.code) { if (active) { e.preventDefault(); undo(); } return; }
    if (km.fav === e.code) { if (active) { e.preventDefault(); toggleFav(); } return; }
    if (!active) return;
    if (!flipped) {
        if (km.flip === e.code) { e.preventDefault(); onFlip(); }
    } else {
        if (km.unknown === e.code) { e.preventDefault(); judge(false); }
        else if (km.known === e.code) { e.preventDefault(); judge(true); }
    }
});

// 点击面板外或滚动时收起设置窗
document.addEventListener('click', () => hideSettings());
window.addEventListener('scroll', () => hideSettings(), { passive: true });

// ============ 初始化 ============
async function init() {
    await migrateVocabDecks();
    if (typeof loadFreq === 'function') { try { await loadFreq(); } catch (e) { /* 徽标降级 */ } }
    // 若来自单词本「背这本 →」，URL 带 deck 参数则切换背词范围
    const qDeck = new URLSearchParams(location.search).get('deck');
    if (qDeck && (qDeck === '__all__' || getDeck(qDeck))) { setStudyDeck(qDeck); clearSession(); }
    await renderDeckBar();
    if (await resumeSession()) return;   // 有未完成本轮先续存
    await start(false);
}

init();
