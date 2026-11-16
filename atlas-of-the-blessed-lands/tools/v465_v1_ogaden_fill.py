"""Version 465 (Nawaz, red strokes on the Version 464 preview: one from Lake Turkana's north end along the Ethiopia-Kenya border to Moyale and then
north-east across the Ogaden to the Ethiopia-Somaliland border near Jijiga, and one from there north-east across Somaliland to the Gulf of Aden coast).
Placed by fitting V1's drawn outline in that picture (median error under 1 pixel, ~2 km). All land between V1 and the strokes goes into V1 (shj), the
strokes smoothed into one curve as drawn. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
V = MP(C['shj']['polys'])
ST = [(36.441, 4.331), (36.978, 4.353), (37.515, 4.181), (37.944, 3.753), (38.481, 3.367), (39.126, 3.495), (39.663, 4.288), (40.951, 5.679),
      (42.24, 7.066), (43.314, 8.237), (43.486, 8.832), (44.173, 9.934), (44.925, 10.99), (45.0, 11.5)]
def chaikin(Pt, n=4):
    for _ in range(n):
        Q = [Pt[0]]
        for (x0, y0), (x1, y1) in zip(Pt[:-1], Pt[1:]): Q += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        Pt = Q + [Pt[-1]]
    return Pt
POLY = Polygon(chaikin(ST) + [(45.0, 13.5), (36.0, 13.5), (36.0, 4.35)]).buffer(0)
LAND = unary_union([G[k] for k in ['Ethiopia', 'Somaliland', 'Kenya', 'Djibouti', 'Somalia'] if k in G])
add = POLY.intersection(LAND).difference(V)
print('filled', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Ethiopia', 'Somaliland', 'Kenya', 'Somalia']})
X = unary_union([V, add.buffer(0.003).intersection(LAND.buffer(0.003))]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]
X = unary_union([X] + holes).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km
print('shj', old, '->', km, '| Ethiopia in V1', round(100 * G['Ethiopia'].intersection(Y).area / G['Ethiopia'].area), '%')
for n_, p in {'Moyale': (39.05, 3.52), 'Borama': (43.18, 9.94), 'Hargeisa': (44.06, 9.56), 'Berbera': (45.03, 10.44), 'Gode': (43.55, 5.95), 'Kebri Dahar': (44.27, 6.73), 'Dolo': (42.07, 4.18), 'Mega': (38.3, 4.05)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
