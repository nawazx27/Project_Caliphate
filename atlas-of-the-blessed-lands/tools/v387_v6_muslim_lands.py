"""Version 387 PREVIEW (Nawaz: "Can V6 be considered grand caliphate? If not, then how to make it?" -> option 2: V5 plus every land a Muslim state
actually ruled, Tibet kept as a stated design choice). V6 (tib) keeps V5 + East Turkestan + Greater Tibet + the plateau, and takes, as whole regions
(Overture 2026-10-21.0, tools/data/v387_regions.parquet and tools/data/ru_regions_caucasus.parquet):
  - northern Nigeria: the Sokoto Caliphate (1804-1903) and Kanem-Bornu: Sokoto, Kebbi, Zamfara, Katsina, Kano, Jigawa, Kaduna, Bauchi, Gombe, Yobe, Borno,
    Adamawa, Taraba, Niger, Kwara (Ilorin), Nasarawa, the Federal Capital Territory, and Plateau (enclosed by the others: no-gaps rule);
  - the North Caucasus and the Pontic-Caspian steppe (the Golden Horde, the Crimean Khanate and Nogai lands, the Caucasian Imamate): Dagestan, Chechnya,
    Ingushetia, North Ossetia, Kabardino-Balkaria, Karachay-Cherkessia, Adygea, Krasnodar, Stavropol, Rostov, Kalmykia, Astrakhan;
  - the Volga: the Volga Bulgars, the Golden Horde's Sarai and the Kazan and Astrakhan khanates: Volgograd, Saratov, Samara, Ulyanovsk, Tatarstan, Chuvashia, Mari El.
V7 (sup) takes the same lands so it still holds V6. Not added: Bashkortostan and Orenburg (Nogai Horde), the Malay world (V7 already). DIR env = project dir."""
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
NG = {'NG-SO','NG-KE','NG-ZA','NG-KT','NG-KN','NG-JI','NG-KD','NG-BA','NG-GO','NG-YO','NG-BO','NG-AD','NG-TA','NG-NI','NG-KW','NG-NA','NG-FC','NG-PL'}
RU = {'RU-VGG','RU-SAR','RU-SAM','RU-ULY','RU-TA','RU-CU','RU-ME'}
groups = {'northern Nigeria': [], 'North Caucasus and the steppe': [], 'the Volga': []}
for r in pq.read_table(os.path.join(HERE, 'tools/data/v387_regions.parquet')).to_pylist():
    if r['class'] != 'land' or r['is_land'] is False: continue
    if r['region'] in NG: groups['northern Nigeria'].append(shapely.from_wkb(r['geometry']).buffer(0))
    if r['region'] in RU: groups['the Volga'].append(shapely.from_wkb(r['geometry']).buffer(0))
for r in pq.read_table(os.path.join(HERE, 'tools/data/ru_regions_caucasus.parquet')).to_pylist():
    if r['class'] == 'land' and r['is_land'] is not False: groups['North Caucasus and the steppe'].append(shapely.from_wkb(r['geometry']).buffer(0))
print({k: len(v) for k, v in groups.items()})
W = {k: unary_union(v) for k, v in groups.items()}
NGC = G['566'][1]; W['northern Nigeria'] = W['northern Nigeria'].intersection(NGC.buffer(0.02))
def add(key):
    V = MP(C[key]['polys']); run = V
    for n, g in W.items(): print('  ', key, '+', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
    o = polys(run.buffer(0), 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y6 = add('tib'); Y7 = add('sup')
for n_, p in {'Sokoto': (5.24, 13.06), 'Kano': (8.52, 12.0), 'Ilorin': (4.55, 8.5), 'Abuja': (7.49, 9.06), 'Jos (Plateau)': (8.89, 9.9), 'Lagos (out)': (3.38, 6.52),
              'Kazan': (49.1, 55.79), 'Sarai/Astrakhan': (47.9, 46.6), 'Volgograd': (44.5, 48.71), 'Samara': (50.1, 53.2), 'Cheboksary': (47.25, 56.13), 'Yoshkar-Ola': (47.89, 56.63),
              'Krasnodar': (38.98, 45.04), 'Grozny': (45.69, 43.32), 'Elbrus': (42.44, 43.35), 'Ufa (out)': (55.97, 54.74), 'Moscow (out)': (37.62, 55.75)}.items():
    print('  ', n_, Y6.contains(Point(p)), round(Y6.distance(Point(p)) * 111, 1), 'km')
print('grm outside tib', round(A(MP(C['grm']['polys']).difference(Y6.buffer(0.01)))), '| tib outside sup', round(A(Y6.difference(Y7.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
