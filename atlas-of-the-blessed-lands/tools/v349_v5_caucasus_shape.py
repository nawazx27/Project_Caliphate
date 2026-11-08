"""Version 349 PREVIEW (Nawaz liked the Version 347 crown push with his red line -> "Good, now, Give it this shape", with a map of the
Caucasus whose orange region's north edge runs from Taman east, sagging over the Kuban, to the Caspian north of Makhachkala). V5 (grm)
takes all Russian land south of that north edge (traced from his image; tools/data/v349_caucasus_edge.geojson; schematic, good to
~20-30 km) and keeps his red line from Version 347 (Azov block's north-east corner down to ~39.7E 44.8N) in place of the old straight
line; then ("Push it a bit upward") the traced edge is moved north by DY degrees (0.3, ~33 km). A design choice of the
author, not a historical holding."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
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
DY = float(os.environ.get('DY', '0.3'))   # "Push it a bit upward"
EDGE = [(p[0], p[1] + DY) for p in json.load(open(os.path.join(P, 'tools/data/v349_caucasus_edge.geojson')))['features'][0]['geometry']['coordinates']]
ring = [(36.5, 40.0), (36.5, EDGE[0][1])] + EDGE + [(49.3, EDGE[-1][1]), (49.3, 40.0)]
POD = Polygon(ring).buffer(0).intersection(G['643'][1])
RED = [(41.07, 47.51), (42.0, 47.32), (42.24, 47.10), (42.21, 46.66), (41.59, 46.22), (41.02, 45.88), (40.53, 45.60), (40.12, 45.19), (39.71, 44.79)]
POD = unary_union([POD, Polygon(RED + [(38.0, 44.79), (38.0, 47.45)]).buffer(0).intersection(G['643'][1])])
V5 = M('grm'); print('Caucasus shape, DY =', DY, 'adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Tuapse': (39.07, 44.10), 'Lazarevskoye': (39.33, 43.91), 'Novomikhaylovsky (Nicopsis)': (38.85, 44.26), 'Dzhubga': (38.70, 44.32), 'Maykop': (40.10, 44.61), 'Cherkessk': (42.06, 44.23), 'Nalchik': (43.61, 43.49), 'Vladikavkaz': (44.68, 43.02), 'Grozny': (45.69, 43.32), 'Makhachkala': (47.50, 42.98), 'Krasnodar': (38.98, 45.04), 'Stavropol': (41.97, 45.04), 'Kropotkin': (40.57, 45.44), 'Tikhoretsk': (40.13, 45.85), 'Salsk': (41.54, 46.47), 'Armavir': (41.12, 44.99), 'Volgodonsk (stays out)': (42.16, 47.51)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
