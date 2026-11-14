"""Version 413 helper (Nawaz: "Use this", a map of ancient Egypt's land (olive) from the Delta to Napata, tools/data/v413_egypt_map.jpg).
The map is stylised (its Red Sea and Sinai sit west of their true places), so it is georeferenced on the towns it marks along the Nile
(Memphis, Heracleopolis, Abydos, Thebes (the star), Kom Ombo, Napata) and on the Gulf of Suez, Ras Muhammad and the Sinai's NE corner, with an affine
fit (Mercator latitude). The olive area is traced and written to tools/data/v413_egypt.geojson."""
import numpy as np, json, math, os
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, mapping
H = os.path.dirname(os.path.abspath(__file__))
M = lambda y: math.degrees(math.log(math.tan(math.pi / 4 + math.radians(y) / 2)))
IM = lambda m: math.degrees(2 * math.atan(math.exp(math.radians(m))) - math.pi / 2)
CP = [((217.5, 165), (31.25, 29.85)), ((210, 181), (30.93, 29.08)), ((225, 238.5), (31.92, 26.18)), ((236.5, 249), (32.64, 25.70)), ((242, 278), (32.95, 24.45)),
      ((220, 390), (31.83, 18.53)), ((244, 166), (32.55, 29.97)), ((273, 205), (34.25, 27.73)), ((280, 145), (34.3, 31.3))]
P = np.array([p for p, _ in CP], float); Mx = np.c_[np.ones(len(P)), P]
ax, *_ = np.linalg.lstsq(Mx, np.array([l[0] for _, l in CP]), rcond=None); ay, *_ = np.linalg.lstsq(Mx, np.array([M(l[1]) for _, l in CP]), rcond=None)
f = lambda x, y: (ax[0] + ax[1] * x + ax[2] * y, IM(ay[0] + ay[1] * x + ay[2] * y))
err = [math.hypot((f(*p)[0] - l[0]) * 100, (f(*p)[1] - l[1]) * 111) for p, l in CP]
print('fit km', [round(e) for e in err], 'mean', round(sum(err) / len(err), 1))
a = np.array(Image.open(os.path.join(H, 'data/v413_egypt_map.jpg')).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (r > 80) & (r < 170) & (g > 70) & (g < 150) & (b < 80) & (r - b > 50)
m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=4)); lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = ndi.binary_fill_holes(lab == 1 + int(np.argmax(sz)))
c = max(measure.find_contours(np.pad(m, 1).astype(float), 0.5), key=len) - 1
poly = Polygon([f(x, y) for y, x in c]).buffer(0).simplify(0.01)
print('bounds', [round(v, 2) for v in poly.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Egypt, from his map'}, 'geometry': mapping(poly)}, open(os.path.join(H, 'data/v413_egypt.geojson'), 'w'))
