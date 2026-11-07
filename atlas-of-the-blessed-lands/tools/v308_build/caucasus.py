"""Version 308, step 2 (Nawaz circled the Caucasus on his map of the duration of Roman rule: "In the preview make it look like this",
"The Caucasus"). Inside his circle (mapped to lon/lat with the Version 305 fit tools/v305_build/tf2.json, saved as
tools/v308_build/caucasus_circle308.json), V5 takes the Version 305 shape (that map, traced): the border on the Caucasus crest.
Usage: python3 caucasus.py <atlas dir> <caliph.json of Version 305>"""
import json, sys, os, shapely, subprocess
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.geometry.polygon import orient
from pyproj import Geod
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
P = sys.argv[1]; F_ = os.path.join(P, 'src/caliph.json')
PRE = json.load(open(F_)); OLD = json.load(open(sys.argv[2]))
M = lambda C, k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
R = shape(json.load(open(os.path.join(P, 'tools/v308_build/caucasus_circle308.json')))).buffer(0)
Yp, V305 = M(PRE, 'grm'), M(OLD, 'grm')
print('removed', round(A(Yp.intersection(R).difference(V305))), 'added', round(A(V305.intersection(R).difference(Yp))))
# pieces away from the circle are kept whole (small islands too); pieces the circle cuts lose the bits under 30 km2 it leaves
keep = []
for q in getattr(Yp, 'geoms', [Yp]):
    if not q.intersects(R): keep.append(q); continue
    d = q.difference(R); keep += [s for s in getattr(d, 'geoms', [d]) if s.geom_type == 'Polygon' and A(s) > 30]
X = shapely.union_all(keep + [V305.intersection(R).buffer(0.002)]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
X = shapely.set_precision(X, 0.001); out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
PRE['grm']['polys'] = out; PRE['grm']['km2'] = km2of(out)
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
rws = []
for f in geo['features']:
    if not f.get('geometry'): continue
    g = shape(f['geometry']).buffer(0)
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': f['id'], 'n': f['properties']['n'], 'km2': round(A(g)), 'pct': pct})
PRE['grm']['states'] = sorted(rws, key=lambda r: -r['km2'] * r['pct'])
print('grm', PRE['grm']['km2'])
for a_, b_ in [('sas', 'grm')]: print(a_, 'outside', b_, round(A(M(OLD, a_).difference(Y.buffer(0.01)))), '(V4 of Version 305)')
for n, p in {'Krasnodar': (38.98, 45.04), 'Rostov': (39.72, 47.24), 'Taman': (36.7, 45.2), 'Novorossiysk': (37.77, 44.72), 'Sochi': (39.72, 43.6), 'Stavropol': (41.97, 45.04), 'Grozny': (45.7, 43.32), 'Makhachkala': (47.5, 42.98), 'Derbent': (48.29, 42.06), 'Tbilisi': (44.79, 41.72), 'Baku': (49.87, 40.41), 'Astrakhan': (48.03, 46.35)}.items(): print(' ', n, Y.contains(Point(p)))
json.dump(PRE, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
