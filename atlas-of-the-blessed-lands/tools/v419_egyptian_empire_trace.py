"""Version 419 helper (Nawaz, on my red sketch of the Egyptian Empire map's border: "Preview this"). The map (tools/data/v414_egyptian_empire_map.webp) is placed on
the real coastlines (Mercator fit of its seas to Natural Earth land, IoU 0.93; its towns then land within a few km), so the shape keeps the map's own look.
x = (lon - p0) * p1, y = (p2 - mercator(lat)) * p3 with p = [18.3359375, 55.21875, 47.25, 55.4375]. Writes tools/data/v419_egyptian_empire.geojson (both greens)."""
import numpy as np, json, math, os
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, mapping
H = os.path.dirname(os.path.abspath(__file__)); p = [18.3359375, 55.21875, 47.25, 55.4375]
IM = lambda m: math.degrees(2 * math.atan(math.exp(math.radians(m))) - math.pi / 2)
a = np.array(Image.open(os.path.join(H, 'data/v414_egyptian_empire_map.webp')).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (g > r + 4) & (g > b + 30); m[:160, :700] = False
m = ndi.binary_fill_holes(ndi.binary_opening(ndi.binary_closing(m, iterations=3), iterations=2)); lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = ndi.binary_fill_holes(lab == 1 + int(np.argmax(sz)))
c = max(measure.find_contours(np.pad(m, 1).astype(float), 0.5), key=len) - 1
poly = Polygon([(x / p[1] + p[0], IM(p[2] - y / p[3])) for y, x in c]).buffer(0).simplify(0.01)
print('bounds', [round(v, 2) for v in poly.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Egyptian Empire 15th c. BC (Wikipedia map), coastline fit'}, 'geometry': mapping(poly)}, open(os.path.join(H, 'data/v419_egyptian_empire.geojson'), 'w'))
