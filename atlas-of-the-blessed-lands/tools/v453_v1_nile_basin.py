"""Version 453 (Nawaz, five Wikimedia Nile-basin maps with the red "Boundary of the Nile Basin": "Add in that preview"). V1 (shj) takes all land inside
the Nile basin as traced from his map (tools/v453_nile_basin_trace.py -> tools/data/v453_nile_basin_traced.geojson; placed by 11 labelled points of the
map, mean error ~33 km), on top of the Version 452 whole-Nile preview. Land only. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
B = shape(json.load(open(os.path.join(HERE, 'tools/data/v453_nile_basin_traced.geojson')))['geometry']).buffer(0)
LAND = unary_union([g.intersection(B.buffer(0.1)) for g in G.values() if g.intersects(B)]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
add = B.intersection(LAND)
NEW = add.difference(V)
print('basin land', round(A(add)), 'km2 | new to V1', round(A(NEW)), 'km2', {k: round(A(NEW.intersection(G[k]))) for k in ['Ethiopia','Kenya','Tanzania','DR Congo','Central African Rep.','Chad','Eritrea','Uganda','Rwanda','Burundi','Libya'] if k in G})
X = unary_union([V, add.buffer(0.003).intersection(LAND.buffer(0.003))]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 20]
X = unary_union([X] + holes).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); rws = []
for f in geo['features']:
    if not f.get('geometry'): continue
    g_ = G[f['properties']['n']]
    if g_.area and g_.intersects(Y):
        pct = round(100 * g_.intersection(Y).area / g_.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g_)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| basin inside V1 %', round(100 * add.intersection(Y).area / add.area, 2))
for n_, p in {'Hawassa (out of basin)': (38.48, 7.05), 'Nekemte': (36.55, 9.08), 'Kitale (Kenya)': (35.0, 1.02), 'Musoma': (33.8, -1.5), 'Bunia (DRC)': (30.25, 1.56), 'Goma (DRC)': (29.22, -1.68), 'El Geneina': (22.45, 13.45)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
