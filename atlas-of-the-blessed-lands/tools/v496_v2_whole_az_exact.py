"""Version 496 (Nawaz, his "Whole Azerbaijan" map again, after the check that V2 held 99.93% of its traced shaded area, ~320 km2 left out where the
Version 491 build had rounded off small knobs (east of Tbilisi, near Lagodekhi), and ~200 km2 beyond the red line (Derbent city, the coast to Derbent):
"Make that 99.93% to 100% and I only want from this image"). In Georgia and Russia, V2 (CALIPH.arb) is set to exactly the traced shaded area on land
(tools/data/v486_whole_azerbaijan_traced.geojson, exactly; only the hairline along the Borchaly label's arrow dropped); Azerbaijan and Armenia stay
whole (the map shades them whole); the rest of the traced area is added where V2 lacked it. Derbent city and the coast fill north of the red line go
(his "only from this image" replaces "Add derbent"). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
T = shape(json.load(open(os.path.join(HERE, 'tools/data/v486_whole_azerbaijan_traced.geojson')))['geometry']).buffer(0)
LAND = unary_union([g for g in G.values() if g.intersects(T.buffer(0.5))]).buffer(0)
ARROW = box(44.2, 41.7, 44.85, 42.05)                    # the Borchaly label's arrow, which the trace caught as a hairline running out past the red line
TL = unary_union([T.difference(ARROW), T.intersection(ARROW).buffer(-0.015).buffer(0.015)]).intersection(LAND)   # everywhere else exactly as traced
GR = unary_union([G['Georgia'], G['Russia'].intersection(box(40, 40, 50, 45))]).buffer(0.002)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys'])
X = unary_union([V.difference(GR), TL.buffer(0.001), G['Azerbaijan'].buffer(0.003).difference(GR), G['Armenia'].buffer(0.003).difference(GR)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 50]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o)
TLL = T.intersection(LAND)
print('traced shaded land inside V2:', round(100 * A(TLL.intersection(Y.buffer(0.002))) / A(TLL), 3), '% | outside', round(A(TLL.difference(Y.buffer(0.002))), 1), 'km2')
ext = Y.intersection(GR).difference(T.buffer(0.01))
print('V2 in Georgia/Russia beyond the red line:', round(A(ext), 1) if not ext.is_empty else 0, 'km2 | added', round(A(Y.difference(V))), 'km2, removed', round(A(V.difference(Y))), 'km2')
for n, p in {'Derbent (map line ends south of it)': (48.29, 42.06), 'Marneuli': (44.81, 41.48), 'Rustavi': (45.0, 41.55), 'Tbilisi': (44.79, 41.72)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
