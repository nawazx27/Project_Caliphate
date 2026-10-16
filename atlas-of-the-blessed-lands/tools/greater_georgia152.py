"""Version 152 (2026-10-16, Nawaz: "Include greater Georgia in v2 and not in v2b"; an exception, for V2 only, to his rule of
keeping the Caucasus at the modern Georgia and Azerbaijan borders). Greater Georgia at its widest is the kingdom under Queen Tamar,
which the medieval Georgian chronicles describe as reaching "from Nikopsia to Darband" (Claude's synthesis; wording not checked
against the source in this session). Its parts in today's Russia are added to V2 only:
 - the Black Sea coast from Abkhazia north-west to Nikopsia (taken at Novomikhaylovsky, 38.86 E), south of the main Caucasus crest
   (tools/data/caucasus_south_of_crest.geojson, Version 109's elevation tracing): Sochi, Lazarevskoye, Tuapse;
 - Alania = today's North Ossetia–Alania (Overture Maps region outline, tools/data/north_ossetia.geojson), a vassal of Tamar;
 - Darband = Derbent, with V5's Dagestan block (tools/data/caucasus_v5.geojson, role add).
 - the small pieces of Russia south of the crest along the Georgian border (same file).
Tao-Klarjeti and Lazona (Türkiye), Saingilo (Azerbaijan) and Lori (Armenia) are already inside. V2-B stays at the modern borders.
Writes tools/data/greater_georgia152.geojson. Run: python3 tools/greater_georgia152.py"""
import json, os, subprocess
from shapely.geometry import shape, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
soc = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(D, 'caucasus_south_of_crest.geojson')))['features']])
coast = soc.intersection(box(38.86, 41.0, 41.0, 45.0))
crest_bits = soc.difference(box(30, 41.0, 41.0, 45.0))
alania = shape(json.load(open(os.path.join(D, 'north_ossetia.geojson')))['features'][0]['geometry']).buffer(0)
derbent = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(D, 'caucasus_v5.geojson')))['features'] if f['properties'].get('role') == 'add'])
parts = {'Black Sea coast to Nikopsia': coast, 'Alania (North Ossetia)': alania, 'Derbent block': derbent, 'south of the crest': crest_bits}
for n, g in parts.items(): print(n, round(A(g.intersection(RU))), 'km2')
GG = unary_union(list(parts.values())).intersection(RU)
print('Greater Georgia in Russia', round(A(GG)), 'km2')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 152 Greater Georgia (V2 only)'}, 'geometry': mapping(GG)}]}, open(os.path.join(D, 'greater_georgia152.geojson'), 'w'))
