"""Version 114 (2026-10-13, Nawaz: "Push this land (in the red) from top to bottom to the sea... attach it to the sea").
Dagestan's Caspian coast between the Greater Caucasus band (tools/greater_caucasus.py) and the sea, from just north of
Makhachkala (43.12 N, the band's north-eastern corner) down to the Azerbaijan border: Russia (geo2) in that box, minus what
V2 already holds; only the piece that runs along the coast is kept. Nawaz's specification; not from the sources.
Writes tools/data/dagestan_coast.geojson. Run after node tools/v2_greater_caucasus.js: python3 tools/dagestan_coast.py"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, MultiPolygon, Polygon, box, mapping
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
TOP = 43.12
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(45, 40.5, 50, 44.5))
C = json.load(open(os.path.join(P, 'src/caliph.json')))
V2 = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0).intersection(box(45, 40.5, 50, 44.5))
d = RU.intersection(box(46.6, 41.0, 49.5, TOP)).difference(V2)
main = max([g for g in getattr(d, 'geoms', [d]) if g.geom_type == 'Polygon'], key=lambda g: g.area).simplify(0.001)
km2 = round(abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(main)[0]) / 1e6)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'RU-DC', 'kind': 'coast',
    'n': "Dagestan's Caspian coast from Makhachkala to the Azerbaijan border (with Kaspiysk, Izberbash and Derbent)", 'km2': km2},
    'geometry': mapping(main)}]}, open(os.path.join(H, 'data', 'dagestan_coast.geojson'), 'w'))
print('coast strip', km2, 'km2', [round(v, 3) for v in main.bounds])
