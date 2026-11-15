"""Version 440 (Nawaz: "Make sure v1 has the entire historic farmland of the Middle East"). The one great historic farmland still outside V1 (shj) was
Persia beyond Khuzestan (the Caspian lowlands of Gilan and Mazandaran, Iranian Azerbaijan, the Zagros valleys, Isfahan, Fars, the Khurasan oases of
Nishapur and Mashhad, Sistan). V1 takes Iran whole with its islands; Iran's borders with Afghanistan, Pakistan, Turkmenistan, Azerbaijan, Armenia and
Turkiye become V1's edge (no long straight stretches on them). Iran lies inside V2. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
CTRY = os.environ.get('CTRY', 'Iran')
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
X = unary_union([V, G[CTRY].buffer(0.003).intersection(V2.buffer(0.002))]).buffer(0)
EXTRA = os.environ.get('EXTRA')   # optional "x0,y0,x1,y1" box of land to fill (a pocket left between the new land and V1)
if EXTRA:
    b = [float(t) for t in EXTRA.split(',')]
    pocket = X.buffer(0.45).buffer(-0.45).difference(X).intersection(shapely.box(*b)).intersection(G['Ethiopia'])
    print('   pocket filled', round(A(pocket)), 'km2'); X = unary_union([X, pocket.buffer(0.003)]).buffer(0)
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
    g_ = G[f['properties']['n']]
    if g_.area and g_.intersects(Y):
        pct = round(100 * g_.intersection(Y).area / g_.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g_)), 'pct': pct})
old = C['shj']['km2']; NEW = Y.difference(V)
C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| added', round(A(NEW)), 'km2 | country inside', round(100 * G[CTRY].intersection(Y).area / G[CTRY].area, 2), '%')
for n_, p in {'Tehran': (51.39, 35.69), 'Rasht': (49.58, 37.28), 'Sari': (53.06, 36.56), 'Tabriz': (46.29, 38.08), 'Isfahan': (51.67, 32.65), 'Shiraz': (52.53, 29.59), 'Mashhad': (59.6, 36.3), 'Nishapur': (58.8, 36.21), 'Zabol (Sistan)': (61.49, 31.03), 'Bandar Abbas': (56.27, 27.18), 'Qeshm': (55.9, 26.8)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
