"""Version 316 (Nawaz: "The borders near France and Germany etc etc are along the river and in v5 it's not the same you are not tracing
right"). On his map of Roman rule the frontier in Germany and Austria runs along rivers: the Elbe from the sea to the Saale, the Saale
upstream to its source in the Fichtelgebirge, the Naab (Fichtelnaab) down to the Danube at Regensburg, and the Danube past Vienna.
The traced line only wandered near them. In a band of 0.6 deg along that chain (west of 17.0 E), V5 (grm) is now exactly the land on the
Roman side of those rivers (tools/data/v316_frontier_rivers.geojson: Natural Earth 10m, Naab from Overture water). Elsewhere V5 is
unchanged. Run on the Version 315 caliph.json."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box, LineString
from shapely.ops import polygonize, unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
R = {f['properties']['name']: shape(f['geometry']) for f in json.load(open(os.path.join(P, 'tools/data/v316_frontier_rivers.geojson')))['features']}
ends = lambda g: [c for l in getattr(g, 'geoms', [g]) for c in (l.coords[0], l.coords[-1])]
saale_src = min(ends(R['Saale']), key=lambda c: c[1]); naab_src = max(ends(R['Naab']), key=lambda c: c[1])
elbe_sea = max(ends(R['Elbe']), key=lambda c: c[1])
from shapely.ops import nearest_points
saale_mouth = max(ends(R['Saale']), key=lambda c: c[1]); naab_mouth = min(ends(R['Naab']), key=lambda c: c[1])
join = lambda c, g: LineString([c, nearest_points(Point(c), g)[1].coords[0]])
links = [LineString([saale_src, naab_src]),                      # over the Fichtelgebirge watershed
         LineString([elbe_sea, (8.6, 53.95), (8.2, 54.05), (6.5, 54.5), (6.5, 55.0)]),   # down the Elbe estuary to the open sea, west of the North Frisian islands
         join(saale_mouth, R['Elbe']), join(naab_mouth, R['Danube'])]   # close the small gaps where the rivers meet
chain = unary_union(list(R.values()) + links)
for l in links: print('link', [tuple(round(v, 3) for v in c) for c in l.coords])
FR = box(3.0, 45.5, 17.0, 55.0)
# the river lines have small breaks (arms, data seams), so each river is a band 2 x 0.008 deg wide; the land splits at the bands and
# the Roman side is widened back by the same amount, so the border runs on the river's centre line
BAND = 0.008
parts = FR.difference(chain.buffer(BAND))
faces = list(getattr(parts, 'geoms', [parts]))
seeds = [Point(7, 51), Point(10, 52.6), Point(11, 50.5), Point(11.3, 49.4), Point(12, 48), Point(15, 47.5), Point(16.6, 47.9)]
east = [Point(13.5, 52.5), Point(13.0, 51.0), Point(12.6, 49.6), Point(14.0, 49.0), Point(16.3, 48.6)]
Wf = [f for f in faces if any(f.contains(s) for s in seeds)]
assert not any(f.contains(e) for f in Wf for e in east), 'the rivers do not close: Roman side leaks east'
W = unary_union(Wf).buffer(BAND + 0.0005)
print('Roman-side pieces', len(Wf), 'of', len(faces))
Z = unary_union([g for k, g in R.items()] + links).buffer(0.6).intersection(box(3.0, 45.5, 16.95, 55.0))
win = box(3, 44, 20, 56); L = unary_union([g for n, g in G.values() if g.intersects(win)]).intersection(win)
V5 = M('grm')
NEW = W.intersection(L).intersection(Z)
print('removed', round(A(V5.intersection(Z).difference(W))), 'km2 beyond the rivers; added', round(A(NEW.difference(V5))), 'km2 up to them')
EASTSIDE = FR.difference(W).intersection(box(3.0, 47.9, 17.0, 55.0))   # beyond the rivers (north and east of them), up to 17.0 E
print('V5 land beyond the rivers outside the band (cut off):', round(A(V5.difference(Z).intersection(EASTSIDE))), 'km2')
X = unary_union([V5.difference(Z).difference(EASTSIDE), NEW.buffer(0.002)]).buffer(0)
X = unary_union([q for q in getattr(X, 'geoms', [X]) if q.geom_type == 'Polygon' and (A(q) > 20 or not q.intersects(Z.buffer(0.05)))])
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
X = shapely.set_precision(X, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Cuxhaven': (8.69, 53.86), 'Hamburg (north bank)': (10.0, 53.56), 'Harburg (south bank)': (9.98, 53.46), 'Magdeburg (west bank)': (11.63, 52.13), 'Halle (east of Saale)': (11.97, 51.48), 'Leipzig': (12.37, 51.34), 'Jena (on Saale)': (11.59, 50.93), 'Hof': (11.92, 50.31), 'Weiden (Naab)': (12.16, 49.68), 'Amberg (west of Naab)': (11.86, 49.44), 'Regensburg old town (south bank)': (12.1, 49.018), 'Passau': (13.46, 48.574), 'Linz (south bank)': (14.29, 48.3), 'Vienna centre': (16.37, 48.21), 'Vienna Floridsdorf (north bank)': (16.40, 48.26), 'Carnuntum': (16.86, 48.11), 'Gerulata': (17.15, 48.05), 'Chemnitz': (12.92, 50.83), 'Sylt': (8.3, 54.9), 'Heligoland': (7.88, 54.18), 'Amsterdam': (4.9, 52.37)}.items(): print('  ', n_, Y.contains(Point(p)))
for key in ['v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    X2 = shapely.set_precision(unary_union([V, Y.buffer(0.003)]).buffer(0), 0.001); o2 = []
    for q in getattr(X2, 'geoms', [X2]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        o2.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    old = C[key]['km2']; C[key].update(polys=o2, km2=km2of(o2)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
