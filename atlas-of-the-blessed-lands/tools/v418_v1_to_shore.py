"""Version 418 PREVIEW (Nawaz, on the pushed-down V1 (`MEET=1 X0=39.5 DY=2.5 tools/v407_v1_nile_euphrates.py`), arrow from its straight east edge to the Gulf: "Just
bring it to the shore"). The Saudi land between the east edge (~48.6 E) and the Gulf shore is added; its lower edge is NOT a straight line: it carries on the lobe's
own wavy southern edge (the last 2.15 degrees of it, copied east and joined at the corner). Bahrain and Qatar not added. Then rerun tools/v411_arabia.py and v386_areas_ellipsoid.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
SA = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == 'Saudi Arabia'][0]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
def low(lon):
    s = V.intersection(LineString([(lon, 23.5), (lon, 29.0)])); return min(g.bounds[1] for g in getattr(s, 'geoms', [s]))
E0 = 48.55; W = 2.15; N = 86
src = [(E0 - W + W * i / N, low(E0 - W + W * i / N)) for i in range(N + 1)]
shift = low(E0) - src[0][1]
edge = [(x + W, y + shift) for x, y in src]   # the lobe's own edge, continued east from the corner
print('lower edge from', [round(v, 2) for v in edge[0]], 'to', [round(v, 2) for v in edge[-1]])
REG = Polygon([(E0 - 0.05, 29.3)] + [(E0 - 0.05, edge[0][1])] + edge + [(51.5, edge[-1][1]), (51.5, 29.3)]).buffer(0)
NEW = SA.intersection(REG); print('   land to the shore', round(A(NEW.difference(V))), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000]
X = unary_union([X] + holes).intersection(V3.buffer(0.002)); X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o)
for n_, p in {'Jubail': (49.66, 27.01), 'Dammam': (50.1, 26.43), 'al-Khobar': (50.2, 26.28), 'Abqaiq': (49.67, 25.93), 'al-Hofuf': (49.58, 25.38), 'Bahrain (out)': (50.58, 26.22)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
