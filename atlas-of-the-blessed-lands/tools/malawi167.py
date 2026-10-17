"""Version 167 (Nawaz, screenshot of the V2 outline along Lake Malawi: "Take the left of the border"). All of Malawi, and the whole of Lake Malawi
(Natural Earth lake; the outline had cut it along Mozambique's and Tanzania's shores), added to V2 and V2-B. V7 is rebuilt from V2.
Run: python3 tools/malawi167.py, then tools/v7_build159.py, then the clean-up loop."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}; land = unary_union(list(G.values()))
MW = G['454']
lake = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Malawi'])
reg = unary_union([MW, lake]).buffer(0)
print('Malawi', round(A(MW)), 'km2; Lake Malawi', round(A(lake)), 'km2; together', round(A(reg)))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 167 Malawi and Lake Malawi'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'malawi167.geojson'), 'w'))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def pack(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out): return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for k in ('x', 'xb'):
    X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    add = reg.difference(X); print(k, 'adds', round(A(add)))
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003).union(lake.buffer(0.003))))], grid_size=0.001)
    C[k]['polys'] = pack(X2); C[k]['km2'] = km2(C[k]['polys'])
    C[k]['states'] = [r for r in C[k]['states'] if r['id'] != '454']
    C[k]['states'].append({'id': '454', 'n': 'Malawi', 'km2': round(A(MW)), 'pct': 100})
    C[k]['states'].append({'id': '454_L', 'n': 'Lake Malawi: the whole lake, including its Mozambican and Tanzanian shores', 'km2': round(A(lake.difference(MW))), 'pct': 100})
    print(k, C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
