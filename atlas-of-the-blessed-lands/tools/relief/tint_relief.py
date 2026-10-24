# Version 227: warms the grey relief to brown ink (shadows brown, highlights cream; 128 stays neutral).
# core:  python3 tools/relief/tint_relief.py core <grey relief from make_relief.py> relief_full.webp tint 62
# world: python3 tools/relief/tint_relief.py world /tmp/world.npy relief_world.webp tint 50
import numpy as np, sys
from PIL import Image
# warm the grey overlay: shadows lean brown, highlights lean cream; flat (128) stays neutral so nothing shifts where there is no relief
def tint(g, sh=(0.80,0.98,1.28), hi=(1.08,1.0,0.78)):
    d = g.astype(np.float32) - 128
    k = np.where(d[...,None] < 0, np.array(sh), np.array(hi))
    return np.clip(128 + d[...,None]*k, 0, 255).astype(np.uint8)
mode = sys.argv[1]
if mode == 'core':
    g = np.asarray(Image.open(sys.argv[2]).convert('L'))
else:
    g = np.load(sys.argv[2])
img = Image.fromarray(tint(g)) if sys.argv[4] == 'tint' else Image.fromarray(np.clip(g,0,255).astype(np.uint8))
img.save(sys.argv[3], quality=int(sys.argv[5]), method=6); import os; print(sys.argv[3], img.size, os.path.getsize(sys.argv[3]))
