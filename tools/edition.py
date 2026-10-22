"""Compose tools/edition.json and tools/photos.json from research/news.json and research/photos.json.

python -I tools/edition.py

The research files hold every sourced item and photo candidate; this script is the editor's
desk: it picks the lead, places each story, and writes the captions the site prints. Every
story keeps the source, date and wording the research verified; a story gets a photograph
only if the photograph shows what the story is about, or the place it is about.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS = {i['id']: i for i in json.load(open(os.path.join(ROOT, 'research', 'news.json'), encoding='utf-8'))}
CAND = {p['file']: p for p in json.load(open(os.path.join(ROOT, 'research', 'photos.json'), encoding='utf-8'))}

# slug: (Commons file, alt, caption, focus)
PHOTOS = {
    'battir-terraces': ('File:BattirVillageJan212023.jpg',
                        "Battir's terraced valley seen from above, with the village houses on the far slope",
                        'The terraces of Battir, west of Bethlehem, January 2023', '50% 55%'),
    'nabali-2026': ('File:زيتون نبالي محسن.jpg', 'Branches of light green improved Nabali olives among silvery leaves',
                    'Improved Nabali olives on the branch, photographed 30 September 2026', '50% 45%'),
    'suri-2026': ('File:زيتون الـسُّري (الصُّري) الفلسطيني.jpg', 'Suri olives turning purple on the branch',
                  'Suri olives turning on the branch, photographed 30 September 2026', None),
    'baladi-green': ('File:زيتون نبالي بلدي أخضر.jpg', 'A cluster of green baladi Nabali olives on a branch',
                     'Baladi Nabali olives, October 2019', None),
    'gloved-hand': ('File:قطف ثمار الزيتون.jpg', 'A gloved hand holds a sprig of ripening purple and green olives',
                    'Picking by hand, Hebron governorate, October 2020', '50% 40%'),
    'qaffin-harvest': ('File:Olive harvest.jpg', 'Harvesters, some on ladders, picking a large olive tree on rocky ground',
                       'Picking in Qaffin, Tulkarm, October 2008', None),
    'nablus-picking': ('File:Olives Land nablus 2.jpg', 'A man in a cap and a boy picking olives among dense branches',
                       'Picking near Nablus (date not recorded)', None),
    'kufr-jammal-press': ('File:Olive Oil Presser in Kufrjammal, Palestine.jpg', 'A stainless-steel decanter inside an olive press',
                          'Inside a working press in Kufr Jammal, Tulkarm, 2005', None),
    'natsheh-press': ('File:Olive squwisser77.jpg', 'The stone crushing wheel of an old olive press under a stone vault',
                      "The stone wheel of the old al-Natsheh press, Hebron's Old City, 2019", None),
    'sebastia-columns': ('File:الأعمدة الرومانية القديمة في مدينة سبسطية.jpg', "A row of Roman columns standing among stone blocks on Sebastia's hill",
                         'The Roman columns of Sebastia, Nablus, July 2023', None),
    'ramla-dress': ('File:Ramla Dress (Palestinian Thobe).jpg', 'A black village dress with dense red cross-stitch on the chest, sleeves and skirt',
                    'A Ramla village dress in the Tiraz museum, July 2021', '50% 30%'),
    'hebron-dress': ('File:Palestinian Dress in Hebron Old City.jpg', 'An embroidered dress on a mannequin in a stone-paved market alley',
                     "An embroidered dress in the market of Hebron's Old City, June 2023", '50% 30%'),
    'jericho-dates': ("File:'Palm date harvesting(Jericho)'.jpg", 'Date bunches tied in protective bags high on a palm trunk',
                      'Date bunches bagged on the palm, Jericho, 2007', None),
    'hebron-grapes-2026': ('File:مهرجان العنب، البلدة القديمة، الخليل.jpg', 'A towering display of hanging grape bunches, green to dark red, at a festival',
                           "The grape festival in Hebron's Old City, 27 September 2026", '50% 35%'),
    'hebron-grapes': ('File:العنب الفلسطيني.jpg', 'Green grape bunches hanging among vine leaves', 'Grapes on the vine, Hebron, July 2020', None),
    'masafer-flock': ('File:Al-Halawa village, Masafer Yatta, shepherds and their flock.jpg', 'Shepherds with a flock of goats at a feeding trough',
                      'Shepherds and their flock in al-Halawa, Masafer Yatta, 2025', None),
    'musakhan': ('File:أكلة المسخن الفلسطينية من العادات والتقاليد الاجتماعية تصوير كميل عبادي 2024.jpg',
                 'Two large rounds of musakhan bread heaped with onions and sumac', 'Musakhan, May 2024', '50% 50%'),
    'nablus-soap': ('File:Nabulsi soap 006.jpg', 'Stacked olive oil soap on wooden tables under a vaulted ceiling',
                    "Olive oil soap in an old factory in Nablus's Old City, 2019", None),
    'zaatar': ('File:زعتر مجفف.jpg', "A round tray of dried za'atar with stripes of red sumac and sesame", "Za'atar with sumac and sesame, April 2025", None),
    'gaza-wheat': ('File:Wheat farms inside Gaza before the Gaza war 23-25.jpg', 'A green wheat field under a cloudy sky',
                   'Wheat in Gaza before the war, February 2023', None),
    'tel-rumeida-tree': ('File:An ancient Roman olive tree in Tel Rumeida in the city of Hebron, Palestine.jpg',
                         'An ancient two-trunked olive tree on a dry hillside', 'An ancient olive tree at Tel Rumeida, Hebron, July 2020', '50% 60%'),
}

# story id -> photo slug (only where the photo shows the story's subject or place)
ART = {
    'battir-hosts-national-harvest-campaign': 'battir-terraces',
    'ocha-harvest-could-recover-to-21000-tonnes': 'nabali-2026',
    'deir-istiya-farmer-500-trees': 'qaffin-harvest',
    'zawayda-press-rebuilt-from-rubble': 'kufr-jammal-press',
    'fayyad-calls-for-awna-communal-picking': 'nablus-picking',
    'tammun-umm-al-kubaysh-picking-day': 'suri-2026',
    'pnn-harvest-challenges-early-picking': 'gloved-hand',
    'ministry-sets-2026-picking-dates': 'baladi-green',
    'dura-cooperative-grape-molasses': 'hebron-grapes-2026',
    'al-khader-grape-festival-eighth': 'hebron-grapes',
    'jericho-date-harvest-28860-tonnes': 'jericho-dates',
    'gaza-winter-planting-hampered': 'gaza-wheat',
    'masafer-yatta-feed-and-tractors-seized': 'masafer-flock',
    'hebron-old-city-olive-oil-soap-maker': 'nablus-soap',
    'sebastia-world-heritage-celebration': 'sebastia-columns',
    'heritage-day-launched-hebron-old-city': 'hebron-dress',
    'bayt-al-dammah-folk-games-zababdeh': 'natsheh-press',
    'nisaa-al-shams-online-market': 'zaatar',
    'un-harvest-attacks-pass-last-season': 'tel-rumeida-tree',
    'fayyad-oil-prices-four-regions': 'kufr-jammal-press',
    'cal-improved-nabali-picking-5-nov': 'nabali-2026',
    'cal-world-olive-tree-day-26-nov': 'tel-rumeida-tree',
    'cal-iamm-tatreez-until-april-2027': 'ramla-dress',
}

DESK = {'olives': 'Olives', 'market': 'Market', 'vines': 'Vines', 'palms': 'Dates', 'fields': 'Fields', 'flocks': 'Flocks',
        'kitchen': 'Kitchen', 'heritage': 'Heritage', 'calendar': 'Calendar'}


def outlet(s):
    s = s.split(' (')[0].split(';')[0].split(',')[0].strip()
    return {'Palestine News Network': 'PNN', 'UN OCHA oPt - Humanitarian Situation Report': 'OCHA',
            'Palestinian Information Center': 'Palestinian Information Center', 'Reuters': 'Reuters'}.get(s, s)


def story(i):
    n = NEWS[i]
    return {'headline': n['headline'], 'dek': n['summary'], 'place': n['place'], 'date': n['date'], 'published': n['published'],
            'desk': DESK[n['desk']], 'source': outlet(n['source']), 'url': n['url'], 'background': bool(n.get('background')),
            'photo': ART.get(i), 'figures': n.get('figures', []), 'body': n.get('body', []), 'people': n.get('people', []),
            'lang': n.get('source_lang', 'en'), 'key': n['desk']}


USED = ['battir-hosts-national-harvest-campaign', 'un-harvest-attacks-pass-last-season', 'kisan-120-trees-cut', 'birin-dog-attack-on-pickers',
        'ocha-harvest-could-recover-to-21000-tonnes', 'deir-istiya-farmer-500-trees', 'gaza-groves-150000-trees-left', 'zawayda-press-rebuilt-from-rubble',
        'fayyad-calls-for-awna-communal-picking', 'tammun-umm-al-kubaysh-picking-day', 'pnn-harvest-challenges-early-picking', 'ministry-sets-2026-picking-dates',
        'dura-cooperative-grape-molasses', 'al-khader-grape-festival-eighth', 'arraba-grape-farm-48-hour-order', 'beit-ummar-water-once-a-week',
        'jericho-date-harvest-28860-tonnes', 'gaza-winter-planting-hampered', 'first-showers-flash-flood-warning', 'atouf-water-pipeline-destroyed',
        'gaza-agricultural-initiatives-makshouf', 'masafer-yatta-feed-and-tractors-seized', 'gaza-livestock-and-bees-losses', 'wadi-abu-hindi-130-sheep-seized',
        'um-eyad-bethlehem-pastries', 'hebron-old-city-olive-oil-soap-maker', 'nisaa-al-shams-online-market', 'gaza-family-cannot-afford-oil',
        'sebastia-world-heritage-celebration', 'heritage-day-launched-hebron-old-city', 'bayt-al-dammah-folk-games-zababdeh', 'fayyad-oil-prices-four-regions']

E = {
    'date': '2026-10-21',
    'title': 'Olive Palestine · October on the land',
    'description': 'What Palestine picks, presses and plants in October: the olive harvest, the new oil, the kitchen and the heritage around it.',
    'topline': 'Day 7 of the baladi Nabali picking',
    'line': 'Land, harvest and table, told month by month',
    'loader': 'Laying the walls',
    'month': 'October',
    'month_line': 'The month of picking, new oil and the first showers',
    'season': {'title': 'The picking calendar, 2026', 'src': 'Ministry of Agriculture, via WAFA',
               'start': '2026-10-01', 'end': '2026-11-30', 'compact': ['2026-10-06', '2026-11-30'], 'band': ['2026-10-15', '2026-11-30'],
               'events': [{'date': '2026-10-11', 'label': 'Presses open for tests', 'short': 'Presses', 'sid': 'ministry-sets-2026-picking-dates'},
                          {'date': '2026-10-15', 'label': 'Baladi Nabali picking opens', 'short': 'Baladi Nabali', 'sid': 'ministry-sets-2026-picking-dates'},
                          {'date': '2026-11-05', 'label': 'Improved Nabali and irrigated olives', 'short': 'Improved Nabali', 'sid': 'cal-improved-nabali-picking-5-nov'},
                          {'date': '2026-11-26', 'label': 'World Olive Tree Day', 'short': 'Olive Tree Day', 'kind': 'Day', 'src': 'UNESCO', 'sid': 'cal-world-olive-tree-day-26-nov'}]},
    'counts': [{'n': 7, 'unit': 'days', 'text': 'of picking for baladi Nabali, the main rain-fed olive'},
               {'n': 15, 'unit': 'days', 'text': 'until improved Nabali and the irrigated varieties'},
               {'n': 21000, 'unit': 't', 'text': 'of oil the ministry expects, three times last season'}],
    'lead': 'battir-hosts-national-harvest-campaign',
    'lead_facts': [{'n': '21,000 t', 'text': 'of oil possible this season, against 7,000 t in 2025', 'src': 'OCHA, 19 Oct'},
                   {'n': '200+', 'text': 'attacks on farmers this season, more than all of 2025', 'src': 'UN, via WAFA, 16 Oct'}],
    'also': ['un-harvest-attacks-pass-last-season', 'kisan-120-trees-cut', 'birin-dog-attack-on-pickers'],
    'land': {
        'pick': [{'t': 'Baladi Nabali olives', 'note': 'since 15 Oct, every governorate', 'href': '#ministry-sets-2026-picking-dates'},
                 {'t': 'Medjool dates', 'note': 'Jericho, the Jordan Valley', 'href': '#jericho-date-harvest-28860-tonnes'},
                 {'t': 'The last grapes', 'note': 'into dibs and anabiyyeh, Dura', 'href': '#dura-cooperative-grape-molasses'}],
        'press': [{'t': 'New oil', 'note': '$13 to $26 a kilo at the press', 'href': '#prices'},
                  {'t': 'One line of seven', 'note': 'a press rebuilt, al-Zawayda', 'href': '#zawayda-press-rebuilt-from-rubble'},
                  {'t': 'Olive oil soap', 'note': "Hebron's Old City", 'href': '#hebron-old-city-olive-oil-soap-maker'}],
        'plant': [{'t': 'Winter planting', 'note': 'Gaza: seed and fuel scarce', 'href': '#palms'},
                  {'t': 'The first showers', 'note': 'a flood warning for the valleys', 'href': '#palms'},
                  {'t': 'Gardens rebuilt', 'note': '~100 small projects in Gaza', 'href': '#palms'}]},
    'olives': {'line': 'The picking, the presses and the groves people can and cannot reach.',
               'big': 'ocha-harvest-could-recover-to-21000-tonnes',
               'side': ['deir-istiya-farmer-500-trees', 'gaza-groves-150000-trees-left', 'zawayda-press-rebuilt-from-rubble'],
               'row': ['fayyad-calls-for-awna-communal-picking', 'tammun-umm-al-kubaysh-picking-day', 'pnn-harvest-challenges-early-picking',
                       'ministry-sets-2026-picking-dates']},
    'figures_intro': 'The numbers that shape this harvest, each with the body that counted it. Prices are for new oil, straight from the press.',
    'figures': [{'n': '21,000', 'unit': 't', 'text': "oil the ministry expects this season; last season's was 7,000 t", 'src': 'OCHA, 19 Oct'},
                {'n': '$13–26', 'unit': '/kg', 'text': 'new oil at the press, from the northern West Bank to Beit Jala', 'src': 'Fayyad Fayyad, Raya, 18 Oct', 'hot': True},
                {'n': '200+', 'text': 'settler attacks on farmers this season, against 185 in all of 2025', 'src': 'UN, via WAFA, 16 Oct', 'hot': True},
                {'n': '150,000', 'text': "of Gaza's roughly two million olive trees still standing", 'src': 'Reuters, 14 Oct'},
                {'n': '₪50–55', 'unit': '/litre', 'text': 'local olive oil in Gaza, against about ₪20 for imported oil', 'src': 'Palestinian Information Center, 17 Oct'},
                {'n': '28,860', 'unit': 't', 'text': 'dates forecast for this season in Jericho and the Jordan Valley', 'src': 'WAFA, 30 Sep'}],
    'trio': [{'key': 'vines', 'name': 'Vines &amp; figs', 'now': 'the last grapes go into dibs and molasses.',
              'stories': ['dura-cooperative-grape-molasses'], 'list': ['al-khader-grape-festival-eighth', 'arraba-grape-farm-48-hour-order', 'beit-ummar-water-once-a-week']},
             {'key': 'palms', 'name': 'Palms &amp; fields', 'now': 'Medjool picking; winter sowing waits for rain.',
              'stories': ['jericho-date-harvest-28860-tonnes'], 'list': ['gaza-winter-planting-hampered', 'first-showers-flash-flood-warning', 'atouf-water-pipeline-destroyed']},
             {'key': 'flocks', 'name': 'Flocks', 'now': 'stocking feed before the winter grazing thins.',
              'stories': ['masafer-yatta-feed-and-tractors-seized'], 'list': ['gaza-livestock-and-bees-losses', 'wadi-abu-hindi-130-sheep-seized']}],
    'kitchen': {'line': 'What the season puts on the table, and the people who make it.',
                'recipe': {'photo': 'musakhan', 'when': 'the weeks of new oil', 'title': 'Musakhan, the dish of pressing time',
                           'dek': 'Taboon bread soaked in this season’s oil, heaped with onions cooked slowly with sumac and allspice, and roast chicken on top. A dish from the Tulkarm and Jenin hills, made when the new oil comes home from the press.',
                           'need': ['Taboon bread, or a thin flatbread', 'New-season olive oil, generously', 'Onions, plenty of them, sliced',
                                    'Sumac and allspice', 'Chicken pieces', 'Pine nuts, fried in oil'],
                           'method': ['Cook the onions slowly in plenty of oil with sumac and allspice, until soft and sweet.',
                                      'Roast the chicken with the same spices; some houses add saffron.',
                                      'Wet the bread with oil, spread the onions over it and set the chicken on top.',
                                      'Return it to the oven so the bread takes up the oil. Finish with pine nuts and more sumac.'],
                           'note': 'A home method, cooked by eye: every house has its own measures.', 'src': 'after Tamimi & Wrigley and Kassis'},
                'others': ['hebron-old-city-olive-oil-soap-maker', 'nisaa-al-shams-online-market', 'um-eyad-bethlehem-pastries']},
    'heritage': {'line': 'The places, crafts and customs the land has kept.', 'a': 'sebastia-world-heritage-celebration',
                 'b': ['heritage-day-launched-hebron-old-city', 'bayt-al-dammah-folk-games-zababdeh']},
    'ahead': [{'date': '2026-10-27', 'when': 'Delegation', 'text': "'Olives and Origins' harvest delegation to West Bank villages, until 5 November. Places are full.", 'src': 'CPT'},
              {'date': '2026-11-05', 'when': 'Picking', 'text': 'Picking opens for improved Nabali and the irrigated oil olives.', 'src': 'Ministry of Agriculture'},
              {'date': '2026-11-26', 'when': 'Day', 'text': 'World Olive Tree Day, proclaimed by UNESCO.', 'src': 'UNESCO'},
              {'date': '2027-04-25', 'when': 'Until', 'text': "'Tatreez' embroidery exhibition at the Islamic Arts Museum Malaysia, Kuala Lumpur.", 'src': 'IAMM'}],
    'about_html': '<b>Olive Palestine</b> follows the land of Palestine month by month: what is picked, pressed and planted, the food made from it, and the heritage kept around it. Every story names its source.',
    'stories': {i: story(i) for i in USED + [k for k in NEWS if k not in USED]},
}
E['stories'][E['lead']]['facts'] = E.pop('lead_facts')

ph = {}
for slug, (file, alt, cap, focus) in PHOTOS.items():
    c = CAND[file]
    ph[slug] = {'file': file, 'page_url': c['page_url'], 'author': c['author'].split('(')[0].strip(), 'license': c['license'],
                'date': str(c['date']), 'alt': alt, 'caption': cap}
    if focus:
        ph[slug]['focus'] = focus
missing = [s for s in ART.values() if s not in ph]
assert not missing, missing
json.dump(E, open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(ph, open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(E['stories']), 'stories ·', len(ph), 'photos')
