"""Version 265 (Nawaz, after previews of V4 + the Indian subcontinent: Wikipedia's definition, then Britannica's "Topography of South Asia"
map ("Use this"), then "Add Maldives and chagos", then "make this a new version"; numbered V9 at his choice, so V1-V8 keep their numbers).
NEW V9 (CALIPH.sas, XV 'sas') = V4 (CALIPH.me9, as of Version 264) + the whole of South Asia as Britannica's map shades it: India (with the
Andaman, Nicobar and Lakshadweep islands), Nepal, Bhutan, Bangladesh, Sri Lanka, and all of Kashmir including the China-held Aksai Chin
and Shaksgam valley (dashed on that map; Natural Earth disputed areas, tools/data/china_kashmir_ne.geojson); plus the Maldives and the
British Indian Ocean Territory (Chagos), which he added. Afghanistan, Pakistan and the rest of Kashmir were already in V4. Pockets >= 80%
in 60-100 E, 0-38 N filled except Tashkurgan (political-border gap). Rerun after any V4 change: python3 tools/v9_south_asia265.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
CN = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/china_kashmir_ne.geojson')))['features']]).intersection(G['156'].buffer(0.01))
ADD = {'356': 'India (with the Andaman, Nicobar and Lakshadweep islands)', '524': 'Nepal', '064': 'Bhutan', '050': 'Bangladesh', '144': 'Sri Lanka', '462': 'Maldives', '086': 'British Indian Ocean Territory (Chagos; UK, claimed by Mauritius)'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V, CN.buffer(0.003)] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
m = X.intersection(box(60, 0, 100, 38)); mb = m.buffer(0.01); fill = []
gap = m.buffer(0.5, quad_segs=4).buffer(-0.5, quad_segs=4).difference(m).intersection(land)
for g in getattr(gap, 'geoms', [gap]):
    if g.geom_type != 'Polygon' or A(g) < 100: continue
    t = g.exterior.intersection(mb).length / g.exterior.length; c = g.centroid
    if t < 0.8: continue
    if 74 < c.x < 76.5 and 36 < c.y < 38.5: print('left (political-border gap): Tashkurgan', round(A(g))); continue
    print('pocket filled', round(A(g)), round(t * 100), round(c.x, 2), round(c.y, 2)); fill.append(g)
X = unary_union([X] + [g.buffer(0.003) for g in fill]).buffer(0)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rows = [r for r in C['me9']['states'] if r['id'] not in ADD and r['id'] not in ('IN_JK',)]
rows += [{'id': 'IN_JK', 'n': 'Jammu and Kashmir and Ladakh (Indian-administered)', 'km2': next((r['km2'] for r in C['me9']['states'] if r['id'] == 'IN_JK'), 0), 'pct': 100}]
rows += [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()]
rows += [{'id': '156_K', 'n': 'China: the parts of Jammu and Kashmir it administers (Aksai Chin and the Shaksgam valley)', 'km2': round(A(CN)), 'pct': round(A(CN) / A(G['156']) * 100, 1)}]
for i in ADD: print(ADD[i][:40], round(100 * A(G[i].intersection(Y)) / A(G[i]), 1))
print('Aksai Chin + Shaksgam in %', round(100 * A(CN.intersection(Y)) / A(CN), 1))
C['sas'] = {'polys': out, 'km2': km2, 'states': rows}
print('V9 (sas)', km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
