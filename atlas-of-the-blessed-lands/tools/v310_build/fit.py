"""Version 310: fit reference/v310_ottoman_1683_full_map.jpg (the full 1683 map) to lon/lat on its marked European cities (dots found
by darkest-blob search; 19 found, the 8 in Europe used), affine (K=3); writes tools/v310_build/tf.json and an overlay of Natural Earth coasts for checking."""
import json, sys, os, subprocess, numpy as np, shapely
from shapely.geometry import shape, box
from PIL import Image, ImageDraw
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
cp = {'Vienna': ((438.5, 120.3), (16.37, 48.21)), 'Budapest': ((485.0, 140.0), (19.04, 47.50)), 'Belgrade': ((499.5, 191.7), (20.46, 44.79)),
      'Sofia': ((547.0, 241.6), (23.32, 42.70)), 'Constantinople': ((624.2, 269.6), (28.98, 41.01)), 'Athens': ((540.2, 326.9), (23.73, 37.98)),
      'Venice': ((375.4, 183.6), (12.33, 45.44)), 'Rome': ((382.0, 253.8), (12.50, 41.90)), 'Tunis': ((338.8, 340.2), (10.18, 36.80)),
      'Algiers': ((190.1, 356.4), (3.06, 36.75)), 'Tripoli': ((377.5, 419.0), (13.18, 32.89)), 'Alexandria': ((654.8, 456.2), (29.92, 31.20)),
      'Cairo': ((658.4, 480.6), (31.24, 30.04)), 'Jerusalem': ((723.5, 455.3), (35.22, 31.78)), 'Damascus': ((744.6, 406.2), (36.29, 33.51)),
      'Baghdad': ((867.5, 424.7), (44.36, 33.31)), 'Baku': ((956.7, 286.6), (49.87, 40.41)), 'Medina': ((793.0, 574.0), (39.61, 24.47)), 'Mecca': ((787.4, 626.6), (39.83, 21.42))}
EU = ['Vienna', 'Budapest', 'Belgrade', 'Sofia', 'Constantinople', 'Athens', 'Venice', 'Rome']   # only the Balkans are used, so fit on Europe
cp = {k: cp[k] for k in EU}
ll = np.array([v[1] for v in cp.values()]); px = np.array([v[0] for v in cp.values()])
K = int(os.environ.get('K', 3))
feat = lambda lo, la: np.c_[np.ones_like(lo), lo, la, lo * lo, lo * la, la * la][:, :K]
F = feat(ll[:, 0], ll[:, 1]); cx = np.linalg.lstsq(F, px[:, 0], rcond=None)[0]; cy = np.linalg.lstsq(F, px[:, 1], rcond=None)[0]
for n, r in zip(cp, np.c_[F @ cx, F @ cy] - px): print(n, np.round(r, 1))
json.dump({'cx': list(cx), 'cy': list(cy), 'k': K}, open(os.path.join(P, 'tools/v310_build/tf.json'), 'w'))
if len(sys.argv) > 1:
    geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
    land = shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(box(-5, 10, 60, 55))])
    img = Image.open(os.path.join(P, 'reference/v310_ottoman_1683_full_map.jpg')).convert('RGB'); dr = ImageDraw.Draw(img)
    for p in getattr(land, 'geoms', [land]):
        if p.area < 0.3: continue
        for ring in [p.exterior, *p.interiors]:
            c = np.array(ring.coords); f = feat(c[:, 0], c[:, 1]); dr.line(list(zip(f @ cx, f @ cy)), fill=(0, 0, 255), width=1)
    img.save(sys.argv[1])
