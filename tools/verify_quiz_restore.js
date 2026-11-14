/* 做题记录恢复链回归（article.js init 的后台数据段）：
 * 修复前：答题记录在链前段已读进 answerMap，但要等 dict.json/phrases.json 等约 3.5MB 大 JSON
 *   全部洗完，链尾 enrichRender() 才渲染；且整条链一个 try，后段任一步抛错，记录永远不显示，
 *   做题面板停在「未作答」（慢或不出两种症状）。主页直查库无此链，所以主页一直正常。
 * 修复后：① 本地用户数据段读完立刻 renderQuiz()；② 词典等大资源独立 try，失败只降级高亮。
 *
 * 场景 A：loadDict/loadPhrases/loadFreq/loadHardwords 永远 pending（模拟慢网大文件）
 *   → 做题记录必须已渲染（不被大资源拖住）。
 * 场景 B：四个重资源加载器全部 reject（模拟失败）
 *   → 做题记录必须仍在，且不弹「本地数据读取失败」的误导 toast。
 *
 * 用法: node tools/verify_quiz_restore.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const PWA = path.join(ROOT, 'pwa');
const AID = '2022_text1';

const yearData = JSON.parse(fs.readFileSync(path.join(PWA, 'data', '2022.json'), 'utf8'));
const art = (yearData.articles || []).find(a => a.id === AID);
if (!art || !(art.questions || []).length) {
    console.log('FAIL: 2022_text1 无私题库数据，无法造答题记录');
    process.exit(1);
}
const QIDS = art.questions.map(q => q.id);
// 假 IndexedDB：本篇全部题目都有一笔「全对」记录
const ANSWERS = art.questions.map(q => ({
    question_id: q.id, article_id: AID, user_answer: q.answer, is_correct: 1, answered_at: 0,
}));

function makeDom() {
    const html = fs.readFileSync(path.join(PWA, 'article.html'), 'utf8');
    const dom = new JSDOM(html, {
        url: 'http://localhost/article.html?id=' + AID,
        runScripts: 'outside-only', pretendToBeVisual: true,
    });
    const w = dom.window;
    w.fetch = (p) => Promise.resolve({
        ok: true,
        json: () => Promise.resolve(JSON.parse(fs.readFileSync(path.join(PWA, p), 'utf8'))),
        text: () => Promise.resolve(fs.readFileSync(path.join(PWA, p), 'utf8')),
    });
    const inline = [...w.document.querySelectorAll('script:not([src])')].map(s => s.textContent).join('\n;\n');
    const libs = ['common.js', 'storage.js', 'dict.js', 'annotate.js', 'article.js']
        .map(f => fs.readFileSync(path.join(PWA, 'js', f), 'utf8')).join('\n;\n');
    w.eval(libs + '\n;\n' + inline);   // init() 在此同步启动，停在第一个 await

    // jsdom 没有 IndexedDB：整层桩掉（init 与后续落库都走这些函数）
    w.dbAll = async (store) => (store === 'quiz_answers') ? ANSWERS.slice() : [];
    w.dbGet = async () => null;
    w.dbPut = async () => undefined;
    w.dbPutMany = async () => undefined;
    w.dbDelete = async () => undefined;
    w.getArtNote = async () => '';
    w.saveArtNote = async () => true;
    w.confirm = () => true;
    w.alert = () => {};
    w.scrollTo = () => {};
    w.toast = (m) => { (w.__toasts = w.__toasts || []).push(m); };
    w.__toasts = [];
    return dom;
}

// 重资源加载器覆盖（init 已启动但第二段还没跑到，此刻替换生效）
const HANG = `
    window.loadDict = () => new Promise(() => {});
    window.loadPhrases = () => new Promise(() => {});
    window.loadFreq = () => new Promise(() => {});
    window.loadHardwords = () => new Promise(() => {});
`;
const REJECT = `
    window.loadDict = () => Promise.reject(new Error('模拟慢网失败'));
    window.loadPhrases = () => Promise.reject(new Error('模拟慢网失败'));
    window.loadFreq = () => Promise.reject(new Error('模拟慢网失败'));
    window.loadHardwords = () => Promise.reject(new Error('模拟慢网失败'));
`;

const problems = [];
const sleep = ms => new Promise(r => setTimeout(r, ms));

/** 记录是否已渲染：跳题条 answered-right 数 + 正确选项是否标了 right 类 */
function snapshot(w) {
    const d = w.document;
    const bars = d.querySelectorAll('.qj-btn.answered-right').length;
    const opts = QIDS.filter(id => {
        const a = ANSWERS.find(x => x.question_id === id);
        const el = d.getElementById('opt-' + id + '-' + a.user_answer);
        return el && el.classList.contains('right');
    }).length;
    return { bars, opts };
}

async function scenario(name, stubSrc) {
    const dom = makeDom();
    const w = dom.window;
    w.eval(stubSrc);
    // 等正文渲染 + 本地用户数据段跑完（给足时间；大资源段被桩住，不可能更晚补上记录）
    for (let i = 0; i < 40 && !w.document.querySelector('.qj-btn'); i++) await sleep(50);
    await sleep(400);
    const s = snapshot(w);
    if (s.bars !== QIDS.length) problems.push(`${name}：跳题条已对徽标 ${s.bars}/${QIDS.length}（记录未渲染）`);
    if (s.opts !== QIDS.length) problems.push(`${name}：正确选项已标色 ${s.opts}/${QIDS.length}（记录未恢复）`);
    if ((w.__toasts || []).some(t => /本地数据读取失败/.test(t))) {
        problems.push(`${name}：误弹「本地数据读取失败」toast（大资源失败不该冒报到记录链路）`);
    }
    return s;
}

(async () => {
    const a = await scenario('场景A 大资源永远 pending', HANG);
    const b = await scenario('场景B 大资源全部 reject', REJECT);
    if (problems.length) {
        console.log('FAIL ' + problems.length + ' 处:');
        problems.forEach(p => console.log('  - ' + p));
        process.exit(1);
    }
    console.log(`QUIZ RESTORE OK：场景A 徽标${a.bars}/${QIDS.length} 选项${a.opts}/${QIDS.length} · ` +
        `场景B 徽标${b.bars}/${QIDS.length} 选项${b.opts}/${QIDS.length} · ` +
        '记录不被词典/词组大 JSON 拖延，也不被其失败带崩');
    process.exit(0);
})().catch(e => { console.log('ERROR', e.stack.split('\n').slice(0, 3).join('\n')); process.exit(1); });
