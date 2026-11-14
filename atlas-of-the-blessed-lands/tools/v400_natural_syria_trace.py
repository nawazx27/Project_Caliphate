"""Version 400 PREVIEW helper (Nawaz: "Build exactly like this", on the Arabic General Map of Natural Syria (the Fertile Crescent), tools/data/v400_natural_syria_map.webp).
Traces the coloured land inside the map's Natural Syria border (the land outside it and the sea are drawn in pale blue/lavender) and georeferences it with a
2nd-order polynomial fitted on 20 marked cities and landmarks. Writes tools/data/v400_natural_syria.geojson."""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.join(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(H, 'data/v400_natural_syria_map.webp'); OUT = os.path.join(H, 'data/v400_natural_syria.geojson')
CP = [((366, 655), (35.50, 33.89)), ((437, 706), (36.29, 33.51)), ((400, 870), (35.93, 31.95)), ((519, 404), (37.16, 36.20)), ((347, 314), (35.32, 37.00)), ((160, 520), (33.36, 35.17)),
      ((285, 855), (34.77, 32.07)), ((1165, 720), (44.36, 33.31)), ((1003, 390), (43.13, 36.34)), ((1485, 1005), (47.81, 30.51)), ((1517, 1133), (47.98, 29.37)), ((1785, 1155), (50.84, 28.97)), ((79, 1079), (32.55, 29.97)), ((212, 1308), (34.25, 27.73)), ((240, 1245), (34.51, 28.49)), ((195, 1232), (33.95, 28.56)), ((1552, 1062), (48.49, 29.98)), ((1732, 1127), (50.32, 29.25)),
      ((303, 1132), (35.00, 29.53)), ((68, 935), (32.30, 31.26))]
P = np.array([p for p, _ in CP], float); L = np.array([l for _, l in CP], float)
def T(x, y): x = np.asarray(x, float); y = np.asarray(y, float); return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1)
cx, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 1], rcond=None)
res = np.hypot((T(P[:, 0], P[:, 1]) @ cx - L[:, 0]) * 92, (T(P[:, 0], P[:, 1]) @ cy - L[:, 1]) * 111)
print('control-point error km: mean', round(res.mean(), 1), 'max', round(res.max(), 1))
a = np.array(Image.open(IMG).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
land = (b < np.maximum(r, g) - 12) | ((g > r + 15) & (b < g + 8)) | ((r + g + b) < 200)   # warm land colours, the green-teal lowlands, and dark lines; the pale lavender sea and outside land are left out
land[25:330, 1245:] = False; land[330:765, 1490:] = False   # the title/text box and the legend box
land[:, 1860:] = False; land[1330:, :] = False; land[:, :30] = False; land[:30, :] = False   # the map frame
land = ndi.binary_opening(ndi.binary_closing(land, iterations=3), iterations=4)
lab, n = ndi.label(land); sz = ndi.sum(land, lab, range(1, n + 1))
keep = [i + 1 for i in range(n) if sz[i] > 5000]
print('pieces kept', len(keep), sorted(int(sz[i - 1]) for i in keep))
polys = []
for k in keep:
    m = ndi.binary_fill_holes(lab == k)
    c = max(measure.find_contours(np.pad(m, 1).astype(float), 0.5), key=len) - 1
    xy = np.array([(x, y) for y, x in c]); lon = T(xy[:, 0], xy[:, 1]) @ cx; lat = T(xy[:, 0], xy[:, 1]) @ cy
    polys.append(Polygon(np.stack([lon, lat], -1)).buffer(0).simplify(0.01))
U = unary_union(polys); print('bounds', [round(v, 2) for v in U.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Natural Syria as drawn on the Arabic general map'}, 'geometry': mapping(U)}, open(OUT, 'w'))
