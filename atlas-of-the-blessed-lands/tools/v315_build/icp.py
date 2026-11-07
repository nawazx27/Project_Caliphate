"""Version 315: fit reference/v315_roman_rule_map_hires.jpg (a sharper redraw of the Roman-rule map) to lon/lat. Start: the Version 305
fit of the original map (tools/v305_build/tf2.json) carried over by the best scale and shift between the two images (purple overlap 0.91);
then iterative closest point between Natural Earth coastlines and this image's black coast lines / water edge, cubic. Writes tf.json."""
import json, sys, os, subprocess, numpy as np, shapely
from shapely.geometry import shape, box
from scipy import ndimage
from PIL import Image, ImageDraw
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
IMG = os.path.join(P, 'reference/v315_roman_rule_map_hires.jpg')
im = np.array(Image.open(IMG).convert('RGB')).astype(int); H, W = im.shape[:2]
r, g, b = im[..., 0], im[..., 1], im[..., 2]
blk = im.max(2) < 70
water = (b > 200) & (g > 190) & (r > 150) & (r < 215) & (b - r > 20)
water = ndimage.binary_opening(water, iterations=1)
tgt = blk | (water ^ ndimage.binary_erosion(water))
dt, ind = ndimage.distance_transform_edt(~tgt, return_indices=True)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(box(-12, 12, 55, 58))]).simplify(0.02)
pts = []
for p in getattr(land, 'geoms', [land]):
    if p.area < 0.3: continue
    pts.append(np.array(p.exterior.segmentize(0.15).coords))
Pp = np.vstack(pts); Pp = Pp[(Pp[:, 0] > -12) & (Pp[:, 0] < 55) & (Pp[:, 1] > 12) & (Pp[:, 1] < 58)]
feat = lambda lo, la: np.c_[np.ones_like(lo), lo, la, lo * lo, lo * la, la * la, lo ** 3, lo * lo * la, lo * la * la, la ** 3]
t0 = json.load(open(os.path.join(P, 'tools/v305_build/tf2.json'))); k0 = t0['cols']
F = feat(Pp[:, 0], Pp[:, 1])
ox = F[:, :k0] @ np.array(t0['cx']); oy = F[:, :k0] @ np.array(t0['cy'])
sx, sy, dx, dy = 909 * 0.99 / W, 765 * 0.99 / H, 4, 2          # old = new * s + d
x = (ox - dx) / sx; y = (oy - dy) / sy
for it, thr in enumerate([30, 24, 18, 14, 10, 8, 6, 5, 5, 4]):
    ok = (x >= 0) & (x < W) & (y >= 0) & (y < H)
    xi = np.clip(x.astype(int), 0, W - 1); yi = np.clip(y.astype(int), 0, H - 1)
    d = dt[yi, xi]; sel = ok & (d < thr)
    cx = np.linalg.lstsq(F[sel], ind[1][yi, xi][sel], rcond=None)[0]; cy = np.linalg.lstsq(F[sel], ind[0][yi, xi][sel], rcond=None)[0]
    x = F @ cx; y = F @ cy
    print(it, 'used', int(sel.sum()), 'median px', round(float(np.median(d[ok])), 2))
json.dump({'cx': list(cx), 'cy': list(cy), 'cols': 10}, open(os.path.join(P, 'tools/v315_build/tf.json'), 'w'))
if len(sys.argv) > 1:
    img = Image.open(IMG).convert('RGB'); dr = ImageDraw.Draw(img)
    for c in pts:
        f = feat(c[:, 0], c[:, 1]); dr.line(list(zip(f @ cx, f @ cy)), fill=(255, 0, 0), width=2)
    img.save(sys.argv[1])
