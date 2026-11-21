"""Version 486 (Nawaz, the Wikipedia article "Whole Azerbaijan" and its map IMG_5482 (North Azerbaijan, Iravan/Armenia, Borchaly, Derbent, South
Azerbaijan, Kirkuk shaded inside a red line): "Preview v2", then on the first preview (whole countries and provinces): "That's not what I sent. look at
the image, trace it, and I want it exactly like that." / "Trace it exactly."). The map was placed by fitting its own drawn borders and coastlines to the
atlas's (first an affine fit, ~5 km error; then, at "Trace the outline more accurately for v2", a 2nd-order polynomial fit, median ~1.5 px, ~1.5 km, and the
edge put on the CENTRE of the red line: tools/v486_build/trace2.py -> tools/data/v486_whole_azerbaijan_traced.geojson). Added to V2 (CALIPH.arb): that traced
area cut to land, plus Azerbaijan and Armenia whole (the map shades them whole; the ~5 km tracing error must not cut slivers off them). Enclosed pockets
filled; V1 unchanged. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
TR = shape(json.load(open(os.path.join(HERE, 'tools/data/v486_whole_azerbaijan_traced.geojson')))['geometry']).buffer(0)
TR = TR.buffer(-0.05).buffer(0.05)                          # the spur along the Borchaly label arrow and two knobs where the red line touches black lines off (~5 km; the Georgia and Dagestan strips are wider)
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(38, 30, 52, 44))]).buffer(0)
TR = TR.intersection(LAND)
print('traced area on land', round(A(TR)), 'km2 | in Georgia', round(A(TR.intersection(G['Georgia']))), '| in Russia', round(A(TR.intersection(G['Russia']))))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys'])
X = unary_union([V, G['Azerbaijan'].buffer(0.003), G['Armenia'].buffer(0.003), TR.buffer(0.003)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 50})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('arb', C['arb']['km2'], '->', km)
for n, p in {'Baku': (49.87, 40.41), 'Yerevan': (44.51, 40.18), 'Nakhchivan': (45.41, 39.21), 'Marneuli (Borchali)': (44.81, 41.48), 'Rustavi': (45.0, 41.55), 'Derbent': (48.29, 42.06), 'Tbilisi (out)': (44.79, 41.72), 'Makhachkala (out)': (47.5, 42.98)}.items():
    print('  ', n, Y.contains(Point(p)))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
