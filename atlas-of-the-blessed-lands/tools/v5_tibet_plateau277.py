"""Version 277 (Nawaz: "Is the entire Tibetan plateau in V5?" -> 98.9%; "Yes" to a preview; "Make sure it's 100 percent inside and apply").
V5 (CALIPH.v2, the Super Caliphate) gains tools/data/v5_tibet_plateau277.geojson: 11 whole Overture 2026-10-21.0 counties holding the
plateau edges outside Greater Tibet (Gansu: Sunan Yugur, Shandan; Sichuan: Pingwu, Baoxing, Shimian, Mianning, Yanyuan; Yunnan: Yulong,
Ninglang, Lanping, Jianchuan), the last thin plateau slivers (~3,200 km2 in 22 other counties) taken exactly as the 3000 m line draws them,
and gap pockets (between Sunan's pieces near Jiuquan, the Nujiang strip by Myanmar, one near Lijiang). The plateau used is
tools/data/tibetan_plateau_3000m.geojson (connected land above 3000 m, Mapzen terrain tiles at zoom 5): 100% inside V5 after this."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
W = shape(json.load(open(os.path.join(P, 'tools/data/v5_tibet_plateau277.geojson')))['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
PL = shape(json.load(open(os.path.join(P, 'tools/data/tibetan_plateau_3000m.geojson')))['geometry']).buffer(0)
print('plateau outside V5:', round(A(PL.difference(Y)), 2), 'km2')
row = {'id': '156_P', 'n': 'China: the Tibetan Plateau’s edges beyond Greater Tibet (Qilian Mountains in Gansu, the eastern rim in Sichuan, Lijiang and Nujiang in Yunnan; whole counties and the last slivers above 3000 m)', 'km2': round(A(W.difference(V))), 'pct': None}
row['pct'] = round(100 * row['km2'] / 9600000, 1)
print('V5 (v2)', C['v2']['km2'], '->', km2, row)
C['v2'].update(polys=out, km2=km2, states=[r for r in C['v2']['states'] if r['id'] != '156_P'] + [row])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
