"""Version 148 (2026-10-16). Nawaz: "Make newly drawn border look nice. And implement natural border rule since changes we started
making since lake Albert"; asked, he chose "Closest natural features", and for DR Congo "Follow the crest" (about 94,000 km² goes).
 - Africa west of the great lakes: the rift's western crest, i.e. the edge of the lakes' own drainage basin (Albert, Edward, Kivu,
   Tanganyika), traced on the Mapzen elevation tiles (tools/dem_fetch.py → tools/data/dem_rift_z8.npz; tools/crest_basin.py, 1:4,
   → tools/data/rift_basin148.geojson). In DR Congo only the land inside that basin stays in V2/V2-B.
 - Africa south-east: no river or crest runs along his line (the Chambeshi, Luangwa, Shire and Licungo all cross it), so his line
   (Version 147) is kept but smoothed (Chaikin); east of it Zambia, Malawi and Mozambique stay in.
 - The Caucasus: the Kuban and Kuma rivers (tools/caucasus_natural148.py → tools/data/caucasus_natural148.geojson).
Rewrites the DR Congo, Zambia, Malawi, Mozambique and North Caucasus parts of V2 and V2-B (other lands untouched); towns follow
(tools/expand_towns146.py). Run: python3 tools/natural148.py. My method; Nawaz's choices."""
import json, os, subprocess, shapely
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
F = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
land = unary_union(list(F.values()))
lakes = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']])
def chaikin(c, n=3):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
# Africa
B = shape(json.load(open(os.path.join(D, 'rift_basin148.geojson')))['geometry']).buffer(0)
B = Polygon(chaikin(list(B.simplify(0.01).exterior.coords), 2)).buffer(0)      # the crest, neatened (cells are ~2 km)
L = json.load(open(os.path.join(D, 'africa_line147.json')))['features'][0]['geometry']['coordinates']
Ls = chaikin(list(LineString(L).simplify(0.03).coords), 4)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'Version 147 line, smoothed'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'africa_line148_smooth.json'), 'w'))
E = Polygon(Ls + [(42.0, Ls[-1][1]), (42.0, Ls[0][1])]).buffer(0).intersection(unary_union([land, lakes]))
AZ = unary_union([F[c] for c in ('180', '894', '454', '508')]).intersection(box(24, -20, 42, 6))
keep_af = AZ.intersection(unary_union([B, E.difference(F['180'])]))
# the lakes' own water in DR Congo stays (Lake Albert, Kivu, Tanganyika halves)
keep_af = unary_union([keep_af, AZ.intersection(lakes).intersection(B.buffer(0.05))])
# Caucasus
cau = shape(json.load(open(os.path.join(D, 'caucasus_natural148.geojson')))['features'][0]['geometry']).buffer(0)
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
RZ = F['643'].intersection(box(36.0, 41.0, 49.0, 46.8)).difference(cr)
for name, g in (('africa_natural148.geojson', keep_af), ('caucasus_zone148.geojson', RZ), ('africa_zone148.geojson', AZ)):
    json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add' if 'natural' in name else 'zone'}, 'geometry': mapping(g)}]}, open(os.path.join(D, name), 'w'))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ('x', 'xb'):
    X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    before = {n: A(X.intersection(z)) for n, z in (('Africa zone', AZ), ('North Caucasus', RZ))}
    X = X.difference(AZ).difference(RZ)
    X = shapely.union_all([shapely.make_valid(g) for g in (X, keep_af, cau)], grid_size=0.001)
    X = MultiPolygon([q for q in getattr(X, 'geoms', [X]) if q.geom_type == 'Polygon'])
    after = {n: A(X.intersection(z)) for n, z in (('Africa zone', AZ), ('North Caucasus', RZ))}
    print(k, {n: (round(before[n]), round(after[n])) for n in before})
    from shapely.geometry.polygon import orient
    out = []
    for p in X.geoms:
        p = orient(Polygon(p.exterior, [h for h in p.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(x, 3), round(y, 3)] for x, y in r.coords] for r in [p.exterior, *p.interiors]])
    C[k]['polys'] = out
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(k, 'km2', C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
