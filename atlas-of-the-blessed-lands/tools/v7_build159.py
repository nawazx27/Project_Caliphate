"""Version 159 (2026-10-17, Nawaz after the peninsula/plateau coverage table: "take those in and build upon v2 and make v7 with the new
changes and leave v2 and v2b alone... and you said Balkan is 99% fill that 1 percent in v2").
 1. V2 only: the 1% of the Balkan Peninsula that V2 lacked (Natural Earth's BALKAN PEN. region on land minus V2: Dobruja and the Danube
    delta, the Danube's banks at the Iron Gates, the top of Slovenia, and thin strips; ~5,000 km2) is filled. V2-B is left alone.
 2. V7 (CALIPH.x7) = V2 (with that fill) plus whole physical regions of Natural Earth's regions layer, each cut to the coast only (never to
    countries): the Himalayas, the Vale of Kashmir, the Deccan Plateau, the Sahara and the whole Libyan Desert. Written to tools/data/v7_lands159.geojson (the added lands).
Run: python3 tools/v7_build159.py   (writes src/caliph.json: x filled, x7 created)"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
mk = lambda polys: MultiPolygon([Polygon(r[0], r[1:]) for r in polys]).buffer(0)
reg = {f['properties']['NAME']: shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'regions.geojson')))['features']}
find = lambda s: [g for n, g in reg.items() if n.upper().startswith(s.upper())]
def pack(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out): return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
X = mk(C['x']['polys'])
bp = find('BALKAN PEN')[0].intersection(land)
miss = bp.difference(X)
print('Balkan fill', round(A(miss)), 'km2')
X = shapely.union_all([shapely.make_valid(X), shapely.make_valid(miss.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
C['x']['polys'] = pack(X); C['x']['km2'] = km2(C['x']['polys']); print('V2 now', C['x']['km2'])
adds = {}
for nm, key in [('Himalayas', 'HIMALAYAS'), ('Vale of Kashmir', 'Vale of Kashmir'), ('Deccan Plateau', 'DECCAN PLATEAU'), ('Sahara', 'SAHARA'), ('Libyan Desert', 'LIBYAN DESERT')]:
    g = unary_union(find(key)).intersection(land).buffer(0)
    new = g.difference(X); adds[nm] = new; print(nm, 'adds', round(A(new)), 'km2 of', round(A(g)))
add = unary_union(list(adds.values()))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 159, V7 lands', 'parts': {k: round(A(v)) for k, v in adds.items()}}, 'geometry': mapping(add)}]}, open(os.path.join(D, 'v7_lands159.geojson'), 'w'))
X7 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
C['x7'] = {'polys': pack(X7)}; C['x7']['km2'] = km2(C['x7']['polys'])
print('V7', C['x7']['km2'])
import copy   # per-country rows for what V7 adds
NM = {'356': ('India', 'the Himalayas, the Vale of Kashmir and the Deccan Plateau'), '156': ('China', 'the Himalayas'), '504': ('Morocco', 'the Sahara'), '732': ('Western Sahara', 'the Sahara'), '064': ('Bhutan', 'the Himalayas'), '140': ('Central African Republic', 'the edge of the Sahara and of the Libyan Desert'), '466': ('Mali', 'the Sahara'), '686': ('Senegal', 'the edge of the Sahara'), '566': ('Nigeria', 'the edge of the Sahara'), '148': ('Chad', 'the Sahara and the rest of the Libyan Desert'), '012': ('Algeria', 'the Sahara'), '524': ('Nepal', 'the Himalayas'), '120': ('Cameroon', 'the edge of the Sahara'), '562': ('Niger', 'the Sahara'), '854': ('Burkina Faso', 'the edge of the Sahara'), '478': ('Mauritania', 'the Sahara'), '818': ('Egypt', 'the rest of the Libyan Desert'), '434': ('Libya', 'the rest of the Libyan Desert'), '729': ('Sudan', 'the rest of the Libyan Desert')}
rows = []
for f in geo['features']:
    i = str(f['id']); g = shape(f['geometry']).buffer(0); a = add.intersection(g)
    if a.is_empty or A(a) < 20: continue
    c, w = NM.get(i, (i, 'the added lands'))
    rows.append({'id': '7_' + i, 'n': '%s: %s, as V7 adds %s' % (c, w, 'it' if i in ('818', '434', '729') else 'them'), 'km2': round(A(a)), 'pct': round(A(a) / A(g) * 100, 1)})
C['x7']['states'] = copy.deepcopy([r for r in C['x']['states']]) + rows
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
