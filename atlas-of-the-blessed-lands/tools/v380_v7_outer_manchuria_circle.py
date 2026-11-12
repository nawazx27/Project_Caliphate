"""Version 380 PREVIEW (Nawaz: "Why do you keep adding that.. restrict to this [the Madrid Maps 'Concept of a Greater China' map] and add the entire
Korean Peninsula and with everything in the image that I gave you right now" = his red circle drawn on the Version 379 preview round the north-east,
tools/data/v380_outer_manchuria_circle.json, georeferenced through the page's own projection, checked on the 30-60N graticule to 2 px).
V7 (sup): China, Taiwan, Hong Kong, Macao, Mongolia (v377), Tuva and the Russian Far East regions (v378), Korea (v379) as before, PLUS all Russian
land inside his circle: the whole Okhotsk-sea coast, northern Khabarovsk, and the land north and west of the Khabarovsk lobe up to the circle's edge.
Nothing from the Yuan or Qing maps. DIR env = project dir (preview: a copy; needs 377-379 applied first)."""
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
CI = Polygon([tuple(p) for p in json.load(open(os.path.join(HERE, 'tools/data/v380_outer_manchuria_circle.json')))]).buffer(0)
V = MP(C['sup']['polys']); RUS = G['643'][1]
W = CI.intersection(RUS); a = W.difference(V)
print('circle', [round(v, 1) for v in CI.bounds], '| Russian land inside it', round(A(W)), 'km2 | new to V7', round(A(a)), 'km2')
for g in sorted(getattr(a, 'geoms', [a]), key=lambda g: -A(g))[:4]: print('   piece', round(A(g)), 'km2 at', [round(c, 1) for c in g.representative_point().coords[0]])
X = unary_union([V, W.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Okhotsk (town)': (143.2, 59.36), 'Ayan': (138.15, 56.45), 'Nikolayevsk-on-Amur': (140.7, 53.14), 'Magadan (out?)': (150.8, 59.56), 'Yakutsk (out)': (129.7, 62.03), 'Neryungri (Yakutia)': (124.7, 56.66),
              'Tynda (Amur)': (124.7, 55.16), 'Khabarovsk': (135.08, 48.48), 'Vladivostok': (131.9, 43.12), 'Sakhalin (out)': (142.75, 46.96), 'Pyongyang': (125.75, 39.02), 'Seoul': (126.98, 37.57)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('tib outside sup', round(A(MP(C['tib']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
