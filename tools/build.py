"""Build home.html from tools/edition.json.

python -I tools/build.py

Everything a reader needs is in the HTML: the season line is drawn here as static SVG, the
stories, the figures and the recipe are plain markup. assets/js/op.js only adds the loader
(laying the walls) and the arrivals on scroll.
"""
import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '4'                                       # bump on any asset change (Chrome caches hard)
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))   # written by brand.py
PH = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))
DIM = json.load(open(os.path.join(ROOT, 'tools', 'out', 'photos.json'), encoding='utf-8')) if os.path.exists(
    os.path.join(ROOT, 'tools', 'out', 'photos.json')) else {}

esc = html.escape
R = ''                                        # path back to the site root, for pages in folders
D = dt.date.fromisoformat
TODAY = D(E['date'])
S = E['stories']


def day(d, year=False, wd=False):
    d = D(d) if isinstance(d, str) else d
    s = f"{d.day} {d.strftime('%b')}" + (f" {d.year}" if year else '')
    return (d.strftime('%a') + ' ' + s) if wd else s


def long_day(d):
    d = D(d) if isinstance(d, str) else d
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')} {d.year}"


# ---------------------------------------------------------------- the icons
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 16 16"><path d="M7 2.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zM10.4 10.4 14 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-mail" viewBox="0 0 16 16"><path d="M2.5 4h11v8h-11zM2.8 4.3 8 8.6l5.2-4.3" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></symbol>
</defs></svg>'''


def icon(name, cls=''):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


def wordmark(cls='', ink='#231B21', soil='#A3412A', label='Olive Palestine'):
    w, m = MARKS['wordmark'], MARKS['mark']
    # the mark in the wordmark is the 64-unit mark scaled into place
    k = w['m'][2] / m['size']
    tx, ty = w['m'][0] - m['cx'] * k, w['m'][1] - m['cy'] * k
    walls = ''.join(f'<path d="{d}"/>' for d in m['walls'][1:])
    return (f'<svg class="{cls}" viewBox="0 0 {w["w"]} {w["h"]}" role="img" aria-label="{label}">'
            f'<g transform="translate({tx:.2f} {ty:.2f}) scale({k:.4f})"><g fill="none" stroke="{ink}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{m["walls"][0]}" stroke-width="{m["skin"]}"/><path d="{m["stalk"]}" stroke-width="{m["skin"] * .8:.2f}"/>'
            f'<g stroke-width="{m["wall"]}">{walls}</g></g><path d="{m["summit"]}" fill="{soil}"/></g>'
            f'<path d="{w["olive"]}" fill="{ink}"/><path d="{w["pal"]}" fill="{ink}"/></svg>')


# ---------------------------------------------------------------- photographs
def photo(slug, sizes='100vw', cls='ph', eager=False, cap=True, ratio=None):
    if not slug or slug not in PH:
        return ''
    p = PH[slug]
    dm = DIM.get(slug, {'w': 1000, 'h': 667})
    pos = f' style="object-position:{p["focus"]}"' if p.get('focus') else ''
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    img = (f'<div class="{cls}"><img src="{R}assets/img/photo/{slug}.webp?v={V}" width="{dm["w"]}" height="{dm["h"]}" '
           f'alt="{esc(p["alt"])}" sizes="{sizes}" {load}{pos}></div>')
    return img, (f'<figcaption>{esc(p["caption"])}. Photo: {esc(p["author"])}, {esc(p["license"])}</figcaption>' if cap else '')


def fig(slug, **kw):
    r = photo(slug, **kw)
    if not r:
        return ''
    img, cap = r
    return f'<figure>{img}{cap}</figure>'


def thumb(slug):
    r = photo(slug, sizes='96px', cap=False)
    return r[0] if r else ''


def row(sid):
    """A list row: thumbnail and headline; rows without an honest photo go text-only."""
    t = thumb(S[sid].get('photo'))
    return f'<li><a href="{link(sid)}"{"" if t else " class=\"np\""}>{t}<b>{esc(S[sid]["headline"])}</b></a></li>'


# each research desk lives on one section page; palms and fields share one, market is the prices page
DESK_PAGE = {'olives': 'olives', 'market': 'prices', 'vines': 'vines', 'palms': 'palms', 'fields': 'palms',
             'flocks': 'flocks', 'kitchen': 'kitchen', 'heritage': 'heritage', 'calendar': 'calendar'}


def link(sid):
    return f'{R}story/{sid}.html'


def href(h):
    """Edition links: '#story-id' is a story page, '#page' a section page."""
    k = h.lstrip('#')
    return link(k) if k in S else f'{R}{k}.html'


def kick(s):
    bits = []
    if s.get('background'):
        bits.append(f'<span class="bg">Background · {day(s["date"])}</span>')
    bits.append(f'<b>{esc(s["desk"])}</b>')
    bits.append(f'<span>{esc(s["place"])}</span>')
    if not s.get('background'):
        bits.append(f'<span>{day(s["date"])}</span>')
    return '<p class="kick">' + ''.join(bits) + '</p>'


def src(s):
    return f'<span class="src">{esc(s["source"])}, {day(s["published"])}</span>'


def story(sid, h='h-m', dek=True, pic=True, cls='st rise', sizes='(max-width:640px) 100vw, 40vw', facts=False):
    s = S[sid]
    pic_html = fig(s.get('photo'), sizes=sizes) if pic else ''
    fx = ''.join(f'<li><span class="n">{esc(f["n"])}</span><p>{esc(f["label"])}</p></li>' for f in s.get('figures', [])[:3]) if facts else ''
    return (f'<article class="{cls}" id="{sid}">{pic_html}{kick(s)}'
            f'<h3 class="{h}"><a href="{link(sid)}">{esc(s["headline"])}</a></h3>'
            + (f'<p class="txt">{esc(s["dek"])} {src(s)}</p>' if dek else '') + (f'<ul class="facts">{fx}</ul>' if fx else '') + '</article>')


# ---------------------------------------------------------------- the season line
def season_svg(compact=False):
    """The picking calendar as a line: weeks as ticks, the ministry's dates as stones on it,
    the picking itself as a band, and today as the red summit stone."""
    se = E['season']
    a, b = D(se['compact'][0] if compact else se['start']), D(se['compact'][1] if compact else se['end'])
    W, L, Rr = (343, 6, 6) if compact else (780, 4, 8)
    span = (b - a).days
    x = lambda d: L + ((D(d) if isinstance(d, str) else d) - a).days / span * (W - L - Rr)
    base = 104 if compact else 100
    parts = [f'<line class="base" x1="{L}" y1="{base}" x2="{W - Rr}" y2="{base}" stroke-width="1"/>']
    # the picking: from the first date to the season's end; filled to today
    p0, p1 = max(a, D(se['band'][0])), min(b, D(se['band'][1]))
    parts.append(f'<rect class="band" x="{x(p0):.1f}" y="{base - 5}" width="{x(p1) - x(p0):.1f}" height="10"/>')
    if TODAY > p0:
        parts.append(f'<rect class="band on" x="{x(p0):.1f}" y="{base - 5}" width="{x(min(TODAY, p1)) - x(p0):.1f}" height="10"/>')
    # weeks and months
    d = a
    while d <= b:
        if d.day == 1 or d == a:
            parts.append(f'<line class="tick" x1="{x(d):.1f}" y1="{base + 8}" x2="{x(d):.1f}" y2="{base + 18}"/>'
                         f'<text class="mo" x="{x(d) + 4:.1f}" y="{base + 30}">{d.strftime("%b").upper()}</text>')
        elif d.weekday() == 6:
            parts.append(f'<line class="tick" x1="{x(d):.1f}" y1="{base + 8}" x2="{x(d):.1f}" y2="{base + 12}"/>')
        d += dt.timedelta(days=1)
    # the dates, alternating rows above the line so labels never collide
    evs = [e for e in se['events'] if a <= D(e['date']) <= b]
    rows = [14, 50] if not compact else [12, 48]
    for i, e in enumerate(evs):
        ex = x(e['date'])
        ry = rows[i % 2]
        past = ' past' if D(e['date']) < TODAY else ''
        anchor = 'end' if ex > W - 150 else 'start'
        tx = ex - 6 if anchor == 'end' else ex + 6
        label = e['short'] if compact else e['label']
        parts.append(f'<g class="ev-g{past}"><line class="pin" x1="{ex:.1f}" y1="{ry + 6}" x2="{ex:.1f}" y2="{base - 6}"/>'
                     f'<rect class="stone" x="{ex - 3.5:.1f}" y="{base - 3.5}" width="7" height="7" transform="rotate(45 {ex:.1f} {base})"/>'
                     f'<text class="ev-d" x="{tx:.1f}" y="{ry}" text-anchor="{anchor}">{day(e["date"])}</text>'
                     f'<text class="ev" x="{tx:.1f}" y="{ry + 15}" text-anchor="{anchor}">{esc(label)}</text></g>')
    tx_ = x(TODAY)
    parts.append(f'<g class="today"><line x1="{tx_:.1f}" y1="{base - 26}" x2="{tx_:.1f}" y2="{base + 4}" stroke-width="1.5"/>'
                 f'<ellipse class="stone" cx="{tx_:.1f}" cy="{base}" rx="8" ry="5.5" transform="rotate(-30 {tx_:.1f} {base})"/>'
                 f'<text x="{tx_:.1f}" y="{base + 50}" text-anchor="middle">TODAY</text></g>')
    H = base + 56
    lab = 'Picking calendar: ' + '; '.join(f'{day(e["date"])}, {e["label"]}' for e in evs) + f'. Today is {day(TODAY)}.'
    return (f'<svg class="{"m" if compact else "d"}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(lab)}">'
            + ''.join(parts) + '</svg>')


# ---------------------------------------------------------------- the page
def head(title, desc, path='home.html'):
    url = 'https://taktek-dev.github.io/olive-palestine-prototype/' + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#231B21">
<link rel="icon" href="{R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Olive Palestine">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="https://taktek-dev.github.io/olive-palestine-prototype/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="{R}assets/fonts/literata.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{R}assets/fonts/commissioner.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{R}assets/css/op.css?v={V}">
<script>(function(){{var d=document.documentElement,f=/[?&]loader/.test(location.search),s;try{{s=sessionStorage.getItem('op-built')}}catch(e){{}}
if((f||!s)&&!matchMedia('(prefers-reduced-motion: reduce)').matches)d.classList.add('loading')}})()</script>
</head>'''


