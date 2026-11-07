"""Version 308, step 1 (Nawaz: "Does it have all the lands that the Roman Empire and the Ottoman Empire held?" -> "Preview").
V5 (grm) += every land Rome or the Ottomans held that V5 still lacked, as whole regions (Overture 2026-10-21.0, fetched by fetch.py,
saved as tools/data/v308_roman_ottoman_regions.parquet): Vienna, Bruck an der Leitha (Carnuntum), Bratislava and Slovakia but Zilina and
Trencin (Upper Hungary under Thokoly), Zakarpattia, Regensburg with Landkreis Regensburg and Kelheim, Stirling, Clackmannanshire, Fife,
Perth and Kinross, Dundee, Angus, the Farasan Islands, Ternopil, Khmelnytskyi, Vinnytsia, Kirovohrad, Cherkasy west of the Dnieper,
and the north Caucasus republics with Stavropol; plus his circled dip (DIP=tools/v308_build/dip308.json). Pockets >=80% filled.
Usage: python3 add_regions.py <atlas dir> <regions parquet>  (step 2, caucasus.py, then redraws the Caucasus)."""
import json, os, sys, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = sys.argv[1]; REG = sys.argv[2]
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
rows = pq.read_table(REG).to_pylist() + (pq.read_table(sys.argv[3]).to_pylist() if len(sys.argv) > 3 else [])
def pick(r):
    c, rg, sub, n = r['country'], r['region'], r['subtype'], r['name'] or ''
    if c == 'RU' and sub == 'county': return n in ('Азовский район', 'городской округ Азов', 'городской округ Батайск', 'Кагальницкий район', 'Зерноградский район', 'Песчанокопский район', 'Целинский район', 'Егорлыкский район', 'Сальский район')   # Rostov land south of the Don and Manych (Nogai, under Crimea)
    if sub == 'region': return c in ('RU', 'AT') or (c == 'UA' and rg != 'UA-71') or (c == 'SK' and rg not in ('SK-ZI', 'SK-TC'))
    if c == 'UA': return 'Золотоні' not in n and 'Zolotono' not in n
    if c == 'AT': return 'Bruck an der Leitha' in n
    if c == 'DE': return n in ('Regensburg', 'Landkreis Regensburg', 'Landkreis Kelheim')   # Castra Regina and the Danube land joining it to V5
    if c == 'GB': return n in ('Perth and Kinross', 'Fife', 'Angus', 'Dundee City', 'Stirling', 'Clackmannanshire', 'Dundee')
    if c == 'SA': return 'Farasan' in n or 'فرسان' in n
    return False
sel = [r for r in rows if pick(r) and r['is_land'] is not False]
for r in sel: print(' +', r['country'], r['subtype'], r['region'], r['name'], round(A(shapely.from_wkb(r['geometry']))))
win = box(-10, 10, 56, 60); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
add = shapely.union_all([shapely.from_wkb(r['geometry']).buffer(0) for r in sel])
V5 = M('grm'); isl = shapely.union_all([shapely.from_wkb(r['geometry']).buffer(0) for r in sel if r['country'] == 'SA' and r['is_land']])   # Farasan: not on the base map's land, keep its own shape
add = shapely.union_all([add.intersection(L.buffer(0.02)), isl])
if os.environ.get('DIP'):   # his circled dip between the Don-Kuban line and Stavropol, closed at his earlier red line
    add = shapely.union_all([add, Polygon(json.load(open(os.environ['DIP']))['ring']).buffer(0).intersection(L)])
print('new land', round(A(add.difference(V5))))
X = shapely.union_all([V5, add.buffer(0.003)]).buffer(0)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 1: continue
    t = q.exterior.intersection(XB).length / q.exterior.length
    if t >= 0.5 and A(q) > 300: print(' pocket %d km2 %.0f%% at %s' % (A(q), 100 * t, tuple(round(v, 1) for v in q.representative_point().coords[0])))
    if t >= 0.8: fill.append(q)
X = shapely.union_all([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X, 0.05); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
T = {'Vienna': (16.37, 48.21), 'Carnuntum': (16.86, 48.11), 'Bratislava': (17.11, 48.15), 'Regensburg': (12.1, 49.02), 'Inchtuthil': (-3.43, 56.54), 'Farasan': (41.85, 16.7),
     'Ternopil': (25.6, 49.55), 'Buchach': (25.39, 49.06), 'Khmelnytskyi': (27.0, 49.42), 'Uman': (30.22, 48.75), 'Chyhyryn': (32.66, 49.08), 'Kyiv': (30.52, 50.45), 'Kosice': (21.26, 48.72), 'Uzhhorod': (22.29, 48.62),
     'Stavropol': (41.97, 45.04), 'Nalchik': (43.61, 43.49), 'Grozny': (45.7, 43.32), 'Makhachkala': (47.5, 42.98), 'Ochakiv': (31.54, 46.61), 'Dnipro': (35.05, 48.46), 'Zilina': (18.74, 49.22)}
for n_, p in T.items(): print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1))
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
