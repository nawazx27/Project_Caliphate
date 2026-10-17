"""Version 175 (Nawaz: "Add Cyprus to all of them"). The whole island of Cyprus (every base-map unit on it: Cyprus, Northern Cyprus, the UN buffer
zone and the British bases, whatever the base map draws) is added to every outline that lacks any of it. Run: python3 tools/cyprus175.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CY = unary_union([shape(f['geometry']).buffer(0).intersection(box(32.2, 34.5, 34.7, 35.75)) for f in geo['features']])
print('Cyprus island', round(A(CY)), 'km2')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k, n in (('me', 'V1'), ('me2', 'V2'), ('xb', 'V3'), ('x', 'V4'), ('x3', 'V5'), ('v2', 'V6')):
    X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    have = A(CY.intersection(X)) / A(CY) * 100; print(n, 'Cyprus', round(have, 1), '%')
    if have >= 99.95: continue
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(CY.buffer(0.003))], grid_size=0.001)
    out = []
    for q in getattr(X2, 'geoms', [X2]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    C[k]['polys'] = out
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    if not any('Cyprus' in r['n'] for r in C[k]['states']): C[k]['states'].append({'id': '196', 'n': 'Cyprus (the whole island)', 'km2': round(A(CY)), 'pct': 100})
    print('  added; now', C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
