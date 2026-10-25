"""Version 232 (Nawaz: "Make a v9 built upon v8 with the regions in the image and include France, Monaco, Switzerland, Austria, Slovakia",
then "Apply V9"). A NEW V9 (key CALIPH.eu, XV 'eu') = V8 (af) + the European shore of the Mediterranean, every land whole: Spain and
Portugal with all their islands (the Balearics, the Azores), Andorra, Italy with Sicily and Sardinia, San Marino, Malta, Slovenia, Croatia,
Bosnia and Herzegovina, Serbia, Kosovo, Montenegro, Romania, metropolitan France with Corsica (not its overseas departments outside Africa),
Monaco, Switzerland, Austria, Slovakia; Liechtenstein and Hungary by the no-gaps rule (enclosed 100% and 95%).
Run after tools/v8_africa229.py: python3 tools/v9_med232.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
G['FRM'] = G['FRA'].intersection(box(-6, 41, 10, 52))
ADD = {'724': 'Spain (whole, with the Balearics; the Canaries, Ceuta and Melilla are in V8)', '620': 'Portugal (whole, with the Azores; Madeira is in V8)', '020': 'Andorra',
  '380': 'Italy (with Sicily and Sardinia)', '674': 'San Marino', '470': 'Malta', '705': 'Slovenia', '191': 'Croatia', '070': 'Bosnia and Herzegovina', '688': 'Serbia',
  'KOS': 'Kosovo', '499': 'Montenegro', '642': 'Romania', 'FRM': 'France (metropolitan, with Corsica)', '492': 'Monaco', '756': 'Switzerland', '040': 'Austria',
  '703': 'Slovakia', '438': 'Liechtenstein (enclosed: no-gaps rule)', '348': 'Hungary (95% enclosed: no-gaps rule)'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['af']['polys']]).buffer(0)
X = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i, n in ADD.items():
    p = A(G[i].intersection(Y)) / A(G[i]) * 100
    if p < 99.99: print('NOT WHOLE', n, round(p, 3))
rows = [r for r in C['af']['states'] if r['id'] not in ('CAN', 'MAD', 'CEU', 'MEL')] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()]
C['eu'] = {'polys': out, 'km2': km2, 'states': rows}
print('V9 (eu)', km2, 'km2,', len(out), 'pieces,', len(rows), 'rows')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
