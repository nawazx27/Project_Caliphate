"""Version 461 (Nawaz, red stroke on his phone screenshot below V1's south-east edge in Ethiopia, from the edge near 42.15 E 9.33 N down and south-west
to the edge near 39.66 E 6.89 N: "Fill and preview with full map"). Stroke placed by an affine fit on four lakes of the screenshot (Tana, Abbe, Abaya,
Turkana's north tip; residuals under 7 km). The land between V1's edge and the stroke goes into V1 (shj); the stroke's ends are taken onto V1's own edge.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union, nearest_points
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ST = [(42.145, 9.023), (42.264, 8.791), (42.061, 8.711), (41.569, 7.966), (40.919, 7.453), (40.592, 7.021), (39.705, 6.972)]
Pa = nearest_points(V.boundary, Point(42.149, 9.334))[0]; Pb = nearest_points(V.boundary, Point(39.664, 6.893))[0]
POLY = Polygon([(Pa.x, Pa.y)] + ST + [(Pb.x, Pb.y), (Pb.x - 0.4, Pb.y + 0.4), (Pa.x - 0.4, Pa.y + 0.4)]).buffer(0)
add = POLY.intersection(G['Ethiopia']).difference(V)
print('filled', round(A(add)), 'km2')
X = unary_union([V, add.buffer(0.003).intersection(G['Ethiopia'].buffer(0.003))]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o)
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km
print('shj', old, '->', km, '| Ethiopia in V1', round(100 * G['Ethiopia'].intersection(Y).area / G['Ethiopia'].area), '%')
for n_, p in {'Harar': (42.12, 9.31), 'Jijiga': (42.8, 9.35), 'Goba (Bale)': (39.98, 7.0), 'Robe': (40.0, 7.12), 'Ginir': (40.7, 7.13), 'Dire Dawa': (41.86, 9.6)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
