"""Version 146 (2026-10-16, Nawaz, on a phone screenshot of V2 in East Africa with a black line drawn west of the lakes: "Expand").
His line (traced from reference/v146_africa_request.jpg, georeferenced by fitting the screenshot's lakes to lakes.geojson and checked
against the gold V2 edge, 85% of its pixels on it; tools/data/africa_line146.json) runs from north of Lake Albert through eastern DR
Congo, west of Lakes Albert, Edward, Kivu and Tanganyika, across north-eastern Zambia to the north end of Lake Malawi. Everything
between it and V2 is added (closed to the east through land V2 already holds). Writes tools/data/africa_expand146.geojson and prints
the area by country. Run: python3 tools/africa_line146.py. Nawaz's line; my tracing."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
L = json.load(open(os.path.join(P, 'tools/data/africa_line146.json')))['features'][0]['geometry']['coordinates']
s, e = L[0], L[-1]
ring = L + [(34.3, -9.3), (37.0, -9.3), (37.0, 4.6), (s[0], 4.6), s]
R = Polygon(ring).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
lakes = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']])
from shapely.geometry import MultiPolygon
X = MultiPolygon([Polygon(p[0], p[1:]) for p in json.load(open(os.path.join(P, 'src/caliph.json')))['x']['polys']]).buffer(0)
new = R.difference(X)
for f in geo['features']:
    g = shape(f['geometry']).buffer(0)
    if g.intersects(new):
        i = g.intersection(new)
        if A(i) > 1: print(' ', f['id'], f['properties'].get('name'), round(A(i)), 'km2 of', round(A(g)))
print('new area', round(A(new)), 'km2; of it lake water', round(A(new.intersection(lakes))))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 146 Africa'}, 'geometry': mapping(R)}]},
          open(os.path.join(P, 'tools/data/africa_expand146.geojson'), 'w'))
