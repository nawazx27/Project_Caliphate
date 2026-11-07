"""Version 323 (Nawaz, ticking the Version 321 Kuban on the before/after picture, reference/v323_kuban_back.jpg: "Take it back to this
and push"). In the Kuban (36-41 E, 43.5-46.5 N) V5 (grm) goes back to its Version 321 shape: the straight edge from the Don to
Novorossiysk, no Krasnodar, Abinsk, Gelendzhik districts, no Tuapse coast. Everything else of Version 322 stays (Channel Islands,
Scilly, Breton islands, all of Austria). V6 unchanged (it holds more).
Usage: python3 tools/v323_v5_kuban_back.py <caliph.json of Version 321, from: git show 42df178:./src/caliph.json>"""
import json, os, sys, subprocess, shapely
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
B = box(36, 43.5, 41, 46.5)
Yn, Yo = M(C, 'grm'), M(OLD, 'grm')
print('removed', round(A(Yn.intersection(B).difference(Yo))), 'km2; put back', round(A(Yo.intersection(B).difference(Yn))), 'km2')
X = unary_union([Yn.difference(B), Yo.intersection(B)]).buffer(0)
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
print('Kuban area now equals Version 321:', round(A(Y.intersection(B).symmetric_difference(Yo.intersection(B)))), 'km2 different')
for n_, p in {'Krasnodar': (38.98, 45.04), 'Abinsk': (38.15, 44.87), 'Gelendzhik': (38.06, 44.56), 'Novorossiysk': (37.77, 44.72), 'Anapa': (37.32, 44.89), 'Jersey': (-2.1, 49.19), 'Belle-Ile': (-3.21, 47.34), 'Freistadt': (14.5, 48.51)}.items(): print('  ', n_, Y.contains(Point(p)))
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(C, a).difference(M(C, b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
