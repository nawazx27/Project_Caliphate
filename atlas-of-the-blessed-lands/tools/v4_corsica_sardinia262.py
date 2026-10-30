"""Version 262 (Nawaz, after a preview: add "Corsica and Sardinia", "the Sardo-Corsican islands", to V4). V4 (CALIPH.me9) gains, whole as the
base map draws them, Corsica (every piece of France with its centre in 8.4-9.7 E, 41.2-43.1 N) and Sardinia with its islands (every piece
of Italy in 7.9-10.0 E, 38.7-41.35 N: La Maddalena, Asinara, San Pietro, Sant'Antioco). V5 not changed. Run AFTER tools/v4_v5_iberia_sicily261.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
COR = unary_union([p for p in getattr(G['FRA'], 'geoms', [G['FRA']]) if 8.4 < p.centroid.x < 9.7 and 41.2 < p.centroid.y < 43.1])
SAR = unary_union([p for p in getattr(G['380'], 'geoms', [G['380']]) if 7.9 < p.centroid.x < 10.0 and 38.7 < p.centroid.y < 41.35])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me9']['polys']]).buffer(0)
X = shapely.union_all([V, COR.buffer(0.003), SAR.buffer(0.003)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
rows = [{'id': 'COR', 'n': 'France: Corsica (Corsica and Sardinia, the Sardo-Corsican islands)', 'km2': round(A(COR)), 'pct': round(A(COR) / A(G['FRA']) * 100, 1)},
        {'id': 'SAR', 'n': 'Italy: Sardinia with its islands (Corsica and Sardinia, the Sardo-Corsican islands)', 'km2': round(A(SAR)), 'pct': round(A(SAR) / A(G['380']) * 100, 1)}]
print('Corsica in %', round(100 * A(COR.intersection(Y)) / A(COR), 2), 'Sardinia in %', round(100 * A(SAR.intersection(Y)) / A(SAR), 2), 'V4', C['me9']['km2'], '->', km2)
C['me9'].update(polys=out, km2=km2, states=[r for r in C['me9']['states'] if r['id'] not in ('COR', 'SAR')] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
