"""Version 369 PREVIEW, on top of the Version 368 preview (V5 with Germania Magna). Nawaz drew a red line on that preview, from east of
St Petersburg (~33.8E 59.2N) past Moscow (~37.4E 54.6N) and ~41E 49.4N down to the Caucasus foreland (~41.8E 45.3N): "Add all the modern
countries up until here." V5 (grm) takes every modern country lying wholly west of the line, each whole: Poland, Lithuania, Latvia, Estonia,
Belarus, Ukraine (Moldova is already in). Russia, which the line cuts, is NOT added (asked him), nor Kaliningrad, nor Finland (north of the
line's start). Run after tools/v368_v5_germania.py. DIR env = project dir (preview: a copy)."""
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
V5 = MP(C['grm']['polys'])
IDS = {'616': 'Poland', '440': 'Lithuania', '428': 'Latvia', '233': 'Estonia', '112': 'Belarus', '804': 'Ukraine'}
for k, n in IDS.items():
    assert G[k][0] == n, (k, G[k][0]); print('  +', n, round(A(G[k][1].difference(V5))), 'km2')
X = unary_union([V5] + [G[k][1].buffer(0.003) for k in IDS]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Warsaw': (21.01, 52.23), 'Vilnius': (25.28, 54.69), 'Riga': (24.1, 56.95), 'Tallinn': (24.75, 59.44), 'Minsk': (27.56, 53.9), 'Kyiv': (30.52, 50.45), 'Kharkiv': (36.23, 49.99),
              'Luhansk': (39.3, 48.57), 'Kaliningrad (out)': (20.5, 54.71), 'Smolensk (out)': (32.05, 54.78), 'Moscow (out)': (37.62, 55.75), 'St Petersburg (out)': (30.3, 59.94), 'Helsinki (out)': (24.94, 60.17)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
