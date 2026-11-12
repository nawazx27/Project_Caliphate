"""Version 372 PREVIEW (Nawaz, phone screenshot of V5 in the dark theme with a red line from north of the Caspian down to the Caucasus: "Preview").
The line, georeferenced on the screenshot (Mercator fitted on the Black Sea's west and east ends and its south shore; checked on the Caspian's
north and south tips, about 0.1 deg): from the Kazakh-Russian border north of the Caspian (~50.1E 47.85N) south-west across the lower Volga
(~48.8E 47.3N, ~47.8E 46.7N) to ~46.9E 45.6N, then due south along ~46.4E to the Caucasus (~46.4E 42.45N). V5 (grm) takes the Russian land
east of the line, between it and the Caspian: Astrakhan and the Volga delta, eastern Kalmykia (Lagan), north-eastern Dagestan (Kizlyar,
Khasavyurt). Drawn exactly on his line for now (no district snapping). DIR env = project dir (preview: a copy)."""
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
V5 = MP(C['grm']['polys']); RU = G['643'][1]
LINE = [(50.11, 47.85), (48.8, 47.28), (47.8, 46.71), (47.24, 46.14), (46.88, 45.56), (46.65, 45.26), (46.43, 44.67), (46.43, 43.47), (46.38, 42.45)]
CLOSE = [(47.6, 42.3), (49.5, 43.5), (51.5, 45.5), (51.5, 47.85)]          # back through Dagestan already in V5, the Caspian and Kazakhstan
POLY = Polygon(LINE + CLOSE)
ADD = POLY.intersection(RU).difference(V5)
for g in sorted(getattr(ADD, 'geoms', [ADD]), key=lambda g: -A(g))[:4]: print('  piece', round(A(g)), 'km2 at', [round(c, 2) for c in g.representative_point().coords[0]])
print('  + Russia east of the line', round(A(ADD)), 'km2')
X = unary_union([V5, ADD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Astrakhan': (48.03, 46.35), 'Volga delta mouth': (48.6, 45.9), 'Lagan': (47.37, 45.39), 'Kizlyar': (46.71, 43.85), 'Khasavyurt': (46.59, 43.25), 'Kizilyurt': (46.87, 43.2),
              'Akhtubinsk (out?)': (46.21, 48.28), 'Elista (out)': (44.27, 46.31), 'Grozny (out)': (45.69, 43.32), 'Volgograd (out)': (44.5, 48.71)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(Y.difference(MP(C['sup']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
