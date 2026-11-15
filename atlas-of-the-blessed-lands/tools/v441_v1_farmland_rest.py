"""Version 441 (Nawaz, after the web check found four historic farmlands still outside V1: "Make sure v1 has the entire historic farmland of the Middle
East"). V1 (shj) takes: all of Libya (Tripolitania's Roman olive lands: the Jefara, the Jebel Nafusa, Tarhuna, Leptis Magna, Tripoli; and the Fezzan's
Garamantian oases), Armenia, Azerbaijan and Georgia whole (the Ararat plain, the Kura and Aras valleys, Kakheti), and Afghanistan's Nimroz province
(Afghan Sistan: Zaranj, Chakhansur and the canal-watered Sar-o-Tar plain). Every long straight stretch of the new outer edge (inland, 0.3 deg or longer:
the Saharan borders of Libya, Nimroz's lines) is roughened (fixed seed, up to ~25 km, tapered at its ends). DIR env = project dir. Run v386 after."""
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
NEWL = unary_union([G['Libya'], G['Armenia'], G['Azerbaijan'], G['Georgia'], NIM]).buffer(0)
X = unary_union([V, NEWL.buffer(0.003).intersection(V2.buffer(0.002))]).buffer(0)
# roughen long straight inland stretches of the exterior that lie on the newly added land
SEA = shapely.box(-20, -10, 80, 60).difference(LAND).buffer(0.15)
rng = np.random.default_rng(441)
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
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2', {k: round(100 * G[k].intersection(Y).area / G[k].area, 1) for k in ['Libya', 'Armenia', 'Azerbaijan', 'Georgia', 'Afghanistan']}, '| Nimroz', round(100 * NIM.intersection(Y).area / NIM.area, 1))
for n_, p in {'Tripoli': (13.19, 32.89), 'Leptis Magna': (14.29, 32.64), 'Tarhuna': (13.63, 32.43), 'Gharyan': (13.02, 32.17), 'Sabha': (14.43, 27.04), 'Germa (Garamantes)': (12.75, 26.55), 'Ghadames': (9.5, 30.13),
              'Yerevan': (44.51, 40.18), 'Ganja': (46.36, 40.68), 'Telavi (Kakheti)': (45.47, 41.92), 'Zaranj': (61.88, 31.0), 'Sar-o-Tar': (62.1, 30.9), 'Chakhansur': (62.07, 31.16)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
