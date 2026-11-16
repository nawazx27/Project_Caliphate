"""Version 468 (Nawaz, a red circle round V1's African piece below Egypt (Sudan, South Sudan, Eritrea, Djibouti, most of Ethiopia): "Expand it while
keeping its shape until you have the entire Ethiopian highlands included"). The piece (V1's African land south of 22 N, east of Libya) is enlarged as one
piece, the same shape, by one scale factor in every direction, about the corner where it leaves the Libya-Sudan border (25.06 E 20.0 N, fixed, as in
Version 434), by the SMALLEST factor that puts the whole Ethiopian Highlands inside V1 (Wikipedia: "little of its surface falling below 1500 m"; taken
as all land of Ethiopia and Eritrea at 1500 m or more, Mapzen terrain tiles zoom 6, smoothed as in tools/v464; DEM env = tools/dem_fetch.py .npz).
The enlarged piece is cut to African land (the Red Sea, the Gulf of Aden and Arabia stay as they are) and joined to V1; enclosed pockets filled.
DIR env = project dir; SCALE env overrides the factor. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, shapely.affinity, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from rasterio.features import shapes
from rasterio.transform import Affine
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
# ---- the Ethiopian Highlands (as tools/v464)
D = np.load(os.environ['DEM']); h = D['h']; z = int(D['z']); x0 = int(D['x0']); y0 = int(D['y0']); ts = int(D['ts']); N = 2 ** z * ts
mask = (h >= 1500).astype(np.uint8); polys = []
def conv(ring):
    return [((x0 * ts + X) / N * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y0 * ts + Y) / N))))) for X, Y in ring]
for g, v in shapes(mask, mask=mask.astype(bool), transform=Affine.identity()):
    polys.append(Polygon(conv(g['coordinates'][0]), [conv(r) for r in g['coordinates'][1:]]))
EE = unary_union([G['Ethiopia'], G['Eritrea']])
HI = unary_union(polys).buffer(0).intersection(EE).buffer(0.12).buffer(-0.12).buffer(-0.06).buffer(0.06)
HI = unary_union([Polygon(q.exterior) for q in getattr(HI, 'geoms', [HI]) if A(q) > 1500]).intersection(EE).buffer(0)
print('Ethiopian Highlands', round(A(HI)), 'km2')
# ---- V1 and its African piece
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ASIA = {'Yemen', 'Saudi Arabia', 'Oman', 'Israel', 'Palestine', 'Jordan'}
AFL = unary_union([g for n_, g in G.items() if n_ not in ASIA and g.intersects(shapely.box(12, -8, 52, 23))]).buffer(0)   # African land round it
B = V.intersection(shapely.box(24.98, -5, 52, 22.0)).intersection(AFL)
Cc = (25.062, 20.006)
def grow(s):
    BS = shapely.affinity.scale(B, s, s, origin=Cc).intersection(AFL)
    return unary_union([V, BS]).buffer(0)
miss = lambda X: A(HI.difference(X.buffer(0.002))) if not HI.difference(X.buffer(0.002)).is_empty else 0
print('highlands outside V1 now', round(miss(V)), 'km2')
if os.environ.get('SCALE'): s = float(os.environ['SCALE'])
else:
    lo, hi = 1.0, 2.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if miss(grow(mid)) < 1: hi = mid
        else: lo = mid
    s = hi
X = grow(s); print('scale', round(s, 4), '| highlands outside after', round(miss(X), 1), 'km2')
X = unary_union([X] + [Polygon(hh) for q in getattr(X, 'geoms', [X]) for hh in q.interiors if A(Polygon(hh)) < 50000]).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or not (20 < q.centroid.x < 52 and q.centroid.y < 15)])
add = X.difference(V)
print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Chad', 'Central African Rep.', 'DR Congo', 'Uganda', 'Kenya', 'Ethiopia', 'Somaliland', 'Somalia', 'Eritrea', 'Djibouti'] if k in G and A(add.intersection(G[k])) > 50})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [hh for hh in q.interiors if A(Polygon(hh)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Jijiga': (42.8, 9.35), 'Hargeisa': (44.06, 9.56), 'Negele': (39.58, 5.33), 'Yabelo': (38.1, 4.88), 'Moyale': (39.05, 3.52), 'Lodwar (Kenya)': (35.6, 3.12),
              'Gulu (Uganda)': (32.3, 2.78), 'Birao (CAR)': (22.78, 10.28), 'Abeche (Chad)': (20.83, 13.83), 'Berbera': (45.0, 10.44)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
