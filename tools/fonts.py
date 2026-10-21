"""Self-hosted WOFF2 subsets of the two brand faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Literata (TypeTogether, OFL) sets the voice: headlines in its display cut (opsz 72), whose
wedge serifs read as cut stone, and reading text in its text cut. It carries the figures
(tabular, lining or old-style) and true small caps for sources.
Commissioner (Kostas Bartsokas, OFL) sets the labels: navigation, kickers, the calendar.
Its FLAR axis flares the stroke ends like letters cut into a wall; labels use a little of it,
the wordmark's PALESTINE uses all of it.
Both are instanced to the axis ranges the site uses, and every layout feature is kept.
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Basic Latin + Latin-1 + Latin Extended-A, the transliteration letters place names use
# (ḥ ṣ ḍ ṭ ẓ ʿ ʾ), typographic punctuation, arrows, the shekel, euro and dinar-friendly signs.
UNICODES = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x1E0C, 0x1E0D, 0x1E24, 0x1E25, 0x1E62, 0x1E63, 0x1E6C, 0x1E6D, 0x1E92, 0x1E93, 0x02BE, 0x02BF, 0x02BC,
     0x2009, 0x200A, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
     0x2032, 0x2033, 0x2039, 0x203A, 0x2044, 0x20AC, 0x20AA, 0x2190, 0x2191, 0x2192, 0x2193,
     0x2197, 0x2198, 0x2212, 0x2248, 0x2264, 0x2265, 0x00D7, 0x00B0, 0x00B7, 0x00B2, 0x2153, 0x00BD, 0x00BC]
)

JOBS = [
    # (source, out, axis limits)
    ('literata-Literata[opsz,wght].ttf', 'literata.woff2', {'opsz': (7, 72), 'wght': (300, 750)}),
    ('literata-Literata-Italic[opsz,wght].ttf', 'literata-italic.woff2', {'opsz': (7, 72), 'wght': (300, 750)}),
    ('commissioner-Commissioner[FLAR,VOLM,slnt,wght].ttf', 'commissioner.woff2',
     {'wght': (300, 800), 'FLAR': (0, 100), 'VOLM': 0, 'slnt': 0}),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.name_languages = ['*']
    o.notdef_outline = True
    o.glyph_names = False
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits in JOBS:
    font = TTFont(os.path.join(SRC, src))
    font = instancer.instantiateVariableFont(font, limits)
    buf = io.BytesIO()
    font.save(buf)  # round-trip so the partial instance subsets cleanly
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    path = os.path.join(OUT, out)
    subset.save_font(font, path, options())
    print(out, os.path.getsize(path) // 1024, 'KB')

for src, lic in (('literata-OFL.txt', 'OFL-Literata.txt'), ('commissioner-OFL.txt', 'OFL-Commissioner.txt')):
    with open(os.path.join(SRC, src), encoding='utf-8') as f, open(os.path.join(OUT, lic), 'w', encoding='utf-8') as g:
        g.write(f.read())
