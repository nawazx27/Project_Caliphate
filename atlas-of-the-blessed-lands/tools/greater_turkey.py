"""Version 97 (2026-10-12, Nawaz: "Greater turkey should look like this", with three maps and the Misak-ı Millî article; he chose to
take out the Ottoman Balkans of Version 96 and keep only the part of Bulgaria his maps colour red).
Builds tools/data/greater_turkey.geojson with two features:
  "outline": Greater Turkey as the union of everything his maps colour (reference/greater_turkey_silk_map.webp,
             reference/greater_turkey_2019_map.jpg, reference/greater_turkey_1950_map.jpg, reference/misak_i_milli_wikipedia.jpg);
  "v2_add":  the land of it that V2 lacks once Version 96 is undone: the part of Bulgaria (and a sliver of North Macedonia) they colour red.
The silk-flag map is traced: its red is picked out by colour and warped to longitude and latitude by a thin-plate spline through
14 towns printed on it (my method; good to some 10-25 km, it is a photograph of painted silk). The other maps are taken by province
(Natural Earth admin-1, saved in tools/data/ne_admin1_greater_turkey.geojson). A Bulgarian province is taken whole when a map colours
40% or more of it or its main town; beyond those, the traced red is added as it lies.
Usage: python3 tools/greater_turkey.py [ne_10m_admin_1_states_provinces.shp] geo2_countries.geojson"""
import sys, json, numpy as np
from PIL import Image
from scipy.interpolate import RBFInterpolator
from shapely.geometry import shape, Polygon, box, mapping
from shapely.ops import unary_union
from pyproj import Geod
Gd = Geod(ellps='WGS84'); km2 = lambda g: abs(Gd.geometry_area_perimeter(g)[0]) / 1e6 if not g.is_empty else 0
A1F = 'tools/data/ne_admin1_greater_turkey.geojson'
WANT = {'TUR': None, 'BGR': None, 'MKD': None,
        'GRC': ['Anatoliki Makedonia kai Thraki', 'Kentriki Makedonia', 'Ayion Oros', 'Voreio Aigaio', 'Notio Aigaio'],
        'GEO': ['Ajaria'], 'SYR': ['Aleppo', 'Idlib', 'Ar Raqqah', 'Hasaka (Al Haksa)', 'Dayr Az Zawr', 'Hamah', 'Homs (Hims)', 'Lattakia', 'Tartus'],
        'IRQ': ['Ninawa', 'Dihok', 'Arbil', "At-Ta'mim", 'As-Sulaymaniyah']}
args = sys.argv[1:]
if args and args[0].endswith('.shp'):
    import shapefile
    r = shapefile.Reader(args.pop(0), encoding='utf-8'); fl = [f[0] for f in r.fields[1:]]; out = []
    for sr in r.iterShapeRecords():
        d = dict(zip(fl, sr.record)); c = d['adm0_a3']
        if c in WANT and (WANT[c] is None or d['name'] in WANT[c]) and c != 'TUR':
            out.append({'type': 'Feature', 'properties': {'adm0_a3': c, 'name': d['name']}, 'geometry': sr.shape.__geo_interface__})
    json.dump({'type': 'FeatureCollection', 'features': out}, open(A1F, 'w'))
A1 = json.load(open(A1F))['features']
prov = lambda c, n: shape(next(f for f in A1 if f['properties']['adm0_a3'] == c and f['properties']['name'] == n)['geometry']).buffer(0)
C0 = {f['properties']['id']: shape(f['geometry']).buffer(0) for f in json.load(open(args[0]))['features']}   # base-map countries
# --- the silk-flag map, traced
im = np.asarray(Image.open('reference/greater_turkey_silk_map.webp').convert('RGB')).astype(int)
CP = [((219, 50), (26.10, 44.43)), ((84, 185), (23.32, 42.70)), ((86, 303), (22.94, 40.64)), ((126, 515), (23.73, 37.98)),
      ((320, 137), (27.91, 43.21)), ((395, 267), (29.10, 41.22)), ((345, 64), (28.63, 44.17)), ((222, 95), (25.95, 43.85)),
      ((714, 159), (35.15, 42.03)), ((903, 530), (37.16, 36.20)), ((1076, 107), (41.64, 41.64)), ((1246, 419), (43.13, 36.34)),
      ((1328, 475), (44.39, 35.47)), ((1359, 189), (45.41, 39.21))]   # Bucarest, Sofia, Selanik, Athènes, Varna, the Bosporus, Constanţa, Ruse, Sinope, Halep, Batum, Musul, Kerkük, Nahçıvan
