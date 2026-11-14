"""Version 415 (Nawaz: on the Version 413 preview (Egypt from his olive map): "Let's go with this edit and make sure that you have Hijaz correctly included", with
Britannica's Hejaz map). Britannica's orange Hejaz is the four Saudi provinces Tabuk, Medina, Mecca and Al-Bahah (its south tip at ~18.3 N is Mecca province's
coast). Run AFTER tools/v413_v1_egypt_map.py: those four provinces are added whole to V1 (shj) (about 4,000 km2 of their eastern edge was missing).
Then rerun tools/v411_arabia.py. DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, pyarrow.parquet as pq
from shapely.geometry import MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
HJ = unary_union([shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, 'tools/data/v398_sa_regions.parquet')).to_pylist() if r['region'] in {'SA-07', 'SA-03', 'SA-02', 'SA-11'} and r['class'] == 'land'])
V = MP(C['shj']['polys']); V3 = MP(C['me2']['polys'])
print('   Hejaz provinces not yet in V1', round(A(HJ.difference(V))), 'km2')
X = unary_union([V, HJ.buffer(0.003)]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if 0.5 < A(Polygon(h)) < 5000]
X = unary_union([X] + holes).intersection(V3.buffer(0.002))
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km; print('shj', old, '->', km)
Y = MP(o); print('Hejaz provinces outside V1', round(A(HJ.difference(Y.buffer(0.003)))), '| shj outside me2', round(A(Y.difference(V3.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
