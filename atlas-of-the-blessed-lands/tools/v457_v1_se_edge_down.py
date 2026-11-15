"""Version 457 (Nawaz, red loop on his phone screenshot round V1's south-east edge in Ethiopia, from the north tip of Lake Turkana up to Djibouti:
"Bring this piece just a bit down"). V1's (shj) land within a band round that edge is pushed straight south by DY degrees (env, default 0.5, ~55 km),
easing to nothing at the two ends (Lake Turkana, west of 36.3 E; Djibouti, east of 42.3 E), so the edge keeps its own shape and stays joined; only
Ethiopian land is taken. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
DY = float(os.environ.get('DY', '1.0'))
BAND = LineString([(35.95, 4.6), (37.0, 6.0), (39.0, 7.6), (41.0, 9.4), (42.9, 11.1)]).buffer(1.4)
piece = V.intersection(BAND).intersection(G['Ethiopia'].buffer(0.01))
ss = lambda t: t * t * (3 - 2 * t)
TAPER = os.environ.get('TAPER', '0') == '1'   # Nawaz: "More of the entire piece": the whole piece moves, ends included (clipped to Ethiopia's borders)
shift = (lambda x: DY * ss(np.clip((x - 36.3) / 1.2, 0, 1)) * ss(np.clip((42.3 - x) / 1.0, 0, 1))) if TAPER else (lambda x: DY + 0 * x)
seg = piece.segmentize(0.02)
moved = unary_union([shapely.transform(seg, lambda c, k=k: np.c_[c[:, 0], c[:, 1] - k / 8 * shift(c[:, 0])]) for k in range(1, 9)]).buffer(0)   # every step of the way down, so no gap opens behind the piece
add = moved.intersection(G['Ethiopia'])
X = unary_union([V, add.buffer(0.003).intersection(G['Ethiopia'].buffer(0.003))]).buffer(0)
ET = G['Ethiopia']
X = unary_union([X, X.buffer(0.25).buffer(-0.25).intersection(ET)]).buffer(0)   # close slivers left between the moved piece and Ethiopia's borders
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 50000]
X = unary_union([X] + holes).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); rws = []
for f in geo['features']:
    if not f.get('geometry'): continue
    g_ = G[f['properties']['n']]
    if g_.area and g_.intersects(Y):
        pct = round(100 * g_.intersection(Y).area / g_.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g_)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| added', round(A(Y.difference(V))), 'km2 | Ethiopia in V1', round(100 * G['Ethiopia'].intersection(Y).area / G['Ethiopia'].area), '%')
for n_, p in {'Hawassa': (38.48, 7.05), 'Adama': (39.27, 8.54), 'Awash': (40.17, 8.98), 'Dire Dawa': (41.86, 9.6), 'Arba Minch': (37.55, 6.03)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
