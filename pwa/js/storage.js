/* 英语二精翻 PWA - 存储层：题库加载（内存缓存） + IndexedDB（生词本/句子收藏/进度/答题记录）
 * 改自 408 刷题 backend.js 的 openDB + dbAll/dbGet/dbPut/dbDelete 四件套。
 */

// ==================== 题库加载（内存缓存） ====================
const _yearCache = {};   // {year: data}
let _indexCache = null;  // index.json

async function loadIndex() {
    if (_indexCache) return _indexCache;
    const resp = await fetch('data/index.json');
    if (!resp.ok) throw new Error('加载目录失败: ' + resp.status);
    _indexCache = await resp.json();
    return _indexCache;
}

async function loadYear(year) {
    if (_yearCache[year]) return _yearCache[year];
    const resp = await fetch(`data/${year}.json`);
    if (!resp.ok) throw new Error(`加载 ${year} 年题库失败: ` + resp.status);
    const data = await resp.json();
    _yearCache[year] = data;
    return data;
}

/** 文章 id 形如 2022_text1，前4位即年份；en1_ 前缀走英语一独立目录 */
async function getArticle(aid) {
    if (typeof aid === 'string' && aid.startsWith('en1_')) {
        const m = /^en1_(\d{4})_/.exec(aid);
        const year = m ? m[1] : aid.slice(4, 8);
        return getEn1Article(year, aid);
    }
    const year = parseInt(aid.slice(0, 4), 10);
    if (!year) return null;
    const data = await loadYear(year);
    return (data.articles || []).find(a => a.id === aid) || null;
}

// ==================== 英语一（EN1）题库：独立目录 data/en1/${year}.json ====================
const _en1YearCache = {};   // {year: data}
let _en1IndexCache = null;  // en1_index.json

async function loadEn1Year(year) {
    if (_en1YearCache[year]) return _en1YearCache[year];
    const resp = await fetch(`data/en1/${year}.json`);
    if (!resp.ok) throw new Error(`加载英语一 ${year} 年题库失败: ` + resp.status);
    const data = await resp.json();
    _en1YearCache[year] = data;
    return data;
}

async function getEn1Article(year, aid) {
    try {
        const data = await loadEn1Year(year);
        return (data.articles || []).find(a => a.id === aid) || null;
    } catch (e) {
        console.warn(e);
        return null;
    }
}

async function loadEn1Index() {
    if (_en1IndexCache) return _en1IndexCache;
    const resp = await fetch('data/en1_index.json');
    if (!resp.ok) throw new Error('加载英语一目录失败: ' + resp.status);
    _en1IndexCache = await resp.json();
    return _en1IndexCache;
}

// 文章类型显示名
const TYPE_NAMES = {
    text1: '阅读 Text1', text2: '阅读 Text2', text3: '阅读 Text3', text4: '阅读 Text4',
    cloze: '完形填空', newtype: '新题型',
    translation: '翻译', writing_a: '写作 PartA', writing_b: '写作 PartB'
};

// ==================== IndexedDB ====================
const DB_NAME = 'english2';
const DB_VER = 1;
let _dbPromise = null;

function openDB() {
    if (_dbPromise) return _dbPromise;
    _dbPromise = new Promise((resolve, reject) => {
        const req = indexedDB.open(DB_NAME, DB_VER);
        req.onupgradeneeded = () => {
            const db = req.result;
            // 幂等建库：只新增缺失的 store，不动老数据
            if (!db.objectStoreNames.contains('vocab')) {
                db.createObjectStore('vocab', { keyPath: 'word' });
            }
            if (!db.objectStoreNames.contains('fav_sentences')) {
                db.createObjectStore('fav_sentences', { keyPath: 'sentence_id' });
            }
            if (!db.objectStoreNames.contains('article_progress')) {
                db.createObjectStore('article_progress', { keyPath: 'article_id' });
            }
            if (!db.objectStoreNames.contains('quiz_answers')) {
                db.createObjectStore('quiz_answers', { keyPath: 'question_id' });
            }
        };
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => reject(req.error);
    });
    return _dbPromise;
}