NAV = [('October', 'home'), ('Olives', 'olives'), ('Vines &amp; figs', 'vines'), ('Palms &amp; fields', 'palms'),
       ('Flocks', 'flocks'), ('Kitchen', 'kitchen'), ('Heritage', 'heritage'), ('Prices', 'prices'), ('Calendar', 'calendar')]


def top(cur='home'):
    nav = ''.join(f'<li><a href="{R}{k}.html"{" aria-current=\"page\"" if k == cur else ""}>{t}</a></li>' for t, k in NAV)
    nav += f'<li><a href="{R}archive.html"{" aria-current=\"page\"" if cur == "archive" else ""}>Every month <small>12</small></a></li>'
    return f'''<a class="skip" href="#main">Skip to the stories</a>
<div class="loader" aria-hidden="true"><svg viewBox="0 0 64 64"></svg><p>{esc(E["loader"])}</p></div>
{SPRITE}
<div class="topbar"><div class="wrap">
  <p class="today"><span class="day">{long_day(TODAY)}</span><span class="now"><i class="dot"></i>{esc(E["topline"])}</span></p>
  <nav class="links" aria-label="Site"><a href="{R}letter.html">The monthly letter</a><a href="{R}about.html">About</a></nav>
</div></div>
<header class="mast" id="top"><div class="wrap">
  <a class="brand" href="{R}home.html" aria-label="Olive Palestine, home">{wordmark()}</a>
  <p class="line">{esc(E["line"])}</p>
  <div class="acts">
    <a class="btn ghost" href="{R}search.html" aria-label="Search">{icon("i-search")}<span>Search</span></a>
    <a class="btn" href="{R}letter.html">{icon("i-mail")}The monthly letter</a>
  </div>
</div></header>
<nav class="nav" aria-label="Sections"><div class="wrap"><ul>{nav}</ul></div></nav>'''


