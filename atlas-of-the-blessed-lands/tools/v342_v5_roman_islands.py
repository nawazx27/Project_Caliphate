"""Version 342 PREVIEW (Nawaz: "How to be sure of every bit of land held by the former Roman Empire across its entire history ...
check Wikipedia's, Britannica's, etc."). An audit against Pleiades (the gazetteer of the ancient world: 17,517 Roman-era places in
and around the Roman provinces, 3,377 forts, camps, stations and milestones) found the only Roman-held land outside V5 to be
small islands the base map does not draw (Capri, Delos and Rheneia, Levanzo, the Lerins islands, Montecristo, Fournoi, Leipsoi,
Arki, Therasia, Pseira and others). V5 (grm) takes, at full detail, every island of 0.1 to 5000 km2 that lies within ~30 km of the
Roman provinces of AD 117 (DARE), on the Frisian coast west of the Elbe, round Crimea and the Bosporus, on the Colchian coast and
at Farasan, and that V5 lacked or held less than 95% of: 722 islands (Overture 2026-10-21.0 country land;
tools/data/v342_roman_islands.parquet). Coastlines of the mainland and large islands stay as drawn."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
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
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
rows = pq.read_table(os.path.join(P, 'tools/data/v342_roman_islands.parquet')).to_pylist()
I = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows])
V5 = M('grm'); print(len(rows), 'islands add', round(A(I.difference(V5))), 'km2')
X = unary_union([V5, I.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Capri (Villa Iovis)': (14.262, 40.558), 'Delos': (25.268, 37.397), 'Rheneia': (25.213, 37.412), 'Levanzo': (12.339, 37.987),
              'Lerins (Saint-Honorat)': (7.047, 43.507), 'Montecristo': (10.302, 42.338), 'Fournoi': (26.479, 37.579), 'Leipsoi': (26.771, 37.296),
              'Arki fort': (26.734, 37.391), 'Therasia': (25.34, 36.452), 'Pseira': (25.86, 35.186), 'Dokos': (23.348, 37.346)}.items():
    print('  ', n_, Y.buffer(0.005).contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
