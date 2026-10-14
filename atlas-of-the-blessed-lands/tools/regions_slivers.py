"""Version 137 (2026-10-14, Nawaz: "Fill everything", of the last slivers of his Khurāsān, Khwārazm, Transoxiana and Mā warāʾ al-Nahr maps
outside V2 after Version 136, about 36 km²). Like Version 134: every sliver of tools/data/khorasan_max.geojson's land outside the version
is widened by 0.003° within the land (about 300 m) so it survives the outline's 0.001° rounding. Run per version:
python3 tools/regions_slivers.py x|xb  (writes tools/data/regions_slivers_<v>.geojson), then node tools/v2_regions_slivers.js x|xb"""
import json, os, sys, subprocess, pyproj
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data'); K = sys.argv[1]
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
M = shape(json.load(open(os.path.join(D, 'khorasan_max.geojson')))['features'][0]['geometry']).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) != '356' and shape(f['geometry']).intersects(M)])
C = json.load(open(os.path.join(P, 'src', 'caliph.json')))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[K]['polys']]).buffer(0)
miss = M.difference(X)
S = miss.buffer(0.003).intersection(land)
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon'])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'v': K, 'missing_km2': round(A(miss), 1)}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'regions_slivers_' + K + '.geojson'), 'w'))
print(K, 'missing', round(A(miss), 1), 'km2; widened', round(A(S), 1))
