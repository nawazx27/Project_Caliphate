"""Version 202 (Nawaz: "Add these changes to V8", after asking which lands make the outline look most dominant). V8 (key 'v2') gains,
whole: Bulgaria, North Macedonia, Albania, Kosovo (the Aegean wrapped); the North Caucasus republics Dagestan (the rest of it),
Chechnya, Ingushetia, Kabardino-Balkaria, Karachay-Cherkessia, with North Ossetia by the no-gaps rule; Kalmykia and Astrakhan (the
whole Russian Caspian shore); DR Congo and Zambia (a full African base). Out: Saint Helena, Ascension and Tristan da Cunha. Adygea is
left out (it lies wholly inside Krasnodar Krai and would float alone). Russian regions: Natural Earth admin-1 (admin1_used.geojson),
snapped to the base map's Russia along its outer borders and coast. Run: python3 tools/v8_dominant202.py, then tools/fill_gaps.py v2."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
ad = {f['properties']['name']: shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'admin1_used.geojson')))['features'] if f['properties'].get('adm0_a3') == 'RUS'}
TAKE = ['Dagestan', 'Chechnya', 'Ingush', 'North Ossetia', 'Kabardin-Balkar', 'Karachay-Cherkess', 'Kalmyk', "Astrakhan'"]
OTHER = unary_union([g for n, g in ad.items() if n not in TAKE])
NC = unary_union([ad[n] for n in TAKE])
NCs = G['643'].intersection(NC.union(NC.buffer(0.03).difference(OTHER.buffer(0.001))))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
ADD = {'100': 'Bulgaria', '807': 'North Macedonia', '008': 'Albania', 'KOS': 'Kosovo', '180': 'DR Congo', '894': 'Zambia'}
X = shapely.union_all([V, NCs.buffer(0.003)] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
X = shapely.set_precision(X.difference(G['654'].buffer(0.05)), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
nc_in = A(G['643'].intersection(Y)) - A(G['643'].intersection(V))
rows = [r for r in C['v2']['states'] if r['id'] not in list(ADD) + ['180_A', '654', '643_C', '643_NC']]
rows += [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100, 'core': False} for i, n in ADD.items()]
rows += [{'id': '643_NC', 'n': 'Russia: the North Caucasus republics (Dagestan, Chechnya, Ingushetia, North Ossetia, Kabardino-Balkaria, Karachay-Cherkessia) and the Caspian shore (Kalmykia, Astrakhan), whole', 'km2': round(A(NCs)), 'pct': round(A(NCs) / A(G['643']) * 100, 1), 'core': False}]
C['v2']['states'] = rows; print('V8', C['v2']['km2'], '->', km2); C['v2']['polys'] = out; C['v2']['km2'] = km2
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
for i in ADD: print(i, ADD[i], round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
for n in TAKE + ['Adygey', "Stavropol'", 'Krasnodar']: print(n, round(A(ad[n].intersection(Y)) / A(ad[n]) * 100, 1))
print('Saint Helena left', round(A(G['654'].intersection(Y)), 2), '| Russia added', round(nc_in))
