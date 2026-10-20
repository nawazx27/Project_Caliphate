"""Version 204 (Nawaz asked which lands to add or remove for the most imposing, cohesive silhouette, then: "Do whatever you must").
Measured on every outline (solidity = area / convex-hull area, equal-area projection; stray pieces over 500 km from the main body):
the far islands stretch the hull over the ocean, so taking them out raises V7's solidity from 0.48 to 0.68, and Bulgaria, North
Macedonia, Albania and Kosovo fill the notch above Greece. Applied to V7 (key x3) and V8 (key 'v2', which holds all of V7):
out: Saint Helena, Ascension and Tristan da Cunha; Cabo Verde; the Azores. In, whole: Bulgaria, North Macedonia, Albania, Kosovo.
Run: python3 tools/silhouette204.py, then tools/fill_gaps.py x3 v2 and tools/silhouette_gaps204.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
AZ = box(-32, 36, -24, 40.5)
OUT = G['654'].buffer(0.05).union(G['132'].buffer(0.05)).union(AZ)
ADD = {'100': 'Bulgaria', '807': 'North Macedonia', '008': 'Albania', 'KOS': 'Kosovo'}
azores = A(G['620'].intersection(AZ)); pt = round((A(G['620']) - azores) / A(G['620']) * 100, 1)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
km = lambda out: int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for k in ['x3', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    X = shapely.union_all([V.difference(OUT)] + [G[i].buffer(0.003).difference(OUT) for i in ADD], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    rows = []
    for r in C[k]['states']:
        if r['id'] in ('654', '132') or r['id'] in ADD: continue
        if r['id'] == '620': r = dict(r, n='Portugal (without the Azores)', km2=round(A(G['620']) - azores), pct=pt)
        rows.append(r)
    rows += [dict({'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100}, **({'core': False} if k == 'v2' else {})) for i, n in ADD.items()]
    n = km(out); print(k, C[k]['km2'], '->', n); C[k].update(polys=out, km2=n, states=rows)
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    print('  ', {ADD[i]: round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2) for i in ADD}, '| left: St Helena', round(A(G['654'].intersection(Y)), 1), 'Cabo Verde', round(A(G['132'].intersection(Y)), 1), 'Azores', round(A(Y.intersection(AZ)), 1))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
