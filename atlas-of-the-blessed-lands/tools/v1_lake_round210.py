"""Version 210: in V1 (key me8), which holds Lake Albert as a piece of its own (no Uganda), Nawaz's shore strip ends in a thin point
beside a narrow notch at the lake's north end. The lake piece is closed by about 8 km (morphological closing, 0.08 degrees) so it is one
neat shape. Run after tools/lake_albert_all210.py."""
import json, os, subprocess, shapely
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me8']['polys']]).buffer(0)
B = box(30.0, 0.8, 31.8, 2.6)
lake = [p for p in V.geoms if p.intersects(B)]; rest = [p for p in V.geoms if not p.intersects(B)]
L = shapely.union_all(lake); L2 = L.buffer(0.08, join_style=1).buffer(-0.08, join_style=1).union(L)
print('lake piece', round(A(L)), '->', round(A(L2)), 'km2')
X = shapely.union_all(rest + [L2], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
n = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
print('V1', C['me8']['km2'], '->', n); C['me8'].update(polys=out, km2=n)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
