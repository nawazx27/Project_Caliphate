"""Version 134 (2026-10-14, Nawaz: "Take everything of what's outside, inside", of Greater Khurāsān as his three maps draw it). After
Version 132 about 16 km² of the maps' land lay outside V2 in hair-thin slivers along their edges, thinner than the outline's 0.001°
(about 100 m) precision. Each sliver is widened by 0.0015° (inside the land only) so it survives that rounding, and a second run widened
the rest by 0.003°; this takes in at most about 300 m beyond the maps' edges. About 4 km² stays out along the south-east Caspian shore,
where the base map's coastline and V2's shoreline (Version 109) differ by a few hundred metres. Sea water stays out (Version 109). Writes tools/data/khorasan_slivers.geojson.
Run: python3 tools/khorasan_slivers.py, then node tools/v2_khorasan_slivers.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data')
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
def polys(rings): return unary_union([Polygon(r).buffer(0) if isinstance(r[0][0], (int, float)) else Polygon(r[0], r[1:]).buffer(0) for r in rings])
U = unary_union([polys(json.load(open(os.path.join(D, 'greater_khorasan_wiki_trace.json')))), polys(json.load(open(os.path.join(D, 'khorasan_express_trace.json')))),
                 Polygon(json.load(open(os.path.join(D, 'transoxiana_trace.json')))['khorasan']).buffer(0)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) != '356' and shape(f['geometry']).intersects(U)])
C = json.load(open(os.path.join(P, 'src', 'caliph.json')))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
miss = U.intersection(land).difference(X)
S = miss.buffer(0.003).intersection(land)
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon'])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KHORASAN-SLIVERS', 'missing_km2': round(A(miss), 1), 'km2': round(A(S), 1)}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'khorasan_slivers.geojson'), 'w'))
print('missing', round(A(miss), 1), 'km2; widened', round(A(S), 1), 'km2')
