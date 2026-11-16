"""Version 470 (Nawaz, IMG_5409: a red stroke on the phone page across the mouth of the V-shaped notch in V1's southern edge in northern Uganda,
between the north end of Lake Albert and the Albert Nile's bend; "Fill and push directly"). The picture was placed by fitting V1's own drawn outline in it
(Mercator scale and offset, mean error ~4 px, ~2 km); stroke points in tools/data/v470_stroke_points.npy (lon/lat). The land shut in between V1's edge
and the stroke goes into V1 (shj). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
R = np.load(os.path.join(HERE, 'tools/data/v470_stroke_points.npy'))
RB = MultiPoint([tuple(p) for p in R]).buffer(0.03).buffer(0)          # the drawn stroke as a thin area
X = unary_union([V, RB]).buffer(0.15).buffer(-0.15)                     # joins the stroke's ends to V1's edge
holes = unary_union([Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors])
oldh = unary_union([Polygon(h) for q in getattr(V, 'geoms', [V]) for h in q.interiors])
add = unary_union([holes.difference(oldh), RB.buffer(0.001)]).difference(V).intersection(LAND)
add = unary_union([g for g in getattr(add, 'geoms', [add]) if A(g) > 20])
print('filled', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Uganda', 'DR Congo', 'South Sudan'] if k in G})
Y0 = unary_union([V, add.buffer(0.003).intersection(LAND.buffer(0.003))]).buffer(0)
Y0 = Y0.buffer(0.03).buffer(-0.03)   # soften the band's dotted edge
Y0 = unary_union([Y0] + [Polygon(h) for q in getattr(Y0, 'geoms', [Y0]) for h in q.interiors if A(Polygon(h)) < 1000]).buffer(0)
X = shapely.set_precision(Y0, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Arua': (30.91, 3.02), 'Gulu': (32.3, 2.78), 'Pakwach': (31.5, 2.46), 'Nebbi': (31.09, 2.48), 'Lira': (32.9, 2.25)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
