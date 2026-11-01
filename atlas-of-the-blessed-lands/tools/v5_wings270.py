"""Version 270 (Nawaz, after a series of previews drawn on with red lines: Khazar towns and Volga Bulgaria; "Fill" both circles; a matching
"left wing" (Ukraine, western Russia) to his lines; the Moscow and Kirov dips; "Go back to the previous preview"; then a tick mark = apply).
V5 (CALIPH.sas) gains its northern wings, saved as one shape in tools/data/v5_wings270.geojson (made from whole Overture 2026-10-21.0
regions to his lines, plus gap pockets): all of Dagestan (Samandar, Balanjar), Kalmykia and Astrakhan (Itil), Volgograd, Saratov, Samara,
Tatarstan (Bulghar, Suwar), the North Caucasus with Krasnodar, Adygea, Stavropol and Rostov, Orenburg, Bashkortostan, Udmurtia, Chelyabinsk;
most of Ukraine (all but Lviv, Volyn, Zakarpattia) with Crimea and Sevastopol; Moldova; Belarus's Gomel and Mogilev; Bryansk, Kursk,
Belgorod, Oryol, Kaluga, Smolensk, Tula, Moscow, Lipetsk, Voronezh, Tambov, Ryazan, Vladimir, Nizhny Novgorod, Chuvashia, Mari El, Mordovia,
Penza, Ulyanovsk (the version he ticked: without the southern Kirov strip of a later preview). Run AFTER tools/v9_south_asia265.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_wings270.geojson')))['geometry']).buffer(0)
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
rows = [{'id': 'RU_W', 'n': 'Russia: the North Caucasus, the Volga and southern Urals to Tatarstan and Bashkortostan, and the centre to Moscow, Vladimir and Nizhny Novgorod (whole regions to the author’s lines)', 'km2': None, 'pct': None},
        {'id': 'UA_W', 'n': 'Ukraine (all but Lviv, Volyn and Zakarpattia), with Crimea and Sevastopol (disputed)', 'km2': None, 'pct': None},
        {'id': '498', 'n': 'Moldova', 'km2': 33212, 'pct': 100},
        {'id': 'BY_W', 'n': 'Belarus: Gomel and Mogilev regions', 'km2': None, 'pct': None}]
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for r, k in zip(rows, ['643', '804', '498', '112']):
    a = A(G[k].intersection(Y)); r['km2'] = round(a); r['pct'] = round(100 * a / A(G[k]), 1)
print(rows); print('V5 (sas)', C['sas']['km2'], '->', km2)
C['sas'].update(polys=out, km2=km2, states=[r for r in C['sas']['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
