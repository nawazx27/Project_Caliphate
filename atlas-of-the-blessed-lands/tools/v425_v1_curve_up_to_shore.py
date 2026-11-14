"""Version 425 (Nawaz, a red stroke on the Version 422 picture from the bottom of V1's rounded south-west bulge up to the Eritrean coast; read on the picture's
coastline fit as ~35.9 E 13.5 N to the shore near the Gulf of Zula ~39.8 E 15.1 N). V1's (shj) southern edge east of 35.5 E now follows that stroke as a natural,
slightly bowed and roughened curve rising to the shore; everything south of it (southern Eritrea with the Danakil coast and Assab, Tigray, the Djibouti tip) is
taken out, everything north of it to the coast is in (Asmara, Massawa). Run on the Version 424 V1. Then tools/v411_arabia.py and the ellipsoid tool."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
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
x0, y0, x1, y1 = 35.5, 13.0, 40.3, 15.15
t = np.linspace(0, 1, 300); x = x0 + (x1 - x0) * t
y = y0 + (y1 - y0) * t ** 1.35 - 0.12 * np.sin(np.pi * t)          # rises gently at first, then more steeply to the coast (a natural bow)
rng = np.random.default_rng(425)
def noise(sc, amp):
    k = max(2, len(x) // sc); v = rng.normal(0, 1, k + 3); u = np.linspace(0, k, len(x)); i = np.minimum(u.astype(int), k + 1); f = u - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
d = np.clip(noise(25, 0.05) + noise(8, 0.03) + noise(3, 0.012), -0.09, 0.09); d[:10] *= np.linspace(0, 1, 10); y = y + d
SOUTH = Polygon(list(zip(x, y)) + [(44.5, y1), (44.5, 5.0), (x0, 5.0)]).buffer(0)
X = V.difference(SOUTH)
NORTH = LAND.intersection(Polygon(list(zip(x, y)) + [(x1, 18.5), (x0, 18.5)]).buffer(0)).intersection(unary_union([G['Eritrea'], G['Sudan'], G['Ethiopia']]))
X = unary_union([X, NORTH.buffer(0.003)]).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or q.centroid.x < 35])   # drop crumbs south of the line
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
for n_, p in {'Asmara': (38.93, 15.32), 'Massawa': (39.45, 15.61), 'Keren': (38.46, 15.78), 'Kassala': (36.4, 15.45), 'Gedaref': (35.38, 14.03), 'Assab (out)': (42.74, 13.01), 'Mekelle (out)': (39.47, 13.5), 'Axum (out)': (38.72, 14.13)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
