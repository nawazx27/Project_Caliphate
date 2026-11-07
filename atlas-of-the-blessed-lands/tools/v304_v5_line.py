"""Version 304 (Nawaz, screenshot of the V5 + Ukraine preview with a red line from the Saar to Ukraine's NW corner and Crimea circled:
"Revert back to this and fill that gap and add crimea").
V5 (grm) = Version 300 V5 (git feab197; no Germany/Netherlands, Belgium in) + Ukraine (base map) + Crimea (Crimea + Sevastopol regions,
land) + every district at least half south of his red line (tools/v304_build/redline304.json, read off the screenshot with the page's
own projection): German Kreise (south Germany: Saarland, Rhineland-Palatinate south, Baden-Wurttemberg, Bavaria, Thuringia/Saxony
south), Czech and Polish powiaty, Belarus raions; pockets >=80% filled. No Taman, no Netherlands, no northern Germany.
V6 (rom) and V7 (v2) take any V5 land they lack.
Usage: python3 tools/v304_v5_line.py <V300 caliph.json> <crimea.pkl> <DE/NL counties parquet> <PL/CZ/BY counties parquet>"""
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
C300 = json.load(open(sys.argv[1])); F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
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
L = json.load(open(os.path.join(P, 'tools/v304_build/redline304.json')))
south = Polygon([(L[0][0] - 0.3, L[0][1])] + L + [(L[-1][0] + 0.5, L[-1][1]), (L[-1][0] + 0.5, 46), (L[0][0] - 0.3, 46)]).buffer(0)
CB = box(32.3, 44.2, 36.8, 46.3)
land = shapely.union_all([g for n, g in G.values() if g.intersects(CB)])
crimea = shapely.union_all([wkb.loads(g).buffer(0) for c, n, g in pickle.load(open(sys.argv[2], 'rb'))]).intersection(land)
base = M('grm', C300)
add = [G['804'][1], crimea]; names = []
for pth in sys.argv[3:5]:
    for r in pq.read_table(pth).to_pylist():
        if r.get('subtype') not in (None, 'county') or r['country'] in ('NL', 'FR', 'LU'): continue
        g = wkb.loads(r['geometry']).buffer(0)
        if not g.intersects(south) or g.area == 0: continue
        if g.intersection(south).area / g.area >= 0.5: add.append(g); names.append(r['country'])
import collections; print('districts south of the line:', dict(collections.Counter(names)))
X = shapely.union_all([base] + [g.buffer(0.003) for g in add]).buffer(0)
win = box(-12, 40, 42, 58); Lnd = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = Lnd.difference(X); XB = X.buffer(0.05); fill = []
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
for n_, (x, y) in {'Munich': (11.58, 48.14), 'Stuttgart': (9.18, 48.78), 'Nuremberg': (11.08, 49.45), 'Frankfurt': (8.68, 50.11), 'Cologne': (6.96, 50.94), 'Dresden': (13.74, 51.05), 'Prague': (14.42, 50.08), 'Krakow': (19.94, 50.06), 'Wroclaw': (17.03, 51.11), 'Warsaw': (21.01, 52.23), 'Lublin': (22.57, 51.25), 'Kyiv': (30.52, 50.45), 'Simferopol': (34.1, 44.95), 'Taman': (36.72, 45.21), 'Amsterdam': (4.9, 52.37)}.items(): print(' ', n_, Y.contains(Point(x, y)))
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
