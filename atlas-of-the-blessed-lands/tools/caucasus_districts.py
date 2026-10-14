"""Version 125 (2026-10-14, Nawaz: "The straight line doesn't look good. Rather, it should have the shape of the borders of Georgia and
Armenia"; asked how, he chose "Real district borders"). Version 124's straight line from Anapa (37.237 E, 44.99 N) to the Kizlyar Bay
(46.68 E, 44.50 N) is replaced by the borders of the districts it crosses: each district (Overture Maps 2026-09-23.1, division_area
subtype county; tools/data/ru_districts_on_line.geojson) with half or more of its area south of the line comes in whole, each with less
stays out; all of Russia (geo2) south of the line outside those districts comes in. My method; the line is Nawaz's.
Writes tools/data/caucasus_districts.geojson. Run: python3 tools/caucasus_districts.py, then node tools/v2_caucasus_districts.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, Polygon, box, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
INLET, TIP = (46.68, 44.50), (37.237, 44.99)
south = Polygon([TIP, INLET, (50, INLET[1]), (50, 40), (TIP[0], 40), TIP])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(35, 40, 50, 48))
take, drop, rows = [], [], []
for f in json.load(open(os.path.join(H, 'data', 'ru_districts_on_line.geojson')))['features']:
    g = shape(f['geometry']).buffer(0); s = A(g.intersection(south)) / A(g)
    (take if s >= 0.5 else drop).append(g); rows.append((f['properties']['name'], round(s, 2), s >= 0.5))
S = RU.intersection(unary_union([south] + take)).difference(unary_union(drop))
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 1])
# V2's Russian land before Version 124 (the Black Sea strip and V5's Dagestan block, with their whole towns): Version 123, git 3bd55ea
from shapely.geometry import MultiPolygon
old = json.loads(subprocess.check_output(['git', 'show', '3bd55ea:atlas-of-the-blessed-lands/src/caliph.json'], cwd=P))
base = MultiPolygon([Polygon(p[0], p[1:]) for p in old['x']['polys']]).buffer(0).intersection(RU)
base = unary_union([q for q in getattr(base, 'geoms', [base]) if q.geom_type == 'Polygon'])
S = unary_union([S, base])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'RU-NCD', 'km2': round(A(S)), 'districts': rows}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'caucasus_districts.geojson'), 'w'), ensure_ascii=False)
print('area', round(A(S)), 'km2;', sum(r[2] for r in rows), 'districts in whole,', sum(not r[2] for r in rows), 'out')
