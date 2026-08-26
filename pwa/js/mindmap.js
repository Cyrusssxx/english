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
        intro: "一张纸搞定阅读：选项陷阱、六大题型、文章结构、标点暗号。做题前扫一遍，做题后对照复盘。",
        branches: [
          {
            name: "选项",
            color: "#ec4899",
            children: [
              {
                name: "错误",
                children: [
                  { name: "范围太大、太小：英二 08年35AB，英二 13年24D" },
                  { name: "无中生有：英一 10年24BCD" },
                  { name: "过度推断：英二 11年27AD，12年34B，英一 15年36BC" },
                  { name: "不同内容嫁接：英一 17年22D" },
                  { name: "答非所问：英二 10年21A，09年39BCD" },
                  { name: "时态：英一 10年21A" },
                  { name: "偷换概念：08年34B，英一 13年37D，14年31D" },
                  { name: "太绝对：英二 12年30A" }
                ]
              },
              {
                name: "正确",
                children: [
                  { name: "先果后因：英一 15年36，13年36，英二 10年21，18年37" },
                  { name: "主动转被动：英一 11年33" },
                  { name: "正化反说：英一 13年36A，14年35D" },
                  { name: "同义替换：题干与原文同义改写" }
                ]
              }
            ]
          },
          {
            name: "题型",
            color: "#14b8a6",
            children: [
              {
                name: "主旨",
                children: [
                  { name: "作用：覆盖全文" },
                  { name: "特征：标题、关键" },
                  { name: "做法：1. 划掉段意 2. 选文章反复出现内容 3. 站在作者角度写文章" },
                  { name: "例如：英一 10年25、30，11年30、35，12年25、35，13年25、35，14年30，15年35，16年25、35，19年25、35，24年25 等" }
                ]
              },
              {
                name: "段主",
                children: [
                  { name: "作用：概括段落" },
                  { name: "特征：1. 开头第一句 2. 根据某个自然段出题" },
                  { name: "做法：1. 选段意 2. 排除例子" },
                  { name: "例如：英一 11年28、29、37，13年32、33" }
                ]
              },
              {
                name: "观点",
                children: [
                  { name: "作用：强调或论述段落主旨" },
                  { name: "特征：by / example / case / illustrate / mentioned / shown / say / suggest" },
                  { name: "做法：1. 找段主 2. 排除例子 3. 看逻辑" },
                  { name: "例如：英一 14年32，22年37 等" }
                ]
              },
              {
                name: "例子",
                children: [
                  { name: "作用：论述段主或观点" },
                  { name: "特征：by / example / case / illustrate / mentioned / shown" },
                  { name: "做法：1. 选例子以外的 2. 排除例子里面的" },
                  { name: "例如：英一 11年34，12年22、27，14年33，15年22、24，17年22、23，18年21、24，19年33 等" }
                ]
              },
              {
                name: "态度",
                children: [
                  { name: "作用：表明态度" },
                  { name: "特征：attitude / feel" },
                  { name: "做法：1. 排除小墓碑词 2. 看感情色彩" },
                  { name: "例如：英一 10年40，11年25，12年40，13年30，14年36，15年27，16年31，17年40，18年22、23，19年38，20年34，21年25，22年25，23年38 等" }
                ]
              },
              {
                name: "猜词",
                children: [
                  { name: "作用：猜词" },
                  { name: "特征：具体去找的" },
                  { name: "做法：1. 相同逻辑 2. 相反逻辑 3. 第二次提到（it / them / those）" },
                  { name: "例如：英一 11年28，13年23、27，14年22，16年22、23，17年23，19年29，20年25，23年25，24年25，英二 17年37、38 等" }
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
              { name: "少数人/作者：英一 14年2、5" },
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
                  { name: "例如：英一 11年28，13年23、27，14年22，16年22、23，17年23，19年29，20年25，23年25，24年25，英二 17年37、38" }
                ]
              },
              {
                name: "分号 ；",
                children: [
                  { name: "第二次提到：英一..." }
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

  function renderMap(map) {
    var html = '';
    if (map.intro) html += '<p class="map-intro">' + esc(map.intro) + '</p>';
    map.branches.forEach(function (b) {
      html += '<section class="branch-card" style="--c:' + b.color + '">';
      html += '<h3 class="branch-title">' + esc(b.name) + '</h3>';
      html += renderItems(b.children, b.color);
      html += '</section>';
    });
    return html;
  }

  function init() {
    var tabs = document.getElementById('mmTabs');
    var content = document.getElementById('mmContent');
    if (!tabs || !content) return;

    DATA.maps.forEach(function (m, i) {
      var btn = document.createElement('button');
      btn.className = 'mm-tab' + (i === 0 ? ' active' : '');
      btn.type = 'button';
      btn.textContent = m.title;
      btn.addEventListener('click', function () {
        var all = tabs.querySelectorAll('.mm-tab');
        for (var k = 0; k < all.length; k++) all[k].classList.remove('active');
        btn.classList.add('active');
        showMap(i);
      });
      tabs.appendChild(btn);
    });

    function showMap(i) {
      content.innerHTML = DATA.maps.map(function (m, idx) {
        return '<div class="map-panel' + (idx === i ? ' active' : '') + '">' +
          renderMap(m) + '</div>';
      }).join('');
    }

    showMap(0);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
