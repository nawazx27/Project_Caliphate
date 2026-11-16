"""Version 463 (Nawaz, a U-shaped red stroke on the Version 462 preview round V1's edge at Nimule, the Albert Nile's entry: from ~31.22 E 4.10 N down to
~31.61-31.85 E 3.13 N and up to ~32.64 E 3.71 N; placed by fitting V1's own drawn outline in that picture, median error under 1 pixel). The land inside the
U (north-western Uganda: Moyo, Adjumani, Yumbe, the Albert Nile's valley) goes into V1 (shj). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union, nearest_points
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ST = [(31.218, 4.105), (31.25, 3.711), (31.376, 3.348), (31.613, 3.127), (31.85, 3.127), (32.166, 3.348), (32.641, 3.711)]
def chaikin(P, n=5):   # the stroke is a hand-drawn curve: smooth the read-off points into one, no straight segments
    for _ in range(n):
        Q = [P[0]]
        for (x0, y0), (x1, y1) in zip(P[:-1], P[1:]): Q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        P = Q + [P[-1]]
    return P
POLY = Polygon(chaikin(ST) + [(32.641, 4.3), (31.218, 4.3)]).buffer(0)
LANDS = unary_union([G['Uganda'], G['South Sudan'], G['DR Congo']])
add = POLY.intersection(LANDS).difference(V); print('filled', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Uganda', 'South Sudan', 'DR Congo']})
X = unary_union([V, add.buffer(0.003).intersection(LANDS.buffer(0.003))]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Moyo': (31.72, 3.66), 'Adjumani': (31.79, 3.38), 'Yumbe': (31.25, 3.47), 'Arua (out)': (30.91, 3.02), 'Gulu (out)': (32.3, 2.78)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
