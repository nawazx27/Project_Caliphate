"""Version 360 PREVIEW (Nawaz, on a screenshot of the OLD connected V5 = Version 356: "Fill... This is the old v5. I'm just experimenting.").
His two red lines, georeferenced from the screenshot (Istanbul/Baku/Bukhara calibration):
  line A: the Don at the NE corner of the Azov block (40.79E 48.18N) SE to the Caspian coast W of the Volga delta (48.37E 44.88N);
  line B: from line A (42.1E 47.55N) NE to the west edge of the Volga lobe (46.8E 48.94N).
V5 takes the Russian steppe enclosed by the lines and the existing outline (lower Don, Kalmykia, Volgograd south, Astrakhan west).
DIR env = project dir to edit (default: this repo). Preview only."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.environ.get('DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
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
V5 = M('grm')
# his lines (A0 -> J on line A, then line B), closed through points INSIDE the existing V5 (Volga lobe, Caspian side, land bridge, Azov block)
LINE = [(40.79, 48.18), (42.1, 47.55), (44.14, 48.32), (46.8, 48.94)]
CLOSE = [(47.6, 48.6), (48.6, 46.5), (48.6, 44.6), (47.3, 43.4), (43.0, 43.4), (40.0, 44.9), (39.6, 47.6)]
POLY = Polygon(LINE + CLOSE).intersection(G['643'][1])
ADD = POLY.difference(V5)
for g in getattr(ADD, 'geoms', [ADD]):
    if A(g) > 50: print('  piece', round(A(g)), 'km2 at', [round(c, 2) for c in g.representative_point().coords[0]])
print('steppe fill adds', round(A(ADD)), 'km2')
X = unary_union([V5, POLY.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Rostov-on-Don': (39.72, 47.23), 'Elista': (44.27, 46.31), 'Volgograd (line B end area)': (44.5, 48.71), 'Astrakhan': (48.03, 46.35), 'Salsk': (41.54, 46.48), 'Kotelnikovo': (43.15, 47.63), 'Lagan': (47.37, 45.39)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
