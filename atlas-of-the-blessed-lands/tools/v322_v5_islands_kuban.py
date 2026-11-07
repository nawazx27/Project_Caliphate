"""Version 322 (Nawaz: "Now, Does v5 have all the lands that the Roman Empire ever held?" -> "Are you sure?" -> 52 more sites checked:
three Roman lands outside: the Channel Islands, the Isles of Scilly, and the Kuban fringe of the Bosporan client kingdom round
Krasnodar -> "Preview" -> "Are you sure?" -> the DARE provinces of 117 showed the Breton/Vendee islands (Belle-Ile, Yeu, Ouessant,
Sein) and a strip of Noricum north of the Danube at Linz outside -> "Add everything left out"). Also: all of metropolitan France and
all of Austria (Muehlviertel), every country V5 holds 100% taken whole again (coastal specks; the Netherlands in Europe only). (The Tuapse coast is NOT added: it would close the central Kuban plain into a pocket.) V5 (grm) takes Jersey and Guernsey (with Alderney and Sark) from the base map (832, 831) and Overture (with Sark and Herm), the Isles of Scilly
and the Krasnodar Krai districts between the lower Kuban and the coast up to Krasnodar (Krasnodar city, Dinskoy, Seversky, Abinsky,
Gelendzhik; Overture, tools/data/v322_kuban_scilly.parquet). Pockets >=80% filled; V6 (v2) takes any V5 land it lacks."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
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
KUBAN = {'городской округ Краснодар', 'Динской район', 'Северский район', 'Абинский район', 'городской округ Геленджик'}   # the Tuapse coast was tried and left out: it closes a 34,000 km2 pocket of the central Kuban plain (Maykop, Kropotkin, Tikhoretsk)
rows = [r for r in pq.read_table(os.path.join(P, 'tools/data/v322_kuban_scilly.parquet')).to_pylist() if r['is_land'] is not False]
K = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['name'] in KUBAN])
SC = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['name'] == 'Isles of Scilly'])
CI = unary_union([G['832'][1], G['831'][1]] + [shapely.from_wkb(r['geometry']).buffer(0) for r in rows if r['subtype'] == 'dependency'])   # Overture Jersey and Guernsey with Alderney, Sark, Herm
V5 = M('grm')
fr = [k for k, (n, g) in G.items() if n == 'France'][0]
WH = [G[fr][1].intersection(box(-6, 41, 10, 52)), G['040'][1]]          # mainland France with its islands, all of Austria
for r in C['grm']['states']:
    if r['pct'] >= 100 and r['id'] in G:
        g = G[r['id']][1]
        if r['n'] == 'Netherlands': g = g.intersection(box(2, 50, 8, 54))
        WH.append(g)
W = unary_union(WH)
print('whole France/Austria/held countries add', round(A(W.difference(V5))), 'km2')
for n, g in [('Channel Islands', CI), ('Isles of Scilly', SC), ('Kuban fringe', K)]: print(n, 'adds', round(A(g.difference(V5))), 'km2')
X = unary_union([V5, CI.buffer(0.002), SC.buffer(0.002), K.buffer(0.003), W.buffer(0.001)]).buffer(0)
win = box(36, 43.5, 41, 46.5); L = unary_union([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 0.5: continue
    if q.exterior.intersection(XB).length / q.exterior.length >= 0.8: fill.append(q)
X = unary_union([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('pockets filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'St Helier (Jersey)': (-2.1, 49.19), 'St Peter Port (Guernsey)': (-2.54, 49.46), 'Alderney': (-2.2, 49.71), 'Sark': (-2.36, 49.43), 'Scilly (St Mary\'s)': (-6.3, 49.92), 'Krasnodar': (38.98, 45.04), 'Abinsk': (38.15, 44.87), 'Gelendzhik': (38.06, 44.56), 'Goryachy Klyuch': (39.13, 44.63), 'Tuapse': (39.07, 44.1), 'Belle-Ile': (-3.21, 47.34), 'Ile d\'Yeu': (-2.33, 46.71), 'Ouessant': (-5.08, 48.46), 'Linz north bank (Urfahr)': (14.29, 48.32), 'Freistadt (Muehlviertel)': (14.5, 48.51)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(unary_union([V, Y.buffer(0.003)]).buffer(0), 0.02)
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
