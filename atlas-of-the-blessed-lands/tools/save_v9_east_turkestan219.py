"""Nawaz (2026-10-23): "In the V9, remember the current shape of East Turkestan. And save it for future reference."
Saves the East Turkestan part of V9 (key 'v2') as drawn on that date (Version 218): all of V9 inside the base map's China,
which is East Turkestan as the East Turkistan Government in Exile defines it (Version 180, tools/v6_et180.py: Xinjiang without
Aksai Chin, with Subei, Aksay, Dunhuang and Guazhou in Gansu and Mangnai/Lenghu in Qinghai).
Output: tools/data/v9_east_turkestan_v218.geojson (one MultiPolygon, lon/lat)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CN = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['id'] == '156'][0]
C = json.load(open(os.path.join(P, 'src/caliph.json')))
V9 = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
ET = shapely.set_precision(V9.intersection(CN), 0.0001)
km2 = round(A(ET))
out = os.path.join(P, 'tools/data/v9_east_turkestan_v218.geojson')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {
    'name': 'East Turkestan (V9 as of Version 218)', 'km2': km2,
    'definition': 'East Turkistan Government in Exile: Xinjiang without Aksai Chin, plus Subei, Aksay, Dunhuang, Guazhou (Gansu) and Mangnai with Lenghu (Qinghai); Version 180'},
    'geometry': mapping(ET)}]}, open(out, 'w'))
print('saved', out, km2, 'km2')
