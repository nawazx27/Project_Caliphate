"""Version 100 (2026-10-12, Nawaz: "Add Kastellorizo too" ... "use Wikipedia as well to find out its location"). Natural Earth does
not draw Kastellorizo (Megisti) or its islets, OpenStreetMap could not be reached from the cloud computer, and the height grid is
wrong this close to the Turkish coast, so the three islands are traced from the red dotted outline of the author's Google Maps
screenshot (reference/kastellorizo_google_maps.png; dot centres in tools/data/kastellorizo_px.json, chained nearest-neighbour) and
placed with Wikipedia (read 2026-10-12): Kastellorizo 36°08'42"N 29°35'06"E, 9.2 km²; Ro 36°09'19"N 29°29'50"E, 1.6 km²;
Strongyli 0.9 km²; Psomi islet 36.1538 N 29.6088 E, 0.0035 km². Google's map is north-up Mercator, so one scale fits: it is set so
Kastellorizo and Ro together have Wikipedia's 10.8 km², and the position by least squares on the two islands' coordinates (my method;
checks: Ro then measures 1.53 km², Strongyli's visible outline 0.87 km², the two islands 7.7 km apart against 8.0 km from the
coordinates; good to some 200-300 m). Strongyli's southern edge is under Google's label, so it is closed straight across.
Writes tools/data/kastellorizo.geojson. Run: python3 tools/kastellorizo.py"""
import json, math
from shapely.geometry import Polygon, Point, mapping
from shapely.ops import transform
from pyproj import Geod
G = Geod(ellps='WGS84'); km2 = lambda g: abs(G.geometry_area_perimeter(g)[0]) / 1e6
P = json.load(open('tools/data/kastellorizo_px.json'))
WIKI = {'Kastellorizo': (29 + 35/60 + 6/3600, 36 + 8/60 + 42/3600, 9.2), 'Ro': (29 + 29/60 + 50/3600, 36 + 9/60 + 19/3600, 1.6)}
px = {n: Polygon(v['px']).buffer(0) for n, v in P.items()}
s = math.sqrt(sum(WIKI[n][2] for n in WIKI) / sum(px[n].area for n in WIKI))   # km per pixel
LAT = 36.15; kx = s / (111.320 * math.cos(math.radians(LAT))); ky = s / 110.95   # degrees per pixel
# position: lon = a + x*kx, lat = b - y*ky, least squares on the two centroids
a = sum(WIKI[n][0] - px[n].centroid.x * kx for n in WIKI) / 2
b = sum(WIKI[n][1] + px[n].centroid.y * ky for n in WIKI) / 2
ll = lambda g: transform(lambda x, y, z=None: (a + x * kx, b - y * ky), g)
feats = []
for n in ('Kastellorizo', 'Ro', 'Strongyli'):
    g = ll(px[n]); c = g.centroid
    err = G.inv(c.x, c.y, WIKI[n][0], WIKI[n][1])[2] / 1000 if n in WIKI else None
    feats.append({'type': 'Feature', 'properties': {'name': n, 'km2': round(km2(g), 2), 'centroid_off_wikipedia_km': err and round(err, 2)}, 'geometry': mapping(g)})
psomi = Point(29.6088, 36.1538).buffer(0.00036, quad_segs=4)   # about 0.0035 km², Wikipedia's area, at its coordinate
feats.append({'type': 'Feature', 'properties': {'name': 'Psomi', 'km2': round(km2(psomi), 4)}, 'geometry': mapping(psomi)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open('tools/data/kastellorizo.geojson', 'w'))
for f in feats: print(f['properties'])
print('scale', round(s * 1000, 1), 'm per pixel; Ro-Kastellorizo', round(G.inv(*ll(px['Ro']).centroid.coords[0], *ll(px['Kastellorizo']).centroid.coords[0])[2] / 1000, 2), 'km')
