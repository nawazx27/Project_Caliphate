"""Version 427 (Nawaz, Apple Maps screenshots: Kharg and Kharku islands circled off Bushehr, and "in V1 at Bahrain and this one"). V1 (shj) gets the whole of
Bahrain (all its islands) and Kharg and Kharku islands (Iran, off Bandar Ganaveh). Kept inside V2 (me2). Run v386_areas_ellipsoid.py after."""
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
XL = C.get('extraLand', {}); xl = [Polygon(r[0], r[1:]) for k in XL for r in (XL[k] if isinstance(XL[k], list) else []) if isinstance(r, list) and r and isinstance(r[0], list) and len(r[0]) > 2 and isinstance(r[0][0], list)] if False else []
KH = G['Iran'].intersection(shapely.box(50.15, 29.1, 50.55, 29.45))
NEW = unary_union([G['Bahrain'], KH]).difference(V); print('   added: Bahrain', round(A(G['Bahrain'])), 'km2; Kharg/Kharku', round(A(KH), 1), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0).intersection(V2.buffer(0.005)); X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o)
for n_, p in {'Manama': (50.58, 26.22), 'Hawar islands': (50.78, 25.65), 'Kharg': (50.32, 29.25), 'Kharku': (50.40, 29.32)}.items(): print('  ', n_, Y.distance(Point(p)) < 0.02)
print('Bahrain outside', round(A(G['Bahrain'].difference(Y.buffer(0.003))), 2))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
