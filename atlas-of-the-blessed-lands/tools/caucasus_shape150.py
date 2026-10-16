"""Version 150 (2026-10-16, Nawaz, sending the orange Caucasus close-up again with a screenshot of Version 149's border). Version
149 still bent the orange edge (a dip in the middle, a rise to the Caspian) because the sketch had been stretched to fit real
places. Now the orange top edge's own SHAPE is copied undistorted: traced from reference/v146_caucasus_request.jpg and placed by a
similarity (move, turn, scale only; equal scale both ways at 45° N) that pins its two ends: the Kerch Strait at Taman and the
Caspian shore where Version 147's fit put its end (44.27 N). Smoothed lightly; no town bumps. Russia south of it (land only,
Crimea out) replaces the North Caucasus zone of V2 and V2-B. Writes tools/data/caucasus_line150.json, caucasus_shape150.geojson."""
import json, math, os, subprocess, numpy as np, shapely
from PIL import Image
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, mapping
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
im = np.asarray(Image.open(os.path.join(P, 'reference/v146_caucasus_request.jpg')).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]; og = (r > 200) & (g > 80) & (g < 150) & (b < 60)
ys, xs = np.nonzero(og); top = []
for x in range(xs.min(), xs.max() + 1):
    c = np.nonzero(og[:, x])[0]
    if not len(c): continue
    if top and c.min() - top[-1][1] > 12: break        # the edge reaches the Caspian; the orange then runs down the coast
    top.append((x, c.min()))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
lat_e = 44.27
cut = RU.intersection(LineString([(45.5, lat_e), (48.5, lat_e)]))
lon_e = max(c[0] for gg in getattr(cut, 'geoms', [cut]) for c in gg.coords)
W0, E0 = (36.66, 45.30), (lon_e, lat_e)                      # Kerch Strait at Taman; the Caspian shore
k = math.cos(math.radians(45))
z0, z1 = complex(*top[0][:1], -top[0][1]), complex(top[-1][0], -top[-1][1])
z0 = complex(top[0][0], -top[0][1])
w0, w1 = complex(W0[0] * k, W0[1]), complex(E0[0] * k, E0[1])
a = (w1 - w0) / (z1 - z0); bb = w0 - a * z0
ll = [((a * complex(x, -y) + bb).real / k, (a * complex(x, -y) + bb).imag) for x, y in top]
def chaikin(c, n=3):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
Ls = chaikin(list(LineString(ll).simplify(0.02).coords), 3)
print('ends', [round(v, 3) for v in Ls[0]], [round(v, 3) for v in Ls[-1]], 'lowest', round(min(p[1] for p in Ls), 3), 'highest', round(max(p[1] for p in Ls), 3))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'orange top edge, shape copied undistorted (similarity on its two ends)'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'caucasus_line150.json'), 'w'))
R = Polygon([(36.3, Ls[0][1])] + Ls + [(48.6, Ls[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
reg = R.intersection(RU).difference(cr)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 150 Caucasus (orange shape)'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'caucasus_shape150.geojson'), 'w'))
RZ = shape(json.load(open(os.path.join(D, 'caucasus_zone148.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for kk in ('x', 'xb'):
    X = MultiPolygon([Polygon(p[0], p[1:]) for p in C[kk]['polys']]).buffer(0)
    X = shapely.union_all([shapely.make_valid(X.difference(RZ)), shapely.make_valid(reg)], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    C[kk]['polys'] = out
    C[kk]['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    print(kk, 'North Caucasus', round(A(reg)), 'km2; total', C[kk]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
