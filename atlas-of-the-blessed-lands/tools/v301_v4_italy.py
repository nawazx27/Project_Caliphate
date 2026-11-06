"""Version 301 (Nawaz: "Which countries can we add to the Grand Caliphate to get to Rome?" -> "preview" (A: Italy; B: Italy + western
Balkans) -> drew the Tunisia-Sicily-Italy-Balkans line: "Add show full map of this").
V4 (CALIPH.sas) = tools/data/v4_italy_balkans301.geojson: V4 + Italy (San Marino, the Vatican inside it) + Slovenia, Croatia,
Bosnia and Herzegovina, Montenegro, Serbia and Kosovo, whole (base map); 6 small pockets filled. Checks that V5 (grm) still holds V4.
Run after tools/v300_belgium.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F = json.load(open(os.path.join(P, 'tools/data/v4_italy_balkans301.geojson')))['features'][0]['geometry']
NEW = shape(F).buffer(0)
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(F['coordinates']).encode()))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
rows = {r['id']: r for r in C['sas']['states']}
for k in ['380', '674', '705', '191', '070', '499', '688', 'KOS']:
    if k in G: rows[k] = {'id': k, 'n': G[k][0], 'km2': round(A(G[k][1])), 'pct': 100}
old = C['sas']['km2']; C['sas'].update(polys=F['coordinates'], km2=km2, states=sorted(rows.values(), key=lambda r: -(r.get('km2') or 0) * (r.get('pct') or 100)))
print('sas', old, '->', km2)
for k in ['grm', 'rom', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    print(k, 'V4 land outside it km2', round(A(NEW.difference(V.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
