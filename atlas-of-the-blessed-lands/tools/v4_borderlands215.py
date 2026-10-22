"""Version 215 (Nawaz, with the Wikipedia map "Libya–Chad territorial dispute map.png": "Build another version which is upon v3 and in
that this territory is included"). A NEW outline (CALIPH.me10, XV 'me10') = all of V3 (key me2) + the Libya–Chad Borderlands: the land
of Chad north of the line Libya claimed before the ICJ (1994 judgment for Chad): the 15th parallel from the Sudan border west to 19 E,
then straight north-west to the Chad–Niger border at 18 N (read off the map; the Aouzou Strip lies inside). Towns rule: Overture
city/town places the line cuts are taken whole (outline, else a 1.5 km circle). Named V4 (by size, between V3 and the old V4).
Run: python3 tools/v4_borderlands215.py <div.parquet> <area.parquet>, then tools/fill_gaps.py me10."""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, LineString
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
TD = G['148']
b = TD.boundary.intersection(G['562'].boundary.buffer(0.02)).intersection(shapely.box(10, 17.9, 20, 18.1)); x18 = (b.bounds[0] + b.bounds[2]) / 2
CLAIM = Polygon([(x18 - 1, 18.0), (x18 - 1, 24), (26, 24), (26, 15.0), (19, 15.0), (x18, 18.0)])
R = TD.intersection(CLAIM)
LINE = LineString([(x18, 18.0), (19, 15.0), (25, 15.0)]).intersection(TD.buffer(0.05))
land = shapely.union_all(list(G.values()))
AR = {r['division_id']: shapely.make_valid(shapely.from_wkb(r['geometry'])) for r in pq.read_table(sys.argv[2]).to_pylist()}
towns, names = [], []
for r in pq.read_table(sys.argv[1]).to_pylist():
    if r.get('class') not in ('city', 'town'): continue
    p = shapely.from_wkb(r['geometry'])
    if p.distance(LINE) > 0.3: continue
    g = AR.get(r['id']) or p.buffer(0.0135)
    if g.intersects(LINE) and not g.difference(R.buffer(0.002)).intersection(land).is_empty:
        towns.append(g.intersection(land)); names.append((r.get('names') or {}).get('primary'))
print('borderlands', round(A(R)), 'km2 =', round(A(R) / A(TD) * 100, 1), '% of Chad; towns taken whole:', names)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me2']['polys']]).buffer(0)
X = shapely.union_all([V, R.buffer(0.003)] + [t.buffer(0.002) for t in towns], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
tda = A(TD.intersection(Y))
rows = [dict(r) for r in C['me2']['states']] + [{'id': '148_BL', 'n': 'Chad: the Borderlands Libya claimed before the International Court of Justice (north of 15° N and of a line to the Niger border at 18° N; with the Aouzou Strip)' + (', with the towns on that line whole (' + ', '.join(n for n in names if n) + ')' if names else ''), 'km2': round(tda), 'pct': round(tda / A(TD) * 100, 1)}]
C['me10'] = {'polys': out, 'km2': km2, 'states': rows}
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V3', C['me2']['km2'], '-> new', km2, '| Chad held', round(tda / A(TD) * 100, 1), '%')
