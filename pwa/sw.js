/* 英语二精翻 PWA - Service Worker（自动生成，请勿手改；改资源后由 pre-commit 钩子重算 CACHE_VER）
 * 预缓存全部页面/样式/脚本/题库/图标，安装后完全离线可用。
 * 升级题库或代码后：CACHE_VER 会随资源内容自动变化，客户端自动换新缓存。
 */
const CACHE_VER = 'en2-9f8cebff';

const PRECACHE = [
    'index.html',
    'article.html',
    'study.html',
    'vocab.html',
    'favorites.html',
    'en1.html',
    'chain.html',
    'mindmap.html',
    'js/mindmap.js',
    'data/mindmap.json',
    'manifest.webmanifest',
    'css/style.css',
    'js/annotate-lite.js',
    'js/annotate.js',
    'js/article.js',
    'js/common.js',
    'js/dict.js',
    'js/storage.js',
    'js/study.js',
    'data/2007.json',
    'data/2008.json',
    'data/2009.json',
    'data/2010.json',
    'data/2011.json',
    'data/2012.json',
    'data/2013.json',
    'data/2014.json',
    'data/2015.json',
    'data/2016.json',
    'data/2017.json',
    'data/2018.json',
    'data/2019.json',
    'data/2020.json',
    'data/2021.json',
    'data/2022.json',
    'data/2023.json',
    'data/2024.json',
    'data/2025.json',
    'data/chain_corpus.json',
    'data/deck_confusable.json',
    'data/deck_core.json',
    'data/deck_phrases.json',
    'data/deck_realexam.json',
    'data/deck_syllabus.json',
    'data/deck_tc_phrases.json',
    'data/deck_tc_phrases_clean.json',
    'data/deck_tc_senses.json',
    'data/deck_tc_senses_clean.json',
    'data/dict.json',
    'data/en1/2010.json',
    'data/en1/2011.json',
    'data/en1/2012.json',
    'data/en1/2013.json',
    'data/en1/2014.json',
    'data/en1/2015.json',
    'data/en1/2016.json',
    'data/en1/2017.json',
    'data/en1/2018.json',
    'data/en1/2019.json',
    'data/en1/2020.json',
    'data/en1/2021.json',
    'data/en1/2022.json',
    'data/en1/2023.json',
    'data/en1/2024.json',
    'data/en1/2025.json',
    'data/en1_index.json',
    'data/freq.json',
    'data/hardwords.json',
    'data/index.json',
    'data/phrases.json',
    'data/wordbook_freq.json',
    'data/wordbook_obscure.json',
    'img/2010_writingb_chart.png',
    'img/2011_writingb_chart.png',
    'img/2012_writingb_chart.png',
    'img/2013_writingb_chart.png',
    'img/2014_writingb_chart.png',
    'img/2015_writingb_chart.png',
    'img/2016_writingb_chart.png',
    'img/2017_writingb_chart.png',
    'img/2018_writingb_chart.png',
    'img/2019_writingb_chart.png',
    'img/2020_writingb_chart.png',
    'img/2021_writingb_chart.png',
    'img/2022_writingb_chart.png',
    'img/2023_writingb_chart.png',
    'img/2024_writingb_chart.png',
    'img/2025_writingb_chart.png',
    'icons/favicon.svg',
    'icons/icon-192.png',
    'icons/icon-512.png'
];

// 带超时的 fetch：网络慢/挂起时 abort，避免请求无限 pending（首页"加载中"卡死的根因）
function fetchTO(req, ms) {
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), ms);
    return fetch(req, { signal: ctrl.signal }).finally(() => clearTimeout(id));
}

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_VER)
            // 逐个缓存 + allSettled：单个资源失败不阻塞 SW 激活（addAll 是原子的，一个 404 就全废）
            .then(cache => Promise.allSettled(PRECACHE.map(u => cache.add(u))))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE_VER).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

// cache-first：离线优先；缓存未命中走网络（带超时），失败返回 504 而非挂起
self.addEventListener('fetch', (e) => {
    if (e.request.method !== 'GET') return;
    e.respondWith(
        caches.match(e.request, { ignoreSearch: true }).then(hit => {
            if (hit) return hit;
            return fetchTO(e.request, 8000)
                .then(resp => {
                    if (resp.ok && new URL(e.request.url).origin === location.origin) {
                        const clone = resp.clone();
                        caches.open(CACHE_VER).then(cache => cache.put(e.request, clone));
                    }
                    return resp;
                })
                .catch(() => new Response('', { status: 504, statusText: 'Gateway Timeout' }));
        })
    );
});
