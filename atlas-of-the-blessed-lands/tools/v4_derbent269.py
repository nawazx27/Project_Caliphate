"""Version 269 (Nawaz, after "What do you think about V4" and a preview: "Yes"). Derbent (Bab al-Abwab) and the whole districts of southern
Dagestan around it into V4 (CALIPH.me9), exactly as tools/v5_derbent249.py drew them for the old V5 (tools/data/derbent_south_dagestan249.geojson:
Derbent and Dagestanskiye Ogni, Derbentsky, Magaramkentsky, Suleyman-Stalsky, Kurakhsky, Khivsky, Akhtynsky, Dokuzparinsky, Tabasaransky,
Agulsky) plus the Rutul-area pocket (no-gaps rule). Run AFTER tools/v4_kashmir264.py; then rerun tools/v9_south_asia265.py (V5 is built on V4)."""
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
DB = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/derbent_south_dagestan249.geojson')))['features']]).intersection(G['643'].buffer(0.02))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V, DB.buffer(0.003)], grid_size=0.001)
# no-gaps rule in the Caucasus
m = X.intersection(box(44, 40, 50, 44)); gap = m.buffer(0.5, quad_segs=4).buffer(-0.5, quad_segs=4).difference(m).intersection(land); mb = m.buffer(0.01); fill = []
for g in getattr(gap, 'geoms', [gap]):
    if g.geom_type == 'Polygon' and A(g) >= 100 and g.exterior.intersection(mb).length / g.exterior.length >= 0.795: fill.append(g); print('gap filled', round(A(g)), 'km2 at', round(g.centroid.x, 2), round(g.centroid.y, 2))
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
RUin = G['643'].intersection(Y).intersection(box(46.5, 41, 49, 42.6))
print('districts in', round(A(DB.intersection(Y)) / A(DB) * 100, 2), '%; Russian land in V4', round(A(RUin)), 'km2; V5', C['me9']['km2'], '->', km2)
row = {'id': 'DBT', 'n': 'Russia: Derbent (Bāb al-Abwāb) and southern Dagestan (the Samur valley and Derbent’s hinterland)', 'km2': round(A(RUin)), 'pct': round(A(RUin) / A(G['643']) * 100, 2)}
C['me9'].update(polys=out, km2=km2, states=[r for r in C['me9']['states'] if r['id'] != 'DBT'] + [row])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
