/* Olive Palestine: the loader, arrivals on scroll and the season line.
   Everything is readable without it; this only adds motion. */
(function () {
  'use strict';
  var doc = document.documentElement;
  var still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  doc.classList.add('js');

  /* ------------------------------------------------------------ loader: laying the walls
     The mark is built the way a terrace is: the outer wall first, stone by stone from the low side,
     then each wall above it, then the stone on the summit drops into place. The finished mark then
     moves into the masthead, where the same drawing sits in the wordmark. Once per session. */
  function loader() {
    var el = document.querySelector('.loader');
    if (!el) return;
    if (!doc.classList.contains('loading')) { el.remove(); return; }
    var M = window.OP_MARKS && window.OP_MARKS.mark;
    var NS = 'http://www.w3.org/2000/svg';
    var svg = el.querySelector('svg');
    var put = function (tag, attrs, parent) {
      var n = document.createElementNS(NS, tag);
      for (var k in attrs) n.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(n);
      return n;
    };
    var laid = [];
    M.stones.forEach(function (wall, k) {
      wall.forEach(function (d) {
        laid.push(put('path', { d: d, 'class': 'stone-l', 'stroke-width': k ? M.wall : M.skin }));
      });
    });
    var stalk = put('path', { d: M.stalk, 'class': 'stalk-l', 'stroke-width': M.skin * 0.8 });
    var len = stalk.getTotalLength();
    stalk.style.strokeDasharray = len;
    stalk.style.strokeDashoffset = len;
    var summit = put('path', { d: M.summit, 'class': 'summit-l' });
    var note = el.querySelector('p');

    var t = 120, done = false;
    laid.forEach(function (s, i) { setTimeout(function () { s.classList.add('in'); }, t + i * 17); });
    t += laid.length * 17;
    setTimeout(function () {
      stalk.style.transition = 'stroke-dashoffset .4s cubic-bezier(.2,.7,.2,1)';
      stalk.style.strokeDashoffset = 0;
    }, t - 160);
    setTimeout(function () { summit.classList.add('in'); }, t + 40);
    setTimeout(function () { note && note.classList.add('in'); }, 300);
    var timer = setTimeout(finish, t + 640);

    function finish() {
      if (done) return;
      done = true;
      clearTimeout(timer);
      try { sessionStorage.setItem('op-built', '1'); } catch (e) {}
      var target = document.querySelector('.mast .brand svg');
      var W = window.OP_MARKS.wordmark;
      if (target && !still) {
        // land the loader's olive on the wordmark's olive
        var tb = target.getBoundingClientRect(), lb = svg.getBoundingClientRect();
        var u = tb.width / W.w, v = lb.width / M.w;           // px per unit, target and loader
        var k = (u * W.m[2]) / (v * M.size);
        var tx = tb.left + W.m[0] * u, ty = tb.top + W.m[1] * u;
        var sx = lb.left + M.cx * v, sy = lb.top + M.cy * v;
        svg.style.transition = 'transform .75s cubic-bezier(.65,0,.25,1)';
        svg.style.transformOrigin = (M.cx / M.w * 100) + '% ' + (M.cy / M.h * 100) + '%';
        svg.style.transform = 'translate(' + (tx - sx) + 'px,' + (ty - sy) + 'px) scale(' + k + ')';
        note && note.classList.remove('in');
        el.classList.add('flying');
        setTimeout(function () { el.classList.add('out'); doc.classList.remove('loading'); }, 560);
        setTimeout(function () { el.remove(); }, 1150);
      } else {
        el.classList.add('out');
        doc.classList.remove('loading');
        setTimeout(function () { el.remove(); }, 600);
      }
    }
    el.addEventListener('click', finish);
    window.addEventListener('keydown', finish, { once: true });
  }

  /* ------------------------------------------------------------ arrivals */
  function arrivals() {
    var els = document.querySelectorAll('.rise, .course.lay, .season, [data-count]');
    if (still || !('IntersectionObserver' in window)) {
      els.forEach(function (e) { e.classList.add('seen'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var e = en.target;
        io.unobserve(e);
        var d = doc.classList.contains('loading') ? 1500 : 0;
        setTimeout(function () {
          e.classList.add('seen');
          if (e.hasAttribute('data-count')) count(e);
        }, d);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    els.forEach(function (e) { io.observe(e); });
  }

  // a figure counts up to its value; the text in the HTML is already the final value
  function count(e) {
    var to = parseFloat(e.getAttribute('data-count'));
    var n = e.querySelector('.v') || e;
    var t0 = performance.now(), dur = 900;
    (function step(t) {
      var p = Math.min(1, (t - t0) / dur);
      n.textContent = Math.round(to * (1 - Math.pow(1 - p, 3))).toLocaleString('en-GB');
      if (p < 1) requestAnimationFrame(step);
    })(t0);
  }

  loader();
  arrivals();
})();
