"""Version 422 (Nawaz, arrow across Eritrea from V1's south-east corner to the coast: "I meant this entire bit to coast line"). All land between V1's (shj)
eastern edge and the Red Sea shore, from the Sudanese border south to V1's southern tip (~12.95 N), is added: the whole of Eritrea (Massawa, Asmara, Assab) and the
Ethiopian land north of 12.95 N east of V1 (Tigray, northern Afar) so no gap is left; kept inside V3. Then rerun tools/v411_arabia.py and the ellipsoid tool."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
S0 = V.bounds[1]
NEW = unary_union([G['Eritrea'], G['Ethiopia'].intersection(shapely.box(35.5, S0, 43.5, 15.0)), G['Sudan'].intersection(shapely.box(35.5, S0, 39.0, 18.5))]).difference(V)
print('   added', round(A(NEW)), 'km2')
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
for n_, p in {'Asmara': (38.93, 15.32), 'Massawa': (39.45, 15.61), 'Assab': (42.74, 13.01), 'Mekelle (Ethiopia)': (39.47, 13.5), 'Axum': (38.72, 14.13), 'Djibouti (out)': (43.15, 11.59)}.items(): print('  ', n_, Y.contains(Point(p)))
print('Eritrea outside', round(A(G['Eritrea'].difference(Y.buffer(0.003)))), '| outside me2', round(A(Y.difference(V3.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
