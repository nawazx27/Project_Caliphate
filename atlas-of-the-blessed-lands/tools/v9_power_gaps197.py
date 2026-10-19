"""Version 197: the no-gaps rule after tools/v9_power197.py. Fills the pockets tools/fill_gaps.py me9 marks (fill=True: Baikonur, the
Tashkurgan pocket, slivers) and every pocket with at least 80% of its edge on V9 (small bends of the Russia-Kazakhstan border).
Run after tools/fill_gaps.py me9."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
gaps = [shape(f['geometry']) for f in json.load(open(os.path.join(P, 'tools/data/gaps_me9.geojson')))['features']
        if f['properties']['fill'] or f['properties']['touch'] >= 0.8]
print('filling', len(gaps), round(sum(A(g) for g in gaps)), 'km2')
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([X] + [g.buffer(0.003) for g in gaps], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['me9']['states'] = [r for r in C['me9']['states'] if r['id'] not in ('GAPS_197', 'KAB', '156_TK', '643_KZ')] + [
    {'id': 'KAB', 'n': 'Baikonur (Kazakh land leased to Russia)', 'km2': 6487, 'pct': 100},
    {'id': '156_TK', 'n': 'China: the Tashkurgan pocket between Tajikistan, Afghanistan and Pakistan (no-gaps rule)', 'km2': 2054, 'pct': 0.02},
    {'id': '643_KZ', 'n': 'Russia: small bends of the Kazakhstan border, at least 80% enclosed (no-gaps rule)', 'km2': 3867, 'pct': 0.02}]
C['me9']['polys'] = out; C['me9']['km2'] = km2
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V9', km2)
