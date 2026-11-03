"""Version 287 (Nawaz: "Add Sicily to v2"; preview; "Add Malta too and apply").
V2 (me2) and V3 (ca, so V2 stays inside it) get Sicily with its islands (Aeolian, Egadi, Ustica, Pantelleria, Pelagie) exactly as V4 (me9)
holds it (Version 261), and Malta whole (Malta, Gozo, Comino). Run after tools/v2_kashmir286.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
SIC = M('me9').intersection(G['380']).intersection(box(11.5, 35.0, 15.8, 39.0))
ADD = unary_union([SIC, G['470']])
rows = [{'id': 'IT_SIC', 'n': 'Italy: Sicily with its islands (the Aeolian and Egadi islands, Ustica, Pantelleria, the Pelagie islands)', 'km2': round(A(SIC)), 'pct': round(100 * A(SIC) / A(G['380']), 1)},
        {'id': '470', 'n': 'Malta', 'km2': round(A(G['470'])), 'pct': 100}]
for key in ['me2', 'ca']:
    V = M(key)
    X = shapely.set_precision(shapely.union_all([V, ADD.buffer(0.002)], grid_size=0.001).buffer(0), 0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(key, C[key]['km2'], '->', km2)
    C[key].update(polys=out, km2=km2, states=[r for r in C[key]['states'] if r['id'] not in ('IT_SIC', '470')] + [dict(r) for r in rows])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
