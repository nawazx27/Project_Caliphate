"""Version 224 (Nawaz, 2026-10-23: "make another version of Caliphate. In this Caliphate, the lands must include Afghanistan, Pakistan,
India, Sri Lanka, Nepal, Bhutan, Greater Tibet, Andaman and Nicobar Islands, Maldives, Myanmar, and Pakistan administered Kashmir,
along with China administered Kashmir." He chose: ONLY these lands; Bangladesh included (India and Myanmar would enclose it); NOT the
standing every-outline lands (Cyprus, Azerbaijan, Georgia, Armenia, Lake Albert) in this one.
Built: Afghanistan, Pakistan (with Azad Kashmir and Gilgit-Baltistan), India (with the Siachen Glacier and, from Natural Earth 10 m,
every Andaman and Nicobar islet), Sri Lanka, Nepal, Bhutan, Bangladesh, the Maldives, Myanmar, each whole; Greater Tibet as verified in
Version 222 (tools/data/greater_tibet_v222.geojson); China-held Kashmir (Natural Earth's Aksai Chin and Shaksgam valley), kept to the
base map's China.
Run: python3 tools/south_asia224.py <key>, then tools/fill_gaps.py <key> and the no-gaps applier."""
import json, os, sys, subprocess, shapely
from shapely.geometry import shape, box, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); KEY = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
CN = G['156']
ADD = {'004': 'Afghanistan', '586': 'Pakistan (with Azad Kashmir and Gilgit-Baltistan)', '356': 'India (with the Andaman and Nicobar Islands)',
       'KAS': 'Siachen Glacier', '144': 'Sri Lanka', '524': 'Nepal', '064': 'Bhutan', '050': 'Bangladesh', '462': 'Maldives', '104': 'Myanmar'}
NE10 = json.load(open(os.path.join(P, 'ne_10m_admin_0_countries.geojson')))
ANI = unary_union([shape(x['geometry']).buffer(0) for x in NE10['features'] if x['properties'].get('ADM0_A3') == 'IND']).intersection(box(92, 6, 94.5, 14.2))
GT = shape(json.load(open(os.path.join(P, 'tools/data/greater_tibet_v222.geojson')))['features'][0]['geometry']).buffer(0)
NE = json.load(open(os.path.join(P, 'ne_10m_admin_0_disputed_areas.geojson')))
KCN = unary_union([shape(x['geometry']).buffer(0) for x in NE['features'] if x['properties'].get('BRK_NAME') in ('Aksai Chin', 'Shaksam Valley')]).intersection(CN.buffer(0.01))
X = shapely.union_all([G[i].buffer(0.003) for i in ADD] + [ANI.buffer(0.003), GT.buffer(0.003), KCN.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i, n in ADD.items(): print(n, round(A(G[i].intersection(Y)) / A(G[i]) * 100, 2))
print('Andaman and Nicobar', round(A(ANI.intersection(Y)) / A(ANI) * 100, 2), '| Greater Tibet', round(A(GT.intersection(Y)) / A(GT) * 100, 2), '| China-held Kashmir', round(A(KCN.intersection(Y)) / A(KCN) * 100, 2))
print(KEY, km2)
cn = A(CN)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
C[KEY] = {'polys': out, 'km2': km2, 'states': [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()] + [
    {'id': '156_T', 'n': 'China: Greater Tibet (the Tibet Autonomous Region, Qinghai, and the Tibetan autonomous prefectures and counties of Sichuan, Gansu and Yunnan)', 'km2': round(A(GT)), 'pct': round(A(GT) / cn * 100)},
    {'id': '156_K', 'n': 'China: the parts of Jammu and Kashmir it administers (Aksai Chin and the Shaksgam valley)', 'km2': round(A(KCN)), 'pct': round(A(KCN) / cn * 100, 1)}]}
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
