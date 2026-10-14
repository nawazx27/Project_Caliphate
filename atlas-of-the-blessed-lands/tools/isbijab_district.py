"""Version 135 (2026-10-14, Nawaz: "make sure you get the widest and max greater khorasan", for V2). The classical wide sense counts
Isbījāb among Khurāsān's cities (Qudāma b. Jaʿfar, as reported in Encyclopaedia Iranica) and al-Yaʿqūbī stretches Khurāsān to Farghāna;
Le Strange (Lands of the Eastern Caliphate, ch. XXXIV) gives Isbījāb's district as Sayrām, Chimkand (Shymkent), Fārāb/Utrār, Yasī,
Ṣabrān, Ṭarāz and Mirkī (and the Oghuz towns Jand and Yanghikant, which were not Muslim-ruled and are left out). On today's map
(Overture Maps 2026-09-23.1 division areas): the Turkistan region whole (KZ-61) and Shymkent (KZ-79), and from the Zhambyl region the
Ṭarāz oasis to Mirkī: Taraz city, the Zhualy, Talas, Zhambyl, Baizak, Turar Ryskulov and Merke districts (not the Moyynkum and Sarysu
sands nor Shu and Kordai east of Mirkī). Clipped to geo2's Kazakhstan. My mapping of Le Strange's list to modern districts.
Writes tools/data/isbijab_district.geojson. Run: python3 tools/isbijab_district.py <kz_south_div.parquet>"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
ZH = {'Тараз қаласының әкімшілігі', 'Жуалы ауданы', 'Талас ауданы', 'Жамбыл ауданы', 'Байзақ ауданы', 'Тұрар Рысқұлов ауданы', 'Меркі ауданы'}
gs, names = [], []
for r in pq.read_table(sys.argv[1]).to_pylist():
    n = (r['names'] or {}).get('primary')
    if (r['subtype'] == 'region' and r['region'] in ('KZ-61', 'KZ-79')) or (r['subtype'] == 'county' and r['region'] == 'KZ-31' and n in ZH):
        gs.append(shapely.from_wkb(r['geometry']).buffer(0)); names.append(n)
assert len(gs) == 9, names
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
KZ = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '398'][0]
S = KZ.intersection(unary_union(gs).buffer(0.01)).intersection(KZ)
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'ISBIJAB', 'km2': round(A(S)), 'units': names}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'isbijab_district.geojson'), 'w'), ensure_ascii=False)
print('area', round(A(S)), 'km2', names)
