"""Version 196 (Nawaz: "revert back to the previous version… and add Spain and Portugal"). V9 (V2 + the Greater Maghreb, as in Version
194) + Spain and Portugal whole, with their islands (Balearics, Canaries, Azores, Madeira), Ceuta, Melilla and Gibraltar (no-gaps rule:
held between Spain and the sea). Andorra stays out (shares its border with France about half and half). Run: python3 tools/v9_iberia196.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
GIB = Point(-5.352, 36.13).buffer(0.035)  # Gibraltar, about 7 km², a gap between Spain and the sea
ADD = {'724': 'Spain (with the Balearics, Canaries, Ceuta and Melilla)', '620': 'Portugal (with the Azores and Madeira)'}
X = shapely.union_all([V, GIB.intersection(G['724'].buffer(0.05))] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['me9']['states'] = [r for r in C['me9']['states'] if r['id'] not in ADD] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()]
C['me9']['polys'] = out; C['me9']['km2'] = km2
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i in ADD: print(i, round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
print('Gibraltar in', Y.contains(Point(-5.352, 36.13)), '| Andorra', round(A(G['020'].intersection(Y)), 1), '| France', round(A(G['FRA'].intersection(Y)), 1))
print('V9', km2)
