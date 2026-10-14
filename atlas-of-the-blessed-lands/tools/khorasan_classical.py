"""Version 139 (2026-10-14, Nawaz: "just include greater khorasan according to all classical sources and geographers to widest and
maximum"; asked, he chose to cut Central Asia back to the classical Khurāsān only, and to include the edge towns the geographers name).
Central Asia (Kazakhstan with Baikonur, Uzbekistan, Kyrgyzstan, Tajikistan, China) in V2 and V2-B becomes:
 - Version 135's widest classical Khurāsān (his three Khorasan maps, all of Transoxiana and Khwārazm as his maps draw them, provinces
   covered ≥99% whole, Isbījāb's district after Le Strange, with its towns kept whole and gaps filled): taken from V2 as it was then
   (git b35a9d2^ = Version 135, src/caliph.json 'x');
 - Jand and Yanghikant, lower Syr Darya (Le Strange; Oghuz towns): the whole Qyzylorda region (Overture KZ-43), as in Version 136;
 - Nawākath and Barskhān (Muqaddasī, Ibn Ḥawqal via Le Strange; Turkish towns of the Chu valley and Lake Issyk-Kul): Kyrgyzstan's
   Chuy and Issyk-Kul regions and Bishkek (admin1_used.geojson);
 - the Kashgar oasis (Lambton: Khurāsān's Central Asian boundary "the Chinese desert and the Pamirs"; my reading): China's Kashgar and
   Kizilsu prefectures (tools/data/kashgar_and_shore.geojson, Version 138).
Not classical, now out: northern and western Kazakhstan, Mangystau, the Balkhash country (Semirechye beyond the Chu valley).
Writes tools/data/khorasan_classical.geojson. Run: python3 tools/khorasan_classical.py <kz_south_div.parquet>, then
node tools/v2_khorasan_classical.js"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H); D = os.path.join(H, 'data')
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
ctry = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) in ('398', 'KAB', '860', '417', '762', '156')}
CA = unary_union(list(ctry.values()))
v135 = json.loads(subprocess.check_output(['git', 'show', 'b35a9d2^:atlas-of-the-blessed-lands/src/caliph.json'], cwd=P))
X135 = MultiPolygon([Polygon(p[0], p[1:]) for p in v135['x']['polys']]).buffer(0).intersection(CA)
QZ = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[1]).to_pylist() if r['subtype'] == 'region' and r['region'] == 'KZ-43'])
KG = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'admin1_used.geojson')))['features'] if f['properties'].get('adm0_a3') == 'KGZ' and f['properties'].get('name') in ('Chuy', 'Ysyk-Köl', 'Bishkek')])
KS = shape(json.load(open(os.path.join(D, 'kashgar_and_shore.geojson')))['features'][0]['geometry']).buffer(0).intersection(ctry['156'])
S = unary_union([X135, QZ.buffer(0.01).intersection(ctry['398'].union(ctry['KAB'])), KG.buffer(0.01).intersection(ctry['417']), KS])
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) > 0.05])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'KHORASAN-CLASSICAL', 'km2': round(A(S))}, 'geometry': mapping(S)}]}, open(os.path.join(D, 'khorasan_classical.geojson'), 'w'))
print('V135 CA', round(A(X135)), 'Qyzylorda', round(A(QZ)), 'Chuy+Issyk-Kul+Bishkek', round(A(KG)), 'Kashgar', round(A(KS)), '-> total', round(A(S)))
