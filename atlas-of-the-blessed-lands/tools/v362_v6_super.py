"""Version 362 (Nawaz: "Let's build Super Caliphate V6. Take the second atlas from the first image as the base [= the connected V5 of
Version 356, "nose a bit higher"] and add East Turkestan, Greater Tibet and the entire Tibetan Plateau, India, Indian-administered
Kashmir, Chinese-administered Kashmir, the entire princely state of Jammu and Kashmir, Bhutan, Nepal, Bangladesh, Myanmar, Sri Lanka,
the Maldives, and the Chagos Archipelago. Also, incorporate the elements from the last three images" = Melanesia (New Guinea, the
Bismarck Archipelago, the Solomon and Santa Cruz Islands, Vanuatu, Fiji, New Caledonia), Britannica's Southeast Asia (Myanmar, Thailand,
Laos, Vietnam, Cambodia, Malaysia, Singapore, Brunei, Indonesia, the Philippines, East Timor) and Britannica's Malay Archipelago (with
Papua New Guinea).
The new Super Caliphate goes into a NEW key, CALIPH.sup (XV 'sup'); the old Super Caliphate (CALIPH.v2, with its province history) is kept as hidden data.
  base  = tools/data/v362_base_v356_grm.json (V5 as in Version 356, commit e187080)
  + the current V5 (grm) and V4 (sas), so V6 holds every smaller version
  + East Turkestan (tools/data/v9_east_turkestan_v218.geojson), Greater Tibet (greater_tibet_v222), the whole plateau
    (tibetan_plateau_3000m and the whole edge counties of v5_tibet_plateau277), China-held Kashmir (china_kashmir_ne)
  + the countries above, each whole with its islands, from the page's own base map (geo2.json)
DIR env = project dir to edit (default: this repo)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
M = lambda k: MP(C[k]['polys'])
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def gj(name):
    d = json.load(open(os.path.join(HERE, 'tools/data', name + '.geojson')))
    fs = d['features'] if 'features' in d else [d]
    return unary_union([shape(f.get('geometry', f)).buffer(0) for f in fs])
BASE = MP(json.load(open(os.path.join(HERE, 'tools/data/v362_base_v356_grm.json')))['polys'])
V5, V4 = M('grm'), M('sas')
print('base (Version 356 V5)', round(A(BASE)), '| current V5 outside the base', round(A(V5.difference(BASE))), '| V4 outside the base', round(A(V4.difference(BASE))))
CN = {n: gj(n) for n in ['v9_east_turkestan_v218', 'greater_tibet_v222', 'tibetan_plateau_3000m', 'v5_tibet_plateau277', 'china_kashmir_ne']}
IDS = {'104': 'Myanmar', '764': 'Thailand', '418': 'Laos', '704': 'Vietnam', '116': 'Cambodia', '458': 'Malaysia', '702': 'Singapore', '096': 'Brunei', '360': 'Indonesia',
       '608': 'Philippines', '626': 'Timor-Leste', '598': 'Papua New Guinea', '090': 'Solomon Is.', '548': 'Vanuatu', '242': 'Fiji', '540': 'New Caledonia',
       '356': 'India', '524': 'Nepal', '064': 'Bhutan', '050': 'Bangladesh', '144': 'Sri Lanka', '462': 'Maldives'}
for k, n in IDS.items(): assert G[k][0] == n, (k, G[k][0], n)
WORLD = box(-180, -90, 180, 90)
grow = lambda g: g.buffer(0.002).intersection(WORLD)   # closes hairline seams against the base; never past the date line (Fiji)
parts = [BASE, V5, V4] + [grow(g) for g in CN.values()] + [grow(G[k][1]) for k in IDS]
X = unary_union(parts).buffer(0)
run = BASE
for n, g in list(CN.items()) + [(IDS[k], G[k][1]) for k in IDS]:
    a = A(g.difference(run))
    if a >= 1: print('  +', n, round(a), 'km2')
    run = unary_union([run, g])
o = polys(X, 0.02); Y = MP(o)
for p in o:
    for h in p[1:]:
        H = Polygon(h); c = H.representative_point(); print('  hole kept:', round(A(H)), 'km2 at', round(c.x, 1), round(c.y, 1))
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C.get('sup', {}).get('km2'); C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup (Super Caliphate)', old, '->', C['sup']['km2'], '| pieces', len(o))
print('partly inside:', ', '.join('%s %d%%' % (r['n'], r['pct']) for r in C['sup']['states'] if r['pct'] < 99))
T = {'Urumqi': (87.6, 43.8), 'Kashgar': (75.99, 39.47), 'Dunhuang': (94.66, 40.14), 'Lhasa': (91.1, 29.65), 'Xining': (101.8, 36.6), 'Garze': (100.0, 31.6), 'Aksai Chin': (79.5, 35.2),
     'Srinagar': (74.8, 34.08), 'Delhi': (77.2, 28.6), 'Colombo': (79.86, 6.93), 'Male': (73.51, 4.17), 'Diego Garcia': (72.42, -7.32), 'Yangon': (96.17, 16.84), 'Bangkok': (100.5, 13.75),
     'Vientiane': (102.6, 17.97), 'Hanoi': (105.84, 21.03), 'Phnom Penh': (104.92, 11.56), 'Kuala Lumpur': (101.69, 3.14), 'Singapore': (103.82, 1.35), 'Bandar Seri Begawan': (114.94, 4.9),
     'Jakarta': (106.83, -6.2), 'Jayapura': (140.7, -2.55), 'Manila': (121.0, 14.6), 'Dili': (125.57, -8.56), 'Port Moresby': (147.19, -9.45), 'Rabaul (Bismarck)': (152.16, -4.21),
     'Honiara': (159.97, -9.44), 'Santa Cruz (Nendo)': (165.9, -10.72), 'Port Vila': (168.32, -17.74), 'Suva': (178.44, -18.12), 'Taveuni (east of 180)': (-179.95, -16.85), 'Noumea': (166.46, -22.26),
     'Rostov (base)': (39.72, 47.23), 'Krasnodar (base bridge)': (38.98, 45.04), 'Chengdu (out)': (104.07, 30.66), 'Kunming (out)': (102.7, 25.04), 'Taipei (out)': (121.5, 25.03), 'Darwin (out)': (130.84, -12.46), 'Ulaanbaatar (out)': (106.9, 47.9)}
for n_, p in T.items(): print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(V5.difference(Y.buffer(0.01)))), '| sas outside sup', round(A(V4.difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
