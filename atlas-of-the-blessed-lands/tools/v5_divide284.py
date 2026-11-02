"""Version 284 (Nawaz: "Does the Indian subcontinent have the natural borders in V5?"; two natural northern lines previewed on elevation
data: 1 the main Himalayan crest, 2 the Indus-Ganges-Brahmaputra drainage divide; "Option 2").
V5's land in China (except Aksai Chin and the Shaksgam valley, kept whole for the princely state of Jammu and Kashmir) is replaced by the
part of the Indus and Ganges-Brahmaputra basins that lies in China (tools/data/indus_ganges_brahmaputra_basins284.geojson, made by
tools/basins_dem284.py): the whole Yarlung Tsangpo valley with Lhasa and Shigatse, Mount Kailash and Lake Manasarovar, and the upper
Indus and Sutlej in Ngari, to the Transhimalaya (Gangdise, Nyenchen Tanglha); the inland Changtang plateau stays out.
Run after tools/v5_subcontinent283.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
K = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/china_kashmir_ne.geojson')))['features']])
B = shape(json.load(open(os.path.join(P, 'tools/data/indus_ganges_brahmaputra_basins284.geojson')))['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sas']['polys']]).buffer(0)
CN = G['156']
X = unary_union([V.difference(CN.difference(K.buffer(0.02))), B.intersection(CN).buffer(0.003)])
X = shapely.set_precision(X.buffer(0), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for r in C['sas']['states']:
    if r['id'] == '156_S':
        a = A(CN.intersection(Y)); r.update(km2=round(a), pct=round(100 * a / A(CN), 1),
            n='China: Aksai Chin and the Shaksgam valley (all of the princely state of Jammu and Kashmir), and the Tibetan headwaters of the Indus, Sutlej and Brahmaputra to the drainage divide (the Yarlung Tsangpo valley with Lhasa and Shigatse, Mount Kailash and Lake Manasarovar, Ngari)')
print('V5 (sas)', C['sas']['km2'], '->', km2)
C['sas'].update(polys=out, km2=km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
