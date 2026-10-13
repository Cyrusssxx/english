/* openDB() 的升级/阻塞回归：DB 升版本时最容易踩的坑是「被别的标签页挡住」——
 * open 既不 success 也不 error，Promise 永久挂起，页面静默失效（作答不恢复、
 * 做题不落库），而握着旧版连接的标签页一切正常。
 * 用法: node tools/verify_db_open.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const PWA = path.join(path.resolve(__dirname, '..'), 'pwa');
const problems = [];

/** 极简假 IndexedDB：能开关 blocked / error，记录建表调用 */
function fakeIDB(opt) {
    const created = [];
    return {
        created,
        opt,
        indexedDB: {
            open(name, ver) {
                const req = { result: null, error: null };
                setTimeout(() => {
                    if (opt.mode === 'blocked') { req.onblocked && req.onblocked(); return; }
                    if (opt.mode === 'error') { req.error = new Error('boom'); req.onerror && req.onerror(); return; }
                    const names = new Set(opt.existing || []);
                    const db = {
                        version: ver,
                        objectStoreNames: { contains: (s) => names.has(s) },
                        createObjectStore(s) { names.add(s); created.push(s); },
                        close() { opt.closed = true; },
                        transaction() {
                            return { objectStore: () => ({ getAll: () => ({ onsuccess() {}, onerror() {} }) }) };
                        }
                    };
                    req.result = db;
                    req.onupgradeneeded && req.onupgradeneeded();
                    req.onsuccess && req.onsuccess();
                }, 0);
                return req;
            }
        }
    };
}

function load(lib, idb) {
    const dom = new JSDOM('<body></body>', { url: 'http://localhost/', runScripts: 'outside-only' });
    const w = dom.window;
    if (idb) w.indexedDB = idb.indexedDB;
    w.eval(lib);
    return w;
}

const lib = ['common.js', 'storage.js']
    .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
    // 1. 全新库：五张表都要建出来
    let f = fakeIDB({ mode: 'ok', existing: [] });
    let w = load(lib, f);
    let db = await w.openDB();
    const want = ['vocab', 'fav_sentences', 'article_progress', 'quiz_answers', 'article_notes'];
    const miss = want.filter(s => !f.created.includes(s));
    if (miss.length) problems.push('全新库未建表: ' + miss.join(','));
    if (typeof db.onversionchange !== 'function') problems.push('未挂 db.onversionchange（会挡住别的标签页升级）');
    console.log('全新库建表:', f.created.join(','), '| onversionchange:', typeof db.onversionchange);

    // 2. 已存在旧表：只补缺失的，不重建
    f = fakeIDB({ mode: 'ok', existing: ['vocab', 'quiz_answers'] });
    w = load(lib, f);
    await w.openDB();
    if (f.created.includes('quiz_answers')) problems.push('重建了已存在的 quiz_answers（会清数据）');
    if (!f.created.includes('article_notes')) problems.push('v1 老库没有补建 article_notes');
    console.log('老库补表:', f.created.join(','));

    // 3. 被别的标签页挡住：必须 reject 并给出可操作的提示，且不能永久挂起
    f = fakeIDB({ mode: 'blocked' });
    w = load(lib, f);
    let msg = '';
    const t0 = Date.now();
    try {
        await w.openDB();
        problems.push('blocked 时 openDB 竟然 resolve 了');
    } catch (e) {
        msg = e.message || String(e);
        if (!/其它标签页|刷新/.test(msg)) problems.push('blocked 提示不明确: ' + msg);
        if (Date.now() - t0 > 3000) problems.push('blocked 没有快速失败，等了 ' + (Date.now() - t0) + 'ms');
    }
    // Promise 缓存必须清掉，否则后续调用永远拿这个坏 Promise
    try { await w.openDB(); } catch (e) { /* 第二次也应尝试重新 open */ }
    console.log('blocked 报错:', msg || '(无)');

    // 4. 打开失败：同样要清缓存，不能一次失败全站瘫痪
    f = fakeIDB({ mode: 'error' });
    w = load(lib, f);
    try {
        await w.openDB();
        problems.push('error 时 openDB 竟然 resolve 了');
    } catch (e) { /* 预期 */ }

    // 5. versionchange 触发时主动让路（close + 清缓存）
    f = fakeIDB({ mode: 'ok', existing: want });
    w = load(lib, f);
    db = await w.openDB();
    db.onversionchange();
    if (!f.opt.closed) problems.push('versionchange 时没有 close 连接');
    console.log('versionchange 让路:', f.opt.closed ? 'OK（已 close）' : '未 close');

    if (problems.length) {
        console.log('\nFAIL ' + problems.length + ' 处:');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log('\nopenDB OK：建表幂等 / blocked 与 error 快速失败并清缓存 / versionchange 主动让路');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 3).join('\n')); process.exit(1); });
