"""Build every page after the homepage.

python -I tools/pages.py   (after build.py; reads the same edition)

  story/<id>.html            one page per story (40), with its paragraphs, figures, people and source
  olives, vines, palms, flocks, kitchen, heritage .html   the section pages
  prices.html                the season in figures, and the market stories
  calendar.html              the picking calendar and every dated event, plus assets/olive-palestine-2026.ics
  archive.html               the twelve months: what this edition holds, and what is still to come
  about, letter, search, credits .html, 404.html
  assets/data/search.json    what search.html searches

Pages share build.py's head, masthead and footer. build.R is the path back to the site root:
'' for pages at the root, '../' for story pages, and the site's absolute path for 404.html,
which GitHub Pages serves at any depth.
"""
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import E, S, V, esc, day, long_day, icon, fig, photo, kick, src, link, DESK_PAGE, TODAY, D  # noqa: E402

ROOT = build.ROOT
NEWS = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))}
SECTIONS = {
    'olives': ('Olives', 'The picking, the presses and the groves people can and cannot reach.',
               'baladi Nabali picking since 15 October; improved Nabali from 5 November.'),
    'vines': ('Vines &amp; figs', 'Grapes, dibs and molasses, and the vineyards of Hebron and Bethlehem.',
              'the last grapes go into dibs and molasses.'),
    'palms': ('Palms &amp; fields', 'Dates in Jericho and the Jordan Valley; sowing, water and the first rain.',
              'Medjool picking; winter sowing waits for rain.'),
    'flocks': ('Flocks', 'Herders, grazing land and feed, from Masafer Yatta to Gaza.',
               'stocking feed before the winter grazing thins.'),
    'kitchen': ('Kitchen', 'What the season puts on the table, and the people who make it.',
                'the new oil comes home from the press.'),
    'heritage': ('Heritage', 'The places, crafts and customs the land has kept.',
                 'Heritage Day was 7 October; Sebastia joined the World Heritage List in July.'),
    'prices': ('Prices', 'What the season costs and earns, each figure with the body that counted it.',
               'new oil from $13 to $26 a kilo at the press.'),
}


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(text)


def shell(title, desc, path, body, cur='home', cls=''):
    return (build.head(title, desc, path) + f'\n<body class="{cls}">\n' + build.top(cur) + f'\n<main id="main">\n{body}\n</main>\n'
            + build.foot() + f'\n<script src="{build.R}assets/js/marks.js?v={V}"></script><script src="{build.R}assets/js/op.js?v={V}"></script>\n</body>\n</html>\n')


def section_of(sid):
    return DESK_PAGE[S[sid]['key']]


def order(ids):
    """Newest first; background items after this month's."""
    return sorted(ids, key=lambda i: (S[i]['background'], -D(S[i]['published']).toordinal()))


def plate(s, cls='plate'):
    """A story with no honest photograph gets a plate: black olive, the hill drawn round it, and the place."""
    place = s['place'].split(',')[0]
    return (f'<div class="{cls}" role="img" aria-label="{esc(s["place"])}"><img src="{build.R}assets/brand/hill.svg?v={V}" alt="" width="900" height="520">'
            f'<span class="pl-desk">{esc(s["desk"])}</span><span class="pl-place">{esc(place)}</span></div>')


def card(sid, h='h-s', dek=True, cls='card rise'):
    s = S[sid]
    pic = photo(s.get('photo'), sizes='(max-width:640px) 100vw, 30vw', cap=False)
    media = pic[0] if pic else plate(s)
    return (f'<article class="{cls}"><a class="cm" href="{link(sid)}" tabindex="-1" aria-hidden="true">{media}</a>{kick(s)}'
            f'<h3 class="{h}"><a href="{link(sid)}">{esc(s["headline"])}</a></h3>'
            + (f'<p class="txt">{esc(s["dek"])}</p>' if dek else '') + '</article>')


def page_head(name, line, now=None, count=None, lbl='Section'):
    meta = []
    if now:
        meta.append(f'<p class="now"><i class="dot"></i><b>Now:</b> {esc(now)}</p>')
    if count is not None:
        meta.append(f'<p class="count">{count} {"story" if count == 1 else "stories"} in this edition</p>')
    return f'''<section class="phead ink" aria-labelledby="ph-h">
  <img class="hill" src="{build.R}assets/brand/hill.svg?v={V}" alt="" width="900" height="520">
  <div class="wrap">
    <p class="lbl">{esc(lbl)}</p>
    <h1 id="ph-h">{name}</h1>
    <p class="line">{esc(line)}</p>
    <div class="meta">{"".join(meta)}</div>
  </div>
</section>'''


