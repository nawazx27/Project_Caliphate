"""Version 420 helper (Nawaz, on the Version 419 preview: "make the edges around it a bit rough.. like a real map border... it's too smooth").
Takes tools/data/v419_egyptian_empire.geojson, densifies its outline (every ~2 km) and moves each point sideways by a fixed-seed, multi-scale noise
(wiggles of ~3-25 km, at most ~15 km off the traced line), like a hand-surveyed desert border. On the sea the line is cut back to the coast anyway.
Writes tools/data/v420_egyptian_empire_rough.geojson."""
import json, os, numpy as np
from shapely.geometry import shape, Polygon, mapping
H = os.path.dirname(os.path.abspath(__file__))
g = shape(json.load(open(os.path.join(H, 'data/v419_egyptian_empire.geojson')))['geometry'])
g = max(getattr(g, 'geoms', [g]), key=lambda q: q.area)
ring = g.exterior; L = ring.length; n = int(L / 0.02)
pts = np.array([ring.interpolate(L * i / n).coords[0] for i in range(n)])
rng = np.random.default_rng(420)
def noise(scale_pts, amp):
    k = max(2, n // scale_pts); v = rng.normal(0, 1, k + 3)
    x = np.linspace(0, k, n, endpoint=False); i = x.astype(int); f = x - i
    f = f * f * (3 - 2 * f)
    return amp * (v[i] * (1 - f) + v[i + 1] * f)
d = noise(60, 0.07) + noise(20, 0.045) + noise(7, 0.025) + noise(3, 0.012)
d = np.clip(d, -0.14, 0.14)
t = np.roll(pts, -1, 0) - np.roll(pts, 1, 0); nrm = np.stack([-t[:, 1], t[:, 0]], 1); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
out = Polygon(pts + nrm * d[:, None]).buffer(0)
out = max(getattr(out, 'geoms', [out]), key=lambda q: q.area)
print('points', n, 'area ratio', round(out.area / g.area, 3))
json.dump({'type': 'Feature', 'properties': {'n': 'Egyptian Empire border, roughened'}, 'geometry': mapping(out)}, open(os.path.join(H, 'data/v420_egyptian_empire_rough.geojson'), 'w'))
