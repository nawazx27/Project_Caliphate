"""Version 464 (Nawaz: "add the entire Ethiopian highlands"). Wikipedia: the Ethiopian (Abyssinian) Highlands are "a rugged mass of mountains extending
from Ethiopia to Eritrea", "with little of its surface falling below 1500 m", "bisected diagonally by the Great East African Rift", the Eritrean Highlands
its northernmost part. So: all land of Ethiopia and Eritrea at 1500 m or more (Mapzen terrain tiles, zoom 6, ~1.2 km cells; tools/dem_fetch.py with
DEM env = the .npz), both the north-western massif and the south-eastern one (Arsi, Bale, Harar), with small holes in it closed and specks under 50 km2
dropped; its DEM edge smoothed of fingers and inlets narrower than ~10 km, pieces under 1,500 km2 dropped. Added to V1 (shj). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, math, shapely, numpy as np
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
D = np.load(os.environ['DEM']); h = D['h']; z = int(D['z']); x0 = int(D['x0']); y0 = int(D['y0']); ts = int(D['ts'])
n = 2 ** z; N = n * ts
mask = (h >= 1500).astype(np.uint8)
polys = []
for g, v in shapes(mask, mask=mask.astype(bool), transform=Affine.identity()):
    def conv(ring):
        out = []
        for X, Y in ring:
            gx = x0 * ts + X; gy = y0 * ts + Y
            lon = gx / N * 360 - 180; lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / N))))
            out.append((lon, lat))
        return out
    polys.append(Polygon(conv(g['coordinates'][0]), [conv(r) for r in g['coordinates'][1:]]))
HI = unary_union(polys).buffer(0)
EE = unary_union([G['Ethiopia'], G['Eritrea']])
HI = HI.intersection(EE)
HI = HI.buffer(0.12).buffer(-0.12).buffer(-0.06).buffer(0.06)   # a natural edge: narrow inlets closed, thin fingers and specks off (~7-13 km)
HI = unary_union([Polygon(q.exterior) for q in getattr(HI, 'geoms', [HI]) if A(q) > 1500]).intersection(EE).buffer(0)
print('Ethiopian Highlands (>=1500 m in Ethiopia and Eritrea)', round(A(HI)), 'km2')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
NEW = HI.difference(V); print('new to V1', round(A(NEW)), 'km2')
X = unary_union([V, HI.buffer(0.004).intersection(EE.buffer(0.004))]).buffer(0)
holes = [Polygon(hh) for q in getattr(X, 'geoms', [X]) for hh in q.interiors if A(Polygon(hh)) < 20000]
X = unary_union([X] + holes).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if A(q) > 30 or not EE.contains(q.centroid)])
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [hh for hh in q.interiors if A(Polygon(hh)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o)
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km
print('shj', old, '->', km, '| Ethiopia in V1', round(100 * G['Ethiopia'].intersection(Y).area / G['Ethiopia'].area), '% | highlands inside', round(100 * HI.intersection(Y).area / HI.area, 2), '%')
for n_, p in {'Jijiga': (42.8, 9.35), 'Ginir': (40.7, 7.13), 'Negele': (39.58, 5.33), 'Yabelo': (38.1, 4.88), 'Konso': (37.43, 5.34), 'Jinka': (36.55, 5.78), 'Mizan Teferi': (35.58, 6.98), 'Bonga': (36.23, 7.27)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
