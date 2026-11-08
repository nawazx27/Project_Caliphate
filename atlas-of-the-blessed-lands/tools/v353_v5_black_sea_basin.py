"""Version 353 PREVIEW (Nawaz sent Wikipedia's "Mediterranean basin"; V5 already holds the whole Mediterranean climate region, all
of Macaronesia and the whole Mediterranean drainage basin (Nile, Rhone); the one limit: on the widest view the Black Sea's rivers
drain to the Mediterranean too -> "Preview"). V5 (grm) takes the whole drainage basin of the Black Sea and the Sea of Azov (Danube,
Dniester, Southern Bug, Dnieper with the Pripyat and Desna, Don, Kuban and the Anatolian and Caucasian rivers), computed here by a
priority-flood watershed from the Mapzen terrain tiles at zoom 5 (~1.5-3 km) with the atlas's land (tools/data/v353_black_sea_basin.geojson,
2.41 million km2; approximate along low divides such as the Pripyat marshes). A design choice of the author, not a historical holding."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
BASIN = shape(json.load(open(os.path.join(P, 'tools/data/v353_black_sea_basin.geojson')))['features'][0]['geometry']).buffer(0)
LAND = unary_union([g for n, g in G.values() if g.intersects(BASIN)])
POD = BASIN.intersection(LAND)
V5 = M('grm'); print('Black Sea basin adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Kyiv': (30.52, 50.45), 'Kharkiv': (36.23, 49.99), 'Minsk (Dnieper basin?)': (27.56, 53.90), 'Gomel': (30.98, 52.43), 'Smolensk': (32.05, 54.78), 'Bryansk': (34.36, 53.24), 'Kursk': (36.19, 51.73), 'Voronezh': (39.20, 51.67), 'Volgograd (Volga, stays out)': (44.51, 48.71), 'Stavropol': (41.97, 45.04), 'Lviv': (24.03, 49.84), 'Prague (Elbe, stays out)': (14.42, 50.08), 'Moscow (Volga, stays out)': (37.62, 55.75), 'Warsaw (Vistula, stays out)': (21.01, 52.23)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
