"""Version 328 (Nawaz: "Remove any stray lines from V5 (if it has any)"). Checked: no holes inside V5, no seams between its pieces
(every hairline gap is on its outer edge, ~1 m wide, from rounding). Found and removed: the 6.5 km hairline piece at the Elbe mouth left by
Version 318 (8.89-8.94 E, 53.92-53.97 N). Seven other places flagged as "spikes" (Kinburn spit, Arabat spit, Chesil Beach, Pembrokeshire,
Sicily, the Algerian coast, La Palma) were false alarms: long straight coast edges of the base map, zero area, not lines. Method: drop that piece; open the outline by 0.0002 deg (~20 m), which only removes parts
thinner than ~40 m; real land is not touched (checked: V4 still inside, area change reported)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
gd = Geod(ellps='WGS84'); A = lambda g: abs(gd.geometry_area_perimeter(g)[0]) / 1e6; Pm = lambda g: abs(gd.geometry_area_perimeter(g)[1]) / 1e3
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
polys = [Polygon(r[0], r[1:]) for r in C['grm']['polys']]
EB = box(8.85, 53.90, 8.97, 53.98)
keep = [p for p in polys if not (p.within(EB.buffer(0.01)) and A(p) < 1)]
print('Elbe hairline pieces dropped:', len(polys) - len(keep))
V0 = MultiPolygon(polys).buffer(0)
Y = MultiPolygon(keep).buffer(0)
parts = list(getattr(Y, 'geoms', [Y]))
Y = shapely.union_all([p.buffer(-0.0002, join_style=2).buffer(0.0002, join_style=2) if A(p) > 0.5 else p for p in parts]).buffer(0)
X = shapely.set_precision(Y, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Yn = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
lost = V0.difference(Yn); gained = Yn.difference(V0)
print('removed', round(A(lost), 2), 'km2, added', round(A(gained), 2), 'km2 (rounding)')
op = Yn.buffer(-0.0006).buffer(0.0006); sp = Yn.difference(op)
left = [q for q in getattr(sp, 'geoms', [sp]) if q.geom_type == 'Polygon' and Pm(q) > 1.5 and 2 * A(q) / Pm(q) < 0.06]
print('thin spikes left:', len(left))
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Yn):
        pct = round(100 * g.intersection(Yn).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': out, 'km2': km2of(out), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'], '| pieces', len(polys), '->', len(out))
print('sas outside grm', round(A(M('sas').difference(Yn.buffer(0.01)))))
for n_, p in {'Lobos': (-13.82, 28.75), 'Mogador': (-9.789, 31.497), 'Sark': (-2.36, 49.43), 'Scilly': (-6.3, 49.92), 'Farasan': (41.9, 16.74), 'Cuxhaven': (8.69, 53.86), 'Arabat spit mid': (35.3, 45.6)}.items(): print('  ', n_, Yn.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
