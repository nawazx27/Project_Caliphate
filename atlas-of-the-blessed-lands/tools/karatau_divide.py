"""Trace the Karatau's divide (Syr Darya side against the Chu-Talas side) on the elevation grid (tools/data/dem_*.npz
from tools/dem_fetch.py). The grid is cut to a box round the range and flooded from seeds on each side, in the same way
as tools/crest_basin.py; the box's own edges take the side of the range's axis they lie on, so in the flat sands far
from the range the line between the floods means nothing (only its stretch on the ridge is used). My method.
Usage: python3 tools/karatau_divide.py dem.npz divide.json syr_side.geojson"""
import sys, math, heapq, json, numpy as np
from shapely.geometry import box as sbox
from shapely.ops import unary_union
d = np.load(sys.argv[1]); f = 2
h = d['h'].astype(np.float32); Z = int(d['z']); X0 = int(d['x0']); Y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z
def gpx(lon, lat):
    fx = ((lon + 180) / 360 * n - X0) * TS
    fy = ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - Y0) * TS
    return fx, fy
W_, S_, E_, N_ = 66.5, 41.6, 71.8, 45.4
x0, y0 = map(int, gpx(W_, N_)); x1, y1 = map(int, gpx(E_, S_))
sub = h[y0:y1, x0:x1]; H, W = sub.shape[0] // f, sub.shape[1] // f
g = sub[:H * f, :W * f].reshape(H, f, W, f).max(axis=(1, 3)); g[g < -500] = 0
def to_ll(r, c):
    x = ((c * f + x0) / TS + X0) / n; y = ((r * f + y0) / TS + Y0) / n
    return x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
def to_rc(lon, lat):
    fx, fy = gpx(lon, lat); return int((fy - y0) / f), int((fx - x0) / f)
A, B = (67.3, 44.6), (71.2, 42.3)   # the range's axis, north-west end to south-east end (approximate)
side = lambda lon, lat: (B[0] - A[0]) * (lat - A[1]) - (B[1] - A[1]) * (lon - A[0])   # > 0: north-east (Chu-Talas) side
lab = np.zeros((H, W), np.int8); heap = []
def seed(r, c, l):
    if 0 <= r < H and 0 <= c < W and not lab[r, c]: lab[r, c] = l; heapq.heappush(heap, (float(g[r, c]), r, c))
for lo, la in [(68.25, 43.3), (69.6, 42.3), (68.8, 42.43), (68.6, 43.0)]: seed(*to_rc(lo, la), 1)   # Turkistan, Shymkent, Arys, Otrar side
for lo, la in [(68.37, 44.15), (69.17, 43.76), (69.75, 43.57), (71.37, 42.9), (70.3, 43.6)]: seed(*to_rc(lo, la), 2)   # Sozak, Sholakkorgan, Zhanatas, Taraz
for c in range(W):
    for r in (0, H - 1): seed(r, c, 2 if side(*to_ll(r, c)) > 0 else 1)
for r in range(H):
    for c in (0, W - 1): seed(r, c, 2 if side(*to_ll(r, c)) > 0 else 1)
while heap:
    e, r, c = heapq.heappop(heap); l = lab[r, c]
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < H and 0 <= cc < W and not lab[rr, cc]:
            lab[rr, cc] = l; heapq.heappush(heap, (max(e, float(g[rr, cc])), rr, cc))
m1 = lab == 1
edge = np.zeros_like(m1)
for ax, s in ((0, 1), (0, -1), (1, 1), (1, -1)): edge |= m1 & (np.roll(lab, s, ax) == 2)
edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = False
pts = [[round(v, 5) for v in to_ll(r + .5, c + .5)] + [float(g[r, c])] for r, c in zip(*np.nonzero(edge))]
json.dump(pts, open(sys.argv[2], 'w'))
cells = []
for r in range(H):
    run = None
    for c in range(W + 1):
        if c < W and m1[r, c]:
            if run is None: run = c
        elif run is not None:
            lo0, la0 = to_ll(r, run); lo1, la1 = to_ll(r + 1, c); cells.append(sbox(lo0, la1, lo1, la0)); run = None
poly = unary_union(cells).simplify(0.002)
json.dump({'type': 'Feature', 'properties': {'side': 'Syr Darya side of the Karatau divide'}, 'geometry': poly.__geo_interface__}, open(sys.argv[3], 'w'))
print('grid', H, W, 'divide cells', len(pts))
