"""Version 386 (Nawaz: "Let's do everything in fixing the accuracy and improving the experience"). The base map (geo2.json, build_geo3.js) dropped
islands under about 7 km2 (minArea 0.0006 deg2). This tool
 1. finds every Natural Earth 10m island (ne_10m_admin_0_countries.geojson) that the base map does not draw, between 85 S and 85 N, and saves them
    in tools/data/v386_missing_islands.geojson;
 2. puts them in CALIPH.extraLand (after the traced Kastellorizo group, kept in tools/data/v386_extraland_base.json), so the page draws them as land;
 3. adds them to each outline (me2, me9, sas, grm, tib, sup; not V1, which is drawn on exact lines) when the island's country is whole in that outline
    (99% or more of it inside), or when the island lies within 0.3 deg of the outline and the nearest mainland is inside it.
Safe to rerun. Run tools/v386_areas_ellipsoid.py afterwards. DIR env = project dir."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union, nearest_points
from shapely.geometry.polygon import orient
from shapely import STRtree
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
BASE_F = os.path.join(HERE, 'tools/data/v386_extraland_base.json')
if not os.path.exists(BASE_F): json.dump(C['extraLand'], open(BASE_F, 'w'), separators=(',', ':'), ensure_ascii=False)
BASE = json.load(open(BASE_F))
parts = [q for g in G.values() for q in getattr(g, 'geoms', [g])] + [Polygon(p[0], p[1:]).buffer(0) for p in BASE['polys']]
tree = STRtree(parts)
NAMES = {'Turkey': 'Türkiye', 'Dem. Rep. Congo': 'DR Congo'}
ne = json.load(open(os.path.join(P, 'ne_10m_admin_0_countries.geojson'))); miss = []
for f in ne['features']:
    g = shape(f['geometry']).buffer(0); n = f['properties'].get('NAME'); n = NAMES.get(n, n)
    for q in getattr(g, 'geoms', [g]):
        if q.bounds[3] > 85 or q.bounds[1] < -85: continue
        if len(tree.query(q, predicate='intersects')) == 0:
            q = shapely.set_precision(q, 0.001)
            for z in getattr(q, 'geoms', [q]):
                if z.geom_type == 'Polygon' and not z.is_empty and A(z) >= 0.02: miss.append((n, orient(Polygon(z.exterior), 1.0)))
print('islands the base map lacks:', len(miss), '|', round(sum(A(q) for n, q in miss)), 'km2 |', sum(len(q.exterior.coords) for n, q in miss), 'points')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'n': n}, 'geometry': mapping(q)} for n, q in miss]}, open(os.path.join(HERE, 'tools/data/v386_missing_islands.geojson'), 'w'), separators=(',', ':'))
ring = lambda q: [[round(x, 3), round(y, 3)] for x, y in q.exterior.coords]
C['extraLand'] = {'n': BASE['n'] + '; and the Natural Earth islands the base map lacks (tools/v386_missing_islands.py)', 'polys': BASE['polys'] + [[ring(q)] for n, q in miss], 'km2': round(BASE['km2'] + sum(A(q) for n, q in miss), 2)}
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.02):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
LANDTREE = STRtree(parts)
import collections
for key in ['me2', 'me9', 'sas', 'grm', 'tib', 'sup']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0); shapely.prepare(V); Vb = V.buffer(0.02); shapely.prepare(Vb)
    whole = {n for n, g in G.items() if g.area and V.intersection(g).area / g.area >= 0.99}
    add = []; why = collections.Counter()
    for n, q in miss:
        if V.intersects(q): continue
        if n in whole and V.distance(q) <= 3: add.append(q); why[n] += 1; continue   # (fix: not a whole country's islands across an ocean, e.g. the Dutch Caribbean)
        if V.distance(q) <= 0.3:
            m = parts[LANDTREE.nearest(q)]
            if Vb.contains(nearest_points(q, m)[1]): add.append(q); why[n + ' (near)'] += 1
    if not add: print(key, 'nothing to add'); continue
    X = unary_union([V] + add).buffer(0); o = polys(X); old = C[key]['km2']
    C[key] = dict(C[key], polys=o, km2=km2of(o))
    print(key, '+', len(add), 'islands,', round(sum(A(q) for q in add)), 'km2 | pieces', len(C[key]['polys']), '|', dict(why.most_common(9)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