// Promise 化的通用读写
async function dbAll(store) {
    const db = await openDB();
    return new Promise((res, rej) => {
        const r = db.transaction(store).objectStore(store).getAll();
        r.onsuccess = () => res(r.result);
        r.onerror = () => rej(r.error);
    });
}

async function dbGet(store, key) {
    const db = await openDB();
    return new Promise((res, rej) => {
        const r = db.transaction(store).objectStore(store).get(key);
        r.onsuccess = () => res(r.result);
        r.onerror = () => rej(r.error);
    });
}

async function dbPut(store, val) {
    const db = await openDB();
    return new Promise((res, rej) => {
        const tx = db.transaction(store, 'readwrite');
        const r = tx.objectStore(store).put(val);
        r.onsuccess = () => res(r.result);
        tx.onerror = () => rej(tx.error);
    });
}

async function dbDelete(store, key) {
    const db = await openDB();
    return new Promise((res, rej) => {
        const tx = db.transaction(store, 'readwrite');
        tx.objectStore(store).delete(key);
        tx.oncomplete = () => res();
        tx.onerror = () => rej(tx.error);
    });
}

/** 单事务批量写（一次性 put 多个记录），避免逐条 await dbPut 造成的"事务洪水" */
async function dbPutMany(store, vals) {
    if (!vals || !vals.length) return;
    const db = await openDB();
    await new Promise((res, rej) => {
        const tx = db.transaction(store, 'readwrite');
        const os = tx.objectStore(store);
        for (const v of vals) os.put(v);
        tx.oncomplete = res;
        tx.onerror = () => rej(tx.error);
    });
}

function now() {
    const d = new Date(), p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

/** 全局自增序号：保证加入顺序稳定（added_at 秒级相同会乱序），存 localStorage */
function nextSeq() {
    const v = (parseInt(localStorage.getItem('en2_vocabSeq') || '0', 10) || 0) + 1;
    localStorage.setItem('en2_vocabSeq', String(v));
    return v;
}

// ==================== 词书（多词书系统） ====================
// 词书元数据存 localStorage；词-词书归属存 vocab 记录的 decks 数组（随备份导出）。
const DEFAULT_DECK_ID = 'default';
const ALL_DECKS = '__all__';

/** 读取词书列表（始终保证内置「我的生词本」存在且置顶） */
function getDecks() {
    let list;
    try { list = JSON.parse(localStorage.getItem('en2_decks') || 'null'); } catch (e) { list = null; }
    if (!Array.isArray(list)) list = [];
    if (!list.some(d => d.id === DEFAULT_DECK_ID)) {
        list.unshift({ id: DEFAULT_DECK_ID, name: '我的生词本', builtin: true, order: 0, created_at: now() });
    }
    return list;
}
function saveDecks(list) { localStorage.setItem('en2_decks', JSON.stringify(list)); }
function ensureDefaultDeck() { saveDecks(getDecks()); }
function getDeck(id) { return getDecks().find(d => d.id === id) || null; }
function deckName(id) { const d = getDeck(id); return d ? d.name : '未知词书'; }

/** 当前收藏/记录目标词书 id（默认内置词书） */
function getActiveDeck() {
    const id = localStorage.getItem('en2_activeDeck') || DEFAULT_DECK_ID;
    return getDeck(id) ? id : DEFAULT_DECK_ID;
}
function setActiveDeck(id) { localStorage.setItem('en2_activeDeck', id); }

/** 背单词过滤的词书 id（默认全部） */
function getStudyDeck() {
    const id = localStorage.getItem('en2_studyDeck') || ALL_DECKS;
    return (id === ALL_DECKS || getDeck(id)) ? id : ALL_DECKS;
}
function setStudyDeck(id) { localStorage.setItem('en2_studyDeck', id); }

/** 精翻点词「加入生词本」的目标词书：背词范围指定了具体词书就用它，否则用收藏目标词书 */
function getVocabTarget() {
    const study = getStudyDeck();
    return study === ALL_DECKS ? getActiveDeck() : study;
}

/** 新建词书，返回新 id */
function createDeck(name) {
    name = String(name || '').trim();
    if (!name) return null;
    const list = getDecks();
    const id = 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);
    list.push({ id, name, builtin: false, order: list.length, created_at: now() });
    saveDecks(list);
    return id;
}
function renameDeck(id, name) {
    name = String(name || '').trim();
    if (!name) return;
    const list = getDecks();
    const d = list.find(x => x.id === id);
    if (d) { d.name = name; saveDecks(list); }
}

