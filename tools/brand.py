"""Olive Palestine marks.

python -I tools/brand.py   -> assets/brand/*.svg + assets/js/marks.js + favicon.svg + tools/out/marks.json

The mark is two drawings at once: an olive on its stalk, and a terraced hill seen from above.
The skin is the outer wall. Inside it, each terrace wall is the olive's outline drawn smaller
and moved up-slope, so the walls crowd together on the steep face (towards the stalk) and
open out on the gentle one, the way contours do on a map of the hills around Battir or
Sebastia. On the summit sits a stone in terra rossa, the red soil the trees stand in.
That red stone is also the site's "here, now": the same point marks today on every calendar.

In large drawings (the loader, the book) each wall is laid as separate stones, outside in,
the way a dry-stone terrace is built from the bottom of the hill.
"""
import io
import json
import math
import os
import random

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)

# limestone, black olive, terra rossa, terra rossa lifted for dark grounds
STONE, INK, SOIL, SOIL_LIT = '#EFE9DC', '#231B21', '#A3412A', '#D2603F'

A, B, EGG = 1.0, 0.64, 0.12     # the olive: half-length, half-width, how much fuller the stalk end is
TILT = -30                      # degrees: the fruit hanging off its stalk
WALLS = [1.0, 0.72, 0.46]       # the skin, then each terrace wall, as a scale of the outline
UPHILL = (0.62, -0.30)          # where the summit lies, in olive units: towards the stalk, the steep face
SUMMIT = 0.17                   # the stone
SKIN, WALL = 0.13, 0.06         # line weights, as a share of the half-length
STALK = [(1.02, 0), (1.30, -0.10), (1.48, -0.30)]   # a quadratic from the stalk end


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def instance(path, limits):
    font = instancer.instantiateVariableFont(TTFont(path), limits)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    return TTFont(buf)


def egg(t, s, b=B):
    """Point at parameter t on the outline scaled by s and moved up-slope by (1 - s), before the tilt."""
    x = A * math.cos(t)
    y = b * math.sin(t) * (1 + EGG * math.cos(t))
    return s * x + UPHILL[0] * (1 - s), s * y + UPHILL[1] * (1 - s)


def place(p, cx, cy, size):
    a = math.radians(TILT)
    x, y = p
    return cx + size * (x * math.cos(a) - y * math.sin(a)), cy + size * (x * math.sin(a) + y * math.cos(a))


def poly(pts, close=True):
    return 'M' + 'L'.join(f'{f(x)} {f(y)}' for x, y in pts) + ('Z' if close else '')


def wall(k, cx, cy, size, n=120):
    return poly([place(egg(2 * math.pi * i / n, WALLS[k]), cx, cy, size) for i in range(n)])


def summit(cx, cy, size, n=60):
    return poly([place(egg(2 * math.pi * i / n, SUMMIT, 0.8), cx, cy, size) for i in range(n)])


def stalk(cx, cy, size):
    (x0, y0), (x1, y1), (x2, y2) = (place(p, cx, cy, size) for p in STALK)
    return f'M{f(x0)} {f(y0)}Q{f(x1)} {f(y1)} {f(x2)} {f(y2)}'


def stones(k, cx, cy, size, seed=7):
    """Wall k laid as stones: open arcs along it, uneven lengths, a joint between each.
    Laid round from the gentle low side, the way a terrace is walked while it is built."""
    rnd = random.Random(seed * 31 + k)
    lens = [0.7 + rnd.random() * 0.6 for _ in range([20, 14, 9][k])]
    tot = sum(lens)
    out, t = [], math.pi * 0.85
    for ln in lens:
        span = 2 * math.pi * ln / tot
        j = span * 0.09
        a0, a1 = t + j, t + span - j
        steps = max(3, int(span / 0.05))
        out.append(poly([place(egg(a0 + (a1 - a0) * i / steps, WALLS[k]), cx, cy, size) for i in range(steps + 1)], False))
        t += span
    return out


