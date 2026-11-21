"""Version 495 (Nawaz, a red loop round the Derbent lobe's coast south of its tip, where thin land slivers lay between V2 and the Caspian:
"Push the entire area to the coast", then on the tip's north-east shore "Push it to the coast"). Every piece of land between V2 (CALIPH.arb) and the sea on the Dagestan-Azerbaijan coast round Derbent
(47.8-48.8 E, 41.6-42.4 N) that touches both V2 and the sea and is under 100 km2 is added, so V2 runs to the shore. DIR env = project dir."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = box(47.8, 41.6, 48.8, 42.4)
LAND = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(B.buffer(0.5))])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); SEA = B.difference(LAND)
g = LAND.intersection(B).difference(V)
add = [q for q in getattr(g, 'geoms', [g]) if 0 < A(q) < 100 and q.buffer(0.003).intersects(SEA) and q.buffer(0.003).intersects(V)]
# and where a sliver of coast runs on past the lobe's tip into the land beyond (so it is not a separate piece), the strip between V2 and the sea that is
# narrower than ~4 km is taken too (Nawaz, a loop round the tip's north-east shore: "Push it to the coast")
strip = LAND.intersection(B).intersection(V.buffer(0.04)).intersection(SEA.buffer(0.04)).difference(V)
add += [q for q in getattr(strip, 'geoms', [strip]) if A(q) > 0.01]
print('coastal slivers added', len(add), round(sum(A(q) for q in add), 1), 'km2')
X = unary_union([V] + [q.buffer(0.003).intersection(LAND.buffer(0.003)) for q in add]).buffer(0)
X = unary_union([X, X.intersection(B.buffer(0.2)).buffer(0.05, quad_segs=16).buffer(-0.05, quad_segs=16).intersection(B).intersection(LAND)]).buffer(0)   # the little hook at the tip rounded off
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o); print('lost', round(A(V.difference(Y.buffer(0.002))), 2), 'km2')
C['arb']['polys'] = o
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
