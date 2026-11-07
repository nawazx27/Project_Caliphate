"""Version 305 (Nawaz, with a map of how long Rome ruled each land, all coloured areas incl. the '>50' zones: "I want it to look exactly
like this" -> chose "Exactly this map" for V5's Europe).
V5 (grm) = V4 (sas) + the land of that map (tools/data/v5_roman_map305.geojson). The map (reference/v305_roman_rule_duration_map.jpg)
was georeferenced by matching Natural Earth coastlines to its coast lines (cubic transform, median error 1 px; tools/v305_build/icp.py,
tf2.json), its coloured area traced (trace.py -> tools/data/v305_roman_map_shape.geojson) and cut to land with a 0.25 deg coastal
snap and whole small islands (build.py). So in Europe V5 follows the map's edge exactly: Britain to the Forth-Clyde line, NW Germany
to the Elbe, the Rhine-Danube line, Dacia, the Bosporan Crimea; Ireland, northern Scotland, Czechia, Poland, Slovakia, inland
Ukraine are no longer in V5. V6 (rom) and V7 (v2) take any V5 land they lack. Run after tools/v304_v5_line.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F = json.load(open(os.path.join(P, 'tools/data/v5_roman_map305.geojson')))['features'][0]['geometry']
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = shape(F).buffer(0)
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': F['coordinates'], 'km2': km2of(F['coordinates']), 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for key in ['rom', 'v2']:
    V = M(key); ex = A(Y.difference(V))
    if ex < 1: print(key, 'already holds V5'); continue
    X = shapely.set_precision(shapely.union_all([V, Y.buffer(0.003)], grid_size=0.001).buffer(0), 0.001); o = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    old = C[key]['km2']; C[key].update(polys=o, km2=km2of(o)); print(key, 'took', round(ex), 'km2:', old, '->', C[key]['km2'])
for a, b in [('sas', 'grm'), ('grm', 'rom'), ('rom', 'v2')]: print(a, 'outside', b, round(A(M(a).difference(M(b).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
