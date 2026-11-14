"""Version 392 PREVIEW (Nawaz: "Preview option 3 in V6 preview"): the Sokoto Caliphate's own lands (1804-1903) in V6 (tib); V7 (sup) gets them too
so V6 stays inside V7; V5 is NOT changed. Lands: the 16 Nigerian states of Version 388 (Sokoto, Kebbi (Gwandu), Zamfara, Katsina, Kano, Jigawa, Kaduna (Zazzau),
Bauchi, Gombe, Adamawa (Yola), Taraba, Niger (Nupe), Kwara (Ilorin), Nasarawa, FCT, Plateau) PLUS the Cameroon side of the Adamawa emirate (Fombina):
Cameroon's North, Adamaoua and Far North regions (Overture 2026-10-21.0, tools/data/v392_cm_regions.parquet; Garoua, Ngaoundere, Tibati, Maroua).
Enclosed pockets (Borno/Yobe) closed by the no-gaps rule. Niger, Burkina Faso (Liptako) and Chad parts are already inside. DIR env = project dir (preview: a copy).
Run v386_areas_ellipsoid.py after."""
import pyarrow.parquet as pq
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
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
KEEP = {'NG-SO','NG-KE','NG-ZA','NG-KT','NG-KN','NG-JI','NG-KD','NG-BA','NG-GO','NG-AD','NG-TA','NG-NI','NG-KW','NG-NA','NG-FC','NG-PL'}
rs = pq.read_table(os.path.join(HERE, 'tools/data/v387_regions.parquet')).to_pylist() + pq.read_table(os.path.join(HERE, 'tools/data/v388_ng_kwara.parquet')).to_pylist()
parts = {}
for r in rs:
    if r['region'] in KEEP and r['class'] == 'land' and r['is_land'] is not False: parts[r['region']] = shapely.from_wkb(r['geometry']).buffer(0)
print('states', len(parts), sorted(parts))
CM = {'CM-NO', 'CM-AD', 'CM-EN'}
cmp = [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, 'tools/data/v392_cm_regions.parquet')).to_pylist() if r['region'] in CM and r['class'] == 'land' and r['is_land'] is not False]
print('Cameroon regions', len(cmp))
W = unary_union([unary_union(list(parts.values())).intersection(G['566'][1].buffer(0.02)), unary_union(cmp).intersection(G['120'][1].buffer(0.02))])
def add(key):
    V = MP(C[key]['polys']); print('  +', key, round(A(W.difference(V))), 'km2')
    X = unary_union([V, W.buffer(0.003)]).buffer(0)
    holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if Polygon(h).representative_point().x > 5 and Polygon(h).representative_point().x < 16 and 8 < Polygon(h).representative_point().y < 14]
    for h in holes: print('     closing an enclosed pocket (no-gaps rule):', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
    o = polys(unary_union([X] + holes).buffer(0), 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y6 = add('tib'); Y7 = add('sup')
for n_, p in {'Sokoto': (5.24, 13.06), 'Gwandu': (4.65, 12.62), 'Kano': (8.52, 12.0), 'Katsina': (7.6, 13.0), 'Zaria': (7.71, 11.11), 'Bauchi': (9.84, 10.31), 'Yola': (12.46, 9.2), 'Bida (Nupe)': (6.01, 9.08), 'Ilorin': (4.55, 8.5),
              'Abuja': (7.49, 9.06), 'Jos': (8.89, 9.9), 'Maiduguri (Borno, not part)': (13.15, 11.85), 'Lagos (out)': (3.38, 6.52), 'Ibadan (out)': (3.9, 7.38), 'Lokoja (Kogi, out)': (6.74, 7.8), 'Garoua (Cameroon)': (13.4, 9.3), 'Ngaoundere (Cameroon)': (13.58, 7.32), 'Maroua (Cameroon)': (14.32, 10.6), 'Tibati (Cameroon)': (12.63, 6.47), 'Yaounde (out)': (11.52, 3.87)}.items():
    print('  ', n_, Y6.contains(Point(p)), round(Y6.distance(Point(p)) * 111, 1), 'km')
print('grm outside tib', round(A(MP(C['grm']['polys']).difference(Y6.buffer(0.01)))), '| tib outside sup', round(A(Y6.difference(Y7.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
