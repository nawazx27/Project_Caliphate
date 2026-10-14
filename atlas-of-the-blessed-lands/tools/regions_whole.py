"""Version 131 (2026-10-14, Nawaz: "Is the entire greater khorasan, khawarzm and transoxiana included in v2" — then, told what was
missing, "Add all the land that's missing… no exceptions"). Every land part of every region map he traced earlier that lay outside V2
is added to V2 and V2-B: Greater Khurāsān (Wikipedia map and his Khorasan map), the dashed-outline map's Khurāsān, Khwārazm and
Transoxiana, the red-line map's Mā warāʾ al-Nahr (the mountains east of Farghāna, Kyrgyzstan and China) and the green locator map's
Transoxiana (south-east Kazakhstan round Lake Balkhash and northern Kyrgyzstan). Land only (geo2 countries); sea water stays out.
Writes tools/data/regions_whole_missing.geojson. Run: python3 tools/regions_whole.py, then node tools/v2_regions_whole.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data')
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
def polys(rings): return unary_union([Polygon(r).buffer(0) if isinstance(r[0][0], (int, float)) else Polygon(r[0], r[1:]).buffer(0) for r in rings])
R = [polys(json.load(open(os.path.join(D, 'greater_khorasan_wiki_trace.json')))), polys(json.load(open(os.path.join(D, 'khorasan_express_trace.json'))))]
d = json.load(open(os.path.join(D, 'transoxiana_trace.json'))); R += [Polygon(d[k]).buffer(0) for k in ('transoxiana', 'khwarazm', 'khorasan')]
R.append(Polygon(json.load(open(os.path.join(D, 'mawarannahr_trace2.json')))['mawarannahr_img2']).buffer(0))
R.append(Polygon(json.load(open(os.path.join(D, 'transoxiana_locator_trace.json')))['transoxiana_locator']).buffer(0))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
U = unary_union(R); land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if shape(f['geometry']).intersects(U)])
C = json.load(open(os.path.join(P, 'src', 'caliph.json')))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
S = U.intersection(land).difference(X)
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == "Polygon" and A(q) > 0])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'REGIONS-MISSING', 'km2': round(A(S))}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'regions_whole_missing.geojson'), 'w'))
print('missing land', round(A(S)), 'km2')
