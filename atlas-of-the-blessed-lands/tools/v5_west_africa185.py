"""Version 185 (Nawaz: "Remove DR Congo from V5 and cover the entire West Africa until Cameroon"). DR Congo out of V5 (its neighbours V5
holds kept whole), except the DR Congo half of Lake Albert (standing rule: every outline holds the whole lake; tools/data/lake_albert_drc.geojson).
Added whole: every country of West Africa (UN Western Africa: Benin, Burkina Faso, Cabo Verde, Côte d'Ivoire, Gambia, Ghana, Guinea,
Guinea-Bissau, Liberia, Mali, Mauritania, Niger, Nigeria, Senegal, Sierra Leone, Togo, and Saint Helena with Ascension and Tristan da
Cunha) and Cameroon. Run: python3 tools/v5_west_africa185.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
LAKE = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Albert'])
LDRC = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/lake_albert_drc.geojson')))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x3']['polys']]).buffer(0)
held = unary_union([G[i][1].buffer(0.003) for i in ('800', '646', '108', '834', '728', '140')])   # Uganda, Rwanda, Burundi, Tanzania, South Sudan, CAR
V = V.difference(G['180'][1].buffer(0.004).difference(held))
WA = ['204', '854', '132', '384', '270', '288', '324', '624', '430', '466', '478', '562', '566', '686', '694', '768', '120']
SH = [i for i, (n, g) in G.items() if n == 'Saint Helena']
X = shapely.union_all([V, LAKE.buffer(0.003), LDRC.buffer(0.003)] + [G[i][1].buffer(0.003) for i in WA + SH], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x3']['polys'] = out
C['x3']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [s for s in C['x3']['states'] if s['id'] != '180']
have = {s['id'] for s in rows}
rows.append({'id': '180_A', 'n': 'DR Congo: the western half of Lake Albert', 'km2': round(A(LDRC)), 'pct': 0.0})
for i in WA + SH:
    if i not in have: rows.append({'id': i, 'n': G[i][0] + (' (with Ascension and Tristan da Cunha, counted in West Africa by the UN)' if i in SH else ''), 'km2': round(A(G[i][1])), 'pct': 100})
C['x3']['states'] = rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i in WA + SH + ['800', '646', '108', '140']: print(G[i][0], round(A(G[i][1].intersection(Y)) / A(G[i][1]) * 100, 2))
print('DR Congo in V5 km2', round(A(G['180'][1].intersection(Y))), '| Lake Albert', round(A(LAKE.intersection(Y)) / A(LAKE) * 100, 2), '| V5', C['x3']['km2'])
