"""Version 346 PREVIEW (Nawaz: "Are you sure about these and whatever is outside?" -> Gelendzhik (ancient Torik, land of the Toretae,
named among the Bosporan kings' subjects in the 4th century BC) is the one close call on the Roman outside list -> "Preview").
V5 (grm) takes Gelendzhik urban okrug: the Toretae coast round Gelendzhik Bay from Kabardinka to Arkhipo-Osipovka (Overture,
tools/data/v322_kuban_scilly.parquet), and -> "Fill" (his red line on the preview, from the Don-Novorossiysk line at ~38.34E 45.06N
south-east to ~38.75E 44.53N): the land between that line, the old straight line and the Gelendzhik district, so the hinterland of
Novorossiysk and Gelendzhik closes up. Evidence: the Roman watchtower near Arkhipo-Osipovka (1st century AD, second third; Gallo-Roman
helmet cheek-piece; burned when the garrison left c. AD 68; Bonin and Meleshko). Tuapse (Zichian client coast) and the Kuban interior
are NOT added."""
import json, os, subprocess, shapely
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
import pyarrow.parquet as pq
FILL = Polygon([(38.34, 45.06), (38.43, 44.95), (38.56, 44.82), (38.67, 44.68), (38.75, 44.53), (38.69, 44.49), (38.2, 44.6), (37.9, 44.9), (38.2, 45.15)]).intersection(G['643'][1])   # his red line
POD0 = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(P, 'tools/data/v322_kuban_scilly.parquet')).to_pylist() if r['name'] == 'городской округ Геленджик' and r['is_land'] is not False])
POD = unary_union([POD0, FILL])
V5 = M('grm'); print('Gelendzhik (Toretae coast) adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Gelendzhik': (38.06, 44.56), 'Kabardinka': (37.92, 44.65), 'Divnomorskoye': (38.13, 44.50), 'Arkhipo-Osipovka': (38.53, 44.37), 'Roman tower (Arkhipo-Osipovka)': (38.55, 44.39), 'Krymsk (inside already)': (37.98, 44.93), 'Nizhnebakanskaya (filled)': (37.86, 44.86), 'Shapsugskaya (filled)': (38.42, 44.82), 'Tuapse (stays out)': (39.07, 44.10), 'Krasnodar (stays out)': (38.98, 45.04)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
