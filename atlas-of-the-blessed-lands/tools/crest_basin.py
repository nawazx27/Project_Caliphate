"""Trace a valley's ring of crests on the elevation grid (tools/data/dem_*.npz from tools/dem_fetch.py) by flooding:
the valley is flooded from a seed on its floor and the outside from seeds round it (the grid's edge and named points);
each cell takes the label of whichever flood reaches it first by the lowest pass, so the two meet on the watershed (my method).
Usage: python3 tools/crest_basin.py dem.npz factor in_lon,in_lat out_lon,out_lat[;...] out.geojson"""
import sys, math, heapq, json, numpy as np
d = np.load(sys.argv[1]); f = int(sys.argv[2])
h = d['h'].astype(np.float32); Z = int(d['z']); X0 = int(d['x0']); Y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z
H, W = h.shape[0] // f, h.shape[1] // f
g = h[:H * f, :W * f].reshape(H, f, W, f).max(axis=(1, 3))    # keep the crests: the highest point in each block
g[g < -500] = 0
def to_px(lon, lat):
    fx = ((lon + 180) / 360 * n - X0) * TS / f
    fy = ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - Y0) * TS / f
    return int(fy), int(fx)
def to_ll(r, c):
    x = (c * f / TS + X0) / n; y = (r * f / TS + Y0) / n
    return x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))
inside = [tuple(map(float, p.split(','))) for p in sys.argv[3].split(';')]
outside = [tuple(map(float, p.split(','))) for p in sys.argv[4].split(';')]
lab = np.zeros((H, W), np.int8); heap = []
def seed(r, c, l):
    if 0 <= r < H and 0 <= c < W and not lab[r, c]: lab[r, c] = l; heapq.heappush(heap, (float(g[r, c]), r, c))
for lo, la in inside: seed(*to_px(lo, la), 1)
for lo, la in outside: seed(*to_px(lo, la), 2)
for c in range(W): seed(0, c, 2); seed(H - 1, c, 2)
for r in range(H): seed(r, 0, 2); seed(r, W - 1, 2)
while heap:
    e, r, c = heapq.heappop(heap); l = lab[r, c]
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < H and 0 <= cc < W and not lab[rr, cc]:
            lab[rr, cc] = l; heapq.heappush(heap, (max(e, float(g[rr, cc])), rr, cc))
m = (lab == 1)
# outline of the valley region: trace its boundary (Moore neighbour) on the cell grid
ys, xs = np.nonzero(m); i = np.argmin(ys * W + xs); start = (ys[i], xs[i])
nb = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
pts = [start]; cur = start; dd = 6
while True:
    for k in range(8):
        q = (dd + k) % 8; r, c = cur[0] + nb[q][0], cur[1] + nb[q][1]
        if 0 <= r < H and 0 <= c < W and m[r, c]: cur = (r, c); dd = (q + 5) % 8; break
    if cur == start: break
    pts.append(cur)
ring = [list(map(lambda v: round(v, 4), to_ll(r + 0.5, c + 0.5))) for r, c in pts]; ring.append(ring[0])
json.dump({'type': 'Feature', 'properties': {'cells': int(m.sum()), 'max_crest_m': float(g[m].max())}, 'geometry': {'type': 'Polygon', 'coordinates': [ring]}}, open(sys.argv[5], 'w'))
print('valley cells', int(m.sum()), 'ring points', len(ring), 'lon', min(p[0] for p in ring), max(p[0] for p in ring), 'lat', min(p[1] for p in ring), max(p[1] for p in ring))
