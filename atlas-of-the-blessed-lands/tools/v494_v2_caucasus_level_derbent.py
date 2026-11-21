"""Version 494 (Nawaz, red marks on the Version 492 preview (V2 filled with all of Kvemo Kartli and Derbent district): two loops round the notches on the
Georgian edge, and on the current-V2 half a loop round the whole Derbent lobe up the Dagestan coast: "just fill those to until level with the gap and push
the exact shape of the derbent area upward"; the Version 493 tries (circles as edges, then bends raised) were wrong). Run after tools/v492_v2_whole_az_fill.py.
Marks: tools/data/v494_marks.geojson (placed by fitting V2's own drawn outline in each half of his picture, ~1 km; convex hulls of his strokes).
(1) Each Georgian notch inside a loop is filled up to the level of its lower shoulder, with a natural curve across its mouth (a closing of V2's edge,
RC_W 0.6 / RC_T 0.3 deg) instead of a flat ruler line.
(2) The Derbent lobe (V2 north of 41.6 N and east of 47.55 E, in Russia and Azerbaijan) is enlarged as one piece in its exact shape about its base on the coast (never swept:
a sweep made a straight, stepped side) until its tip reaches the top of his loop, cut to land and joined to V2; the lobe's own run along the coast in between is filled. Nothing is taken out.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, shapely.affinity, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(41, 40, 50, 44))]).buffer(0)
MK = [(f['properties']['side'], shape(f['geometry']).buffer(0)) for f in json.load(open(os.path.join(HERE, 'tools/data/v494_marks.geojson')))['features']]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); VL = V.intersection(shapely.box(41, 39.5, 50, 44))
adds = []
# (1) the Georgian notches, filled level
for side, mk in MK:
    if side != 'R': continue
    x0, y0, x1, y1 = mk.bounds
    xs = np.arange(x0, x1 + 1e-9, 0.01); e = []
    for x in xs:
        col = VL.intersection(shapely.box(x - 0.005, y0 - 1, x + 0.005, y1))
        e.append(col.bounds[3] if not col.is_empty else np.nan)
    e = np.array(e); k = int(np.nanargmin(e)); left, right = np.nanmax(e[:k + 1]), np.nanmax(e[k:])
    level = min(left, right)
    Rc = float(os.environ.get('RC_W', '0.6')) if x0 < 43.5 else float(os.environ.get('RC_T', '0.3'))   # a closing of V2's edge wide enough to span the notch's mouth:
    fill = VL.buffer(Rc, quad_segs=24).buffer(-Rc, quad_segs=24).intersection(shapely.box(x0, y0 - 1, x1, level + 0.02))  # the notch filled up to its shoulders' level
    fill = fill.intersection(mk.buffer(0.05)).intersection(LAND).difference(V)                                     # with a natural curve, not a ruler line
    fill = unary_union([q for q in getattr(fill, 'geoms', [fill]) if not q.is_empty and q.distance(V) < 0.01 and A(q) > 2])
    print('notch at', round(xs[k], 2), 'E: bottom', round(e[k], 2), 'N, filled level to', round(level, 2), 'N |', round(A(fill)) if not fill.is_empty else 0, 'km2')
    adds.append(fill)
# (2) the Derbent lobe moved north in its exact shape
mk = [m for s, m in MK if s == 'L'][0]
lobe = V.intersection(shapely.box(47.55, 41.6, 49.5, 43.5)).intersection(unary_union([G['Russia'], G['Azerbaijan']]).buffer(0.01))
lobe = max(getattr(lobe, 'geoms', [lobe]), key=lambda q: q.area)
o0 = min(lobe.exterior.coords if lobe.geom_type == 'Polygon' else [], key=lambda q: q[1] - 0.3 * q[0])   # the lobe's base on the coast side
fct = (mk.bounds[3] - o0[1]) / (lobe.bounds[3] - o0[1])
up = shapely.affinity.scale(lobe, fct, fct, origin=o0)    # the same shape made larger (never swept), so its tip reaches the top of his loop
run = up; DY = mk.bounds[3] - lobe.bounds[3]; DX = 0
# as before, the lobe runs to the shore: on each row, the land from the enlarged lobe's western edge east to the sea
rows = []
for y in np.arange(up.bounds[1], up.bounds[3], 0.01):
    r = up.intersection(shapely.box(40, y, 52, y + 0.01))
    if not r.is_empty: rows.append(shapely.box(r.bounds[0], y, 52, y + 0.012))
up = unary_union([up] + rows).intersection(LAND)
up = unary_union([g for g in getattr(up, 'geoms', [up]) if g.distance(lobe) < 0.05 or g.intersects(lobe)])
up = up.buffer(0.08, quad_segs=16).buffer(-0.08, quad_segs=16).intersection(LAND)   # the sharp corner where it meets the old edge rounded off
up = unary_union([up.buffer(-0.1, quad_segs=16).buffer(0.1, quad_segs=16), up.intersection(shapely.box(40, 30, 52, up.bounds[3] - 0.35))]).intersection(LAND)   # its flat top rounded
run = up
lob = unary_union([up, run]).intersection(LAND).difference(V)
print('Derbent lobe: tip', round(lobe.bounds[3], 2), 'N -> ', round(mk.bounds[3], 2), 'N (moved', round(DY, 2), 'N,', round(DX, 2), 'E) |', round(A(lob)), 'km2')
adds.append(lob)
X = unary_union([V] + [a.buffer(0.002) for a in adds if not a.is_empty]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 5000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 20})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o); print('lost', round(A(V.difference(Y.buffer(0.002))), 2), 'km2')
for n, p in {'Tbilisi': (44.79, 41.72), 'Akhalkalaki': (43.49, 41.41), 'Ninotsminda': (43.59, 41.26), 'Izberbash': (47.87, 42.56), 'Kaspiysk': (47.64, 42.88), 'Makhachkala': (47.5, 42.98), 'Buynaksk': (47.12, 42.82)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