warp = RBFInterpolator(np.array([p for p, _ in CP], float), np.array([l for _, l in CP], float), kernel='thin_plate_spline', degree=1)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
red = (R > 150) & (G < 110) & (B < 120) & (R - G > 80)
cells = []
for y in range(red.shape[0]):
    row = red[y]; x = 0
    while x < row.size:
        if row[x]:
            x0 = x
            while x < row.size and row[x]: x += 1
            cells.append(Polygon(warp(np.array([[x0, y], [x, y], [x, y + 1], [x0, y + 1]], float))))
        else: x += 1
m = unary_union(cells).buffer(0.01).buffer(-0.01)
# the silk's gold lettering, crescent and star leave holes: fill them; the old map's own red city dots and lettering are small loose
# pieces (under 600 km²) and are dropped (the Aegean islands among them are taken whole by province below)
SILK = unary_union([Polygon(p.exterior) for p in getattr(m, 'geoms', [m]) if km2(Polygon(p.exterior)) >= 600])
# --- Bulgaria: whole provinces where a map colours 40% or more, or the main town (the 2019 map: Şumnu, Eski Cuma); plus the traced red
BG_WHOLE = ['Burgas', 'Yambol', 'Haskovo', 'Kardzhali', 'Smolyan', 'Sliven', 'Stara Zagora', 'Plovdiv', 'Pazardzhik', 'Blagoevgrad', 'Varna', 'Shumen', 'Targovishte']
sel = unary_union([prov('BGR', n) for n in BG_WHOLE] + [SILK])
uns = unary_union([shape(f['geometry']).buffer(0) for f in A1 if f['properties']['adm0_a3'] == 'BGR' and f['properties']['name'] not in BG_WHOLE])
BG = C0['100'].intersection(sel.buffer(0.03).difference(uns.difference(SILK)))
MK = C0['807'].intersection(SILK)
GR_DODEC = prov('GRC', 'Notio Aigaio').intersection(box(26.2, 35.0, 30.0, 37.6))
KM_EAST = prov('GRC', 'Kentriki Makedonia').intersection(box(22.55, 39.8, 24.5, 41.5))   # the 2019 map: Selanik, Kılkış, Serez, Chalkidiki
OUT = unary_union([SILK, C0['792'], C0['196'], C0['CYN'], BG, MK, GR_DODEC, KM_EAST] + [prov('GRC', n) for n in ['Anatoliki Makedonia kai Thraki', 'Ayion Oros', 'Voreio Aigaio']]
                  + [prov(c, n) for c in ('GEO', 'SYR', 'IRQ') for n in WANT[c]])
FC = {'type': 'FeatureCollection', 'features': [
    {'type': 'Feature', 'properties': {'part': 'outline', 'km2': round(km2(OUT))}, 'geometry': mapping(OUT.simplify(0.003))},
    {'type': 'Feature', 'properties': {'part': 'v2_add', 'bulgaria_km2': round(km2(BG)), 'north_macedonia_km2': round(km2(MK))}, 'geometry': mapping(unary_union([BG, MK]))}]}
json.dump(FC, open('tools/data/greater_turkey.geojson', 'w'))
print('outline', round(km2(OUT)), '| Bulgaria part', round(km2(BG)), 'of', round(km2(C0['100'])), '| N. Macedonia part', round(km2(MK)), '| silk traced', round(km2(SILK)))
