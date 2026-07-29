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

/** 文章 id 形如 2022_text1，前4位即年份 */
async function getArticle(aid) {
    const year = parseInt(aid.slice(0, 4), 10);
    if (!year) return null;
    const data = await loadYear(year);
    return (data.articles || []).find(a => a.id === aid) || null;
}

// 文章类型显示名
const TYPE_NAMES = {
    text1: '阅读 Text1', text2: '阅读 Text2', text3: '阅读 Text3', text4: '阅读 Text4',
    cloze: '完形填空', newtype: '新题型'
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

function now() {
    const d = new Date(), p = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`;
}

// ==================== 业务操作 ====================

/** 生词本：加词（word 已存在则覆盖；保留已有的复习状态 srs） */
async function addVocab(word, meaning, phonetic, sentenceId, articleId, exampleEn, exampleCn) {
    const old = await dbGet('vocab', word);
    await dbPut('vocab', {
        word, meaning, phonetic: phonetic || '',
        sentence_id: sentenceId, article_id: articleId,
        example_en: exampleEn || (old && old.example_en) || '',
        example_cn: exampleCn || (old && old.example_cn) || '',
        srs: old && old.srs ? old.srs : undefined,
        added_at: (old && old.added_at) || now()
    });
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

// ==================== 数据备份：导出 / 导入 ====================
async function backupExport() {
    const payload = {
        version: 1, exported_at: now(), source: 'english-reading',
        vocab: await dbAll('vocab'),
        fav_sentences: await dbAll('fav_sentences'),
        article_progress: await dbAll('article_progress'),
        quiz_answers: await dbAll('quiz_answers')
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
            alert('导入成功，页面即将刷新');
            location.reload();
        } catch (e) {
            alert('导入失败: ' + e.message);
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
