"""Version 391 PREVIEW (Nawaz: "Add entire modern Germany to v5."): the whole of modern Germany (geo2.json country, with its islands) is added to V5 (grm);
V6 (tib) gets it too so V5 stays inside V6 (V7 already holds all of Germany). Before: 77.7% of Germany was in V5 and V6. DIR env = project dir (preview: a copy).
Run v386_areas_ellipsoid.py after."""
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
NAMES = ['Germany']
W = {n: G[[k for k, (nm, g) in G.items() if nm == n][0]][1] for n in NAMES}
def add(key):
    V = MP(C[key]['polys']); run = V
    for n, g in W.items(): print('  ', key, '+', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
    X = run.buffer(0)
    holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 2 < Polygon(h).representative_point().x < 20 and 45 < Polygon(h).representative_point().y < 56 and A(Polygon(h)) > 1]
    for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
    o = polys(unary_union([X] + holes).buffer(0), 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y5 = add('grm'); Y6 = add('tib')
Y7 = MP(C['sup']['polys'])
for n_, p in {'Berlin': (13.40, 52.52), 'Hamburg': (9.99, 53.55), 'Munich': (11.58, 48.14), 'Cologne': (6.96, 50.94), 'Dresden': (13.74, 51.05), 'Rostock': (12.10, 54.09), 'Flensburg': (9.43, 54.79),
              'Ruegen (Bergen)': (13.43, 54.42), 'Sylt': (8.31, 54.90), 'Copenhagen (Denmark, out)': (12.57, 55.68), 'Szczecin (Poland, out)': (14.55, 53.43), 'Prague (Czechia, out)': (14.42, 50.08)}.items():
    print('  ', n_, Y5.contains(Point(p)), round(Y5.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(MP(C['sas']['polys']).difference(Y5.buffer(0.01)))), '| grm outside tib', round(A(Y5.difference(Y6.buffer(0.01)))), '| tib outside sup', round(A(Y6.difference(Y7.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
