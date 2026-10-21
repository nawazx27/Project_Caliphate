"""Version 209 (Nawaz, with a map of the whole Balkan Peninsula shaded (reference/v209_balkans_map.jpg): "Add this to v7").
Whole, into V7 (key x3): Slovenia, Croatia, Bosnia and Herzegovina, Serbia, Montenegro, Kosovo, North Macedonia, Albania, Romania
and Bulgaria (Greece and Türkiye were already in; Moldova and Hungary are not shaded). Also into V8 (key 'v2'), whose note says it
holds all of V7. Run: python3 tools/v7_balkans209.py, then tools/fill_gaps.py x3,v2 and tools/silhouette_gaps204.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
ADD = {'705': 'Slovenia', '191': 'Croatia', '070': 'Bosnia and Herzegovina', '688': 'Serbia', '499': 'Montenegro', 'KOS': 'Kosovo',
       '807': 'North Macedonia', '008': 'Albania', '642': 'Romania', '100': 'Bulgaria'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ['x3', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    X = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    n = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    rows = [r for r in C[k]['states'] if r['id'] not in ADD] + [dict({'id': i, 'n': nm, 'km2': round(A(G[i])), 'pct': 100}, **({'core': False} if k == 'v2' else {})) for i, nm in ADD.items()]
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    print(k, C[k]['km2'], '->', n, {nm: round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2) for i, nm in ADD.items()})
    C[k].update(polys=out, km2=n, states=rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
