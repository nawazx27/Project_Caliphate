"""Version 481 (Nawaz, on the first weak spot of V2 (Mombasa and Dar es Salaam, East Africa's two big ports, outside): "Fix the first weak spot and
preview full map"). Added to V2 (CALIPH.arb): all of Kenya (the coast strip with Mombasa, Malindi and Lamu; V2 held 98%), and Tanzania's coast from the
Kenyan border to Dar es Salaam as whole regions (Natural Earth admin-1, A1 env = its geojson): Tanga, Pwani, Dar es Salaam and the Zanzibar and Pemba
islands (the five Zanzibar regions); V2 already held Arusha and Kilimanjaro, so the coast joins it through Tanga. Enclosed pockets filled; V1 unchanged.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
REG = ['Tanga', 'Pwani', 'Dar-Es-Salaam', 'Zanzibar South and Central', 'Kaskazini-Unguja', 'Zanzibar West', 'Kusini-Pemba', 'Kaskazini-Pemba']
TZ = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.environ['A1']))['features'] if f['properties'].get('adm0_a3') == 'TZA' and f['properties'].get('name') in REG])
KE = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.environ['A1']))['features'] if f['properties'].get('adm0_a3') == 'KEN'])   # Natural Earth admin-1 keeps the coastal islands (Mombasa, Lamu, Pemba, Zanzibar) the base map lacks
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); V1 = MP(C['shj']['polys'])
ISL = unary_union([Point(39.668, -4.045).buffer(0.045), Point(40.90, -2.27).buffer(0.06), Point(40.95, -2.18).buffer(0.05)])   # Mombasa island and the Lamu archipelago (Lamu, Manda), too small for the base map's coastline: the city on its island taken whole
X = unary_union([V, G['Kenya'].buffer(0.003), KE, TZ.buffer(0.003), ISL]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 50})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o)
print('arb', C['arb']['km2'], '->', km, '| Kenya', round(100 * A(G['Kenya'].intersection(Y)) / A(G['Kenya']), 2), '% | Tanzania', round(100 * A(G['Tanzania'].intersection(Y)) / A(G['Tanzania']), 1), '%')
for n, p in {'Mombasa': (39.67, -4.05), 'Lamu': (40.9, -2.27), 'Tanga': (39.1, -5.07), 'Dar es Salaam': (39.28, -6.8), 'Bagamoyo': (38.9, -6.44), 'Zanzibar City': (39.19, -6.16), 'Pemba (Kusini-Pemba)': (39.7, -5.3), 'Morogoro (out)': (37.66, -6.82)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
