"""Version 210 (Nawaz: "Each lake Albert requires a slightly larger boundary that includes the water and some adjacent land").
His own Lake Albert border of Version 150 (a smooth line a little inland of the DR Congo shore; tools/data/lake_albert_border150.geojson,
the land between it and the lake), which only V4 and V5 (keys xb, x) held, now goes into every other outline too: V1 me8, V2 me,
V3 me2, V6 me9, V7 x3, V8 'v2'. Row 180_A becomes the lake's DR Congo half with that shore land. Run: python3 tools/lake_albert_all210.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
D = lambda f: unary_union([shape(x['geometry']) for x in json.load(open(os.path.join(P, 'tools/data', f)))['features']]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LA = unary_union([D('lake_albert_drc.geojson'), D('lake_albert_border150.geojson')])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
ref = next(r for r in C['x']['states'] if r['id'] == '180_A')
for k in ['me8', 'me', 'me2', 'me9', 'x3', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    X = shapely.union_all([V, LA.buffer(0.003)], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    n = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    rows = [dict(r, n=ref['n'], km2=ref['km2'], pct=ref['pct']) if r['id'] == '180_A' else r for r in C[k]['states']]
    print(k, C[k]['km2'], '->', n, '| shore area inside', round(A(LA.intersection(Y)) / A(LA) * 100, 2), '% | DRC held', round(A(G['180'].intersection(Y))))
    C[k].update(polys=out, km2=n, states=rows)
print('V5 for comparison: DRC held', round(A(G['180'].intersection(MultiPolygon([Polygon(r[0], r[1:]) for r in C['x']['polys']]).buffer(0)))), '| row', ref)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
