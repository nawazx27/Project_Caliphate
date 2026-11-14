"""Version 417 PREVIEW (Nawaz, on the Version 409-style preview (push down + shore fill) with a red loop from the corner of V1 to the Gulf shore and down past Riyadh:
"I just asked for this bit"). Run after `MEET=1 X0=39.5 DY=2.5 tools/v407_v1_nile_euphrates.py` and `SOUTH=25.63 tools/v409_v1_gulf_fill.py` on today's V1:
the Saudi land inside his loop (read off his screenshot; box 36-52 E, 22-33 N; Riyadh at x700 y584, ~45.3 px per degree) is added, so the edge there follows his
curved loop down to Riyadh's latitude instead of a straight line. Bahrain and Qatar not added. Then rerun tools/v411_arabia.py and v386_areas_ellipsoid.py."""
import json, os, math, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
M = lambda y: math.degrees(math.log(math.tan(math.pi / 4 + math.radians(y) / 2))); IM = lambda m: math.degrees(2 * math.atan(math.exp(math.radians(m))) - math.pi / 2)
K = 45.3; ll = lambda x, y: (46.72 + (x - 700) / K, IM(M(24.69) - (y - 584) / K))
LOOP = Polygon([ll(x, y) for x, y in [(700, 488), (735, 472), (790, 466), (845, 470), (880, 490), (887, 530), (872, 580), (850, 603), (790, 603), (740, 596), (700, 590), (688, 560), (690, 520)]])
print('loop bounds', [round(v, 2) for v in LOOP.bounds])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
SA = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == 'Saudi Arabia'][0]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
NEW = SA.intersection(LOOP); print('   loop land new to V1', round(A(NEW.difference(V))), 'km2')
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
for n_, p in {'Riyadh': (46.72, 24.69), 'al-Hofuf': (49.58, 25.38), 'Abqaiq': (49.67, 25.93), 'Dammam': (50.1, 26.43), 'al-Kharj (out?)': (47.31, 24.15), 'Bahrain (out)': (50.58, 26.22), 'Qatar (out)': (51.2, 25.3)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
