"""Version 334 preview (Nawaz: "By going back to Georgia's political border, do we lose any Roman land?" -> middle way offered ->
"Preview"). In the Caucasus band (37.9-50 E, 41-44.3 N) V5's Russian land is cut back to the Georgian/Azerbaijani political border,
EXCEPT the two places with a Roman client claim: the Sochi-Adler coast (Sochi and Sirius districts; the Sanigae, whose king Hadrian
appointed, Arrian Periplus 11) and southern Dagestan to Derbent (Caucasian Albania's north; tools/data/derbent_south_dagestan249.geojson).
The north slope (Kabardino-Balkaria, North Ossetia, Ingushetia, Chechnya, inland Dagestan above the crest) goes out.
Run with PLAIN=1 to drop the two exceptions too (the plain political border)."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
GI = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
V5 = M('grm'); B = box(39.0, 41.0, 50.0, 44.3)
cut = G['Russia'].intersection(B)
keep = []
if not os.environ.get('PLAIN'):
    rows = pq.read_table(os.path.join(P, 'tools/data/v322_kuban_scilly.parquet')).to_pylist()
    keep.append(unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['name'] in ('городской округ Сочи', 'городской округ Сириус') and r['is_land'] is not False]))
    keep.append(unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/derbent_south_dagestan249.geojson')))['features']]))
K = unary_union(keep) if keep else Polygon()
REM = cut.difference(K.buffer(0.003)).difference(M('sas').buffer(0.003))   # never cut V4's own land (its Derbent/Rutul block)
print('removed', round(A(V5.intersection(REM))), 'km2; kept as Roman-client exceptions', round(A(V5.intersection(K))), 'km2')
X = V5.difference(REM.buffer(0.002)).buffer(0)
X = shapely.union_all([q for q in getattr(X, 'geoms', [X]) if q.geom_type == 'Polygon' and A(q) > 0.5]).buffer(0)
X = shapely.set_precision(X, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rws = []
for k, (n, g) in GI.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Sochi': (39.72, 43.6), 'Adler': (39.92, 43.43), 'Krasnaya Polyana': (40.2, 43.68), 'Derbent': (48.29, 42.06), 'Akhty': (47.73, 41.46), 'Nalchik': (43.61, 43.49), 'Vladikavkaz': (44.68, 43.02), 'Pityus': (40.34, 43.16), 'Tbilisi': (44.79, 41.72), 'Darial (Georgian side)': (44.63, 42.70)}.items(): print('  ', n_, Y.contains(Point(p)))
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
