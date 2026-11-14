"""Version 398 PREVIEW (Nawaz, after V1 was removed in Version 397: "Read this for v1" with the Wikipedia article Hejaz). A NEW V1 (key shj, replaced, not added to):
MODE=hejaz (default): the Hejaz as the article's infobox defines it, the four Saudi provinces Tabuk, Medina, Mecca and Al-Bahah (Overture 2026-10-21.0,
tools/data/v398_sa_regions.parquet); Asir, Jazan and Najd are not in it. MODE=sham_hejaz: that Hejaz together with Greater Syria as in Version 396 (Syria, Lebanon, Jordan,
Israel, Palestine, Hatay and Southeastern Anatolia). DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
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
MODE = os.environ.get('MODE', 'hejaz')
def rg(f, keep): return [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, f)).to_pylist() if r['region'] in keep and r['class'] == 'land' and r['is_land'] is not False]
cid = lambda n: [k for k, (nm, g) in G.items() if nm == n][0]
SA = cid('Saudi Arabia'); TRK = cid('Türkiye')
parts = {'Hejaz (Tabuk, Medina, Mecca, Al-Bahah)': unary_union(rg('tools/data/v398_sa_regions.parquet', {'SA-07', 'SA-03', 'SA-02', 'SA-11'})).intersection(G[SA][1].buffer(0.02))}
if MODE == 'sham_hejaz':
    for n in ['Syria', 'Lebanon', 'Jordan', 'Israel', 'Palestine']: parts[n] = G[cid(n)][1]
    parts['Hatay and Southeastern Anatolia'] = unary_union(rg('tools/data/v396_tr_southeast.parquet', {'TR-31', 'TR-27', 'TR-79', 'TR-02', 'TR-63', 'TR-21', 'TR-47', 'TR-72', 'TR-56', 'TR-73'})).intersection(G[TRK][1].buffer(0.02))
for n, g in parts.items(): print('  ', n, round(A(g)), 'km2')
X = unary_union([g.buffer(0.003) for g in parts.values()]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) > 0.5]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
o = polys(unary_union([X] + holes).buffer(0), 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', MODE, old, '->', C['shj']['km2'])
for n_, p in {'Mecca': (39.83, 21.42), 'Medina': (39.61, 24.47), 'Jeddah': (39.17, 21.54), 'Taif': (40.41, 21.27), 'Yanbu': (38.06, 24.09), 'Tabuk': (36.57, 28.38), 'Al-Ula': (37.92, 26.62), 'Khaybar': (39.29, 25.70),
              'Tayma (Tabuk)': (38.55, 27.63), 'Al-Bahah': (41.47, 20.01), 'Badr': (38.79, 23.73), 'Riyadh (Najd, out)': (46.72, 24.69), 'Abha (Asir, out)': (42.5, 18.22), 'Jerusalem': (35.23, 31.78), 'Damascus': (36.29, 33.51)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('shj outside me2', round(A(Y.difference(MP(C['me2']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
