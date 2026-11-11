"""Version 370 PREVIEW (Nawaz asked whether V5 holds every Rashidun land: yes, all held land; only Balanjar, the Khazar town of the failed raid of
c. 652, is outside -> "Preview"). V5 (grm) takes the Dagestan land of Version 281 (tools/data/v4_rashidun281.geojson, key 'v2': whole districts
filled to his red lines of that time, from Derbent's hinterland north to Makhachkala, Kaspiysk and Buynaksk, covering two of the three
proposed sites of Balanjar: Buynaksk and the ruins south of Makhachkala; the lower Sulak site lies further north and is NOT covered).
On the live V5; the Germania / Eastern Europe previews (368, 369) are separate. DIR env = project dir (preview: a copy)."""
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
D = {f['properties']['key']: shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'tools/data/v4_rashidun281.geojson')))['features']}
V5 = MP(C['grm']['polys']); W = D['v2']
print('  + Dagestan (Balanjar raid lands)', round(A(W.difference(V5))), 'km2', [round(v, 2) for v in W.bounds])
X = unary_union([V5, W.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Derbent': (48.29, 42.06), 'Makhachkala': (47.5, 42.98), 'Buynaksk (Balanjar site 1)': (47.12, 42.82), 'Tarki ruins (site 2)': (47.49, 42.95), 'lower Sulak / Verkhny Chiryurt (site 3)': (46.85, 43.2),
              'Kizlyar (out)': (46.71, 43.85), 'Grozny (out)': (45.69, 43.32)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(Y.difference(MP(C['sup']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
