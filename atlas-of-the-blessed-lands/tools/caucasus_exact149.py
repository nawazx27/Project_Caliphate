"""Version 149 (2026-10-16, Nawaz, with a screenshot of the Kuban–Kuma border of Version 148 and his orange Caucasus map again: "This
is bad. I asked for this exact one"). The North Caucasus edge of V2 and V2-B goes back to the top edge of his orange shading as
fitted in Version 147 (tools/data/caucasus_line147.json: the sketch matched to the real borders and coasts), smoothed (Chaikin) so
it is the same gentle line as on his map, from the Kerch Strait to the Caspian shore; no town bumps on it (he wants the shape
exactly). All of Russia south of it, land only, Crimea out. Writes tools/data/caucasus_exact149.geojson and rewrites the North
Caucasus zone of V2 and V2-B. Run: python3 tools/caucasus_exact149.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, mapping, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
def chaikin(c, n=4):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
L = json.load(open(os.path.join(D, 'caucasus_line147.json')))['features'][0]['geometry']['coordinates']
Ls = chaikin(list(LineString(L).simplify(0.06).coords), 4)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'orange top edge (Version 147 fit), smoothed'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'caucasus_line149_smooth.json'), 'w'))
R = Polygon([(36.3, Ls[0][1])] + Ls + [(48.6, Ls[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
reg = R.intersection(RU).difference(cr)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 149 Caucasus (orange, exact)'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'caucasus_exact149.geojson'), 'w'))
RZ = shape(json.load(open(os.path.join(D, 'caucasus_zone148.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ('x', 'xb'):
    X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    b = A(X.intersection(RZ))
    X = shapely.union_all([shapely.make_valid(X.difference(RZ)), shapely.make_valid(reg)], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(a, 3), round(c, 3)] for a, c in r.coords] for r in [q.exterior, *q.interiors]])
    C[k]['polys'] = out
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(k, 'North Caucasus zone', round(b), '->', round(A(reg)), 'km2; total', C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
