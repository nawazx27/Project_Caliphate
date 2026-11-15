"""Version 435 (Nawaz: "Add entire modern Sudan"). V1 (shj) takes all of Sudan (Darfur, West and South Kordofan to the borders of Chad, the Central African
Republic and South Sudan). Two straight stretches of the new edge are roughened with natural-looking bends (fixed seed, up to ~40 km, tapered at the ends):
the Sudan-Chad line along 24 E (15.7-19.5 N) and the Sudan-South Sudan line along 9.33 N (28.05-28.84 E). Kept inside V2.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
X = unary_union([V, G['Sudan'].buffer(0.003).intersection(V2.buffer(0.002))]).buffer(0)
rng = np.random.default_rng(435)
def roughen(X, P0, P1, inside, outside_land):
    P0, P1 = np.array(P0), np.array(P1); L = np.hypot(*(P1 - P0)); n = max(16, int(L / 0.015)); u = np.linspace(0, 1, n)
    def noise(k, amp):
        k = max(2, int(k)); v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, n); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
        return amp * (v[i] * (1 - f) + v[i + 1] * f)
    # bends every ~90, ~28 and ~9 km, like the natural stretch of the Sudan-Chad border further south (up to ~40 km)
    d = np.clip(noise(L / 0.8, 0.28) + noise(L / 0.25, 0.09) + noise(L / 0.08, 0.03), -0.38, 0.38) * np.sin(np.pi * u) ** 0.6
    Lp = P0 + u[:, None] * (P1 - P0); nv = np.array([-(P1 - P0)[1], (P1 - P0)[0]]) / L
    if np.dot(np.array(inside) - P0, nv) < 0: nv = -nv                 # nv points into V1
    RL = Lp + d[:, None] * nv[None, :]
    OUT = Polygon(list(map(tuple, RL)) + [tuple(P1 - 0.6 * nv), tuple(P0 - 0.6 * nv)]).buffer(0)
    BAND = LineString(Lp).buffer(0.45, cap_style=2)
    return unary_union([X.difference(OUT.intersection(BAND)), BAND.difference(OUT).intersection(outside_land)]).buffer(0)
X = roughen(X, (23.982, 19.497), (23.985, 15.721), (25.0, 17.5), unary_union([G['Sudan'], G['Chad']]))
X = roughen(X, (28.842, 9.325), (28.046, 9.332), (28.4, 10.5), unary_union([G['Sudan'], G['South Sudan']]))
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 34.5]
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
    g = G[f['properties']['n']]
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; NEW = Y.difference(V)
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2', {k: round(A(NEW.intersection(G[k]))) for k in ['Sudan', 'Chad', 'South Sudan', 'Central African Rep.'] if k in G},
      '| Sudan inside', round(100 * G['Sudan'].intersection(Y).area / G['Sudan'].area, 2), '%')
for n_, p in {'El Fasher': (25.35, 13.63), 'Nyala': (24.88, 12.05), 'El Geneina': (22.45, 13.45), 'Zalingei': (23.47, 12.9), 'El Daein': (26.13, 11.46), 'Babanusa': (27.81, 11.33), 'Abyei area': (28.4, 9.6), 'Jebel Marra': (24.27, 12.95)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
