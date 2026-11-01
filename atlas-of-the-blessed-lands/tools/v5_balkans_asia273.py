"""Version 273 (Nawaz: "Add the entire Balkans and add east Turkestan, greater Tibet, Myanmar, Pakistan administered Kashmir, china
administered Kashmir from v6"; on the preview, circling Hungary and a stray line by Vietnam: "Add Hungary as well and remove that stray
line in the image and a stray lines near west Africa in v6"; then "Apply everything").
V5 (CALIPH.sas) gains tools/data/v5_balkans_asia273.geojson: Hungary, Slovenia, Croatia, Bosnia and Herzegovina, Serbia, Montenegro,
Kosovo, North Macedonia, Albania, Romania and Bulgaria whole (base map), and East Turkestan, Greater Tibet and Myanmar exactly as V6
draws them, without V6's hairline strips along China's borders with Vietnam and Laos. Both Kashmirs were already in V5.
V6 (CALIPH.v2): the 103 tiny slivers off the West African coast (Côte d'Ivoire to Benin, lagoons, Saint Helena bits; ~620 km2) that
touch nothing of V4 are dropped, and its hairline strip along China's southern border is cut. Run AFTER tools/v5_byua272.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def rings(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
# V5
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_balkans_asia273.geojson')))['geometry']).buffer(0)
V = M('sas'); X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
out = rings(X); k5 = km2(out); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
BK = {'348': 'Hungary', '705': 'Slovenia', '191': 'Croatia', '070': 'Bosnia and Herzegovina', '688': 'Serbia', '499': 'Montenegro', 'KOS': 'Kosovo',
      '807': 'North Macedonia', '008': 'Albania', '642': 'Romania', '100': 'Bulgaria'}
rows = [{'id': k, 'n': n, 'km2': round(A(G[k].intersection(Y))), 'pct': round(100 * A(G[k].intersection(Y)) / A(G[k]), 1)} for k, n in BK.items()]
rows += [{kk: r[kk] for kk in ('id', 'n', 'km2', 'pct')} for r in C['v2']['states'] if r['id'] in ('104', '156_T', '156_X')]
print('V5 (sas)', C['sas']['km2'], '->', k5); print([(r['id'], r['km2'], r['pct']) for r in rows])
C['sas'].update(polys=out, km2=k5, states=[r for r in C['sas']['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
# V6
V4 = M('me9'); bx = box(-20, -20, 15, 8); keep = []
for q in C['v2']['polys']:
    Pq = Polygon(q[0], q[1:])
    if A(Pq) < 500 and bx.contains(Pq) and not Pq.intersects(V4): continue
    keep.append(q)
print('V6 West African slivers dropped', len(C['v2']['polys']) - len(keep))
V6 = MultiPolygon([Polygon(r[0], r[1:]) for r in keep]).buffer(0)
cn = V6.intersection(G['156']); thin = cn.difference(cn.buffer(-0.02).buffer(0.025)).intersection(box(97, 20, 110, 24))
print('V6 hairline along China-Vietnam/Laos cut', round(A(thin), 1), 'km2')
out6 = rings(shapely.set_precision(V6.difference(thin), 0.001)); k6 = km2(out6)
print('V6 (v2)', C['v2']['km2'], '->', k6)
C['v2'].update(polys=out6, km2=k6)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
