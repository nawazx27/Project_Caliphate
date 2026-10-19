"""Version 195 (towns rule, 2026-10-16): every recognised CITY or TOWN (Overture 2026-09-23.1 divisions, locality class city/town) that V9's
new Sahara line cuts is taken whole: by its outline where Overture has one, else a circle of about 1.5 km round its point. Cut = some of it
on each side of the new line, which is the Sahara's southern edge (Natural Earth) on land. Repeats until none is cut.
Run: python3 tools/v9_sahara_towns195.py <div.parquet> <area.parquet>"""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')])
R = json.load(open(os.path.join(P, 'regions.geojson')))
SAH = unary_union([shape(f['geometry']).buffer(0) for f in R['features'] if (f['properties'].get('NAME') or '').upper() in ('SAHARA', 'LIBYAN DESERT')])
D = pq.read_table(sys.argv[1]).to_pylist()
AR = {r['division_id']: shapely.make_valid(shapely.from_wkb(r['geometry'])) for r in pq.read_table(sys.argv[2]).to_pylist()}
towns = []
for r in D:
    pt = shapely.from_wkb(r['geometry'])
    g = AR.get(r['id']) or pt.buffer(0.0135)
    towns.append(((r['names'] or {}).get('primary') or '?', r['country'], g))
tree = STRtree([g for _, _, g in towns])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
taken = {}
for rnd in range(4):
    edge = V.boundary.intersection(SAH.boundary.buffer(0.02)).intersection(land)
    cut = []
    for i in tree.query(edge.buffer(0.01)):
        n, c, g = towns[i]
        if (n, c) in taken: continue
        out_part = g.difference(V)
        if not out_part.is_empty and A(out_part) > 0.01 and g.intersection(V).area > 0: cut.append(i)
    if not cut: break
    for i in cut: n, c, g = towns[i]; taken[(n, c)] = g
    V = shapely.union_all([V] + [towns[i][2].buffer(0.003) for i in cut], grid_size=0.001)
    print('round', rnd + 1, 'towns taken whole:', len(cut))
out = []
for q in getattr(V, 'geoms', [V]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['me9']['polys'] = out
C['me9']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
if taken:
    C['me9']['states'].append({'id': 'TOWNS_SAH', 'n': 'Towns on the Sahara line taken whole: ' + ', '.join(sorted(n for n, c in taken)[:60]) + (' and others' if len(taken) > 60 else ''), 'km2': round(sum(A(g) for g in taken.values())), 'pct': None})
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print(len(taken), 'towns:', ', '.join(f'{n} ({c})' for n, c in sorted(taken)))
print('V9', C['me9']['km2'])
