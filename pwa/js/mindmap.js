/* 方法导图渲染引擎：数据驱动竖向树 SVG + 缩放/平移/折叠 + 窄屏树形列表兜底 */
(function () {
  'use strict';

  var ROWDEPTH = 138;  // 层级纵向间距（竖向布局：depth -> y）
  var COLX = 212;      // 叶子横向间距（竖向布局：兄弟 -> x）
  var MARGIN_X = 56;
  var MARGIN_Y = 40;
  var MAXW = 260;      // 节点最大宽度
  var MINW = 96;
  var CHARW = 13;      // 每字符近似宽度
  var DEFAULT_ZOOM = 1.32; // 默认放大倍数（竖排长图默认放大，字号更清晰）

  var data = null;
  var curMap = null;
  var collapsed = {};  // id -> true 表示收起
  var tf = { x: MARGIN_X, y: MARGIN_Y, k: DEFAULT_ZOOM };
  var didInitialFit = false;
  var dragging = false, moved = false, lastX = 0, lastY = 0;

  function hexToRgba(hex, a) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(function (c) { return c + c; }).join('');
    var n = parseInt(hex, 16);
    return 'rgba(' + ((n >> 16) & 255) + ',' + ((n >> 8) & 255) + ',' + (n & 255) + ',' + a + ')';
  }

  function nodeWidth(name) {
    var w = name.length * CHARW + 26;
    return Math.max(MINW, Math.min(MAXW, w));
  }

  function wrapText(name, maxChars) {
    if (name.length <= maxChars) return [name];
    var lines = [], cur = '';
    for (var i = 0; i < name.length; i++) {
      var ch = name[i];
      if (cur.length >= maxChars && ch !== '、' && ch !== '，' && ch !== ' ') {
        lines.push(cur); cur = '';
      }
      cur += ch;
    }
    if (cur) lines.push(cur);
    return lines;
  }

  function colorOf(node) {
    return node._color || node.color || (node._parent ? colorOf(node._parent) : '#0d9488');
  }

  // 构建带 parent/color/id 的节点树
  function buildTree(map) {
    var root = { name: map.root, color: map.rootColor, id: map.id + '/r', _isRoot: true, children: map.branches };
    function attach(parent, children) {
      (children || []).forEach(function (c, i) {
        c._parent = parent;
        c.id = parent.id + '-' + i;
        if (!c.color && parent.color && !parent._isRoot) c._color = parent.color;
        attach(c, c.children);
      });
    }
    attach(root, map.branches);
    return root;
  }

  // 竖向布局：depth -> y（自上而下），兄弟按中序铺开 -> x（自左而右），父节点居中于子节点
  function layout(root) {
    var nodes = [];
    var leafCursor = 0; // 叶子横向游标，按实际宽度累加避免重叠(串)
    function walk(node, depth) {
      var w = nodeWidth(node.name);
      var maxChars = Math.floor((w - 16) / CHARW);
      var lines = wrapText(node.name, maxChars);
      node._w = w;
      node._h = lines.length * 17 + 14;
      node._lines = lines;
      var n = { node: node, depth: depth, x: 0, y: MARGIN_Y + depth * ROWDEPTH };
      nodes.push(n);
      var kids = (collapsed[node.id] ? [] : (node.children || []));
      if (!kids.length) {
        n.x = MARGIN_X + leafCursor + w / 2;
        leafCursor += w + 30;
      } else {
        var childNs = kids.map(function (c) { return walk(c, depth + 1); });
        n.x = (childNs[0].x + childNs[childNs.length - 1].x) / 2;
      }
      return n;
    }
    walk(root, 0);
    // 归一化到 (0,0) 起
    var minX = Infinity, minY = Infinity;
    nodes.forEach(function (n) {
      minX = Math.min(minX, n.x - n.node._w / 2);
      minY = Math.min(minY, n.y - n.node._h / 2);
    });
    nodes.forEach(function (n) { n.x -= minX; n.y -= minY; });
    return nodes;
  }

  function measure() {
    var nodes = layout(buildTree(curMap));
    var W = 0, H = 0;
    nodes.forEach(function (n) {
      W = Math.max(W, n.x + n.node._w / 2);
      H = Math.max(H, n.y + n.node._h / 2);
    });
    return { W: W + MARGIN_X, H: H + MARGIN_Y };
  }

  function renderSVG() {
    var stage = document.getElementById('mmStage');
    var empty = document.getElementById('mmEmpty');
    if (empty) empty.style.display = 'none';
    document.getElementById('mmToolbar').style.display = '';

    var root = buildTree(curMap);
    var nodes = layout(root);

    var W = 0, H = 0;
    nodes.forEach(function (n) {
      W = Math.max(W, n.x + n.node._w / 2);
      H = Math.max(H, n.y + n.node._h / 2);
    });
    W += MARGIN_X; H += MARGIN_Y;

    var edges = '', boxes = '';
    nodes.forEach(function (n) {
      var node = n.node;
      var cy = n.y, cx = n.x; // cx/cy 为中心点
      // 边（竖向：父底 -> 子顶）
      if (node._parent) {
        var p = node._parent;
        var x1 = p._x, y1 = p._y + p._h / 2;
        var x2 = cx, y2 = cy - node._h / 2;
        var my = (y1 + y2) / 2;
        edges += '<path d="M' + x1 + ',' + y1 + ' C' + x1 + ',' + my + ' ' + x2 + ',' + my + ' ' + x2 + ',' + y2 +
          '" stroke="' + hexToRgba(colorOf(node), 0.5) + '" stroke-width="1.6" fill="none"/>';
      }
      node._x = cx; node._y = cy;
      // 框
      var col = colorOf(node);
      var fill = node._isRoot ? col : hexToRgba(col, 0.14);
      var txtColor = node._isRoot ? '#fff' : '#1f2937';
      var hasKids = (node.children || []).length > 0;
      var rx = cx - node._w / 2, ry = cy - node._h / 2;
      boxes += '<g class="mm-node" data-id="' + node.id + '">';
      boxes += '<rect x="' + rx + '" y="' + ry + '" width="' + node._w + '" height="' + node._h +
        '" fill="' + fill + '" stroke="' + col + '" stroke-width="' + (node._isRoot ? 2.2 : 1.5) + '" rx="10" ry="10"/>';
      var tspans = '';
      node._lines.forEach(function (ln, li) {
        var ty = ry + 16 + li * 17;
        tspans += '<tspan x="' + cx + '" y="' + ty + '" text-anchor="middle" fill="' + txtColor + '">' + esc(ln) + '</tspan>';
      });
      boxes += '<text font-size="13.5">' + tspans + '</text>';
      if (hasKids) {
        var tag = collapsed[node.id] ? '＋' : '－';
        boxes += '<text class="mm-toggle" x="' + (rx + node._w - 10) + '" y="' + (ry + node._h - 6) + '" text-anchor="end">' + tag + '</text>';
      }
      boxes += '</g>';
    });

    stage.innerHTML =
      '<svg id="mmSvg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">' +
      '<g id="mmRoot" transform="translate(' + tf.x + ',' + tf.y + ') scale(' + tf.k + ')">' +
      edges + boxes + '</g></svg>';

    bindSVG();
    if (!didInitialFit) { initialZoom(W, H); didInitialFit = true; }
  }

  // 默认放大：固定 DEFAULT_ZOOM，字号清晰；图宽于视口则左上对齐，靠拖拽查看其余部分
  function initialZoom(W, H) {
    var stage = document.getElementById('mmStage');
    var sw = stage.clientWidth || 1000;
    tf.k = DEFAULT_ZOOM;
    tf.x = Math.max(8, (sw - W * DEFAULT_ZOOM) / 2);
    tf.y = 18;
    applyTf();
  }

  function applyTf() {
    var g = document.getElementById('mmRoot');
    if (g) g.setAttribute('transform', 'translate(' + tf.x + ',' + tf.y + ') scale(' + tf.k + ')');
  }

  var windowBound = false;
  function bindSVG() {
    var svg = document.getElementById('mmSvg');
    if (!svg) return;
    if (!windowBound) {
      windowBound = true;
      window.addEventListener('mousemove', function (e) {
        if (!dragging) return;
        var dx = e.clientX - lastX, dy = e.clientY - lastY;
        if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
        tf.x += dx; tf.y += dy; lastX = e.clientX; lastY = e.clientY;
        applyTf();
      });
      window.addEventListener('mouseup', function () {
        dragging = false;
        var svg2 = document.getElementById('mmSvg');
        if (svg2) svg2.classList.remove('grabbing');
      });
    }
    svg.addEventListener('wheel', function (e) {
      e.preventDefault();
      var rect = svg.getBoundingClientRect();
      var mx = e.clientX - rect.left, my = e.clientY - rect.top;
      var factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
      tf.x = mx - (mx - tf.x) * factor;
      tf.y = my - (my - tf.y) * factor;
      tf.k *= factor;
      applyTf();
    }, { passive: false });

    svg.addEventListener('mousedown', function (e) {
      dragging = true; moved = false; lastX = e.clientX; lastY = e.clientY;
      svg.classList.add('grabbing');
    });

    svg.addEventListener('click', function (e) {
      if (moved) return;
      var g = e.target.closest('.mm-node');
      if (!g) return;
      var id = g.getAttribute('data-id');
      var node = findNode(curMap, id);
      if (node && (node.children || []).length) {
        if (collapsed[id]) delete collapsed[id]; else collapsed[id] = true;
        didInitialFit = true; // 折叠后保持当前视图
        renderSVG();
      }
    });
  }

  function findNode(map, id) {
    var root = buildTree(map);
    var stack = [root];
    while (stack.length) {
      var n = stack.pop();
      if (n.id === id) return n;
      (n.children || []).forEach(function (c) { stack.push(c); });
    }
    return null;
  }

  // 窄屏树形列表
  function renderList() {
    var stage = document.getElementById('mmStage');
    document.getElementById('mmToolbar').style.display = 'none';
    var root = buildTree(curMap);
    function nodeHTML(node) {
      var col = colorOf(node);
      var kids = (collapsed[node.id] ? [] : (node.children || []));
      var has = (node.children || []).length > 0;
      var caret = has ? (collapsed[node.id] ? '▸' : '▾') : '';
      var inner = '<div class="mm-li-head" data-id="' + node.id + '">' +
        '<span class="caret">' + caret + '</span>' +
        '<span class="dot" style="background:' + col + '"></span>' +
        '<span>' + esc(node.name) + '</span></div>';
      var html = '<li class="mm-li">' + inner;
      if (has && !collapsed[node.id]) {
        html += '<ul>' + kids.map(nodeHTML).join('') + '</ul>';
      }
      html += '</li>';
      return html;
    }
    stage.innerHTML = '<div class="mm-list"><ul>' + nodeHTML(root) + '</ul></div>';
    stage.querySelectorAll('.mm-li-head').forEach(function (h) {
      h.addEventListener('click', function () {
        var id = h.getAttribute('data-id');
        var node = findNode(curMap, id);
        if (node && (node.children || []).length) {
          if (collapsed[id]) delete collapsed[id]; else collapsed[id] = true;
          renderList();
        }
      });
    });
  }

  function render() {
    if (!curMap) return;
    if (window.innerWidth <= 768) renderList();
    else renderSVG();
  }

  function buildTabs() {
    var box = document.getElementById('mmTabs');
    box.innerHTML = data.maps.map(function (m, i) {
      return '<button class="mm-tab ' + (i === 0 ? 'active' : '') + '" data-i="' + i + '">' + esc(m.title) + '</button>';
    }).join('');
    box.querySelectorAll('.mm-tab').forEach(function (b) {
      b.addEventListener('click', function () {
        box.querySelectorAll('.mm-tab').forEach(function (x) { x.classList.remove('active'); });
        b.classList.add('active');
        curMap = data.maps[+b.getAttribute('data-i')];
        didInitialFit = false; // 切换地图重新按默认放大铺开
        render();
      });
    });
  }

  // 暴露给工具栏
  window.mm = {
    zoomBy: function (f) {
      var stage = document.getElementById('mmStage');
      var mx = stage.clientWidth / 2, my = stage.clientHeight / 2;
      tf.x = mx - (mx - tf.x) * f;
      tf.y = my - (my - tf.y) * f;
      tf.k *= f; applyTf();
    },
    fit: function () {
      var m = measure();
      var stage = document.getElementById('mmStage');
      var sw = stage.clientWidth || 1000, sh = stage.clientHeight || 700;
      var k = Math.min(sw / m.W, sh / m.H);
      tf.k = k; tf.x = (sw - m.W * k) / 2; tf.y = Math.max(10, (sh - m.H * k) / 2);
      applyTf();
    },
    reset: function () {
      var m = measure();
      didInitialFit = true;
      initialZoom(m.W, m.H);
    },
    expandAll: function () { collapsed = {}; didInitialFit = false; render(); },
    collapseAll: function () {
      collapsed = {};
      buildTree(curMap).children.forEach(function (c) { collapsed[c.id] = true; });
      didInitialFit = false; render();
    }
  };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function init() {
    fetch('data/mindmap.json').then(function (r) { return r.json(); }).then(function (j) {
      data = j;
      buildTabs();
      curMap = data.maps[0];
      render();
    }).catch(function (e) {
      document.getElementById('mmStage').innerHTML = '<div class="mm-empty">加载失败：' + esc(e.message) + '<br>请用 http 方式访问（start.bat 本地服务或 GitHub Pages），勿用 file:// 直接打开。</div>';
    });
  }

  window.addEventListener('resize', function () {
    if (!curMap) return;
    clearTimeout(window._mmRz);
    window._mmRz = setTimeout(render, 200);
  });

  init();
})();
