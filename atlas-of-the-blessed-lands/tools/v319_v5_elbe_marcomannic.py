"""Version 319 (Nawaz: "Does v5 have all the lands that the Roman Empire ever held?" -> two gaps -> "Both and preview" -> "apply").
V5 (grm) takes (a) the Saale-Elbe land: all of Germany on the Roman side of the Elbe up to the Czech border (Halle, Leipzig,
Dessau, Dresden's old town); (b) the Marcomannic-war lands north of the Middle Danube: Lower Austria and Vienna whole, South Moravia,
and western Slovakia (Bratislava, Trnava, Nitra, Trencin regions). Pockets >=80% filled; V6 takes what it lacks."""
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
# (a) Germany split by the whole Elbe (Natural Earth, into Czechia)
ne = json.load(open(os.path.join(P, 'tools/data/v319_elbe.geojson')))['features']
elbe = unary_union([shape(f['geometry']) for f in ne if (f['properties'].get('name') or '') == 'Elbe'])
DE = G['276'][1]; parts = DE.difference(elbe.buffer(0.008)); parts = list(getattr(parts, 'geoms', [parts]))
west = [q for q in parts if q.contains(Point(12.37, 51.34))][0]
assert not west.contains(Point(13.4, 52.52)) and not west.contains(Point(10.0, 53.56)), 'Elbe does not split Germany'
west = west.buffer(0.0085).intersection(DE)
a_add = west.difference(V5); print('(a) Saale-Elbe land added', round(A(a_add)), 'km2')
# (b) Overture regions
rows = pq.read_table(os.path.join(P, 'tools/data/v319_cz_at_regions.parquet')).to_pylist() + pq.read_table(os.path.join(REPO, 'tools/data/v308_roman_ottoman_regions.parquet')).to_pylist()
pick = lambda r: r['subtype'] == 'region' and r['is_land'] is not False and r['region'] in ('AT-3', 'AT-9', 'CZ-64', 'SK-BL', 'SK-TA', 'SK-NI', 'SK-TC')
B = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if pick(r)])
b_add = B.difference(V5); print('(b) Marcomannic-war lands added', round(A(b_add)), 'km2')
X = unary_union([V5, west.buffer(0.002), B.buffer(0.003)]).buffer(0)
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
for n_, p in {'Halle': (11.97, 51.48), 'Leipzig': (12.37, 51.34), 'Dessau': (12.24, 51.83), 'Dresden old town': (13.74, 51.05), 'Dresden Neustadt (east bank)': (13.75, 51.07), 'Chemnitz': (12.92, 50.83), 'Berlin': (13.4, 52.52), 'Hamburg north': (10.0, 53.56), 'Stillfried': (16.85, 48.41), 'Musov': (16.6, 48.9), 'Brno': (16.61, 49.2), 'Trencin': (18.04, 48.89), 'Nitra': (18.09, 48.31), 'Bratislava old town': (17.11, 48.145), 'Zilina': (18.74, 49.22), 'Olomouc': (17.25, 49.59), 'Prague': (14.42, 50.08)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(unary_union([V, Y.buffer(0.003)]).buffer(0), 0.02)
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
