/* 熟词僻义 - 表格渲染
 * 数据：pwa/data/wordnotes.json（tools/build_wordnotes.py 生成）
 * 结构：按年份分区的四列表格 —— 单词 / 熟义 / 僻义 / 原句（英 + 中）
 */
(function () {
  'use strict';

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function yearLabel(y) {
    return y === '通用' ? '通用（未定位年份）' : y + ' 年';
  }

  function rowHtml(r) {
    return '<tr>' +
      '<td class="wn-w" data-label="单词">' + esc(r.w) + '</td>' +
      '<td class="wn-common" data-label="熟义">' + esc(r.common) + '</td>' +
      '<td class="wn-uncommon" data-label="僻义">' + esc(r.uncommon) + '</td>' +
      '<td class="wn-sent" data-label="原句">' +
        '<div class="wn-en">' + esc(r.en) + '</div>' +
        (r.cn ? '<div class="wn-cn">' + esc(r.cn) + '</div>' : '') +
        (r.src ? '<div class="wn-src">' + esc(r.src) + '</div>' : '') +
      '</td>' +
    '</tr>';
  }

  function sectionHtml(sec) {
    return '<section class="wn-year" id="wn-y-' + esc(sec.year) + '">' +
      '<h2 class="wn-year-h">' + esc(yearLabel(sec.year)) +
        '<span class="wn-year-n">' + sec.rows.length + ' 词</span></h2>' +
      '<div class="wn-table-wrap">' +
        '<table class="wn-table">' +
          '<thead><tr><th>单词</th><th>熟义</th><th>僻义</th><th>原句</th></tr></thead>' +
          '<tbody>' + sec.rows.map(rowHtml).join('') + '</tbody>' +
        '</table>' +
      '</div>' +
    '</section>';
  }

  function render(data) {
    var content = document.getElementById('wnContent');
    var toc = document.getElementById('wnToc');
    if (!content) return;
    content.innerHTML = data.years.map(sectionHtml).join('');
    if (toc) {
      toc.innerHTML = '<span style="color:var(--text-light);font-size:.82rem;align-self:center">跳到：</span>' +
        data.years.map(function (s) {
          return '<a href="#wn-y-' + esc(s.year) + '">' + esc(s.year === '通用' ? '通用' : s.year) +
                 '（' + s.rows.length + '）</a>';
        }).join('');
    }
    document.title = '熟词僻义（' + (data.count || 0) + ' 词） - 英语真题精翻';
  }

  function fail(msg) {
    var content = document.getElementById('wnContent');
    if (content) content.innerHTML = '<p style="color:var(--text-light)">' + esc(msg) + '</p>';
  }

  function init() {
    fetch('data/wordnotes.json')
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(render)
      .catch(function (e) { fail('数据加载失败：' + e.message + '（请用 start.bat 启动后访问）'); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
