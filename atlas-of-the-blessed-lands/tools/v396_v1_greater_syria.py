"""Version 396 PREVIEW (Nawaz: "Let's make some changes to v1", then the Wikipedia link Syria (region)): V1 (shj) takes the whole of the region's countries as the
article's infobox lists them: all of Syria (V1 had 73%, not the Euphrates and Jazira east), and Turkey's Hatay and Southeastern Anatolia region (Gaziantep, Kilis, Adiyaman,
Sanliurfa, Diyarbakir, Mardin, Batman, Siirt, Sirnak; Overture 2026-10-21.0, tools/data/v396_tr_southeast.parquet). Lebanon, Jordan, Israel, Palestine and the Hijaz were already in.
DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
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
import pyarrow.parquet as pq
tr = [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, 'tools/data/v396_tr_southeast.parquet')).to_pylist() if r['class'] == 'land' and r['is_land'] is not False]
TRK = [k for k, (nm, g) in G.items() if nm == 'Türkiye'][0]; SYR = [k for k, (nm, g) in G.items() if nm == 'Syria'][0]
W = {'Syria (whole)': G[SYR][1], 'Hatay and Southeastern Anatolia': unary_union(tr).intersection(G[TRK][1].buffer(0.02))}
def add(key):
    V = MP(C[key]['polys']); run = V
    for n, g in W.items(): print('  ', key, '+', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
    X = run.buffer(0)
    holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 33 < Polygon(h).representative_point().x < 45 and 30 < Polygon(h).representative_point().y < 39.5 and A(Polygon(h)) > 0.5]
    for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
    o = polys(unary_union([X] + holes).buffer(0), 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y1 = add('shj')
for n_, p in {'Damascus': (36.29, 33.51), 'Aleppo': (37.16, 36.2), 'Raqqa': (39.01, 35.95), 'Deir ez-Zor': (40.14, 35.33), 'Abu Kamal': (40.92, 34.45), 'Hasakah': (40.75, 36.5), 'Qamishli': (41.23, 37.05),
              'Antakya': (36.16, 36.2), 'Gaziantep': (37.38, 37.07), 'Sanliurfa (Edessa)': (38.79, 37.16), 'Harran': (39.03, 36.86), 'Diyarbakir (Amid)': (40.23, 37.91), 'Mardin': (40.74, 37.31), 'Adiyaman': (38.28, 37.76),
              'Siirt': (41.94, 37.93), 'Cizre (Sirnak)': (42.19, 37.33), 'Malatya (already in)': (38.31, 38.35), 'Adana (already in)': (35.32, 37.0), 'Mosul (Iraq, out)': (43.13, 36.34), 'Mecca': (39.83, 21.42), 'Jerusalem': (35.23, 31.78)}.items():
    print('  ', n_, Y1.contains(Point(p)), round(Y1.distance(Point(p)) * 111, 1), 'km')
print('shj outside me2', round(A(Y1.difference(MP(C['me2']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
