"""Version 307: trace the empire (dark red + light red) of reference/v306_ottoman_1683_map.jpg, with the sea next to its coasts (within 8 px),
into lon/lat using the control-point fit in tf.json (made by fit.py: 11 cities and coast points, quadratic, residuals <= 8 px).
Writes tools/data/v307_ottoman_map_shape.geojson. The seas are kept so that the drawing's rough coasts do not cut real coast land;
the result is later cut to real land, so only the drawing's land border (its outer line) matters."""
import json, os, numpy as np, shapely
from shapely.geometry import shape, mapping
from scipy import ndimage
from PIL import Image
from rasterio import features
from rasterio.transform import Affine
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
im = np.array(Image.open(os.path.join(P, 'reference/v306_ottoman_1683_map.jpg')).convert('RGB')).astype(int); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
red = (r > 150) & (r - g > 45) & (r - b > 45)
water = (b > 150) & (b > r + 30)
near = ndimage.distance_transform_edt(~red) <= 8      # sea only next to the empire's coasts (not the far Caspian shores)
m = ndimage.binary_closing(red | (water & near), iterations=2)
m = ndimage.binary_fill_holes(m)
lab, n = ndimage.label(m); keep = np.bincount(lab[red & m].ravel()); keep[0] = 0
m = lab == keep.argmax()                       # the one region holding the empire
tf = json.load(open(os.path.join(P, 'tools/v307_build/tf.json'))); k = tf['k']
step = 0.02; lons = np.arange(12, 54, step); lats = np.arange(34, 53, step)
LO, LA = np.meshgrid(lons, lats); lo, la = LO.ravel(), LA.ravel()
F = np.c_[np.ones_like(lo), lo, la, lo * lo, lo * la, la * la][:, :k]
x = np.round(F @ np.array(tf['cx'])).astype(int); y = np.round(F @ np.array(tf['cy'])).astype(int)
ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
grid = np.zeros(lo.size, bool); grid[ok] = m[y[ok], x[ok]]; grid = grid.reshape(LO.shape)
T = Affine(step, 0, lons[0] - step / 2, 0, step, lats[0] - step / 2)
O = shapely.union_all([shape(s) for s, v in features.shapes(grid.astype(np.uint8), transform=T) if v == 1]).buffer(0.02).buffer(-0.02).simplify(0.04)
def chaikin(c, n=4):                           # smooth the pixel steps into a drawn-looking line
    c = np.asarray(c)[:-1]
    for _ in range(n):
        q = np.roll(c, -1, 0); c = np.vstack([np.c_[0.75 * c + 0.25 * q], np.c_[0.25 * c + 0.75 * q]]).reshape(2, -1, 2).transpose(1, 0, 2).reshape(-1, 2)
    return np.vstack([c, c[:1]])
from shapely.geometry import Polygon
O = Polygon(chaikin(O.exterior.coords), [chaikin(h.coords) for h in O.interiors]).buffer(0)
json.dump({'type': 'Feature', 'properties': {'source': 'reference/v306_ottoman_1683_map.jpg', 'note': 'empire + enclosed seas, before cutting to land'}, 'geometry': mapping(O)}, open(os.path.join(P, 'tools/data/v307_ottoman_map_shape.geojson'), 'w'))
print('traced', O.geom_type, round(O.area, 1), 'sq deg')
