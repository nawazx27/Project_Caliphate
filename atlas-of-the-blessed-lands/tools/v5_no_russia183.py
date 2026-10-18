"""Version 183b (Nawaz: "I don't need the republic of Dagestan in v5"). V5 holds no Russian land: it stops at the northern borders of
Georgia and Azerbaijan (Russia removed with the 300 m overshoot, Georgia and Azerbaijan kept whole). Run after tools/v5_political183.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x3']['polys']]).buffer(0)
cut = G['643'].buffer(0.004).difference(G['268'].buffer(0.003)).difference(G['031'].buffer(0.003))
X = shapely.set_precision(V.difference(cut), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x3']['polys'] = out
C['x3']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['x3']['states'] = [s for s in C['x3']['states'] if not s['id'].startswith('643')]
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('V5', C['x3']['km2'], '| Russia in V5', round(A(Y.intersection(G['643'])), 1), '| Georgia', round(A(Y.intersection(G['268'])) / A(G['268']) * 100, 3), '| Azerbaijan', round(A(Y.intersection(G['031'])) / A(G['031']) * 100, 3))
