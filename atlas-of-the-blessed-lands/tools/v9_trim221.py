"""Version 221 (Nawaz, with a phone screenshot circling Corsica and Sardinia on V9: "Remove these from the super caliphate and return
Azerbaijan and Georgia to their modern borders in the super caliphate"). V9 (key 'v2'):
- Corsica and Sardinia out (all of V9 in France and Italy in 7-10.5 E, 38-43.5 N), with their rows and country notes (COR, SAR);
- every bit of Russia in the Caucasus (36-51 E, 40-46 N) out: Derbent, the Samur valley and the Dagestan coast (row 643_C), and a
  sliver past Georgia's border, so the outline follows Azerbaijan's and Georgia's modern borders with Russia; both stay whole.
Run: python3 tools/v9_trim221.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, box, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
CS = box(7, 38, 10.5, 43.5)
cut1 = V.intersection(CS.intersection(G['FRA'].union(G['380']).buffer(0.05)))
cut2 = V.intersection(box(36, 40, 51, 46).intersection(G['643']))
V = V.difference(cut1).difference(cut2)
X = shapely.union_all([V, G['031'].buffer(0.003).difference(G['643']), G['268'].buffer(0.003).difference(G['643'])], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('cut Corsica+Sardinia', round(A(cut1)), '| cut Russia in the Caucasus', round(A(cut2)))
print('left: Corsica/Sardinia', round(A(Y.intersection(CS.intersection(G['FRA'].union(G['380']))))), '| Russia in the Caucasus', round(A(Y.intersection(box(36, 40, 51, 46)).intersection(G['643']))))
for i, n in [('031', 'Azerbaijan'), ('268', 'Georgia'), ('051', 'Armenia')]: print(n, round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
print('V9', C['v2']['km2'], '->', km2)
v = C['v2']
v.update(polys=out, km2=km2, states=[r for r in v['states'] if r['id'] not in ('FRA', '380', '643_C')])
v['countries'] = [c for c in v['countries'] if c['a3'] not in ('COR', 'SAR')]
v['iberia'] = 'Version 42: Spain and Portugal whole, Corsica and Sardinia (Corsica and Sardinia out in Version 221)'
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
