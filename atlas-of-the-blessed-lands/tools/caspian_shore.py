"""Version 109 (2026-10-13, Nawaz, with a screenshot of the Caucasus and the Caspian: "Make this place follow its natural border";
he chose: both the Caucasus and the Caspian shore, in V2, V2-B and V2N).
Caspian part: the outline is to follow the natural shore, so the Caspian water inside V2 / V2-B / V2N (the strip along the Turkmen
coast and Gorgan Bay that the Khorasan map of Version 82 drew over the sea, the Anzali lagoon, and thin slivers along the coast) is
taken out. The water is everything in the Caspian basin that is not land in the base map (geo2.json).
Writes tools/data/caspian_water_in_v2.geojson for tools/v2_natural_caucasus_caspian.js. Run: python3 tools/caspian_shore.py"""
import json, os, subprocess
from shapely.geometry import shape, box, Point, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=R))
B = box(45, 35.5, 56, 48)
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if shape(f['geometry']).intersects(B)])
sea = B.difference(land)
casp = [p for p in getattr(sea, 'geoms', [sea]) if p.contains(Point(50.5, 42))][0]
C = json.load(open(os.path.join(R, 'src', 'caliph.json')))
feats = []
for k in ['x', 'xb', 'xn']:
    mp = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    w = mp.intersection(casp)
    for p in getattr(w, 'geoms', [w]):
        if p.geom_type == 'Polygon' and p.area > 0: feats.append({'type': 'Feature', 'properties': {'v': k}, 'geometry': mapping(p)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', 'caspian_water_in_v2.geojson'), 'w'))
print({k: sum(1 for f in feats if f['properties']['v'] == k) for k in ['x', 'xb', 'xn']}, 'pieces')
