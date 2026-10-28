"""Version 256 (Nawaz, phone screenshot with a red line across the Kuban dip from about 38.1 E 45.28 N to 40.3 E 45.19 N: "Fill",
then "Push"). Version 255 plus every rural/urban settlement (Overture 2026-10-21.0 localities, 'сельское/городское поселение') with half
or more of its area south of that line (18 settlements: Oktyabrskoe, Novomyshastovskoe, Maryanskoe, Novotitarovskoe, Yuzhno-Kubanskoe,
Michurinskoe, Dinskoe, Pervorechenskoe, Vasyurinskoe, Krasnogvardeyskoe, Beloselskoe, Khatukayskoe, Yelenovskoe, Nekrasovskoe,
Bolshesidorovskoe, Ulyapskoe, Novolabinskoe, Tenginskoe), Krasnodar city okrug whole, and Novotitarovskaya town whole (towns rule);
~2,900 km2. Saved as tools/data/caucasus_v5_256.geojson. REPLACES v5_caucasus255.py (same run order: after v7_sahara239,
v5_derbent249, v5_sicily250, v5_ca_borders251; do NOT also run 252-255)."""
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
ADD = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/caucasus_v5_256.geojson')))['features']])
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