def grid(ids):
    if not ids:
        return ''
    ids = order(ids)
    first = next((i for i in ids if S[i].get('photo')), ids[0])
    rest = [i for i in ids if i != first]
    return (f'<div class="sgrid">{card(first, h="h-l", cls="card big rise")}'
            + ''.join(card(i) for i in rest) + '</div>')


# ---------------------------------------------------------------- story pages
def story_page(sid):
    s = S[sid]
    n = NEWS[sid]
    sec = section_of(sid)
    sec_name = SECTIONS.get(sec, ('Calendar',))[0]
    words = sum(len(p.split()) for p in s['body']) + len(s['dek'].split())
    mins = max(1, round(words / 220))
    r = photo(s.get('photo'), sizes='(max-width:900px) 100vw, 1100px', eager=True)
    media = f'<figure class="s-ph">{r[0]}{r[1]}</figure>' if r else f'<div class="s-ph">{plate(s, "plate big")}</div>'
    paras = ''.join(f'<p>{esc(p)}</p>' for p in s['body']) or f'<p>{esc(s["dek"])}</p>'
    facts = ''.join(f'<li><span class="n">{esc(f["n"])}</span><p>{esc(f["label"])}</p></li>' for f in s['figures'])
    people = ''.join(f'<li><b>{esc(p["name"])}</b><span>{esc(p["role"])}</span></li>' for p in s['people'])
    lang = ' (in Arabic)' if s['lang'] == 'ar' else ''
    others = [i for i in order([k for k in S if section_of(k) == sec and k != sid])][:3]
    if len(others) < 3:
        others += [k for k in order([k for k in S if k != sid and k not in others and S[k].get('photo')])][:3 - len(others)]
    bg = (f'<p class="bgnote">This is a <b>background</b> story, first reported on {long_day(s["published"])}, '
          f'before this month\'s edition. It is kept here because it explains what is happening now.</p>') if s['background'] else ''
    body = f'''<article class="story" aria-labelledby="s-h">
  <header class="s-head wrap">
    <nav class="crumbs lbl" aria-label="Breadcrumb"><a href="{build.R}home.html">October</a><span aria-hidden="true">/</span><a href="{build.R}{sec}.html">{sec_name}</a></nav>
    {kick(s)}
    <h1 class="h-xl" id="s-h">{esc(s["headline"])}</h1>
    <p class="dek">{esc(s["dek"])}</p>
    <p class="by">By the Olive Palestine land desk · based on reporting by <b>{esc(s["source"])}</b>, {long_day(s["published"])} · {mins} min read</p>
  </header>
  <div class="wrap">{media}</div>
  <div class="wrap s-body">
    <div class="prose">
      {bg}{paras}
      <div class="course"></div>
      <p class="from">First reported by <b>{esc(s["source"])}</b>{lang} on {long_day(s["published"])}. Olive Palestine retells it in its own words and links the original.
        <a class="more" href="{esc(s["url"])}" rel="noopener" target="_blank">Read the original report {icon("i-right")}<span class="vh"> (opens in a new tab)</span></a></p>
    </div>
    <aside class="s-side">
      {f'<section><h2 class="lbl">In figures</h2><ul class="facts col">{facts}</ul></section>' if facts else ''}
      {f'<section><h2 class="lbl">People in this story</h2><ul class="people">{people}</ul></section>' if people else ''}
      <section><h2 class="lbl">Where</h2><p class="where">{esc(s["place"])}</p><p class="by">{day(s["date"], True)}</p></section>
    </aside>
  </div>
</article>
<section class="related" aria-labelledby="rel-h"><div class="wrap">
  <div class="desk-head"><h2 id="rel-h">More from {sec_name}</h2><div><a class="more" href="{build.R}{sec}.html">All of {sec_name} {icon("i-right")}</a></div></div>
  <div class="course"></div>
  <div class="cards3">{"".join(card(i) for i in others)}</div>
</div></section>'''
    return shell(f'{s["headline"]} · Olive Palestine', s['dek'], f'story/{sid}.html', body, sec)


