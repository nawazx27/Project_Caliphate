"""Version 498 helper (Nawaz, the Wikipedia Septimania map IMG_5624 (Septimania in red between the Franks, the Visigoths and the Rhone): "Trace this map
exactly"). The map is a sketch (an affine fit through its five town dots leaves 20-70 px, ~10-25 km, errors), so it is placed by a thin-plate warp that
puts its own landmarks exactly where they are: the dots of Bordeaux, Carcassonne, Narbonne, Beziers and Arles, and three corners of the red area
(its south-east corner on the sea at the Pyrenees, i.e. the Franco-Spanish border at Cerbere; its south-west corner on the Pyrenees, the Carlit;
its east corner where the Rhone reaches the sea at Aigues-Mortes / the Petit Rhone). The red area is taken to the centre of its black outline.
Usage: python3 tools/v498_septimania_trace.py <map.png> <out.geojson>"""
import sys, json, numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, label, binary_dilation
from scipy.interpolate import RBFInterpolator
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
m = lambda la: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(la) / 2)))
im_ = lambda y: np.degrees(2 * np.arctan(np.exp(np.radians(y))) - np.pi / 2)
im = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
blk = im.sum(-1) < 120
def dot(x, y):
    sub = blk[y - 25:y + 26, x - 25:x + 26]; ys, xs = np.where(sub); return (x - 25 + xs.mean(), y - 25 + ys.mean())
CP = [(dot(400, 355), (-0.579, 44.838)), (dot(1150, 905), (2.353, 43.213)), (dot(1487, 850), (3.215, 43.344)), (dot(1349, 960), (3.004, 43.184)),
      (dot(1802, 770), (4.631, 43.677)), ((1340, 1150), (3.17, 42.44)), ((1100, 1138), (1.95, 42.55)), ((1728, 852), (4.40, 43.46))]
P = np.array([c[0] for c in CP], float); Q = np.array([(c[1][0], m(c[1][1])) for c in CP])
warp = RBFInterpolator(P, Q, kernel='thin_plate_spline')
red = (abs(im[..., 0] - 180) < 25) & (abs(im[..., 1] - 125) < 25) & (abs(im[..., 2] - 113) < 25)
lab, n = label(binary_fill_holes(red)); sz = np.bincount(lab.ravel()); sz[0] = 0; R = lab == sz.argmax()
R = binary_fill_holes(R | (binary_dilation(R, iterations=5) & blk))
polys = []
for g, v in shapes(R.astype(np.uint8), mask=R, transform=Affine.identity()):
    c = np.array(g['coordinates'][0], float); ll = warp(c); polys.append(Polygon(np.c_[ll[:, 0], im_(ll[:, 1])]))
S = unary_union(polys).buffer(0).simplify(0.003)
print('traced Septimania', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(S)[0]) / 1e6), 'km2', [round(v, 2) for v in S.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Septimania traced from the Wikipedia map IMG_5624 (thin-plate warp through its landmarks)'}, 'geometry': mapping(S)}, open(sys.argv[2], 'w'))
