"""Build index.html, the identity book, and assets/olive-palestine-identity.zip.

python -I tools/book.py   (after brand.py and build.py)

The book explains the identity to the client: the idea, the mark and how it is drawn, the
wordmark, colour, type, the course and the season line, motion, photography, and the files.
It uses the site's own stylesheet plus assets/css/book.css, and the real marks from brand.py.
"""
import json
import math
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import brand  # noqa: E402
import build  # noqa: E402
from build import E, V, esc, wordmark, season_svg, SPRITE, icon, photo  # noqa: E402

ROOT = build.ROOT
M = build.MARKS['mark']


def mk(size=200, bg=None, ink=brand.INK, soil=brand.SOIL, walls=3):
    return brand.svg(64, 64, brand.mark(M['cx'], M['cy'], M['size'], walls=walls, ink=ink, soil=soil), bg).replace(
        f'width="64" height="64"', f'width="{size}" height="{size}"')


def idea():
    """Three drawings: the olive, the terraced hill seen from above, and the two as one."""
    cx, cy, s = 150, 128, 92
    olive = (f'<path d="{brand.wall(0, cx, cy, s)}" fill="#3A2C36"/>'
             f'<path d="{brand.stalk(cx, cy, s)}" fill="none" stroke="#3A2C36" stroke-width="{s * .1:.1f}" stroke-linecap="round"/>'
             f'<path d="{brand.poly([brand.place((0.12 * math.cos(2 * math.pi * i / 60) * 2.2 + .06, 0.12 * math.sin(2 * math.pi * i / 60) * .9), cx, cy, s) for i in range(60)])}" fill="#7B6A58" opacity=".55"/>')
    hill = brand.contours(300, 256, cx + 10, cy + 6, 30, n=9, color='#8E7F6C', width=1.2)
    hill = hill[hill.index('>') + 1:hill.rindex('</svg>')] + f'<path d="{brand.summit(cx + 10, cy + 6, 30)}" fill="#7B6A58"/>'
    both = brand.mark(cx, cy, s)
    cell = lambda body, cap: (f'<figure class="i-cell"><svg viewBox="0 0 300 256" role="img" aria-label="{esc(cap)}">{body}</svg>'
                              f'<figcaption>{cap}</figcaption></figure>')
    return (cell(olive, 'An olive on its stalk: skin, flesh, stone')
            + cell(hill, 'A terraced hill from above: walls close together on the steep face, the village on top')
            + cell(both, 'The mark: the skin is the outer wall, the summit is the stone'))


def construction():
    """The mark drawn large, with its geometry shown: the outline, each wall's scale, the up-slope shift."""
    cx, cy, s = 330, 300, 168
    g = []
    a = math.radians(brand.TILT)
    ax = lambda t: (cx + t * math.cos(a) * s, cy + t * math.sin(a) * s)
    x0, y0 = ax(-1.25)
    x1, y1 = ax(1.6)
    g.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" class="c-axis"/>')
    for k, sc in enumerate(brand.WALLS):
        p = brand.place(brand.egg(math.pi / 2 * 0 + 0.0, sc), cx, cy, s)
        lab = 'skin · 1.00' if k == 0 else f'wall {k} · {sc:.2f}'
        q = brand.place(brand.egg(math.pi * 0.98, sc), cx, cy, s)
        ly = 470 + k * 26
        g.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="3.5" class="c-pt"/><path d="M{q[0]:.1f} {q[1]:.1f}V{ly - 4}H{36 + 110}" class="c-axis"/>'
                 f'<text x="36" y="{ly}" class="c-t">{lab}</text>')
    sx, sy = brand.place(brand.UPHILL, cx, cy, s)
    g.append(f'<line x1="{cx}" y1="{cy}" x2="{sx:.1f}" y2="{sy:.1f}" class="c-up" marker-end="url(#arr)"/>'
             f'<circle cx="{cx}" cy="{cy}" r="3.5" class="c-pt"/>'
             f'<text x="604" y="522" class="c-t" text-anchor="end">red: up-slope, to the summit</text>')
    g.append(f'<text x="{x0 - 4:.1f}" y="{y0 + 22:.1f}" class="c-t">tilt {abs(brand.TILT)}°</text>')
    return (f'<svg viewBox="0 90 640 470" role="img" aria-label="How the mark is drawn"><defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 10 5 0 10z" fill="#A3412A"/></marker></defs>'
            f'{brand.mark(cx, cy, s)}<g>{"".join(g)}</g></svg>')


