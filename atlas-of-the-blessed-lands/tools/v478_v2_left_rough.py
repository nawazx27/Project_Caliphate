"""Version 478 (Nawaz: "Make the left side look better and rough like all other borders and not cartoonish... and push directly"). V2's (CALIPH.arb)
left side of the shield, from the foot of the straight Sudan-Chad line (24 E 15.72 N, the line itself untouched) down round the west and south-west
through Chad, the Central African Republic and DR Congo to ~3 S near Lake Tanganyika, is given a natural, surveyed-border roughness: the edge is
densified (~2 km) and moved along its normal by fixed-seed fractal noise (four scales, from ~60 km bends down to ~2 km wiggles, at most ~12 km),
faded to nothing at both ends. V1 and the whole traced Nile basin are kept inside. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(10, -8, 35, 20))]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); V1 = MP(C['shj']['polys'])
B = shape(json.load(open(os.path.join(HERE, 'tools/data/v453_nile_basin_traced.geojson')))['geometry']).buffer(0)
GS = list(V.geoms); mi = max(range(len(GS)), key=lambda i: GS[i].area); M = GS[mi]
R = np.array(shapely.segmentize(M.exterior, 0.02).coords)[:-1]
inreg = (R[:, 0] < 30.6) & (R[:, 1] > -3.0) & (R[:, 1] < 15.6) & ~((R[:, 0] > 23.9) & (R[:, 1] > 15.0))
# the longest run of ring points in the region (wrapping round the ring's start)
idx = np.where(inreg)[0]; n = len(R)
runs, cur = [], [idx[0]]
for a, b in zip(idx[:-1], idx[1:]):
    if b == a + 1: cur.append(b)
    else: runs.append(cur); cur = [b]
runs.append(cur)
if len(runs) > 1 and runs[0][0] == 0 and runs[-1][-1] == n - 1: runs[0] = runs[-1] + runs[0]; runs.pop()
run = np.array(max(runs, key=len)); print('edge points', len(run), 'from', R[run[0]].round(2), 'to', R[run[-1]].round(2))
E = R[run]; m = len(E)
tg = np.gradient(E, axis=0); tg /= np.hypot(tg[:, 0], tg[:, 1])[:, None] + 1e-12; nv = np.c_[tg[:, 1], -tg[:, 0]]
rng = np.random.default_rng(478)
def octave(step, amp):
    k = max(3, m // step + 3); v = rng.normal(0, 1, k); q = np.linspace(0, k - 2, m); i = q.astype(int); f = q - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
dn = octave(30, 0.05) + octave(11, 0.022) + octave(4, 0.009) + octave(1, 0.004)
dn = np.clip(dn, -0.11, 0.11) * np.minimum(1, np.minimum(np.arange(m), np.arange(m)[::-1]) / 25.0)
R2 = R.copy(); R2[run] = E + dn[:, None] * nv
X = Polygon(R2).buffer(0)
X = unary_union([X] + [g for i, g in enumerate(GS) if i != mi] + [V1, B.intersection(V).intersection(LAND)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 2000]).buffer(0)
print('moved out', round(A(X.difference(V))), 'km2, in', round(A(V.difference(X))), 'km2 | max shift', round(float(np.abs(dn).max()) * 111, 1), 'km')
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('arb', C['arb']['km2'], '->', km, '| V1 outside', round(A(V1.difference(Y.buffer(0.002))), 1), '| basin outside', round(A(B.intersection(LAND).difference(Y.buffer(0.002))), 1))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