# ---------------------------------------------------------------- section pages
def section_page(key):
    name, line, now = SECTIONS[key]
    ids = [k for k in S if section_of(k) == key]
    extra = ''
    if key == 'olives':
        extra = f'<section class="sline"><div class="wrap almanac-mini ink">{season_block()}</div></section>'
    if key == 'kitchen':
        extra = build.kitchen(page=True).replace('class="desk kitchen ink"', 'class="desk kitchen ink kpage"')
    if key == 'prices':
        extra = build.figures()
    body = page_head(name, line, now, len(ids)) + extra + f'<section class="desk" aria-label="Stories"><div class="wrap">{grid(ids)}</div></section>'
    return shell(f'{re.sub("&amp;", "&", name)} · Olive Palestine', line, f'{key}.html', body, key)


def season_block():
    se = E['season']
    return (f'<div class="season seen"><div class="season-head"><p class="lbl"><b>{esc(se["title"])}</b></p><p class="lbl">{esc(se["src"])}</p></div>'
            f'{build.season_svg()}{build.season_svg(True)}</div>')


# ---------------------------------------------------------------- calendar
def events():
    """Every dated thing in the edition: the ministry's season dates, what is ahead, and the calendar stories."""
    ev = []
    for e in E['season']['events']:
        ev.append({'date': e['date'], 'what': e['label'], 'kind': e.get('kind', 'Season'), 'src': e.get('src', E['season']['src']),
                   **({'sid': e['sid']} if e.get('sid') else {})})
    for a in E['ahead']:
        if not any(x['date'] == a['date'] for x in ev):
            ev.append({'date': a['date'], 'what': a['text'], 'kind': a['when'], 'src': a['src']})
    for sid, s in S.items():
        if s['key'] == 'calendar':
            for x in ev:
                if x['date'] == s['date'] and 'sid' not in x:
                    x['sid'] = sid
    ev.append({'date': '2026-10-07', 'what': 'Palestinian Heritage Day opens in Hebron\'s Old City', 'kind': 'Day',
               'src': 'WAFA', 'sid': 'heritage-day-launched-hebron-old-city'})
    ev.append({'date': '2026-10-16', 'what': 'World Food Day', 'kind': 'Day', 'src': 'FAO'})
    ev.append({'date': '2026-10-20', 'what': 'National olive campaign launched in Battir', 'kind': 'Harvest',
               'src': 'PNN', 'sid': 'battir-hosts-national-harvest-campaign'})
    return sorted(ev, key=lambda x: x['date'])


def ics(ev):
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Olive Palestine//Season 2026//EN', 'CALSCALE:GREGORIAN',
             'X-WR-CALNAME:Olive Palestine · season 2026']
    for i, x in enumerate(ev):
        d0 = D(x['date'])
        lines += ['BEGIN:VEVENT', f'UID:op-{x["date"]}-{i}@olive-palestine', f'DTSTAMP:{TODAY:%Y%m%d}T000000Z',
                  f'DTSTART;VALUE=DATE:{d0:%Y%m%d}', f'DTEND;VALUE=DATE:{d0 + dt.timedelta(days=1):%Y%m%d}',
                  'SUMMARY:' + x['what'].replace(',', '\\,').replace(';', '\\;'), f'DESCRIPTION:Source: {x["src"]}', 'END:VEVENT']
    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines) + '\r\n'


def calendar_page():
    ev = events()
    rows, marked = [], False
    for x in ev:
        d0 = D(x['date'])
        if not marked and d0 >= TODAY:
            rows.append(f'<li class="today-row" aria-label="Today"><span class="dot"></span><b>Today</b> · {long_day(TODAY)}</li>')
            marked = True
        state = 'past' if d0 < TODAY else 'next'
        what = f'<a href="{link(x["sid"])}">{esc(x["what"])}</a>' if x.get('sid') else esc(x['what'])
        rows.append(f'<li class="ev {state} rise"><time datetime="{x["date"]}"><small>{esc(x["kind"])}</small>{day(d0, wd=True)}'
                    f'{"" if d0.year == TODAY.year else f" {d0.year}"}</time><p>{what} <span class="src">{esc(x["src"])}</span></p></li>')
    write('assets/olive-palestine-2026.ics', ics(ev))
    body = (page_head('Calendar', 'The picking season and every dated event in this edition, from the ministry\'s dates to festivals and exhibitions.',
                      'day 7 of the baladi Nabali picking.', lbl='The season')
            + f'<section class="sline"><div class="wrap almanac-mini ink">{season_block()}</div></section>'
            + f'''<section class="cal" aria-labelledby="cal-h"><div class="wrap">
  <div class="desk-head"><h2 id="cal-h">Every date</h2><div><a class="btn ghost" href="{build.R}assets/olive-palestine-2026.ics" download>Add the season to your calendar (.ics)</a></div></div>
  <div class="course"></div>
  <ol class="evlist">{"".join(rows)}</ol>
</div></section>''')
    return shell('Calendar · Olive Palestine', 'The 2026 picking calendar and every dated event in the edition.', 'calendar.html', body, 'calendar')


