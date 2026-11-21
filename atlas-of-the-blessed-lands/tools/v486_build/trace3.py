"""Third trace of his Whole Azerbaijan map (Nawaz, on spurs in the second trace: "My image doesn't contain these stupid lines"): the region is now the area
ENCLOSED BY THE RED LINE (and the Caspian coast where the line stops at the sea), not the grey shading, so the black borders and the Borchaly label's arrow
inside it can no longer leak into the edge. The edge is put on the red line's centre, then smoothed (Chaikin, 3 passes) so the pixel staircase goes.
Placement: the 2nd-order polynomial fit of trace2.py (waz_M_whole_2.npy). Usage: python3 trace3.py <dir> <out.geojson>"""
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
red = (im[..., 0] > 100) & (im[..., 0] < 210) & (im[..., 1] < 80) & (im[..., 2] < 80) & (im[..., 0] - im[..., 1] > 60)
blue = (im[..., 2] > 150) & (im[..., 0] < 140) & (im[..., 1] > 120)              # coastlines and lake shores (the blue outline, not the pale sea fill)
sea = (abs(im[..., 0] - 200) < 15) & (abs(im[..., 1] - 235) < 15) & (im[..., 2] > 240)
redc = binary_closing(red, iterations=2)
wall = binary_closing(redc | blue | sea, iterations=6)          # small gaps where the red line meets the coast closed
lab, n = label(~wall); k = lab[1000, 900]; reg = lab == k                         # the open area inside the red line (and the Caspian coast)
reg = binary_fill_holes(reg | (redc & binary_dilation(reg, iterations=12)))        # with the red line itself and the lakes inside
dout = distance_transform_edt(reg); runs = []
for arr in (red, red.T):
    for row in arr[::7]:
        d = np.diff(np.r_[0, row.astype(int), 0]); st = np.where(d == 1)[0]; en = np.where(d == -1)[0]; runs += list(en - st)
half = int(round(float(np.median([r for r in runs if r < 20])) / 2))
reg = reg & ~(red & (dout <= half))
lab, n = label(reg); sz = np.bincount(lab.ravel()); sz[0] = 0; reg = binary_fill_holes(lab == sz.argmax())
print('region px', int(reg.sum()), '| red line half width', half)
m = lambda la: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(la) / 2)))
im_ = lambda y: np.degrees(2 * np.arctan(np.exp(np.radians(y))) - np.pi / 2)
Mx = np.load(S + '/waz_M_whole_2.npy')
f2 = lambda x, y: np.c_[x, y, np.ones(len(x)), x * x, x * y, y * y]
gx, gy = np.meshgrid(np.linspace(37, 56, 120), np.linspace(m(30), m(45), 120)); gx, gy = gx.ravel(), gy.ravel()
pp = f2(gx, gy) @ Mx; u, v = pp[:, 0], pp[:, 1]
f3 = lambda u, v: np.c_[u, v, np.ones(len(u)), u * u, u * v, v * v, u ** 3, u * u * v, u * v * v, v ** 3]
Inv = np.linalg.lstsq(f3(u / 1000, v / 1000), np.c_[gx, gy], rcond=None)[0]
def chaikin(a, k=3):
    for _ in range(k):
        b = np.r_[a, a[:1]]; q = 0.75 * b[:-1] + 0.25 * b[1:]; r = 0.25 * b[:-1] + 0.75 * b[1:]; a = np.empty((2 * len(q), 2)); a[0::2] = q; a[1::2] = r
    return a
def px2ll(ring):
    a = chaikin(np.array(ring, float)[:-1]); q = f3(a[:, 0] / 1000, a[:, 1] / 1000) @ Inv; return list(zip(q[:, 0], im_(q[:, 1])))
polys = [Polygon(px2ll(g['coordinates'][0])) for g, val in shapes(reg.astype(np.uint8), mask=reg, transform=Affine.identity())]
P = unary_union(polys).buffer(0); P = unary_union([Polygon(q.exterior) for q in getattr(P, 'geoms', [P]) if q.area > 0.01]).simplify(0.002)
print('pieces', len(getattr(P, 'geoms', [P])), '| area km2', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(P)[0]) / 1e6), [round(b, 2) for b in P.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Whole Azerbaijan, traced from his map IMG_5482: the area enclosed by the red line (3rd pass, smoothed)'}, 'geometry': mapping(P)}, open(OUT, 'w'))
d = Image.open(S + '/waz.png').convert('RGB'); dr = ImageDraw.Draw(d)
for q in getattr(P, 'geoms', [P]):
    c = np.array(q.exterior.coords); X = f2(c[:, 0], m(c[:, 1])) @ Mx; dr.line(list(map(tuple, X)), fill=(0, 170, 0), width=2)
d.save(S + '/waz_chk3.png')
