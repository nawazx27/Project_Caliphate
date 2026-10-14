"""Version 136 (2026-10-14, Nawaz: "Add it in v2b as well" and "Don't leave anything out… widest and max!!!"). On top of Version 135's
widest classical Khurāsān, the three things Version 135 had left out come in too: Jand and Yanghikant, the Oghuz towns of the lower Syr
Darya that Le Strange lists with Isbījāb's district (taken as the whole Qyzylorda region, Overture Maps KZ-43), and the green locator map's
Transoxiana (south-east Kazakhstan round Lake Balkhash, Semirechye, and northern Kyrgyzstan), with every other region map he traced
(Version 131's set) and Isbījāb's district (Version 135). Land only (geo2, India out: Version 133), sea water out (Version 109).
Writes tools/data/khorasan_max.geojson. Run: python3 tools/khorasan_max.py <kz_south_div.parquet>, then node tools/v2_khorasan_max_all.js"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data')
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
def polys(rings): return unary_union([Polygon(r).buffer(0) if isinstance(r[0][0], (int, float)) else Polygon(r[0], r[1:]).buffer(0) for r in rings])
d = json.load(open(os.path.join(D, 'transoxiana_trace.json')))
R = [polys(json.load(open(os.path.join(D, 'greater_khorasan_wiki_trace.json')))), polys(json.load(open(os.path.join(D, 'khorasan_express_trace.json'))))]
R += [Polygon(d[k]).buffer(0) for k in ('transoxiana', 'khwarazm', 'khorasan')]
R.append(Polygon(json.load(open(os.path.join(D, 'mawarannahr_trace2.json')))['mawarannahr_img2']).buffer(0))
R.append(Polygon(json.load(open(os.path.join(D, 'transoxiana_locator_trace.json')))['transoxiana_locator']).buffer(0))
R.append(shape(json.load(open(os.path.join(D, 'isbijab_district.geojson')))['features'][0]['geometry']).buffer(0))
R += [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[1]).to_pylist() if r['subtype'] == 'region' and r['region'] == 'KZ-43']
U = unary_union(R)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) != '356' and shape(f['geometry']).intersects(U)])
S = U.intersection(land)
C = json.load(open(os.path.join(P, 'src', 'caliph.json')))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
print('max region land', round(A(S)), 'km2; new to V2', round(A(S.difference(X))))
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) > 0])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KHORASAN-MAX', 'km2': round(A(S))}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'khorasan_max.geojson'), 'w'))
