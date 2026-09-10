/* 熟词僻义 - 表格渲染
 * 数据：pwa/data/wordnotes.json（tools/build_wordnotes.py 生成，按词频降序）
 * 单表五列：单词 / 词频 / 熟义 / 僻义 / 原句（含该词的短句 + 译文 + 出处）
 */
(function () {
  'use strict';

  var state = { data: null, q: '' };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function rowHtml(r) {
    return '<tr>' +
      '<td class="wn-w" data-label="单词">' + esc(r.w) + '</td>' +
      '<td class="wn-freq" data-label="词频">' + (r.freq || 0) + '</td>' +
      '<td class="wn-common" data-label="熟义">' + esc(r.common) + '</td>' +
      '<td class="wn-uncommon" data-label="僻义">' + esc(r.uncommon) + '</td>' +
      '<td class="wn-sent" data-label="原句">' +
        '<div class="wn-en">' + esc(r.en) + '</div>' +
        (r.cn ? '<div class="wn-cn">' + esc(r.cn) + '</div>' : '') +
        (r.src ? '<div class="wn-src">' + esc(r.src) + '</div>' : '') +
      '</td>' +
    '</tr>';
  }

  function render() {
    var content = document.getElementById('wnContent');
    if (!content || !state.data) return;
    var q = state.q.trim().toLowerCase();
    var rows = state.data.rows.filter(function (r) {
      if (!q) return true;
      return (r.w + ' ' + r.common + ' ' + r.uncommon + ' ' + (r.cn || '')).toLowerCase().indexOf(q) >= 0;
    });
    var head = '<div class="wn-count">' + rows.length + ' / ' + state.data.count + ' 词' +
               (q ? '（筛选：' + esc(state.q) + '）' : '，按词频降序') + '</div>';
    if (!rows.length) {
      content.innerHTML = head + '<p style="color:var(--text-light)">没有匹配的词</p>';
      return;
    }
    content.innerHTML = head +
      '<div class="wn-table-wrap"><table class="wn-table">' +
        '<thead><tr><th>单词</th><th>词频</th><th>熟义</th><th>僻义</th><th>原句（含该词的短句）</th></tr></thead>' +
        '<tbody>' + rows.map(rowHtml).join('') + '</tbody>' +
      '</table></div>';
  }

  function fail(msg) {
    var content = document.getElementById('wnContent');
    if (content) content.innerHTML = '<p style="color:var(--text-light)">' + esc(msg) + '</p>';
  }

  function init() {
    var input = document.getElementById('wnSearch');
    if (input) {
      input.addEventListener('input', function () { state.q = input.value; render(); });
    }
    fetch('data/wordnotes.json')
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        state.data = d;
        render();
        document.title = '熟词僻义（' + (d.count || 0) + ' 词） - 英语真题精翻';
      })
      .catch(function (e) { fail('数据加载失败：' + e.message + '（请用 start.bat 启动后访问）'); });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
