"""Version 390 PREVIEW (Nawaz: Wikipedia 'Golden Horde' map c.1300, "Preview Exactly, with the yellow shape"): the yellow Golden Horde shape exactly as drawn
(tools/data/v390_golden_horde.geojson, traced and georeferenced by tools/v390_golden_horde_trace.py) is added to V6 (tib) and V7 (sup), clipped to land (no sea added),
tiny gaps (< 20,000 km2) between it and the old edge closed. DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
LAND = unary_union([g for n, g in G.values()]).buffer(0.01)
GH = shape(json.load(open(os.path.join(HERE, 'tools/data/v390_golden_horde.geojson')))['geometry']).buffer(0)
NEW = GH.intersection(LAND)
print('shape as drawn', round(A(GH)), 'km2; on land', round(A(NEW)), 'km2')
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
def add(key):
    V = MP(C[key]['polys']); X = unary_union([V, NEW.buffer(0.003)]).buffer(0)
    holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0 < A(Polygon(h)) < 20000 and Polygon(h).representative_point().x > 20]
    for h in holes: print('   ', key, 'gap closed', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
    Y = MP(polys(unary_union([X] + holes).buffer(0), 0.02)); o = polys(Y, 0.02)
    rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
    print(key, old, '->', C[key]['km2'], '| newly added', round(A(Y.difference(V))), 'km2'); return Y
Y6 = add('tib'); Y7 = add('sup')
print('grm outside tib', round(A(MP(C['grm']['polys']).difference(Y6.buffer(0.01)))), '| tib outside sup', round(A(Y6.difference(Y7.buffer(0.01)))))
print('share of the drawn shape now inside V6:', round(100 * A(NEW.intersection(Y6)) / A(NEW), 1), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
