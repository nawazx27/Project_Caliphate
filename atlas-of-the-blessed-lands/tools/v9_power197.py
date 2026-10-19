"""Version 197 (Nawaz: "just make the v9 the most powerful caliphate out of all versions and even logically and realistically").
V9 keeps all it holds (V2 + the Greater Maghreb + Spain and Portugal) and gains, whole, the lands that are mostly Muslim, joined to V9
by land (or, for the Comoros, by a short sea crossing) and rich in what V9 lacked:
  Central Asia: Kazakhstan, Uzbekistan, Turkmenistan, Kyrgyzstan, Tajikistan (gas, oil, uranium, rivers, farmland);
  the Sahel and West Africa: Mali, Niger, Chad, Senegal, Gambia, Guinea, Sierra Leone, Nigeria (the Niger and Senegal rivers, Lake
  Chad, uranium, bauxite, oil, people); Guinea-Bissau by the no-gaps rule (held between Senegal, Guinea and the sea);
  the Balkans: Albania and Kosovo; the Indian Ocean: the Comoros.
Burkina Faso stays out (Nawaz removed it in Version 193). Run: python3 tools/v9_power197.py, then tools/fill_gaps.py me9."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
ADD = {'398': 'Kazakhstan', '860': 'Uzbekistan', '795': 'Turkmenistan', '417': 'Kyrgyzstan', '762': 'Tajikistan',
       '466': 'Mali', '562': 'Niger', '148': 'Chad', '686': 'Senegal', '270': 'Gambia', '324': 'Guinea', '694': 'Sierra Leone',
       '624': 'Guinea-Bissau (no-gaps rule)', '566': 'Nigeria', '008': 'Albania', 'KOS': 'Kosovo', '174': 'Comoros'}
X = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
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
for i in ADD: print(i, ADD[i], round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
print('V9', km2)
