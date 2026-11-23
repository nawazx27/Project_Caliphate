"""Version 497 (Nawaz, on the check that V4, V5 and V6 held 99.99% of his Whole Azerbaijan red-line area, ~30 km2 of slivers on the Georgia-Azerbaijan
border near Lagodekhi left out: "Fill"). The land inside the red line (tools/data/v496_whole_azerbaijan_redline.geojson) that V4 (me9), V5 (grm) and V6
(tib) lack is added to each as small pieces overlapping it by ~1 km (the outlines themselves untouched). V7 (sup) and V2 already hold it all. V3 (me2) is
NOT filled: its standing rule keeps it to official lines of the countries it lists (its missing piece is the Dagestan strip to Derbent, in Russia).
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = box(38, 30, 52, 45)
LAND = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(B)])
TL = shape(json.load(open(os.path.join(HERE, 'tools/data/v496_whole_azerbaijan_redline.geojson')))['geometry']).buffer(0).intersection(LAND)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for key in ['me9', 'grm', 'tib']:
    V = unary_union([Polygon(r[0], r[1:]).buffer(0) for r in C[key]['polys'] if box(*Polygon(r[0]).bounds).intersects(B)])
    miss = TL.difference(V.buffer(0.002))
    miss = [q for q in getattr(miss, 'geoms', [miss]) if not q.is_empty and q.area > 0]
    piece = unary_union([q.buffer(0.01).intersection(LAND.buffer(0.003)) for q in miss]).buffer(0) if miss else None
    if piece is None or piece.is_empty: print(key, 'nothing missing'); continue
    for q in getattr(piece, 'geoms', [piece]):
        if q.geom_type == 'Polygon': C[key]['polys'].append([[[round(a, 3), round(b, 3)] for a, b in orient(Polygon(q.exterior), 1.0).exterior.coords]])
    Y = unary_union([V, piece])
    o = TL.difference(Y.buffer(0.002))
    print(key, 'filled', round(sum(A(q) for q in miss), 1), 'km2 | inside now', round(100 * (1 - (A(o) if not o.is_empty else 0) / A(TL)), 3), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
