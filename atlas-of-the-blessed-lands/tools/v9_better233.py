"""Version 233 (Nawaz: "Go with everything suggested", for "How can v9 be better"). On V9 (CALIPH.eu, after tools/v9_med232.py):
Moldova, Belgium, the Netherlands (European part), Luxembourg and Czechia added whole; then the hairline spill cleaned: the land of
every country that V9 does not hold whole (Russia, China, India, Germany, Poland, Ukraine, Belarus..., and France's lands outside its
mainland, Corsica, Mayotte and Réunion) is cut out, so V9's land edge lies on the political borders (as tools/v3_official223.py did for V3).
Run: python3 tools/v9_better233.py [preview]   (writes CALIPH.eu)"""
import json, os, subprocess, shapely, sys
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') if len(sys.argv) < 2 else sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
N = {f['id']: f['properties']['n'] for f in geo['features'] if f.get('geometry')}
G['NLE'] = G['528'].intersection(box(2, 50, 8, 54))
ADD = {'498': 'Moldova', '056': 'Belgium', 'NLE': 'Netherlands (European part)', '442': 'Luxembourg', '203': 'Czechia'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['eu']['polys']]).buffer(0)
V1 = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD])
# countries held whole: inside by >= 99% after the additions; everything else is cut out (France keeps only its held parts)
held = {k for k, g in G.items() if A(g) > 0 and A(g.intersection(V1)) / A(g) >= 0.99}
FR_KEEP = unary_union([G['FRA'].intersection(box(-6, 41, 10, 52)), G['FRA'].intersection(box(44.9, -13.1, 45.4, -12.5)), G['FRA'].intersection(box(55.1, -21.5, 55.9, -20.8))])
cut = unary_union([g for k, g in G.items() if k not in held and k not in ('FRA', '528')] + [G['FRA'].difference(FR_KEEP), G['528'].difference(G['NLE'])])
spill = V1.intersection(cut)
print('spill cut', round(A(spill)), 'km2 from', sorted({N[k] for k, g in G.items() if k not in held and g.intersects(spill) and A(g.intersection(spill)) > 5}))
X = shapely.set_precision(V1.difference(cut), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
low = [(N.get(k, k), round(A(G[k].intersection(Y)) / A(G[k]) * 100, 2)) for k in held if A(G[k]) > 0 and A(G[k].intersection(Y)) / A(G[k]) < 0.999]
print('held lands below 99.9% after the cut:', low)
for i, n in ADD.items(): print(n, round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
rows = C['eu']['states'] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()]
print('V9', C['eu']['km2'], '->', km2)
C['eu'].update(polys=out, km2=km2, states=rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
