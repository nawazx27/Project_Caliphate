"""Version 170 (Nawaz: "Make sure the full lake Albert stays in all models and models, which don't have Azerbaijan and Georgia must hold them").
Checked every outline: V3, V4 (keys xb, x) already hold the whole of Lake Albert, Azerbaijan and Georgia. V1, V2, V5, V6 (keys me, me2, x3, v2) held only 65.1%
of Lake Albert (the Ugandan side): the DR Congo half (tools/data/lake_albert_drc.geojson) is added to them. V1 and V2 (me, me2) also lacked Azerbaijan and
Georgia: both are added whole. Run: python3 tools/models_fill168.py"""
import json, os, subprocess, shapely, copy
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
LAKE = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Albert'])
DRC = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(D, 'lake_albert_drc.geojson')))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
mk = lambda ps: MultiPolygon([Polygon(r[0], r[1:]) for r in ps]).buffer(0)
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
for k, name in (('me', 'V1'), ('me2', 'V2'), ('x3', 'V5'), ('v2', 'V6')):
    X = mk(C[k]['polys']); add = [DRC.union(LAKE).difference(X)]; rows = []
    if k in ('me', 'me2'):
        for i, n in (('031', 'Azerbaijan'), ('268', 'Georgia')):
            if A(G[i].difference(X)) > 1: add.append(G[i].difference(X)); rows.append({'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100})
    add = unary_union(add)
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003))], grid_size=0.001)
    C[k]['polys'] = pack(X2); C[k]['km2'] = km2(C[k]['polys'])
    if A(DRC.union(LAKE).difference(X)) > 1: rows.append({'id': '180_A', 'n': 'DR Congo: the western half of Lake Albert', 'km2': round(A(DRC.difference(X))), 'pct': 0.0})
    C[k]['states'] += [r for r in rows if not any(q['id'] == r['id'] for q in C[k]['states'])]
    print(name, k, C[k]['km2'], 'Lake Albert now', round(A(LAKE.intersection(X2)) / A(LAKE) * 100, 1), '%', [r['n'] for r in rows])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
