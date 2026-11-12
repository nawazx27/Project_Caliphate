"""Version 371 (Nawaz: "cover the left out site", the third proposed site of Balanjar on the lower Sulak, Verkhny Chiryurt by Kizilyurt, 7 km outside
after Version 370). V5 (grm) and V6 (sup) take, whole (Overture Maps 2026-10-21.0 districts, tools/data/v371_sulak_kizilyurt.geojson):
Kizilyurt city okrug (which holds the site) and the Kizilyurtovsky District round it, so no pocket is left. Run after tools/v370_v5_balanjar.py."""
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
W = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'tools/data/v371_sulak_kizilyurt.geojson')))['features']])
def add(key):
    V = MP(C[key]['polys']); print('  +', key, round(A(W.difference(V))), 'km2')
    X = unary_union([V, W.buffer(0.002)]).buffer(0); o = polys(X, 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y5 = add('grm'); Y6 = add('sup')
for n_, p in {'Verkhny Chiryurt (Balanjar site 3)': (46.85, 43.2), 'Kizilyurt': (46.87, 43.2), 'Buynaksk (site 1)': (47.12, 42.82), 'Tarki (site 2)': (47.49, 42.95), 'Khasavyurt (out)': (46.59, 43.25)}.items():
    print('  ', n_, Y5.contains(Point(p)), round(Y5.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(Y5.difference(Y6.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
