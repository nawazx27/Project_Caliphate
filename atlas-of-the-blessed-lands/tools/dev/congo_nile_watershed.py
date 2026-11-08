"""Nile part of DR Congo: priority-flood watershed on Mapzen terrain (zoom 8, ~300 m). Seeds: Lakes Albert, Edward, George = Nile;
Lake Kivu = Congo; box edges: east = Nile, west = Congo, north = Nile east of 30.7E else Congo, south = Nile east of 29.3E else Congo.
Usage: python3 tools/dev/congo_nile_watershed.py dem.npz out.geojson"""
import json, math, heapq, sys, numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from rasterio import features
from rasterio.transform import Affine
d = np.load(sys.argv[1]); h = d['h'].astype(np.float32); Z = int(d['z']); x0 = int(d['x0']); y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z
H, W = h.shape
def px(lon, lat):
    return ((lon + 180) / 360 * n - x0) * TS, ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - y0) * TS
def ll(x, y):
    X = np.asarray(x); Y = np.asarray(y)
    return (X / TS + x0) / n * 360 - 180, np.degrees(np.arctan(np.sinh(math.pi * (1 - 2 * (Y / TS + y0) / n))))
lakes = {f['properties']['name']: shape(f['geometry']) for f in json.load(open('lakes.geojson'))['features'] if f['properties'].get('name') in ('Lake Albert', 'Lake Edward', 'Lake George', 'Lake Kivu')}
label = np.zeros((H, W), np.int8)
for nm, g in lakes.items():
    im = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(im)
    for p in getattr(g, 'geoms', [g]): dr.polygon([px(*c) for c in p.exterior.coords], fill=1)
    label[np.array(im).astype(bool)] = 2 if nm == 'Lake Kivu' else 1
seeded = label > 0
lonc = ll(np.arange(W), np.zeros(W))[0]; latr = ll(np.zeros(H), np.arange(H))[1]
for x in range(W):
    for y in (0, H - 1):
        if label[y, x] == 0: label[y, x] = 1 if ((y == 0 and lonc[x] > 30.7) or (y == H - 1 and lonc[x] > 29.3)) else 2
for y in range(H):
    if label[y, 0] == 0: label[y, 0] = 2
    if label[y, W - 1] == 0: label[y, W - 1] = 1
heap = []
ys, xs = np.nonzero(label)
for y, x in zip(ys, xs):
    e = -1000.0 if seeded[y, x] else float(h[y, x]); heapq.heappush(heap, (e, int(y), int(x)))
nb = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
while heap:
    e, y, x = heapq.heappop(heap); L = label[y, x]
    for dy, dx in nb:
        yy, xx = y + dy, x + dx
        if 0 <= yy < H and 0 <= xx < W and label[yy, xx] == 0:
            label[yy, xx] = L; heapq.heappush(heap, (max(float(h[yy, xx]), e), yy, xx))
nile = (label == 1).astype('uint8')
P = unary_union([shape(g) for g, v in features.shapes(nile, mask=nile == 1, transform=Affine.identity()) if v == 1])
G = transform(ll, P).buffer(0).simplify(0.003)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Nile drainage (Lakes Albert, Edward, George) in the box 27.5-31.6E, 2.6S-3.6N, priority-flood watershed on Mapzen terrain z8'}, 'geometry': mapping(G)}]}, open(sys.argv[2], 'w'))
print('done')
