"""Version 302 (Nawaz: "revert back to the previous Grand Caliphate, and in v5 add Ukraine with entire Crimean Peninsula and all the
lands that the Roman Empire ever held and push").
1. V4 (sas) back to its Version 296 shape (no Italy / western Balkans of Version 301).
2. V5 (grm) + Ukraine (base map, whole) + the whole Crimean peninsula with Sevastopol (base-map land inside Overture's Crimea and
   Sevastopol regions) + the rest of Rome's lands: Germany between the Rhine and the Elbe (Augustus) and the whole Netherlands, taken
   from the Version 298 V4 (git 4595055) where it lies in Germany or the Netherlands, and Taman (Temryuk district; the Bosporan
   kingdom). Belgium, Luxembourg etc. were already in.
3. V6 (rom) and V7 (v2) take any part of the new V5 they lack, so each version stays inside the next.
Usage: python3 tools/v302_v5_ukraine_rome.py <Version 296 caliph.json> <Version 298 caliph.json> <crimea.pkl> <crim divs.parquet>"""
import json, os, sys, subprocess, pickle, shapely
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
C296 = json.load(open(sys.argv[1])); C298 = json.load(open(sys.argv[2]))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k, c=None: MultiPolygon([Polygon(r[0], r[1:]) for r in (c or C)[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def rows(Y, base):
    r = {x['id']: x for x in base}
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: r[k] = {'id': k, 'n': r.get(k, {}).get('n', n), 'km2': round(A(g)), 'pct': pct}
            elif k in r: r.pop(k)
    return sorted(r.values(), key=lambda x: -(x.get('km2') or 0) * (x.get('pct') or 100))
# 1
C['sas'] = C296['sas']; print('sas back to', C['sas']['km2'])
# 2
CB = box(32.3, 44.2, 36.8, 46.3)
land = shapely.union_all([g for n, g in G.values() if g.intersects(CB)])
crimea = shapely.union_all([wkb.loads(g).buffer(0) for c, n, g in pickle.load(open(sys.argv[3], 'rb'))]).intersection(land)
taman = shapely.union_all([wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[4]).to_pylist() if (r['names'] or {}).get('primary') == 'Темрюкский район'])
deNL = M('sas', C298).intersection(shapely.union_all([G['276'][1], G['528'][1]]).buffer(0.05))
print('Crimea km2', round(A(crimea)), 'Taman', round(A(taman)), 'Germany-to-Elbe + Netherlands', round(A(deNL)))
X = shapely.union_all([M('grm'), G['804'][1].buffer(0.003), crimea.buffer(0.003), taman.buffer(0.003), deNL]).buffer(0)
# pockets >=80% in Europe
win = box(-12, 40, 42, 58); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 1: continue
    t = q.exterior.intersection(XB).length / q.exterior.length
    if t >= 0.5 and A(q) > 300: print(' pocket %d km2 %.0f%% at %s' % (A(q), 100 * t, tuple(round(v, 1) for v in q.representative_point().coords[0])))
    if t >= 0.8: fill.append(q)
X = shapely.union_all([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X, 0.05); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': rows(Y, C['grm']['states'])}; print('grm', old, '->', C['grm']['km2'])
for n_, (x, y) in {'Kyiv': (30.52, 50.45), 'Simferopol': (34.1, 44.95), 'Sevastopol': (33.52, 44.6), 'Kerch': (36.47, 45.36), 'Taman': (36.72, 45.21), 'Cologne': (6.96, 50.94), 'Hamburg': (9.99, 53.55), 'Amsterdam': (4.9, 52.37)}.items(): print(' ', n_, Y.contains(Point(x, y)))
# 3
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
