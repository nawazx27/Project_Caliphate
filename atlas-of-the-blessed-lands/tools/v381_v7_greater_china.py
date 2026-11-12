"""Version 381 PREVIEW (Nawaz, after the 378/380 tries added too much in the north-east: "restrict to this", the Madrid Maps "Concept of a Greater China" map,
"and add the entire Korean Peninsula"). One tool, run on the LIVE V7 (sup), replacing the 377-380 preview chain:
  China (PRC) whole with Hong Kong and Macao, Taiwan, Mongolia, the Tuva Republic, the whole Korean Peninsula (North and South Korea), and
  Outer Manchuria as the map draws it = the land north of the Amur and east of the Ussuri ceded in 1858-60, its northern edge the Stanovoy range:
  Amur Oblast, the Jewish Autonomous Oblast, Primorsky Krai, and Khabarovsk Krai WITHOUT its northern Okhotsky and Ayano-Maysky districts (the
  Okhotsk coast north of the Uda, the lobe he circled). Kazakhstan, Kyrgyzstan, Nepal, Bhutan and Arunachal (on the map) are already in V7.
  Sakhalin is not on the map and is not added. Sources: base map (geo2.json) and Overture 2026-10-21.0 regions/districts
  (tools/data/v378_ru_far_east.parquet, tools/data/v381_khabarovsk_counties.parquet). DIR env = project dir (preview: a copy)."""
import pyarrow.parquet as pq
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
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
V = MP(C['sup']['polys']); parts = {}
for k in ['156', '158', '344', '446', '496', '408', '410']: parts[G[k][0]] = G[k][1]
for r in pq.read_table(os.path.join(HERE, 'tools/data/v378_ru_far_east.parquet')).to_pylist():
    if r['class'] != 'land' or r['is_land'] is False or r['region'] == 'RU-KHA': continue
    parts[dict(r['names']['common']).get('en')] = shapely.from_wkb(r['geometry']).buffer(0)
NORTH = ('Охотский муниципальный округ', 'Аяно-Майский район')
kha = [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, 'tools/data/v381_khabarovsk_counties.parquet')).to_pylist() if r['class'] == 'land' and r['names']['primary'] not in NORTH]
parts['Khabarovsk Krai without Okhotsky and Ayano-Maysky'] = unary_union(kha)
run = V
for n, g in parts.items():
    a = A(g.difference(run))
    if a >= 1: print('  +', n, round(a), 'km2')
    run = unary_union([run, g.buffer(0.003)])
X = run.buffer(0); o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Beijing': (116.4, 39.9), 'Taipei': (121.56, 25.03), 'Ulaanbaatar': (106.92, 47.92), 'Kyzyl (Tuva)': (94.45, 51.72), 'Pyongyang': (125.75, 39.02), 'Seoul': (126.98, 37.57), 'Jeju': (126.53, 33.5),
              'Blagoveshchensk': (127.53, 50.27), 'Tynda': (124.7, 55.16), 'Khabarovsk': (135.08, 48.48), 'Vladivostok': (131.9, 43.12), 'Komsomolsk': (137.0, 50.55), 'Nikolayevsk-on-Amur': (140.7, 53.14), 'Chumikan (Uda)': (135.3, 54.7),
              'Ayan (out)': (138.15, 56.45), 'Okhotsk (out)': (143.2, 59.36), 'Sakhalin (out)': (142.75, 46.96), 'Chita (out)': (113.5, 52.03), 'Tokyo (out)': (139.69, 35.69)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('tib outside sup', round(A(MP(C['tib']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
