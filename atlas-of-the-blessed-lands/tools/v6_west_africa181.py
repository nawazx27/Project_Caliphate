"""Version 181 (Nawaz, phone screenshot of V6 over West Africa: "Cover the entire West Africa"). Every country of West Africa (the UN
geoscheme's Western Africa) whole in V6: Côte d'Ivoire, Ghana, Togo, Benin, Liberia and Cabo Verde added, the coast slivers of Gambia,
Guinea-Bissau and Sierra Leone closed, and Saint Helena (with Ascension and Tristan da Cunha, which the UN counts in Western Africa) added
under the leave-no-area-out rule. Run: python3 tools/v6_west_africa181.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: (f['id'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
NAMES = ["Côte d'Ivoire", 'Ghana', 'Togo', 'Benin', 'Liberia', 'Cabo Verde', 'Saint Helena', 'Gambia', 'Guinea-Bissau', 'Sierra Leone']
adds = []
have = {s['id'] for s in C['v2']['states']}
for n in NAMES:
    i, g = G[n]; adds.append(g.buffer(0.003))
    if i not in have:
        C['v2']['states'].append({'id': i, 'n': n + (' (with Ascension and Tristan da Cunha, counted in West Africa by the UN)' if n == 'Saint Helena' else ''), 'km2': round(A(g)), 'pct': 100})
X = shapely.union_all([V] + adds, grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['v2']['polys'] = out
C['v2']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
V2 = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for n in NAMES: print(n, round(A(G[n][1].intersection(V2)) / A(G[n][1]) * 100, 2))
print('V6', C['v2']['km2'])
