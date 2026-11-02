"""Version 285 (Nawaz: "Add modern Albania, north Macedonia and Bulgaria" ... "I meant with the current v5" ... "Apply").
Bulgaria, North Macedonia and Albania, whole (base map), added to V5 (CALIPH.sas) and to V6 (CALIPH.v2, the Super Caliphate, so V5 stays
inside V6). Their edge is the Danube in the north and the Šar and Prokletije mountains in the north-west. The other natural-frontier
previews of that day (the steppe and West Africa to the forest edge, Dagestan to the Sulak) were not applied.
Run after tools/v5_divide284.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
NAMES = {'100': 'Bulgaria', '807': 'North Macedonia', '008': 'Albania'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for key in ['sas', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    X = shapely.set_precision(shapely.union_all([V] + [G[k].buffer(0.003) for k in NAMES], grid_size=0.001).buffer(0), 0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    rows = [{'id': k, 'n': n, 'km2': round(A(G[k])), 'pct': 100} for k, n in NAMES.items()]
    print(key, C[key]['km2'], '->', km2)
    C[key].update(polys=out, km2=km2, states=[r for r in C[key]['states'] if r['id'] not in NAMES] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
