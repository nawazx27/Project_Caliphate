"""Version 412 PREVIEW (Nawaz: "Give Egypt its natural borders in v1", south edge chosen: the First Cataract at Aswan). V1 (shj) gets Egypt from the Mediterranean
to the First Cataract (~24.03 N), between the Western (Libyan) Desert and the Red Sea, with the oases (Siwa, Bahariya, Farafra, Dakhla, Kharga); Lower Nubia (Lake Nasser,
Abu Simbel) and the south-east corner below the cataract stay out. The cataract line is carried straight across both deserts (no natural feature there).
Then tools/v411_arabia.py must be rerun so V2 still holds V1. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
SOUTH = float(os.environ.get('SOUTH', '24.03'))   # the First Cataract at Aswan (between Aswan and the old dam, ~24.03 N)
EG = [g for k, (n, g) in G.items() if n == 'Egypt'][0]
NEW = EG.intersection(shapely.box(24.0, SOUTH, 37.0, 32.0))
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
print('   Egypt north of the First Cataract', round(A(NEW)), 'km2; new to V1', round(A(NEW.difference(V))))
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x < 36]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
def polys_lakes(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
o = polys_lakes(unary_union([X] + holes).buffer(0).intersection(V3.buffer(0.002))); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Cairo': (31.24, 30.04), 'Alexandria': (29.92, 31.2), 'Luxor': (32.64, 25.69), 'Aswan': (32.9, 24.09), 'Siwa': (25.52, 29.2), 'Kharga': (30.55, 25.44), 'Dakhla (Mut)': (28.98, 25.49), 'Hurghada': (33.81, 27.26), 'Marsa Alam': (34.89, 25.07), 'Marsa Matruh': (27.24, 31.35), 'Abu Simbel (Nubia, out)': (31.63, 22.34), 'Berenice (out)': (35.48, 23.95)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('Egypt left out', round(A(EG.difference(Y))), 'km2 | shj outside me2', round(A(Y.difference(V3.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