def almanac():
    counts = ''.join(f'<li><span class="n num" data-count="{c["n"]}"><span class="v">{c["n"]:,}</span><small>{esc(c["unit"])}</small></span>'
                     f'<p>{esc(c["text"])}</p></li>' for c in E['counts'])
    se = E['season']
    return f'''<section class="almanac" aria-labelledby="month-h">
  <img class="hill" src="{R}assets/brand/hill.svg?v={V}" alt="" width="900" height="520">
  <div class="wrap">
    <div class="month">
      <p class="lbl">The month on the land</p>
      <h1 id="month-h">{esc(E["month"])}</h1>
      <p>{esc(E["month_line"])}</p>
    </div>
    <div class="season">
      <div class="season-head"><p class="lbl"><b>{esc(se["title"])}</b></p><p class="lbl">{esc(se["src"])}</p></div>
      {season_svg()}{season_svg(True)}
      <ul class="counts">{counts}</ul>
    </div>
  </div>
</section>'''


def lead():
    s = S[E['lead']]
    facts = ''.join(f'<li><span class="n">{esc(f["n"])}</span><p>{esc(f["text"])} <span class="src">{esc(f["src"])}</span></p></li>'
                    for f in s.get('facts', []))
    also = ''.join(row(i) for i in E['also'])
    r = photo(s['photo'], sizes='(max-width:900px) 100vw, 58vw', eager=True)
    return f'''<section class="lead" id="lead" aria-label="The lead"><div class="wrap">
  <figure>{r[0]}{r[1]}</figure>
  <article class="copy" id="{E["lead"]}">
    {kick(s)}
    <h2 class="h-xl"><a href="{link(E["lead"])}">{esc(s["headline"])}</a></h2>
    <p class="dek">{s["dek_html"] if s.get("dek_html") else esc(s["dek"])} {src(s)}</p>
    {f'<ul class="facts">{facts}</ul>' if facts else ''}
    <p class="by">{esc(s.get("by", "By the Olive Palestine land desk"))}</p>
    <ul class="also" aria-label="Also on the land today">{also}</ul>
  </article>
</div></section>'''


