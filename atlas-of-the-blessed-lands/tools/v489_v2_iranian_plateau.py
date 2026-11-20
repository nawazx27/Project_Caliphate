"""Version 489 (Nawaz, the Wikipedia article "Iranian plateau": ~3.7 million km2, between the Zagros, the Caspian and Kopet Dag, the Armenian Highlands,
the Gulf, the Hindu Kush and the Sulaiman Mountains; "the overwhelming majority of both Iran and Afghanistan, as well as the parts of Pakistan that are
situated to the west of the Indus River (Balochistan and Khyber Pakhtunkhwa)": "Preview v2 with the entire Iranian plateau"). Added to V2 (CALIPH.arb):
Afghanistan whole, and Pakistan's Balochistan and Khyber Pakhtunkhwa with the former FATA (Natural Earth admin-1, A1 env), each whole. Iran, Iraqi
Kurdistan and Turkiye are already whole in V2. Enclosed pockets filled; V1 unchanged. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
PK = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.environ['A1']))['features'] if f['properties'].get('adm0_a3') == 'PAK' and f['properties'].get('name') in ('Baluchistan', 'K.P.', 'F.A.T.A.')])
PK = PK.intersection(G['Pakistan'].buffer(0.02)).buffer(0)
print('Pakistan west of the Indus (Balochistan, KP, FATA)', round(A(PK)), 'km2')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys'])
X = unary_union([V, G['Afghanistan'].buffer(0.003), PK.buffer(0.003)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 200})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('arb', C['arb']['km2'], '->', km)
for n, p in {'Kabul': (69.17, 34.53), 'Herat': (62.2, 34.35), 'Kandahar': (65.71, 31.61), 'Mazar-i-Sharif': (67.11, 36.71), 'Quetta': (67.0, 30.18), 'Peshawar': (71.58, 34.01), 'Gwadar': (62.32, 25.12), 'Islamabad (out)': (73.05, 33.68), 'Karachi (out)': (67.0, 24.86)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
