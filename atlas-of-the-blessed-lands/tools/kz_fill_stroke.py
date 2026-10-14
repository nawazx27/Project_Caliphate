"""Version 128 (2026-10-14). On a screenshot of V2 Nawaz drew a line over the notch left north of Beyneu and west of the Aral district by
Version 127 (Shalkar, Baiganin and Zhylyoi districts out) and wrote "Fill this region". Placed on the map from the screenshot's graticule
(45 N at y 950, 50 N at y 345, 55 E at x 163, 60 E at x 575): about 54.24 E 46.24 N - 56.06 E 46.57 N - 58.12 E 47.36 N - 60.0 E 47.64 N
- 61.76 E 47.77 N (the Aral district's northern tip). Shalkar district is 56% south of it, so (Version 125's rule) it comes in whole; the
rest of the region under his line (parts of Baiganin and Zhylyoi districts) comes in exactly up to his line, since he asked for all of it.
Writes tools/data/kz_fill_stroke.geojson. Run: python3 tools/kz_fill_stroke.py <kz_div_areas.parquet>"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, Polygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
LINE = [(54.24, 46.24), (56.06, 46.57), (58.12, 47.36), (60.0, 47.64), (61.76, 47.77), (62.06, 47.56)]
south = Polygon(LINE + [(LINE[-1][0], 44), (LINE[0][0], 44)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
KZ = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '398'][0]
shalkar = [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[1]).to_pylist() if r['subtype'] == 'county' and (r['names'] or {}).get('primary') == 'Шалқар ауданы']
assert len(shalkar) == 1
S = KZ.intersection(unary_union([south, shalkar[0]]))
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KZ-FILL', 'km2': round(A(S)), 'line': LINE}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'kz_fill_stroke.geojson'), 'w'))
print('area', round(A(S)), 'km2')
