"""Version 416 PREVIEW (Nawaz, after the blocky Version 409-style push: "I want it to be naturally downward, like how the piece was ending before"). On today's V1 (Egypt +
the whole Hejaz): the lobe's own southern edge of Version 406 (tools/data/v416_v1_v406.json), from the Nafud bay (41.4 E) to the Kuwait coast (48.45 E), is copied and
moved straight down, and the band between the old and the moved edge is filled, so the new edge has the same natural curve; the push is the least that holds all
the Greater Israel land of his red-line and MEE maps (tools/data/v407_*); then the Saudi land east of it is filled to the Gulf shore. Notches against the Hejaz filled.
Then rerun tools/v411_arabia.py. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping, LineString
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
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
LAND = unary_union([g for n, g in G.values()]).buffer(0)
SA = [g for k, (n, g) in G.items() if n == 'Saudi Arabia'][0]
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
OLD = MP(json.load(open(os.path.join(HERE, 'tools/data/v416_v1_v406.json')))['polys'])
# the lobe's own southern edge (Version 406), from the Nafud bay east to the Kuwait coast, sampled every 0.05 deg
LONS = [41.4 + 0.05 * i for i in range(int((48.45 - 41.4) / 0.05) + 1)]
def edge(lon):
    s = OLD.intersection(LineString([(lon, 28.0), (lon, 31.5)]))
    return min(g.bounds[1] for g in getattr(s, 'geoms', [s]))
PROF = [(x, edge(x)) for x in LONS]
WEDGE = unary_union([shape(json.load(open(os.path.join(HERE, 'tools/data/' + f + '.geojson')))['geometry']).buffer(0) for f in ['v407_nile_euphrates_redline', 'v407_nile_euphrates_mee']]).intersection(shapely.box(36.5, 20, 50, 33)).intersection(LAND)
DY = float(os.environ.get('DY', '2.0'))
def band(dy): return Polygon(PROF + [(x, y - dy) for x, y in reversed(PROF)]).buffer(0)
def shore(dy):   # east of the band, Saudi land to the Gulf shore, between the pushed-down corner and the old corner
    y0 = PROF[-1][1] - dy; return SA.intersection(shapely.box(PROF[-1][0] - 0.02, y0, 51.0, PROF[-1][1] + 0.6))
def grown(dy): return unary_union([V, band(dy), shore(dy)]).buffer(0)
while A(WEDGE.difference(grown(DY).buffer(0.003))) > 1: DY += 0.05
print('   the lobe edge pushed down', round(DY, 2), 'deg (~%d km), keeping its own curve; then filled east to the Gulf shore' % round(DY * 111))
NEW = unary_union([band(DY), shore(DY)]).intersection(LAND)
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 20000]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
X = unary_union([X] + holes)
B_ = shapely.box(39, 22, 51, 30.5); LEFT = LAND.intersection(B_).difference(X)
for q in getattr(LEFT, 'geoms', [LEFT]):   # notches left between the pushed lobe and the Hejaz (no-gaps rule)
    if q.area and A(q) < 20000 and q.buffer(0.02).difference(X.buffer(0.02)).area < 0.25 * q.buffer(0.02).area:
        print('     notch filled:', round(A(q)), 'km2 at', [round(c, 2) for c in q.representative_point().coords[0]]); X = unary_union([X, q.buffer(0.003)])
X = X.buffer(0).intersection(V3.buffer(0.002))
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Hail': (41.69, 27.52), 'Hafar al-Batin': (45.97, 28.43), 'Buraydah': (43.97, 26.33), 'Khafji': (48.49, 28.43), 'Jubail': (49.66, 27.01), 'Dammam': (50.1, 26.43), 'Riyadh (out)': (46.72, 24.69), 'Bahrain (out)': (50.58, 26.22)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('wedge land outside', round(A(WEDGE.difference(Y.buffer(0.005)))), '| shj outside me2', round(A(Y.difference(V3.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