# ---------------------------------------------------------------- archive
def archive_page():
    by = {}
    for sid, s in S.items():
        by.setdefault(D(s['published']).month, []).append(sid)
    first = min((m for m in range(1, 13) if by.get(m)), default=TODAY.month)
    blocks = [f'<section class="mo-b empty" id="m01" aria-labelledby="mh01"><h2 id="mh01">January – {dt.date(TODAY.year, first - 1, 1):%B}</h2>'
              f'<div><p class="txt muted">Before this prototype’s first edition. Monthly editions start in October 2026.</p>'
              + ''.join(f'<span id="m{m:02d}"></span>' for m in range(2, first)) + '</div></section>'] if first > 1 else []
    for m in range(first, 13):
        d0 = dt.date(TODAY.year, m, 1)
        mname = d0.strftime('%B')
        ids = order(by.get(m, []))
        if m == TODAY.month:
            body = (f'<p class="txt">This month\'s edition: {len(ids)} stories, the picking calendar and the recipe of the season.</p>'
                    f'<p><a class="btn" href="{build.R}home.html">Open the October edition {icon("i-right")}</a></p>')
            state = 'cur'
        elif m > TODAY.month:
            soon = [x for x in events() if D(x['date']).month == m and D(x['date']).year == TODAY.year]
            body = ('<p class="txt">This month\'s edition opens on the first of the month. Already on its calendar:</p><ul class="soon">'
                    + ''.join(f'<li><b>{day(x["date"])}</b> {esc(x["what"])}</li>' for x in soon) + '</ul>') if soon else \
                '<p class="txt">This month\'s edition opens on the first of the month.</p>'
            state = 'later'
        elif ids:
            body = ('<p class="txt">Background stories first reported this month, kept because they explain October:</p><ul class="alist">'
                    + ''.join(build.row(i) for i in ids) + '</ul>')
            state = 'past'
        else:
            body = '<p class="txt muted">Before this prototype\'s first edition. Monthly editions start in October 2026.</p>'
            state = 'empty'
        blocks.append(f'<section class="mo-b {state}" id="m{m:02d}" aria-labelledby="mh{m:02d}"><h2 id="mh{m:02d}">{mname}'
                      f'{"<i class=\"dot\"></i>" if state == "cur" else ""}</h2><div>{body}</div></section>')
    body = (page_head('Every month', 'The site is an almanac: one edition a month, each following what the land does that month.', lbl='Archive')
            + f'<section class="archive"><div class="wrap">{"".join(blocks)}</div></section>')
    return shell('Every month · Olive Palestine', 'The monthly editions of Olive Palestine.', 'archive.html', body, 'archive')


# ---------------------------------------------------------------- about, letter, search, credits, 404
def about_page():
    body = page_head('About', 'Olive Palestine follows the land of Palestine month by month.', lbl='About') + f'''
<section class="prose-page"><div class="wrap narrow">
  <h2 class="h-l">An almanac of the land</h2>
  <p class="dek">Every month the land does something different: it is picked, pressed, sown, grazed or left to rest. Olive Palestine follows that year, and the people who work the land through it: what is picked, pressed and planted, the food made from it, and the heritage kept around it.</p>
  <div class="course"></div>
  <h3 class="h-m">How it is made</h3>
  <p class="txt">Each edition opens on the first of the month and grows through it. Stories are retold in our own words from named reports: the Palestinian Ministry of Agriculture, UN agencies, WAFA, PNN and other outlets, each credited and linked on the story. Background stories from earlier months are marked as such.</p>
  <h3 class="h-m">Photographs</h3>
  <p class="txt">Photographs come from Wikimedia Commons under free licences, in their own colour, captioned with the place, the year and the photographer. A photograph only sits beside a story it shows; a story without one gets a plain plate with its place.</p>
  <h3 class="h-m">The identity</h3>
  <p class="txt">The mark is an olive cut in half, which is also a terraced hill seen from above. <a class="inl" href="{build.R}index.html">Read how it was made</a>.</p>
  <p class="note">This is a design prototype by TakTek. Contact details, the editorial team and the newsletter will be added when the site goes live.</p>
</div></section>'''
    return shell('About · Olive Palestine', 'What Olive Palestine is and how it is made.', 'about.html', body, 'about')


