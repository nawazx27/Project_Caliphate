"""Version 251 (Nawaz: "take the entire Central Asia back to its political borders, and don't do a preview, just apply it").
V5 (CALIPH.sah) in Central Asia (46-90 E, 35-56 N, outside the Derbent/southern Dagestan block of Version 249) loses every piece of land
of Russia and China (the ~1,840 km2 strip on Kazakhstan's northern border and the ~800 km2 strip in the Ili valley, leftovers of earlier
outline work), so it ends on the borders of Kazakhstan, Kyrgyzstan and Tajikistan. Run AFTER tools/v7_sahara239.py, tools/v5_derbent249.py
and tools/v5_sicily250.py."""
import json, os, subprocess
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
CA = box(46, 35, 90, 56).difference(box(46.5, 41, 49.2, 42.6))
CUT = G['643'].union(G['156']).intersection(CA)
for k in ('643', '156'): print(k, 'land removed', round(A(G[k].intersection(CA).intersection(V))), 'km2')
X = V.difference(CUT).buffer(0)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for k, n in (('398', 'Kazakhstan'), ('417', 'Kyrgyzstan'), ('762', 'Tajikistan'), ('860', 'Uzbekistan'), ('795', 'Turkmenistan'), ('004', 'Afghanistan')):
    print(n, 'in %.2f%%' % (A(G[k].intersection(Y)) / A(G[k]) * 100))
print('Russia left in V5', round(A(G['643'].intersection(Y))), 'km2; China left', round(A(G['156'].intersection(Y))), 'km2')
print('V5 (sah)', C['sah']['km2'], '->', km2)
C['sah'].update(polys=out, km2=km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
