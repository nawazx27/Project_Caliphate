"""Version 239 (Nawaz: previews of V6 with Niger, all of Chad ("the sticking out of Chad looks awkward"), then his map of northern Chad,
then "add Burkina Faso", then "make this a new version"). NEW outline CALIPH.sah (XV 'sah', V7) = V6 (CALIPH.me9) + Niger and Burkina
Faso whole + northern Chad = Borkou, Ennedi and Tibesti (the old BET prefecture; Overture Maps 2026-10-21.0 regions Tibesti, Borkou,
Ennedi Ouest, Ennedi Est, cut to Chad as the base map draws it, main body only: tools/data/northern_chad239.geojson). V6 is unchanged.
Run after any V6 change: python3 tools/v7_sahara239.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
G['BET'] = shape(json.load(open(os.path.join(P, 'tools/data/northern_chad239.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
ADD = {'562': 'Niger', '854': 'Burkina Faso', 'BET': 'Chad: Borkou, Ennedi and Tibesti (northern Chad, the old BET prefecture)'}
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
print('V7 (sah)', C['me9']['km2'], '->', km2)
pct = {i: (round(A(G['BET']) / A(G['148']) * 100, 1) if i == 'BET' else 100) for i in ADD}
C['sah'] = {'polys': out, 'km2': km2, 'states': [dict(r) for r in C['me9']['states'] if r['id'] not in ADD] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': pct[i]} for i, n in ADD.items()]}
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
