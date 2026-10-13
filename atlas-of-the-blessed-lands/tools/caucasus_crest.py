"""Version 109 (2026-10-13, Nawaz: "Make this place follow its natural border"; he chose: out to the crest of the Greater Caucasus,
keep the rest (Georgia and Azerbaijan stay whole), in V2, V2-B and V2N).
Finds the land on the southern side of the Greater Caucasus watershed that is not yet in V2: Russia's Black Sea coast from the
Taman side to the Psou (Anapa, Novorossiysk, Gelendzhik, Tuapse, Sochi) and any other Russian land south of the crest.
Method (mine): elevation from the Mapzen terrain tiles (tools/data/dem_caucasus_z8.npz, from tools/dem_fetch.py), kept at its crests
(highest point in each 2 x 2 block); the sea (land per the base map geo2.json) is a barrier; two floods rise from seeds on each side
(south: the Black Sea coast towns and Transcaucasia; north: the Kuban, Terek and Dagestan plains) and every cell takes the label of
the flood that reaches it by the lowest pass, so the floods meet on the watershed.
Writes tools/data/caucasus_south_of_crest.geojson (the Russian land on the southern side). Run: python3 tools/caucasus_crest.py"""
import json, os, math, heapq, subprocess, numpy as np
from shapely.geometry import shape, Polygon, MultiPolygon, mapping, box
from shapely.ops import unary_union
from rasterio.features import rasterize, shapes
from affine import Affine
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
d = np.load(os.path.join(H, 'data', 'dem_caucasus_z8.npz'))
h = d['h'].astype(np.float32); Z = int(d['z']); X0 = int(d['x0']); Y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z; f = 2
Hh, Ww = h.shape[0] // f, h.shape[1] // f
g = h[:Hh * f, :Ww * f].reshape(Hh, f, Ww, f).max(axis=(1, 3))
def ll(r, c):   # cell centre
    x = ((c + 0.5) * f / TS + X0) / n; y = ((r + 0.5) * f / TS + Y0) / n
    return x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
def px(lon, lat):
    fx = ((lon + 180) / 360 * n - X0) * TS / f
    fy = ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - Y0) * TS / f
    return int(fy), int(fx)
lons = np.array([ll(0, c)[0] for c in range(Ww)]); lats = np.array([ll(r, 0)[1] for r in range(Hh)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=R))
CT = {str(f_['id']): shape(f_['geometry']).buffer(0) for f_ in geo['features']}
# rasterise land and Russia on the (Mercator) cell grid: rows are not evenly spaced in latitude, so rasterise row by row bands
LON0, LON1 = lons[0], lons[-1]
def rast(geom):
    out = np.zeros((Hh, Ww), bool)
    dx = lons[1] - lons[0]
    for r in range(Hh):
        lat = lats[r]
        row = geom.intersection(box(LON0 - dx, lat - 1e-6, LON1 + dx, lat + 1e-6))
        if row.is_empty: continue
        for seg in getattr(row, 'geoms', [row]):
            b = seg.bounds; c0 = max(0, int(math.ceil((b[0] - LON0) / dx))); c1 = min(Ww - 1, int((b[2] - LON0) / dx))
            out[r, c0:c1 + 1] = True
    return out
bb = box(LON0, lats[-1], LON1, lats[0])
land = rast(unary_union([g_ for g_ in CT.values() if g_.intersects(bb)]))
rus = rast(CT['643'])
SOUTH = [(39.72, 43.59), (39.07, 44.10), (38.06, 44.56), (37.77, 44.72), (37.32, 44.89), (41.02, 43.00), (42.70, 42.27), (44.80, 41.70),
         (46.36, 40.68), (47.17, 41.20), (48.63, 40.63), (49.87, 40.41), (43.00, 41.60), (45.40, 41.30)]
NORTH = [(38.98, 45.04), (40.10, 44.60), (42.06, 44.23), (43.60, 43.49), (44.68, 43.02), (45.69, 43.32), (47.50, 42.98), (48.29, 42.06),
         (37.38, 45.27), (38.12, 45.26), (41.97, 45.04), (43.06, 44.04), (46.71, 43.85), (48.15, 41.60), (47.70, 42.40), (39.50, 45.40)]
lab = np.zeros((Hh, Ww), np.int8); heap = []
def seed(r, c, l):
    if 0 <= r < Hh and 0 <= c < Ww and land[r, c] and not lab[r, c]: lab[r, c] = l; heapq.heappush(heap, (float(g[r, c]), r, c))
for lo, la in SOUTH:
    r, c = px(lo, la)
    for dr in range(-3, 4):
        for dc in range(-3, 4): seed(r + dr, c + dc, 1)
for lo, la in NORTH:
    r, c = px(lo, la)
    for dr in range(-3, 4):
        for dc in range(-3, 4): seed(r + dr, c + dc, 2)
for c in range(Ww): seed(0, c, 2)                     # the northern edge of the grid is on the northern side
while heap:
    e, r, c = heapq.heappop(heap); l = lab[r, c]
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < Hh and 0 <= cc < Ww and land[rr, cc] and not lab[rr, cc]:
            lab[rr, cc] = l; heapq.heappush(heap, (max(e, float(g[rr, cc])), rr, cc))
south_ru = (lab == 1) & rus
print('Russian cells on the southern side', int(south_ru.sum()), 'of land cells', int(land.sum()), 'unlabelled land', int((land & (lab == 0)).sum()))
# vectorise in cell space, then map vertices to lon/lat
geoms = []
for gm, v in shapes(south_ru.astype('uint8'), mask=south_ru, transform=Affine.identity()):
    def tx(ring): return [ (lambda c, r: ( (lambda x: x * 360 - 180)((c * f / TS + X0) / n), math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ((r * f / TS + Y0) / n))))) ))(c, r) for c, r in ring]
    geoms.append(Polygon(tx(gm['coordinates'][0]), [tx(q) for q in gm['coordinates'][1:]]))
S = unary_union(geoms).intersection(CT['643'])
parts = sorted([p for p in getattr(S, 'geoms', [S]) if p.area > 0.0005], key=lambda p: -p.area)   # drop specks under ~5 km²
from pyproj import Geod
geod = Geod(ellps='WGS84'); A = lambda q: abs(geod.geometry_area_perimeter(q)[0]) / 1e6
for p in parts: print('  piece', round(A(p)), 'km2 at', [round(v, 2) for v in p.bounds])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'km2': round(A(p))}, 'geometry': mapping(p)} for p in parts]},
          open(os.path.join(H, 'data', 'caucasus_south_of_crest.geojson'), 'w'))
np.save('/tmp/caucasus_lab.npy', lab)
