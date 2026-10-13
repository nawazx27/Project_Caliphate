"""Version 114 (2026-10-13, Nawaz: the whole Greater Caucasus in V2, V2-B and V2N; after first choosing "the republics whole + all
mountains" he asked, on seeing it: "Extend the border a bit upwards so that it looks like the border of Georgia and Azerbaijan combined",
and chose "to the foot of the mountains").
Builds tools/data/greater_caucasus.geojson: the Russian land of the Greater Caucasus down to the northern foot of the mountains, so the
new northern line follows the range like Georgia's and Azerbaijan's northern border, further up.
Mountain land (my method): on the Mapzen elevation (tools/data/dem_caucasus_z8.npz), cells at least 400 m high where the ground rises and
falls at least 300 m within about 5 km (so the gentle Stavropol plateau and the plains are left out), small gaps closed, joined to the main
range (Elbrus), valleys inside filled, the edge smoothed (about 3 km); cut to Russia in the base map (geo2.json).
Run: python3 tools/greater_caucasus.py"""
import json, os, math, subprocess, numpy as np
from scipy import ndimage
from shapely.geometry import shape, Polygon, mapping, box
from shapely.ops import unary_union
from rasterio.features import shapes
from affine import Affine
from pyproj import Geod
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=R))
RUg = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(36, 40, 50, 47))
d = np.load(os.path.join(H, 'data', 'dem_caucasus_z8.npz')); h = d['h']; Z = int(d['z']); X0 = int(d['x0']); Y0 = int(d['y0']); TS = int(d['ts']); n = 2 ** Z; f = 2
g = h[:h.shape[0] // f * f, :h.shape[1] // f * f].reshape(h.shape[0] // f, f, h.shape[1] // f, f).mean(axis=(1, 3))
relief = ndimage.maximum_filter(g, 23) - ndimage.minimum_filter(g, 23)
m = ndimage.binary_closing((g >= 400) & (relief >= 300), iterations=3)
def px(lon, lat):
    fx = ((lon + 180) / 360 * n - X0) * TS / f; fy = ((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n - Y0) * TS / f
    return int(fy), int(fx)
lab, _ = ndimage.label(m); main = ndimage.binary_fill_holes(lab == lab[px(42.44, 43.35)])
main = ndimage.binary_opening(ndimage.binary_closing(main, iterations=7), iterations=4)   # smooth the edge (about 3 km)
lab2, _ = ndimage.label(main); main = ndimage.binary_fill_holes(lab2 == lab2[px(42.44, 43.35)])
def tx(ring):
    out = []
    for c, r in ring:
        x = (c * f / TS + X0) / n; y = (r * f / TS + Y0) / n
        out.append((x * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y))))))
    return out
mp = unary_union([Polygon(tx(gm['coordinates'][0]), [tx(q) for q in gm['coordinates'][1:]]) for gm, v in shapes(main.astype('uint8'), mask=main, transform=Affine.identity())]).buffer(0)
p = mp.intersection(RUg)
geod = Geod(ellps='WGS84'); A = lambda q: abs(geod.geometry_area_perimeter(q)[0]) / 1e6
parts = [q for q in getattr(p, 'geoms', [p]) if q.geom_type == 'Polygon' and A(q) >= 20]
p = unary_union(parts).simplify(0.002)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'RU-GC', 'n': 'the northern side of the Greater Caucasus, to the foot of the mountains', 'kind': 'mountains', 'km2': round(A(p))}, 'geometry': mapping(p)}]},
          open(os.path.join(H, 'data', 'greater_caucasus.geojson'), 'w'))
print('Russian land of the range', round(A(p)), 'km2 in', len(getattr(p, 'geoms', [p])), 'pieces')
