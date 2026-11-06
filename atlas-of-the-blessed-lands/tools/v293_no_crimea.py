"""Version 293 (Nawaz: "Return to the previous version" ... "To the one without crimea").
V7 (CALIPH.rom) and V8 (CALIPH.v2) go back to their Version 291 shapes (no Crimea, no Black Sea link; the Ottoman-lands and
red-line previews were never applied). The Version 292 V1 (CALIPH.shj) stays, and is unioned into the restored V7 and V8 so
each version stays inside the next.
Usage: python3 tools/v293_no_crimea.py <caliph.json of Version 291, from: git show 41bf9f1:./src/caliph.json>"""
import json, os, sys, subprocess, shapely
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
OLD = json.load(open(sys.argv[1])); F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
NEW = MultiPolygon([Polygon(r[0], r[1:]) for r in C['shj']['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for key in ['rom', 'v2']:
    C[key] = OLD[key]
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    if A(NEW.difference(V)) >= 1:
        X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
        out = []
        for q in getattr(X, 'geoms', [X]):
            if q.geom_type != 'Polygon' or A(q) < 0.02: continue
            q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
            out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
        C[key].update(polys=out, km2=km2of(out))
    print(key, C[key]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
