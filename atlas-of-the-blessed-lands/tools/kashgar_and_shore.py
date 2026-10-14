"""Version 138 (2026-10-14, Nawaz: "Add entire modern Pakistan, Afghanistan, Uzbekistan, Kazakhstan, Turkmenistan, Tajikistan, Kyrgyzstan to
v2 and v2b and even at the thing that you said was left outside"). The things said to be left outside: (1) the Kashgar oasis, which the
widest reading of Lambton's Khurāsān ("its Central Asian boundary was the Chinese desert and the Pamirs") could take in: taken as China's
Kashgar Prefecture (喀什地区: Kashgar, Yarkand, Tashkurgan, Maralbexi, to the Taklamakan's western edge) and the Kizilsu Kyrgyz Prefecture
between it and Kyrgyzstan (Artux, Akto, Ulugqat), with the Caohu enclave (Overture Maps 2026-09-23.1 division areas), clipped to geo2's
China; (2) the last ~4.6 km² of his region maps along the south-east Caspian shore, taken as the missing pieces widened by 0.003°
without clipping to the base map's land (a few hundred metres of shore). Writes tools/data/kashgar_and_shore.geojson.
Run: python3 tools/kashgar_and_shore.py <cn_kashgar_div.parquet>, then node tools/v2_ca_countries_whole.js"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data')
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
WANT = ('喀什地区', '克孜勒苏柯尔克孜自治州', '草湖项目区')
K = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[1]).to_pylist() if r['subtype'] == 'county' and any(((r['names'] or {}).get('primary') or '').startswith(w) for w in WANT)])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CN = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '156'][0]
KG = CN.intersection(K.buffer(0.01))
M = shape(json.load(open(os.path.join(D, 'khorasan_max.geojson')))['features'][0]['geometry']).buffer(0)
C = json.load(open(os.path.join(P, 'src', 'caliph.json')))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
SH = M.difference(X).buffer(0.003)
S = unary_union([KG, SH])
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) > 0])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KASHGAR-SHORE', 'kashgar_km2': round(A(KG)), 'shore_km2': round(A(SH), 1)}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'kashgar_and_shore.geojson'), 'w'))
print('Kashgar+Kizilsu', round(A(KG)), 'km2; shore pieces', round(A(SH), 1))
