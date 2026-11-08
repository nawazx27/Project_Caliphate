"""Version 339 (Nawaz: "Does v5 have the entire British Isles" -> about ten small islands found missing, because the base map
does not draw them -> "just apply directly"). V5 (grm) takes, at full detail, every island of the United Kingdom and Ireland of
0.1 to 5000 km2 that it lacked or held less than 95% of: 480 islands (Overture 2026-10-21.0 country land of GB and IE;
tools/data/v339_british_isles_islands.parquet). Great Britain and the island of Ireland themselves are left as drawn.
Among them Foula, Out Skerries, Fetlar and other Shetland isles, North Ronaldsay and other Orkney isles, North Rona, many
Hebridean isles, Lundy, Rathlin, Tory, the Skelligs and Cape Clear. Rockall (a bare rock of under 0.001 km2, claimed by the UK and
not recognised by Ireland) is below the size limit and is not added."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
from shapely.geometry import MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
from shapely.geometry import shape
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
rows = pq.read_table(os.path.join(P, 'tools/data/v339_british_isles_islands.parquet')).to_pylist()
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
for n_, p in {'Lundy': (-4.67, 51.18), 'Rathlin': (-6.20, 55.29), 'Tory Island': (-8.23, 55.26), 'Skellig Michael': (-10.54, 51.77),
              'Cape Clear': (-9.50, 51.44), 'North Rona': (-5.82, 59.12), 'North Ronaldsay': (-2.42, 59.37), 'Foula': (-2.07, 60.14),
              'Out Skerries': (-0.76, 60.42), 'London': (-0.13, 51.51), 'Dublin': (-6.26, 53.35), 'Lerwick': (-1.15, 60.15)}.items():
    print('  ', n_, Y.buffer(0.01).contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
