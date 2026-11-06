"""Version 303 (Nawaz, phone screenshot with the Czechia/southern-Poland gap circled: "Fill this and remove Crimean Peninsula and just
add Crimea." ... "complete the task").
1. V5 (grm) + Czechia whole + the southern Polish voivodeships south of a line from Gorlitz (Saxony's NE corner) to Ukraine's NW corner
   on the Bug: Dolnoslaskie, Opolskie, Slaskie, Malopolskie, Podkarpackie, Swietokrzyskie, Lubelskie (Overture 2026-10-21.0 regions,
   tools/data/v303_pl_cz_regions.parquet); pockets >=80% filled.
2. Crimea only: around the Crimean peninsula V5 keeps just base-map Ukraine and the Crimea + Sevastopol regions (land); Taman and the
   Version 302 Sivash/Arabat pocket fills outside them are removed.
3. V6 (rom) and V7 (v2) take any V5 land they lack. Usage: python3 tools/v303_v5_czpl_crimea.py <crimea.pkl> <Overture divs.parquet with Temryuk district>"""
import json, os, sys, subprocess, pickle, shapely
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point
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
def polys(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
PLW = {'Woj Dolnoslaskie', 'Woj Opolskie', 'Woj Śląskie', 'Woj Małopolskie', 'Woj Podkarpackie', 'Woj Świętokrzyskie', 'Woj Lubelskie'}
R = [(r['country'], (r['names'] or {}).get('primary'), wkb.loads(r['geometry']).buffer(0)) for r in pq.read_table(os.path.join(P, 'tools/data/v303_pl_cz_regions.parquet')).to_pylist()]
add = [g for c, n, g in R if c == 'CZ' or n in PLW] + [G['203'][1]]
X = shapely.union_all([M('grm')] + [g.buffer(0.003) for g in add]).buffer(0)
# Crimea only
CB = box(32.3, 44.2, 37.0, 46.4)
land = shapely.union_all([g for n, g in G.values() if g.intersects(CB)])
crimea = shapely.union_all([wkb.loads(g).buffer(0) for c, n, g in pickle.load(open(sys.argv[1], 'rb'))]).intersection(land)
keep = shapely.union_all([crimea, G['804'][1]]).buffer(0.004)
X = shapely.union_all([X.difference(CB), X.intersection(CB).intersection(keep)]).buffer(0)
tam = shapely.union_all([wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(sys.argv[2]).to_pylist() if (r['names'] or {}).get('primary') == 'Темрюкский район'])
X = X.difference(tam.buffer(0.01).difference(G['804'][1])).buffer(0)   # all of Taman (Temryuk district) out
# pockets >=80% (Europe)
win = box(-12, 40, 42, 58); L = shapely.union_all([g for n, g in G.values() if g.intersects(win)]).intersection(win)
rest = L.difference(X); XB = X.buffer(0.05); fill = []
for q in getattr(rest, 'geoms', [rest]):
    if A(q) < 1 or q.intersects(CB): continue
    t = q.exterior.intersection(XB).length / q.exterior.length
    if t >= 0.5 and A(q) > 300: print(' pocket %d km2 %.0f%% at %s' % (A(q), 100 * t, tuple(round(v, 1) for v in q.representative_point().coords[0])))
    if t >= 0.8: fill.append(q)
X = shapely.union_all([X] + [q.buffer(0.003) for q in fill]).buffer(0); print('filled', len(fill), round(sum(A(q) for q in fill)))
o = polys(X, 0.05); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rows = {r['id']: r for r in C['grm']['states']}
for k in ['203', '616']:
    rows[k] = {'id': k, 'n': G[k][0], 'km2': round(A(G[k][1])), 'pct': round(100 * G[k][1].intersection(Y).area / G[k][1].area)}
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rows.values(), key=lambda r: -(r.get('km2') or 0) * (r.get('pct') or 100))}
print('grm', old, '->', C['grm']['km2'])
for n_, (x, y) in {'Prague': (14.42, 50.08), 'Krakow': (19.94, 50.06), 'Wroclaw': (17.03, 51.11), 'Lublin': (22.57, 51.25), 'Warsaw': (21.01, 52.23), 'Simferopol': (34.1, 44.95), 'Sevastopol': (33.52, 44.6), 'Kerch': (36.47, 45.36), 'Taman': (36.72, 45.21)}.items(): print(' ', n_, Y.contains(Point(x, y)))
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    o2 = polys(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0))
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