def mark(cx, cy, size, walls=3, ink=INK, soil=SOIL, skin=SKIN, weight=WALL):
    """The mark as SVG elements, centred near (cx, cy). size = the olive's half-length."""
    inner = ''.join(f'<path d="{wall(k, cx, cy, size)}"/>' for k in range(1, walls))
    return (f'<g fill="none" stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{wall(0, cx, cy, size)}" stroke-width="{f(size * skin)}"/>'
            f'<path d="{stalk(cx, cy, size)}" stroke-width="{f(size * skin * 0.8)}"/>'
            f'<g stroke-width="{f(size * weight)}">{inner}</g></g>'
            f'<path d="{summit(cx, cy, size)}" fill="{soil}"/>')


def glyphs(font, text, x0, base, s, track=0):
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    paths, x = [], x0
    for ch in text:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (s, 0, 0, -s, x, base)))
        paths.append(pen.getCommands())
        x += gs[g].width * s + track
    return ''.join(paths), x - track


def svg(w, h, body, bg=None, label='Olive Palestine'):
    rect = f'<rect width="{f(w)}" height="{f(h)}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(w)} {f(h)}" width="{f(w)}" height="{f(h)}" '
            f'role="img" aria-label="{label}">{rect}{body}</svg>\n')


def course(w=520, h=22, seed=3, color=INK, width=1.1, fill='none'):
    """A dry-stone wall face as a repeating tile: two courses of uneven, roughly squared stones,
    the joints of the upper course falling over the stones of the lower one. Each stone is a
    hexagon with its corners knocked off by a random amount. The tile closes on itself."""
    rnd = random.Random(seed)
    rows = [(1.2, h / 2 - 0.4), (h / 2 + 0.4, h - 1.2)]
    body = []
    for r, (y0, y1) in enumerate(rows):
        x = 0.0
        while x < w:
            sw_ = rnd.uniform(22, 46) if r == 0 else rnd.uniform(28, 58)
            if x + sw_ > w - 10:
                sw_ = w - x
            x0, x1 = x + 0.9, x + sw_ - 0.9
            c = [rnd.uniform(0.3, 1.6) for _ in range(4)]
            t0, t1 = y0 + rnd.uniform(0, 1.6), y0 + rnd.uniform(0, 1.6)
            b0, b1 = y1 - rnd.uniform(0, 0.6), y1 - rnd.uniform(0, 0.6)
            pts = [(x0, t0 + c[0]), (x0 + c[0], t0), (x1 - c[1], t1), (x1, t1 + c[1]),
                   (x1, b1 - c[2]), (x1 - c[2], b1), (x0 + c[3], b0), (x0, b0 - c[3])]
            body.append(poly(pts))
            x += sw_
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<path d="{"".join(body)}" fill="{fill}" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/></svg>')


def contours(w, h, cx, cy, size, n=11, color=STONE, width=1):
    """The hill around the mark, mapped further out: the mark's own walls continued downhill,
    each a little wider apart, as a contour drawing for dark grounds. No summit here: the red
    is kept for today."""
    rings = []
    for k in range(n):
        sc = 1 + k * 0.62 + k * k * 0.05
        pts = []
        for i in range(160):
            t = 2 * math.pi * i / 160
            x, y = egg(t, sc)
            wob = 1 + 0.025 * math.sin(3 * t + k * 0.9) + 0.018 * math.sin(5 * t - k * 1.7)
            pts.append(place(((x - UPHILL[0]) * wob + UPHILL[0], (y - UPHILL[1]) * wob + UPHILL[1]), cx, cy, size))
        rings.append(poly(pts))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}">' + ''.join(f'<path d="{d}"/>' for d in rings) +
            f'</g></svg>')


def write(name, text):
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(text)


