"""Version 171 (Nawaz: "I forgot to say Armenia"): every outline must hold Armenia whole, like Azerbaijan, Georgia and Lake Albert (Version 170).
Adds Armenia to any outline that lacks it. Run: python3 tools/armenia170.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
AM = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '051'][0]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def pack(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out): return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for k, n in (('me', 'V1'), ('me2', 'V2'), ('xb', 'V3'), ('x', 'V4'), ('x3', 'V5'), ('v2', 'V6')):
    X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    have = A(AM.intersection(X)) / A(AM) * 100
    print(n, k, 'Armenia', round(have, 1), '%')
    if have >= 99.9: continue
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(AM.buffer(0.003))], grid_size=0.001)
    C[k]['polys'] = pack(X2); C[k]['km2'] = km2(C[k]['polys'])
    if not any(r['id'] == '051' for r in C[k]['states']): C[k]['states'].append({'id': '051', 'n': 'Armenia', 'km2': round(A(AM)), 'pct': 100})
    print('  added; now', C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
