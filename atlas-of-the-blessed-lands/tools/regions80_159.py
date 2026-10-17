"""Version 159 (Nawaz: "Anything between 80%-100% take them entirely in v2"). Every physical region of Natural Earth's regions layer
(mountains, plateaus, deserts, plains, basins, lowlands, deltas, valleys, peninsulas; not islands, continents, coasts, lakes or
the tundra and foothills strips) of which V2 already holds 80% to under 100% of the land part is taken entirely into V2 (cut to the coast
only, never to countries). V2-B is left alone. Run: python3 tools/regions80_159.py, then python3 tools/v7_build159.py to refresh V7."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}; land = unary_union(list(G.values()))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C['x']['polys']]).buffer(0)
SKIP = ('Island', 'Island group', 'Continent', 'Dragons-be-here', 'Geoarea', 'Tundra', 'Coast', 'Lake', 'Foothills')
take = []; adds = []
for f in json.load(open(os.path.join(P, 'regions.geojson')))['features']:
    p = f['properties']
    if p['FEATURECLA'] in SKIP: continue
    g = shape(f['geometry']).buffer(0).intersection(land)
    if g.is_empty or A(g) < 1000: continue
    pc = A(g.intersection(X)) / A(g) * 100
    if 80 <= pc < 99.995:
        add = g.difference(X); take.append((p['NAME'].title(), p['FEATURECLA'], round(pc, 1), round(A(add)))); adds.append(add)
for t in sorted(take, key=lambda t: -t[3]): print(t)
add = unary_union(adds)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 159, regions 80-100% (V2)', 'regions': take}, 'geometry': mapping(add)}]}, open(os.path.join(P, 'tools/data/regions80_159.geojson'), 'w'))
X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
out = []
for q in getattr(X2, 'geoms', [X2]):
    if q.geom_type != 'Polygon': continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x']['polys'] = out
C['x']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
print('adds', round(A(add)), 'km2; V2', C['x']['km2'])
rows = []
for i, g in G.items():
    a = add.intersection(g)
    if A(a) >= 20: rows.append({'id': 'R80_' + i, 'n': i + ': the rest of the mountains, plains and deserts that V2 already held 80% or more of', 'km2': round(A(a)), 'pct': round(A(a) / A(g) * 100, 1)})
C['x']['states'] += rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print(len(rows), 'rows')
