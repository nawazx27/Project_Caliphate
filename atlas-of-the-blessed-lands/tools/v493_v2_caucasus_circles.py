"""Version 493 (Nawaz, red circles on the Version 492 preview (V2 filled with all of Kvemo Kartli and Derbent district): on the current-V2 half a circle
round the bend between the Greater Caucasus edge and the Derbent lobe, with a tick at the bottom of the bend; on the preview half two circles round the
notches on the Georgian edge (west of the Kvemo Kartli bulge, and the hook at Tbilisi): "Fill both of that and push the shape ... more upward to include the
entire thing", then, on a first try that drew the circles themselves as the edge: "I'm not saying the circle shape, but I'm saying fill it from the bottom
up. And the point near the bend, push it naturally upward."). Run after tools/v492_v2_whole_az_fill.py. The circles (placed by fitting V2's own drawn
outline in each half of his picture, ~1 km; tools/data/v493_circles.geojson) only say WHERE: inside each, V2's inward bend is filled from its bottom up to
its natural shape pushed up: V2's own edge is moved north, most at the bend's bottom (by UP=0.8 of the way from it to the circle's top) and easing\naway smoothly towards the circle's sides, and the land under it filled;
nothing is taken out. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(41, 40, 50, 43.5))]).buffer(0)
CIS = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'tools/data/v493_circles.geojson')))['features']]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys'])
loc = shapely.box(41.5, 40.0, 50.0, 43.5); VL = V.intersection(loc)
import numpy as np
from shapely.ops import transform
adds = []
for ci in CIS:
    x0, y0, x1, y1 = ci.bounds
    xs = np.arange(x0, x1 + 1e-9, 0.01); e = []
    for x in xs:                                       # V2's northern edge across the circle: the top of V2 in each thin column (at or below the circle's top)
        col = VL.intersection(shapely.box(x - 0.005, y0 - 1.5, x + 0.005, y1))
        e.append(col.bounds[3] if not col.is_empty else np.nan)
    e = np.array(e); ok = ~np.isnan(e)
    e = np.interp(xs, xs[ok], e[ok]) if ok.any() else e
    inside = np.array([ci.contains(Point(x, y)) or ci.distance(Point(x, y)) < 0.05 for x, y in zip(xs, e)])
    k = int(np.argmin(np.where(inside, e, 99))); xb, bottom = xs[k], e[k]
    DY = max(0.0, (y1 - bottom) * float(os.environ.get('UP', '0.8')))
    sig = (x1 - x0) / 4.5
    g = np.exp(-0.5 * ((xs - xb) / sig) ** 2) * np.clip(np.minimum(xs - x0, x1 - xs) / (0.15 * (x1 - x0)), 0, 1)
    n = np.minimum(e + DY * g, np.maximum(e, y1))      # the edge's own shape, raised most at the bend's bottom; never above the circle's top
    n = np.convolve(np.r_[[n[0]] * 4, n, [n[-1]] * 4], np.ones(9) / 9, mode='valid') if len(n) > 9 else n
    n = np.maximum(n, e)
    poly = Polygon(list(zip(xs, n)) + [(x1, y0 - 1.5), (x0, y0 - 1.5)]).buffer(0)
    fill = poly.difference(V).intersection(LAND)
    fill = unary_union([q for q in getattr(fill, 'geoms', [fill]) if not q.is_empty and A(q) > 2])
    print('circle at', round(ci.centroid.x, 2), round(ci.centroid.y, 2), '| bend bottom', round(xb, 2), 'E', round(bottom, 2), 'N -> raised', round(DY, 2), 'deg | filled', round(A(fill)) if not fill.is_empty else 0, 'km2')
    adds.append(fill)
X = unary_union([V] + [a.buffer(0.002) for a in adds if not a.is_empty]).buffer(0)
for ci in CIS:                                         # where a raised edge meets the old one, the sharp corner is rounded off (~12 km), only filling
    b = shapely.box(*ci.buffer(0.3).bounds)
    X = unary_union([X, X.intersection(b.buffer(0.3)).buffer(0.12, quad_segs=16).buffer(-0.12, quad_segs=16).intersection(b).intersection(LAND)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 5000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 20})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o); print('lost', round(A(V.difference(Y.buffer(0.002))), 2), 'km2')
for n, p in {'Tbilisi': (44.79, 41.72), 'Akhalkalaki': (43.49, 41.41), 'Ninotsminda': (43.59, 41.26), 'Gardabani': (45.09, 41.46), 'Majalis': (47.83, 42.12), 'Khuchni': (47.98, 41.94), 'Kayakent': (47.95, 42.39)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
