"""Version 429 (Nawaz, screenshot of V1's Libyan side with a red line across the notch at the Libya-Sudan-Chad corner: "Fill and make the straight edges and lines
rough"). (1) The notch between Libya's south-east corner and the Egyptian map's edge is filled (Sudanese land closed off by his red line; morphological
closing, land only). (2) V1's straight inland edges in Africa west of the Nile (the 20 E line through Libya, Libya's straight southern borders, the notch sides)
are roughened like the Version 420 border (fixed-seed noise, up to ~10 km); coasts are not touched. Kept inside V2. Run v386_areas_ellipsoid.py after."""
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
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
# (1) the notch
B = shapely.box(23.0, 18.5, 27.0, 22.5)
closed = V.intersection(B.buffer(1)).buffer(0.45, join_style=2).buffer(-0.45, join_style=2).intersection(B).intersection(LAND)
notch = closed.difference(V); print('   notch filled', round(A(notch)), 'km2')
V = unary_union([V, notch.buffer(0.002)]).buffer(0)
# (2) roughen inland edges in the box
BOX = shapely.box(17.5, 17.5, 27.5, 32.0)
SEA = shapely.box(10, 10, 40, 40).difference(LAND)
rng = np.random.default_rng(429)
def rough_ring(coords):
    ls = LineString(coords); L = ls.length; n = max(8, int(L / 0.015))
    pts = np.array([ls.interpolate(L * i / n).coords[0] for i in range(n)])
    def noise(sc, amp):
        k = max(2, n // sc); v = rng.normal(0, 1, k + 3); u = np.linspace(0, k, n, endpoint=False); i = u.astype(int); f = u - i; f = f * f * (3 - 2 * f)
        return amp * (v[i] * (1 - f) + v[i + 1] * f)
    d = np.clip(noise(120, 0.05) + noise(40, 0.03) + noise(12, 0.015), -0.09, 0.09)
    ok = np.array([BOX.contains(Point(p)) and SEA.distance(Point(p)) > 0.15 for p in pts])
    # fade the noise in and out of the inland stretches
    from scipy.ndimage import uniform_filter1d
    w = uniform_filter1d(ok.astype(float), 15, mode='wrap'); d = d * w
    t = np.roll(pts, -1, 0) - np.roll(pts, 1, 0); nrm = np.stack([-t[:, 1], t[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    return pts + nrm * d[:, None]
out = []
for q in getattr(V, 'geoms', [V]):
    if q.intersects(BOX) and q.area > 1:
        ext = Polygon(rough_ring(list(q.exterior.coords)), [h.coords for h in q.interiors]).buffer(0)
        # keep the coast exact: outside BOX or near the sea, take the original
        ext = unary_union([ext.intersection(BOX).difference(SEA.buffer(0.15)), q.difference(BOX), q.intersection(SEA.buffer(0.15).buffer(0))]).buffer(0)
        out.append(ext)
    else: out.append(q)
X = unary_union(out).buffer(0)
X = unary_union([g for g in getattr(X, 'geoms', [X]) if A(g) > 2 or not BOX.contains(g)])
X = X.intersection(LAND.buffer(0.004)).intersection(V2.buffer(0.004))
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.005: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km, '| pieces', len(o))
Y = MP(o)
for n_, p in {'Benghazi': (20.07, 32.12), 'Kufra': (23.31, 24.2), 'Ajdabiya': (20.22, 30.76), 'Uweinat': (25.0, 21.9), 'Cairo': (31.24, 30.04)}.items(): print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
