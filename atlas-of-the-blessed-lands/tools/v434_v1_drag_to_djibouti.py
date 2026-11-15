"""Version 434 (Nawaz, after "Thoughts on V1?" named the African shore of the Bab el-Mandeb as outside: "Drag that block until Djibouti").
V1's (shj) Eritrean block is dragged down the coast to Djibouti: its own southern edge (the Version 425 curve from the bottom of the south-western bulge,
~35.5 E 13.0 N, up to the shore at the Gulf of Zula) keeps its shape and roughness but its coastal end is pulled to Djibouti's south-western corner
by Lake Abbe (41.76 E 10.99 N), the pull growing along the edge (none at the bulge, full at the end; env W = power, default 1.6), so the edge passes under
the whole of Djibouti with no step on the Djibouti-Ethiopia line. The land between the old and the new edge goes in (southern Eritrea with the Danakil coast
and Assab, the part of Tigray and Afar above the new edge), and Djibouti whole with its islands; from the corner the outline follows Djibouti's own southern
border, and the straight Djibouti-Somaliland border to the sea is roughened like the Version 429 edges (fixed seed, ~3 km). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
AF = max(V.geoms, key=lambda q: q.contains(Point(31.2, 30.0)))
R = np.array(AF.exterior.coords[:-1]); n = len(R)
i0 = int(np.argmin(np.hypot(R[:, 0] - 35.5, R[:, 1] - 13.0))); i1 = int(np.argmin(np.hypot(R[:, 0] - 40.3, R[:, 1] - 15.15)))
def path(a, b, step): 
    out = [a]
    while out[-1] != b: out.append((out[-1] + step) % n)
    return out
pa, pb = path(i0, i1, 1), path(i0, i1, -1); idx = pa if len(pa) < len(pb) else pb
S = R[idx]; print('edge', len(S), 'points from', S[0].round(2), 'to', S[-1].round(2), 'lat range', S[:, 1].min().round(2), S[:, 1].max().round(2))
seg = np.r_[0, np.cumsum(np.hypot(*np.diff(S, axis=0).T))]; t = seg / seg[-1]
TARGET = np.array([41.762, 10.985]); D = TARGET - S[-1]; W = float(os.environ.get('W', '1.6'))
S2 = S + (t ** W)[:, None] * D[None, :]
ADD = Polygon(list(map(tuple, S2)) + [(43.6, 10.6), (44.6, 11.6), (44.6, 15.6), (40.6, 15.6)] + list(map(tuple, S[::-1]))).buffer(0)
AFR = unary_union([G['Eritrea'], G['Ethiopia'], G['Sudan']])
add = unary_union([ADD.intersection(AFR), G['Djibouti']]).buffer(0.003)
X = unary_union([V, add.intersection(V2.buffer(0.002))]).buffer(0)
# roughen the straight Djibouti-Somaliland border (tripoint 42.925 E 10.999 N to the coast 43.242 E 11.488 N): within a band round it, land on the
# Djibouti side of a rough line is in, on the Somaliland side out
P0, P1 = np.array([42.925, 10.999]), np.array([43.242, 11.488]); u = np.linspace(0, 1, 160); L = P0 + u[:, None] * (P1 - P0)
nv = np.array([-(P1 - P0)[1], (P1 - P0)[0]]); nv /= np.hypot(*nv)          # normal pointing north-west (into Djibouti)
rng = np.random.default_rng(434)
def noise(sc, amp):
    k = max(2, len(u) // sc); v = rng.normal(0, 1, k + 3); q = np.linspace(0, k, len(u)); i = np.minimum(q.astype(int), k + 1); f = q - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
dn = np.clip(noise(20, 0.02) + noise(7, 0.012) + noise(3, 0.005), -0.035, 0.035) * np.sin(np.pi * u) ** 0.5
RL = L + dn[:, None] * nv[None, :]
BAND = LineString(L).buffer(0.06)
SE = Polygon(list(map(tuple, RL)) + [(43.6, 11.2), (43.2, 10.6), (42.6, 10.7)]).buffer(0)
LANDH = unary_union([G['Djibouti'], G['Somaliland'], G['Ethiopia']])
X = unary_union([X.difference(SE.intersection(BAND)), BAND.difference(SE).intersection(LANDH)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 34.5]
X = unary_union([X] + holes).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or not (35 < q.centroid.x < 44 and q.centroid.y < 13.5)])   # no crumbs below the new edge
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); rws = []
for k_, g in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'n': k_, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': [{**r, 'id': f['id']} for r in sorted(rws, key=lambda r: -r['km2'] * r['pct']) for f in geo['features'] if f['properties']['n'] == r['n']][:len(rws)]}
print('shj', old, '->', km, '| added', round(A(Y.difference(V))), 'km2')
for n_, p in {'Asmara': (38.93, 15.32), 'Massawa': (39.45, 15.61), 'Assab': (42.74, 13.01), 'Djibouti city': (43.15, 11.59), 'Ras Siyyan': (43.32, 12.48), 'Tadjoura': (42.88, 11.79), 'Ali Sabieh': (42.71, 11.16),
              'Mekelle': (39.47, 13.5), 'Axum': (38.72, 14.13), 'Adigrat': (39.46, 14.28), 'Semera': (41.01, 11.79), 'Lalibela': (39.04, 12.03), 'Gondar': (37.47, 12.6), 'Lake Tana': (37.3, 12.0), 'Dessie': (39.63, 11.13)}.items():
    print('  ', n_, Y.contains(Point(p)))
for lon in [36, 37, 38, 39, 40, 41, 42]:
    i = int(np.argmin(abs(S2[:, 0] - lon))); print('   new edge at', lon, 'E ~', S2[i, 1].round(2), 'N')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