SW = [('Limestone', '#EFE9DC', 'The page. The pale stone of the walls and the villages.', 'ink'),
      ('Black olive', '#231B21', 'Text, the mark, dark grounds. A ripe Nabali, not pure black.', 'stone'),
      ('Terra rossa', '#A3412A', 'The red soil under the trees. Only for now: today, the summit, the live date.', 'stone'),
      ('Olive leaf', '#46532E', 'The grove. Kept for maps and the rare green note; never a ground.', 'stone'),
      ('Sunk course', '#E6DECD', 'Panels set back from the page.', 'ink'),
      ('Soil on dark', '#D2603F', 'Terra rossa lifted for black grounds: marks and large type only.', 'ink')]


def swatches():
    return ''.join(f'<li><span class="sw" style="background:{h};color:{"#231B21" if t == "ink" else "#EFE9DC"}"><b>{n}</b><code>{h}</code></span>'
                   f'<p>{esc(d)}</p></li>' for n, h, d, t in SW)


def loader_demo():
    return ('<div class="demo"><svg class="lay" viewBox="0 0 64 64" role="img" aria-label="The loader: the mark is built stone by stone"></svg>'
            '<button class="btn ghost" type="button" id="relay">Lay the walls again</button></div>')


BOOK_JS = """
(function(){
  var M = window.OP_MARKS.mark, NS = 'http://www.w3.org/2000/svg', svg = document.querySelector('.demo .lay');
  if (!svg) return;
  function run(){
    svg.innerHTML = '';
    var put = function(tag, a){ var n = document.createElementNS(NS, tag); for (var k in a) n.setAttribute(k, a[k]); svg.appendChild(n); return n; };
    var st = [];
    M.stones.forEach(function(w, k){ w.forEach(function(d){ st.push(put('path', {d: d, 'class': 'stone-l', 'stroke-width': k ? M.wall : M.skin})); }); });
    var sk = put('path', {d: M.stalk, 'class': 'stalk-l', 'stroke-width': M.skin * .8}), L = sk.getTotalLength();
    sk.style.strokeDasharray = L; sk.style.strokeDashoffset = L;
    var sm = put('path', {d: M.summit, 'class': 'summit-l'});
    var t = 200;
    st.forEach(function(s, i){ setTimeout(function(){ s.classList.add('in'); }, t + i * 34); });
    t += st.length * 34;
    setTimeout(function(){ sk.style.transition = 'stroke-dashoffset .5s'; sk.style.strokeDashoffset = 0; }, t);
    setTimeout(function(){ sm.classList.add('in'); }, t + 300);
  }
  var io = new IntersectionObserver(function(e){ if (e[0].isIntersecting){ run(); io.disconnect(); } }, {threshold: .5});
  io.observe(svg);
  document.getElementById('relay').addEventListener('click', run);
})();
"""


