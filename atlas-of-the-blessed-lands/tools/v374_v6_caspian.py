"""Version 374 PREVIEW, second design (Nawaz: "You don't need to use my line. Enclose it yourself. Mine is not good."). V6 (sup) encloses the
Caspian on real regional borders: every Russian region between the Black Sea, the Caucasus and the Caspian is taken WHOLE (Overture regions,
tools/data/ru_regions_caucasus.parquet): Dagestan, Chechnya, Ingushetia, North Ossetia, Kabardino-Balkaria, Karachay-Cherkessia, Adygea,
Krasnodar Krai, Stavropol Krai, Kalmykia and Astrakhan Oblast. Rostov Oblast keeps its present part (the Azov and lower Don lands).
So V6's edge there is the northern border of Krasnodar, Stavropol, Kalmykia and Astrakhan, meeting Kazakhstan north of the Caspian.
V5 is NOT changed. Replaces the first design (his Version 372 line). DIR env = project dir (preview: a copy)."""
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
V6 = MP(C['sup']['polys']); parts = []
for r in pq.read_table(os.path.join(HERE, 'tools/data/ru_regions_caucasus.parquet')).to_pylist():
    if r['class'] != 'land' or r['is_land'] is False or r['region'] == 'RU-ROS': continue
    g = shapely.from_wkb(r['geometry']).buffer(0).intersection(G['643'][1].buffer(0.02)); parts.append(g)
    a = A(g.difference(V6))
    if a >= 1: print('  +', dict(r['names']['common']).get('en'), round(a), 'km2')
W = unary_union(parts)
# Russian Caspian islets off these coasts (base map land not inside Overture's land polygons)
ISL = G['643'][1].intersection(Polygon([(46.5, 42.0), (50.6, 42.0), (50.6, 46.6), (49.3, 46.6), (47.8, 45.0), (46.5, 44.0)])).difference(W)
print('  + coast slivers and islets', round(A(ISL.difference(V6))), 'km2')
X = unary_union([V6, W.buffer(0.003), ISL.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Astrakhan': (48.03, 46.35), 'Akhtubinsk': (46.21, 48.28), 'Elista': (44.27, 46.31), 'Stavropol': (41.97, 45.04), 'Grozny': (45.69, 43.32), 'Kizlyar': (46.71, 43.85), 'Krasnodar': (38.98, 45.04),
              'Sochi': (39.72, 43.59), 'Rostov': (39.72, 47.23), 'Volgodonsk (Rostov, out)': (42.15, 47.51), 'Volgograd (out)': (44.5, 48.71)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
import numpy as np
CO = G['643'][1].boundary.intersection(Polygon([(46.5, 42.0), (50.5, 42.0), (50.5, 47.0), (46.5, 47.0)]))
out = [p for p in (CO.interpolate(f, normalized=True) for f in np.linspace(0, 1, 4000)) if Y.distance(p) > 0.02]
print('Russian Caspian shore points outside V6:', len(out), [(round(p.x, 2), round(p.y, 2)) for p in out[:6]])
print('grm outside sup', round(A(MP(C['grm']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
