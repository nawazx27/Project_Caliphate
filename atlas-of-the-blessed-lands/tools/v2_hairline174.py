"""Version 174 (Nawaz, phone screenshot of V2: "What's this line in V2?"). Removing Turkmenistan and Tunisia from V2 (Version 173) kept, along their
borders with Uzbekistan, Kazakhstan and Algeria, the outline's hairline overshoot into those countries (about 300 m wide), drawn as a thin line.
Near both countries, V2 now keeps only the land of countries it lists. Run: python3 tools/v2_hairline174.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me2']['polys']]).buffer(0)
held = unary_union([G[r['id']] for r in C['me2']['states'] if r['id'] in G])
zone = unary_union([G['795'], G['788']]).buffer(0.3)
X2 = unary_union([X.difference(zone), X.intersection(zone).intersection(held.buffer(0.003))])
X2 = shapely.union_all([shapely.make_valid(X2)], grid_size=0.001)
print('removed', round(A(X) - A(X2), 1), 'km2')
out = []
for q in getattr(X2, 'geoms', [X2]):
    if q.geom_type != 'Polygon' or A(q) < 0.5: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['me2']['polys'] = out
C['me2']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
print('V2', C['me2']['km2'], 'pieces', len(out))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
