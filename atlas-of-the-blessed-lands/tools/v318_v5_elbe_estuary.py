"""Version 318 (Nawaz circled the Elbe mouth on Version 317: "Fill this gap to the shore"). V5 (grm) takes the water of the Elbe estuary
from Cuxhaven to Hamburg-Wedel (8.94-9.85 E) up to its north shore, so the whole mouth of the frontier river is inside; the small square of
north-bank land at the mouth that Version 317's box cut out is taken out again. V6 (v2) takes any V5 land it lacks."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
from shapely.geometry import box
EB = box(8.94, 53.50, 9.85, 53.93)
Lb = shapely.union_all([g for n, g in G.values() if g.intersects(EB.buffer(0.3))])
water = EB.difference(Lb)
B5 = shapely.union_all([q for q in getattr(water, 'geoms', [water]) if q.area > 1e-4])     # the estuary between the two shores
north = [q for q in getattr(Lb, 'geoms', [Lb]) if q.contains(Point(9.4, 53.95))][0]          # Schleswig-Holstein, the north bank
V5 = M('grm'); print('adds', round(A(B5.difference(V5))), 'km2')
X = shapely.union_all([V5, B5.buffer(0.003)]).buffer(0)
sq = X.intersection(north).intersection(box(8.8, 53.86, 9.1, 54.1)); print('north-bank square removed', round(A(sq), 1), 'km2')
X = X.difference(north.intersection(box(8.8, 53.86, 9.1, 54.1)).buffer(0.002)).buffer(0)
o = polys(X); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Elbe mid-estuary': (9.2, 53.82), 'Brunsbuettel (north bank)': (9.14, 53.9), 'Cuxhaven': (8.69, 53.86), 'Stade': (9.48, 53.6), 'Glueckstadt (north bank)': (9.42, 53.79)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0), 0.02)
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
