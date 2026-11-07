"""Version 324 (Nawaz circled northern/eastern Slovakia and the Ostrava area on Version 323: "Is this area a part of Roman empire" -> no
(Barbaricum north of the Danube; only western Slovakia had Marcomannic-war forts and camps) -> "Sure").
In 16.9-23.0 E, 47.0-50.6 N V5 (grm) goes back to its Version 319 shape (the Roman Marcomannic-war lands + the 1683 Ottoman line, which
keeps the Ottoman Hungarian plain) plus the Olomouc and Zlin regions (the Roman marching camps at Olomouc-Neredin and Hulin). Out: the
Moravian-Silesian region (Ostrava), the Zilina, Banska Bystrica, Presov and Kosice regions, and NE Hungary beyond the 1683 line.
V6 (v2) unchanged (it holds more).
Usage: python3 tools/v324_v5_roman_ottoman_north.py <caliph.json of Version 319, from: git show 7a52f0f:./src/caliph.json>"""
import json, os, sys, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_)); OLD = json.load(open(sys.argv[1]))
M = lambda C, k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
B = box(16.9, 47.0, 23.0, 50.6)
rows = pq.read_table(os.path.join(P, 'tools/data/v319_cz_at_regions.parquet')).to_pylist()
CAMPS = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['subtype'] == 'region' and r['is_land'] is not False and r['region'] in ('CZ-71', 'CZ-72')])
Yn, Yo = M(C, 'grm'), M(OLD, 'grm')
NEWB = unary_union([Yo.intersection(B), CAMPS.intersection(B).buffer(0.003)])
print('removed', round(A(Yn.intersection(B).difference(NEWB))), 'km2; added', round(A(NEWB.difference(Yn))), 'km2')
X = unary_union([Yn.difference(B), NEWB]).buffer(0)
X = shapely.set_precision(X, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Olomouc camp': (17.22, 49.6), 'Hulin camp': (17.46, 49.32), 'Trencin (Laugaricio)': (18.04, 48.89), 'Iza': (18.2, 47.75), 'Bratislava': (17.11, 48.145), 'Nitra': (18.09, 48.31), 'Ostrava': (18.29, 49.82), 'Zilina': (18.74, 49.22), 'Banska Bystrica': (19.15, 48.74), 'Kosice': (21.26, 48.72), 'Presov': (21.24, 49.0), 'Budapest': (19.04, 47.5), 'Eger': (20.38, 47.9), 'Miskolc': (20.78, 48.1), 'Debrecen': (21.63, 47.53), 'Szeged': (20.15, 46.25), 'Nyiregyhaza': (21.72, 47.95)}.items(): print('  ', n_, Y.contains(Point(p)))
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(C, a).difference(M(C, b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
