"""Version 486 trace, second pass (Nawaz: "Trace the outline more accurately for v2"). The map is placed by a 2nd-order polynomial fit of its own drawn
borders and coasts to the atlas's (lon, Mercator y) -> pixel: median error 1.5 px (~1.5 km), against 4.7 px for the first, affine fit. The shaded area
is taken to the CENTRE of the red line (the first trace stopped at its outer edge). Usage: python3 trace2.py <dir with waz.png, waz_M_whole_2.npy> <out.geojson>"""
import json, sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, binary_closing, binary_dilation, label, distance_transform_edt
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
S, OUT = sys.argv[1], sys.argv[2]
im = np.array(Image.open(S + '/waz.png').convert('RGB')).astype(int); H, W = im.shape[:2]
gray = (abs(im[..., 0] - 227) < 7) & (abs(im[..., 1] - 232) < 7) & (abs(im[..., 2] - 232) < 7)
red = (im[..., 0] > 100) & (im[..., 0] < 210) & (im[..., 1] < 80) & (im[..., 2] < 80) & (im[..., 0] - im[..., 1] > 60)
blk = im.sum(-1) < 330
R1 = gray | red | (blk & binary_dilation(gray, iterations=6))          # the shaded area with the black lines and lettering inside it (as the first trace)
R1 = binary_fill_holes(binary_closing(R1, iterations=3))
lab, n = label(R1); sz = np.bincount(lab.ravel()); sz[0] = 0; R1 = lab == sz.argmax()
runs = []
for arr in (red, red.T):
    for row in arr[::7]:
        d = np.diff(np.r_[0, row.astype(int), 0]); st = np.where(d == 1)[0]; en = np.where(d == -1)[0]; runs += list(en - st)
w = float(np.median([r for r in runs if r < 20])); half = max(1, int(round(w / 2)))
dout = distance_transform_edt(R1)                                   # distance from outside the area
reg = R1 & ~(red & (dout <= half))                                  # the outer half of the red line taken off: the edge is the line's centre
lab, n = label(reg); sz = np.bincount(lab.ravel()); sz[0] = 0; reg = binary_fill_holes(lab == sz.argmax())
print('red line width ~', round(w, 1), 'px; edge put', half, 'px in from its outer side')
m = lambda la: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(la) / 2)))
im_ = lambda y: np.degrees(2 * np.arctan(np.exp(np.radians(y))) - np.pi / 2)
Mx = np.load(S + '/waz_M_whole_2.npy')
f2 = lambda x, y: np.c_[x, y, np.ones(len(x)), x * x, x * y, y * y]
# inverse: fit pixel -> (lon, mercY) by a cubic on a dense grid
gx, gy = np.meshgrid(np.linspace(37, 56, 120), np.linspace(m(30), m(45), 120)); gx, gy = gx.ravel(), gy.ravel()
pp = f2(gx, gy) @ Mx; u, v = pp[:, 0], pp[:, 1]
f3 = lambda u, v: np.c_[u, v, np.ones(len(u)), u * u, u * v, v * v, u ** 3, u * u * v, u * v * v, v ** 3]
Inv = np.linalg.lstsq(f3(u / 1000, v / 1000), np.c_[gx, gy], rcond=None)[0]
back = f3(u / 1000, v / 1000) @ Inv; print('inverse error (deg)', round(float(np.abs(back - np.c_[gx, gy]).max()), 5))
def px2ll(ring):
    a = np.array(ring, float); q = f3(a[:, 0] / 1000, a[:, 1] / 1000) @ Inv; return list(zip(q[:, 0], im_(q[:, 1])))
polys = [Polygon(px2ll(g['coordinates'][0]), [px2ll(r) for r in g['coordinates'][1:]]) for g, val in shapes(reg.astype(np.uint8), mask=reg, transform=Affine.identity())]
P = unary_union(polys).buffer(0); P = unary_union([Polygon(q.exterior) for q in getattr(P, 'geoms', [P])]).simplify(0.004)
print('pieces', len(getattr(P, 'geoms', [P])), '| area km2', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(P)[0]) / 1e6), [round(b, 2) for b in P.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Whole Azerbaijan, traced from his map IMG_5482 to the centre of the red line (2nd pass, polynomial fit)'}, 'geometry': mapping(P)}, open(OUT, 'w'))
d = Image.open(S + '/waz.png').convert('RGB'); dr = ImageDraw.Draw(d)
for q in getattr(P, 'geoms', [P]):
    c = np.array(q.exterior.coords); X = f2(c[:, 0], m(c[:, 1])) @ Mx; dr.line(list(map(tuple, X)), fill=(0, 170, 0), width=2)
d.save(S + '/waz_chk2.png')
