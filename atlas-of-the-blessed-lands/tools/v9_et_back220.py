"""Version 220 (Nawaz: "Ykw, add back East Turkestan"): East Turkestan back into V9 (key 'v2') exactly as it was in Version 218,
from tools/data/v9_east_turkestan_v218.geojson (saved by tools/save_v9_east_turkestan219.py), with its row, its three province-history
units and its country note (tools/data/v9_east_turkestan_v218_history.json). Qinghai's Mangnai/Lenghu are in both East Turkestan and
Greater Tibet. Run, then tools/fill_gaps.py v2 and tools/v9_super_gaps219.py <Overture dir> (its East Turkestan exclusion then finds
nothing to drop, East Turkestan being inside)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
ET = shape(json.load(open(os.path.join(P, 'tools/data/v9_east_turkestan_v218.geojson')))['features'][0]['geometry']).buffer(0)
H = json.load(open(os.path.join(P, 'tools/data/v9_east_turkestan_v218_history.json')))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
X = shapely.union_all([V, ET.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('East Turkestan in', round(A(ET.intersection(Y)) / A(ET) * 100, 2), '| V9', C['v2']['km2'], '->', km2)
v = C['v2']
v.update(polys=out, km2=km2, states=[r for r in v['states'] if r['id'] != '156_X'] + [H['row']])
v['units'] = [u for u in v['units'] if u['a3'] != 'XJ'] + H['units']
cs = [c for c in v['countries'] if c['a3'] != 'XJ']; i = next((k for k, c in enumerate(cs) if c['a3'] == 'CMR'), len(cs)); v['countries'] = cs[:i] + [H['country']] + cs[i:]
v['xinjiang'] = H['xinjiang']
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
