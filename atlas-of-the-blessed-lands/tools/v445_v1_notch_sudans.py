"""Version 445 (Nawaz, red stroke on his phone screenshot across the notch in V1's edge north-east of Lake Turkana, ~37.0 E 6.0 N to ~37.85 E 6.7 N:
"Fill and make sure the entire modern Sudan and South Sudan is in v1 and push directly"). The notch north-west of his stroke is filled (Ethiopian land);
Sudan and South Sudan are taken whole (the Version 435 roughening of the Sudan-Chad line had left ~0.2% of Sudan out). DIR env = project dir. Run v386 after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
NOTCH = Polygon([(36.8, 5.85), (37.0, 6.0), (37.85, 6.7), (37.85, 7.3), (36.8, 7.3)]).intersection(G['Ethiopia']).difference(V)
print('notch filled', round(A(NOTCH)), 'km2')
X = unary_union([V, NOTCH.buffer(0.003).intersection(G['Ethiopia'].buffer(0.003)), G['Sudan'].buffer(0.003), G['South Sudan'].buffer(0.003)]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); rws = []
for f in geo['features']:
    if not f.get('geometry'): continue
    g_ = G[f['properties']['n']]
    if g_.area and g_.intersects(Y):
        pct = round(100 * g_.intersection(Y).area / g_.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g_)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {**C['shj'], 'polys': o, 'km2': km, 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km, '| Sudan', round(100 * G['Sudan'].intersection(Y).area / G['Sudan'].area, 3), '% | South Sudan', round(100 * G['South Sudan'].intersection(Y).area / G['South Sudan'].area, 3), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
