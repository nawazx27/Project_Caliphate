"""Version 432 (Nawaz: "Add the entire Arabian peninsula to v1"). V1 (shj) += the whole Arabian Peninsula as whole countries with all their islands:
Saudi Arabia, Yemen (with Socotra), Oman (Musandam, Kuria Muria), the UAE, Qatar, Bahrain, Kuwait; small enclosed pockets closed. V1's own land is kept as it is
(not clipped); only the added land is kept inside V2 (me2). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
NAMES = ['Saudi Arabia', 'Yemen', 'Oman', 'United Arab Emirates', 'Qatar', 'Bahrain', 'Kuwait']
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
parts = [g for k, (n, g) in G.items() if n in NAMES]
print('   countries found', sorted(n for k, (n, g) in G.items() if n in NAMES))
add = unary_union([g.buffer(0.003) for g in parts]).buffer(0).intersection(V2.buffer(0.002))
X = unary_union([V, add]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 34.5]   # only pockets in Arabia: Egypt's Lake Manzala and Lake Burullus stay water
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
o = polys(unary_union([X] + holes).buffer(0)); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']
C['shj'] = {**C['shj'], 'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Riyadh': (46.72, 24.69), 'Sanaa': (44.21, 15.35), 'Aden': (45.03, 12.79), 'Muscat': (58.41, 23.59), 'Socotra': (53.85, 12.48), 'Doha': (51.53, 25.29), 'Manama': (50.58, 26.22), 'Abu Dhabi': (54.37, 24.45), 'Dubai': (55.27, 25.2), 'Najran': (44.13, 17.49), 'Kuria Muria': (56.0, 17.5), 'Musandam': (56.25, 26.2), 'Salalah': (54.09, 17.02)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('old V1 lost', round(A(V.difference(Y.buffer(0.005)))), 'km2 | Arabia not in new V1', round(A(unary_union(parts).difference(Y.buffer(0.005)))), 'km2')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
