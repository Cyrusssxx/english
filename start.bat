@echo off
rem 考研英语二精翻 - 一键启动本地服务器
rem 必须经 http:// 访问（Service Worker 与 fetch 在 file:// 下不可用）
cd /d "%~dp0pwa"
start "" http://localhost:8410/index.html
python -m http.server 8410
