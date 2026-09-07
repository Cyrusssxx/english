/* 选项高频近义词 - 点亮图
 * 数据内联，零 fetch，离线可用，打开即读。交互同方法导图：点条目点亮（黄色），localStorage 持久化。
 * 词频来源：tools/_optfreq.py / _optfreq2.py 统计 36 年真题（英二 2007-2026 + 英一 2010-2025）阅读/完形/新题型选项文本。
 */
(function () {
  'use strict';

  var DATA = {
    maps: [
      {
        id: "near",
        title: "选项高频近义词",
        root: "选项高频近义词",
        rootColor: "#0d9488",
        intro: "36 年真题（英二 2007–2026 + 英一 2010–2025）阅读 / 完形 / 新题型【选项】里的高频词与短语，按意思相近成簇。词频 = 该词在选项文本里出现的次数。做选择时同簇词先想清各自侧重：如 reduce 是减少、decline 是下降、ease 是缓解。短语簇（连接·过渡 / 因果·由来）专治“选项看了半天不懂”——点条目可点亮标记，再点取消。",
        branches: [
          { name: "增长 · 提升", color: "#ef4444", children: [
            { name: "change 改变 · 61 次" },
            { name: "growth 增长 · 38 次" },
            { name: "development 发展 · 33 次" },
            { name: "improve 改善 · 31 次" },
            { name: "increase 增加 · 30 次" }
          ]},
          { name: "重要 · 关键", color: "#f59e0b", children: [
            { name: "important 重要的 · 25 次" },
            { name: "major 主要的 · 25 次" },
            { name: "critical 关键的 · 20 次" }
          ]},
          { name: "促进 · 增强", color: "#f97316", children: [
            { name: "promote 促进 · 17 次" },
            { name: "advance 推进 · 16 次" },
            { name: "boost 推动 · 14 次" },
            { name: "strengthen 加强 · 14 次" },
            { name: "enhance 增强 · 11 次" },
            { name: "facilitate 促进 · 5 次" }
          ]},
          { name: "减轻 · 缓解", color: "#10b981", children: [
            { name: "reduce 减少 · 30 次" },
            { name: "decline 下降 · 18 次" },
            { name: "lower 降低 · 15 次" },
            { name: "ease 缓解 · 11 次" },
            { name: "relieve 减轻 · 8 次" }
          ]},
          { name: "削弱 · 阻止", color: "#dc2626", children: [
            { name: "prevent 阻止 · 21 次" },
            { name: "weaken 削弱 · 8 次" },
            { name: "undermine 削弱 · 8 次" },
            { name: "hinder 阻碍 · 4 次" }
          ]},
          { name: "支持 · 帮助", color: "#84cc16", children: [
            { name: "help 帮助 · 42 次" },
            { name: "support 支持 · 33 次" },
            { name: "back 支持 · 24 次" },
            { name: "provide 提供 · 20 次" }
          ]},
          { name: "影响 · 效应", color: "#3b82f6", children: [
            { name: "influence 影响 · 34 次" },
            { name: "effect 效果 · 24 次" },
            { name: "impact 影响 · 20 次" }
          ]},
          { name: "原因 · 结果", color: "#8b5cf6", children: [
            { name: "lead 导致 · 55 次" },
            { name: "result 结果 · 50 次" },
            { name: "reason 原因 · 42 次" },
            { name: "because 因为 · 39 次" },
            { name: "cause 原因 · 26 次" },
            { name: "thus 因此 · 15 次" },
            { name: "therefore 因此 · 8 次" }
          ]},
          { name: "研究 · 结果", color: "#0ea5e9", children: [
            { name: "research 研究 · 66 次" },
            { name: "study 研究 · 35 次" },
            { name: "found 发现 · 24 次" },
            { name: "results 结果 · 22 次" }
          ]},
          { name: "商业 · 市场", color: "#ec4899", children: [
            { name: "business 商业 · 53 次" },
            { name: "companies 公司 · 45 次" },
            { name: "market 市场 · 42 次" },
            { name: "industry 行业 · 22 次" },
            { name: "firms 公司 · 19 次" }
          ]},
          { name: "政府 · 法律", color: "#14b8a6", children: [
            { name: "government 政府 · 54 次" },
            { name: "law 法律 · 44 次" },
            { name: "federal 联邦的 · 41 次" },
            { name: "legal 法律的 · 30 次" }
          ]},
          { name: "教育 · 学校", color: "#a855f7", children: [
            { name: "education 教育 · 67 次" },
            { name: "students 学生 · 50 次" },
            { name: "degree 学位 · 27 次" },
            { name: "school 学校 · 25 次" },
            { name: "university 大学 · 25 次" }
          ]},
          { name: "工作 · 就业", color: "#0891b2", children: [
            { name: "work 工作 · 75 次" },
            { name: "jobs 工作 · 32 次" },
            { name: "job 工作 · 31 次" },
            { name: "workers 工人 · 30 次" }
          ]},
          { name: "信息 · 媒体", color: "#06b6d4", children: [
            { name: "data 数据 · 64 次" },
            { name: "media 媒体 · 55 次" },
            { name: "information 信息 · 49 次" },
            { name: "news 新闻 · 26 次" },
            { name: "content 内容 · 20 次" }
          ]},
          { name: "科技 · 数字", color: "#6366f1", children: [
            { name: "science 科学 · 38 次" },
            { name: "scientific 科学的 · 37 次" },
            { name: "digital 数字的 · 32 次" },
            { name: "online 在线的 · 29 次" },
            { name: "technology 技术 · 28 次" }
          ]},
          { name: "经济 · 金融", color: "#0d9488", children: [
            { name: "economic 经济的 · 51 次" },
            { name: "tax 税 · 35 次" },
            { name: "financial 金融的 · 34 次" },
            { name: "gdp 国内生产总值 · 21 次" }
          ]},
          { name: "代替 · 选择", color: "#d946ef", children: [
            { name: "choice 选择 · 22 次" },
            { name: "replace 取代 · 16 次" },
            { name: "option 选择 · 10 次" },
            { name: "alternative 替代 · 7 次" }
          ]},
          { name: "连接 · 过渡", color: "#64748b", children: [
            { name: "rather than 而不是 · 22 次" },
            { name: "so that 以便 · 10 次" },
            { name: "even if 即使 · 7 次" },
            { name: "as to 关于 · 7 次" },
            { name: "even though 尽管 · 5 次" },
            { name: "regardless of 不管 · 5 次" },
            { name: "in terms of 就…而言 · 3 次" }
          ]},
          { name: "因果 · 由来", color: "#334155", children: [
            { name: "lead to 导致 · 10 次" },
            { name: "due to 由于 · 9 次" },
            { name: "in that 在于 · 因为 · 7 次" },
            { name: "in favor of 赞成 · 6 次" },
            { name: "result in 导致 · 3 次" },
            { name: "owing to 由于 · 3 次" },
            { name: "arise from 源于 · 2 次" },
            { name: "give rise to 引发 · 1 次" },
            { name: "account for 占 · 解释 · 1 次" }
          ]},
          { name: "大 · 小", color: "#ca8a04", children: [
            { name: "big 大的 · 36 次" },
            { name: "little 小的 · 30 次" },
            { name: "small 小的 · 22 次" },
            { name: "large 大的 · 21 次" }
          ]},
          { name: "好 · 优秀", color: "#eab308", children: [
            { name: "good 好的 · 40 次" },
            { name: "better 更好的 · 40 次" },
            { name: "well 好 · 37 次" },
            { name: "great 极好的 · 31 次" }
          ]}
        ]
      }
    ]
  };

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function leafText(t) {
    var m = t.match(/^([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(.+)$/);
    if (m) return '<b>' + esc(m[1]) + '</b> ' + esc(m[2]);
    return esc(t);
  }

  function renderItems(items) {
    var html = '';
    items.forEach(function (it) {
      if (it.children && it.children.length) {
        html += renderItems(it.children);
      } else {
        html += '<div class="leaf-row">' + leafText(it.name) + '</div>';
      }
    });
    return html;
  }

  // 响应式卡片网格：每簇一张卡，桌面 2~3 列、手机 1 列（替代原横向横滑，长列表也不再需要横滑）
  function renderMap(map) {
    var html = '';
    if (map.intro) html += '<p class="map-intro">' + esc(map.intro) + '</p>';
    html += '<div class="nm-grid">';
    map.branches.forEach(function (b) {
      html += '<div class="nm-card" style="--c:' + b.color + '">';
      html += '<div class="nm-card-head">' + esc(b.name) + '</div>';
      html += renderItems(b.children);
      html += '</div>';
    });
    html += '</div>';
    return html;
  }

  // ==================== 高亮标记（独立 key，与方法导图互不干扰） ====================
  var HL_KEY = 'nm_highlights_v1';
  var content = null;
  var hlSet = loadHL();

  function loadHL() {
    try { return new Set(JSON.parse(localStorage.getItem(HL_KEY) || '[]')); }
    catch (e) { return new Set(); }
  }
  function saveHL() {
    try { localStorage.setItem(HL_KEY, JSON.stringify(Array.from(hlSet))); } catch (e) {}
  }
  function rowKey(row) { return row.textContent; }

  function restoreHL() {
    if (!content) return;
    var rows = content.querySelectorAll('.leaf-row');
    for (var i = 0; i < rows.length; i++) {
      if (hlSet.has(rowKey(rows[i]))) rows[i].classList.add('hl');
    }
  }
  function onContentClick(e) {
    var row = e.target.closest ? e.target.closest('.leaf-row') : null;
    if (!row) return;
    var k = rowKey(row);
    if (hlSet.has(k)) { hlSet.delete(k); row.classList.remove('hl'); }
    else { hlSet.add(k); row.classList.add('hl'); }
    saveHL();
  }
  window.clearHighlights = function () {
    hlSet.clear();
    saveHL();
    if (content) {
      var rows = content.querySelectorAll('.hl');
      for (var i = 0; i < rows.length; i++) rows[i].classList.remove('hl');
    }
  };

  function init() {
    content = document.getElementById('mmContent');
    if (!content) return;
    content.innerHTML = DATA.maps.map(function (m) {
      return '<section class="map-section"><h2 class="map-h">' + esc(m.title) + '</h2>' + renderMap(m) + '</section>';
    }).join('');
    restoreHL();
    content.addEventListener('click', onContentClick);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();