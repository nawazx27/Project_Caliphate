"""Version 183 (Nawaz: "Except lake Albert return every thing to political borders", for V5; his choices: whole Dagestan, whole Western
Sahara). V5's non-political edges replaced: (1) the traced Derbent / Samur / Dagestan-coast strip of Russia -> the whole Republic of Dagestan
(Overture region RU-DA); (2) the Moroccan-held part of Western Sahara (cut at the sand wall) -> all of Western Sahara (base map 732);
(3) the Caspian water strip off the Khorasan shore (Gorgan Bay, Turkmen coast) taken out, so the edge is the coast. Lake Albert's DR Congo
half stays (his exception). Sicily stays: its edge is Italy's Sicily region border. Run: python3 tools/v5_political183.py <dir with dag.parquet>"""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
DAG = unary_union([shapely.make_valid(wkb.loads(r['geometry'])) for r in pq.read_table(os.path.join(D, 'dag.parquet')).to_pylist() if r['region'] == 'RU-DA'])
DAG = DAG.intersection(G['643'].buffer(0.01))   # kept to the base map's Russia (its coast and borders)
WS = G['732']
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x3']['polys']]).buffer(0)
oldRU = V.intersection(G['643']); print('old Russian strip', round(A(oldRU)), '| Dagestan', round(A(DAG)), '| W Sahara', round(A(WS)), 'held', round(A(V.intersection(WS))))
# take out the old Russian strip (with its 300 m overshoot) and the Caspian water off the Khorasan shore
CASP = box(49.5, 36.4, 55.5, 42.5)
V = V.difference(G['643'].buffer(0.004).difference(G['268'].buffer(0.002)).difference(G['031'].buffer(0.002)))
V = V.difference(CASP.difference(land.buffer(0.003)))
X = shapely.union_all([V, DAG.buffer(0.003), WS.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x3']['polys'] = out
C['x3']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = []
for s in C['x3']['states']:
    if s['n'].startswith('Caspian Sea: the Khorasan shore'): continue
    if s['n'].startswith('Western Sahara'): s = dict(s, n='Western Sahara (all of it, to its international border)', km2=round(A(WS)), pct=100)
    if s['n'].startswith('Russia: Derbent'): s = dict(s, id='643_DA', n='Russia: the Republic of Dagestan, whole (with Derbent and the Samur valley)', km2=round(A(DAG)), pct=round(A(DAG) / A(G['643']) * 100, 1))
    rows.append(s)
C['x3']['states'] = rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('V5', C['x3']['km2'], '| Dagestan in', round(A(DAG.intersection(Y)) / A(DAG) * 100, 2), '| WS in', round(A(WS.intersection(Y)) / A(WS) * 100, 2),
      '| Russia outside Dagestan in V5', round(A(Y.intersection(G['643']).difference(DAG.buffer(0.01)))), '| Caspian water in box', round(A(Y.intersection(CASP).difference(land.buffer(0.004)))))
