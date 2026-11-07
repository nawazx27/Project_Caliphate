"""Version 320 (Nawaz: "Now, Does v5 have all the lands that the Roman Empire ever held?" -> only the Marcomannic-war marching camps at
Olomouc-Neredín and Hulín lay outside -> "Preview"). V5 (grm) takes the Olomouc and Zlín regions of Czechia, and (his red line, "Extend and make it follow the border of Czechia till Slovakia",
reference/v320_moravia_silesia_line.jpg) the Moravian-Silesian region with Ostrava, (Overture,
tools/data/v319_cz_at_regions.parquet). Pockets >=80% filled; V6 takes what it lacks."""
import json, os, sys, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); REPO = P
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
V5 = M('grm')
rows = pq.read_table(os.path.join(P, 'tools/data/v319_cz_at_regions.parquet')).to_pylist()
B = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['subtype'] == 'region' and r['is_land'] is not False and r['region'] in ('CZ-71', 'CZ-72', 'CZ-80')])   # + Moravian-Silesian region: his line along the Czech border to Slovakia
print('Olomouc, Zlin and Moravian-Silesian regions add', round(A(B.difference(V5))), 'km2; touch V5:', B.buffer(0.01).intersects(V5))
X = unary_union([V5, B.buffer(0.003)]).buffer(0)
win = box(5, 44, 25, 56); L = unary_union([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 0.5 or not q.intersects(box(9, 46, 21, 54)): continue
    if q.exterior.intersection(XB).length / q.exterior.length >= 0.8: fill.append(q)
X = unary_union([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('pockets filled', len(fill), round(sum(A(q) for q in fill)))
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
o = polys(X); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Olomouc-Neredin camp': (17.22, 49.6), 'Hulin camp': (17.46, 49.32), 'Zlin': (17.67, 49.22), 'Olomouc': (17.25, 49.59), 'Ostrava': (18.29, 49.82), 'Brno': (16.61, 49.2), 'Zilina': (18.74, 49.22)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(unary_union([V, Y.buffer(0.003)]).buffer(0), 0.02)
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
