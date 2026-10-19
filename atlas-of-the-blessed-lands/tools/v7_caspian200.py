"""Version 200 (Nawaz, phone screenshot of V7 round the western Caspian: "What's this line in v7"). Leftovers of Version 183 (V7, then
named V5, was to hold no Russian land; Nawaz: "I don't need the republic of Dagestan"): a sea strip about 1 km wide along the whole
Dagestan coast (about 540 km²) and Chechen Island (Russian) with its water ring. Removes from V7 (key x3) everything north of 41.9 N
between 46.5 and 49.5 E that lies on Russian land or within about 5 km of it, keeping Azerbaijan's and Georgia's own edges.
Run: python3 tools/v7_caspian200.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x3']['polys']]).buffer(0)
R = box(46.5, 41.9, 49.5, 46.0).intersection(G['643'].buffer(0.05)).difference(G['031'].buffer(0.003)).difference(G['268'].buffer(0.003))
cut = V.intersection(R)
print('removing', round(A(cut)), 'km2, of it Russian land', round(A(cut.intersection(G['643']))))
X = shapely.set_precision(V.difference(R), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['x3']['polys'] = out; print('V7', C['x3']['km2'], '->', km2); C['x3']['km2'] = km2
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('Azerbaijan in', round(A(G['031'].intersection(Y)) / A(G['031']) * 100, 3), '| Georgia in', round(A(G['268'].intersection(Y)) / A(G['268']) * 100, 3),
      '| Russia left in V7', round(A(G['643'].intersection(Y)), 1), '| left in the box', round(A(Y.intersection(box(46.5, 41.9, 49.5, 46.0)).difference(G['031'].buffer(0.003)).difference(G['268'].buffer(0.003))), 1))
