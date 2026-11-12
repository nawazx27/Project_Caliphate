"""Version 376 (Nawaz: "Add this between v5 and v6 and push", after the V5 preview with East Turkestan, Greater Tibet and the whole Tibetan Plateau).
A NEW outline, key CALIPH.tib (XV 'tib'), becomes V6 and the Super Caliphate (CALIPH.sup) becomes V7: tib = V5 (grm) + East Turkestan
(tools/data/v9_east_turkestan_v218.geojson) + Greater Tibet (greater_tibet_v222) + the Tibetan Plateau above 3000 m (tibetan_plateau_3000m) + its
edge counties (v5_tibet_plateau277), exactly as V6/V7 holds them. V5 itself is NOT changed. Rerun after any V5 change so tib still holds V5.
Run after tools/v362_v6_super.py (and its later patches), which it needs for the sup check. DIR env = project dir."""
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
def gj(n):
    d = json.load(open(os.path.join(HERE, 'tools/data/' + n + '.geojson'))); fs = d['features'] if 'features' in d else [d]
    return unary_union([shape(f.get('geometry', f)).buffer(0) for f in fs])
V5 = MP(C['grm']['polys']); run = V5
for n in ['v9_east_turkestan_v218', 'greater_tibet_v222', 'tibetan_plateau_3000m', 'v5_tibet_plateau277']:
    g = gj(n); print('  +', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
X = run.buffer(0); o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C.get('tib', {}).get('km2'); C['tib'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('tib', old, '->', C['tib']['km2'], '| V5', C['grm']['km2'], '| sup', C['sup']['km2'])
print('V5 outside tib', round(A(V5.difference(Y.buffer(0.01)))), '| tib outside sup', round(A(Y.difference(MP(C['sup']['polys']).buffer(0.01)))))
for n_, p in {'Urumqi': (87.6, 43.8), 'Kashgar': (75.99, 39.47), 'Lhasa': (91.1, 29.65), 'Qamdo': (97.17, 31.14), 'Xining': (101.8, 36.6), 'Kangding': (101.96, 30.05), 'Shangri-La': (99.7, 27.83),
              'Lanzhou (out)': (103.8, 36.06), 'Chengdu (out)': (104.07, 30.66), 'Bangkok (V7 only)': (100.5, 13.75), 'Krasnodar (V7 only)': (38.98, 45.04)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
