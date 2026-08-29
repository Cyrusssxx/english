/* 方法导图 - 静态方法页渲染
 * 数据内联，零 fetch / 零 SVG，离线可用，打开即读。
 * 内容源：pwa/data/mindmap.json（如需改内容，可同步修改此处内联 DATA 与 json）。
 */
(function () {
  'use strict';

  var DATA = {
    maps: [
      {
        id: "attitude",
        title: "态度词小墓碑",
        root: "态度词小墓碑",
        rootColor: "#0d9488",
        intro: "这些词在考研阅读态度题里一出现，基本就是干扰项（小墓碑）——看到先排除，别选。",
        branches: [
          {
            name: "不符合价值观",
            color: "#f59e0b",
            children: [
              { name: "scornful 轻蔑的" },
              { name: "sarcastic 讽刺的" },
              { name: "contempt 轻蔑的" },
              { name: "biased 有偏见的" },
              { name: "indulgence 放纵" },
              { name: "permissive 放纵的" },
              { name: "tolerant 容忍的" },
              { name: "indifferent 冷漠的" },
              { name: "trivial 不重要的" }
            ]
          },
          {
            name: "感情色彩太过",
            color: "#ef4444",
            children: [
              { name: "destructive 毁灭的" },
              { name: "enthusiasm 极热情的" },
              { name: "desperate 绝望的" },
              { name: "conceited 自负的（过分看重自己）" }
            ]
          },
          {
            name: "模糊的",
            color: "#3b82f6",
            children: [
              { name: "ambiguous 模棱两可的" },
              { name: "uncertain 不确定的" },
              { name: "puzzled 困惑的" }
            ]
          }
        ]
      },
      {
        id: "reading",
        title: "阅读一张纸",
        root: "阅读一张纸",
        rootColor: "#0d9488",
        intro: "一张纸搞定阅读：选项陷阱、六大题型 + 阅读 B 节、完形、句意题，文章结构、标点暗号。做题前扫一遍，做题后对照复盘。",
        branches: [
          {
            name: "选项",
            color: "#ec4899",
            children: [
              {
                name: "错误",
                children: [
                  { name: "范围太大、太小：英二 08年35AB，13年24D，10年22A，11年27A，18年37A，22年24A" },
                  { name: "无中生有：英二 10年24BCD，14年36A，16年33A，22年21A" },
                  { name: "过度推断：英二 11年27AD，12年34B，13年40D，15年39D，18年30D，20年39D" },
                  { name: "不同内容嫁接：英二 14年30A，15年33A，17年22D，19年33A" },
                  { name: "答非所问：英二 10年21A，09年39BCD，11年24A，12年21A，13年27A" },
                  { name: "时态：英二 10年21A，11年26A" },
                  { name: "偷换概念：英二 08年34B，13年37D，14年31D，16年32A，20年40A" },
                  { name: "太绝对：英二 12年30A，14年22A，15年24A，18年26A" }
                ]
              },
              {
                name: "正确",
                children: [
                  { name: "先果后因：英二 10年21，18年37，14年25，15年40" },
                  { name: "主动转被动：英二 11年33A，14年37" },
                  { name: "正化反说：英二 13年36A，14年35D，18年23A" },
                  { name: "同义替换：题干与原文同义改写" }
                ]
              }
            ]
          },
          {
            name: "题型",
            color: "#14b8a6",
            split: 2,
            children: [
              {
                name: "主旨",
                children: [
                  { name: "作用：覆盖全文" },
                  { name: "特征：标题、关键" },
                  { name: "做法：1. 划掉段意 2. 选文章反复出现内容 3. 站在作者角度写文章" },
                  { name: "例如：英二 10年25、29、40，11年30，12年25，13年25、30，14年25、35，15年40，16年35，17年35，18年40，19年35，20年30，21年36，23年25、30、40 等" }
                ]
              },
              {
                name: "段主",
                children: [
                  { name: "作用：概括段落" },
                  { name: "特征：1. 开头第一句 2. 根据某个自然段出题" },
                  { name: "做法：1. 选段意 2. 排除例子" },
                  { name: "例如：英二 10年21、22，11年28、29，12年28、29，13年32、33，14年32，15年32，16年32，17年32，18年31，19年31，20年31 等" }
                ]
              },
              {
                name: "观点",
                children: [
                  { name: "作用：强调或论述段落主旨" },
                  { name: "特征：by / example / case / illustrate / mentioned / shown / say / suggest" },
                  { name: "做法：1. 找段主 2. 排除例子 3. 看逻辑" },
                  { name: "例如：英二 19年22、23、39、40，20年24、33、34、40，21年22、26、32、33、38，22年23、25、30、39，23年21、22、33、35 等" }
                ]
              },
              {
                name: "例子",
                children: [
                  { name: "作用：论述段主或观点" },
                  { name: "特征：by / example / case / illustrate / mentioned / shown" },
                  { name: "做法：1. 选例子以外的 2. 排除例子里面的" },
                  { name: "例如：英二 14年23，10年34，11年34，12年22、27，15年32、34，16年34，17年22、23，18年21、24，19年33 等" }
                ]
              },
              {
                name: "态度",
                children: [
                  { name: "作用：表明态度" },
                  { name: "特征：attitude / feel" },
                  { name: "做法：1. 排除小墓碑词 2. 看感情色彩" },
                  { name: "例如：英二 10年35，11年25、40，12年35、40，13年35、39，14年22，17年25，18年25，19年30，21年30 等" }
                ]
              },
              {
                name: "猜词",
                children: [
                  { name: "作用：猜词" },
                  { name: "特征：具体去找的" },
                  { name: "做法：1. 相同逻辑 2. 相反逻辑 3. 第二次提到（it / them / those）" },
                  { name: "例如：英二 10年24、27，14年29，15年24，16年25，17年33、37、38，18年26，19年25，20年38 等" }
                ]
              },
              {
                name: "判断（七选五）",
                children: [
                  { name: "作用：选出符合文章语境的句子填空" },
                  { name: "特征：选项给出完整句子，题号在 41-45" },
                  { name: "做法：1. 看空前空后逻辑（代词/转折/并列/因果）2. 排除代词/时态/逻辑矛盾的 3. 回代验证" },
                  { name: "例如：英二 10年41-45" }
                ]
              },
              {
                name: "小标题（信息匹配）",
                children: [
                  { name: "作用：从标题列表中选标题匹配段落" },
                  { name: "特征：阅读 B 节，给出 7 选 5（A-G）" },
                  { name: "做法：1. 抓段首段尾关键词 2. 标题关键词与段落同义改写 3. 先易后难" },
                  { name: "例如：英二 13年41-45，15年41-45，16年41-45，18年41-45，20年41-45，21年41-45，22年41-45，25年41-45 等" }
                ]
              },
              {
                name: "匹配（多项对应）",
                children: [
                  { name: "作用：把人/事/观点/理论与描述匹配（信息匹配题）" },
                  { name: "特征：阅读 B 节，给出人和描述（可多对多）" },
                  { name: "做法：1. 先看描述抓人名关键词 2. 定位该人出现的段 3. 排除只提到但未做该事的" },
                  { name: "例如：英二 11年41-45，12年41-45，14年41-45，17年41-45，19年41-45，23年41-45，24年41-45 等" }
                ]
              },
              {
                name: "完形填空",
                children: [
                  { name: "作用：上下文选出最合适的词" },
                  { name: "特征：题号 21-40（与阅读同号段），一篇 4 段 20 空" },
                  { name: "做法：1. 先通读把握大意 2. 上下文逻辑（因果/转折/并列/指代）3. 词义辨析+搭配 4. 排除法" },
                  { name: "例如：英二 10年完形-21-40 至 25年完形-21-40（共 16 篇）" }
                ]
              },
              {
                name: "句意题",
                children: [
                  { name: "作用：判断某句的隐含意义或作者意图" },
                  { name: "特征：题目直接引述某句，问「言下之意」「意在说明」「旨在表达」「best interprets」" },
                  { name: "做法：1. 定位句子上下文 2. 看逻辑走向（顺承/转折）3. 排除字面义，选言外义" },
                  { name: "例如：英二 12年34、36 等" }
                ]
              }
            ]
          },
          {
            name: "文章结构",
            color: "#22c55e",
            children: [
              { name: "观点" },
              { name: "段主：论述段落主旨" },
              { name: "观点反推段主" },
              { name: "少数人/作者：英二 14年23，15年24，19年33，20年34" },
              { name: "概括自然段意思" },
              { name: "考以偏概全" },
              {
                name: "例子",
                children: [
                  { name: "例子论述段主" },
                  { name: "例子论述观点" }
                ]
              }
            ]
          },
          {
            name: "标点符号",
            color: "#f97316",
            children: [
              {
                name: "破折号 — 细节",
                children: [
                  { name: "特征：具体去找的" },
                  { name: "做法：1. 细节服从主位、观点 2. 细节定位" },
                  { name: "例如：英二 10年24，14年29，15年24，16年25，17年33、37、38，18年26，19年25，20年38" }
                ]
              },
              {
                name: "分号 ；",
                children: [
                  { name: "第二次提到：英二 10年21，11年25，13年25" }
                ]
              },
              {
                name: "冒号 ：",
                children: [
                  { name: "1. 前后一个意思 2. 看不懂前面看后面" }
                ]
              },
              {
                name: "引号（反讽）",
                children: [
                  { name: "反讽" }
                ]
              },
              {
                name: "问号 ？",
                children: [
                  { name: "开章设问，文章主旨大概就是问题的回答" }
                ]
              }
            ]
          }
        ]
      }
    ]
  };

  function esc(s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c];
    });
  }

  function leafText(t) {
    var m = t.match(/^([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(.+)$/);
    if (m) return '<b>' + esc(m[1]) + '</b> ' + esc(m[2]);
    return esc(t);
  }

  function renderItems(items, color) {
    var html = '<div class="branch-body">';
    items.forEach(function (it) {
      if (it.children && it.children.length) {
        html += '<div class="sub" style="--c:' + color + '">';
        html += '<div class="sub-title">' + esc(it.name) + '</div>';
        html += renderItems(it.children, color);
        html += '</div>';
      } else {
        html += '<div class="leaf-row">' + leafText(it.name) + '</div>';
      }
    });
    html += '</div>';
    return html;
  }

  // 拆分列：将分支的子项直接铺进 N 列网格（每个子项是一个网格单元，不再被整包 .branch-body）
  function renderSplitItems(items, color) {
    var html = '<div class="mm-split">';
    items.forEach(function (it) {
      if (it.children && it.children.length) {
        html += '<div class="sub" style="--c:' + color + '">';
        html += '<div class="sub-title">' + esc(it.name) + '</div>';
        html += renderItems(it.children, color);
        html += '</div>';
      } else {
        html += '<div class="leaf-row">' + leafText(it.name) + '</div>';
      }
    });
    html += '</div>';
    return html;
  }

  function renderMap(map) {
    var html = '';
    if (map.intro) html += '<p class="map-intro">' + esc(map.intro) + '</p>';
    html += '<div class="mm-cols">';
    map.branches.forEach(function (b) {
      var colCls = b.split ? 'mm-col mm-col-split' : 'mm-col';
      html += '<div class="' + colCls + '" style="--c:' + b.color + '">';
      html += '<div class="mm-col-head">' + esc(b.name) + '</div>';
      html += b.split ? renderSplitItems(b.children, b.color) : renderItems(b.children, b.color);
      html += '</div>';
    });
    html += '</div>';
    return html;
  }

  // ==================== 高亮标记 ====================
  var HL_KEY = 'mm_highlights_v1';
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
  // 供「清除高亮」按钮调用（暴露到全局）
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
