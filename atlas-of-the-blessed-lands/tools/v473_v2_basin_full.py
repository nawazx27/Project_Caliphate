"""Version 473 (Nawaz, after the check that the new V2 holds 99.8% of the Nile basin: "Fill and push"). The last two bits of the Nile basin outside V2
(CALIPH.arb) are added: (1) the far western head of Wadi Howar (the 'Yellow Nile') in Chad, the part of the traced basin (tools/data/v453_nile_basin_traced.geojson)
outside V2, ~6,400 km2; (2) the southernmost source, the Ruvyironza head of the Kagera in southern Burundi (~29.81 E 3.92 S), with the traced Nile's southern
end, joined to V2's edge with a smooth closing (~10 km). Cut to land; V1 unchanged. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for g in G.values() if g.intersects(shapely.box(15, -6, 40, 32))]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['arb']['polys']); V1 = MP(C['shj']['polys'])
B = shape(json.load(open(os.path.join(HERE, 'tools/data/v453_nile_basin_traced.geojson')))['geometry']).buffer(0)
NL = [r for r in json.load(open(os.path.join(P, 'src/four_rivers.json')))['rivers'] if r['k'] == 'nile'][0]['parts']
SRC = unary_union([Point(29.81, -3.92).buffer(0.06)] + [LineString(c).buffer(0.04) for c in NL if min(y for x, y in c) < -3.3])
add = unary_union([B.difference(V), SRC.difference(V)]).intersection(LAND)
X = unary_union([V, add]).buffer(0)
loc = shapely.box(29.4, -4.3, 30.4, -3.3)                                   # a smooth join at the Burundi source only
X = unary_union([X, X.intersection(loc.buffer(0.3)).buffer(0.1).buffer(-0.1).intersection(loc).intersection(LAND)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 2000]).buffer(0)
new = X.difference(V); print('added', round(A(new)), 'km2', {k: round(A(new.intersection(G[k]))) for k in G if G[k].intersects(new) and A(new.intersection(G[k])) > 5})
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o)
print('arb', C['arb']['km2'], '->', km, '| basin outside V2:', round(A(B.difference(Y.buffer(0.001)).intersection(LAND)), 1), 'km2 | source in:', Y.contains(Point(29.81, -3.92)),
      '| V1 outside V2:', round(A(V1.difference(Y.buffer(0.002))), 1))
C['arb']['polys'] = o; C['arb']['km2'] = km
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
