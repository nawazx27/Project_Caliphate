"""Version 252 (Nawaz, after the Rashidun check: Wikipedia lists Dagestan among the Rashidun conquests; previews of all of Dagestan,
Dagestan + Chechnya, the North Caucasus republics, a moved copy of Georgia's border, then his orange Caucasus map again; he chose
"Option 2" = his orange Caucasus (tools/data/caucasus_shape155.geojson) + all of Dagestan and Chechnya (Overture regions RU-DA, RU-CE),
and ticked it). The Russian land of that union, with every city and town the line cuts taken whole (Overture 2026-10-21.0 localities
class city/town; Anapa, Kabardinka, Adygeysk, Labinsk, Yablonovsky, Yelizavetinskaya, Lermontov, Inozemtsevo, Izberbash, Kaspiysk,
Makhachkala), is saved in tools/data/caucasus_v5_252.geojson and added to V5 (CALIPH.sah); land pockets in the Caucasus >= 80% enclosed
by V5 are filled (no-gaps rule; political-border bends left). Supersedes the Derbent block of Version 249 (inside it).
Run AFTER tools/v7_sahara239.py, v5_derbent249.py, v5_sicily250.py, v5_ca_borders251.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
ADD = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/caucasus_v5_252.geojson')))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
X = shapely.union_all([V, ADD.buffer(0.003)], grid_size=0.001)
m = X.intersection(box(36, 40, 50, 47)); gap = m.buffer(0.5, quad_segs=4).buffer(-0.5, quad_segs=4).difference(m).intersection(land); mb = m.buffer(0.01); fill = []
for g in getattr(gap, 'geoms', [gap]):
    if g.geom_type == 'Polygon' and A(g) >= 100 and g.exterior.intersection(mb).length / g.exterior.length >= 0.8: fill.append(g); print('gap filled', round(A(g)), 'km2 at', round(g.centroid.x, 2), round(g.centroid.y, 2))
X = unary_union([X] + [g.buffer(0.003) for g in fill]).buffer(0)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
RUin = G['643'].intersection(Y).intersection(box(36, 40, 50, 47))
print('Caucasus addition in', round(A(ADD.intersection(Y)) / A(ADD) * 100, 2), '%; Russian land in V5 Caucasus', round(A(RUin)), 'km2; V5', C['sah']['km2'], '->', km2)
row = {'id': 'DBT', 'n': 'Russia: the North Caucasus (the author’s Caucasus map, with all of Dagestan and Chechnya; Derbent, Bāb al-Abwāb)', 'km2': round(A(RUin)), 'pct': round(A(RUin) / A(G['643']) * 100, 2)}
C['sah'].update(polys=out, km2=km2, states=[r for r in C['sah']['states'] if r['id'] != 'DBT'] + [row])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
