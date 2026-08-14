/* 英语二精翻 PWA - Service Worker（自动生成，请勿手改；改资源后由 pre-commit 钩子重算 CACHE_VER）
 * 预缓存全部页面/样式/脚本/题库/图标，安装后完全离线可用。
 * 升级题库或代码后：CACHE_VER 会随资源内容自动变化，客户端自动换新缓存。
 */
const CACHE_VER = 'en2-e06b8d7b';

const PRECACHE = [
    'index.html',
    'article.html',
    'study.html',
    'vocab.html',
    'favorites.html',
    'en1.html',
    'chain.html',
    'manifest.webmanifest',
    'css/style.css',
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

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_VER)
            .then(cache => cache.addAll(PRECACHE))
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

// cache-first：离线优先；缓存未命中再走网络并回填
self.addEventListener('fetch', (e) => {
    if (e.request.method !== 'GET') return;
    e.respondWith(
        caches.match(e.request, { ignoreSearch: true }).then(hit => {
            if (hit) return hit;
            return fetch(e.request).then(resp => {
                if (resp.ok && new URL(e.request.url).origin === location.origin) {
                    const clone = resp.clone();
                    caches.open(CACHE_VER).then(cache => cache.put(e.request, clone));
                }
                return resp;
            });
        })
    );
});
