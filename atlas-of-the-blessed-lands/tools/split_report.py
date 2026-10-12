"""Version 106: writes reports/settlements_on_the_line.md from splits_named.json (see tools/split_settlements.py).
Run: python3 tools/split_report.py <scratch dir>"""
import json, sys, os
D = sys.argv[1]
S = json.load(open(os.path.join(D, 'splits_named.json')))
NB = json.load(open(os.path.join(D, 'neighbours_named.json'))) if os.path.exists(os.path.join(D, 'neighbours_named.json')) else []
CN = {'UZ':'Uzbekistan','KG':'Kyrgyzstan','KZ':'Kazakhstan','CN':'China','IN':'India','TM':'Turkmenistan','TJ':'Tajikistan','PK':'Pakistan',
      'CD':'DR Congo','UG':'Uganda','RW':'Rwanda','BI':'Burundi','TZ':'Tanzania','ZM':'Zambia','MW':'Malawi','MZ':'Mozambique','KE':'Kenya',
      'SS':'South Sudan','SD':'Sudan','TD':'Chad','CF':'Central African Republic','LY':'Libya','DZ':'Algeria','TN':'Tunisia','NE':'Niger',
      'EG':'Egypt','ET':'Ethiopia','ER':'Eritrea','DJ':'Djibouti','SO':'Somalia','GR':'Greece','BG':'Bulgaria','MK':'North Macedonia',
      'AL':'Albania','TR':'Türkiye','GE':'Georgia','RU':'Russia','AM':'Armenia','AZ':'Azerbaijan','IR':'Iran','AF':'Afghanistan','IQ':'Iraq',
      'SY':'Syria','IL':'Israel','JO':'Jordan','LB':'Lebanon','SA':'Saudi Arabia','YE':'Yemen','OM':'Oman','AE':'United Arab Emirates','?':'(no country)'}
def nm(s):
    m = (s.get('main') or [{}])[0]
    n = m.get('en') or m.get('name') or 'unnamed settlement'
    if m.get('en') and m.get('name') and m['name'] != m['en']: n += f" ({m['name']})"
    if m.get('side') == 'near': n = 'near ' + n + f" ({m.get('km')} km)"
    return n
def ppl(v): return f"{int(round(v)):,}"
def hoods(s, side):
    q = [p for p in s['places'] if p['side'] == side and p['sub'] != 'locality']
    q2 = [p for p in s['places'] if p['side'] == side and p['sub'] == 'locality']
    names = [(p['en'] or p['name']) for p in q2 + q if (p['en'] or p['name'])]
    seen = []; [seen.append(x) for x in names if x not in seen]
    return ', '.join(seen[:25]) + (' …' if len(seen) > 25 else '')
L = []
L.append('# Settlements on the line: V2 and V2N (Version 106)\n')
L.append('Settlements (cities, towns, villages, hamlets, neighbourhoods; rural and urban) that the edge of V2 or V2N cuts in two, with the people on each side.\n')
L.append('**How it was found (my method):** population from Meta\'s High Resolution Settlement Layer (people per ~30 m cell, census-based, about 2015–2020); '
         'inhabited cells less than about 90 m apart are counted as one settlement. V2 is taken as meant: every country listed whole is in to its real borders '
         'and coasts, other countries are out, and in the partly included countries (Uzbekistan, Kyrgyzstan, Kazakhstan, China; India in V2N) the drawn line decides. '
         'Real borders: Overture Maps country areas (from OpenStreetMap). Names: Overture Maps places (towns, villages, neighbourhoods) inside each settlement. '
         'China has no Meta population data: there, Overture building outlines were used instead (no settlement there is cut). Numbers of people are estimates from the grid, not a census. '
         'In thickly settled countryside (the Rwandan and Ugandan highlands, the Khorezm and Fergana oases, Punjab) houses run on almost without a break, so one "settlement" can be a whole populated district: '
         'there the number on the near side counts the countryside too, and the number on the far side is the better measure of the people cut off. '
         'Where a settlement is marked "at least", it reaches beyond the largest window measured (about 80 km across).\n')
