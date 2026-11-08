"""Version 347 PREVIEW (Nawaz, on a screenshot of V5 with the Caucasus circled: "Push this exact shape of the crown upward so that
the entire Black Sea is engulfed and the land is completely connected"). The northern edge of V5's Caucasus "crown" (the crest line
from Sochi to Derbent) is moved north by DY degrees, keeping its exact shape; west of the crown's tip the pushed line runs on at the
tip's height to the old Don-Novorossiysk line. All Russian land between the old crest line and the pushed line is added, which
closes the gap on the Black Sea coast (Arkhipo-Osipovka - Tuapse - Lazarevskoye) so the whole Black Sea is ringed by V5.
A design choice of the author (outline is his specification), not a historical holding."""
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
from shapely.geometry import LineString
DY = float(os.environ.get('DY', '0.6'))
V0 = M('grm')
def top(lon):
    seg = V0.intersection(LineString([(lon, 40.5), (lon, 47.5)]))
    tops = [g.bounds[3] for g in getattr(seg, 'geoms', [seg]) if not g.is_empty and g.bounds[1] < 44.2 and g.bounds[3] < 44.5]
    return max(tops) if tops else None
lons = [round(39.5 + i * 0.02, 2) for i in range(int((49.2 - 39.5) / 0.02) + 1)]
pts = [(x, top(x)) for x in lons]; pts = [(x, y + DY) for x, y in pts if y is not None]
west = pts[0][1]
ring = [(37.6, 40.0), (37.6, west)] + pts + [(49.3, pts[-1][1]), (49.3, 40.0)]
POD = Polygon(ring).buffer(0).intersection(G['643'][1])
V5 = M('grm'); print('pushed crown, DY =', DY, 'adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Tuapse': (39.07, 44.10), 'Lazarevskoye': (39.33, 43.91), 'Novomikhaylovsky (Nicopsis)': (38.85, 44.26), 'Dzhubga': (38.70, 44.32), 'Maykop': (40.10, 44.61), 'Cherkessk': (42.06, 44.23), 'Nalchik': (43.61, 43.49), 'Vladikavkaz': (44.68, 43.02), 'Grozny': (45.69, 43.32), 'Makhachkala': (47.50, 42.98), 'Krasnodar': (38.98, 45.04), 'Stavropol': (41.97, 45.04)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