def main():
    lit = instance(os.path.join(SRC, 'literata-Literata[opsz,wght].ttf'), {'opsz': 72, 'wght': 540})
    ita = instance(os.path.join(SRC, 'literata-Literata-Italic[opsz,wght].ttf'), {'opsz': 72, 'wght': 500})
    upm = lit['head'].unitsPerEm
    cap = lit['OS/2'].sCapHeight

    # ---- the mark on its own field: 64 x 64, the olive 22 half-length
    MS, MX, MY = 22.5, 29, 36
    marks = {'mark': {'w': 64, 'h': 64, 'cx': MX, 'cy': MY, 'size': MS,
                      'walls': [wall(k, MX, MY, MS) for k in range(3)], 'summit': summit(MX, MY, MS),
                      'stalk': stalk(MX, MY, MS), 'skin': round(MS * SKIN, 2), 'wall': round(MS * WALL, 2),
                      'stones': [stones(k, MX, MY, MS) for k in range(3)]}}
    write('mark.svg', svg(64, 64, mark(MX, MY, MS), label='Olive Palestine mark'))
    write('mark-ink.svg', svg(64, 64, mark(MX, MY, MS, ink=STONE, soil=SOIL_LIT), INK, 'Olive Palestine mark'))
    write('mark-soil.svg', svg(64, 64, mark(MX, MY, MS, ink=STONE, soil=INK), SOIL, 'Olive Palestine mark'))

    # ---- wordmark: the mark, then «Olive» in Literata display and «Palestine» in its italic,
    # the mark as tall as the capitals plus the stalk; one line.
    s = 46 / cap                          # caps 46 high
    pad, gap = 4, 15
    base = pad + 52
    msz = cap * s * 0.66
    mcx, mcy = pad + msz * 1.02, base - cap * s * 0.47
    x0 = pad + msz * 2.18 + gap
    olive, xa = glyphs(lit, 'Olive', x0, base, s)
    pal, xb = glyphs(ita, 'Palestine', xa + 0.24 * upm * s, base, s)
    W, H = xb + pad, base + 0.24 * upm * s + pad
    body = lambda ink, soil: (mark(mcx, mcy, msz, ink=ink, soil=soil) +
                              f'<path d="{olive}" fill="{ink}"/><path d="{pal}" fill="{ink}"/>')
    write('wordmark.svg', svg(W, H, body(INK, SOIL)))
    write('wordmark-ink.svg', svg(W, H, body(STONE, SOIL_LIT), INK))
    marks['wordmark'] = {'w': round(W, 1), 'h': round(H, 1), 'olive': olive, 'pal': pal,
                         'm': [round(mcx, 2), round(mcy, 2), round(msz, 2)]}

    # ---- stacked: the mark above, the two words centred under it (avatars, the book cover)
    s2 = 40 / cap
    o2, wa = glyphs(lit, 'Olive', 0, 0, s2)
    p2, wb = glyphs(ita, 'Palestine', 0, 0, s2)
    SW = max(wa, wb) + 2 * pad
    sm = 46
    top = pad + sm * 1.4
    lines = (f'<g transform="translate({f((SW - wa) / 2)} {f(top + sm * 0.9 + cap * s2)})"><path d="{o2}"/></g>'
             f'<g transform="translate({f((SW - wb) / 2)} {f(top + sm * 0.9 + cap * s2 * 2.25)})"><path d="{p2}"/></g>')
    SH = top + sm * 0.9 + cap * s2 * 2.25 + 0.24 * upm * s2 + pad
    write('wordmark-stack.svg', svg(SW, SH, mark(SW / 2 - sm * 0.1, top, sm) + f'<g fill="{INK}">{lines}</g>'))

    # ---- avatar and favicon: the small mark keeps the skin and one wall
    write('avatar.svg', svg(512, 512, mark(236, 284, 168, ink=STONE, soil=SOIL_LIT), INK))
    write('avatar-soil.svg', svg(512, 512, mark(236, 284, 168, ink=STONE, soil=INK), SOIL))
    open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="{INK}"/>'
        + mark(14.2, 18.4, 11.8, walls=2, ink=STONE, soil=SOIL_LIT, skin=0.17, weight=0.1) + '</svg>\n')

    # ---- the course (section rule) and the hill (contour field for dark grounds)
    write('course.svg', course(color='#B9AC95', fill='#E3DACA'))
    write('course-ink.svg', course(color='#4F434B', fill='#2C2229'))
    write('hill.svg', contours(900, 520, 640, 250, 62, color='#4A3D45'))

    os.makedirs(os.path.join(ROOT, 'assets', 'js'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)
    json.dump(marks, open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8'))
    open(os.path.join(ROOT, 'assets', 'js', 'marks.js'), 'w', encoding='utf-8').write(
        '// generated by tools/brand.py — do not edit\nwindow.OP_MARKS = ' + json.dumps(marks) + ';\n')
    print('wordmark', round(W), 'x', round(H), '· stack', round(SW), 'x', round(SH))


if __name__ == '__main__':
    main()
