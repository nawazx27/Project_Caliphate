"""Version 456 (Nawaz: "Make sure you draw Nile end to end", with an OSM map of the Gilgel Abay from Gish Abay to Lake Tana). The Blue Nile's head
stream, the Gilgel (Little) Abay, is added to the Nile in src/four_rivers.json: the OSM-named Gilgel Abay / Lesser Abay (37.07 E 11.18 N to its mouth in
Lake Tana) and, below the spring at Gish Abay, the shortest path along the unnamed OSM river lines (~40 km), from tools/data/v456_gilgel_abay.json
(Overture base/water, release 2026-10-21.0). Coordinates rounded to 0.001."""
import json, os
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
G = json.load(open(os.path.join(HERE, 'tools/data/v456_gilgel_abay.json')))
F = os.path.join(HERE, 'src/four_rivers.json'); R = json.load(open(F))
nile = [r for r in R['rivers'] if r['k'] == 'nile'][0]
rnd = lambda c: [[round(x, 3), round(y, 3)] for x, y in c]
new = [rnd(G['upper'])] + [rnd(c) for c in G['named']]
have = {json.dumps(p) for p in nile['parts']}
add = [p for p in new if json.dumps(p) not in have and len(p) > 1]
nile['parts'] += add
print('parts added', len(add))
json.dump(R, open(F, 'w'), separators=(',', ':'), ensure_ascii=False)