for v, title in [('x', 'V2'), ('xn', 'V2N')]:
    A = sorted([s for s in S if s['v'] == v and s['kind'] == 'new'], key=lambda s: -(s['in'] + s['out']))
    B = sorted([s for s in S if s['v'] == v and s['kind'] == 'border'], key=lambda s: -(s['in'] + s['out']))
    L.append(f'\n## {title}\n')
    L.append(f'### A. Cut by the author\'s own lines ({len(A)} settlements; about {ppl(sum(s["in"] for s in A))} people were inside and {ppl(sum(s["out"] for s in A))} outside)\n')
    L.append('Since Version 106 every one of these is whole INSIDE ' + title + ': the line now goes round it (checked again after the change: none is cut any more).\n')
    L.append('| # | Settlement | Country | People inside before | People outside before (now added) | Places in it (inside · outside before) | Where |\n|---|---|---|---|---|---|---|')
    for i, s in enumerate(A, 1):
        c = ', '.join(CN.get(k, k) for k in sorted(set(s['cin']) | set(s['cout'])))
        L.append(f"| {i} | {nm(s)} | {c} | {ppl(s['in'])} | {ppl(s['out'])} | {hoods(s,'in') or '–'} · {hoods(s,'out') or '–'} | {s['lat']:.3f} N, {s['lon']:.3f} E |")
    C2 = sorted([s for s in NB if s['v'] == v], key=lambda s: -(s['in'] + s['out']))
    if C2:
        L.append(f'\n### A2. Neighbours taken in whole ({len(C2)} settlements; about {ppl(sum(s["out"] for s in C2))} people)\n')
        L.append('The new line round the settlements in A is drawn smooth (gaps of up to about 300 m between houses closed, so that a town goes in as one piece); '
                 'where it then touched a neighbouring village, that village was taken in whole as well.\n')
        L.append('| # | Settlement | Country | People already inside | People added | Places in it | Where |\n|---|---|---|---|---|---|---|')
        for i, s in enumerate(C2, 1):
            c = ', '.join(CN.get(k, k) for k in sorted(s['cin']))
            L.append(f"| {i} | {nm(s)} | {c} | {ppl(s['in'])} | {ppl(s['out'])} | {hoods(s,'in') or '–'} | {s['lat']:.3f} N, {s['lon']:.3f} E |")
    L.append(f'\n### B. Across an existing international border ({len(B)} settlements; about {ppl(sum(s["in"] for s in B))} people inside and {ppl(sum(s["out"] for s in B))} outside)\n')
    L.append('Here ' + title + ' follows a border that already exists, so ' + title + ' does not newly divide anyone; these are towns that have grown together across it. '
             'NOT changed: adding the outer halves would mean adding parts of countries that are not in ' + title + ' (for the author to decide).\n')
    L.append('| # | Settlement | Inside (country: people) | Outside (country: people) | Places (inside · outside) | Where |\n|---|---|---|---|---|---|')
    for i, s in enumerate(B, 1):
        ci = ', '.join(f"{CN.get(k,k)}: {ppl(x)}" for k, x in sorted(s['cin'].items(), key=lambda t: -t[1]))
        co = ', '.join(f"{CN.get(k,k)}: {ppl(x)}" for k, x in sorted(s['cout'].items(), key=lambda t: -t[1]))
        if s.get('trunc'): ci, co = 'at least ' + ci, 'at least ' + co
        L.append(f"| {i} | {nm(s)} | {ci} | {co} | {hoods(s,'in') or '–'} · {hoods(s,'out') or '–'} | {s['lat']:.3f} N, {s['lon']:.3f} E |")
out = os.path.join(os.path.dirname(__file__), '..', 'reports', 'settlements_on_the_line.md')
open(out, 'w').write('\n'.join(L) + '\n'); print('written', out)