def land():
    steps = []
    for key, verb, small in (('pick', 'Pick', 'picked now'), ('press', 'Press', 'milled now'), ('plant', 'Plant', 'sown now')):
        items = ''.join(f'<li><a href="{href(i["href"])}"><b>{esc(i["t"])}</b><span>{esc(i["note"])}</span></a></li>' for i in E['land'][key])
        steps.append(f'<div class="step rise"><h3><span>{verb}</span><small>{small}</small></h3><ul>{items}</ul></div>')
    return f'''<section class="land" aria-labelledby="land-h"><div class="wrap">
  <div class="land-head"><h2 class="lbl" id="land-h">This month on the land</h2><p class="by">Three steps of the season, as of {long_day(TODAY)}</p></div>
  <div class="steps">{"".join(steps)}</div>
</div></section>'''


def desk_head(hid, name, line, more='All stories', page=None):
    return (f'<div class="desk-head"><h2 id="{hid}">{name}</h2><div><p>{esc(line)}</p>'
            f'<a class="more" href="{R}{page}.html">{more} {icon("i-right")}</a></div></div><div class="course lay"></div>')


def olives():
    o = E['olives']
    side = ''.join(story(i, h='h-s', sizes='172px') for i in o['side'])
    row = ''.join(story(i, h='h-s', dek=False, sizes='(max-width:640px) 96px, 25vw') for i in o['row'])
    return f'''<section class="desk" id="olives" aria-labelledby="olives-h"><div class="wrap">
  {desk_head("olives-h", "Olives", o["line"], "All olive stories", "olives")}
  <div class="grid-olives">
    {story(o["big"], h="h-l", cls="st big rise", sizes="(max-width:1180px) 100vw, 56vw", facts=True)}
    <div class="side">{side}</div>
    <div class="row">{row}</div>
  </div>
</div></section>'''


def figures():
    items = ''.join(f'<li class="rise"><span class="n{" hot" if f.get("hot") else ""}">{esc(f["n"])}{f"<small>{esc(f["unit"])}</small>" if f.get("unit") else ""}</span>'
                    f'<p>{esc(f["text"])} <span class="src">{esc(f["src"])}</span></p></li>' for f in E['figures'])
    return f'''<section class="figures" id="figures" aria-labelledby="fig-h"><div class="wrap">
  <div class="intro"><h2 id="fig-h">The season in figures</h2><p>{esc(E["figures_intro"])}</p><a class="more" href="{R}prices.html">Prices and the market {icon("i-right")}</a></div>
  <ul class="board">{items}</ul>
</div></section>'''


def trio():
    cols = []
    for c in E['trio']:
        lst = ''.join(row(i) for i in c.get('list', []))
        cols.append(f'<section class="col" id="{c["key"]}" aria-labelledby="{c["key"]}-h"><h2 id="{c["key"]}-h"><a href="{R}{c["key"]}.html">{c["name"]}</a></h2>'
                    f'<p class="now"><b>Now:</b> {esc(c["now"])}</p><div class="course lay"></div>'
                    + ''.join(story(i, h='h-s', sizes='(max-width:900px) 100vw, 30vw') for i in c['stories'])
                    + (f'<ul class="list">{lst}</ul>' if lst else '') + '</section>')
    return f'<div class="desk trio"><div class="wrap"><div class="cols">{"".join(cols)}</div></div></div>'


