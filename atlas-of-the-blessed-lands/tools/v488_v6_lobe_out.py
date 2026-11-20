"""Version 488 (Nawaz, a red circle on V6 round its East African lobe (Uganda, Rwanda, Burundi, Tanzania and Kenya, with Lake Victoria): "You see this
shape?", then "Push that shape a bit outward"). The lobe (V6 = CALIPH.tib within those five countries) is enlarged as one piece, its own shape, about its
own centre, by SCALE (default 1.10: ~0.5 deg out on the west, ~1 deg on the south), cut to land and joined; enclosed pockets filled. Done to V6 (tib)
and to V7 (sup, which holds V6) alike. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, shapely.affinity
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(15, -25, 45, 8))]).buffer(0)
LOBE = unary_union([G[n] for n in ['Tanzania', 'Uganda', 'Rwanda', 'Burundi', 'Kenya']]).buffer(0.05)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
s = float(os.environ.get('SCALE', '1.10'))
B = MP(C['tib']['polys']).intersection(LOBE)
c = B.centroid; print('lobe', round(A(B)), 'km2, centre', round(c.x, 2), round(c.y, 2), '| scale', s)
BS = shapely.affinity.scale(B, s, s, origin=c).intersection(LAND)
for key in ['tib', 'sup']:
    V = MP(C[key]['polys'])
    X = unary_union([V, BS]).buffer(0)
    X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 20000]).buffer(0)
    add = X.difference(V); print(key, 'added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 200})
    X = shapely.set_precision(X, 0.001); o = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
        o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
    km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
    Y = MP(o); print('  ', key, C[key]['km2'], '->', km, '| Goma', Y.contains(Point(29.22, -1.68)), '| Bukavu', Y.contains(Point(28.86, -2.5)), '| Kalemie', Y.contains(Point(29.19, -5.94)), '| Mbala (Zambia)', Y.contains(Point(31.33, -8.84)), '| Lilongwe', Y.contains(Point(33.78, -13.97)))
    C[key]['polys'] = o; C[key]['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
