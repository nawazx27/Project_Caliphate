"""Version 407/408 PREVIEW (408: MODE=drag (default): Egypt from the shapes only; in Arabia V1's lobe between the Tayyi edge and Kuwait is dragged down DY degrees (default 1.0) instead of the flat line; MODE=flat = the Version 407 form). Version 407 PREVIEW (Nawaz: his red line from the Nile to the Euphrates and the Middle East Eye map of the "Nile to Euphrates" shape: "Does it have everything of this red line?" -> "Preview").
V1 (shj) gets all land inside either shape (tools/data/v407_nile_euphrates_redline.geojson traced on his map, fit ~9 km; v407_nile_euphrates_mee.geojson traced from the MEE map, ~25-40 km):
Egypt east of the Nile from the Delta to Aswan with the Eastern Desert, and the Ha'il - Hafar al-Batin wedge of Saudi Arabia. Kept inside V2. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
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
LAND = unary_union([g for n, g in G.values()])
SH = unary_union([shape(json.load(open(os.path.join(HERE, 'tools/data/' + f + '.geojson')))['geometry']).buffer(0) for f in ['v407_nile_euphrates_redline', 'v407_nile_euphrates_mee']])
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
MODE = os.environ.get('MODE', 'drag')
if MODE == 'drag':   # Version 408: Nawaz: "The Nile is good, but just drag that piece which I circled downward instead of taking the flat line"
    SH = SH.intersection(shapely.box(28, 20, 36.5, 33))     # keep only the Egyptian (Nile) part of the two shapes
    DY = float(os.environ.get('DY', '1.0'))
    PIECE = V.intersection(shapely.box(41.9, 27, 48.6, 31.5))   # V1's lobe between the Tayyi edge and Kuwait, the piece he circled
    SWEPT = unary_union([shapely.affinity.translate(PIECE, 0, -DY * i / 40) for i in range(41)]).buffer(0)
    print('   dragged down', DY, 'deg; new land from the drag', round(A(SWEPT.intersection(LAND).difference(V))), 'km2')
    SH = unary_union([SH, SWEPT])
NEW = SH.intersection(LAND).difference(V)
print('   land added', round(A(NEW)), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) > 0.5]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
def polys_lakes(X, mn=0.02):   # like polys(), but keeps holes of 100 km2 or more (Lake Manzala, which V2 leaves as water)
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
o = polys_lakes(unary_union([X] + holes).buffer(0).intersection(V2.buffer(0.002))); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Cairo': (31.24, 30.04), 'Luxor': (32.64, 25.69), 'Aswan': (32.9, 24.09), 'Hurghada': (33.81, 27.26), 'Port Said': (32.3, 31.26), 'Suez': (32.55, 29.97), 'Hail': (41.69, 27.52), 'Hafar al-Batin': (45.97, 28.43), 'Giza (west bank)': (31.21, 30.01), 'Alexandria (out?)': (29.92, 31.2), 'Riyadh (out)': (46.72, 24.69)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('red line land outside', round(A(SH.intersection(LAND).difference(Y.buffer(0.005)))), '| shj outside me2', round(A(Y.difference(V2.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
