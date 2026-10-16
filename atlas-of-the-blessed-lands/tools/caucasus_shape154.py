"""Version 154 (2026-10-16, Nawaz, close-ups of his orange Caucasus map: "Look at the edges carefully"). Version 150/153 pinned the
orange edge's two ends with a similarity (move, TURN, scale), which tilted it: the line rose north from Taman and took in the
Taman peninsula's north and the Azov shore, which the orange leaves out. Now the edge is copied north-up (no turning): its west end
at the Black Sea mouth of the Kerch Strait (Cape Panagia, 36.65 E 45.13 N, where the orange begins), its east end on the Caspian
shore at 44.27 N, the sketch's horizontal and vertical proportions of the edge kept (stretched separately to fit the two ends), so
it falls from the strait and runs flat into the Caspian as drawn. Smoothed lightly; no town bumps. V2 only (V2-B keeps the modern
borders): Russia south of it (Crimea out) replaces caucasus_shape150; Greater Georgia (Version 152) stays. Run: python3
tools/caucasus_shape154.py"""
import json, os, subprocess, numpy as np, shapely
from PIL import Image
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import glob
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
im = np.asarray(Image.open(os.path.join(P, 'reference/v146_caucasus_request.jpg')).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]; og = (r > 200) & (g > 80) & (g < 150) & (b < 60)
ys, xs = np.nonzero(og); top = []
for x in range(xs.min(), xs.max() + 1):
    c = np.nonzero(og[:, x])[0]
    if not len(c): continue
    if top and c.min() - top[-1][1] > 12: break
    top.append((x, c.min()))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
lat_e = 44.27
cut = RU.intersection(LineString([(45.5, lat_e), (48.5, lat_e)]))
lon_e = max(c[0] for gg in getattr(cut, 'geoms', [cut]) for c in gg.coords)
W0, E0 = (36.65, 45.13), (lon_e, lat_e)
x0, y0 = top[0]; x1 = top[-1][0]
ymax = max(y for _, y in top)
# x: tip -> coast; y: the edge's drop from the tip to its lowest (flat) part maps to tip lat -> end lat
ll = [(W0[0] + (x - x0) / (x1 - x0) * (E0[0] - W0[0]), W0[1] - (y - y0) / (ymax - y0) * (W0[1] - E0[1])) for x, y in top]
def chaikin(c, n=3):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
Ls = chaikin(list(LineString(ll).simplify(0.02).coords), 3)
print('ends', [round(v, 3) for v in Ls[0]], [round(v, 3) for v in Ls[-1]], 'highest', round(max(p[1] for p in Ls), 3), 'lowest', round(min(p[1] for p in Ls), 3))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'orange top edge copied north-up (Version 154)'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'caucasus_line154.json'), 'w'))
R = Polygon([(36.3, Ls[0][1] - 0.4)] + Ls + [(48.6, Ls[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
reg = R.intersection(RU).difference(cr)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 154 Caucasus (orange, north-up)'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'caucasus_shape154.geojson'), 'w'))
RZ = shape(json.load(open(os.path.join(D, 'caucasus_zone148.geojson')))['features'][0]['geometry']).buffer(0)
GG = unary_union([shape(f['geometry']).buffer(0) for q in [os.path.join(D, 'greater_georgia152.geojson')] + sorted(glob.glob(os.path.join(D, 'expand_towns152_*_x.geojson'))) for f in json.load(open(q))['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
X = MultiPolygon([Polygon(p[0], p[1:]) for p in C['x']['polys']]).buffer(0)
X = shapely.union_all([shapely.make_valid(X.difference(RZ)), shapely.make_valid(reg), shapely.make_valid(GG.difference(cr))], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon': continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
C['x']['polys'] = out
C['x']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
print('x orange Caucasus', round(A(reg)), 'km2; total', C['x']['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
