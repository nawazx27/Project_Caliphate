"""Version 127 (2026-10-14). On a screenshot of V2-B, Nawaz drew a line from the north-east corner of the Caspian to the outline's corner
in Kazakhstan north of the Syr Darya, and wrote "Connect this". Placed on the map from the outline's corners (Uzbekistan's north-west
corner 56.0 E 45.0 N, its corner on the Aral 58.55 E 45.56 N, the outline's corner at 66.7 E 45.7 N); his line, about:
52.5 E 46.05 N - 57.3 E 46.9 N - 61.8 E 47.5 N - 65.7 E 46.5 N - 66.7 E 45.7 N. As in Version 125 (his choice of real district
borders), each Kazakh district (Overture Maps 2026-09-23.1, division_area subtype county) with half or more of its area south of the
line comes in whole, each with less stays out; geo2's coast slivers next to the districts taken come too. My method; the line is his.
Writes tools/data/kz_west_districts.geojson. Run: python3 tools/kz_west_districts.py <kz_div_areas.parquet>"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, box, Polygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
LINE = [(52.5, 46.05), (55.0, 46.45), (57.3, 46.94), (59.6, 47.4), (61.8, 47.5), (64.1, 47.1), (65.7, 46.5), (66.7, 45.7)]
south = Polygon([(48, LINE[0][1])] + LINE + [(66.7, 40), (48, 40)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
KZ = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '398'][0]
take, drop, rows = [], [], []
for r in pq.read_table(sys.argv[1]).to_pylist():
    if r['subtype'] != 'county': continue
    g = shapely.from_wkb(r['geometry']).buffer(0)
    if not g.intersects(box(48, 40, 72, 50)): continue
    s = A(g.intersection(south)) / A(g)
    if s == 0: drop.append(g); continue
    (take if s >= 0.5 else drop).append(g); rows.append(((r['names'] or {}).get('primary'), round(s, 2), s >= 0.5))
S = KZ.intersection(unary_union(take).buffer(0.02)).difference(unary_union(drop))
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KZ-WEST', 'km2': round(A(S)), 'districts': rows, 'line': LINE}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'kz_west_districts.geojson'), 'w'), ensure_ascii=False)
for r in rows: print(r)
print('area', round(A(S)), 'km2')
