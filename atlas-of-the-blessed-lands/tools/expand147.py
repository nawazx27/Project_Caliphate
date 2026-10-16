"""Version 147 (2026-10-16). Three requests from Nawaz, for V2 and V2-B:
 (1) "I want the orange border to look exactly like this!" (a close-up of the same Caucasus sketch, reference/
     v147_caucasus_exact_request.png): the sketch refitted by matching ALL its drawn borders and coasts to the real ones (affine,
     chamfer fit; tools/data/caucasus_line147.json, mean 5 px off); its orange top edge lies north of Version 146's stretched line,
     so Russia south of it (Kerch Strait to the Caspian, land only, Crimea out) is added: tools/data/caucasus_expand147.geojson.
 (2) Google Maps screenshot of the Comoros and Mayotte, "add the ones in the image": the Comoros (174) whole and Mayotte (the French
     island, FRA within 44.9-45.4 E, 13.1-12.5 S): tools/data/comoros_mayotte147.geojson.
 (3) "And with that extend", then "Update" with a redrawn line: from west of Lake Tanganyika (3.9 S) south past the lake and
     south-east through Zambia, Malawi and Mozambique to the sea just north-east of the Zambezi mouth (reference/
     v147_africa_line_update.jpg, which replaces v147_africa_line_request.jpg; fitted on the gold V2 edge;
     tools/data/africa_line147.json); all land and lake east of it to the coast: tools/data/africa_expand147.geojson.
Run: python3 tools/expand147.py. Nawaz's maps; my tracing."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, MultiPolygon, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
F = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
N = {str(f['id']): f['properties'].get('n') for f in geo['features']}
land = unary_union(list(F.values()))
lakes = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']])
X = MultiPolygon([Polygon(p[0], p[1:]) for p in json.load(open(os.path.join(P, 'src/caliph.json')))['x']['polys']]).buffer(0)
line = lambda n: json.load(open(os.path.join(D, n)))['features'][0]['geometry']['coordinates']
def save(name, g):
    json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 147'}, 'geometry': mapping(g)}]}, open(os.path.join(D, name), 'w'))
def report(name, g):
    new = g.difference(X); print(name, 'new to V2', round(A(new)), 'km2')
    for c, s in F.items():
        if s.intersects(new):
            a = A(s.intersection(new))
            if a > 1: print('   ', c, N[c], round(a), 'km2 of', round(A(s)))
L = line('caucasus_line147.json')
R = Polygon([(36.3, L[0][1])] + L + [(48.6, L[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
cau = R.intersection(F['643']).difference(box(32.0, 44.0, 36.55, 46.5))
save('caucasus_expand147.geojson', cau); report('Caucasus', cau)
cm = unary_union([F['174'], F['FRA'].intersection(box(44.9, -13.1, 45.4, -12.5))])
save('comoros_mayotte147.geojson', cm); report('Comoros and Mayotte', cm)
L = line('africa_line147.json')
R = Polygon(L + [(42.0, L[-1][1]), (42.0, L[0][1])]).buffer(0)   # closed east through the sea and land V2 holds
af = R.intersection(unary_union([land, lakes]))
save('africa_expand147.geojson', af); report('Africa', af)
