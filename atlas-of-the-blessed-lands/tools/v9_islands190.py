"""Version 190 (Nawaz: "Add Canary Islands and Madeira to V9"). The Canary Islands (Spain) and Madeira with Porto Santo, the Desertas and
the Savage Islands (Portugal's Madeira region), whole, in V9. Run: python3 tools/v9_islands190.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
CAN = G['724'].intersection(box(-18.5, 27.4, -13.0, 29.6))
MAD = G['620'].intersection(box(-17.5, 29.8, -15.5, 33.3))
print('Canaries', round(A(CAN)), 'pieces', len(getattr(CAN, 'geoms', [CAN])), '| Madeira', round(A(MAD)), 'pieces', len(getattr(MAD, 'geoms', [MAD])))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V, CAN.buffer(0.003), MAD.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['me9']['polys'] = out
C['me9']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['me9']['states'] += [{'id': '724_CN', 'n': 'Spain: the Canary Islands', 'km2': round(A(CAN)), 'pct': round(A(CAN) / A(G['724']) * 100, 1)},
                       {'id': '620_MD', 'n': 'Portugal: Madeira (with Porto Santo, the Desertas and the Savage Islands)', 'km2': round(A(MAD)), 'pct': round(A(MAD) / A(G['620']) * 100, 1)}]
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('Canaries in', round(A(CAN.intersection(Y)) / A(CAN) * 100, 2), '| Madeira in', round(A(MAD.intersection(Y)) / A(MAD) * 100, 2), '| V9', C['me9']['km2'])
