"""Version 368 PREVIEW (Nawaz: "Preview V6 Germanica in V5"). V5 (grm) takes the Germania Magna that V6 (sup) holds since Versions 365/367:
Germany, Denmark (with Bornholm) and Czechia whole, Poland west of the Vistula to the San-Danube diagonal; no Sweden. Taken straight from
V6's shape inside the box 5-23 E, 47.5-58.5 N, so both versions share the same line there. DIR env = project dir (preview: a copy)."""
from shapely.geometry import box
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
V5 = MP(C['grm']['polys']); V6 = MP(C['sup']['polys'])
ADD = V6.intersection(box(5, 47.5, 23, 58.5)).difference(V5)
for k, n in [('276', 'Germany'), ('208', 'Denmark'), ('203', 'Czechia'), ('616', 'Poland')]: print('  +', n, round(A(ADD.intersection(G[k][1]))), 'km2')
print('  total', round(A(ADD)), 'km2')
X = unary_union([V5, ADD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Berlin': (13.4, 52.52), 'Copenhagen': (12.57, 55.68), 'Prague': (14.42, 50.08), 'Gdansk': (18.65, 54.35), 'Krakow': (19.94, 50.06), 'Warsaw west bank': (20.98, 52.23),
              'Lublin (out)': (22.57, 51.25), 'Malmo (out)': (13.0, 55.6), 'Krasnodar (out, V6 only)': (38.98, 45.04)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(MP(C['sas']['polys']).difference(Y.buffer(0.01)))), '| grm outside sup', round(A(Y.difference(V6.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
