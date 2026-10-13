"""Version 114 (2026-10-13, Nawaz: "Sure", to taking the whole Greater Caucasus into V2; he chose "the republics whole + all mountains",
in V2, V2-B and V2N).
Builds tools/data/greater_caucasus.geojson: the pieces of Russia to add (the base map's Russia, geo2.json, cut by these):
  - the seven North Caucasus republics, whole: Adygea, Karachay-Cherkessia, Kabardino-Balkaria, North Ossetia–Alania, Ingushetia,
    Chechnya and Dagestan (their borders from OpenStreetMap via Overture Maps, tools/data/ru_regions_caucasus.parquet);
  - the mountain land of the Greater Caucasus outside them, in Krasnodar Krai and Stavropol Krai. Mountain land (my method): on the
    Mapzen elevation (tools/data/dem_caucasus_z8.npz), cells at least 400 m high where the ground rises and falls at least 300 m within
    about 5 km (so the gentle Stavropol plateau and the plains are not counted), joined to the main range (Elbrus); small gaps closed.
Run: python3 tools/greater_caucasus.py"""
import json, os, math, subprocess, numpy as np, shapely, pyarrow.parquet as pq
from scipy import ndimage
from shapely.geometry import shape, Polygon, mapping, box
from shapely.ops import unary_union
from rasterio.features import shapes
from affine import Affine
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=R))
RUg = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(36, 40, 50, 47))
T = pq.read_table(os.path.join(H, 'data', 'ru_regions_caucasus.parquet')).to_pylist()
reg = {r['region']: shapely.from_wkb(r['geometry']).buffer(0) for r in T if r['is_land']}
REP = ['RU-AD', 'RU-KC', 'RU-KB', 'RU-SE', 'RU-IN', 'RU-CE', 'RU-DA']
NAMES = {'RU-AD': 'Adygea', 'RU-KC': 'Karachay-Cherkessia', 'RU-KB': 'Kabardino-Balkaria', 'RU-SE': 'North Ossetia–Alania', 'RU-IN': 'Ingushetia', 'RU-CE': 'Chechnya', 'RU-DA': 'Dagestan'}
# mountains on the elevation grid
d = np.load(os.path.join(H, 'data', 'dem_caucasus_z8.npz')); h = d['h']; Z = int(d['z']); X0 = int(d['x0']); Y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z; f = 2
g = h[:h.shape[0] // f * f, :h.shape[1] // f * f].reshape(h.shape[0] // f, f, h.shape[1] // f, f).mean(axis=(1, 3))
win = 23   # about 5 km at ~0.44 km per cell
relief = ndimage.maximum_filter(g, win) - ndimage.minimum_filter(g, win)
m = (g >= 400) & (relief >= 300)
m = ndimage.binary_closing(m, iterations=3)
lab, _ = ndimage.label(m)
def px(lon, lat):
    fx = ((lon + 180) / 360 * n - X0) * TS / f; fy = ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - Y0) * TS / f
    return int(fy), int(fx)
main = lab == lab[px(42.44, 43.35)]
main = ndimage.binary_fill_holes(main)
def tx(ring):
    out = []
    for c, r in ring:
        x = (c * f / TS + X0) / n; y = (r * f / TS + Y0) / n
        out.append((x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))))
    return out
mp = unary_union([Polygon(tx(gm['coordinates'][0]), [tx(q) for q in gm['coordinates'][1:]]) for gm, v in shapes(main.astype('uint8'), mask=main, transform=Affine.identity())]).buffer(0)
feats = []
from pyproj import Geod
geod = Geod(ellps='WGS84'); A = lambda q: abs(geod.geometry_area_perimeter(q)[0]) / 1e6
for r in REP:
    p = reg[r].intersection(RUg)
    feats.append({'type': 'Feature', 'properties': {'id': r, 'n': NAMES[r], 'kind': 'republic', 'km2': round(A(p))}, 'geometry': mapping(p)})
reps = unary_union([reg[r] for r in REP])
for r, nm in [('RU-KDA', 'Krasnodar Krai'), ('RU-STA', 'Stavropol Krai')]:
    p = mp.intersection(reg[r]).difference(reps).intersection(RUg)
    p = unary_union([q for q in getattr(p, 'geoms', [p]) if q.geom_type == 'Polygon' and A(q) >= 20])
    if not p.is_empty: feats.append({'type': 'Feature', 'properties': {'id': r, 'n': nm + ': its mountains of the Greater Caucasus', 'kind': 'mountains', 'km2': round(A(p))}, 'geometry': mapping(p)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', 'greater_caucasus.geojson'), 'w'))
for f_ in feats: print(f_['properties']['n'], f_['properties']['km2'], 'km2')
print('mountain land of the whole range (all countries)', round(A(mp)), 'km2')
