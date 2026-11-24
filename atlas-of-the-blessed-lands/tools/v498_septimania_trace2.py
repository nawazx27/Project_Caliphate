"""Second Septimania trace (Nawaz: "Trace this map exactly and compare it to your previous trace", a map of the Iberian Peninsula and Gaul in 600 (Catalan
'Any 600', Visigothic lands in yellow, Septimania labelled, white borders). This map has real coastlines and relief, so it is placed by fitting its own
coastline to the atlas's (2nd-order polynomial, lon/Mercator-y -> pixel; median error ~4 px, ~3.5 km at ~120 px per degree). Septimania = the yellow area
round its label, bounded by the white borders (Aquitaine, Hispania) and the sea; its edge put on the centre of the white border lines.
Usage: python3 tools/v498_septimania_trace2.py <map.png> <fit M.npy> <out.geojson>"""
import sys, json, numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, binary_closing, binary_dilation, label
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
im = np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
wall = binary_closing(binary_dilation((r > 195) & (g > 195) & (b > 185), iterations=2), iterations=6)   # the white borders and coastline as walls, small gaps sealed
sea = (abs(r - 137) < 16) & (abs(g - 177) < 16) & (abs(b - 202) < 16)
lab, n = label(~wall & ~sea); k = lab[int(960 * W / 1451), int(1250 * W / 1451)]   # the area round Septimania's label (display 1250,960)
R = binary_fill_holes(lab == k)
R = binary_fill_holes(R | (binary_dilation(R, iterations=4) & wall & ~sea))      # to the centre of the white lines
print('Septimania px', int(R.sum()))
m = lambda la: np.degrees(np.log(np.tan(np.pi / 4 + np.radians(la) / 2)))
im_ = lambda y: np.degrees(2 * np.arctan(np.exp(np.radians(y))) - np.pi / 2)
Mx = np.load(sys.argv[2]); f2 = lambda x, y: np.c_[x, y, np.ones(len(x)), x * x, x * y, y * y]
gx, gy = np.meshgrid(np.linspace(-11, 7, 100), np.linspace(m(35), m(52), 100)); gx, gy = gx.ravel(), gy.ravel()
pp = f2(gx, gy) @ Mx; u, v = pp[:, 0] / 1000, pp[:, 1] / 1000
f3 = lambda u, v: np.c_[u, v, np.ones(len(u)), u * u, u * v, v * v, u ** 3, u * u * v, u * v * v, v ** 3]
Inv = np.linalg.lstsq(f3(u, v), np.c_[gx, gy], rcond=None)[0]
polys = []
for gg, val in shapes(R.astype(np.uint8), mask=R, transform=Affine.identity()):
    c = np.array(gg['coordinates'][0], float); q = f3(c[:, 0] / 1000, c[:, 1] / 1000) @ Inv; polys.append(Polygon(np.c_[q[:, 0], im_(q[:, 1])]))
S = unary_union(polys).buffer(0).simplify(0.003)
print('traced Septimania', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(S)[0]) / 1e6), 'km2', [round(x, 2) for x in S.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Septimania traced from the Any 600 map (IMG_5626)'}, 'geometry': mapping(S)}, open(sys.argv[3], 'w'))
