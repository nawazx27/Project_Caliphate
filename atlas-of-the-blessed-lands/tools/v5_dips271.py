"""Version 271 (Nawaz: "Fill these two dips as well", then "Why are these smooth", "Keep all real borders", "Sure").
V5 (CALIPH.sas) gains tools/data/v5_dips271.geojson: 22 whole Overture 2026-10-21.0 districts filling the two dips in its northern edge
(Kirov region: Nolinsk, Lebyazhye, Urzhum, Malmyzh, Kilmez, Nema, Uni, Bogorodskoye, Falyonki; Perm region: Kuyeda, Chaykovsky;
Kurgan region: Shchuchye, Safakulevo, Tselinnoye, Kurtamysh, Almenevo, Shumikha, Yurgamysh, Mishkino, Pritobolny, Zverinogolovskoye,
Polovinnoye) plus one 174 km2 gap pocket. Run AFTER tools/v5_wings270.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_dips271.geojson')))['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sas']['polys']]).buffer(0)
X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [r for r in C['sas']['states'] if r['id'] == 'RU_W']
rows[0]['n'] = rows[0]['n'].replace('Tatarstan and Bashkortostan,', 'Tatarstan and Bashkortostan, districts of southern Kirov and western Kurgan,')
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for r, k in zip(rows, ['643']):
    a = A(G[k].intersection(Y)); r['km2'] = round(a); r['pct'] = round(100 * a / A(G[k]), 1)
print(rows); print('V5 (sas)', C['sas']['km2'], '->', km2)
C['sas'].update(polys=out, km2=km2, states=C['sas']['states'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
