"""Version 310: trace the empire (dark red + light red) of reference/v310_ottoman_1683_full_map.jpg with the sea within 8 px of it,
into lon/lat with tools/v310_build/tf.json; smoothed; writes tools/data/v310_ottoman_full_map_shape.geojson."""
import json, os, numpy as np, shapely
from shapely.geometry import shape, mapping, Polygon
from scipy import ndimage
from PIL import Image
from rasterio import features
from rasterio.transform import Affine
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
im = np.array(Image.open(os.path.join(P, 'reference/v310_ottoman_1683_full_map.jpg')).convert('RGB')).astype(int); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
red = (r > 140) & (r - g > 40) & (r - b > 40)
water = (b > 140) & (b > r + 20)
near = ndimage.distance_transform_edt(~red) <= 8
m = ndimage.binary_fill_holes(ndimage.binary_closing(red | (water & near), iterations=2))
lab, n = ndimage.label(m); cnt = np.bincount(lab[red & m].ravel()); cnt[0] = 0; m = lab == cnt.argmax()
tf = json.load(open(os.path.join(P, 'tools/v310_build/tf.json'))); k = tf['k']
step = 0.02; lons = np.arange(10, 36, step); lats = np.arange(34, 52, step)
LO, LA = np.meshgrid(lons, lats); lo, la = LO.ravel(), LA.ravel()
F = np.c_[np.ones_like(lo), lo, la, lo * lo, lo * la, la * la][:, :k]
x = np.round(F @ np.array(tf['cx'])).astype(int); y = np.round(F @ np.array(tf['cy'])).astype(int)
ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
grid = np.zeros(lo.size, bool); grid[ok] = m[y[ok], x[ok]]; grid = grid.reshape(LO.shape)
T = Affine(step, 0, lons[0] - step / 2, 0, step, lats[0] - step / 2)
O = shapely.union_all([shape(s) for s, v in features.shapes(grid.astype(np.uint8), transform=T) if v == 1]).buffer(0.02).buffer(-0.02).simplify(0.04)
def chaikin(c, n=4):
    c = np.asarray(c)[:-1]
    for _ in range(n):
        q = np.roll(c, -1, 0); c = np.vstack([np.c_[0.75 * c + 0.25 * q], np.c_[0.25 * c + 0.75 * q]]).reshape(2, -1, 2).transpose(1, 0, 2).reshape(-1, 2)
    return np.vstack([c, c[:1]])
O = shapely.union_all([Polygon(chaikin(p.exterior.coords), [chaikin(h.coords) for h in p.interiors]).buffer(0) for p in getattr(O, 'geoms', [O])])
json.dump({'type': 'Feature', 'properties': {'source': 'reference/v310_ottoman_1683_full_map.jpg', 'note': 'empire + sea within 8 px, before cutting to land; only its Balkans part is used'}, 'geometry': mapping(O)}, open(os.path.join(P, 'tools/data/v310_ottoman_full_map_shape.geojson'), 'w'))
print('traced', O.geom_type, round(O.area, 1))
