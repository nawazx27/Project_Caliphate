"""Version 124 (2026-10-14, Nawaz, with two phone screenshots of V2-B, one circling the inlet of the Caspian coast just north of V5's
Dagestan block, the other the tip of Russia's Black Sea strip at Anapa: "Draw a line from that crevice in the image one to the tip in the
image two and fill everything bottom and in between"). The inlet is the Kizlyar Bay, the deepest bend of the coast there (46.68 E,
44.50 N, geo2's coastline); the tip is the strip's westernmost point (37.237 E, 44.99 N). All of Russia (geo2) south of the straight line
between them is taken (the Caspian side down to the Dagestan block too). Nawaz's specification; not from the sources.
Writes tools/data/caucasus_line.geojson (one feature, what V2 lacks). Run: python3 tools/caucasus_line.py [caliph.json before the change], then node tools/v2_caucasus_line.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, MultiPolygon, Polygon, box, mapping
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: round(abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6)
INLET, TIP = (46.68, 44.50), (37.237, 44.99)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(35, 40, 50, 48))
south = Polygon([TIP, INLET, (50, INLET[1]), (50, 40), (TIP[0], 40), TIP])   # from the Anapa tip eastward only (a first run went west to 35 E and took a strip of Crimea) 
import sys
C = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(P, 'src/caliph.json')))   # the map before the change (Version 123's src/caliph.json, git 3bd55ea)
x = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
add = RU.intersection(south).difference(x)
add = MultiPolygon([g for g in getattr(add, 'geoms', [add]) if g.geom_type == 'Polygon' and A(g) >= 1])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'RU-NC', 'km2': A(add)}, 'geometry': mapping(add)}]}, open(os.path.join(H, 'data', 'caucasus_line.geojson'), 'w'))
print('added', A(add), 'km2 in', len(add.geoms), 'pieces; Russia south of the line in all', A(RU.intersection(south)), 'km2')
