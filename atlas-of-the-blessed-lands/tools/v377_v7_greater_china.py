"""Version 377 PREVIEW (Nawaz sent Wikipedia's Greater China article, then "Preview entire greater china"). V7 (sup, the Super Caliphate, which already
holds East Turkestan and Tibet) takes the rest of Greater China in every sense the article gives: the People's Republic of China whole (mainland with
Manchuria, Hainan, Hong Kong and Macao), Taiwan, and Mongolia (Outer Mongolia, one of the five lands of the 1944 map and of the Qing sense). Base-map
countries 156, 158, 344, 446, 496. Overseas Chinese communities and Singapore (the wider sense) are not land to add. Preview: V6 (tib) and
V5 are NOT changed here. DIR env = project dir (preview: a copy)."""
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
IDS = {'156': 'China (PRC)', '158': 'Taiwan', '344': 'Hong Kong', '446': 'Macao', '496': 'Mongolia'}
V = MP(C['sup']['polys']); parts = []
for k, n in IDS.items():
    g = G[k][1]; parts.append(g); print('  +', n, round(A(g.difference(V))), 'km2 of', round(A(g)))
X = unary_union([V] + [g.buffer(0.003) for g in parts]).buffer(0)
o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Beijing': (116.4, 39.9), 'Shanghai': (121.47, 31.23), 'Guangzhou': (113.26, 23.13), 'Harbin': (126.64, 45.75), 'Chengdu': (104.07, 30.66), 'Hainan (Haikou)': (110.35, 20.04), 'Hong Kong': (114.17, 22.32),
              'Taipei': (121.56, 25.03), 'Ulaanbaatar': (106.92, 47.92), 'Vladivostok (out)': (131.9, 43.12), 'Seoul (out)': (126.98, 37.57), 'Tokyo (out)': (139.69, 35.69), 'Hanoi (V7 already)': (105.84, 21.03)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('tib outside sup', round(A(MP(C['tib']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
