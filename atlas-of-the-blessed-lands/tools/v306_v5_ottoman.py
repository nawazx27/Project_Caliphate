"""Version 306 (Nawaz, with a schematic map of the Ottoman Empire at its height, 1683: "It should look like this").
The map is a stylised drawing (coastlines cannot be fitted: median 5 px off after fitting), so its lands are taken as the real
Ottoman provinces and vassal lands it shows, whole, and ADDED to V5 (grm) on top of the Roman map of Version 305:
Hungary (base map; Budapest in, Vienna out); Podolia (Khmelnytskyi, Vinnytsia, Ternopil oblasts); Yedisan and the north Black Sea
coast (Odesa, Mykolaiv, Kherson, Zaporizhzhia oblasts); Crimea and Sevastopol; the Azov shore to Azak (Mariupol and Kalmiuskyi raions,
Neklinovsky raion, Taganrog, Azov city and raion); Kuban (Krasnodar Krai, Adygea). Overture 2026-10-21.0 shapes saved in
tools/data/v306_ottoman_regions.parquet. Pockets >=80% filled. V6 (rom) and V7 (v2) take any V5 land they lack.
Run after tools/v305_v5_roman_map.py."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
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
def polys(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
regs = [wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(P, 'tools/data/v306_ottoman_regions.parquet')).to_pylist()]
CB = box(32, 44, 37, 46.5); land = shapely.union_all([g for n, g in G.values() if g.intersects(CB)])
regs = [g.intersection(land) if g.intersects(CB) else g for g in regs]   # Crimea/Sevastopol regions to land
X = shapely.union_all([M('grm'), G['348'][1].buffer(0.003)] + [g.buffer(0.003) for g in regs]).buffer(0)
win = box(10, 40, 50, 55); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
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
for n_, (x, y) in {'Vienna': (16.37, 48.21), 'Budapest': (19.04, 47.5), 'Kamianets': (26.58, 48.68), 'Vinnytsia': (28.47, 49.23), 'Odesa': (30.73, 46.48), 'Simferopol': (34.1, 44.95), 'Azov': (39.42, 47.11), 'Krasnodar': (38.98, 45.04), 'Kyiv': (30.52, 50.45), 'Baku': (49.87, 40.41)}.items(): print(' ', n_, Y.contains(Point(x, y)))
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
