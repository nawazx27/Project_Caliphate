"""Version 258 (Nawaz, with the Wikipedia "Balkans" article and its interactive map: "Use my Balkan outline and push").
V5 (CALIPH.sah) gains the Balkan Peninsula exactly as Version 107 drew it for V2: OpenStreetMap relation 4016746 (tools/data/balkans_osm.geojson)
cut to the base map per country (tools/data/balkans_v2.geojson: Bulgaria, Bosnia and Herzegovina, Montenegro, Albania, Kosovo and North
Macedonia whole; Croatia with every island, Serbia, Slovenia, Romania and Italy's Trieste in part) plus the towns the line cuts, taken whole
(tools/data/balkan_settlements.geojson and _pass2). Greece and Türkiye were already in V5. Africa unchanged. Pockets >= 80% enclosed and
>= 100 km2 in 11-31E, 38-48N filled (one, about 800 km2, by Belgrade). Run AFTER tools/v5_ca_borders251.py (Version 257 state)."""
import json, os, subprocess, shapely
from shapely import make_valid
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
D = lambda n: json.load(open(os.path.join(P, 'tools/data', n)))['features']
parts = D('balkans_v2.geojson')
ADD = unary_union([make_valid(shape(f['geometry'])).buffer(0) for f in parts + D('balkan_settlements.geojson') + D('balkan_settlements_pass2.geojson')])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
X = shapely.union_all([V, ADD.buffer(0.003)], grid_size=0.001)
m = X.intersection(box(11, 38, 31, 48)); mb = m.buffer(0.01); fill = []
gap = m.buffer(0.5, quad_segs=4).buffer(-0.5, quad_segs=4).difference(m).intersection(land)
for g in getattr(gap, 'geoms', [gap]):
    if g.geom_type != 'Polygon' or A(g) < 100: continue
    t = g.exterior.intersection(mb).length / g.exterior.length
    print('pocket', round(A(g)), round(t * 100), round(g.centroid.x, 2), round(g.centroid.y, 2), 'FILLED' if t >= 0.8 else '')
    if t >= 0.8: fill.append(g)
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
NM = {'191': 'Croatia: south of the Kupa and Sava, with every island (Balkan Peninsula)', '688': 'Serbia: south of the Sava and Danube (Balkan Peninsula)',
      '705': 'Slovenia: the south-west with the coast (Balkan Peninsula)', '642': 'Romania: Dobruja (Balkan Peninsula)', '380': 'Italy: Trieste (Balkan Peninsula)'}
rows = []
for f in parts:
    i = f['properties']['id']; pct = round(A(G[i].intersection(Y)) / A(G[i]) * 100, 1)
    rows.append({'id': i if f['properties']['whole'] else i + '_B', 'n': NM.get(i, f['properties']['n'].replace('Herz.', 'Herzegovina')), 'km2': round(A(G[i].intersection(Y))), 'pct': 100 if f['properties']['whole'] else pct})
    print(rows[-1])
print('V5', C['sah']['km2'], '->', km2)
C['sah'].update(polys=out, km2=km2, states=[r for r in C['sah']['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
