"""Version 245 (Nawaz: "reverse in V5" -> rivers; preview of V5 with the Indus, then "B"). Indian-administered Kashmir (Jammu and
Kashmir and Ladakh union territories; Overture Maps 2026-10-21.0 regions IN-JK and IN-LA, cut to India as the base map draws it:
tools/data/indian_kashmir245.geojson) whole into V5 (CALIPH.sah), so the Indus is inside but for its source in Tibet.
Disputed land (India/Pakistan). Run AFTER tools/v7_sahara239.py (which rebuilds sah from me9 and would drop it)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
G['KIN'] = shapely.union_all([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/indian_kashmir245.geojson')))['features']]).intersection(G['356'].buffer(0.02))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
ADD = {'KIN': 'India: Jammu and Kashmir and Ladakh (Indian-administered Kashmir, disputed)'}
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
C['sah'].update(polys=out, km2=km2, states=[r for r in C['sah']['states'] if r['id'] not in ADD] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': round(A(G[i]) / A(G['356']) * 100, 1)} for i, n in ADD.items()])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
