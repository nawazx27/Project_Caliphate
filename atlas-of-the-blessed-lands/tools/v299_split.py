"""Version 299 (Nawaz: "Remove Germany, Netherlands and Belgium. And bring back the old V4 and put the Mediterranean V4 as a new version.").
- New key CALIPH.grm (the new V5) = the Version 298 V4 (Grand Caliphate + Roman Empire + Rome's other holdings + UK, Ireland,
  Moldova, Hungary, Slovakia, Romania) WITHOUT Germany, the Netherlands and Belgium (base-map countries, whole).
- V4 (sas) back to its Version 296 shape (the Grand Caliphate before the Roman additions).
- V6 (rom) and V7 (v2) back to their Version 297 shapes (before Germany to the Elbe came in with Version 298); the new V5 lies
  inside them (checked).
Usage: python3 tools/v299_split.py <caliph.json of Version 296 (git show e9e9fe3:./src/caliph.json)> <caliph.json of Version 297 (git show eddac2b:./src/caliph.json)>"""
import json, os, sys, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
C296 = json.load(open(sys.argv[1])); C297 = json.load(open(sys.argv[2]))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
M = lambda k, c=None: MultiPolygon([Polygon(r[0], r[1:]) for r in (c or C)[k]['polys']]).buffer(0)
V298 = M('sas')
cut = shapely.union_all([G[k][1] for k in ('276', '528', '056')])
from shapely.geometry import box
keep = shapely.union_all([g for k, (n, g) in G.items() if k not in ('276', '528', '056') and g.intersects(box(-12, 44, 25, 60))])
X = shapely.union_all([V298.difference(cut.buffer(0.2)), V298.intersection(keep.difference(cut.buffer(0.004)))]).buffer(0)
X = X.difference(box(32, 44, 38.6, 46.7)).buffer(0)          # no Crimea / Taman leftovers (stray lines)
X = X.difference(box(11.5, 48.7, 15.3, 51.4).difference(G['040'][1].buffer(0.01))).buffer(0)   # no German-Czech border slivers
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
C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', C['grm']['km2'], [r['n'] for r in rows if r['n'] in ('Germany', 'Netherlands', 'Belgium')])
C['sas'] = C296['sas']; C['rom'] = C297['rom']; C['v2'] = C297['v2']
print('sas', C['sas']['km2'], 'rom', C['rom']['km2'], 'v2', C['v2']['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2'), ('shj', 'me2')]:
    print(a, 'outside', b, 'km2', round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
# keep each version inside the next: fold the new V5's edge pieces into V6 and V7
C = json.load(open(F_)); NEW = M('grm')
for key in ['rom', 'v2']:
    V = M(key); ex = A(NEW.difference(V))
    if ex < 1: continue
    X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001); o = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    old = C[key]['km2']; C[key].update(polys=o, km2=km2of(o)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
