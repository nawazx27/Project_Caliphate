"""Version 321 (Nawaz: "Now, Does v5 have all the lands that the Roman Empire ever held?" -> every Roman site in, but a corner of western
Czechia round Cheb on both his Roman-rule maps lay outside (left by Version 316's Saale-Naab river line) -> the sharper map again: "Cover").
V5 (grm) takes all land of both traced Roman maps (tools/data/v5_roman_map305.geojson, tools/data/v315_roman_map_hires_shape.geojson)
that it lacks; cut towns (Overture city/town) are not split: the corner is closed by smoothing the edge 0.05 deg; pockets >=80% filled.
V6 (v2) takes any V5 land it lacks."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
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
maps = []
for f in ['tools/data/v5_roman_map305.geojson', 'tools/data/v315_roman_map_hires_shape.geojson']:
    d = json.load(open(os.path.join(P, f))); maps.append(shape(d['geometry'] if 'geometry' in d else d['features'][0]['geometry']).buffer(0))
O = unary_union(maps)
L = unary_union([g for n, g in G.values() if g.intersects(O)])
V5 = M('grm'); miss = O.intersection(L).difference(V5)
add = [q for q in getattr(miss, 'geoms', [miss]) if q.geom_type == 'Polygon' and A(q) > 0.5]
for q in sorted(add, key=A, reverse=True)[:6]:
    p = q.representative_point(); print('  + %6d km2 at %.2f %.2f %s' % (A(q), p.x, p.y, [n for n, g in G.values() if g.contains(p)][:1]))
NEW = unary_union(add)
Z = NEW.buffer(0.1)                                              # smooth the new edge locally, never past real land
X = unary_union([V5, NEW.buffer(0.003)]).buffer(0)
X = unary_union([X, X.intersection(Z).buffer(0.05).buffer(-0.05).intersection(L)]).buffer(0)
win = box(9, 47, 16, 52); Lw = unary_union([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = Lw.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 0.5: continue
    if q.exterior.intersection(XB).length / q.exterior.length >= 0.8: fill.append(q)
X = unary_union([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('pockets filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
print('map land still outside V5:', round(A(O.intersection(L).difference(Y.buffer(0.005)))), 'km2')
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Cheb': (12.37, 50.08), 'Marianske Lazne': (12.7, 49.96), 'Karlovy Vary': (12.87, 50.23), 'Plzen': (13.38, 49.75), 'Hof': (11.92, 50.31)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(unary_union([V, Y.buffer(0.003)]).buffer(0), 0.02)
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
