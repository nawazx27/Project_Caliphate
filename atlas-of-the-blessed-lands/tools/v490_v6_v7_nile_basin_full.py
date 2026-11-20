"""Version 490 (Nawaz, on the check that V6 held 99.999% of the traced Nile basin, a 21 km2 sliver on the South Sudan-DR Congo watershed near Yei left
out: "Make sure it's 100% inside."). The traced basin's land outside V6 (tib) and V7 (sup) (tools/data/v453_nile_basin_traced.geojson, cut to land)
is added to each, joined with a ~1 km overlap so no hairline remains. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = shape(json.load(open(os.path.join(HERE, 'tools/data/v453_nile_basin_traced.geojson')))['geometry']).buffer(0)
LAND = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(B)])
BL = B.intersection(LAND)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
BX = box(20, -6, 42, 33)
for key in ['tib', 'sup']:
    polys = [Polygon(r[0], r[1:]) for r in C[key]['polys']]
    near = [i for i, p in enumerate(polys) if box(*p.exterior.bounds).intersects(BX)]
    V = unary_union([polys[i].buffer(0) for i in near])
    add = BL.difference(V.buffer(0.002))
    add = unary_union([g for g in getattr(add, 'geoms', [add]) if not g.is_empty and g.area > 0])
    print(key, 'basin land outside before', round(A(add), 1), 'km2')
    if add.is_empty: continue
    piece = add.buffer(0.01).intersection(LAND.buffer(0.003)).buffer(0)   # the missing sliver as its own small piece, overlapping V by ~1 km
    # (the rest of the outline is left untouched: rebuilding the whole union would drop its small holes and change its area by more than the sliver)
    for q in getattr(piece, 'geoms', [piece]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior), 1.0); C[key]['polys'].append([[[round(a, 3), round(b, 3)] for a, b in q.exterior.coords]])
    Y = unary_union([V, piece])
    print('  ', key, 'basin land outside after', round(A(BL.difference(Y.buffer(0.002))) if not BL.difference(Y.buffer(0.002)).is_empty else 0, 2), 'km2')
km = lambda pl: int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(pl).encode()))
for key in ['tib', 'sup']: print(key, 'km2 left to tools/v386_areas_ellipsoid.py')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
