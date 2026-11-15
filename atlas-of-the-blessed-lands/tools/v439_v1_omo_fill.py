"""Version 439 (Nawaz, red stroke on the Version 438 close-up from the north tip of Lake Turkana up to V1's edge, ~35.95 E 4.62 N to ~36.95 E 6.15 N: "Fill").
The Ethiopian land west of his stroke (the lower Omo corner between South Sudan and V1's Ethiopian lobe) goes into V1 (shj); the stroke becomes the edge,
roughened like the Version 429 edges (fixed seed). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
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
P0, P1 = np.array([35.95, 4.62]), np.array([36.95, 6.15]); n = 160; u = np.linspace(0, 1, n); L = P0 + u[:, None] * (P1 - P0)
nv = np.array([-(P1 - P0)[1], (P1 - P0)[0]]); nv /= np.hypot(*nv)
rng = np.random.default_rng(439)
def noise(k, amp):
    v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, n); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
d = np.clip(noise(3, 0.06) + noise(9, 0.025) + noise(25, 0.01), -0.1, 0.1) * np.sin(np.pi * u) ** 0.5
RL = L + d[:, None] * nv[None, :]
WEST = Polygon(list(map(tuple, RL)) + [(36.95, 7.6), (34.0, 7.6), (34.0, 4.3), (35.95, 4.3)]).buffer(0)
add = WEST.intersection(G['Ethiopia'])
X = unary_union([V, add.buffer(0.003).intersection(G['Ethiopia'].buffer(0.003))]).buffer(0)
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
print('shj', old, '->', km, '| added', round(A(Y.difference(V))), 'km2 | holes', sum(len(p) - 1 for p in o))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
