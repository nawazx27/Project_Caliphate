"""Version 247 (Nawaz: is all of Greater Khurasan, Transoxiana and Khwarazm in V5 at their widest? -> preview -> "Apply"). V5 (CALIPH.sah) + every land of Nawaz's Transoxiana, Khwarazm and Greater Khurasan maps not yet inside (strips in China, the Kashgar
and Kizilsu prefectures of the widest classical Khurasan, the Caspian corner of his Khurasan map). Run AFTER tools/v7_sahara239.py (which rebuilds sah from me9 and would drop these): python3 tools/v5_khorasan_widest247.py"""
import json, os, subprocess, shapely, sys
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
R = {}
for f in ('khorasan_max', 'khorasan_classical'): R[f] = shape(json.load(open(os.path.join(D, f + '.geojson')))['features'][0]['geometry']).buffer(0)
for f, ks in (('transoxiana_trace', ('transoxiana', 'khwarazm', 'khorasan')), ('transoxiana_locator_trace', ('transoxiana_locator',)), ('mawarannahr_trace2', ('mawarannahr_img2', 'khwarazm_corners'))):
    d = json.load(open(os.path.join(D, f + '.json')))
    for k in ks: R[k] = Polygon(d[k]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0)
NEW = unary_union(list(R.values())).difference(V)
print('China land added', round(A(NEW.intersection(G['156']))), 'water added', round(A(NEW.difference(land))), 'other land', round(A(NEW.intersection(land).difference(G['156']))))
X = shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for k, g in R.items(): print(k, 'in %.2f%%' % (A(g.intersection(Y)) / A(g) * 100))
print('V5', C['sah']['km2'], '->', km2)
KS = unary_union(list(R.values())).intersection(G['156'])
row = {'id': 'KSG', 'n': 'China: the Kashgar country (Kashgar and Kizilsu prefectures) and border strips, part of the widest Khurāsān and Transoxiana', 'km2': round(A(KS)), 'pct': round(A(KS) / A(G['156']) * 100, 1)}
C['sah'].update(polys=out, km2=km2, states=[r for r in C['sah']['states'] if r['id'] != 'KSG'] + [row])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
