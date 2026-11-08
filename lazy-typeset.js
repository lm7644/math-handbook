/* ================================================================
   lazy-typeset.js — MathJax 惰性排版（首屏不等全量渲染）
   ----------------------------------------------------------------
   背景：教科书版 textbook.html 有 5799 个公式容器，一次性排版耗时
   17s+，首屏被拖住。本脚本把 MathJax 改成「按需排版」：

   1) 深链：#tb00-s3 / #eq-1-2 这类锚点，先把「目标之前的全部单元 +
      目标所在单元 + 紧随其后的一个单元」排完，再定位，落点才准；
   2) 首屏：视口上下各留一屏，视口内的单元最先排（直接排，不等 idle）；
   3) 其余：requestIdleCallback 分批后台排版；用户滚动时按新视口重排
      优先级，滚到哪排到哪；
   4) 打印：打印按钮与 Ctrl/Cmd+P 走「展开折叠答案 → 全量排版 →
      window.print()」；浏览器菜单打印在 beforeprint 里尽力补齐；
   5) 无 JS：本脚本不隐藏任何内容，公式的 TeX 原文始终可读，
      模板另配 <noscript> 提示。
   ================================================================ */
(function () {
  'use strict';

  var MATH_RE = /\\[\(\[]/;                 // 匹配 \( 或 \[
  var BATCH = 8;                            // 每批排版单元数（批越大越快、单次卡顿越久）
  var ZONE_UP = 0.6, ZONE_DOWN = 1.7;       // 视口上/下各留几屏

  var MJ = null;
  var queue = [];
  var deferred = [];                        // 深链时目标章之前的单元，暂不进后台队列
  var doneSet = new Set();
  var busy = false;
  var finished = false;
  var started = false;
  var allDoneWaiters = [];

  /* ---------- 通用 ---------- */
  function roots() {
    var out = [];
    var cover = document.querySelector('.cover');
    var mast = document.querySelector('.masthead-sec');
    if (cover) out.push(cover);
    if (mast) out.push(mast);
    Array.prototype.push.apply(out, document.querySelectorAll('.chapter'));
    return out;
  }
  function hasMath(el) { var t = el.textContent; return !!(t && MATH_RE.test(t)); }
  function targetEl() {
    var h = window.location.hash;
    if (!h || h.length < 2) return null;
    var id;
    try { id = decodeURIComponent(h.slice(1)); } catch (e) { return null; }
    return document.getElementById(id);
  }
  /* 落点钉住：深链目标上方的章节仍在后台排版，版面持续长高会把落点顶走。
     逐帧比对目标与它的 scroll-margin，偏差大于 2px 就补回；用户一动就永久让位。 */
  function stickTarget() {
    if (!targetEl()) return;
    var released = false;
    var stop = function () { released = true; };
    ['wheel', 'touchmove', 'keydown', 'mousedown'].forEach(function (ev) {
      window.addEventListener(ev, stop, { passive: true, once: true });
    });
    var t0 = performance.now();
    function correct() {
      if (released) return;
      var el = targetEl(); if (!el) return;
      var goal = parseFloat(getComputedStyle(el).scrollMarginTop) || 0;
      var d = el.getBoundingClientRect().top - goal;
      // 用 scrollBy 补相等位移：目标被上方排版顶下多少就补回多少，不做二次定位
      if (Math.abs(d) > 2) window.scrollBy(0, d);
    }
    correct();
    (function frame() {
      if (released || performance.now() - t0 > 12000) return;
      correct();
      requestAnimationFrame(frame);
    })();
    // 页面被切到后台时 rAF 会暂停，用低频定时器兜底
    var iv = setInterval(function () {
      correct();
      if (released || performance.now() - t0 > 12000) clearInterval(iv);
    }, 400);
  }

  /* ---------- 1) 把章节顶层的裸文本公式包成块/行内元素 ----------
     章节源码里不少 display 公式直接写在 <section> 下（不在 <p> 里），
     属于裸文本节点。包一层后它们才能作为独立单元参与惰性排版；
     包法：含 \[ 的用 div（块级，与原来的换行效果一致），
     只含 \( 的用 span（行内，保持行文不断行）。 */
  function wrapBareMath(root) {
    var texts = [];
    for (var n = root.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3 && MATH_RE.test(n.nodeValue)) texts.push(n);
    }
    texts.forEach(function (t) {
      var v = t.nodeValue;
      var isBlock = /\\\[/.test(v);
      var w = document.createElement(isBlock ? 'div' : 'span');
      w.className = isBlock ? 'mj-block' : 'mj-inline';
      root.replaceChild(w, t);
      w.appendChild(t);
    });
  }
  roots().forEach(wrapBareMath);

  /* ---------- 2) 收集排版单元 ----------
     单元 = 章节顶层块（p / 卡片 div / figure / table / 公式块 …）。
     折叠的 <details>（自测答案）先跳过：隐藏容器里 MathJax 量不准宽度，
     展开时再排（见 toggle 监听）。含折叠 details 的容器继续下钻，
     避免「排父容器顺带排了隐藏内容」。 */
  function collectFrom(container, out) {
    var kids = container.children;
    for (var i = 0; i < kids.length; i++) {
      var k = kids[i];
      if (k.tagName === 'DETAILS' && !k.open) continue;
      if (!hasMath(k)) { if (k.children.length) collectFrom(k, out); continue; }
      if (k.querySelector && k.querySelector('details:not([open])')) { collectFrom(k, out); continue; }
      out.push(k);
    }
    return out;
  }
  function collectAll() {
    var out = [];
    roots().forEach(function (r) { collectFrom(r, out); });
    return out;
  }

  /* ---------- 3) 视口优先 ---------- */
  function inZone(el) {
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight || 800;
    return r.top < vh * ZONE_DOWN && r.bottom > -vh * ZONE_UP;
  }
  function prioritize() {
    pullDeferred();
    if (finished || !queue.length) return;
    var hits = queue.filter(inZone);
    if (!hits.length) return;
    queue = hits.concat(queue.filter(function (u) { return hits.indexOf(u) < 0; }));
  }
  /* 暂存的「目标章之前」单元，只有真的滚到它们附近才放回队列 */
  function pullDeferred() {
    if (!deferred.length) return;
    var pull = [], keep = [];
    deferred.forEach(function (u) { (inZone(u) ? pull : keep).push(u); });
    if (!pull.length) return;
    deferred = keep;
    queue = pull.concat(queue);
    finished = false;
    document.documentElement.removeAttribute('data-mj-typeset');
  }

  /* ---------- 4) 分批排版 ---------- */
  function finishAll() {
    document.documentElement.setAttribute('data-mj-typeset', 'done');
    var w = allDoneWaiters; allDoneWaiters = [];
    w.forEach(function (f) { try { f(); } catch (e) {} });
  }
  function step() {
    if (finished || busy || !started) return;
    if (!queue.length) { finished = true; finishAll(); return; }
    busy = true;
    var batch = queue.splice(0, BATCH).filter(function (u) { return !doneSet.has(u); });
    if (!batch.length) { busy = false; step(); return; }
    batch.forEach(function (u) { doneSet.add(u); });
    MJ.typesetPromise(batch).then(function () {
      busy = false;
      if (!queue.length) { finished = true; finishAll(); } else schedule();
    }, function (err) {
      busy = false;
      if (window.console && console.warn) console.warn('[lazy-typeset] 排版失败', err && (err.message || err));
      schedule();
    });
  }
  function schedule() {
    if (finished || busy) return;
    if (window.requestIdleCallback) {
      window.requestIdleCallback(function () { step(); }, { timeout: 700 });
    } else {
      setTimeout(step, 80);
    }
  }

  /* ---------- 5) 滚动/尺寸变化后重排优先级 ---------- */
  var scrollTimer = null;
  function onScroll() {
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function () { prioritize(); schedule(); }, 90);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });

  /* ---------- 6) 深链：先排目标之前的单元 ---------- */
  function unitOf(el, root) {
    var p = el;
    while (p && p.parentElement !== root) p = p.parentElement;
    return p;
  }
  function deepLink() {
    var el = targetEl();
    if (!el) return Promise.resolve();
    var root = el.closest('.chapter') || el.closest('.cover') || el.closest('.masthead-sec');
    if (!root) return Promise.resolve();
    var all = collectFrom(root, []);
    var units = all.filter(function (u) { return u.contains(el); });
    // 目标之前的单元（它们在页面上方，尺寸变化会顶动落点）
    all.forEach(function (u) {
      if (u.contains(el)) return;
      if (u.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) units.push(u);
    });
    // 目标之后紧邻的第一个单元（目标是零宽锚点时，它下面那条公式要跟着排）
    for (var j = 0; j < all.length; j++) {
      var u = all[j];
      if (u.contains(el)) break;
      if (u.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_PRECEDING) { units.push(u); break; }
    }
    if (!units.length) return Promise.resolve();
    units = units.filter(function (u, i) { return units.indexOf(u) === i; });
    units.forEach(function (u) {
      doneSet.add(u);
      var i = queue.indexOf(u); if (i > -1) queue.splice(i, 1);
    });
    /* 目标章之前的单元全部暂存：读者停在目标处阅读时，上方章节若继续排版
       会把整页顶高、落点反复漂移；等读者真的往上滚，pullDeferred() 会按需放回。 */
    deferred = [];
    queue = queue.filter(function (u) {
      if (root.compareDocumentPosition(u) & Node.DOCUMENT_POSITION_PRECEDING) { deferred.push(u); return false; }
      return true;
    });
    return MJ.typesetPromise(units).then(function () {
      setTimeout(function () {
        stickTarget();
        prioritize();   // 落点视口里的单元提到队首，别让读者看几秒裸 TeX
        step();
      }, 30);
    }, function () { setTimeout(stickTarget, 30); });
  }

  /* ---------- 7) 打印：全量排版后再调打印 ---------- */
  var printBusy = false;
  function openDetails() {
    var opened = [];
    Array.prototype.forEach.call(document.querySelectorAll('details:not([open])'), function (d) {
      d.setAttribute('open', '');
      opened.push(d);
    });
    return opened;
  }
  function printFlow() {
    if (printBusy) return Promise.resolve();
    printBusy = true;
    openDetails();
    var pending = [];
    collectAll().forEach(function (u) {
      if (doneSet.has(u)) return;
      doneSet.add(u);
      var i = queue.indexOf(u); if (i > -1) queue.splice(i, 1);
      pending.push(u);
    });
    if (!queue.length && !pending.length) finished = true;
    var p = pending.length ? MJ.typesetPromise(pending) : Promise.resolve();
    return p.then(function () {
      return new Promise(function (res) {
        requestAnimationFrame(function () { setTimeout(function () { window.print(); printBusy = false; res(); }, 60); });
      });
    }, function () { printBusy = false; });
  }
  function bindPrint() {
    Array.prototype.forEach.call(document.querySelectorAll('.sidenav .tools button[onclick]'), function (b) {
      if (!/window\.print\(\)/.test(b.getAttribute('onclick') || '')) return;
      b.removeAttribute('onclick');
      b.addEventListener('click', function (e) {
        e.preventDefault();
        var old = b.innerHTML;
        b.disabled = true;
        b.textContent = '公式排版中…';
        printFlow().then(function () { b.innerHTML = old; b.disabled = false; });
      });
    });
    // Ctrl/Cmd+P 在浏览器打印对话框出现前拦下，先排完再打印
    window.addEventListener('keydown', function (e) {
      if ((e.ctrlKey || e.metaKey) && !e.altKey && (e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        printFlow();
      }
    }, true);
    // 浏览器菜单打印：来不及异步排版，只能尽力补齐（下不为例地先把后续单元排掉）
    window.addEventListener('beforeprint', function () {
      if (finished || printBusy) return;
      openDetails();
      var units = [];
      collectAll().forEach(function (u) { if (!doneSet.has(u)) units.push(u); });
      units.forEach(function (u) { doneSet.add(u); });
      if (units.length) MJ.typesetPromise(units);
    });
  }

  /* ---------- 8) 自测题答案展开时补排 ---------- */
  document.addEventListener('toggle', function (e) {
    var d = e.target;
    if (!d || d.tagName !== 'DETAILS' || !d.open || !MJ) return;
    var units = collectFrom(d, []);
    if (!units.length) return;
    units.forEach(function (u) { doneSet.add(u); });
    MJ.typesetPromise(units);
  }, true);

  /* ---------- 9) 启动 ---------- */
  function boot() {
    if (started) return;
    MJ = window.MathJax;
    if (!MJ || typeof MJ.typesetPromise !== 'function') return;   // MathJax 没起来：保留 TeX 原文
    started = true;
    document.documentElement.setAttribute('data-mj-ready', '1');
    queue = collectAll();
    bindPrint();
    deepLink();
    prioritize();
    step();        // 视口单元直接排，不等 idle
    schedule();    // 其余后台分批
  }
  function waitMathJax() {
    if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
      window.MathJax.startup.promise.then(boot, boot);
      return;
    }
    var tries = 0;
    var iv = setInterval(function () {
      if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
        clearInterval(iv);
        window.MathJax.startup.promise.then(boot, boot);
      } else if (++tries > 400) {
        clearInterval(iv);   // 约 12s 仍未就绪：放弃，页面保持 TeX 原文
      }
    }, 30);
  }
  waitMathJax();
})();
