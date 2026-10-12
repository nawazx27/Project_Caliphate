"""Fetch elevation for a box from the open Mapzen terrain tiles (archive.org item terrain_mapzen_pmtiles, Terrain-RGB in PMTiles;
data: SRTM, GMTED, ETOPO1 and others, see https://github.com/tilezen/joerd/blob/master/docs/attribution.md).
Usage: python3 tools/dem_fetch.py west south east north zoom out.npz   (only the needed tiles are read, by HTTP range requests)"""
import sys, io, math, time, urllib.request, numpy as np
from PIL import Image
from pmtiles.reader import Reader
URL = 'https://ia600905.us.archive.org/33/items/terrain_mapzen_pmtiles/terrain.pmtiles'
def get_bytes(offset, length):
    for i in range(5):
        try:
            req = urllib.request.Request(URL, headers={'Range': f'bytes={offset}-{offset+length-1}', 'User-Agent': 'atlas-of-the-blessed-lands/1.0'})
            with urllib.request.urlopen(req, timeout=120) as r: return r.read()
        except Exception as e:
            time.sleep(3 * (i + 1)); err = e
    raise err
W, S, E, N, Z = map(float, sys.argv[1:6]); Z = int(Z); out = sys.argv[6]
n = 2 ** Z
tx = lambda lon: int((lon + 180) / 360 * n)
ty = lambda lat: int((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n)
x0, x1, y0, y1 = tx(W), tx(E), ty(N), ty(S)
rd = Reader(get_bytes)
TS = 512   # the tiles are 512 pixels square
mos = np.zeros(((y1 - y0 + 1) * TS, (x1 - x0 + 1) * TS), np.float32)
for y in range(y0, y1 + 1):
    for x in range(x0, x1 + 1):
        t = rd.get(Z, x, y)
        a = np.asarray(Image.open(io.BytesIO(t)).convert('RGB')).astype(np.float64)
        h = -10000 + (a[..., 0] * 65536 + a[..., 1] * 256 + a[..., 2]) * 0.1   # Terrain-RGB (Mapbox) decoding
        mos[(y - y0) * TS:(y - y0 + 1) * TS, (x - x0) * TS:(x - x0 + 1) * TS] = h
    print('row', y - y0 + 1, 'of', y1 - y0 + 1, flush=True)
np.savez_compressed(out, h=mos, z=Z, x0=x0, y0=y0, ts=TS)
print('saved', out, mos.shape, 'min', mos.min(), 'max', mos.max())
