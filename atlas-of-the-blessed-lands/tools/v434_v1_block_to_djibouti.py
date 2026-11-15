"""Version 434 (Nawaz, a red circle round V1's Sudan block, the Egyptian-Empire-map land south of Egypt from the Libyan corner to the Eritrean coast:
"I meant this block... drag it keeping its shape until it reaches Djibouti" / "Drag or expand preserving its shape").
The block's whole southern edge (from where it leaves the Libya-Sudan border, 25.06 E 20.0 N, down its south-west side, round the bulge and up to the
Red Sea shore at the Gulf of Zula, 40.16 E 15.03 N) is made larger as one piece, the same shape in length and width (MODE=expand, the default: scaled and turned about the corner where its
left side starts, 25.06 E 20.0 N, so its coastal end reaches Djibouti's coast at the Somaliland border, 43.24 E 11.49 N, then widened across its
length by WIDE, default 1.15, "a bit more wider"; MODE=drag only moves it there, which gave the length but not the width). The new block is joined to V1 as it stands (no sweep: sliding the edge along itself had filled its bends and left a
straight line, which Nawaz rejected; the left side must keep its own shape), so the new left side is the old one carried on with all its bends;
the land between the moved block and the sea is taken to the shore.
Djibouti is taken whole with its islands; Somaliland stays out, and the straight Djibouti-Somaliland border is roughened like the Version 429 edges.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, shapely.affinity, numpy as np
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
AF = max(V.geoms, key=lambda q: q.contains(Point(31.2, 30.0)))
R = np.array(AF.exterior.coords[:-1])
near = lambda x, y: int(np.argmin(np.hypot(R[:, 0] - x, R[:, 1] - y)))
iZ, iC = near(40.16, 15.025), near(25.062, 20.006)
assert iZ < iC, (iZ, iC)
E = R[iZ:iC + 1]; print('edge', len(E), 'points from', E[0].round(3), 'to', E[-1].round(3), '| lowest', E[:, 1].min().round(2))
T = np.array([43.242, 11.488]); D = T - E[0]; print('drag vector', D.round(3), '(east, north) degrees')
B = AF.intersection(Polygon([(24.98, 5), (46, 5), (46, 22.0), (24.98, 22.0)]))      # the block: V1's African land south of Egypt's 22 N line, east of Libya
MODE = os.environ.get('MODE', 'expand')
if MODE == 'drag':                                     # moved as one piece: the length reaches Djibouti, the width stays
    BD = shapely.affinity.translate(B, D[0], D[1]); E2 = E + D
else:                                                  # expanded as one piece (Nawaz: "You got the length, now get the width"): the same shape made larger,
    Cc = E[-1]; vz, vt = E[0] - Cc, T - Cc           # length and width alike, from the corner where its left side starts (fixed), so its tip reaches Djibouti
    k = np.hypot(*vt) / np.hypot(*vz); th = np.arctan2(vt[1], vt[0]) - np.arctan2(vz[1], vz[0])
    a_, b_, d_, e_ = k * np.cos(th), -k * np.sin(th), k * np.sin(th), k * np.cos(th)
    M = [a_, b_, d_, e_, Cc[0] - a_ * Cc[0] - b_ * Cc[1], Cc[1] - d_ * Cc[0] - e_ * Cc[1]]
    WIDE = float(os.environ.get('WIDE', '1.15'))     # Nawaz: "A bit more wider": then widened across its length (corner-to-tip line kept, so the corner
    uu = vt / np.hypot(*vt); nn = np.array([-uu[1], uu[0]])   # and the tip stay put), by WIDE (1 = the plain enlargement)
    Sm = np.eye(2) + (WIDE - 1) * np.outer(nn, nn); Lm = Sm @ np.array([[a_, b_], [d_, e_]]); off = Cc - Lm @ Cc
    M = [Lm[0, 0], Lm[0, 1], Lm[1, 0], Lm[1, 1], off[0], off[1]]
    BD = shapely.affinity.affine_transform(B, M); E2 = E @ Lm.T + off
    print('   widened by', WIDE, '| tip ->', E2[0].round(3), '| corner ->', E2[-1].round(3))
    print('expand: scale', round(k, 3), 'turn', round(np.degrees(th), 2), 'degrees, about', Cc.round(3), '| tip ->', E2[0].round(3))
ib = int(np.argmin(E[:, 1]))                      # the bulge: from here east the land between the moved edge and the sea is taken to the shore
SHORE = Polygon(list(map(tuple, E2[:ib + 1][::-1])) + [(43.9, 11.2), (44.6, 12.2), (44.6, 15.6), (40.6, 15.6)] + list(map(tuple, E[:ib + 1]))).buffer(0)
AFR = unary_union([G[k] for k in ['Sudan', 'South Sudan', 'Eritrea', 'Ethiopia', 'Djibouti']])
add = unary_union([unary_union([BD, SHORE]).intersection(AFR), G['Djibouti']]).buffer(0.003)
X = unary_union([V, add.intersection(V2.buffer(0.002))]).buffer(0)
# the straight Djibouti-Somaliland border (tripoint 42.925 E 10.999 N to the coast 43.242 E 11.488 N) roughened: within a band round it, land on the Djibouti
# side of a rough line is in, on the Somaliland side out
P0, P1 = np.array([42.925, 10.999]), np.array([43.242, 11.488]); u = np.linspace(0, 1, 160); L = P0 + u[:, None] * (P1 - P0)
nv = np.array([-(P1 - P0)[1], (P1 - P0)[0]]); nv /= np.hypot(*nv)
rng = np.random.default_rng(434)
def noise(sc, amp):
    k = max(2, len(u) // sc); v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, len(u)); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
dn = np.clip(noise(20, 0.02) + noise(7, 0.012) + noise(3, 0.005), -0.035, 0.035) * np.sin(np.pi * u) ** 0.5
RL = L + dn[:, None] * nv[None, :]
BAND = LineString(L).buffer(0.06)
SE = Polygon(list(map(tuple, RL)) + [(43.6, 11.2), (43.2, 10.6), (42.6, 10.7)]).buffer(0)
X = unary_union([X.difference(SE.intersection(BAND).difference(G['Ethiopia'])), BAND.difference(SE).intersection(unary_union([G['Djibouti'], G['Somaliland']]))]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 34.5]
X = unary_union([X] + holes).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or not (24 < q.centroid.x < 44 and q.centroid.y < 14)])   # no crumbs
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
old = C['shj']['km2']
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
NEW = Y.difference(V)
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2:', {k: round(A(NEW.intersection(G[k]))) for k in ['Sudan', 'South Sudan', 'Ethiopia', 'Eritrea', 'Djibouti', 'Somaliland', 'Chad']})
for n_, p in {'Assab': (42.74, 13.01), 'Djibouti city': (43.15, 11.59), 'Ras Siyyan': (43.32, 12.48), 'Mekelle': (39.47, 13.5), 'Lalibela': (39.04, 12.03), 'Gondar': (37.47, 12.6),
              'Bahir Dar': (37.39, 11.6), 'Lake Tana centre': (37.3, 12.0), 'Dessie': (39.63, 11.13), 'Debre Markos': (37.73, 10.33), 'Addis Ababa': (38.75, 9.03), 'Semera': (41.01, 11.79),
              'Gedaref': (35.38, 14.03), 'Sennar': (33.63, 13.55), 'Damazin': (34.36, 11.79), 'Kosti': (32.66, 13.16), 'El Obeid': (30.22, 13.18), 'Renk (S. Sudan)': (32.78, 11.75), 'Malakal (S. Sudan)': (31.66, 9.53), 'El Fasher': (25.35, 13.63), 'Kadugli': (29.72, 11.01), 'Asosa': (34.53, 10.07)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
