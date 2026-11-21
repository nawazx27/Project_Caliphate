"""Version 492 (Nawaz, the Wikipedia article "Whole Azerbaijan" again, after the check that V2 held Derbent city but only 63% of Derbentsky district
and 55% of Kvemo Kartli ("Borchali ... part of the Kvemo Kartli province"): "Don't remove anything only fill"). The rest of Derbentsky district (Overture)
and of Kvemo Kartli (Natural Earth admin-1) added to V2 (CALIPH.arb), cut to Russia and Georgia; nothing taken out; pockets filled.
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
D = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'tools/data/v492_derbent_district_kvemo_kartli.geojson')))['features']]
ADD = unary_union([D[0].intersection(G['Russia'].buffer(0.003)), D[1].intersection(G['Georgia'].buffer(0.003))])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys'])
X = unary_union([V, ADD.buffer(0.003)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 2000]).buffer(0)
add = X.difference(V); print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in ['Russia', 'Georgia'] if G[k].intersects(add)})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o); print('nothing removed:', round(A(V.difference(Y.buffer(0.002))), 2), 'km2 lost')
print('Derbentsky', round(100 * A(D[0].intersection(Y)) / A(D[0]), 1), '% | Kvemo Kartli', round(100 * A(D[1].intersection(Y)) / A(D[1]), 1), '% | Tbilisi', Y.contains(Point(44.79, 41.72)), '| Bolnisi', Y.contains(Point(44.54, 41.45)), '| Tsalka', Y.contains(Point(44.09, 41.6)))
C['arb']['polys'] = o
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
