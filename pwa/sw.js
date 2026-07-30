/* 英语二精翻 PWA - Service Worker（改自 408 刷题 sw.js）
 * 预缓存全部页面/样式/脚本/题库/图标，安装后完全离线可用。
 * 升级题库或代码后：改 CACHE_VER 版本号即可让客户端自动换新缓存。
 */
const CACHE_VER = 'en2-v19';

const PRECACHE = [
    'index.html',
    'article.html',
    'study.html',
    'vocab.html',
    'favorites.html',
    'manifest.webmanifest',
    'css/style.css',
    'js/common.js',
    'js/storage.js',
    'js/article.js',
    'js/annotate.js',
    'js/study.js',
    'js/dict.js',
    'data/index.json',
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
    'data/dict.json',
    'data/phrases.json',
    'data/freq.json',
    'data/deck_phrases.json',
    'data/deck_core.json',
    'data/deck_syllabus.json',
    'data/deck_confusable.json',
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
