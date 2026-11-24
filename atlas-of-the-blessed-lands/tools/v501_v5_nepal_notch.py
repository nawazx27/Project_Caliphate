"""Version 501 (Nawaz, a phone screenshot of V5 north of Nepal with an arrow at the inward hook of its border: "Fill"). The pocket of outside
land under the hook (about 83.63-84.16 E, 29.84-30.44 N) is added to V5 (grm), closed on the east at the hook's own tip (84.158 E), in
the border's stair-step style. V6 (tib) and V7 (sup) already hold it (whole Tibetan Plateau). DIR env = project dir. Run v386 after."""
import json, os
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
polys = C['grm']['polys']; W = box(83.5, 29.5, 84.158, 30.46)
near = [i for i, r in enumerate(polys) if box(*Polygon(r[0]).bounds).intersects(W)]
V = unary_union([Polygon(polys[i][0], polys[i][1:]).buffer(0) for i in near])
out = W.difference(V)
pocket = [q for q in getattr(out, 'geoms', [out]) if q.contains(Point(83.9, 30.2))][0]
print('pocket', round(A(pocket)), 'km2, bounds', [round(v, 3) for v in pocket.bounds])
for k in ['tib', 'sup']:
    T = unary_union([Polygon(r[0], r[1:]).buffer(0) for r in C[k]['polys'] if box(*Polygon(r[0]).bounds).intersects(W)])
    print(k, 'holds it:', round(100 * pocket.intersection(T).area / pocket.area, 2), '%')
N = unary_union([V, pocket.buffer(0.0005, join_style=2)]).buffer(0)
new = []
for q in getattr(N, 'geoms', [N]):
    q = orient(q, 1.0)
    new.append([[[round(a, 3), round(b, 3)] for a, b in q.exterior.coords]] + [[[round(a, 3), round(b, 3)] for a, b in h.coords] for h in q.interiors])
C['grm']['polys'] = [r for i, r in enumerate(polys) if i not in near] + new
print('replaced', len(near), 'polygons with', len(new))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
