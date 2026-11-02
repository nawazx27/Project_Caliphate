"""Version 286 (Nawaz: "I think V2 has the core lands and rivers and is a bit easier to maintain than V5"; asked about the Indus
headwaters (outside V2); "Add it"; preview with the whole princely state; "give it V for Kashmir and apply", read as V4's Kashmir).
V2 (me2) and V3 (ca) get exactly the Kashmir V4 (me9) holds: Indian-administered Jammu and Kashmir and Ladakh with Siachen, as on
Pakistan's official 2020 map (V4's land in India and in the base map's Siachen shape 'KAS'); Aksai Chin and Shaksgam (China) are NOT
added. This overrides the Version 223 official-lines rule for V2 at Nawaz's explicit request: do not rerun tools/v3_official223.py on
me2 after this (it would strip this land again). Run after the V2/V3 tools and tools/v4_kashmir264.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
V4 = M('me9'); K = unary_union([V4.intersection(G['356']), V4.intersection(G['KAS'])]).buffer(0)
print('V4 Kashmir %.0f km2' % A(K))
row = [r for r in C['me9']['states'] if r['id'] == 'IN_JK']
for key in ['me2', 'ca']:
    V = M(key)
    X = shapely.set_precision(shapely.union_all([V, K.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(key, C[key]['km2'], '->', km2)
    C[key].update(polys=out, km2=km2, states=[r for r in C[key]['states'] if r['id'] != 'IN_JK'] + [dict(x) for x in row])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
