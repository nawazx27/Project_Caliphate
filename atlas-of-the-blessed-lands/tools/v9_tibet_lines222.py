"""Version 222 (Nawaz: "verify Greater Tibet thoroughly"). Greater Tibet in V9 (key 'v2') checked against three public line sources:
Overture Maps divisions 2026-09-23.1 (used in Version 219), Natural Earth 10 m admin-1 (Qinghai and Xizang) and geoBoundaries gbOpen
CHN ADM2 (every county at least half inside the other two). They differ along the Qinghai-Tibet line (Natural Earth puts the
Tanggula area, ~57,600 km2, in Qinghai, Overture in Tibet), on the Qinghai-Gansu line (~19,000 km2 Natural Earth gives Qinghai,
inside V9 only through East Turkestan) and in thin strips along the eastern edge. By the leave-no-area-out rule the widest line is
taken: tools/data/greater_tibet_v222.geojson (2,169,280 km2), added here; then tools/fill_gaps.py v2 and tools/v9_super_gaps219.py.
Run: python3 tools/v9_tibet_lines222.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
GT = shape(json.load(open(os.path.join(P, 'tools/data/greater_tibet_v222.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
print('Greater Tibet outside V9 before:', round(A(GT.difference(V))), 'km2')
X = shapely.union_all([V, GT.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('Greater Tibet inside V9 after:', round(A(GT.intersection(Y)) / A(GT) * 100, 3), '% | V9', C['v2']['km2'], '->', km2)
for r in C['v2']['states']:
    if r['id'] == '156_T': r['km2'] = round(A(GT))
C['v2'].update(polys=out, km2=km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
