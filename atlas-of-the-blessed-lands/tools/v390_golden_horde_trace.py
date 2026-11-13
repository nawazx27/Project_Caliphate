"""Version 390 PREVIEW helper: trace the yellow Golden Horde shape (c.1300) from Nawaz's picture (Wikipedia 'Golden Horde' map) and georeference it.
The picture is plain equirectangular (fitted against Natural Earth land, IoU 0.967): x=(lon+18.469)*11.680, y=(72.031-lat)*11.689.
Writes tools/data/v390_golden_horde.geojson (the shape exactly as drawn, not clipped)."""
import numpy as np, json, os, sys
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, mapping
IMG = sys.argv[1]; OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/v390_golden_horde.geojson')
a = np.array(Image.open(IMG).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (r > 222) & (g > 190) & (g < 232) & (b < 140) & (r - b > 100)
m = ndi.binary_closing(m, iterations=6); m = ndi.binary_fill_holes(m); m = ndi.binary_opening(m, iterations=2)
lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == (1 + int(np.argmax(sz)))
m = ndi.binary_fill_holes(ndi.binary_dilation(m, iterations=4)); print('mask px', int(m.sum()))
c = max(measure.find_contours(np.pad(m, 1).astype(float), 0.5), key=len) - 1
ll = [(x / 11.680 - 18.469, 72.031 - y / 11.689) for y, x in c]
P = Polygon(ll).buffer(0).simplify(0.03)
print('points', len(P.exterior.coords), 'bounds', [round(v, 1) for v in P.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Golden Horde c.1300 as drawn'}, 'geometry': mapping(P)}, open(OUT, 'w'))
