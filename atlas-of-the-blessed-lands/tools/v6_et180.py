"""Version 180 (Nawaz: "In V6 verify East Turkestan with its official map renderings for an accurate drawing"). V6's East Turkestan was
hand-traced (Version 63, ~8 km error). It is redrawn to the East Turkistan Government in Exile's own definition, as Wikipedia ('East
Turkestan', citing ETGE 'East Turkistan at a Glance', 2021) records it: Xinjiang WITHOUT Aksai Chin, plus Subei, Aksay, Dunhuang and Guazhou
in western Gansu and Lenghu and Mangnai in Qinghai (Mangnai City has held Lenghu since 2018). Lines from Overture divisions 2026-09-23.1
(Xinjiang region, its Aksai Chin row, the county shapes), kept to the base map's China. Run: python3 tools/v6_et180.py <dir with cn_tibet.parquet, et_la.parquet>"""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CN = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['id'] == '156'][0]
rows = pq.read_table(os.path.join(D, 'cn_tibet.parquet')).to_pylist()
g_ = lambda r: shapely.make_valid(wkb.loads(r['geometry']))
XJ = unary_union([g_(r) for r in rows if r['subtype'] == 'region' and r['region'] == 'CN-XJ'])
AC = unary_union([g_(r) for r in rows if r['subtype'] == 'region' and r['names']['primary'].startswith('阿克赛钦')])
la = pq.read_table(os.path.join(D, 'et_la.parquet')).to_pylist()
WANT = {'肃北蒙古族自治县': 'Subei', '阿克塞哈萨克族自治县': 'Aksay', '敦煌市': 'Dunhuang', '瓜州县': 'Guazhou', '茫崖市': 'Mangnai and Lenghu'}
ext = {}
for r in la:
    n = r['names']['primary'].split(' ')[0]
    if r['subtype'] == 'localadmin' and n in WANT: ext[WANT[n]] = g_(r)
assert len(ext) == 5, sorted(ext)
ET = unary_union([XJ.difference(AC)] + list(ext.values())).intersection(CN.buffer(0.01))
print('ET', round(A(ET)), {k: round(A(v)) for k, v in ext.items()}, 'Aksai Chin out', round(A(XJ.intersection(AC))))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V6 = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
old = V6.intersection(CN)
print('old ET', round(A(old)), '| new not in old', round(A(ET.difference(old))), '| old not in new', round(A(old.difference(ET))))
X = shapely.union_all([V6.difference(CN.buffer(0.002)), ET.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['v2']['polys'] = out
C['v2']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for s in C['v2']['states']:
    if s['id'] == '156_X':
        s['n'] = 'China: East Turkestan as its government in exile defines it (Xinjiang without Aksai Chin; Subei, Aksay, Dunhuang, Guazhou in Gansu; Lenghu and Mangnai in Qinghai)'
        s['km2'] = round(A(ET)); s['pct'] = round(A(ET) / A(CN) * 100)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V6', C['v2']['km2'])
