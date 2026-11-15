"""Version 452 (Nawaz, after Wikipedia's Nile article: V1 lacked the White Nile above Nimule and the Lake Victoria sources -> "Preview").
V1 (shj) takes the rest of the Nile basin's countries and lake shores: Uganda, Rwanda and Burundi whole (the White Nile from Lake Victoria through Kyoga
and Albert, the Kagera sources); Kenya's Lake Victoria provinces (Nyanza, Western) and Tanzania's Lake Victoria regions (Kagera, Mwanza, Geita, Mara,
Simiyu, Shinyanga), Natural Earth admin-1 lines; and the DR Congo shore of Lake Albert that V2 holds (the Version 150 strip). Real borders kept, nothing
roughened. Needs the Natural Earth admin-1 file (env NE_ADMIN1). DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
AD = json.load(open(os.environ['NE_ADMIN1']))
REG = {'KEN': ['Nyanza', 'Western'], 'TZA': ['Kagera', 'Mwanza', 'Geita', 'Mara', 'Simiyu', 'Shinyanga']}
R = unary_union([shape(f['geometry']).buffer(0) for f in AD['features'] if f['properties'].get('name') in REG.get(f['properties'].get('adm0_a3'), [])])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys']); V2 = MP(C['me2']['polys'])
KT = unary_union([G['Kenya'], G['Tanzania']]).buffer(0.01)
DRC = V2.intersection(G['DR Congo']).intersection(box(29.5, 0.5, 31.5, 3.0))
NEW = unary_union([G['Uganda'], G['Rwanda'], G['Burundi'], R.intersection(KT), DRC]).buffer(0)
print('new land', round(A(NEW.difference(V))), 'km2 | DRC Lake Albert strip', round(A(DRC)), 'km2')
X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000 and Polygon(h).representative_point().x > 20]
X = unary_union([X] + holes).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); rws = []
for f in geo['features']:
    if not f.get('geometry'): continue
    g_ = G[f['properties']['n']]
    if g_.area and g_.intersects(Y):
        pct = round(100 * g_.intersection(Y).area / g_.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g_)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km)
FR = json.load(open(os.path.join(P, 'src/four_rivers.json'))); r = [x for x in FR['rivers'] if x['k'] == 'nile'][0]
from shapely.geometry import LineString, MultiLineString
Lr = MultiLineString([LineString(p) for p in r['parts'] if len(p) > 1])
print('Nile (traced, all branches) inside V1 %', round(100 * Lr.intersection(Y.buffer(0.01)).length / Lr.length, 1))
for n_, p in {'Kampala': (32.58, 0.35), 'Jinja (Nile source)': (33.2, 0.42), 'Kigali': (30.06, -1.95), 'Bujumbura': (29.36, -3.38), 'Kisumu': (34.75, -0.1), 'Mwanza': (32.9, -2.52), 'Bukoba (Kagera)': (31.81, -1.33), 'Lake Victoria centre': (33.0, -1.0), 'Lake Albert': (31.2, 1.7), 'Nairobi (out)': (36.82, -1.29), 'Juba': (31.58, 4.85)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
