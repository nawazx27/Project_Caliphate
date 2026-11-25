"""Version 503 preview (Nawaz, a screenshot of a Sham/Hijaz diagram: "Trace this map with broader outlines exactly"; then "You didn't trace by
broader outline"). The image's city dots (25 of them) fit a plain lat/lon grid of 72 px per degree to within ~5 km (least squares below).
The outline is the image's outermost lines, read vertex by vertex at 2-3x zoom: the green dashed 'Sham, disputed edge' (north to ~37.6 N above
Halab, east past the Euphrates edge to ~43 E, down to Jabal Tayy), the solid Sham core where it is outermost (Halab to the Euphrates), and the
orange dashed 'Hijaz, uncertain' (Jabal Tayy south along ~42.4 E to ~19.1 N on the Red Sea coast); the Filastin dashed line from al-Arish to Ayla.
Its sea sides (the Levant coast, the Gulf of Aqaba and the Red Sea) are taken out to sea so the real coast is used; Cyprus stays out as drawn.
-> tools/data/v503_sham_hijaz_outer.geojson (land only)."""
import json, os, subprocess, numpy as np
from shapely.geometry import shape, Polygon, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
# image px (x, y) -> real (lon, lat) of the dots
DOTS = [(455,138,36.16,36.20),(527,138,37.16,36.20),(496,244,36.72,34.73),(465.5,332.5,36.29,33.51),(408,304.5,35.50,33.89),(386,348.5,35.20,33.27),
        (410,383,35.53,32.79),(438.5,444,35.93,31.95),(372.5,618.5,35.00,29.53),(485.5,701.5,36.57,28.38),(624,757,38.48,27.63),(854.5,764.5,41.69,27.52),
        (723,599,39.87,29.81),(681.5,894,39.29,25.70),(703,982.5,39.61,24.47),(591.5,1009.5,38.06,24.09),(673,1193,39.17,21.54),(719.5,1202,39.83,21.42),
        (1049,347,44.36,33.31),(1049,440.5,44.40,32.03),(102,581,31.24,30.04),(1214.5,966,46.72,24.69),(390,424,35.26,32.22),(363,446,34.87,31.93),(332.5,476.5,34.47,31.50)]
a = np.array(DOTS); X = np.c_[np.ones(len(a)), a[:, 0], a[:, 1]]
cl = np.linalg.lstsq(X, a[:, 2], rcond=None)[0]; ca = np.linalg.lstsq(X, a[:, 3], rcond=None)[0]
res = np.hypot((X @ cl - a[:, 2]) * 96, (X @ ca - a[:, 3]) * 111); print('dot fit: mean %.1f km, max %.1f km' % (res.mean(), res.max()))
ll = lambda x, y: (float(cl @ [1, x, y]), float(ca @ [1, x, y]))
# the outer lines, clockwise from the north-west (image px)
LINE = [(400,102),(415,92),(508,39),(625,41),(588,95),(665,160),(745,200),(799,262),(872,270),(949,477),(855,764),(910,940),(912,1230),(877,1355),(810,1367)]
RED_SEA = [(40.6,19.0),(39.8,20.0),(39.05,21.2),(38.9,21.9),(38.4,23.0),(37.85,24.0),(37.0,25.0),(36.3,26.0),(35.4,27.2),(34.8,28.0),(34.8,28.9),(34.92,29.45)]
FIL = [(371,619),(285,502)]   # Ayla -> al-Arish, the Filastin dashed line through Sinai
LEVANT_SEA = [(33.3,31.4),(34.2,32.7),(34.75,33.7),(35.6,34.8),(35.6,35.8),(35.6,36.5),(35.3,36.45),(34.6,36.62)]
ring = [ll(*p) for p in LINE] + RED_SEA + [ll(*p) for p in FIL] + LEVANT_SEA
R = Polygon(ring).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = box(*R.bounds); parts = {}
for f in geo['features']:
    if not f.get('geometry'): continue
    g = shape(f['geometry']).buffer(0)
    if not g.intersects(B): continue
    i = g.intersection(R)
    if not i.is_empty and A(i) > 0.5: parts[f['properties']['n']] = (i, A(i), 100 * A(i) / A(g))
T = unary_union([v[0] for v in parts.values()]).buffer(0)
print('traced land', round(A(T)), 'km2')
for n, (g, ar, pc) in sorted(parts.items(), key=lambda x: -x[1][1]): print(f'  {n:25s}{ar:10.0f} km2  {pc:5.1f}% of the country')
print('corners:', [tuple(round(v, 2) for v in ll(*p)) for p in LINE])
json.dump({'type': 'Feature', 'properties': {'name': 'Sham and Hijaz, broader outlines of his diagram'}, 'geometry': mapping(T)},
          open(os.path.join(HERE, 'tools/data/v503_sham_hijaz_outer.geojson'), 'w'))
