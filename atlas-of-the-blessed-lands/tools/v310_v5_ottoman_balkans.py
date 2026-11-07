"""Version 310 (Nawaz: "Go for this balkans shape", then the full 1683 Ottoman map: "Just use this balkans shape").
In the Balkans and Danube lands (Slovenia, Croatia, Bosnia, Serbia, Montenegro, Kosovo, North Macedonia, Albania, Bulgaria, Greece,
Romania, Moldova, Hungary, Slovakia, and Zakarpattia) V5 (grm) is the land inside the empire traced from that map
(tools/v310_build: fit.py on its European cities, trace.py -> tools/data/v310_ottoman_full_map_shape.geojson), plus whatever of V4
lies there (V4 must stay inside V5). Elsewhere V5 is unchanged. Holes the redraw leaves inside V5 are filled; pockets >=80% filled.
Run on the Version 309 caliph.json."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
IDS = ['705', '191', '070', '688', '499', 'KOS', '807', '008', '100', '300', '642', '498', '348', '703']
zak = [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(P, 'tools/data/v308_roman_ottoman_regions.parquet')).to_pylist() if r['region'] == 'UA-21' and r['subtype'] == 'region' and r['is_land'] is not False]
R = shapely.union_all([G[i][1].buffer(0.02) for i in IDS] + [z.buffer(0.02) for z in zak]).buffer(0)
win = box(5, 30, 45, 55); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
O = shape(json.load(open(os.path.join(P, 'tools/data/v310_ottoman_full_map_shape.geojson')))['geometry']).buffer(0)
Yp, V4 = M('grm'), M('sas')
NEW = shapely.union_all([O.intersection(L).intersection(R), V4.intersection(R)])
print('in the Balkans: removed', round(A(Yp.intersection(R).difference(NEW))), 'added', round(A(NEW.difference(Yp))), '; of it kept for V4', round(A(V4.intersection(R).difference(O))))
keep = []
for q in getattr(Yp, 'geoms', [Yp]):
    if not q.intersects(R): keep.append(q); continue
    d = q.difference(R); keep += [s for s in getattr(d, 'geoms', [d]) if s.geom_type == 'Polygon' and A(s) > 100]
X = shapely.union_all(keep + [NEW.buffer(0.003)]).buffer(0)
X = shapely.union_all([Polygon(q.exterior, [h for h in q.interiors if not Polygon(h).intersects(R)]) for q in getattr(X, 'geoms', [X])]).buffer(0)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 1 or not q.intersects(R): continue
    if q.exterior.intersection(XB).length / q.exterior.length >= 0.8: fill.append(q)
X = shapely.union_all([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('filled', len(fill), round(sum(A(q) for q in fill)))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
X = shapely.set_precision(X, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
for n, p in {'Vienna': (16.37, 48.21), 'Bratislava': (17.11, 48.15), 'Budapest': (19.04, 47.5), 'Kosice': (21.26, 48.72), 'Uzhhorod': (22.29, 48.62), 'Ljubljana': (14.51, 46.05), 'Zagreb': (15.98, 45.81), 'Rijeka': (14.44, 45.33), 'Split': (16.44, 43.51), 'Dubrovnik': (18.09, 42.65), 'Sarajevo': (18.41, 43.86), 'Osijek': (18.69, 45.55), 'Kotor': (18.77, 42.42), 'Durres': (19.45, 41.32), 'Corfu': (19.92, 39.62), 'Cluj': (23.6, 46.77), 'Chisinau': (28.86, 47.0), 'Crete': (24.9, 35.2)}.items(): print(' ', n, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
