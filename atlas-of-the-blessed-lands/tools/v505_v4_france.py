"""Version 505 preview (Nawaz: "Preview V4 with France"). V4 (me9) + all of metropolitan France (mainland and its islands; Corsica was
already in V4), taken whole from the base map; the overseas departments are not added. The polygons of V4 that touch France are unioned
with it so no seam is left. DIR env = project dir (run on a preview copy unless he says to apply). Run v386_areas_ellipsoid.py after."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
FR = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == 'France'][0]
EU = box(-6, 41, 10, 52)
FR = unary_union([q for q in getattr(FR, 'geoms', [FR]) if q.intersects(EU)])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
polys = C['me9']['polys']; W = FR.buffer(0.05)
near = [i for i, r in enumerate(polys) if box(*Polygon(r[0]).bounds).intersects(W) and Polygon(r[0], r[1:]).buffer(0).intersects(W)]
V = unary_union([Polygon(polys[i][0], polys[i][1:]).buffer(0) for i in near])
print('France (metropolitan)', round(A(FR)), 'km2 | already in V4', round(A(FR.intersection(V))), 'km2 | added', round(A(FR.difference(V))), 'km2')
N = unary_union([V, FR]).buffer(0)
new = []
for q in getattr(N, 'geoms', [N]):
    q = orient(q, 1.0)
    new.append([[[round(a, 3), round(b, 3)] for a, b in q.exterior.coords]] + [[[round(a, 3), round(b, 3)] for a, b in h.coords] for h in q.interiors])
C['me9']['polys'] = [r for i, r in enumerate(polys) if i not in near] + new
for n in ['Monaco', 'Belgium', 'Luxembourg', 'Switzerland', 'Italy', 'Germany']:
    g = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == n]
    if g: print('  ', n, 'in V4 after:', round(100 * A(g[0].intersection(N)) / A(g[0]), 1), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
