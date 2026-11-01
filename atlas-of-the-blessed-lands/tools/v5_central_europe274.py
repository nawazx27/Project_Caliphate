"""Version 274 (Nawaz, a red line on V5 from Slovenia's northern tip to the corner where Belarus meets Lithuania and Poland; preview;
"Apply"). V5 (CALIPH.sas) gains tools/data/v5_central_europe274.geojson: all of Slovakia, and every Overture 2026-10-21.0 district
(Austrian Bezirk, Czech okres, Polish powiat) whose inner point lies east of his line: eastern Austria (Vienna by gap rule, Lower
Austria, Burgenland, Styria, most of Carinthia), Moravia and Czech Silesia, eastern and southern Poland (Warsaw, Krakow, Upper Silesia,
Lublin, Rzeszow, Bialystok, Kielce), plus gap pockets (Vienna, Opole city and five more). His line placed by matching map features
(approximate): Linz's area, Lodz and the Suwalki corner are just outside. The Lithuanian border pocket (political) left out.
Run AFTER tools/v5_balkans_asia273.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_central_europe274.geojson')))['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sas']['polys']]).buffer(0)
X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [{'id': '703', 'n': 'Slovakia', 'km2': None, 'pct': None},
        {'id': 'AT_E', 'n': 'Austria: the east (Vienna, Lower Austria, Burgenland, Styria, most of Carinthia; whole districts to the author’s line)', 'km2': None, 'pct': None},
        {'id': 'CZ_E', 'n': 'Czechia: Moravia and Czech Silesia (whole districts to the author’s line)', 'km2': None, 'pct': None},
        {'id': 'PL_E', 'n': 'Poland: the east and south (Warsaw, Krakow, Upper Silesia, Lublin, Rzeszow, Bialystok, Kielce; whole districts to the author’s line)', 'km2': None, 'pct': None}]
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for r, k in zip(rows, ['703', '040', '203', '616']):
    a = A(G[k].intersection(Y)); r['km2'] = round(a); r['pct'] = round(100 * a / A(G[k]), 1)
print(rows); print('V5 (sas)', C['sas']['km2'], '->', km2)
C['sas'].update(polys=out, km2=km2, states=[r for r in C['sas']['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
