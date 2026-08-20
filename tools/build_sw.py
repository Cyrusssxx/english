#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""英语二精翻 PWA - 自动重建 Service Worker 缓存版本。

扫描 pwa/ 下所有需要离线预缓存的资源（页面/样式/脚本/题库 JSON/图片/图标），
按它们的内容汇总算一个 SHA-256，取其前 8 位作为 CACHE_VER。
这样只要任一预缓存资源有改动，提交时（pre-commit 钩子）sw.js 的版本号就会变，
客户端自动拉取新缓存，无需手动 bump 版本号。

纯标准库实现，任意 python3 即可运行。
"""
import os
import sys
import hashlib
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))          # tools/
PWA = os.path.normpath(os.path.join(ROOT, "..", "pwa"))     # pwa/

CORE_PAGES = [
    "index.html", "article.html", "study.html", "vocab.html", "favorites.html",
    "en1.html", "chain.html",
    "manifest.webmanifest", "css/style.css",
]


def rel(p):
    return os.path.relpath(p, PWA).replace(os.sep, "/")


def collect_precache():
    files = []
    for f in CORE_PAGES:
        fp = os.path.join(PWA, f)
        if os.path.isfile(fp):
            files.append(f)
    # js
    for fp in sorted(glob.glob(os.path.join(PWA, "js", "*.js"))):
        if os.path.isfile(fp):
            files.append(rel(fp))
    # data json（含子目录，如 data/en1/*.json）
    for fp in sorted(glob.glob(os.path.join(PWA, "data", "**", "*.json"), recursive=True)):
        if os.path.isfile(fp):
            files.append(rel(fp))
    # img
    for fp in sorted(glob.glob(os.path.join(PWA, "img", "*"))):
        if os.path.isfile(fp):
            files.append(rel(fp))
    # icons
    for fp in sorted(glob.glob(os.path.join(PWA, "icons", "*"))):
        if os.path.isfile(fp):
            files.append(rel(fp))
    # 去重，保序
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def content_hash(files):
    h = hashlib.sha256()
    for f in files:
        fp = os.path.join(PWA, f)
        try:
            with open(fp, "rb") as fh:
                h.update(fh.read())
        except OSError:
            pass
    return h.hexdigest()[:8]


SW_TEMPLATE = """/* 英语二精翻 PWA - Service Worker（自动生成，请勿手改；改资源后由 pre-commit 钩子重算 CACHE_VER）
 * 预缓存全部页面/样式/脚本/题库/图标，安装后完全离线可用。
 * 升级题库或代码后：CACHE_VER 会随资源内容自动变化，客户端自动换新缓存。
 */
const CACHE_VER = '{ver}';

const PRECACHE = [
{precache}
];

// 带超时的 fetch：网络慢/挂起时 abort，避免请求无限 pending（首页"加载中"卡死的根因）
function fetchTO(req, ms) {{
    const ctrl = new AbortController();
    const id = setTimeout(() => ctrl.abort(), ms);
    return fetch(req, {{ signal: ctrl.signal }}).finally(() => clearTimeout(id));
}}

self.addEventListener('install', (e) => {{
    e.waitUntil(
        caches.open(CACHE_VER)
            // 逐个缓存 + allSettled：单个资源失败不阻塞 SW 激活（addAll 是原子的，一个 404 就全废）
            .then(cache => Promise.allSettled(PRECACHE.map(u => cache.add(u))))
            .then(() => self.skipWaiting())
    );
}});

self.addEventListener('activate', (e) => {{
    e.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE_VER).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
}});

// cache-first：离线优先；缓存未命中走网络（带超时），失败返回 504 而非挂起
self.addEventListener('fetch', (e) => {{
    if (e.request.method !== 'GET') return;
    e.respondWith(
        caches.match(e.request, {{ ignoreSearch: true }}).then(hit => {{
            if (hit) return hit;
            return fetchTO(e.request, 8000)
                .then(resp => {{
                    if (resp.ok && new URL(e.request.url).origin === location.origin) {{
                        const clone = resp.clone();
                        caches.open(CACHE_VER).then(cache => cache.put(e.request, clone));
                    }}
                    return resp;
                }})
                .catch(() => new Response('', {{ status: 504, statusText: 'Gateway Timeout' }}));
        }})
    );
}});
"""


def main():
    if not os.path.isdir(PWA):
        print("⚠️  未找到 pwa 目录：%s" % PWA, file=sys.stderr)
        return 1
    files = collect_precache()
    ver = "en2-" + content_hash(files)
    precache_block = ",\n".join("    '%s'" % f for f in files)
    sw = SW_TEMPLATE.format(ver=ver, precache=precache_block)
    out = os.path.join(PWA, "sw.js")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(sw)
    print("✅ sw.js 已重建：CACHE_VER=%s，预缓存 %d 个资源" % (ver, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
