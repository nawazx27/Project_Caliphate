"""Version 179: the no-gaps rule for the new V7. Fills the pockets tools/fill_gaps.py marks to fill (tools/data/gaps_x7.geojson, fill=True)
and, in the new lands east of 76 E, every pocket with at least 80% of its edge on V7 (northern Nujiang between Myanmar and Tibet, the
Linxia-Lanzhou edge, the Lijiang and Mianyang bends). Run after tools/v7_india179.py and tools/fill_gaps.py x7."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
gaps = [shape(f['geometry']) for f in json.load(open(os.path.join(P, 'tools/data/gaps_x7.geojson')))['features']
        if f['properties']['fill'] or (f['properties']['touch'] >= 0.8 and shape(f['geometry']).representative_point().x > 76)]
print('filling', len(gaps), round(sum(A(g) for g in gaps)), 'km2')
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x7']['polys']]).buffer(0)
X = shapely.union_all([X] + [g.buffer(0.003) for g in gaps], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x7']['polys'] = out
C['x7']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['x7']['states'].append({'id': 'GAPS', 'n': 'Pockets between lands filled (no-gaps rule): northern Nujiang, the Linxia–Lanzhou edge and smaller bends', 'km2': round(sum(A(g) for g in gaps)), 'pct': None})
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V7', C['x7']['km2'], 'holes', sum(len(p) - 1 for p in out))
