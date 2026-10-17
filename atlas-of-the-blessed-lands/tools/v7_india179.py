"""Version 179 (Nawaz): a new V7 = all of V2 plus India (with the Andaman and Nicobar Islands), Nepal, Bhutan (enclosed by India and
Tibet, so taken whole under the no-gaps rule), Greater Tibet (Tibet Autonomous Region, Qinghai, and the Tibetan autonomous prefectures
and counties: Garzê, Ngawa and Muli in Sichuan, Gannan and Tianzhu in Gansu, Dêqên in Yunnan; Overture divisions), Myanmar, Bangladesh,
Sri Lanka, the Maldives, and the parts of Jammu and Kashmir held by China (Aksai Chin, the Shaksgam valley) and Pakistan (already in V2),
with the Siachen Glacier. Writes CALIPH.x7. Run: python3 tools/v7_india179.py <dir with cn_tibet.parquet and cn_la.parquet>"""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely import wkb
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
C = json.load(open(os.path.join(P, 'src/caliph.json')))
V2 = shapely.make_valid(MultiPolygon([Polygon(r[0], r[1:]) for r in C['me2']['polys']]))
rows = [dict(r) for r in C['me2']['states']]
adds = []
for cid, n in (('356', 'India (with the Andaman and Nicobar Islands)'), ('524', 'Nepal'), ('064', 'Bhutan (enclosed by India and Tibet)'), ('104', 'Myanmar'),
               ('050', 'Bangladesh'), ('144', 'Sri Lanka'), ('462', 'Maldives'), ('KAS', 'Siachen Glacier (Kashmir)')):
    g = G[cid]; adds.append(g); rows.append({'id': cid, 'n': n, 'km2': round(A(g)), 'pct': 100})
# the China-held parts of Jammu and Kashmir (Natural Earth disputed areas, clipped to the Kashmir box)
dis = json.load(open(os.path.join(P, 'ne_10m_admin_0_disputed_areas.geojson')))
KB = box(72, 32.3, 81, 37.2)
for key, n, rid in (('Admin. by China; Claimed by India', 'China: Aksai Chin (Kashmir, held by China)', '156_AC'),
                    ('Ceded to China by Pakistan', 'China: the Shaksgam valley (Kashmir, held by China)', '156_SK')):
    gs = [shapely.make_valid(shape(f['geometry'])).intersection(KB) for f in dis['features'] if key in (f['properties'].get('NOTE_BRK') or '')]
    g = unary_union([x for x in gs if not x.is_empty]); g = g.intersection(G['156'].buffer(0.02)).union(g.intersection(G['356'].buffer(0.02)))
    adds.append(g); rows.append({'id': rid, 'n': n, 'km2': round(A(g)), 'pct': 100}); print(n, round(A(g)))
# Greater Tibet: whole regions and prefectures/counties from Overture, kept to China's land in the base map
t = pq.read_table(os.path.join(D, 'cn_tibet.parquet')).to_pylist() + pq.read_table(os.path.join(D, 'cn_la.parquet')).to_pylist()
WANT_R = {'CN-XZ': 'Tibet Autonomous Region', 'CN-QH': 'Qinghai'}
WANT_C = {'甘孜藏族自治州': 'Garzê (Sichuan)', '阿坝藏族羌族自治州': 'Ngawa (Sichuan)', '木里藏族自治县': 'Muli (Sichuan)', '甘南藏族自治州': 'Gannan (Gansu)',
          '天祝藏族自治县': 'Tianzhu (Gansu)', '迪庆藏族自治州': 'Dêqên (Yunnan)'}
CN = G['156'].buffer(0.01)
parts = {}
for r in t:
    nm = (r['names']['primary'] if r['names'] else '').split(' ')[0]
    if r['subtype'] in ('county', 'localadmin') and r['region'] in WANT_R: lab = WANT_R[r['region']]   # prefectures too: Overture's Qinghai shape alone is short
    elif r['subtype'] == 'region' and nm != '阿克赛钦': lab = WANT_R.get(r['region'])
    else: lab = WANT_C.get(nm)
    if lab: parts.setdefault(lab, []).append(shapely.make_valid(wkb.loads(r['geometry'])))
assert len(parts) == 8, sorted(parts)
tib = []
for lab, gs in parts.items():
    g = unary_union(gs).intersection(CN)
    tib.append(g); rows.append({'id': '156_T', 'n': 'China: Greater Tibet: ' + lab, 'km2': round(A(g)), 'pct': 100}); print(lab, round(A(g)))
adds += tib
X = shapely.union_all([shapely.make_valid(V2)] + [shapely.make_valid(g).buffer(0.003) for g in adds], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
C['x7'] = {'polys': out, 'km2': km2, 'states': rows}
print('V7', km2, 'km2,', len(out), 'pieces,', len(rows), 'rows')
F_ = os.path.join(P, 'src/caliph.json'); json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
