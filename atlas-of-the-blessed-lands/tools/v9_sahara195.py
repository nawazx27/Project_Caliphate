"""Version 195 (Nawaz: "Add the entire Sahara Desert to V9"). The whole Sahara as Natural Earth's physical regions draw it (SAHARA and its
eastern part, the LIBYAN DESERT; regions.geojson), kept to land, added to V9. Natural Earth's Sahara reaches about 9°N in places, so it
takes in the Saharan and Sahelian parts of Mali, Niger, Chad, Sudan, Senegal, Burkina Faso, Nigeria, Cameroon and the Central African
Republic (part only). Towns cut by the new line are taken whole by tools/v9_sahara_towns195.py. Run: python3 tools/v9_sahara195.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
land = unary_union([g for n, g in G.values()])
R = json.load(open(os.path.join(P, 'regions.geojson')))
SAH = unary_union([shape(f['geometry']).buffer(0) for f in R['features'] if (f['properties'].get('NAME') or '').upper() in ('SAHARA', 'LIBYAN DESERT')]).intersection(land)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
new = SAH.difference(V)
X = shapely.union_all([V, SAH.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['me9']['polys'] = out
C['me9']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [s for s in C['me9']['states'] if not s['id'].endswith('_SAH')]
for i, (n, g) in sorted(G.items(), key=lambda kv: -A(kv[1][1].intersection(new)) if kv[1][1].intersects(new) else 0):
    if not g.intersects(new): continue
    a = A(g.intersection(new))
    if a < 50: continue
    rows.append({'id': i + '_SAH', 'n': f'{n}: its part of the Sahara', 'km2': round(a), 'pct': round(a / A(g) * 100, 1)})
    print(n, round(a), round(a / A(g) * 100, 1), '%')
C['me9']['states'] = rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('Sahara in V9', round(A(SAH.intersection(Y)) / A(SAH) * 100, 2), '% | V9', C['me9']['km2'], 'holes', sum(len(p) - 1 for p in out))
