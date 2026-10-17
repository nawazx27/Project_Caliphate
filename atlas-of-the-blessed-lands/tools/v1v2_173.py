"""Version 173 (Nawaz: "In v2 remove Tunisia and Turkmenistan and add Greece in v1 and v2"; names as of Version 169). V2 (key me2) loses Tunisia and Turkmenistan
(cut to the countries' land; the strips of sea within 2 km of their coasts and Caspian shore go with them, so no hairline stays); Greece, whole, with
Kastellorizo, Ro, Strongyli and Psomi (tools/data/kastellorizo.geojson), is added to V1 (key me) and V2. Run: python3 tools/v1v2_173.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
KAS = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(D, 'kastellorizo.geojson')))['features']])
GR = unary_union([G['300'], KAS])
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
# V2: remove Tunisia and Turkmenistan
X = mk(C['me2']['polys'])
for i, n in (('788', 'Tunisia'), ('795', 'Turkmenistan')):
    others = unary_union([g for j, g in G.items() if j != i])
    X = unary_union([shapely.make_valid(X.difference(G[i].buffer(0.02))), shapely.make_valid(X.intersection(others))])
    print(n, 'removed; V2 now', round(A(X)))
C['me2']['polys'] = pack(shapely.union_all([shapely.make_valid(X)], grid_size=0.001))
C['me2']['states'] = [r for r in C['me2']['states'] if r['id'] not in ('788', '795')]
# Greece in V1 and V2
for k in ('me', 'me2'):
    X = mk(C[k]['polys']) if k == 'me' else mk(C[k]['polys'])
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(GR.buffer(0.003))], grid_size=0.001)
    C[k]['polys'] = pack(X2)
    for r in C[k]['states']:
        pass
    C[k]['states'] = [r for r in C[k]['states'] if r['id'] not in ('300', '300_K')]
    C[k]['states'] += [{'id': '300', 'n': 'Greece', 'km2': round(A(G['300'])), 'pct': 100}, {'id': '300_K', 'n': 'Greece: Kastellorizo (Megisti), Ro, Strongyli and Psomi (not drawn by the base map; traced)', 'km2': round(A(KAS)), 'pct': 100}]
for k in ('me', 'me2'): C[k]['km2'] = km2(C[k]['polys']); print(k, C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
