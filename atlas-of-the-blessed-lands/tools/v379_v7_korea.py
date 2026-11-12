"""Version 379 PREVIEW (Nawaz, on the Madrid Maps "Concept of a Greater China" map alone, dropping the other five: "Only this and add the entire
Korean Peninsula"). That map shades China, Taiwan, Mongolia, Tuva, Outer Manchuria, part of Kazakhstan, part of Kyrgyzstan, Nepal, Bhutan and Arunachal
Pradesh. V7 (sup) already holds Kazakhstan, Kyrgyzstan, Nepal, Bhutan and India whole; the preview chain is Version 377 (China, Taiwan, Hong Kong, Macao, Mongolia)
+ Version 378 (Tuva, Outer Manchuria) + this: North Korea and South Korea whole, so the whole Korean Peninsula with its islands (Jeju and the rest).
Base-map countries 408 and 410. DIR env = project dir (preview: a copy; needs 377 and 378 applied first)."""
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
V = MP(C['sup']['polys']); parts = []
for k, n in {'408': 'North Korea', '410': 'South Korea'}.items():
    assert G[k][0] == n, (k, G[k][0]); g = G[k][1]; parts.append(g); print('  +', n, round(A(g.difference(V))), 'km2 of', round(A(g)))
X = unary_union([V] + [g.buffer(0.003) for g in parts]).buffer(0)
o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Pyongyang': (125.75, 39.02), 'Seoul': (126.98, 37.57), 'Busan': (129.08, 35.18), 'Jeju': (126.53, 33.5), 'Dokdo/Ulleungdo (Ulleung)': (130.9, 37.5), 'Tokyo (out)': (139.69, 35.69), 'Tsushima (Japan, out)': (129.3, 34.4),
              'Vladivostok': (131.9, 43.12), 'Beijing': (116.4, 39.9), 'Ulaanbaatar': (106.92, 47.92), 'Kyzyl (Tuva)': (94.45, 51.72), 'Taipei': (121.56, 25.03)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('tib outside sup', round(A(MP(C['tib']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
