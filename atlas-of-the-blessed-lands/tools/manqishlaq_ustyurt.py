"""Version 141 (2026-10-14, Nawaz: "Sure", to adding the two doubtful desert edges of the widest classical Khurāsān left outside after
Version 140): Manqishlāq / Siyāh-Kūh (Ibn Ḥawqal's Ghuzz pasture beside Khwārazm), taken as Kazakhstan's whole Mangystau region (Overture
KZ-47 districts: Tupkaragan, Munaily, Aktau, Mangystau, Karakiya, Beyneu, Zhanaozen), and the Ustyurt plateau (the Ghuzz desert between
Khwārazm and the Caspian), taken as the rest of Uzbekistan (so Uzbekistan whole) with the Kazakh Ustyurt inside the Mangystau region.
Doubtful as Khurāsān; included so nothing is left out. Writes tools/data/manqishlaq_ustyurt.geojson.
Run: python3 tools/manqishlaq_ustyurt.py <kz_div_areas.parquet>, then node tools/v2_manqishlaq_ustyurt.js"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
MG = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[1]).to_pylist() if r['subtype'] == 'county' and r['region'] == 'KZ-47'])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
c = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) in ('398', '860')}
S = unary_union([c['398'].intersection(MG.buffer(0.02)), c['860']])
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) > 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'MANQISHLAQ-USTYURT', 'mangystau_km2': round(A(c['398'].intersection(MG.buffer(0.02))))}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'manqishlaq_ustyurt.geojson'), 'w'))
print('Mangystau', round(A(MG)), 'km2; total with Uzbekistan', round(A(S)))
