"""Version 421 (Nawaz, phone screenshot with an arrow at the Sudanese Red Sea coast south of Port Sudan: "Bring that to the shore"). The Sudanese land between
V1's (shj) eastern edge (from the Egyptian Empire map) and the Red Sea shore, from 20.5 N south to the Eritrean border, is added to V1. Then rerun tools/v411_arabia.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
SD = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == 'Sudan'][0]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
NEW = SD.intersection(shapely.box(36.0, 14.5, 40.0, 20.5)).difference(V)
NEW = unary_union([q for q in getattr(NEW, 'geoms', [NEW]) if q.buffer(0.02).intersects(V)])
print('   coast strip added', round(A(NEW)), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0).intersection(V3.buffer(0.002)); X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o)
for n_, p in {'Suakin': (37.33, 19.1), 'Tokar': (37.73, 18.43), 'Aqiq': (38.19, 18.23), 'Kassala': (36.4, 15.45)}.items(): print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
