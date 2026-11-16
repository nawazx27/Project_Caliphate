"""Version 471 (Nawaz, five Nile maps (the Nile and its branches; the basin with its sources, the Lake Victoria outlet, Murchison Falls, the
dams): "Preview expanding it until we have the entire river.. end to end?"). As tools/v468, the same shape made larger: V1's African piece (south of
22 N, east of Libya) is scaled as one piece about 23.98 E 22.0 N, the point on the Egypt line straight above the original 24 E Sudan-Chad border, so that straight border stays on 24 E and the top stays on 22 N (Nawaz: "take it to its original straight border on the left side"; ORIGIN env; other anchors tried: 31 E 22 N +2.02M km2 but moves the straight border west, 25.06 E 20 N +2.21M, 36 E 15 N +2.42M, 40 E 12 N +4.96M; this one +2.16M) by the SMALLEST factor that puts the whole Nile
inside V1: every traced part of src/four_rivers.json from the Kagera headwaters in Burundi and Rwanda to the Delta, and the lakes it runs through
(Victoria, Kyoga, Albert, No, Tana) whole. Cut to African land, joined to V1, enclosed pockets filled. DIR env = project dir; SCALE env overrides the
factor. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, shapely.affinity, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from rasterio.features import shapes
from rasterio.transform import Affine
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
# ---- the target: the whole Nile end to end (src/four_rivers.json, every traced part, the Kagera headwaters to the Delta) and the lakes it runs through
NL = json.load(open(os.path.join(P, 'src/four_rivers.json')))['rivers']; NL = [r for r in NL if r['k'] == 'nile'][0]['parts']
LAKES = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']
         if str(f['properties'].get('name')) in ('Lake Victoria', 'Lake Kyoga', 'Lake Albert', 'Lake Tana', 'Lake No')]
HI = unary_union([shapely.LineString(c).buffer(0.01) for c in NL] + LAKES).buffer(0)
print('target: the Nile', len(NL), 'parts, lakes', len(LAKES))
# ---- V1 and its African piece
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
ASIA = {'Yemen', 'Saudi Arabia', 'Oman', 'Israel', 'Palestine', 'Jordan'}
AFL = unary_union([g for n_, g in G.items() if n_ not in ASIA and g.intersects(shapely.box(12, -8, 52, 23))]).buffer(0)   # African land round it
B = V.intersection(shapely.box(12, -10, 52, 22.0)).intersection(AFL).difference(G['Libya']).buffer(0)   # the whole piece, Darfur and eastern Chad included (a box edge at 25 E had left a straight cut line)
Cc = tuple(float(v) for v in os.environ.get('ORIGIN', '23.982,22.0').split(','))
def grow(s):
    BS = shapely.affinity.scale(B, s, s, origin=Cc).intersection(AFL)
    return unary_union([V, BS]).buffer(0)
miss = lambda X: A(HI.difference(X.buffer(0.002))) if not HI.difference(X.buffer(0.002)).is_empty else 0
print('highlands outside V1 now', round(miss(V)), 'km2')
if os.environ.get('SCALE'): s = float(os.environ['SCALE'])
else:
    lo, hi = 1.0, 2.5
    for _ in range(14):
        mid = (lo + hi) / 2
        if miss(grow(mid)) < 1: hi = mid
        else: lo = mid
    s = hi
X = grow(s); X = unary_union([V, X.difference(V).buffer(-0.03).buffer(0.03).intersection(AFL)]).buffer(0)   # hairline slivers of the enlarged piece dropped
print('scale', round(s, 4), '| highlands outside after', round(miss(X), 1), 'km2')
X = unary_union([X] + [Polygon(hh) for q in getattr(X, 'geoms', [X]) for hh in q.interiors if A(Polygon(hh)) < 80000]).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 1 or not (20 < q.centroid.x < 52 and q.centroid.y < 15)])
add = X.difference(V)
print('added', round(A(add)), 'km2', {k: round(A(add.intersection(G[k]))) for k in G if G[k].intersects(add) and A(add.intersection(G[k])) > 500})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [hh for hh in q.interiors if A(Polygon(hh)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
for n_, p in {'Jinja (Nile leaves Lake Victoria)': (33.2, 0.43), 'Kampala': (32.58, 0.32), 'Kigali': (30.06, -1.95), 'Mwanza': (32.9, -2.52), 'Bujumbura': (29.36, -3.38), 'Nairobi': (36.82, -1.29), 'Kisumu': (34.76, -0.1), 'Lodwar': (35.6, 3.12), 'Mogadishu': (45.34, 2.05), 'Bangui': (18.56, 4.36), 'Kisangani': (25.19, 0.52), 'Abeche': (20.83, 13.83), 'Ndjamena': (15.04, 12.11)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
