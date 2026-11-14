"""Version 424 (Nawaz: "Just drag the last part out to the shore entirely" ... "Not in a straight line, but take its natural curve and drag it to the shore").
V1's (shj) southern edge east of the Egyptian Empire map's own south edge (which curves down to ~12.97 N at 35-36 E) no longer runs as the straight 12.95 N cut
of Version 422: the map's gentle curve is carried on east, sagging a little (~12.4 N near 40 E) and rising to the Bab el-Mandeb shore (Ras Siyyan, 43.32 E 12.48 N),
roughened like the Version 420 border. Land above it (Eritrea, the Ethiopian/Djiboutian strip) is in, land below out. Then rerun tools/v411_arabia.py and the ellipsoid tool."""
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
x = np.linspace(36.0, 43.32, 400)
t = (x - 36.0) / (43.32 - 36.0)
y = 12.97 + (12.48 - 12.97) * t - 0.42 * np.sin(np.pi * t)          # a smooth sag between the two ends
rng = np.random.default_rng(424)
def noise(sc, amp):
    k = max(2, len(x) // sc); v = rng.normal(0, 1, k + 3); u = np.linspace(0, k, len(x)); i = np.minimum(u.astype(int), k + 1); f = u - i; f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
d = np.clip(noise(30, 0.06) + noise(10, 0.035) + noise(4, 0.015), -0.1, 0.1); d[:12] *= np.linspace(0, 1, 12); d[-12:] *= np.linspace(1, 0, 12); y = y + d
ABOVE = Polygon(list(zip(x, y)) + [(44.5, 12.48), (44.5, 18.5), (36.0, 18.5)]).buffer(0)
BOX = shapely.box(36.0, 9.0, 44.5, 18.5)
keep = V.difference(BOX)
inside = LAND.intersection(ABOVE).intersection(unary_union([V, G['Eritrea'], G['Ethiopia'], G['Djibouti'], G['Sudan']]))
X = unary_union([keep, inside.buffer(0.003)]).buffer(0)
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
for n_, p in {'Asmara': (38.93, 15.32), 'Assab': (42.74, 13.01), 'Ras Siyyan (shore)': (43.3, 12.5), 'Gondar (out)': (37.47, 12.6), 'Lalibela (out)': (39.05, 12.03), 'Djibouti city (out)': (43.15, 11.59)}.items():
    print('  ', n_, Y.contains(Point(p)) or Y.distance(Point(p)) < 0.03)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