/** 确保一个固定 id 的内置词书存在（已存则直接返回；可删、重导幂等），返回该 id。 */
function ensureDeck(id, name) {
    const list = getDecks();
    if (!list.some(d => d.id === id)) {
        list.push({ id, name, builtin: false, order: list.length, created_at: now() });
        saveDecks(list);
    }
    return id;
}
/** 删除词书（内置禁删）：从所有 vocab.decks 移除该 id，空记录随之删除 */
async function deleteDeck(id) {
    if (id === DEFAULT_DECK_ID) return;
    saveDecks(getDecks().filter(d => d.id !== id));
    for (const v of await dbAll('vocab')) {
        const decks = Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID];
        if (!decks.includes(id)) continue;
        const nd = decks.filter(x => x !== id);
        if (nd.length) { v.decks = nd; await dbPut('vocab', v); }
        else await dbDelete('vocab', v.word);
    }
    if (getActiveDeck() === id) setActiveDeck(DEFAULT_DECK_ID);
    if (getStudyDeck() === id) setStudyDeck(ALL_DECKS);
}

/** 一次性迁移：给历史无 decks 字段的生词补 ['default']（带完成标记）。
 *  每个迁移用 dbPutMany 单事务批量写，几百上千词也只开一次事务，不再洪水式逐条写。 */
async function migrateVocabDecks() {
    ensureDefaultDeck();
    // 1) 历史无 decks 字段 → 补 ['default']
    if (localStorage.getItem('en2_decksMigrated') !== '1') {
        const all = await dbAll('vocab');
        const changed = all
            .filter(v => !Array.isArray(v.decks) || !v.decks.length)
            .map(v => ({ ...v, decks: [DEFAULT_DECK_ID] }));
        if (changed.length) await dbPutMany('vocab', changed);
        localStorage.setItem('en2_decksMigrated', '1');
    }
    // 2) fav 星标并入当前收藏词书（单事务）
    if (localStorage.getItem('en2_favMigrated') !== '1') {
        const target = getActiveDeck();
        const all = await dbAll('vocab');
        const changed = [];
        for (const v of all) {
            if (!v.fav) continue;
            const decks = new Set(Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID]);
            decks.add(target);
            const nv = { ...v, decks: [...decks] };
            delete nv.fav;
            changed.push(nv);
        }
        if (changed.length) await dbPutMany('vocab', changed);
        localStorage.setItem('en2_favMigrated', '1');
    }
    // 3) 补齐 seq（按来源顺序重排，单事务一次写）
    if (localStorage.getItem('en2_seqMigrated') !== '2') {
        const all = (await dbAll('vocab'));
        const key = v => {
            const aid = v.article_id || '';
            const m = /_s(\d+)$/.exec(v.sentence_id || '');
            if (!aid) return 'zzzzzz_' + (v.added_at || '');
            return aid + '_' + (m ? String(m[1]).padStart(5, '0') : '');
        };
        all.sort((a, b) => key(a).localeCompare(key(b)) || (a.added_at || '').localeCompare(b.added_at || ''));
        const changed = all.map(v => ({ ...v, seq: nextSeq() }));
        await dbPutMany('vocab', changed);
        localStorage.setItem('en2_seqMigrated', '2');
    }
}

// ==================== 业务操作 ====================

