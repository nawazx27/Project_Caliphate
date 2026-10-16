"""Version 146 (2026-10-16, Nawaz, with a map of the Caucasus shaded orange from the Taman peninsula to the Caspian: "Expand").
The top edge of the orange (tools/data/caucasus_line146.json, traced from reference/v146_caucasus_request.jpg; the map is a drawn
sketch, so it was fitted on the Taman tip, Sarpi, the Absheron tip and Astara, and its east end stretched to the real Caspian shore,
which it touches) is the new line: all of Russia south of it is added (land only: no Black Sea or Caspian water, Crimea kept out as
before). Georgia, Armenia and Azerbaijan are already whole. Writes tools/data/caucasus_expand146.geojson. Run: python3
tools/caucasus_line146.py. Nawaz's map; my tracing."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, MultiPolygon, mapping, box
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
L = json.load(open(os.path.join(P, 'tools/data/caucasus_line146.json')))['features'][0]['geometry']['coordinates']
R = Polygon([(36.3, L[0][1])] + L + [(48.5, L[-1][1]), (48.5, 41.0), (36.3, 41.0)]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
crimea = RU.intersection(box(32.0, 44.0, 36.7, 46.3)).difference(box(36.55, 44.0, 36.7, 46.3) if False else box(0, 0, 0, 0))
print('Crimea in base-map Russia', round(A(RU.intersection(box(32.0, 44.0, 36.55, 46.3)))), 'km2')
add = R.intersection(RU).difference(box(32.0, 44.0, 36.55, 46.3))   # Crimea out (Kerch peninsula ends at ~36.6 E, Taman starts east of the strait)
X = MultiPolygon([Polygon(p[0], p[1:]) for p in json.load(open(os.path.join(P, 'src/caliph.json')))['x']['polys']]).buffer(0)
print('Russia south of the line', round(A(add)), 'km2; new to V2', round(A(add.difference(X))), 'km2')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 146 Caucasus'}, 'geometry': mapping(add)}]},
          open(os.path.join(P, 'tools/data/caucasus_expand146.geojson'), 'w'))
