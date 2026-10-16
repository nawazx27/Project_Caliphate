"""Version 155 (Nawaz, two phone screenshots: "What are these leftover lines?"). About forty specks of Russian coast and estuary (0.02-4.5 km2
each, ~60 km2 in all) stayed in V2 and V2-B along the Sea of Azov and the Taman peninsula (left by Versions 144-148's whole-town and
whole-sliver passes; they lie inside russia_out151, Russia plus its coastal sea, which the standing rule keeps out of the Caucasus). They are
taken out here: V2 loses russia_out151 minus the orange Caucasus and Greater Georgia (Version 152-155); V2-B loses all of russia_out151.
Run: python3 tools/russia_specks155.py, then the clean-up loop."""
import json, os, glob, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
RO = shape(json.load(open(os.path.join(D, 'russia_out151.geojson')))['features'][0]['geometry']).buffer(0)
reg = shape(json.load(open(os.path.join(D, 'caucasus_shape155.geojson')))['features'][0]['geometry']).buffer(0)
GG = unary_union([shape(f['geometry']).buffer(0) for q in [os.path.join(D, 'greater_georgia152.geojson')] + sorted(glob.glob(os.path.join(D, 'expand_towns152_*_x.geojson'))) for f in json.load(open(q))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k, cut in [('x', RO.difference(reg.union(GG).buffer(0.002))), ('xb', RO)]:
    X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    gone = X.intersection(cut); n = [q for q in getattr(gone, 'geoms', [gone]) if q.geom_type == 'Polygon' and not q.is_empty]
    print(k, 'taken out:', len(n), 'pieces', round(sum(A(q) for q in n), 1), 'km2')
    X = shapely.union_all([shapely.make_valid(X.difference(cut))], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.0005: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    C[k]['polys'] = out
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(k, C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
