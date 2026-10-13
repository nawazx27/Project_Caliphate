"""Version 115 (2026-10-13, Nawaz: "Ykw, just give it v5 borders"; asked, he chose "V5's, keep Black Sea", for V2, V2-B and V2N).
V2's Caucasus becomes V5's: Russia's part is V5's Dagestan block (Derbent, the Samur valley and the Dagestan coast, up to 44 N),
plus Russia's Black Sea coast from Anapa to Sochi kept from Version 109. The Greater Caucasus band and the coast strip of Version 114
and Version 109's thin strips along the crest come out (the line is Georgia's and Azerbaijan's border with Russia again, as in V5).
Nawaz's specification; not from the sources.
Writes tools/data/caucasus_v5.geojson: 'drop' (Russia in the Caucasus box, minus the Black Sea piece) and 'add' (V5's Russian
land in that box, every piece). The Black Sea piece is the largest piece of Russia inside V2 at Version 113 (git 81b44ef).
Run: python3 tools/caucasus_v5.py, then node tools/v2_caucasus_v5.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, MultiPolygon, Polygon, box, mapping
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
G = pyproj.Geod(ellps='WGS84'); A = lambda g: round(abs(G.geometry_area_perimeter(g)[0]) / 1e6)
BOX = box(36, 40, 50, 45)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(BOX)
mp = lambda polys: MultiPolygon([Polygon(p[0], p[1:]) for p in polys]).buffer(0)
old = json.loads(subprocess.check_output(['git', 'show', '81b44ef:atlas-of-the-blessed-lands/src/caliph.json'], cwd=P))
r = mp(old['x']['polys']).intersection(RU)
sea = max([g for g in getattr(r, 'geoms', [r]) if g.geom_type == 'Polygon'], key=lambda g: g.area)
C = json.load(open(os.path.join(P, 'src/caliph.json')))
add = mp(C['x3']['polys']).intersection(RU)
add = MultiPolygon([g for g in getattr(add, 'geoms', [add]) if g.geom_type == 'Polygon'])
drop = RU.difference(sea)
feats = [{'type': 'Feature', 'properties': {'role': 'drop'}, 'geometry': mapping(drop)},
         {'type': 'Feature', 'properties': {'role': 'add', 'km2': A(add)}, 'geometry': mapping(add)},
         {'type': 'Feature', 'properties': {'role': 'sea', 'km2': A(sea)}, 'geometry': mapping(sea)}]
json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', 'caucasus_v5.geojson'), 'w'))
print('Black Sea piece', A(sea), 'km2; V5 Russian land added', A(add), 'km2 in', len(add.geoms), 'pieces')
