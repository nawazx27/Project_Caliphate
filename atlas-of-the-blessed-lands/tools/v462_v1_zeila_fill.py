"""Version 462 (Nawaz, red stroke on the Version 461 preview from V1's edge at the Djibouti-Ethiopia-Somaliland corner, ~42.80 E 10.02 N, north-east
across Somaliland to the Gulf of Aden coast, ~44.03 E 11.77 N; placed by an affine fit on Lakes Tana, Abbe, Abaya and Turkana in the picture, residuals
under 7 km). Somaliland's (and Ethiopia's) land west of the stroke, Zeila and Borama country, goes into V1 (shj). DIR env = project dir. Run v386 after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union, nearest_points
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ST = [(43.156, 10.355), (43.639, 10.893), (43.911, 11.277), (44.033, 11.768), (44.05, 12.2)]
Pa = nearest_points(V.boundary, Point(42.801, 10.017))[0]
POLY = Polygon([(Pa.x, Pa.y)] + ST + [(42.8, 12.2), (42.4, 11.0), (Pa.x - 0.3, Pa.y)]).buffer(0)
LANDS = unary_union([G['Somaliland'], G['Ethiopia'], G['Djibouti']])
add = POLY.intersection(LANDS).difference(V); print('filled', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Somaliland', 'Ethiopia', 'Djibouti']})
X = unary_union([V, add.buffer(0.003).intersection(LANDS.buffer(0.003))]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Zeila': (43.47, 11.35), 'Borama': (43.18, 9.94), 'Lughaya': (43.95, 10.69), 'Berbera (out)': (45.03, 10.44), 'Hargeisa (out)': (44.06, 9.56)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
