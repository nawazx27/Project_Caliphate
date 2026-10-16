"""Version 155 (2026-10-16, Nawaz, with a red X over Version 153's line and his orange Caucasus map: "Your rendering is way too
straight"). Two faults in Versions 150-154: (1) the tracing of the orange edge stopped where the "Caucasus" label's pointer line crosses
it (x = 657 of 1408), so the last third of the edge, its flat run into the Caspian, was missing and the rest was stretched over the whole
width; (2) Version 154 pinned the east end at 44.27 N, which squashed the drop to 0.86 degrees. Now the whole edge is traced (columns
crossed by the pointer line are skipped), from the Black Sea mouth of the Kerch Strait to the Caspian shore, and placed with ONE scale
per axis fitted to three points the sketch shares with the real map (the Kerch Strait mouth, the Psou mouth on the Russia-Georgia
border, the Samur mouth on the Russia-Azerbaijan border; 39.4 px per degree of longitude, 110.2 px per degree of latitude), north-up,
so the edge falls about 1.4 degrees, as on his map, and runs flat into the Caspian. Near the Caspian the edge's own small rise into the
coast is raised by 0.26 degrees (smoothly, 45.9-46.8 E) so that Greater Georgia's Dagestan block (Version 152) stays inside without a
bump. Chaikin-smoothed; no town bumps (as Versions 150-154). V2 only (V2-B keeps the modern borders): Russia south of the edge
(Crimea out) replaces caucasus_shape154 in whole_slivers.py; Greater Georgia stays. Run: python3 tools/caucasus_shape155.py"""
import json, os, subprocess, numpy as np, shapely
from PIL import Image
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
import glob
import numpy as np
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
im = np.asarray(Image.open(os.path.join(P, 'reference/v146_caucasus_request.jpg')).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]; og = (r > 200) & (g > 80) & (g < 150) & (b < 60)
top = []
for x in range(378, 769):                      # the orange's top edge, Kerch Strait mouth (x 378) to the Caspian shore (x 768)
    c = np.nonzero(og[450:, x])[0]
    if not len(c): continue
    y = c.min() + 450
    if top and abs(y - top[-1][1]) > 6: continue   # the label's pointer line crosses the edge at x 657-660
    top.append((x, y))
top = np.array(top, float)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
# one scale per axis, fitted to the Kerch Strait mouth, the Psou mouth and the Samur mouth (sketch px -> degrees)
ky = np.polyfit([542, 702, 900], [45.13, 43.386, 41.86], 1)[0]
kx = np.polyfit([378, 485, 840], [36.65, 40.006, 48.58], 1)[0]
ll = np.c_[36.65 + (top[:, 0] - 378) * kx, 45.13 + (top[:, 1] - 542) * ky]
def coast_lon(la):
    cut = RU.intersection(LineString([(45.5, la), (48.5, la)]))
    return max(c[0] for gg in getattr(cut, 'geoms', [cut]) for c in gg.coords)
def chaikin(c, n=3):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
ll[:, 0] = 36.65 + (ll[:, 0] - 36.65) * (coast_lon(ll[-1, 1]) - 36.65) / (ll[-1, 0] - 36.65)
Ls = chaikin(list(LineString(ll).simplify(0.02).coords), 3)
Ls = np.array(Ls)
GG = unary_union([shape(f['geometry']).buffer(0) for q in [os.path.join(D, 'greater_georgia152.geojson')] + sorted(glob.glob(os.path.join(D, 'expand_towns152_*_x.geojson'))) for f in json.load(open(q))['features']])
R0 = Polygon([(36.3, Ls[0][1] - 0.4)] + [tuple(p) for p in Ls] + [(48.6, Ls[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
o = GG.difference(R0); need = 0.0
for q in getattr(o, 'geoms', [o]):
    if q.geom_type == 'Polygon':
        for x, y in q.exterior.coords: need = max(need, y + 0.03 - float(np.interp(x, Ls[:, 0], Ls[:, 1])))
t = np.clip((Ls[:, 0] - 45.9) / 0.9, 0, 1); Ls[:, 1] += need * (3 * t * t - 2 * t * t * t)   # the rise into the Caspian shore
# the edge ends on the Caspian coast's turning point (the little cape at 44.22 N, 47.24 E; Nawaz circled the notch north of the end), not 0.09 degrees south of it
t2 = np.clip((Ls[:, 0] - 46.4) / (Ls[-1, 0] - 46.4), 0, 1); Ls[:, 1] += (44.22 - Ls[-1, 1]) * t2 ** 2 * 1.0
e = coast_lon(Ls[-1, 1]); Ls[:, 0] = np.where(Ls[:, 0] > 46.0, Ls[:, 0] + (e - Ls[-1, 0]) * np.clip((Ls[:, 0] - 46.0) / (Ls[-1, 0] - 46.0), 0, 1), Ls[:, 0])
Ls = [tuple(p) for p in Ls]
print('raised at the Caspian end by', round(need, 3))
print('ends', [round(v, 3) for v in Ls[0]], [round(v, 3) for v in Ls[-1]], 'highest', round(max(p[1] for p in Ls), 3), 'lowest', round(min(p[1] for p in Ls), 3))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'orange top edge, whole, one scale per axis (Version 155)'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'caucasus_line155.json'), 'w'))
R = Polygon([(36.3, Ls[0][1] - 0.4)] + Ls + [(48.6, Ls[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
reg = R.intersection(RU).difference(cr)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 155 Caucasus (orange, whole edge)'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'caucasus_shape155.geojson'), 'w'))
RZ = shape(json.load(open(os.path.join(D, 'caucasus_zone148.geojson')))['features'][0]['geometry']).buffer(0)
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
