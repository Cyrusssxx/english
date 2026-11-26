/* 临时扫描：范文/模板里点开查不到释义的词（2026-11-27）
   跑法：NODE_PATH=E:/deps_cache/jsdom-test/node_modules node tools/_scan_missing_trans.js */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('E:/deps_cache/jsdom-test/node_modules/jsdom');
const P = 'D:/ai code/english-reading/';

const dom = new JSDOM('', { runScripts: 'outside-only', url: 'http://localhost/' });
const w = dom.window;
const dictRaw = fs.readFileSync(P + 'pwa/data/dict.json', 'utf8');
w.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(dictRaw)) });
w.eval(fs.readFileSync(P + 'pwa/js/dict.js', 'utf8'));

(async () => {
    await w.loadDict();
    const lookup = w.dictLookup;
    const WORD = /[A-Za-z][A-Za-z'\-]*/g;
    const missing = new Map();   // word -> {n, where:Set}

    const scan = (text, where) => {
        if (!text || typeof text !== 'string') return;
        let m;
        while ((m = WORD.exec(text)) !== null) {
            const word = m[0];
            if (!lookup(word)) {
                const key = word.toLowerCase();
                if (!missing.has(key)) missing.set(key, { n: 0, where: new Set() });
                const e = missing.get(key);
                e.n++;
                if (e.where.size < 5) e.where.add(where);
            }
        }
    };

    const yati = JSON.parse(fs.readFileSync(P + 'pwa/data/yati.json', 'utf8'));
    yati.groups.forEach(g => (g.items || []).forEach(it => {
        const tag = 'NO' + it.no + ' ' + it.title;
        (it.blocks || []).forEach(b => {
            scan(b.v || '', tag);
            (b.sents || []).forEach(s => { scan(s.en || '', tag); });
        });
        scan(it.en || '', tag);
    }));

    const tpl = JSON.parse(fs.readFileSync(P + 'pwa/data/writing_templates.json', 'utf8'));
    (tpl.sections || []).forEach(sec => {
        const tag = 'TPL ' + sec.id;
        (sec.sentences || []).forEach(s => { scan(s.en || '', tag); });
        (sec.skeletons || []).forEach(s => {
            scan(s.en || s.text || '', tag);
            (s.sents || []).forEach(x => scan(typeof x === 'string' ? x : (x.en || ''), tag));
            (s.sents_alt || []).forEach(x => scan(typeof x === 'string' ? x : (x.en || ''), tag));
        });
        (sec.framework || []).forEach(f => scan(f.en || f.text || '', tag));
        (sec.linkers || []).forEach(l => scan(l.better || l.en || '', tag));
    });

    const rows = [...missing.entries()].sort((a, b) => b[1].n - a[1].n);
    console.log('缺译词总数', rows.length, '出现总次数', rows.reduce((s, r) => s + r[1].n, 0));
    rows.forEach(([word, e]) => console.log(String(e.n).padStart(3), word.padEnd(22), [...e.where].join(' | ')));
})();
