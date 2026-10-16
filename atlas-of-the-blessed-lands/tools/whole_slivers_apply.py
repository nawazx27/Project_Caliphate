"""Version 145: adds tools/data/whole_slivers_<v>.geojson (from tools/whole_slivers.py) to that version in shapely (polygon-clipping
was too slow for thousands of hairline pieces), snapped to the 0.001° grid with shapely.union_all(grid_size=0.001) so the result stays valid;
holes under 5,000 km² are filled as in the other tools; exteriors counter-clockwise, holes clockwise (polygon-clipping's order).
km2 recounted like the JS tools (d3.geoArea × 6371.0088²). Rows unchanged. Run: python3 tools/whole_slivers_apply.py <x|xb> [geojson, default tools/data/whole_slivers_<v>.geojson]"""
import json, os, subprocess, sys, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); k = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F = os.path.join(P, 'src/caliph.json'); C = json.load(open(F))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
N = [shape(f['geometry']) for f in json.load(open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(P, 'tools/data/whole_slivers_%s.geojson' % k)))['features']]
U = shapely.union_all([shapely.make_valid(g) for g in [X] + N], grid_size=0.001)
U = MultiPolygon([q for q in getattr(U, 'geoms', [U]) if q.geom_type == 'Polygon'])
out = []
for p in getattr(U, 'geoms', [U]):
    if p.geom_type != 'Polygon' or p.is_empty: continue
    p = orient(Polygon(p.exterior, [h for h in p.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(x, 3), round(y, 3)] for x, y in r.coords] for r in [p.exterior, *p.interiors]])
before = C[k]['km2']; C[k]['polys'] = out
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C[k]['km2'] = km2
json.dump(C, open(F + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F + '.tmp', F)   # atomic: a stopped run never leaves a half-written file
print(k, before, '->', km2, '(+', km2 - before, ') polygons', len(out))
