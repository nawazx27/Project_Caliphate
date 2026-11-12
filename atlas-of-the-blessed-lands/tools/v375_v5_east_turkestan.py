"""Version 375 PREVIEW (Nawaz: "Add east turkestan preview v5"; then "Add greater Tibet and the entire Tibetan plateau to the preview": also Greater Tibet (tools/data/greater_tibet_v222.geojson), the whole plateau above 3000 m (tools/data/tibetan_plateau_3000m.geojson) and its edge counties (tools/data/v5_tibet_plateau277.geojson), as V6 holds them). V5 (grm) takes East Turkestan exactly as V6 holds it (Version 362): the shape saved in
tools/data/v9_east_turkestan_v218.geojson (Xinjiang without Aksai Chin, with the edges of western Gansu and Qinghai: its government in
exile's definition). Preview only; DIR env = project dir (preview: a copy)."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
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
def gj(n):
    d = json.load(open(os.path.join(HERE, 'tools/data/' + n + '.geojson'))); fs = d['features'] if 'features' in d else [d]
    return unary_union([shape(f.get('geometry', f)).buffer(0) for f in fs])
PARTS = {n: gj(n) for n in ['v9_east_turkestan_v218', 'greater_tibet_v222', 'tibetan_plateau_3000m', 'v5_tibet_plateau277']}
_V = MP(C['grm']['polys']); _run = _V
for n, g in PARTS.items():
    print('  +', n, round(A(g.difference(_run))), 'km2'); _run = unary_union([_run, g])
ET = unary_union(list(PARTS.values()))
V5 = MP(C['grm']['polys']); a = ET.difference(V5)
print('  + all four', round(A(a)), 'km2 | bounds', [round(v, 1) for v in ET.bounds])
X = unary_union([V5, ET.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Urumqi': (87.6, 43.8), 'Kashgar': (75.99, 39.47), 'Hotan': (79.92, 37.11), 'Turpan': (89.19, 42.95), 'Kuqa': (82.96, 41.72), 'Yining (Ili)': (81.33, 43.92), 'Dunhuang': (94.66, 40.14),
              'Aksai Chin': (79.5, 35.2), 'Lhasa': (91.1, 29.65), 'Shigatse': (88.88, 29.27), 'Nagqu': (92.05, 31.48), 'Qamdo (Kham)': (97.17, 31.14), 'Golmud': (94.9, 36.4), 'Yushu': (97.0, 33.0), 'Kangding': (101.96, 30.05), 'Labrang (Xiahe)': (102.5, 35.2), 'Zoige': (102.97, 33.58), 'Shangri-La (Yunnan)': (99.7, 27.83), 'Zhangye (Qilian)': (100.45, 38.93), 'Xining (out)': (101.8, 36.6), 'Lanzhou (out)': (103.8, 36.06), 'Jiuquan (out?)': (98.5, 39.74)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(MP(C['sas']['polys']).difference(Y.buffer(0.01)))), '| grm outside sup', round(A(Y.difference(MP(C['sup']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
