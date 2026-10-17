"""Version 165 (Nawaz: "Yes, take the whole delta in v2"). The whole Danube delta (Natural Earth physical region, on land; Romania and Ukraine) is
added to V2 only (V2-B is left alone); V7 is rebuilt from V2. Run: python3 tools/danube_delta164.py, then python3 tools/v7_build159.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}; land = unary_union(list(G.values()))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x']['polys']]).buffer(0)
DD = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'regions.geojson')))['features'] if f['properties']['NAME'].upper().startswith('DANUBE DELTA')][0].intersection(land)
add = DD.difference(X); print('Danube delta', round(A(DD)), 'km2; before', round(A(DD.intersection(X)) / A(DD) * 100, 1), '%; adds', round(A(add)))
X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
out = []
for q in getattr(X2, 'geoms', [X2]):
    if q.geom_type != 'Polygon': continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x']['polys'] = out
C['x']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for i, n in (('642', 'Romania'), ('804', 'Ukraine')):
    a = add.intersection(G[i])
    if A(a) >= 1: C['x']['states'].append({'id': 'DD_' + i, 'n': n + ': the rest of the Danube delta', 'km2': round(A(a)), 'pct': round(A(a) / A(G[i]) * 100, 2)}); print(n, round(A(a)))
print('V2', C['x']['km2'], 'Danube delta now', round(A(DD.intersection(X2)) / A(DD) * 100, 1), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