def kitchen(page=False):
    """The recipe of the season with the kitchen stories; page=True is the kitchen page's version,
    where the page head already names the section and the stories follow as cards."""
    k = E['kitchen']
    r = k['recipe']
    need = ''.join(f'<li>{esc(i)}</li>' for i in r['need'])
    method = ''.join(f'<li><span>{esc(i)}</span></li>' for i in r['method'])
    others = ''.join(story(i, h='h-s', sizes='(max-width:640px) 100vw, 30vw') for i in k['others'])
    return f'''<section class="desk kitchen ink" id="kitchen" aria-labelledby="kitchen-h"><div class="wrap">
  {'<h2 class="vh" id="kitchen-h">Recipe of the season</h2>' if page else desk_head("kitchen-h", "Kitchen", k["line"], "The kitchen", "kitchen")}
  <div class="recipe">
    {fig(r["photo"], sizes="(max-width:900px) 100vw, 48vw")}
    <div class="copy">
      <p class="kick"><b>Recipe of the season</b><span>{esc(r["when"])}</span></p>
      <h3 class="h-l">{esc(r["title"])}</h3>
      <p class="dek">{esc(r["dek"])}</p>
      <div class="lists"><div><h4>You will need</h4><ul>{need}</ul></div><div><h4>Method</h4><ol>{method}</ol></div></div>
      <p class="by">{esc(r["note"])} <span class="src">{esc(r["src"])}</span></p>
    </div>
  </div>
  {"" if page else f'<div class="others">{others}</div>'}
</div></section>'''


def heritage():
    h = E['heritage']
    b = ''.join(story(i, h='h-s', cls='st b rise', sizes='(max-width:640px) 100vw, 24vw') for i in h['b'])
    return f'''<section class="desk" id="heritage" aria-labelledby="her-h"><div class="wrap">
  {desk_head("her-h", "Heritage", h["line"], "All heritage stories", "heritage")}
  <div class="grid-her">{story(h["a"], h="h-l", cls="st a rise", sizes="(max-width:900px) 100vw, 48vw")}{b}</div>
</div></section>'''


def ahead():
    items = ''.join(f'<li class="rise"><time datetime="{a["date"]}"><small>{esc(a["when"])}</small>{day(a["date"], wd=True)}</time>'
                    f'<p>{esc(a["text"])} <span class="src">{esc(a["src"])}</span></p></li>' for a in E['ahead'])
    return f'''<section class="ahead" id="ahead" aria-labelledby="ahead-h"><div class="wrap">
  <div><h2 id="ahead-h">Next on the calendar</h2><a class="more" href="{R}calendar.html">The full calendar {icon("i-right")}</a></div><ol>{items}</ol>
</div></section>'''


def foot():
    mos = []
    for i in range(1, 13):
        m = dt.date(TODAY.year, i, 1)
        cur = ' aria-current="page"' if i == TODAY.month else ''
        later = ' class="later"' if i > TODAY.month else ''
        mos.append(f'<li><a href="{R}archive.html#m{i:02d}"{cur}{later}>{m.strftime("%b")}</a></li>')
    return f'''<footer><div class="wrap">
  <div>{wordmark("wm", "#EFE9DC", "#D2603F")}<p class="about">{E["about_html"]}</p>
    <p class="flinks"><a href="{R}about.html">About</a><a href="{R}letter.html">The monthly letter</a><a href="{R}search.html">Search</a><a href="{R}calendar.html">Calendar</a></p></div>
  <nav class="months" id="archive" aria-labelledby="months-h"><h2 id="months-h">Every month</h2><ul>{"".join(mos)}</ul></nav>
  <div class="course on-ink"></div>
  <p class="foot"><span>© {TODAY.year} Olive Palestine · a design prototype by TakTek</span><span><a href="{R}index.html">The identity</a> · <a href="{R}credits.html">Sources &amp; credits</a> · Photos: Wikimedia Commons, credited on each image</span></p>
</div></footer>'''


def page():
    return (head(E['title'], E['description']) + '\n<body>\n' + top() + '\n<main id="main">\n' + almanac() + lead() + land()
            + olives() + figures() + trio() + kitchen() + heritage() + ahead() + '\n</main>\n' + foot()
            + f'\n<script src="{R}assets/js/marks.js?v={V}"></script><script src="{R}assets/js/op.js?v={V}"></script>\n</body>\n</html>\n')


if __name__ == '__main__':
    open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8').write(page())
    print('home.html', len(page()) // 1024, 'KB')
