"""Version 195: no-gaps rule after the Sahara. Fills the pockets tools/fill_gaps.py me9 marks (fill=True) and, in the Sahel band
(-20..30 E, 5..22 N), every pocket with at least 80% of its edge on V9: the Inner Niger Delta in Mali (about 29,000 km², wetland that
Natural Earth's Sahara leaves out), a pocket in northern Cameroon and one on the Senegal river. Run after tools/v9_sahara_towns195.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
gaps = []
for f in json.load(open(os.path.join(P, 'tools/data/gaps_me9.geojson')))['features']:
    g = shape(f['geometry']); c = g.representative_point(); p = f['properties']
    if p['fill'] or (p['touch'] >= 0.8 and -20 < c.x < 30 and 5 < c.y < 22): gaps.append(g)
print('filling', len(gaps), round(sum(A(g) for g in gaps)), 'km2')
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V] + [g.buffer(0.003) for g in gaps], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['me9']['polys'] = out
C['me9']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['me9']['states'].append({'id': 'GAPS_SAH', 'n': 'Pockets between lands filled (no-gaps rule): the Inner Niger Delta in Mali, a pocket in northern Cameroon, one on the Senegal river and small slivers', 'km2': round(sum(A(g) for g in gaps)), 'pct': None})
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V9', C['me9']['km2'])
