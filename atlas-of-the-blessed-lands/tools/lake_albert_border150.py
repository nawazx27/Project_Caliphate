"""Version 150 (2026-10-16, Nawaz, on a close-up of V2 at Lake Albert with a smooth black line drawn a little inland of the DR Congo
shore: "Lake Albert draw a border professionally"). The border along the lake's west side, which hugged the shore, is replaced by
his line (traced from reference/v150_lake_albert_request.jpg, fitted on the gold V2 edge; smoothed): all land between it and the
lake is added to V2 and V2-B. Writes tools/data/lake_albert_line150.json and lake_albert_border150.geojson. Run:
python3 tools/lake_albert_border150.py <fit.json>"""
import json, math, os, sys, subprocess, numpy as np
from PIL import Image
from shapely.geometry import LineString, Polygon, shape, mapping
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
f = json.load(open(sys.argv[1])); a, tx, ty = f['a'], f['tx'], f['ty']
Mi = lambda y: math.degrees(2 * math.atan(math.exp(math.radians(y))) - math.pi / 2)
im = np.asarray(Image.open(os.path.join(P, 'reference/v150_lake_albert_request.jpg')).convert('RGB')).astype(int)
blk = im.max(axis=2) < 45
ys, xs = np.nonzero(blk)
pts = []
for y in range(ys.min(), ys.max() + 1, 2):
    m = (ys >= y) & (ys < y + 2)
    if m.sum(): pts.append((np.median(xs[m]), y + 1))
ll = [((x - tx) / a, Mi((ty - y) / a)) for x, y in pts]
def chaikin(c, n=4):
    for _ in range(n):
        out = [c[0]]
        for p, q in zip(c, c[1:]): out += [(0.75*p[0]+0.25*q[0], 0.75*p[1]+0.25*q[1]), (0.25*p[0]+0.75*q[0], 0.25*p[1]+0.75*q[1])]
        c = out + [c[-1]]
    return c
Ls = chaikin(list(LineString(ll).simplify(0.004).coords), 4)
print('line', [round(v, 3) for v in Ls[0]], '->', [round(v, 3) for v in Ls[-1]], len(Ls))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'Nawaz line west of Lake Albert, smoothed'}, 'geometry': mapping(LineString(Ls))}]}, open(os.path.join(D, 'lake_albert_line150.json'), 'w'))
# close it through the lake (east of the line): from its south end into the lake, up the lake, back to its north end
n, s = (Ls[0], Ls[-1]) if Ls[0][1] > Ls[-1][1] else (Ls[-1], Ls[0])
lake = [shape(g['geometry']).buffer(0) for g in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if g['properties'].get('name') == 'Lake Albert'][0]
c = lake.centroid
R = Polygon(Ls + [(c.x, c.y)]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CD = [shape(g['geometry']).buffer(0) for g in geo['features'] if str(g['id']) == '180'][0]
reg = unary_union([R.intersection(CD), lake])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 150 Lake Albert border'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'lake_albert_border150.geojson'), 'w'))
print('DR Congo land between the line and the lake', round(A(R.intersection(CD).difference(lake))), 'km2')
