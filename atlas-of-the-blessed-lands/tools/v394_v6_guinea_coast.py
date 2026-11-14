"""Version 394 PREVIEW (Nawaz, on the Version 393 full-map picture, a red loop round the West African gap between Liberia/Guinea and Nigeria: "Fill").
Run AFTER tools/v392_v6_sokoto_adamawa.py and tools/v393_v6_nigeria_south.py: the four modern countries in the loop, Cote d'Ivoire, Ghana, Togo and Benin, are added WHOLE
to V6 (tib) and V7 (sup). (Liberia, Sierra Leone and Guinea are already inside; Cameroon, Equatorial Guinea and Sao Tome are outside the loop and stay out.) V5 not changed.
DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
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
NAMES = ["Côte d'Ivoire", 'Ghana', 'Togo', 'Benin']
W = {n: G[[k for k, (nm, g) in G.items() if nm == n][0]][1] for n in NAMES}
def add(key):
    V = MP(C[key]['polys']); run = V
    for n, g in W.items(): print('  ', key, '+', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
    X = run.buffer(0)
    holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 2 < Polygon(h).representative_point().x < 16 and 3 < Polygon(h).representative_point().y < 14 and A(Polygon(h)) > 0.5]
    for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
    o = polys(unary_union([X] + holes).buffer(0), 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y6 = add('tib'); Y7 = add('sup')
for n_, p in {'Abidjan': (-4.03, 5.36), 'Yamoussoukro': (-5.28, 6.82), 'San-Pedro': (-6.64, 4.75), 'Accra': (-0.19, 5.6), 'Kumasi': (-1.62, 6.69), 'Tamale': (-0.85, 9.4), 'Lome': (1.22, 6.13), 'Cotonou': (2.42, 6.37), 'Porto-Novo': (2.63, 6.5), 'Parakou': (2.6, 9.34), 'Monrovia (already in)': (-10.8, 6.3), 'Douala (Cameroon, out)': (9.7, 4.05), 'Malabo (out)': (8.78, 3.75)}.items():
    print('  ', n_, Y6.contains(Point(p)), round(Y6.distance(Point(p)) * 111, 1), 'km')
print('grm outside tib', round(A(MP(C['grm']['polys']).difference(Y6.buffer(0.01)))), '| tib outside sup', round(A(Y6.difference(Y7.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
