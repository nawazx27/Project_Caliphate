"""Version 458 (Nawaz, red stroke across the small notch in V1's edge at Nimule on the South Sudan-Uganda border, where the Albert Nile enters:
"Fill and push"). The land in that notch (V1 closed by ~9 km inside a small box round it) is added to V1 (shj). Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = box(31.3, 3.3, 32.5, 3.95)
LAND = unary_union([shape(f['geometry']).buffer(0).intersection(B) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(B)])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
notch = V.buffer(0.08).buffer(-0.08).intersection(B).intersection(LAND).difference(V)
notch = unary_union([g for g in getattr(notch, 'geoms', [notch]) if A(g) > 1])
# Version 459 (his second red stroke along the notch's mouth, read off the screenshot: 31.64 E 3.62 N, 31.71 E 3.62 N, 31.84 E 3.55 N, 31.93 E 3.56 N):
# all land north of that stroke and outside V1 in the notch goes in
if os.environ.get('STROKE'):
    from shapely.geometry import Polygon as Pg
    from shapely.ops import nearest_points
    P0 = nearest_points(V.boundary, Point(31.64, 3.62))[0]          # the stroke starts on V1's own edge, so no step is left
    S = Pg([(P0.x, 3.85), (P0.x, P0.y), (31.71, 3.62), (31.84, 3.55), (31.95, 3.555), (31.95, 3.85)])
    extra = S.intersection(LAND).difference(V); print('   stroke fill', round(A(extra)), 'km2')
    notch = unary_union([notch, extra])
print('notch filled', round(A(notch)), 'km2', [round(c, 2) for c in notch.bounds] if not notch.is_empty else '')
X = unary_union([V, notch.buffer(0.002)]).buffer(0)
if os.environ.get('STROKE'):   # smooth the two little steps where the stroke meets the old edge
    SB = box(31.45, 3.45, 32.0, 3.75)
    X = unary_union([X, X.buffer(0.04).buffer(-0.04).intersection(SB).intersection(LAND)]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