def letter_page():
    body = page_head('The monthly letter', 'One email on the first of each month: what the land does that month, and the dates to know.', lbl='Newsletter') + f'''
<section class="prose-page"><div class="wrap narrow">
  <form class="letter" id="letter-f" novalidate>
    <label for="em">Email address</label>
    <input id="em" name="email" type="email" autocomplete="email" inputmode="email" placeholder="name@example.com" required>
    <fieldset><legend>Also send me</legend>
      <label class="chk"><input type="checkbox" name="cal" checked> The picking calendar, when the ministry sets dates</label>
      <label class="chk"><input type="checkbox" name="recipe"> The recipe of the season</label>
    </fieldset>
    <button class="btn" type="submit">{icon("i-mail")}Send me the letter</button>
    <p class="note" id="letter-msg" role="status" aria-live="polite">This is a design prototype: nothing is sent or stored.</p>
  </form>
  <div class="course"></div>
  <h3 class="h-m">What the November letter will carry</h3>
  <ul class="soon">{"".join(f'<li><b>{day(x["date"])}</b> {esc(x["what"])}</li>' for x in events() if D(x["date"]).month == 11)}</ul>
</div></section>
<script>document.getElementById('letter-f').addEventListener('submit',function(e){{e.preventDefault();var f=this,i=f.email,m=document.getElementById('letter-msg');
if(!i.value||!i.checkValidity()){{i.setAttribute('aria-invalid','true');m.textContent='Please enter an email address like name@example.com.';i.focus();return}}
i.removeAttribute('aria-invalid');m.textContent='Thank you. In the live site, the November letter would go to '+i.value+'. This prototype sends nothing.'}});</script>'''
    return shell('The monthly letter · Olive Palestine', 'Sign up for the monthly letter.', 'letter.html', body, 'letter')


def search_data():
    out = []
    for sid in order(list(S)):
        s = S[sid]
        out.append({'u': f'story/{sid}.html', 'h': s['headline'], 'd': s['dek'], 'p': s['place'], 's': s['desk'],
                    'k': ' '.join(s['body']), 'i': s.get('photo') or '', 'dt': day(s['published'])})
    write('assets/data/search.json', json.dumps(out, ensure_ascii=False))


def search_page():
    body = page_head('Search', 'Every story in this edition, by word, place or person.', lbl='Search') + f'''
<section class="prose-page"><div class="wrap">
  <form class="sform" role="search" onsubmit="return false"><label class="vh" for="q">Search the stories</label>
    {icon("i-search")}<input id="q" type="search" placeholder="Try Battir, oil, Gaza, grapes" autocomplete="off"></form>
  <p class="by" id="sr-n" role="status" aria-live="polite"></p>
  <ul class="sres" id="sr"></ul>
</div></section>
<script>(function(){{var q=document.getElementById('q'),ul=document.getElementById('sr'),n=document.getElementById('sr-n'),data=[],R='{build.R}';
function e(s){{return s.replace(/[&<>"]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function show(){{var t=q.value.trim().toLowerCase(),w=t.split(/\\s+/).filter(Boolean),hits=data.filter(function(x){{var b=(x.h+' '+x.d+' '+x.p+' '+x.s+' '+x.k).toLowerCase();return w.every(function(y){{return b.indexOf(y)>-1}})}});
n.textContent=t?hits.length+(hits.length==1?' story':' stories')+' for “'+q.value.trim()+'”':data.length+' stories in this edition';
ul.innerHTML=hits.slice(0,40).map(function(x){{return '<li><a href="'+R+x.u+'">'+(x.i?'<span class="ph"><img src="'+R+'assets/img/photo/'+x.i+'.webp?v={V}" alt="" loading="lazy"></span>':'<span class="ph np"></span>')+
'<span class="t"><span class="kick"><b>'+e(x.s)+'</b><span>'+e(x.p)+'</span><span>'+x.dt+'</span></span><b class="h-s">'+e(x.h)+'</b><span class="txt">'+e(x.d)+'</span></span></a></li>'}}).join('')||'<li class="none"><p class="txt">Nothing in this edition matches. Try a place (Hebron, Jericho), a crop (grapes, dates) or a word like oil.</p></li>'}}
fetch(R+'assets/data/search.json?v={V}').then(function(r){{return r.json()}}).then(function(d){{data=d;var p=new URLSearchParams(location.search).get('q');if(p)q.value=p;show()}});
q.addEventListener('input',show);}})();</script>'''
    return shell('Search · Olive Palestine', 'Search the stories.', 'search.html', body, 'search')


