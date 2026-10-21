"""Write tools/out/og.html, the 1200 x 630 link card, then capture it as assets/og.png.

python -I tools/og.py
node --experimental-websocket tools/shot.mjs http://localhost:8169/tools/out/og.html assets/og.png 1200 630 view

The card is the month and the lead: the wordmark on black olive, the month in display light,
the lead's headline, and its photograph.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import E, esc, wordmark  # noqa: E402

L = E['stories'][E['lead']]
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../assets/css/op.css">
<style>html,body{{margin:0;background:#231B21}}.og{{display:grid;grid-template-columns:640px 560px;width:1200px;height:630px}}
.l{{position:relative;overflow:hidden;padding:52px 56px;display:flex;flex-direction:column;justify-content:space-between;color:#EFE9DC}}
.l .hill{{position:absolute;right:-380px;top:-90px;width:980px;opacity:.85;z-index:0}}
.l > *{{position:relative}}.l .wm{{width:330px}}
.l h1{{font-family:Literata;font-weight:300;font-size:118px;line-height:.86;letter-spacing:-.035em;margin:0}}
.l p{{font-family:Literata;font-size:30px;line-height:1.16;font-weight:500;letter-spacing:-.01em;margin:18px 0 0;max-width:20ch}}
.r{{background:#3A2C36 url(../../assets/img/photo/{L["photo"]}.webp) center/cover}}</style></head>
<body><div class="og"><div class="l"><img class="hill" src="../../assets/brand/hill.svg" alt="">{wordmark("wm", "#EFE9DC", "#D2603F")}
<div><h1>{esc(E["month"])}</h1><p>{esc(L["headline"])}</p></div></div><div class="r"></div></div></body></html>'''
os.makedirs(os.path.join(build.ROOT, 'tools', 'out'), exist_ok=True)
open(os.path.join(build.ROOT, 'tools', 'out', 'og.html'), 'w', encoding='utf-8').write(html)
print('tools/out/og.html')
