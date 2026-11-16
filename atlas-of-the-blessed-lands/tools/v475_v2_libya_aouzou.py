"""Version 475 (Nawaz, a map of Chad with the Aouzou Strip in red along the Libyan border: "Preview Libya in v2 with this strip"). All of Libya and
the Aouzou Strip added to V2 (CALIPH.arb). The strip (Wikipedia: "extending south to a depth of about 100 kilometers into Chad's Borkou, Ennedi Ouest,
Ennedi Est, and Tibesti regions for an area of 114,000 km2"; added to Italian Libya by the Franco-Italian Agreement of 1935) is drawn as on his map:
Chad north of a straight line from the Chad-Libya-Niger tripoint (14.99 E 23.00 N) to the Sudan border on 24 E, its eastern end placed so the strip
measures Wikipedia's 114,000 km2 (~17.87 N; approximate, the treaty line was not traced). Enclosed pockets filled; V1 unchanged.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
V = MP(C['arb']['polys'])
NAMES = ['Libya']
T = G['Chad']; lo, hi = 17.0, 19.5
for _ in range(30):
    ye = (lo + hi) / 2; SW = T.intersection(Polygon([(14.991, 23.001), (24.3, ye), (24.3, 24), (14.0, 24), (14.0, 23.001)]))
    if A(SW) > 114000: lo = ye
    else: hi = ye
print('Aouzou Strip: south line ends at 24 E', round(ye, 3), 'N |', round(A(SW)), 'km2 | Aouzou town in:', SW.contains(Point(17.43, 21.82)), '| Bardai:', SW.contains(Point(16.99, 21.35)))
X = unary_union([V, G['Libya'].buffer(0.003), SW.buffer(0.003).intersection(T.buffer(0.003))]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 5000]).buffer(0)
print('added', round(A(X.difference(V))), 'km2 |', {n: round(100 * A(G[n].intersection(X)) / A(G[n]), 2) for n in NAMES}, '% in V2')
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('arb', C['arb']['km2'], '->', km, '| Tripoli', Y.contains(Point(13.19, 32.89)), '| Sabha', Y.contains(Point(14.43, 27.04)), '| Faya-Largeau (out)', Y.contains(Point(19.11, 17.92)))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
