"""Version 315: trace every purple and magenta shade of reference/v315_roman_rule_map_hires.jpg (Roman rule of any length), with the sea
within 6 px of it so the drawing's coasts do not cut real coast land, into lon/lat with tf.json; writes tools/data/v315_roman_map_hires_shape.geojson."""
import json, os, numpy as np, shapely
from shapely.geometry import shape, mapping
from scipy import ndimage
from PIL import Image
from rasterio import features
from rasterio.transform import Affine
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
im = np.array(Image.open(os.path.join(P, 'reference/v315_roman_rule_map_hires.jpg')).convert('RGB')).astype(int); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
pur = (r - g > 25) & (b - g > 25)
pur[H - 80:, W - 160:] = False                                   # the Grok mark
water = (b > 200) & (g > 190) & (b - r > 20)
near = ndimage.distance_transform_edt(~pur) <= 6
m = ndimage.binary_fill_holes(ndimage.binary_closing(pur | (water & near), iterations=3))
lab, n = ndimage.label(m); cnt = np.bincount(lab[pur & m].ravel()); cnt[0] = 0
m = np.isin(lab, np.nonzero(cnt > 30)[0])                       # every purple piece (islands too)
tf = json.load(open(os.path.join(P, 'tools/v315_build/tf.json')))
step = 0.02; lons = np.arange(-14, 52, step); lats = np.arange(10, 60, step)
LO, LA = np.meshgrid(lons, lats); lo, la = LO.ravel(), LA.ravel()
F = np.c_[np.ones_like(lo), lo, la, lo * lo, lo * la, la * la, lo ** 3, lo * lo * la, lo * la * la, la ** 3]
x = np.round(F @ np.array(tf['cx'])).astype(int); y = np.round(F @ np.array(tf['cy'])).astype(int)
ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
grid = np.zeros(lo.size, bool); grid[ok] = m[y[ok], x[ok]]; grid = grid.reshape(LO.shape)
T = Affine(step, 0, lons[0] - step / 2, 0, step, lats[0] - step / 2)
O = shapely.union_all([shape(s) for s, v in features.shapes(grid.astype(np.uint8), transform=T) if v == 1]).buffer(0.02).buffer(-0.02).simplify(0.03)
def chaikin(c, n=3):                           # smooth the pixel steps into a drawn line
    c = np.asarray(c)[:-1]
    if len(c) < 4: return np.vstack([c, c[:1]])
    for _ in range(n):
        q = np.roll(c, -1, 0); c = np.vstack([np.c_[0.75 * c + 0.25 * q], np.c_[0.25 * c + 0.75 * q]]).reshape(2, -1, 2).transpose(1, 0, 2).reshape(-1, 2)
    return np.vstack([c, c[:1]])
from shapely.geometry import Polygon
O = shapely.union_all([Polygon(chaikin(p.exterior.coords), [chaikin(h.coords) for h in p.interiors]).buffer(0) for p in getattr(O, 'geoms', [O])])
json.dump({'type': 'Feature', 'properties': {'source': 'reference/v315_roman_rule_map_hires.jpg', 'note': 'Roman rule (all shades) + sea within 6 px, before cutting to land'}, 'geometry': mapping(O)}, open(os.path.join(P, 'tools/data/v315_roman_map_hires_shape.geojson'), 'w'))
print('traced', O.geom_type, round(O.area, 1))