/** 生词本：加词（word 已存在则更新释义并并入词书；保留已有复习状态 srs） */
async function addVocab(word, meaning, phonetic, sentenceId, articleId, exampleEn, exampleCn, deckId) {
    deckId = deckId || getActiveDeck();
    const old = await dbGet('vocab', word);
    const decks = new Set(Array.isArray(old && old.decks) ? old.decks : (old ? [DEFAULT_DECK_ID] : []));
    decks.add(deckId);
    await dbPut('vocab', {
        word, meaning, phonetic: phonetic || '',
        sentence_id: sentenceId, article_id: articleId,
        example_en: exampleEn || (old && old.example_en) || '',
        example_cn: exampleCn || (old && old.example_cn) || '',
        srs: old && old.srs ? old.srs : undefined,
        decks: [...decks],
        seq: (old && old.seq) || nextSeq(),
        added_at: (old && old.added_at) || now()
    });
}

/** 批量加词到某词书（单事务）：已存在只并入词书、不覆盖释义/srs。返回新增到该词书的数量 */
async function addWordsBulk(items, deckId) {
    deckId = deckId || getActiveDeck();
    const db = await openDB();
    const existing = {};
    (await dbAll('vocab')).forEach(v => { existing[v.word] = v; });
    const puts = [];
    let added = 0;
    for (const it of items) {
        const word = it.word;
        if (!word) continue;
        const old = existing[word];
        if (old) {
            const decks = new Set(Array.isArray(old.decks) ? old.decks : [DEFAULT_DECK_ID]);
            if (!decks.has(deckId)) { decks.add(deckId); old.decks = [...decks]; puts.push(old); added++; }
        } else {
            puts.push({
                word, meaning: it.meaning || '', phonetic: it.phonetic || '',
                sentence_id: it.sentence_id || '', article_id: it.article_id || '',
                example_en: it.example_en || '', example_cn: it.example_cn || '',
                srs: undefined, decks: [deckId], seq: nextSeq(), added_at: now()
            });
            added++;
        }
    }
    await new Promise((res, rej) => {
        const tx = db.transaction('vocab', 'readwrite');
        for (const p of puts) tx.objectStore('vocab').put(p);
        tx.oncomplete = res; tx.onerror = () => rej(tx.error);
    });
    return added;
}

/** 从某词书移出该词；decks 空则删除整条记录 */
async function removeVocabFromDeck(word, deckId) {
    const v = await dbGet('vocab', word);
    if (!v) return;
    const decks = (Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID]).filter(x => x !== deckId);
    if (decks.length) { v.decks = decks; await dbPut('vocab', v); }
    else await dbDelete('vocab', word);
}

/** 切换某词在指定词书的归属，返回切换后是否在该书。
 *  移除到空时回退到内置词书，绝不删除记录（避免背词途中单词凭空消失）。 */
async function toggleWordInDeck(word, deckId) {
    const v = await dbGet('vocab', word);
    if (!v) return false;
    const decks = new Set(Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID]);
    if (decks.has(deckId)) {
        decks.delete(deckId);
        if (decks.size === 0) decks.add(DEFAULT_DECK_ID);
        v.decks = [...decks]; await dbPut('vocab', v); return false;
    }
    decks.add(deckId); v.decks = [...decks]; await dbPut('vocab', v); return true;
}

/** 取某词书的生词（__all__ 返回全部；缺省 decks 视为 default） */
async function vocabByDeck(deckId) {
    const all = await dbAll('vocab');
    if (!deckId || deckId === ALL_DECKS) return all;
    return all.filter(v => (Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID]).includes(deckId));
}

/** 各词书生词计数：{__all__:n, deckId:n, ...} */
async function deckCounts() {
    const counts = { [ALL_DECKS]: 0 };
    for (const v of await dbAll('vocab')) {
        counts[ALL_DECKS]++;
        const decks = Array.isArray(v.decks) ? v.decks : [DEFAULT_DECK_ID];
        for (const id of decks) counts[id] = (counts[id] || 0) + 1;
    }
    return counts;
}

