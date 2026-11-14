"""Version 414 check (Nawaz: the Wikipedia map "The Egyptian Empire, 15th century BC" (tools/data/v414_egyptian_empire_map.webp): "Does this preview even hold this?").
Traces both greens (the empire and its core) and georeferences them with a 2nd-order fit on 21 marked towns; writes tools/data/v414_egyptian_empire.geojson
and reports how much of its land each given caliph.json's V1 (shj) holds. Usage: python3 tools/v414_egyptian_empire_check.py caliph.json [...]"""
import numpy as np, json, os, sys, subprocess
from PIL import Image
from scipy import ndimage as ndi
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon, Point, shape, mapping
from shapely.ops import unary_union
from pyproj import Geod
H = os.path.dirname(os.path.abspath(__file__)); P0 = os.path.join(H, '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
K = 1920 / 1708   # the town positions below were read on a 1708 px wide copy
CP = [((618, 800), (31.25, 29.85)), ((634, 779), (31.31, 30.13)), ((665, 720), (31.88, 30.98)), ((790, 704), (34.47, 31.50)), ((823, 620), (35.20, 33.27)), ((836, 585), (35.37, 33.56)),
      ((851, 545), (35.65, 34.12)), ((886, 600), (36.29, 33.51)), ((904, 551), (36.52, 34.56)), ((954, 404), (38.02, 36.83)), ((760, 500), (33.63, 34.92)), ((696, 1038), (32.64, 25.70)),
      ((708, 1108), (32.90, 24.09)), ((629, 1215), (31.63, 22.34)), ((642, 1430), (31.83, 18.53)),
      ((667, 998), (31.92, 26.18)), ((589, 886), (30.93, 29.08))]
P = np.array([p for p, _ in CP], float) * K; L = np.array([l for _, l in CP], float)
T = lambda x, y: np.stack([np.ones_like(x), x, y, x * x, x * y, y * y], -1)
cx, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(T(P[:, 0], P[:, 1]), L[:, 1], rcond=None)
e = np.hypot((T(P[:, 0], P[:, 1]) @ cx - L[:, 0]) * 100, (T(P[:, 0], P[:, 1]) @ cy - L[:, 1]) * 111); print('fit km mean', round(e.mean(), 1), 'max', round(e.max(), 1))
a = np.array(Image.open(os.path.join(H, 'data/v414_egyptian_empire_map.webp')).convert('RGB')).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (g > r + 4) & (g > b + 30)   # both greens (pale empire, darker core)
m[:160, :700] = False
m = ndi.binary_fill_holes(ndi.binary_opening(ndi.binary_closing(m, iterations=3), iterations=2)); lab, n = ndi.label(m); sz = ndi.sum(m, lab, range(1, n + 1))
keep = [i + 1 for i in range(n) if sz[i] > 20000]; print('pieces', sorted(int(sz[i - 1]) for i in keep))
polys = []
for k in keep:
    c = max(measure.find_contours(np.pad(ndi.binary_fill_holes(lab == k), 1).astype(float), 0.5), key=len) - 1
    xy = np.array([(x, y) for y, x in c]); polys.append(Polygon(np.stack([T(xy[:, 0], xy[:, 1]) @ cx, T(xy[:, 0], xy[:, 1]) @ cy], -1)).buffer(0).simplify(0.01))
EMP = unary_union(polys); print('bounds', [round(v, 2) for v in EMP.bounds])
json.dump({'type': 'Feature', 'properties': {'n': 'Egyptian Empire 15th c. BC (Wikipedia map)'}, 'geometry': mapping(EMP)}, open(os.path.join(H, 'data/v414_egyptian_empire.geojson'), 'w'))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P0))
LAND = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')])
IN = EMP.intersection(LAND); print('empire land', round(A(IN)), 'km2')
for f in sys.argv[1:]:
    C = json.load(open(f)); V = MultiPolygon([Polygon(r_[0], r_[1:]) for r_ in C['shj']['polys']]).buffer(0)
    out = IN.difference(V.buffer(0.005)); print(f, 'V1 holds', round(100 * (1 - A(out) / A(IN)), 1), '% ; outside', round(A(out)), 'km2')
    import shapely
    for nm, bx in [('west of 29E (Western Desert, Siwa, Dakhla, into Libya)', shapely.box(20, 10, 29, 40)), ('south of 15.5N (Sudan beyond Khartoum)', shapely.box(29, 10, 40, 15.5)), ('elsewhere', None)]:
        part = out.intersection(bx) if bx else out.difference(shapely.box(20, 10, 29, 40)).difference(shapely.box(29, 10, 40, 15.5)); print('    missing', nm, round(A(part)), 'km2')
    for n_, p_ in {'Siwa': (25.52, 29.2), 'Dakhla': (28.98, 25.49), 'Bahariya': (28.86, 28.35), 'Farafra': (27.97, 27.06), 'Khartoum': (32.53, 15.6), 'Kosti': (32.66, 13.17), 'Kufra (Libya)': (23.31, 24.2), 'Carchemish': (38.02, 36.83), 'Byblos': (35.65, 34.12)}.items():
        print('     ', n_, 'in empire', EMP.contains(Point(p_)), '| in V1', V.contains(Point(p_)))
    for q in sorted(getattr(out, 'geoms', [out]), key=lambda q: -q.area)[:0]: print('    missing', round(A(q)), 'km2 at', [round(c_, 2) for c_ in q.representative_point().coords[0]], [round(v, 1) for v in q.bounds])
