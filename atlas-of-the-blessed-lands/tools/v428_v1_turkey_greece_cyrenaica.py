"""Version 428 (Nawaz, Wikipedia's orthographic map of the Levant in its broad, historical meaning (the Eastern Mediterranean): "Add Turkey, Greece, and the portion
of Libya in the image to V1"). V1 (shj) gets all of Türkiye and all of Greece (every island, with the extraLand islets such as Kastellorizo) and eastern Libya
(Cyrenaica) east of the map's straight line, read as 20.0 E, from the Gulf of Sidra to the Sudan/Chad border. Kept inside V2 (me2). Run v386_areas_ellipsoid.py after."""
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
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
X0 = float(os.environ.get('LIBYA_W', '20.0'))
XL = MP(C['extraLand']['polys'])
TG = unary_union([G['Türkiye'], G['Greece']])
isl = XL.intersection(TG.buffer(0.6)).intersection(V2.buffer(0.01))     # extraLand islets of Greece/Türkiye already held by V2
CY = G['Libya'].intersection(shapely.box(X0, 18.0, 26.0, 34.0))
for n, g in [('Türkiye', G['Türkiye']), ('Greece', G['Greece']), ('Cyrenaica (Libya east of %.1f E)' % X0, CY)]: print('  ', n, round(A(g.difference(V))), 'km2 new')
NEW = unary_union([TG, CY, isl]).difference(V)
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000]
X = unary_union([X] + holes).intersection(V2.buffer(0.004)); X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.005: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o)
for n_, p in {'Istanbul': (28.97, 41.01), 'Edirne': (26.56, 41.68), 'Kars': (43.1, 40.6), 'Athens': (23.73, 37.98), 'Thessaloniki': (22.94, 40.64), 'Corfu': (19.92, 39.62), 'Heraklion (Crete)': (25.13, 35.34), 'Rhodes': (28.22, 36.43), 'Benghazi': (20.07, 32.12), 'Tobruk': (23.96, 32.08), 'Kufra': (23.31, 24.2), 'Sirte (out)': (16.59, 31.2)}.items():
    print('  ', n_, Y.contains(Point(p)) or Y.distance(Point(p)) < 0.01)
print('Greece outside', round(A(G['Greece'].difference(Y.buffer(0.003)))), '| Turkey outside', round(A(G['Türkiye'].difference(Y.buffer(0.003)))), '| outside me2', round(A(Y.difference(V2.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
