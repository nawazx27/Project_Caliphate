"""Version 466 (Nawaz, two red strokes on the Version 465 full-map preview just outside V1's south-western and southern edge, from Darfur round
South Sudan's southern border to Lake Turkana and on along northern Kenya; no words). Read as before: fill V1 out to the line. The stroke pixels were
placed by fitting V1's drawn outline in that picture (median error ~1 pixel, ~10 km at that scale; tools/data/v466_stroke_points.npy, lon/lat).
The land between V1's edge and the outer stroke goes into V1 (shj): V1 plus a band round the stroke, closed by ~35 km and kept within ~45 km of the
stroke, its outer side cut on the stroke. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, MultiPoint
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(18, 0, 46, 20))]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
R = np.load(os.path.join(HERE, 'tools/data/v466_stroke_points.npy'))
RB = MultiPoint([tuple(p) for p in R[::2]]).buffer(0.15).buffer(0)          # the drawn strokes as an area
X = unary_union([V, RB]).buffer(0)
Xc = X.buffer(0.5).buffer(-0.5)
Xc = unary_union([Xc] + [Polygon(h) for q in getattr(Xc, 'geoms', [Xc]) for h in q.interiors])                                           # close the gap between the edge and the stroke
add = Xc.difference(V).intersection(RB.buffer(0.4)).intersection(LAND)
add = unary_union([g for g in getattr(add, 'geoms', [add]) if A(g) > 20])
print('filled', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Chad', 'Central African Rep.', 'DR Congo', 'Uganda', 'Kenya', 'Ethiopia', 'South Sudan', 'Sudan'] if k in G})
Y0 = unary_union([V, add.buffer(0.003).intersection(LAND.buffer(0.003))]).buffer(0)
Y0 = Y0.buffer(0.03).buffer(-0.03)   # soften the band's dotted edge
Y0 = unary_union([Y0] + [Polygon(h) for q in getattr(Y0, 'geoms', [Y0]) for h in q.interiors if A(Polygon(h)) < 400000]).buffer(0)
X = shapely.set_precision(Y0, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Juba': (31.58, 4.85), 'Yei': (30.68, 4.09), 'Moyale': (39.05, 3.52), 'Lokichogio (Kenya)': (34.35, 4.2), 'Birao (CAR)': (22.78, 10.28), 'Abeche (Chad)': (20.83, 13.83)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
