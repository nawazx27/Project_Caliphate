"""Version 151 (2026-10-16, Nawaz: "Return to modern Azerbaijan and Georgia borders"). All Russian land in the Caucasus leaves V2
and V2-B (the orange-map North Caucasus of Versions 146-150 and V5's Dagestan block with Derbent): the border is the modern northern
border of Georgia and Azerbaijan. Writes tools/data/russia_out151.geojson (Russia from the Kerch Strait to the Caspian, Crimea
included) which tools/whole_slivers.py subtracts from the held lands, and rewrites V2 and V2-B. Run: python3 tools/caucasus_modern151.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, Polygon, MultiPolygon, mapping, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
RZ = RU.intersection(box(32.0, 41.0, 49.5, 47.5))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'Russia in the Caucasus, out of V2/V2-B (Version 151)'}, 'geometry': mapping(RZ)}]}, open(os.path.join(D, 'russia_out151.geojson'), 'w'))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ('x', 'xb'):
    X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    print(k, 'Russian land in the Caucasus before', round(A(X.intersection(RZ))), 'km2')
    X = shapely.make_valid(X.difference(RZ.buffer(0.002)))   # a hair past the border so no Russian rim remains
    X = shapely.union_all([X], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    C[k]['polys'] = out
    C[k]['states'] = [r for r in C[k]['states'] if not str(r['id']).startswith('643')]
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(k, 'total', C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
