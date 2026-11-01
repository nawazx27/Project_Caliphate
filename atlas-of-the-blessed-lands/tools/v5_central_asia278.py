"""Version 278 (Nawaz: "Is greater Central Asia in v5", "Check Wikipedia", previews of the widest and the Wikipedia definitions, then
Wikipedia's map "Central Asia definitions (orthographic).png" (reference/v278_central_asia_definitions_wikipedia.png): "I want exactly
the lines of light green and dark green shaded outlines", then "Apply").
V5 (CALIPH.v2) gains tools/data/v5_central_asia278.geojson: Mongolia whole, and the two Russian light-green areas on the map's own lines
(traced, unprojected: tools/data/wiki_central_asia_traced278.geojson): the Volga-Ural piece (most of Orenburg, Samara, Ulyanovsk, southern
Saratov, slices of Bashkortostan, Tatarstan, Penza, Chuvashia, Mordovia; ~339,000 km2) and the Altai-Sayan piece (Altai Republic, most of
Khakassia, western Tuva, a strip of Altai Krai; ~214,000 km2), plus small tracing pockets. Everything else green was already in V5."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_central_asia278.geojson')))['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
mn = A(G['496'].intersection(Y)); ru = A(G['643'].intersection(W.difference(V)))
rows = [{'id': '496', 'n': 'Mongolia', 'km2': round(mn), 'pct': round(100 * mn / A(G['496']), 1)},
        {'id': '643_CA', 'n': 'Russia: the light-green Central Asian lands of Wikipedia’s Central Asia definitions map, on its own lines (the Volga–Ural steppe of Orenburg, Samara, Ulyanovsk and southern Saratov; the Altai–Sayan of the Altai Republic, Khakassia and western Tuva)', 'km2': round(ru), 'pct': round(100 * ru / A(G['643']), 1)}]
print('V5 (v2)', C['v2']['km2'], '->', km2, rows)
C['v2'].update(polys=out, km2=km2, states=[r for r in C['v2']['states'] if r['id'] not in ('496', '643_CA')] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
