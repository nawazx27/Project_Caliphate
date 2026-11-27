"""Version 509 preview (Nawaz: "Preview the entire Jammu and Kashmir... princely state in v4"). V4 (me9) already holds the state as Pakistan's
official 2020 map draws it (Azad Kashmir, Gilgit-Baltistan, the Kashmir Valley, Jammu, Ladakh, Siachen; Version 264). The princely state of
1846-1947 also held the two China-administered parts: Aksai Chin and the Shaksgam (Trans-Karakoram) valley, ceded by Pakistan to China in
1963. Both are added from Natural Earth 10m admin-0 disputed areas (tools/data/china_kashmir_ne.geojson), which follow India's claim line.
The state's northern edge was never surveyed or agreed (Johnson line vs Macartney-MacDonald line), so that edge is one reading among several.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, shapely
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
ADD = [(f['properties']['BRK_NAME'], shape(f['geometry']).buffer(0)) for f in json.load(open(os.path.join(HERE, 'tools/data/china_kashmir_ne.geojson')))['features']]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
polys = C['me9']['polys']; W = box(70, 30, 82, 38)
near = [i for i, r in enumerate(polys) if box(*Polygon(r[0]).bounds).intersects(W)]
V = unary_union([Polygon(polys[i][0], polys[i][1:]).buffer(0) for i in near])
for n, g in ADD: print(f'{n}: {round(A(g))} km2, already in V4 {round(A(g.intersection(V)))} km2')
N = unary_union([V] + [g for _, g in ADD]).buffer(0)
holes = [Polygon(h) for q in getattr(N, 'geoms', [N]) for h in q.interiors if A(Polygon(h)) < 2000]   # slivers between the claim lines and V4
if holes: print('slivers filled', round(sum(A(h) for h in holes), 1), 'km2'); N = unary_union([N] + holes)
N = shapely.set_precision(N, 0.001)
new = [[[[round(a, 3), round(b, 3)] for a, b in orient(q, 1.0).exterior.coords]] + [[[round(a, 3), round(b, 3)] for a, b in h.coords] for h in orient(q, 1.0).interiors] for q in getattr(N, 'geoms', [N])]
C['me9']['polys'] = [r for i, r in enumerate(polys) if i not in near] + new
print('added', round(A(N) - A(V)), 'km2')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
