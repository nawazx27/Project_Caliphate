"""Version 354 PREVIEW (Nawaz sent Wikipedia's "Mediterranean Sea": its drainage basin includes DR Congo through the Nile; V5 lacked
the Congolese Nile lands round Lakes Albert and Edward and the Semliki -> "Preview"). V5 (grm) takes the part of DR Congo that drains to
the Nile: the land draining to Lakes Albert, Edward and George (west shores, Semliki valley, western Rwenzori, the escarpment above Lake
Albert), computed by a priority-flood watershed on the Mapzen terrain tiles at zoom 8 (~300 m) (tools/dev/congo_nile_watershed.py,
tools/data/v354_nile_watershed_box.geojson), clipped to DR Congo."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
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
NILE = shape(json.load(open(os.path.join(P, 'tools/data/v354_nile_watershed_box.geojson')))['features'][0]['geometry']).buffer(0)
POD = NILE.intersection(G['180'][1])
V5 = M('grm'); print('Congolese Nile basin adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Lake Edward DRC shore (Vitshumbi)': (29.38, -0.68), 'Semliki at Beni': (29.47, 0.49), 'Mutwanga (Rwenzori)': (29.75, 0.33), 'Bunia': (30.25, 1.56), 'Mahagi': (30.99, 2.31), 'Butembo (Congo side?)': (29.29, 0.13), 'Goma (Kivu, Congo)': (29.23, -1.68), 'Aru': (30.86, 2.87)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
