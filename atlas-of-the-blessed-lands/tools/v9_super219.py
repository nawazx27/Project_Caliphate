"""Version 219 (Nawaz, 2026-10-23, the "Super Caliphate" in V9, key 'v2'):
"In V9, give the Balkans the shape of V3. Include Afghanistan, Pakistan, India, Nepal, Bhutan, Greater Tibet, Bangladesh, Sri Lanka,
Myanmar, Maldives; in Jammu and Kashmir include the land administered by Pakistan and the land administered by China; and the entire
Southeast Asia [of his Britannica map: Myanmar, Thailand, Laos, Cambodia, Vietnam, Malaysia, Singapore, Brunei, Indonesia, the
Philippines, East Timor], and add Papua New Guinea. ... For the Super Caliphate, remove East Turkestan. And remove Sicily."
- Balkans: everything V9 held in 13-30.5 E, 39.5-49 N is replaced by what V3 holds there (Greece, Bulgaria, Albania, North Macedonia,
  Turkish Thrace); Romania, Serbia, Kosovo, Montenegro, Bosnia, Croatia and Slovenia go out.
- East Turkestan (all of V9 inside the base map's China; saved first by tools/save_v9_east_turkestan219.py) and Sicily with its
  islands (Malta stays) go out.
- Greater Tibet as the Central Tibetan Administration defines it (Wikipedia 'Greater Tibet'): the Tibet Autonomous Region, Qinghai,
  and the Tibetan autonomous prefectures and counties of Sichuan (Garze, Ngawa, Muli), Gansu (Gannan, Tianzhu) and Yunnan (Diqing);
  lines from Overture divisions 2026-09-23.1, kept to the base map's China. Qinghai's Mangnai/Lenghu, once in East Turkestan, come
  back as part of Greater Tibet.
- China-administered Kashmir: Aksai Chin and the Shaksgam valley (Natural Earth disputed areas), kept to the base map's China.
- Whole: India (with the Siachen Glacier), Nepal, Bhutan, Bangladesh, Sri Lanka, the Maldives, Myanmar, Thailand, Laos, Cambodia,
  Vietnam, Malaysia, Singapore, Brunei, Indonesia, the Philippines, East Timor, Papua New Guinea. Afghanistan and Pakistan (with
  Azad Kashmir and Gilgit-Baltistan) were already whole in V9.
- Nawaz then: "Apply it and add Andaman and Nicobar Islands as well": they are part of India on the base map (16 islands); India's
  islands in 92-94.5 E, 6-14.2 N from Natural Earth 10 m are added too, for the two islets the base map lacks.
Run: python3 tools/v9_super219.py <dir with cn_tibet.parquet and cn_la.parquet>, then tools/fill_gaps.py v2, then
tools/v9_super_gaps219.py <same dir> (no-gaps rule for V9 only, never inside East Turkestan)."""
import json, os, sys, subprocess, shapely, pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, box, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = sys.argv[1]
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
CN = G['156']
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
V = M('v2')
# Balkans as in V3
BX = box(13, 39.5, 30.5, 49)
V = V.difference(BX).union(M('me2').intersection(BX))
# Sicily and its islands out (Malta and Tunisia untouched)
V = V.difference(box(11.5, 35, 16, 39).difference(G['470'].buffer(0.05)).difference(G['788'].buffer(0.02)))
# East Turkestan out: nothing of China stays except what is added below
V = V.difference(CN)
# Greater Tibet
g_ = lambda r: shapely.make_valid(wkb.loads(r['geometry']))
rows = pq.read_table(os.path.join(D, 'cn_tibet.parquet')).to_pylist() + pq.read_table(os.path.join(D, 'cn_la.parquet')).to_pylist()
nm = lambda r: (r['names'] or {}).get('primary', '').split(' ')[0]
REG = {'CN-XZ', 'CN-QH'}
SUB = ['甘孜藏族自治州', '阿坝藏族羌族自治州', '木里藏族自治县', '甘南藏族自治州', '天祝藏族自治县', '迪庆藏族自治州']
parts = [g_(r) for r in rows if r['subtype'] == 'region' and r['region'] in REG]
found = {nm(r): g_(r) for r in rows if nm(r) in SUB}
assert len(parts) == 2 and sorted(found) == sorted(SUB), (len(parts), sorted(found))
TIB = unary_union(parts + list(found.values())).intersection(CN.buffer(0.01))
# China-administered Kashmir
NE = json.load(open(os.path.join(P, 'ne_10m_admin_0_disputed_areas.geojson')))
KCN = unary_union([shape(x['geometry']).buffer(0) for x in NE['features'] if x['properties'].get('BRK_NAME') in ('Aksai Chin', 'Shaksam Valley')]).intersection(CN.buffer(0.01))
NE10 = json.load(open(os.path.join(P, 'ne_10m_admin_0_countries.geojson')))
ANI = unary_union([shape(x['geometry']).buffer(0) for x in NE10['features'] if x['properties'].get('ADM0_A3') == 'IND']).intersection(box(92, 6, 94.5, 14.2))
ADD = {'356': 'India', 'KAS': 'Siachen Glacier', '524': 'Nepal', '064': 'Bhutan', '050': 'Bangladesh', '144': 'Sri Lanka', '462': 'Maldives',
       '104': 'Myanmar', '764': 'Thailand', '418': 'Laos', '116': 'Cambodia', '704': 'Vietnam', '458': 'Malaysia', '702': 'Singapore',
       '096': 'Brunei', '360': 'Indonesia', '608': 'Philippines', '626': 'East Timor', '598': 'Papua New Guinea'}
X = shapely.union_all([V, TIB.buffer(0.003), KCN.buffer(0.003), ANI.buffer(0.003)] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
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
print('Andaman and Nicobar', round(A(ANI)), 'inside', round(A(ANI.intersection(Y)) / A(ANI) * 100, 2))
print('Greater Tibet', round(A(TIB)), {k: round(A(v)) for k, v in found.items()}, '| China-held Kashmir', round(A(KCN)))
print('V9', C['v2']['km2'], '->', km2)
OUT = {'642', '688', '191', '070', '705', '499', 'KOS', '156_X', '380_C'}
cn = A(CN)
C['v2'].update(polys=out, km2=km2, states=[r for r in C['v2']['states'] if r['id'] not in OUT and r['id'] not in ADD] +
    [{'id': i, 'n': 'India (with the Andaman and Nicobar Islands)' if i == '356' else n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()] +
    [{'id': '156_T', 'n': 'China: Greater Tibet as the Central Tibetan Administration defines it (the Tibet Autonomous Region, Qinghai, and the Tibetan autonomous prefectures and counties of Sichuan, Gansu and Yunnan)', 'km2': round(A(TIB)), 'pct': round(A(TIB) / cn * 100)},
     {'id': '156_K', 'n': 'China: the parts of Jammu and Kashmir it administers (Aksai Chin and the Shaksgam valley)', 'km2': round(A(KCN)), 'pct': round(A(KCN) / cn * 100, 1)}])
# East Turkestan's province-history entries (the 'XJ' units and country note) leave V9 with it
C['v2']['units'] = [u for u in C['v2']['units'] if u['a3'] != 'XJ']; C['v2']['countries'] = [c for c in C['v2']['countries'] if c['a3'] != 'XJ']; C['v2'].pop('xinjiang', None)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
