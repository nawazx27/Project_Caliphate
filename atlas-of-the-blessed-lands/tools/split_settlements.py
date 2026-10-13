"""Version 106 (2026-10-12, Nawaz: "Include all major and minor cities, neighborhoods, villages, towns, and both rural and urban areas
that are divided, separated, or split in half by the proposed borders of V2 ... preserve existing communities wherever possible").

Builds tools/data/split_settlements.geojson: for V2 (x) and V2N (xn), the outer part of every settlement that the author's own lines
(the Greater Khurāsān line through Uzbekistan, Kyrgyzstan, Kazakhstan and China; in V2N also the Punjab, Farghāna and Turkistan lines)
cut in two, so that tools/v2_whole_settlements.js can add it and keep the settlement whole inside.

Inputs (made by the scan in the session scratchpad, see notes.md Version 106):
  scan2_final.json   settlements cut by V2/V2N, from Meta's High Resolution Settlement Layer (population on a ~30 m grid,
                     dataforgood-fb-data on AWS; populated cells within ~90 m of each other count as one settlement), judged
                     against real country borders from Overture Maps (OpenStreetMap-based) country areas;
  splits_named.json  the same settlements with the names of the towns, villages and neighbourhoods inside them (Overture divisions).
Only kind == 'new' (people of the same country on both sides) is used; settlements cut by an existing international border are
listed in the report but not changed.
Run: python3 tools/split_settlements.py <scratch dir> [final.json named.json out.geojson]  (Version 107: the Balkan line uses balkan_final.json balkan_named.json balkan_settlements.geojson)"""
import json, sys, os
from shapely.geometry import shape, mapping, Polygon
from shapely.ops import unary_union
D = sys.argv[1]
F = json.load(open(os.path.join(D, sys.argv[2] if len(sys.argv) > 2 else 'scan2_final.json')))
N = {(s['v'], s['lon'], s['lat']): s for s in json.load(open(os.path.join(D, sys.argv[3] if len(sys.argv) > 3 else 'splits_named.json')))}
feats = []
for cell, ss in F.items():
    for s in ss:
        if s['kind'] != 'new' or not s.get('fout'): continue
        n = N.get((s['v'], s['lon'], s['lat']), {})
        m = (n.get('main') or [{}])[0]
        # the whole settlement as one solid shape: its outline with the gaps between houses closed (~300 m) and holes filled,
        # plus a ~60 m margin round its outer part so rounding to 0.001 deg cannot cut it again
        whole = shape(s['fp']).union(shape(s['fout']).buffer(0.0006)).buffer(0.003).buffer(-0.0025)
        whole = unary_union([Polygon(q.exterior) for q in getattr(whole, 'geoms', [whole])])
        g = whole.simplify(0.0002)
        feats.append({'type': 'Feature', 'geometry': mapping(g), 'properties': {
            'v': s['v'], 'lon': s['lon'], 'lat': s['lat'], 'people_in': round(s['in']), 'people_out': round(s['out']),
            'country': sorted(set(s['cin']) | set(s['cout'])), 'name': m.get('en') or m.get('name'), 'name_local': m.get('name'),
            'places': [(p['en'] or p['name'], p['sub'], p['side']) for p in n.get('places', [])][:40]}})
out = os.path.join(os.path.dirname(__file__), 'data', sys.argv[4] if len(sys.argv) > 4 else 'split_settlements.geojson')
json.dump({'type': 'FeatureCollection', 'features': feats}, open(out, 'w'), ensure_ascii=False)
for v in ['x', 'xn']:
    f = [q for q in feats if q['properties']['v'] == v]
    print(v, len(f), 'settlements; people outside to bring in', sum(q['properties']['people_out'] for q in f))
