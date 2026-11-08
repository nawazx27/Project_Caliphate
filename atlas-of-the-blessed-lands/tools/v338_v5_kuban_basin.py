"""Version 338 preview step (Nawaz: "Are you sure?" -> the peoples in the Bosporan kings' titles (Psessians, Thateans...) may have lived
further up the Kuban -> "Sure"). After tools/v337_v5_client_lands.py, V5 (grm) takes all of Krasnodar Krai and Adygea (the whole lower
and middle Kuban basin: Maykop, Kropotkin, Armavir, Tikhoretsk, Goryachy Klyuch; Overture regions, tools/data/v338_kuban_adygea.parquet).
No pocket filling."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
K = shapely.union_all([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(P, 'tools/data/v338_kuban_adygea.parquet')).to_pylist() if r['is_land']])
V5 = M('grm'); print('Kuban basin adds', round(A(K.difference(V5))), 'km2')
X = shapely.union_all([V5, K.buffer(0.003)]).buffer(0)
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
for n_, p in {'Maykop': (40.1, 44.6), 'Kropotkin': (40.57, 45.44), 'Armavir': (41.12, 45.0), 'Goryachy Klyuch': (39.13, 44.63), 'Tuapse': (39.07, 44.1), 'Stavropol': (41.97, 45.04), 'Cherkessk': (42.05, 44.22)}.items(): print('  ', n_, Y.contains(Point(p)))
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
