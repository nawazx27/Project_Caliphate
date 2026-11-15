"""Version 436 (Nawaz: "Push the piece a bit downward", then "I meant this piece": a red circle round the whole bottom of V1 in Africa, Darfur and
Kordofan, the South Sudan part and the Ethiopian lobe, from about 15 N down). That piece is pushed straight down by DY degrees (env, default 0.75, about
83 km), shape kept: every point below 12.5 N goes down by DY, easing to nothing at 14.5 N (where the piece joins the rest of V1) and at the tip by
Djibouti (so the tip stays on the coast); a straight-down push keeps every bend of the edges, and nothing is swept, so no straight lines appear.
Only African land is moved and taken (Arabia is not touched). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
DY = float(os.environ.get('DY', '0.75')); Y0, Y1, XT = 14.5, 12.5, 42.92
AFR = unary_union([G[k] for k in ['Sudan', 'South Sudan', 'Ethiopia', 'Eritrea', 'Djibouti', 'Chad', 'Central African Rep.', 'Egypt', 'Libya']])
piece = V.intersection(AFR).intersection(box(15, 0, XT, Y0 + 0.01))
ss = lambda t: t * t * (3 - 2 * t)
def shift(x, y):
    v = ss(np.clip((Y0 - y) / (Y0 - Y1), 0, 1)); w = ss(np.clip((XT - x) / 2.2, 0, 1))
    return DY * v * w
moved = shapely.transform(piece.segmentize(0.02), lambda c: np.c_[c[:, 0], c[:, 1] - shift(c[:, 0], c[:, 1])]).buffer(0)
TAKE = unary_union([G[k] for k in ['Sudan', 'South Sudan', 'Ethiopia', 'Eritrea', 'Djibouti', 'Chad', 'Central African Rep.']])
X = unary_union([V, moved.intersection(TAKE).buffer(0.003).intersection(TAKE.buffer(0.003))]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 20]
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
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2', {k: round(A(NEW.intersection(G[k]))) for k in ['South Sudan', 'Ethiopia', 'Central African Rep.', 'Chad', 'Somaliland', 'Kenya', 'Uganda']})
for n_, p in {'Addis Ababa': (38.75, 9.03), 'Adama': (39.27, 8.54), 'Jimma': (36.83, 7.67), 'Hawassa': (38.48, 7.05), 'Gambela': (34.58, 8.25), 'Malakal': (31.66, 9.53), 'Bentiu': (29.8, 9.23),
              'Aweil': (27.4, 8.77), 'Wau': (28.0, 7.7), 'Bor': (31.56, 6.21), 'Birao (CAR)': (22.78, 10.28), 'Dire Dawa': (41.86, 9.6), 'Harar': (42.12, 9.31)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
