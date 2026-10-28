"""Version 250 (Nawaz: which classical heartlands are still outside V5 -> Sicily, Malta, Pantelleria; "Sure" to a preview, then "Sure").
Adds to V5 (CALIPH.sah), whole: Sicily with its islands as the base map draws them (every piece of Italy with its centre in 11-16 E,
35-39.2 N except the mainland: Sicily, the Aegadian and Aeolian Islands, Ustica, Pantelleria and the Pelagie Islands) and Malta.
Run AFTER tools/v7_sahara239.py (and after tools/v5_derbent249.py)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
G['SIC'] = unary_union([p for p in getattr(G['380'], 'geoms', [G['380']]) if 11 < p.centroid.x < 16 and 35 < p.centroid.y < 39.2 and p.area < 10])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
ADD = {'SIC': 'Italy: Sicily with its islands (Aegadian, Aeolian, Ustica, Pantelleria, Pelagie)', '470': 'Malta'}
X = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i, n in ADD.items(): print(n[:40], round(A(G[i])), 'km2, in', round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
print('V5 (sah)', C['sah']['km2'], '->', km2)
pct = {'SIC': round(A(G['SIC']) / A(G['380']) * 100, 1), '470': 100}
C['sah'].update(polys=out, km2=km2, states=[r for r in C['sah']['states'] if r['id'] not in ADD] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': pct[i]} for i, n in ADD.items()])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
