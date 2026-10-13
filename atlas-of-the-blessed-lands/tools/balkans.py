"""Version 107 (2026-10-13, Nawaz, with the Wikipedia article "Balkans" and its interactive map: "I want the entire Balkan Peninsula in v2…
look at the red outline").

The red outline of that map is OpenStreetMap relation 4016746 ("Balkans", natural=peninsula), read here from Overture Maps
(release 2026-09-23.1; tools/data/balkans_osm.geojson): about 475,900 km², from the Gulf of Trieste along the Sava (through Zagreb
and Belgrade) and the Danube to the Black Sea, with Dobruja, East Thrace and mainland Greece. Wikipedia: "Its northern boundary
... is often given as the Danube, Sava and Kupa Rivers" (the author's specification; not a ruling).

Writes tools/data/balkans_v2.geojson: the pieces to add to V2 / V2N, per country of the base map (geo2.json):
  - countries inside the outline: whole (Bulgaria, Bosnia and Herzegovina, Montenegro, Albania, Kosovo, North Macedonia);
  - countries the outline crosses: the part inside it (Croatia, Serbia, Slovenia, Romania: Dobruja, Italy: Trieste), and for
    Croatia also every Adriatic island (an island is never left out);
Greece and Türkiye are in V2 already. Run: python3 tools/balkans.py"""
import json, os
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
B = shape(json.load(open(os.path.join(H, 'data', 'balkans_osm.geojson')))['geometry']).buffer(0)
import subprocess
geo = json.loads(subprocess.check_output(['node', '-e', """
const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));
process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)));"""], cwd=R))
C = {str(f['id']): (f['properties'].get('n'), shape(f['geometry']).buffer(0)) for f in geo['features']}
WHOLE = ['100', '070', '499', '008', 'KOS', '807']
PART = ['191', '688', '705', '642', '380']
feats = []
for i in WHOLE:
    n, g = C[i]; feats.append({'type': 'Feature', 'properties': {'id': i, 'n': n, 'whole': True}, 'geometry': mapping(g)})
for i in PART:
    n, g = C[i]
    inside = g.intersection(B)
    if i == '191':   # Croatia: also every island that the outline leaves out
        rest = g.difference(B)
        isl = [p for p in getattr(rest, 'geoms', [rest]) if p.area > 0 and not p.buffer(0.002).intersects(B.boundary) and p.centroid.y < 45.4]
        inside = unary_union([inside] + isl)
    inside = unary_union([p for p in getattr(inside, 'geoms', [inside]) if p.area > 1e-7])
    feats.append({'type': 'Feature', 'properties': {'id': i, 'n': n, 'whole': False}, 'geometry': mapping(inside)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', 'balkans_v2.geojson'), 'w'))
for f in feats: print(f['properties']['n'], 'whole' if f['properties']['whole'] else 'part', round(shape(f['geometry']).area, 3))