def chapters():
    pb = E['stories'][E['lead']].get('photo')
    ph = photo(pb, sizes='(max-width:900px) 100vw, 50vw', cap=True)
    return f'''
<header class="cover ink"><div class="wrap">
  <div class="cover-mark">{mk(300, ink="#EFE9DC", soil="#D2603F")}</div>
  <div class="cover-copy">
    <p class="lbl">Identity · first edition · {build.long_day(build.TODAY)}</p>
    <h1>Olive Palestine</h1>
    <p class="dek">An identity for a site about the land of Palestine: what is picked, pressed and planted each month, the food made from it, and the heritage kept around it.</p>
    <p class="go"><a class="btn" href="home.html">See the homepage {icon("i-right")}</a></p>
  </div>
</div></header>

<nav class="toc" aria-label="Chapters"><div class="wrap"><ol>
  <li><a href="#idea">The idea</a></li><li><a href="#mark">The mark</a></li><li><a href="#word">The wordmark</a></li>
  <li><a href="#colour">Colour</a></li><li><a href="#type">Type</a></li><li><a href="#course">The course &amp; the season</a></li>
  <li><a href="#motion">Motion</a></li><li><a href="#photo">Photographs</a></li><li><a href="#files">Files</a></li>
</ol></div></nav>

<section class="ch" id="idea"><div class="wrap">
  <div class="ch-head"><p class="ch-n">01</p><h2>The idea</h2><p class="dek">Cut an olive across and you see skin, flesh and a stone. Look down on a terraced hill in Palestine and you see the same drawing: rings of dry-stone walls, crowded where the slope is steep, and the village on the summit.</p></div>
  <div class="ideas">{idea()}</div>
  <div class="cols2">
    <p class="txt">The hills where Palestine's olives grow were built by hand, wall by wall, over centuries: the terraces of Battir, of Sebastia, of every village around Ramallah and Hebron. The site's subject is that land and what comes from it. So the mark is the fruit and the hill at once: its skin is the outer wall, the walls inside it are terraces, and the stone at its heart is the summit.</p>
    <p class="txt">The summit is drawn in <b>terra rossa</b>, the red soil the trees stand in. It is the only red in the identity, and it always means the same thing: <b>here, now</b>. It marks today on the season line, the current month in the archive, the section you are in. The rest of the identity is limestone and black olive, the colours of the walls and the ripe fruit.</p>
  </div>
</div></section>

<section class="ch alt" id="mark"><div class="wrap">
  <div class="ch-head"><p class="ch-n">02</p><h2>The mark</h2><p class="dek">One outline, drawn three times. Each wall is the olive's own outline drawn smaller and moved up the slope, so the walls close up on the steep face, towards the stalk, and open out on the gentle one.</p></div>
  <div class="build">
    <div class="draw">{construction()}</div>
    <dl class="spec">
      <dt>Outline</dt><dd>An egg: half-length 1, half-width {brand.B}, fuller by {int(brand.EGG * 100)}% at the stalk end, hung at {abs(brand.TILT)}° off its stalk.</dd>
      <dt>Walls</dt><dd>The skin at 1.00, then walls at {brand.WALLS[1]:.2f} and {brand.WALLS[2]:.2f}. Each moves towards the summit by the share it shrinks.</dd>
      <dt>Weights</dt><dd>The skin is {brand.SKIN / brand.WALL:.1f} times heavier than the walls, so at small sizes the olive holds and the walls fall back.</dd>
      <dt>Summit</dt><dd>A stone of {brand.SUMMIT:.2f}, always terra rossa on limestone and lifted terra rossa on black olive.</dd>
      <dt>Under 24 px</dt><dd>One wall is dropped: skin, a single terrace and the summit. The favicon uses this drawing.</dd>
    </dl>
  </div>
  <ul class="sizes">
    <li>{mk(160)}<p>Full mark</p></li>
    <li>{mk(64)}<p>64 px</p></li>
    <li>{mk(32, walls=2)}<p>32 px · two walls</p></li>
    <li>{mk(16, walls=2)}<p>16 px</p></li>
    <li class="dk">{mk(120, bg="#231B21", ink="#EFE9DC", soil="#D2603F")}<p>On black olive</p></li>
    <li class="dk">{mk(120, bg="#A3412A", ink="#EFE9DC", soil="#231B21")}<p>On terra rossa: the summit turns black</p></li>
  </ul>
</div></section>

<section class="ch" id="word"><div class="wrap">
  <div class="ch-head"><p class="ch-n">03</p><h2>The wordmark</h2><p class="dek">«Olive» in Literata's display cut, «Palestine» in its italic: one name in two voices, the fruit and the place. The mark stands as tall as the capitals, its stalk rising above them like an ascender.</p></div>
  <div class="wms">
    <div class="wm-l">{wordmark("w1")}</div>
    <div class="wm-l ink">{wordmark("w1", "#EFE9DC", "#D2603F")}</div>
    <div class="wm-s"><img src="assets/brand/wordmark-stack.svg?v={V}" alt="Olive Palestine, stacked lockup" width="240" height="217"></div>
    <div class="wm-rules">
      <p class="txt"><b>Clear space</b> is the height of the summit stone times four on every side. <b>Smallest</b> horizontal lockup: 140 px wide on screen, 30 mm in print; below that, use the mark alone.</p>
      <p class="txt">Never recolour the walls, never set the name in another face, never put the summit in any colour but terra rossa (or black olive on terra rossa).</p>
    </div>
  </div>
</div></section>

<section class="ch alt" id="colour"><div class="wrap">
  <div class="ch-head"><p class="ch-n">04</p><h2>Colour</h2><p class="dek">Stone, fruit and soil. The page is limestone, the voice is black olive, and terra rossa is spent only on what is happening now.</p></div>
  <ul class="swatches">{swatches()}</ul>
  <div class="ratio" aria-label="Proportion of use"><span style="flex:70;background:#EFE9DC">Limestone 70</span><span style="flex:22;background:#231B21;color:#EFE9DC">Black olive 22</span><span style="flex:5;background:#E6DECD">5</span><span style="flex:3;background:#A3412A;color:#EFE9DC">3</span></div>
  <p class="txt small">Text contrast on limestone: black olive 13.9:1, secondary ink #4D4248 7.9:1, captions #64585E 5.6:1, terra rossa 5.2:1. On black olive: limestone 13.9:1, secondary #A89BA3 6.3:1.</p>
</div></section>

<section class="ch" id="type"><div class="wrap">
  <div class="ch-head"><p class="ch-n">05</p><h2>Type</h2><p class="dek">Literata carries the voice. Its display cut, which the browser picks by itself at large sizes, has wedge serifs that read as letters cut into stone; its text cut is built for long reading. Commissioner sets the labels, with a little of its flare.</p></div>
  <div class="spec-type">
    <div class="t1"><p class="lbl">Literata · display cut · 300</p><p class="big">October</p></div>
    <div class="t2"><p class="lbl">Literata · display · 520</p><p class="h-xl">Picking opens on the hills, a week after the presses</p></div>
    <div class="t3"><p class="lbl">Literata · italic</p><p class="it">Pick, press, plant</p></div>
    <div class="t4"><p class="lbl">Literata · text · 17/1.6</p><p class="txt">The agriculture ministry's first estimate for the season is about <b>21,000 tonnes</b> of oil. Sources are set in Literata's own small capitals: <span class="src">WAFA, 21 Oct</span></p></div>
    <div class="t5"><p class="lbl">Commissioner · labels · FLAR 0 → 100</p><p class="flare"><span style="font-variation-settings:'FLAR' 0">Olives</span><span style="font-variation-settings:'FLAR' 50">Vines</span><span style="font-variation-settings:'FLAR' 100">Heritage</span></p><p class="kick"><b>Olives</b><span>Salfit</span><span>21 Oct</span></p></div>
    <div class="t6"><p class="lbl">Figures · Literata tabular lining</p><p class="figs num">21,000 t · ₪550 · 15 Oct · 7,000</p></div>
  </div>
</div></section>

<section class="ch alt" id="course"><div class="wrap">
  <div class="ch-head"><p class="ch-n">06</p><h2>The course and the season</h2><p class="dek">Two devices carry the idea through the site. The course is a dry-stone wall face, drawn as the site's rule under every section. The season line is the picking calendar, with today as the summit stone.</p></div>
  <div class="course" style="margin:10px 0 34px"></div>
  <div class="almanac ink book-season"><div class="season seen">{season_svg()}</div></div>
  <p class="txt small" style="margin-top:14px">The season line is drawn at build time from the ministry's dates. The picked part of the season fills up to today; today's stone is the only red on it.</p>
  <div class="three">
    <div><p class="lbl">Pick · Press · Plant</p><p class="txt">The month on the land is three steps, set like terraces down the page: each step lower than the one before, each with its course under it.</p></div>
    <div><p class="lbl">Now</p><p class="txt"><i class="dot"></i> The summit stone at text size marks the live part of any list: the current month, today's date, the section you are in.</p></div>
    <div><p class="lbl">The hill</p><p class="txt">On black grounds the mark's walls are continued downhill as a contour drawing: the same geometry, mapped further out.</p></div>
  </div>
</div></section>

<section class="ch" id="motion"><div class="wrap">
  <div class="ch-head"><p class="ch-n">07</p><h2>Motion</h2><p class="dek">The loader lays the walls. The outer wall goes down first, stone by stone from the low side, then each terrace above it, then the stone drops onto the summit and the finished mark moves into the masthead. It plays once per visit, and not at all when the reader asks for less motion.</p></div>
  {loader_demo()}
  <table class="mo-t"><thead><tr><th>Moment</th><th>What moves</th><th>Time · curve</th></tr></thead><tbody>
    <tr><td>Loader</td><td>43 stones, 17 ms apart; the stalk drawn; the summit dropped with a little settle; the mark flown to the masthead</td><td>about 1.6 s · ease-out, then 0.75 s in-out</td></tr>
    <tr><td>Arrival</td><td>Blocks rise 14 px as they come into view; each course is laid left to right</td><td>0.7–1.2 s · cubic-bezier(.16, 1, .3, 1)</td></tr>
    <tr><td>Season line</td><td>The picked part fills to today, the dates appear in order, today's stone drops last</td><td>1.5 s, today at 1.4 s</td></tr>
    <tr><td>Hover</td><td>Headlines underline from the left; photos ease in by 3%</td><td>0.45 s · 1.1 s</td></tr>
  </tbody></table>
</div></section>

<section class="ch alt" id="photo"><div class="wrap">
  <div class="ch-head"><p class="ch-n">08</p><h2>Photographs</h2><p class="dek">People and places in their own colour, with a caption that says where, when and who took it. A story gets a photograph of what it is about, or none at all.</p></div>
  <figure class="ph-ex">{ph[0] if ph else ""}{ph[1] if ph else ""}</figure>
  <div class="three">
    <div><p class="lbl">Natural colour</p><p class="txt">No filters, no duotone. The harvest is green, violet and black; the soil is red. That colour is the subject.</p></div>
    <div><p class="lbl">Honest captions</p><p class="txt">Place, date, photographer, licence. An archive photograph says it is one; a photograph from another year says which year.</p></div>
    <div><p class="lbl">Crops</p><p class="txt">4:3 for the lead, 3:2 for stories, squares for lists. Hands and faces stay in frame.</p></div>
  </div>
</div></section>

<section class="ch" id="files"><div class="wrap">
  <div class="ch-head"><p class="ch-n">09</p><h2>Files</h2><p class="dek">Every mark as SVG, the fonts with their licences, and the colours.</p></div>
  <ul class="files">
    <li><img src="assets/brand/wordmark.svg?v={V}" alt="" width="265" height="38"><a href="assets/brand/wordmark.svg" download>wordmark.svg</a></li>
    <li class="dk"><img src="assets/brand/wordmark-ink.svg?v={V}" alt="" width="265" height="38"><a href="assets/brand/wordmark-ink.svg" download>wordmark-ink.svg</a></li>
    <li><img src="assets/brand/wordmark-stack.svg?v={V}" alt="" width="80" height="72"><a href="assets/brand/wordmark-stack.svg" download>wordmark-stack.svg</a></li>
    <li><img src="assets/brand/mark.svg?v={V}" alt="" width="64" height="64"><a href="assets/brand/mark.svg" download>mark.svg</a></li>
    <li><img src="assets/brand/avatar.svg?v={V}" alt="" width="72" height="72"><a href="assets/brand/avatar.svg" download>avatar.svg</a></li>
    <li><img src="assets/brand/avatar-soil.svg?v={V}" alt="" width="72" height="72"><a href="assets/brand/avatar-soil.svg" download>avatar-soil.svg</a></li>
  </ul>
  <p class="go"><a class="btn" href="assets/olive-palestine-identity.zip" download>Download everything (.zip)</a> <a class="btn ghost" href="home.html">See the homepage</a></p>
</div></section>'''


