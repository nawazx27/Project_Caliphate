"""Version 307 (Nawaz, of Version 306: "I don't like this shape", then the Ottoman 1683 map again: "I want this shape... the shape of
dark red shaded region"). V5 (grm) = V5 of Version 305 (the Roman map) + the land inside the drawn Ottoman empire, its outer line
traced from the map (tools/v307_build: fit.py control-point fit, trace.py -> tools/data/v307_ottoman_map_shape.geojson),
plus his red line from the Don to the Kuban corner (tools/v307_build/redline307.json, read off his screenshot).
The whole-region additions of Version 306 are dropped. Pockets >=80% surrounded are filled. V6 (rom) and V7 (v2) go back to their
Version 305 shapes and take any V5 land they lack.
Usage: python3 tools/v307_v5_ottoman_map.py <caliph.json of Version 305, from: git show a79f13e~1:./src/caliph.json>"""
import json, os, sys, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
OLD = json.load(open(sys.argv[1])); F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for key in ['grm', 'rom', 'v2']: C[key] = OLD[key]
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
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
O = shape(json.load(open(os.path.join(P, 'tools/data/v307_ottoman_map_shape.geojson')))['geometry'])
win = box(10, 34, 56, 56); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
T = O.intersection(L); V5 = M('grm')
T = shapely.union_all([q for q in getattr(T, 'geoms', [T]) if q.geom_type == 'Polygon' and (A(q) > 200 or q.distance(V5) < 0.05)])
X = shapely.union_all([V5, T.buffer(0.003)]).buffer(0)
# his red line on the Version 307 preview: the border runs from where it meets the Don straight down to the Kuban corner
RL = Polygon(json.load(open(os.path.join(P, 'tools/v307_build/redline307.json')))['ring']).buffer(0).intersection(L)
print('red line adds', round(A(RL.difference(X))), 'km2'); X = shapely.union_all([X, RL.buffer(0.003)]).buffer(0)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 1: continue
    t = q.exterior.intersection(XB).length / q.exterior.length
    if t >= 0.5 and A(q) > 300: print(' pocket %d km2 %.0f%% at %s' % (A(q), 100 * t, tuple(round(v, 1) for v in q.representative_point().coords[0])))
    if t >= 0.8: fill.append(q)
X = shapely.union_all([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X, 0.05); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, (x, y) in {'Vienna': (16.37, 48.21), 'Bratislava': (17.11, 48.15), 'Budapest': (19.04, 47.5), 'Kosice': (21.26, 48.72), 'Lviv': (24.03, 49.84), 'Kamianets': (26.58, 48.68), 'Vinnytsia': (28.47, 49.23), 'Uman': (30.22, 48.75), 'Kyiv': (30.52, 50.45), 'Dnipro': (35.05, 48.46), 'Odesa': (30.73, 46.48), 'Zaporizhzhia': (35.14, 47.84), 'Simferopol': (34.1, 44.95), 'Donetsk': (37.8, 48.0), 'Rostov': (39.72, 47.24), 'Krasnodar': (38.98, 45.04), 'Stavropol': (41.97, 45.04), 'Elista': (44.27, 46.31), 'Makhachkala': (47.5, 42.98), 'Astrakhan': (48.03, 46.35), 'Baku': (49.87, 40.41)}.items(): print(' ', n_, Y.contains(Point(x, y)))
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
