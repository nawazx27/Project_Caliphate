"""Version 184 (Nawaz, six phone screenshots of country notes on V5: "Add these lands to V5 and remove Sicily"). Senegal, Mali, Niger, Chad,
the Central African Republic and DR Congo added whole to V5; Gambia too (Senegal would enclose it: no-gaps rule); Sicily and its islands
(all of Italy that V5 held) taken out. Run: python3 tools/v5_africa184.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x3']['polys']]).buffer(0)
V = V.difference(G['380'][1].buffer(0.02))   # Italy (Sicily and its islands) out
ADD = {'686': 'Senegal', '466': 'Mali', '562': 'Niger', '148': 'Chad', '140': 'Central African Republic', '180': 'DR Congo', '270': 'Gambia (enclosed by Senegal)'}
X = shapely.union_all([V] + [G[i][1].buffer(0.003) for i in ADD], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x3']['polys'] = out
C['x3']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [s for s in C['x3']['states'] if not s['id'].startswith('380') and not s['id'].startswith('180')]
rows += [{'id': i, 'n': n, 'km2': round(A(G[i][1])), 'pct': 100} for i, n in ADD.items()]
C['x3']['states'] = rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i in list(ADD) + ['380', '470']: print(G[i][0], round(A(G[i][1].intersection(Y)) / A(G[i][1]) * 100, 2))
print('V5', C['x3']['km2'], 'holes', sum(len(p) - 1 for p in out))