def credits_page():
    ph = build.PH
    used = {s.get('photo') for s in S.values()} | {E['kitchen']['recipe']['photo']}
    rows = ''.join(f'<li>{build.thumb(k)}<p><b>{esc(p["caption"])}</b><span>{esc(p["author"])} · {esc(p["license"])} · '
                   f'<a class="inl" href="{esc(p["page_url"])}" rel="noopener" target="_blank">Wikimedia Commons<span class="vh"> (opens in a new tab)</span></a></span></p></li>'
                   for k, p in ph.items() if k in used)
    outlets = {}
    for s in S.values():
        outlets[s['source']] = outlets.get(s['source'], 0) + 1
    srcs = ''.join(f'<li><b>{esc(o)}</b><span>{n} {"story" if n == 1 else "stories"}</span></li>' for o, n in sorted(outlets.items(), key=lambda x: -x[1]))
    body = page_head('Sources &amp; credits', 'Who reported what we retell, who took the photographs, and the type.', lbl='Credits') + f'''
<section class="prose-page"><div class="wrap">
  <div class="cr-grid">
    <section><h2 class="h-m">Reporting</h2><p class="txt">Every story links the report it retells. In this edition:</p><ul class="outlets">{srcs}</ul></section>
    <section><h2 class="h-m">Type</h2><p class="txt"><b>Literata</b> by TypeTogether and <b>Commissioner</b> by Kostas Bartsokas, both under the SIL Open Font License.</p></section>
  </div>
  <div class="course"></div>
  <h2 class="h-m">Photographs</h2>
  <ul class="credits">{rows}</ul>
</div></section>'''
    return shell('Sources & credits · Olive Palestine', 'Sources, photographs and type.', 'credits.html', body, 'credits')


def notfound_page():
    m = build.MARKS['mark']
    walls = ''.join(f'<path d="{d}"/>' for d in m['stones'][0][:12])
    body = f'''<section class="nf"><div class="wrap">
  <svg class="nf-mark" viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke="#231B21" stroke-width="{m["skin"]}" stroke-linecap="round">{walls}</g></svg>
  <div><p class="lbl">404</p><h1 class="h-xl">This terrace hasn't been built yet</h1>
  <p class="dek">The page you asked for isn't here. The walls stop where the site does, for now.</p>
  <p class="go"><a class="btn" href="{build.R}home.html">Back to October {icon("i-right")}</a><a class="btn ghost" href="{build.R}search.html">Search the stories</a></p></div>
</div></section>'''
    return shell('Not found · Olive Palestine', 'Page not found.', '404.html', body, '404')


def main():
    n = 0
    build.R = '../'
    for sid in S:
        write(f'story/{sid}.html', story_page(sid))
        n += 1
    build.R = ''
    for key in SECTIONS:
        write(f'{key}.html', section_page(key))
    write('calendar.html', calendar_page())
    write('archive.html', archive_page())
    write('about.html', about_page())
    write('letter.html', letter_page())
    search_data()
    write('search.html', search_page())
    write('credits.html', credits_page())
    build.R = '/olive-palestine-prototype/'
    write('404.html', notfound_page())
    build.R = ''
    print(n, 'story pages ·', len(SECTIONS), 'section pages · calendar, archive, about, letter, search, credits, 404')


if __name__ == '__main__':
    main()