/** 某词书学习统计（基于 vocab.srs）：
 *  total 总数 / newCount 未学 / learning 学习中 / mastered 已掌握(interval≥21天) / dueToday 今日待复习 */
async function deckStats(deckId) {
    const all = await vocabByDeck(deckId);
    const today = new Date().toISOString().slice(0, 10);
    let newCount = 0, learning = 0, mastered = 0, dueToday = 0;
    for (const v of all) {
        const s = v.srs;
        if (!s) { newCount++; continue; }
        if ((s.interval || 0) >= 21) mastered++; else learning++;
        if (s.due && s.due <= today) dueToday++;
    }
    return { total: all.length, newCount, learning, mastered, dueToday };
}

/** 句子收藏切换，返回收藏后状态 */
async function toggleFavSentence(sent, articleId) {
    const existing = await dbGet('fav_sentences', sent.id);
    if (existing) {
        await dbDelete('fav_sentences', sent.id);
        return false;
    }
    await dbPut('fav_sentences', { sentence_id: sent.id, article_id: articleId, en: sent.en, cn: sent.cn, added_at: now() });
    return true;
}

/** 学习进度：记录文章内最后停留的句子 */
async function saveProgress(articleId, sentenceId) {
    await dbPut('article_progress', { article_id: articleId, last_sentence_id: sentenceId, updated_at: now() });
}

/** 答题记录 */
async function saveAnswer(questionId, articleId, userAnswer, isCorrect) {
    await dbPut('quiz_answers', { question_id: questionId, article_id: articleId, user_answer: userAnswer, is_correct: isCorrect ? 1 : 0, answered_at: now() });
}

/** 清空某篇文章的全部作答记录 */
async function clearAnswers(articleId) {
    const all = await dbAll('quiz_answers');
    for (const a of all) {
        if (a.article_id === articleId) await dbDelete('quiz_answers', a.question_id);
    }
}

// ==================== 数据备份：导出 / 导入 ====================
async function backupExport() {
    const payload = {
        version: 1, exported_at: now(), source: 'english-reading',
        vocab: await dbAll('vocab'),
        fav_sentences: await dbAll('fav_sentences'),
        article_progress: await dbAll('article_progress'),
        quiz_answers: await dbAll('quiz_answers'),
        decks: getDecks(),
        active_deck: getActiveDeck()
    };
    const blob = new Blob([JSON.stringify(payload, null, 1)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '英二精翻备份-' + new Date().toISOString().slice(0, 10) + '.json';
    a.click();
    URL.revokeObjectURL(a.href);
}

async function backupImport(input) {
    const f = input.files && input.files[0];
    if (!f) return;
    const rd = new FileReader();
    rd.onload = async () => {
        try {
            const body = JSON.parse(rd.result);
            if (!Array.isArray(body.vocab)) throw new Error('备份文件格式不正确');
            const db = await openDB();
            for (const store of ['vocab', 'fav_sentences', 'article_progress', 'quiz_answers']) {
                const rows = Array.isArray(body[store]) ? body[store] : [];
                await new Promise((res, rej) => {
                    const tx = db.transaction(store, 'readwrite');
                    tx.objectStore(store).clear();
                    for (const r of rows) tx.objectStore(store).put(r);
                    tx.oncomplete = res; tx.onerror = () => rej(tx.error);
                });
            }
            // 词书元数据（localStorage）一并还原；清除迁移标记以便下次加载补齐缺失的 decks
            if (Array.isArray(body.decks)) localStorage.setItem('en2_decks', JSON.stringify(body.decks));
            if (body.active_deck) localStorage.setItem('en2_activeDeck', body.active_deck);
            localStorage.removeItem('en2_decksMigrated');
            toast('导入成功，即将刷新…');
            setTimeout(() => location.reload(), 1000);
        } catch (e) {
            toast('导入失败: ' + e.message);
        }
        input.value = '';
    };
    rd.readAsText(f);
}

// ==================== Service Worker 注册 ====================
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').catch(e => console.warn('SW注册失败（file:// 下属正常，请用 start.bat 启动）', e));
    });
}
