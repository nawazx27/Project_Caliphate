"""Version 264 (Nawaz, with the Survey of Pakistan's political map (2020, 5th edition; reissued by PIPS, October 2024): "Just make this
preview", then, circling Junagadh, "Leave this area and apply"). V4 (CALIPH.me9) gains the land that map shades as Jammu and Kashmir
beyond Azad Kashmir and Gilgit-Baltistan (already in V4): Indian-administered Jammu and Kashmir and Ladakh (Overture regions IN-JK and
IN-LA, tools/data/indian_kashmir245.geojson) and the Siachen Glacier (base map row KAS; the map runs the Line of Control to the Karakoram
Pass). Not added: Aksai Chin and Shaksgam (the map leaves them "frontier undefined" / on China's side), Junagadh and Manavadar (left by
Nawaz), Sir Creek (only the creek's width). Pockets >= 80% enclosed in 66-82 E, 28-38 N filled, except Tashkurgan (political-border gap).
Run AFTER tools/v4_corsica_sardinia262.py."""
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
JK = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/indian_kashmir245.geojson')))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V, JK.buffer(0.003), G['KAS'].buffer(0.003)], grid_size=0.001)
m = X.intersection(box(66, 28, 82, 38)); mb = m.buffer(0.01); fill = []
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
rows = [{'id': 'IN_JK', 'n': 'Jammu and Kashmir and Ladakh (Indian-administered; shown on Pakistan’s official map as disputed territory)', 'km2': round(A(JK)), 'pct': 100},
        {'id': 'KAS', 'n': 'Siachen Glacier', 'km2': round(A(G['KAS'])), 'pct': 100}]
print('J&K in %', round(100 * A(JK.intersection(Y)) / A(JK), 2), 'Siachen in %', round(100 * A(G['KAS'].intersection(Y)) / A(G['KAS']), 2), 'V4', C['me9']['km2'], '->', km2)
C['me9'].update(polys=out, km2=km2, states=[r for r in C['me9']['states'] if r['id'] not in ('IN_JK', 'KAS')] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
