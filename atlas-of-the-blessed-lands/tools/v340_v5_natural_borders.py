"""Version 340 PREVIEW (Nawaz: "Does the Roman Empire in V5 have the optimal natural borders?" -> "Preview the entire Roman Empire
with natural borders"). V5 (grm) closes its three weak spots onto natural lines; nothing is removed:
 1. Bohemia: all of Czechia, so the border runs on the Ore Mountains, the Sudetes and the Bohemian Forest.
 2. Transcarpathia (Zakarpattia oblast): the border runs on the Carpathian crest.
 3. The Bug-Dnieper gap: Kirovohrad oblast and the right (west) bank of Dnipropetrovsk oblast, so the border reaches the Dnieper.
 4. The Kuban steppe: the Kuma-Manych depression from the Sea of Azov to the Caspian (the Don below Rostov, the Manych, the Kuma):
    Krasnodar Krai, Adygea, Stavropol Krai, Karachay-Cherkessia, Kabardino-Balkaria, North Ossetia, Ingushetia, Chechnya,
    Dagestan and the Rostov districts south of the Don and the Manych.
Overture 2026-10-21.0 divisions (tools/data/v340_natural_regions.parquet); Dnieper from Natural Earth 10m (tools/data/v340_rivers.geojson).
Pockets of foreign land >=80% enclosed in the steppe windows are filled."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box, LineString
from shapely.ops import unary_union, split
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
rows = pq.read_table(os.path.join(P, 'tools/data/v340_natural_regions.parquet')).to_pylist()
g = lambda r: shapely.from_wkb(r['geometry']).buffer(0)
REG = lambda codes: unary_union([g(r) for r in rows if r['subtype'] == 'region' and r['region'] in codes])
CZ = unary_union([g(r) for r in rows if r['subtype'] == 'country' and r['country'] == 'CZ'])
ZK = REG({'UA-21'})
KR = REG({'UA-35'})
dn = [shape(f['geometry']) for f in json.load(open(os.path.join(P, 'tools/data/v340_rivers.geojson')))['features'] if f['properties']['name'] == 'Dnipro'][0]
DP = REG({'UA-12'}); parts = split(DP, dn)
DPW = unary_union([q for q in parts.geoms if q.representative_point().x < 35.2 and Point(q.representative_point()).distance(Point(34.0, 48.0)) < Point(q.representative_point()).distance(Point(36.0, 48.6))])   # the pieces on the right (west) bank
NC = REG({'RU-KDA', 'RU-AD', 'RU-STA', 'RU-KC', 'RU-KB', 'RU-SE', 'RU-IN', 'RU-CE', 'RU-DA'})
SOUTH_ROS = {'Азовский район', 'Кагальницкий район', 'Зерноградский район', 'Егорлыкский район', 'Целинский район', 'Сальский район',
             'Песчанокопский район', 'городской округ Батайск', 'городской округ Азов'}
RS = unary_union([g(r) for r in rows if r['subtype'] == 'county' and r['name'] in SOUTH_ROS])
V5 = M('grm')
for n, x in [('Czechia (Bohemia)', CZ), ('Transcarpathia', ZK), ('Kirovohrad', KR), ('Dnipropetrovsk right bank', DPW), ('North Caucasus to the Kuma-Manych', NC), ('Rostov south of the Don and Manych', RS)]:
    print(n, 'adds', round(A(x.difference(V5))), 'km2')
X = unary_union([V5] + [x.buffer(0.003) for x in (CZ, ZK, KR, DPW, NC, RS)]).buffer(0)
fills = 0
for win in [box(29, 46, 37, 50.5), box(36, 43, 48, 48.5), box(12, 48, 19.5, 51.5), box(21.5, 47.5, 25.5, 49.5)]:
    L = unary_union([gg for n, gg in G.values() if gg.intersects(win)]).intersection(win)
    rest = L.difference(X); XB = X.buffer(0.05); fill = []
    for q in getattr(rest, 'geoms', [rest]):
        if A(q) < 0.5: continue
        if q.exterior.intersection(XB).length / q.exterior.length >= 0.8: fill.append(q)
    X = unary_union([X] + [q.buffer(0.003) for q in fill]).buffer(0); fills += sum(A(q) for q in fill)
print('pockets filled', round(fills), 'km2')
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, gg) in G.items():
    if gg.area and gg.intersects(Y):
        pct = round(100 * gg.intersection(Y).area / gg.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(gg)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Prague': (14.42, 50.08), 'Uzhhorod': (22.29, 48.62), 'Kropyvnytskyi': (32.26, 48.51), 'Kryvyi Rih': (33.39, 47.91), 'Kamianske': (34.61, 48.51),
              'Dnipro (left bank)': (35.05, 48.46), 'Krasnodar': (38.98, 45.04), 'Stavropol': (41.97, 45.04), 'Grozny': (45.69, 43.32), 'Makhachkala': (47.5, 42.98),
              'Salsk': (41.54, 46.47), 'Elista (stays out)': (44.27, 46.31), 'Astrakhan (stays out)': (48.03, 46.35), 'Kyiv (stays out)': (30.52, 50.45)}.items():
    print('  ', n_, Y.contains(Point(p)))
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
