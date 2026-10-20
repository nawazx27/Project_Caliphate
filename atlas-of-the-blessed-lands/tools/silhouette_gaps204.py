"""Version 204: the no-gaps rule after tools/silhouette204.py, for V7 (x3) and V8 ('v2'): fills the pockets tools/fill_gaps.py marks
(fill=True) and every pocket with at least 80% of its edge on the outline, except on Indian-held land (India and the Siachen-Ladakh
box 75.8-80.5 E, 34-36.2 N): automatic gap filling never pulls Indian land in. Run after tools/fill_gaps.py x3,v2."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
IND = G['356'].union(box(75.8, 34, 80.5, 36.2))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ['x3', 'v2']:
    gaps = [shape(f['geometry']) for f in json.load(open(os.path.join(P, f'tools/data/gaps_{k}.geojson')))['features'] if f['properties']['fill'] or f['properties']['touch'] >= 0.8]
    keep = [g for g in gaps if A(g.intersection(IND)) < 0.1]
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    X = shapely.union_all([V] + [g.buffer(0.003).difference(IND) for g in keep], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    n = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    print(k, 'filled', len(keep), 'of', len(gaps), round(sum(A(g) for g in keep)), 'km2;', C[k]['km2'], '->', n, '| India added', round(A(G['356'].intersection(Y)) - A(G['356'].intersection(V)), 2))
    C[k]['polys'] = out; C[k]['km2'] = n
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
