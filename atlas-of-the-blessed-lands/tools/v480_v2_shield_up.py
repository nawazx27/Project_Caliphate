"""Version 480 (Nawaz: "Push it a bit more upward", of the widened left side of V2's shield). The part of V2's (CALIPH.arb) African piece west of the
straight 24 E Sudan-Chad line (the widened bulge in Chad, the CAR and DR Congo) is moved up (north) by DY (default 1.0 deg, ~110 km) as one piece, its
rough edge kept, and joined to V2, so its top corner in eastern Chad rises from ~15.7 N toward ~16.7 N along the straight line, which stays as it is.
Cut to land; enclosed pockets filled; V1 unchanged. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, shapely.affinity
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for n, g in G.items() if n != 'Libya' and g.intersects(shapely.box(10, -8, 30, 22))]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); V1 = MP(C['shj']['polys'])
DY = float(os.environ.get('DY', '1.0'))
W = V.intersection(shapely.box(10, -6, 23.99, 15.9)).intersection(LAND)
WU = shapely.affinity.translate(W, 0, DY).intersection(shapely.box(10, -6, 23.99, 19.4)).intersection(LAND)
X = unary_union([V, WU]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]).buffer(0)
X = unary_union([X, X.intersection(shapely.box(10, 10, 24.5, 20)).buffer(0.08).buffer(-0.08).intersection(LAND)]).buffer(0)   # no hairline notch where the moved piece meets the straight line
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 50})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('arb', C['arb']['km2'], '->', km, '| Biltine', Y.contains(Point(20.92, 14.53)), '| Arada', Y.contains(Point(20.66, 15.02)), '| Fada (out?)', Y.contains(Point(21.58, 17.19)), '| V1 outside', round(A(V1.difference(Y.buffer(0.002))), 1))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
