"""Version 423 (Nawaz, a red curve from V1's south-west corner below Lake Tana to the coast at the Bab el-Mandeb: "push it to the coast naturally").
V1's (shj) southern edge from the Egyptian Empire border (~33.6 E 13.6 N) to the Eritrea-Djibouti coast (Ras Doumeira, 43.12 E 12.71 N) becomes his curve,
dipping below Lake Tana (~10.95 N, the whole lake inside), roughened like the Version 420 border; the land between it and V1 is added (no straight cut at 12.95 N any more). Kept inside V3.
Then rerun tools/v411_arabia.py and the ellipsoid tool."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union(list(G.values()))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
K = [(33.6, 13.6), (34.3, 12.9), (35.0, 12.2), (35.8, 11.6), (36.6, 11.15), (37.5, 10.95), (38.5, 10.95), (39.5, 11.15), (40.5, 11.6), (41.5, 12.15), (42.4, 12.6), (43.12, 12.71)]
line = LineString(K); n = int(line.length / 0.02); pts = np.array([line.interpolate(line.length * i / n).coords[0] for i in range(n + 1)])
# smooth (Chaikin-like) then rough
from scipy.ndimage import gaussian_filter1d
pts[:, 1] = gaussian_filter1d(pts[:, 1], 6, mode='nearest')
rng = np.random.default_rng(423)
def noise(sc, amp):
    k = max(2, n // sc); v = rng.normal(0, 1, k + 3); x = np.linspace(0, k, n + 1); i = np.minimum(x.astype(int), k + 1); f = x - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
d = np.clip(noise(40, 0.06) + noise(14, 0.04) + noise(5, 0.02), -0.12, 0.12); d[:15] *= np.linspace(0, 1, 15); d[-15:] *= np.linspace(1, 0, 15)
pts[:, 1] += d
REG = Polygon(list(map(tuple, pts)) + [(43.6, 12.71), (43.6, 16.5), (33.4, 16.5), (33.4, 13.6)]).buffer(0)
NEW = REG.intersection(LAND).difference(V).difference(G.get('Djibouti', Polygon()))
print('   added', round(A(NEW)), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000]
X = unary_union([X] + holes).intersection(V3.buffer(0.002)); X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o)
for n_, p in {'Lake Tana (Bahir Dar)': (37.39, 11.59), 'Gondar': (37.47, 12.6), 'Lalibela': (39.05, 12.03), 'Woldia': (39.6, 11.83), 'Semera': (41.0, 11.79), 'Dessie (out)': (39.63, 11.13), 'Djibouti (out)': (43.15, 11.59)}.items(): print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
