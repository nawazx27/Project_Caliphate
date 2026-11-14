"""Version 414 PREVIEW (Nawaz, with the Wikipedia map "The Egyptian Empire, 15th century BC": "Preview with the whole map"). As tools/v413_v1_egypt_map.py, but V1 (shj)
gets the union of his olive Egypt map (tools/data/v413_egypt.geojson) and the whole Egyptian Empire map (both greens, tools/data/v414_egyptian_empire.geojson, traced by
tools/v414_egyptian_empire_check.py), clipped to land, coasts to the sea, kept inside V3. Then rerun tools/v411_arabia.py. Run v386_areas_ellipsoid.py after."""
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
SOUTH = float(os.environ.get('SOUTH', '24.03'))   # the First Cataract at Aswan (between Aswan and the old dam, ~24.03 N)
EG = [g for k, (n, g) in G.items() if n == 'Egypt'][0]
LAND = unary_union([g for k, (n, g) in G.items()]).buffer(0)
TR_ = unary_union([shape(json.load(open(os.path.join(HERE, 'tools/data/' + f + '.geojson')))['geometry']).buffer(0) for f in os.environ.get('TRACES', 'v414_egyptian_empire').split(',')])   # Nawaz: "I want exactly this outline": the Egyptian Empire map alone (TRACES=v413_egypt,v414_egyptian_empire gives the earlier union)   # his olive map + the whole 15th-century-BC Egyptian Empire map
SEA = shapely.box(20, 10, 45, 36).difference(LAND)
CB = float(os.environ.get('COAST', '0.12')); COAST = unary_union([TR_.buffer(CB).difference(TR_).intersection(LAND).intersection(SEA.buffer(CB)), TR_.buffer(0.4).difference(TR_).intersection(LAND).intersection(SEA.buffer(0.4)).intersection(shapely.box(24, 22.0, 37, 32))])   # in Egypt (north of 22 N) the map's green runs to the sea on both coasts, so the land is taken to the sea there; in Sudan its edge stays inland   # only where the map's edge is the sea (fit error ~20 km)   # the map is stylised: on the coasts, the land is taken to the sea
NEW = unary_union([TR_, COAST]).intersection(LAND)
print('   traced', round(A(TR_.intersection(LAND))), 'km2; coastal strips', round(A(COAST)), 'km2; land outside V3 (dropped to keep the nesting)', round(A(NEW.difference(MP(C['me2']['polys']).buffer(0.01)))), 'km2')
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
print('   Egypt of his map', round(A(NEW)), 'km2; new to V1', round(A(NEW.difference(V))))
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
B_ = shapely.box(24, 15, 38.5, 32); LEFT = LAND.intersection(B_).difference(X)   # small strips left between the traced edge and the Red Sea coast (or wholly enclosed): filled
for q in getattr(LEFT, 'geoms', [LEFT]):
    if q.area and A(q) < 5000 and q.representative_point().y > 15.5 and q.buffer(0.02).intersects(X):
        print('     coastal strip filled:', round(A(q)), 'km2 at', [round(c, 2) for c in q.representative_point().coords[0]]); X = unary_union([X, q.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x < 36]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
def polys_lakes(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
o = polys_lakes(unary_union([X] + holes).buffer(0).intersection(V3.buffer(0.002))); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Cairo': (31.24, 30.04), 'Alexandria': (29.92, 31.2), 'Luxor': (32.64, 25.69), 'Aswan': (32.9, 24.09), 'Siwa': (25.52, 29.2), 'Kharga': (30.55, 25.44), 'Dakhla (Mut)': (28.98, 25.49), 'Hurghada': (33.81, 27.26), 'Marsa Alam': (34.89, 25.07), 'Marsa Matruh': (27.24, 31.35), 'Abu Simbel': (31.63, 22.34), 'Berenice': (35.48, 23.95), 'Wadi Halfa': (31.35, 21.8), 'Dongola': (30.48, 19.17), 'Napata (Karima)': (31.83, 18.53), 'Meroe': (33.75, 16.94), 'Khartoum': (32.53, 15.6), 'Farafra': (27.97, 27.06), 'Sixth Cataract (Sabaloka)': (32.67, 16.33), 'Kadesh': (36.52, 34.56), 'Carchemish': (38.02, 36.83), 'Port Sudan': (37.22, 19.62), 'Atbara': (33.99, 17.7)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('modern Egypt left out', round(A(EG.difference(Y))), 'km2 | shj outside me2', round(A(Y.difference(V3.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
