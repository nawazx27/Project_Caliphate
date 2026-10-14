"""Version 129 (2026-10-14). On a picture of V2 (the close-up sent with Version 128) Nawaz drew a red line from the Caspian coast at
Atyrau to Shalkar district's north-west corner (no words: the same request as before, fill south of it). Placed from the picture's own
projection (56.0 E 45.0 N, Uzbekistan's north-west corner, at x 512 y 480; 38.7 px per degree; checked on Baku and Shalkar's northern
tip): about 51.76 E 47.15 N - 52.59 E 47.36 N - 54.4 E 47.71 N - 56.47 E 47.81 N - 58.27 E 48.07 N - 58.84 E 48.09 N.
As in Version 128: each Kazakh district with half or more of its land south of the line comes in whole (Atyrau city 74%, Zhylyoi 98%,
Makat 70%, Baiganin 72%); the rest of the land under the line (slivers of Kyzylkoga and Mugalzhar districts) comes in up to the line.
Writes tools/data/kz_fill_line2.geojson. Run: python3 tools/kz_fill_line2.py <kz_div_areas.parquet>"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, Polygon, box, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
LINE = [(51.76, 47.15), (52.59, 47.36), (54.4, 47.71), (56.47, 47.81), (58.27, 48.07), (58.84, 48.09)]
south = Polygon(LINE + [(LINE[-1][0], 44), (LINE[0][0], 44)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
KZ = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '398'][0]
take, rows = [], []
for r in pq.read_table(sys.argv[1]).to_pylist():
    if r['subtype'] != 'county': continue
    g = shapely.from_wkb(r['geometry']).buffer(0)
    if not g.intersects(south): continue
    s = A(g.intersection(south)) / A(g)
    if s >= 0.5: take.append(g)
    rows.append(((r['names'] or {}).get('primary'), round(s, 2), s >= 0.5))
S = KZ.intersection(unary_union([south] + take))
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KZ-FILL2', 'km2': round(A(S)), 'line': LINE, 'districts': rows}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'kz_fill_line2.geojson'), 'w'), ensure_ascii=False)
for r in rows: print(r)
print('area', round(A(S)), 'km2')
