"""Version 437 (Nawaz, after "Does v1 have" the fertile Nile lands: the White Nile floodplains were only half in, down to ~7.45 N; "Preview").
V1's (shj) bottom in South Sudan is pushed further south round the White Nile, in its own shape, until the whole Sudd floodplain to Bor is in: every
point below Y1 moves straight down by DY * g(x), g = 1 over the White Nile corridor (30-33 E) easing to 0 by 28 E and 35 E, and the push eases
to nothing between Y1 and Y0 (env DY default 2.6, Y0 13, Y1 9; the edge by the river was at ~8.4 N); nothing is swept, so the edge keeps its bends. Only Sudanese, South Sudanese and
Ethiopian land is taken. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely.prepared import prep
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
DY = float(os.environ.get('DY', '2.6')); Y0 = float(os.environ.get('Y0', '13.0')); Y1 = float(os.environ.get('Y1', '9.0'))
XA, XB, XC, XD = 28.0, 30.0, 33.0, 35.0
AFR = unary_union([G[k] for k in ['Sudan', 'South Sudan', 'Ethiopia', 'Chad', 'Central African Rep.']])
piece = V.intersection(AFR).intersection(box(XA - 0.5, 0, XD + 0.5, Y0 + 0.01))
ss = lambda t: t * t * (3 - 2 * t)
def shift(x, y):
    v = ss(np.clip((Y0 - y) / (Y0 - Y1), 0, 1)); g = ss(np.clip((x - XA) / (XB - XA), 0, 1)) * ss(np.clip((XD - x) / (XD - XC), 0, 1))
    return DY * v * g
moved = shapely.transform(piece.segmentize(0.02), lambda c: np.c_[c[:, 0], c[:, 1] - shift(c[:, 0], c[:, 1])]).buffer(0)
TAKE = unary_union([G[k] for k in ['Sudan', 'South Sudan', 'Ethiopia']])
X = unary_union([V, moved.intersection(TAKE).buffer(0.003).intersection(TAKE.buffer(0.003))]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 20]
X = unary_union([X] + holes).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u_, 3), round(v_, 3)] for u_, v_ in rr.coords] for rr in [q.exterior, *q.interiors]])
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
old = C['shj']['km2']; NEW = Y.difference(V)
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2', {k: round(A(NEW.intersection(G[k]))) for k in ['South Sudan', 'Ethiopia', 'Uganda', 'Kenya']})
F = json.load(open(os.path.join(P, 'src/four_rivers.json'))); r = [x for x in F['rivers'] if x['k'] == 'nile'][0]
pts = np.array([q for p in r['parts'] for q in p]); wn = pts[(pts[:, 0] > 29.5) & (pts[:, 0] < 33.0) & (pts[:, 1] < 15.6) & (pts[:, 1] > 3.5)]
PY = prep(Y.buffer(0.01)); ins = np.array([PY.contains(Point(p)) for p in wn])
print('White Nile in: southernmost inside', round(wn[ins][:, 1].min(), 2), '| northernmost outside', round(wn[~ins][:, 1].max(), 2) if (~ins).any() else None)
print('Sudd box (29.8-32.2 E, 6.0-9.6 N) inside %', round(100 * box(29.8, 6.0, 32.2, 9.6).intersection(Y).area / box(29.8, 6.0, 32.2, 9.6).area, 1))
for n_, p in {'Bor': (31.56, 6.21), 'Shambe': (30.77, 7.11), 'Mongalla': (31.77, 5.2), 'Juba': (31.58, 4.85), 'Rumbek': (29.7, 6.8), 'Wau': (28.0, 7.7), 'Akobo': (33.0, 7.78), 'Malakal': (31.66, 9.53)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