def main():
    body = (build.head('Olive Palestine · Identity', 'The identity of Olive Palestine: an olive cut in half is a terraced hill seen from above.', 'index.html')
            .replace(f'<link rel="stylesheet" href="assets/css/op.css?v={V}">',
                     f'<link rel="stylesheet" href="assets/css/op.css?v={V}"><link rel="stylesheet" href="assets/css/book.css?v={V}">')
            .replace("d.classList.add('loading')", "0"))
    page = (body + '\n<body class="book">\n' + SPRITE + '<main>' + chapters() + '</main>\n'
            + '<footer class="bfoot"><div class="wrap"><p>Olive Palestine identity · a design prototype by TakTek · fonts: Literata and Commissioner, SIL Open Font License</p></div></footer>\n'
            + f'<script src="assets/js/marks.js?v={V}"></script><script>document.documentElement.classList.add("js");{BOOK_JS}</script>\n</body>\n</html>\n')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    z = os.path.join(ROOT, 'assets', 'olive-palestine-identity.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fn in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            zf.write(os.path.join(ROOT, 'assets', 'brand', fn), 'olive-palestine/brand/' + fn)
        for fn in sorted(os.listdir(os.path.join(ROOT, 'assets', 'fonts'))):
            zf.write(os.path.join(ROOT, 'assets', 'fonts', fn), 'olive-palestine/fonts/' + fn)
        zf.writestr('olive-palestine/colours.txt', '\n'.join(f'{n}\t{h}\t{d}' for n, h, d, _ in SW) + '\n')
        zf.write(os.path.join(ROOT, 'favicon.svg'), 'olive-palestine/favicon.svg')
    print('index.html', os.path.getsize(os.path.join(ROOT, 'index.html')) // 1024, 'KB · zip', os.path.getsize(z) // 1024, 'KB')


if __name__ == '__main__':
    main()
