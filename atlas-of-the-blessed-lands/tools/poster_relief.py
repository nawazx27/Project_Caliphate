"""Warp the colour shaded relief (tools/relief/shadedrelief.jpg, a 10800x5400 plate carree of the world) into a poster's Mercator frame.
Usage: python3 tools/poster_relief.py params.json out.png   (params: k, tx, ty of a d3 geoMercator; x0, y0, w, h of the frame in pixels)"""
import sys, json, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
P = json.load(open(sys.argv[1]))
src = np.asarray(Image.open(sys.argv[3] if len(sys.argv) > 3 else 'tools/relief/shadedrelief.jpg').convert('RGB')).astype(np.float32)
H, W, _ = src.shape
xs = P['x0'] + np.arange(P['w']) + 0.5
ys = P['y0'] + np.arange(P['h']) + 0.5
lon = np.degrees((xs - P['tx']) / P['k'])
lat = np.degrees(2*np.arctan(np.exp((P['ty'] - ys) / P['k'])) - np.pi/2)
cx = (lon + 180) / 360 * W - 0.5
cy = (90 - lat) / 180 * H - 0.5
X, Y = np.meshgrid(cx, cy)
x0 = np.floor(X).astype(int); y0 = np.floor(Y).astype(int); fx = (X - x0)[..., None]; fy = (Y - y0)[..., None]
x0 = np.clip(x0, 0, W-2); y0 = np.clip(y0, 0, H-2)
out = (src[y0, x0]*(1-fx)*(1-fy) + src[y0, x0+1]*fx*(1-fy) + src[y0+1, x0]*(1-fx)*fy + src[y0+1, x0+1]*fx*fy)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(sys.argv[2])
print('relief', out.shape[1], 'x', out.shape[0])
