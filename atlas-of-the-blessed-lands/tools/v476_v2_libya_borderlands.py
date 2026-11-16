"""Version 476 (Nawaz, after the Aouzou Strip preview, the Wikipedia map "Libya-Chad territorial dispute map" with the Disputed Territory in red; no
words: read as V2 with Libya and this territory instead of the strip). All of Libya and the Libya-Chad Borderlands added to V2 (CALIPH.arb): the land of
Chad north of the line Libya claimed before the ICJ (1994 judgment for Chad), as in tools/v4_borderlands215.py: the 15th parallel from the Sudan border
west to 19 E, then straight north-west to the Chad-Niger border at 18 N (read off the map; the Aouzou Strip lies inside). Enclosed pockets filled;
V1 unchanged. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
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
T = G['Chad']
b = T.boundary.intersection(G['Niger'].boundary.buffer(0.02)).intersection(shapely.box(10, 17.9, 20, 18.1)); x18 = (b.bounds[0] + b.bounds[2]) / 2
SW = T.intersection(Polygon([(x18 - 1, 18.0), (x18 - 1, 24), (26, 24), (26, 15.0), (19, 15.0), (x18, 18.0)]))
print('Borderlands', round(A(SW)), 'km2 =', round(100 * A(SW) / A(T), 1), '% of Chad | Aouzou', SW.contains(Point(17.43, 21.82)), '| Bardai', SW.contains(Point(16.99, 21.35)), '| Faya-Largeau', SW.contains(Point(19.11, 17.92)), '| Fada', SW.contains(Point(21.58, 17.19)), '| Abeche (out)', SW.contains(Point(20.83, 13.83)))
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
Y = MP(o); print('arb', C['arb']['km2'], '->', km, '| Tripoli', Y.contains(Point(13.19, 32.89)), '| Sabha', Y.contains(Point(14.43, 27.04)), '| Faya-Largeau', Y.contains(Point(19.11, 17.92)))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
