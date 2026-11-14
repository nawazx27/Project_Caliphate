"""Version 401 PREVIEW helper (Nawaz: the Wikipedia map of Bilad al-Sham's provinces (ajnad, with al-'Awasim and al-Thughur al-Shamiyya), then the Wikipedia Hejaz map:
"Preview this map plus the Hejaz").
1. Bilad al-Sham: the dashed outer border read point by point off tools/data/v401_bilad_al_sham_map.webp (pixel vertices below; the sea side is closed offshore,
   clear of Cyprus), georeferenced with a 2nd-order polynomial fitted on 26 marked towns (Hama left out: the map draws it well east of its true place) of the map.
2. The Hejaz: the red and pink (Tihamah) area of tools/data/v401_hejaz_map.webp, georeferenced by fitting the map's coast to Natural Earth
   (equirectangular, x=(lon-33.0859)*70.0234, y=(39.1484-lat)*74.2656, IoU 0.967).
Writes tools/data/v401_bilad_al_sham.geojson and tools/data/v401_hejaz.geojson."""
import numpy as np, json, os
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__))
# 1. Bilad al-Sham
CP = [((685, 295), (34.89, 36.92)), ((788, 275), (35.32, 37.00)), ((864, 288), (35.64, 36.95)), ((1162, 143), (36.94, 37.58)), ((997, 476), (36.16, 36.20)), ((1253, 471), (37.16, 36.20)),
      ((1449, 390), (37.95, 36.53)), ((1592, 147), (38.53, 37.53)), ((1580, 283), (38.42, 36.98)), ((1478, 506), (38.08, 35.98)), ((1710, 528), (39.01, 35.95)), ((1650, 621), (38.75, 35.63)),
      ((1528, 885), (38.27, 34.56)), ((1330, 960), (37.24, 34.23)), ((915, 643), (35.78, 35.52)), ((1140, 843), (36.72, 34.73)), ((922, 918), (35.84, 34.44)),
      ((838, 1056), (35.50, 33.89)), ((843, 1327), (35.53, 32.79)), ((943, 1545), (35.93, 31.95)), ((763, 1581), (35.23, 31.78)), ((571, 1647), (34.47, 31.50)), ((709, 2143), (35.00, 29.53)),
      ((944, 1981), (35.73, 30.19)), ((1083, 1398), (36.48, 32.52)), ((647, 1514), (34.75, 32.05))]
BORDER = [(480, 440), (450, 425), (370, 415), (365, 395), (410, 350), (510, 280), (600, 235), (710, 180), (810, 145), (950, 100), (1100, 60), (1230, 45), (1370, 28),   # al-Thughur, along the Taurus
          (1400, 100), (1420, 160), (1435, 220), (1450, 260), (1470, 300), (1485, 355), (1535, 390), (1515, 420), (1510, 460), (1490, 485), (1495, 510),            # against al-Jazira
          (1550, 540), (1630, 562), (1705, 540), (1725, 550), (1740, 585), (1820, 618),                                                                            # the Euphrates by al-Raqqa, al-Rusafa
          (1810, 680), (1780, 780), (1730, 890), (1680, 950), (1620, 1050), (1570, 1130), (1510, 1210), (1473, 1250), (1393, 1477), (1333, 1650), (1253, 1797),   # the desert edge
          (1160, 1917), (1027, 2037), (880, 2103), (773, 2143), (687, 2154),                                                                                         # to Ayla
          (620, 2077), (547, 1917), (480, 1783), (460, 1723),                                                                                                        # Sinai side, to the coast east of al-'Arish
          (420, 1700), (540, 1600), (680, 1350), (780, 1100), (860, 900), (870, 700), (900, 560), (1000, 520), (900, 470), (700, 420), (480, 450)]                  # offshore, back to the start
P = np.array([p for p, _ in CP], float); L = np.array([l for _, l in CP], float)
def T(x, y): x = np.asarray(x, float); y = np.asarray(y, float); return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1)
cx, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 1], rcond=None)
res = np.hypot((T(P[:, 0], P[:, 1]) @ cx - L[:, 0]) * 90, (T(P[:, 0], P[:, 1]) @ cy - L[:, 1]) * 111)
print('Bilad al-Sham fit error km: mean', round(res.mean(), 1), 'max', round(res.max(), 1))
B = np.array(BORDER, float); SH = Polygon(np.stack([T(B[:, 0], B[:, 1]) @ cx, T(B[:, 0], B[:, 1]) @ cy], -1)).buffer(0)
print('Bilad al-Sham bounds', [round(v, 2) for v in SH.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Bilad al-Sham (Wikipedia ajnad map)'}, 'geometry': mapping(SH)}, open(os.path.join(H, 'data/v401_bilad_al_sham.geojson'), 'w'))
# 2. Hejaz
a = np.array(Image.open(os.path.join(H, 'data/v401_hejaz_map.webp')).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (r > 170) & (r - g > 45) & (r - b > 40)
m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=3)); lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1)); m = lab == 1 + int(np.argmax(sz))
c = max(measure.find_contours(np.pad(m, 1).astype(float), 0.5), key=len) - 1
HJ = Polygon([(x / 70.0234 + 33.0859, 39.1484 - y / 74.2656) for y, x in c]).buffer(0).simplify(0.01)
print('Hejaz px', int(m.sum()), 'bounds', [round(v, 2) for v in HJ.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Hejaz (Wikipedia map, red and Tihamah pink)'}, 'geometry': mapping(HJ)}, open(os.path.join(H, 'data/v401_hejaz.geojson'), 'w'))
