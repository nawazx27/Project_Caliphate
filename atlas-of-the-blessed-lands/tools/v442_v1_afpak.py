"""Version 442 (Nawaz: "Add Pakistan and Afghanistan", after the Version 441 preview). V1 (shj) takes Afghanistan and Pakistan whole (Pakistan as the
base map draws it, with Azad Kashmir and Gilgit-Baltistan; Indian-administered Kashmir and Siachen are not added). Long straight inland stretches of the new
edge are roughened as in Version 441 (fixed seed). Run AFTER tools/v441_v1_farmland_rest.py. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union(list(G.values())).buffer(0)
AD = json.load(open(os.path.join(P, 'admin1_used.geojson')))
NIM = unary_union([shape(f['geometry']).buffer(0) for f in AD['features'] if f['properties'].get('adm0_a3') == 'AFG' and f['properties'].get('name') == 'Nimroz'])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
NEWL = unary_union([G['Afghanistan'], G['Pakistan']]).buffer(0)
X = unary_union([V, NEWL.buffer(0.003).intersection(V2.buffer(0.002))]).buffer(0)
# roughen long straight inland stretches of the exterior that lie on the newly added land
SEA = shapely.box(-20, -10, 80, 60).difference(LAND).buffer(0.15)
rng = np.random.default_rng(442)
def rough(ring):
    c = np.array(ring.coords); out = [c[0]]; nr = 0
    for a, b in zip(c[:-1], c[1:]):
        L = np.hypot(*(b - a)); mid = Point((a + b) / 2)
        if L >= 0.3 and NEWL.buffer(0.05).contains(mid) and not SEA.contains(mid):
            n = max(12, int(L / 0.02)); u = np.linspace(0, 1, n + 1)[1:]
            def nz(k, amp):
                v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, n); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
                return amp * (v[i] * (1 - f) + v[i + 1] * f)
            d = np.clip(nz(max(2, int(L / 0.8)), 0.12) + nz(max(3, int(L / 0.25)), 0.05) + nz(max(4, int(L / 0.08)), 0.02), -0.22, 0.22) * np.sin(np.pi * u) ** 0.6
            nv = np.array([-(b - a)[1], (b - a)[0]]) / L
            for t_, dd in zip(u, d): out.append(a + t_ * (b - a) + dd * nv)
            nr += 1
        else: out.append(b)
    return out, nr
# straight runs are found on a simplified copy of the edge (the base map stores them as many short collinear pieces), then each is replaced
# inside a band round it by a rough line: land on V1's side of the rough line in, the other side out
segs = []
for q in getattr(X, 'geoms', [X]):
    c = np.array(q.exterior.simplify(0.004).coords)
    for a, b in zip(c[:-1], c[1:]):
        L = np.hypot(*(b - a)); mid = Point((a + b) / 2)
        if L >= 0.3 and NEWL.buffer(0.05).contains(mid) and not SEA.contains(mid): segs.append((a, b))
print('   straight stretches roughened:', len(segs))
for a, b in segs:
    L = np.hypot(*(b - a)); n = max(16, int(L / 0.015)); u = np.linspace(0, 1, n)
    def nz(k, amp):
        v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, n); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
        return amp * (v[i] * (1 - f) + v[i + 1] * f)
    d = np.clip(nz(max(2, int(L / 0.8)), 0.12) + nz(max(3, int(L / 0.25)), 0.05) + nz(max(4, int(L / 0.08)), 0.02), -0.22, 0.22) * np.sin(np.pi * u) ** 0.6
    nv = np.array([-(b - a)[1], (b - a)[0]]) / L
    Lp = a + u[:, None] * (b - a)
    if X.contains(Point((a + b) / 2 + 0.05 * nv)): nv = -nv          # nv points out of V1
    RL = Lp + d[:, None] * nv[None, :]
    OUT = Polygon(list(map(tuple, RL)) + [tuple(b + 0.6 * nv), tuple(a + 0.6 * nv)]).buffer(0)
    BAND = LineString(Lp).buffer(0.3, cap_style=2)
    X = unary_union([X.difference(OUT.intersection(BAND)), BAND.difference(OUT).intersection(LAND)]).buffer(0)
X = X.intersection(LAND.buffer(0.004)).buffer(0) if False else X
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 20]
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
old = C['shj']['km2']; NEW = Y.difference(V)
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2', {k: round(100 * G[k].intersection(Y).area / G[k].area, 1) for k in ['Afghanistan', 'Pakistan', 'India']})
for n_, p in {'Kabul': (69.17, 34.53), 'Herat': (62.2, 34.35), 'Balkh': (66.9, 36.76), 'Kandahar': (65.71, 31.61), 'Islamabad': (73.05, 33.68), 'Lahore': (74.34, 31.55), 'Karachi': (67.0, 24.86), 'Gilgit': (74.31, 35.92), 'Muzaffarabad': (73.47, 34.37)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
