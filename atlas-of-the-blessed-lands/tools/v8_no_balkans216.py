"""Version 216 (Nawaz: "Remove the balkans from v8"; V8 = key x3 since Version 215). Based on tools/v7v8_greece206.py, for x3 only, with all ten Balkan countries of Version 209. V7 (key x3) and V8 (key 'v2') end at Greece again:
Bulgaria, North Macedonia, Albania and Kosovo (added in Version 204) taken out, Greece and Türkiye kept whole (their own edges kept); everything else in the Balkans (13-30 E, 39.5-48 N), such as the Danube slivers
Version 204's gap filling added, taken out too.
The far Atlantic islands stay out (Version 204). Chad was taken out of V3 by restoring its data from Version 204.
Run: python3 tools/v7v8_greece206.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
B = ['705', '191', '070', '688', '499', 'KOS', '807', '008', '642', '100']
R = unary_union([G[i] for i in B]).buffer(0.004).union(shapely.box(13, 39.5, 30, 48)).difference(G['300'].buffer(0.003)).difference(G['792'].buffer(0.003))  # also the Danube slivers Version 204's gap filling added
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ['x3']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    X = shapely.union_all([V.difference(R), G['300'].buffer(0.003), G['792'].buffer(0.003).intersection(V.buffer(0.01))], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    n = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    print(k, C[k]['km2'], '->', n, {i: round(A(G[i].intersection(Y)), 1) for i in B}, '| Greece', round(A(G['300'].intersection(Y)) / A(G['300']) * 100, 2), 'Türkiye', round(A(G['792'].intersection(Y)) / A(G['792']) * 100, 2))
    C[k].update(polys=out, km2=n, states=[r for r in C[k]['states'] if r['id'] not in B])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
