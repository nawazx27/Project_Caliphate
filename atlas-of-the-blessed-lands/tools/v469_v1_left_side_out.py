"""Version 469 (Nawaz, on the Version 468 preview: "Good now expand its left side"). V1's African piece (south of 20 N, east of 20 E: Darfur, Kordofan,
South Sudan ...) is widened westward in its own shape: every point is pushed west, away from the piece's east side (44 E), by a factor that is 1 at the
corner where the left side starts (25.06 E 20.0 N) and reaches WEST (default 1.10, i.e. the Darfur edge moves ~2 deg, ~220 km west) from 3 deg south of it,
eased in between (no straight joint). The left side keeps all its bends; the widened piece is cut to African land and joined to V1; enclosed pockets
filled. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union, transform
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ASIA = {'Yemen', 'Saudi Arabia', 'Oman', 'Israel', 'Palestine', 'Jordan'}
AFL = unary_union([g for n_, g in G.items() if n_ not in ASIA and g.intersects(shapely.box(5, -8, 52, 23))]).buffer(0)
B = V.intersection(shapely.box(20, -6, 52, 20.006)).intersection(AFL).buffer(0)
XA, Y0, W = 44.0, 20.006, float(os.environ.get('WEST', '1.10'))
def f(x, y, z=None):
    x = np.asarray(x); y = np.asarray(y); t = np.clip((Y0 - y) / 3.0, 0, 1); t = t * t * (3 - 2 * t)
    return XA - (XA - x) * (1 + (W - 1) * t), y
BS = transform(f, shapely.segmentize(B, 0.02)).buffer(0).intersection(AFL)
X = unary_union([V, BS]).buffer(0)
X = unary_union([X] + [Polygon(hh) for q in getattr(X, 'geoms', [X]) for hh in q.interiors if A(Polygon(hh)) < 50000]).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or not (15 < q.centroid.x < 52 and q.centroid.y < 15)])
add = X.difference(V)
print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Chad', 'Libya', 'Central African Rep.', 'DR Congo', 'Uganda', 'Sudan', 'South Sudan', 'Cameroon'] if k in G and A(add.intersection(G[k])) > 50})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [hh for hh in q.interiors if A(Polygon(hh)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Abeche (Chad)': (20.83, 13.83), 'Adre (Chad)': (22.2, 13.47), 'Birao (CAR)': (22.78, 10.28), 'Ndele (CAR)': (20.65, 8.41), 'Bangassou (CAR)': (22.8, 4.74), 'Faya (Chad)': (19.1, 17.9)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
