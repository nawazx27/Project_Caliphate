# Version 227. Usage: python3 make_world_relief.py tools/relief/shadedrelief.jpg /tmp/world 7.5
# writes /tmp/world.npy (grey relief of the whole world in Mercator, 85N-85S, 7.5 px a degree), then:
#   python3 tools/relief/tint_relief.py world /tmp/world.npy relief_world.webp tint 50
# world relief outside the old sheet, same band-pass as tools/relief/make_relief.py; neutral (128) inside the sheet
import numpy as np, sys, os
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, binary_opening
src_path, out_path, PXDEG = sys.argv[1], sys.argv[2], float(sys.argv[3])
im = Image.open(src_path).convert('RGB'); W,H = im.size
a = np.asarray(im).astype(np.float32)
R,G,B = a[...,0],a[...,1],a[...,2]
L = 0.30*R+0.59*G+0.11*B
sea = (B > R + 18) & (B > G + 4)
sea = binary_opening(sea, iterations=1)
land = (~sea).astype(np.float32)
nb = lambda x, r: gaussian_filter(x*land, r, mode='wrap') / (gaussian_filter(land, r, mode='wrap') + 1e-4)
b1, b2 = nb(L, 7), nb(L, 42)
sh = ((L - b1) * 1.15 + (b1 - b2) * 0.55) * land
# same strength as the sheet: scale by the std over the old sheet's land
x0=int((-30+180)/360*W); x1=int((104+180)/360*W); y0=int((90-60)/180*H); y1=int((90+36.5)/180*H)
s = np.std(sh[y0:y1,x0:x1][land[y0:y1,x0:x1] > 0.5]); hp = np.tanh(sh/(1.25*s)) * 112
out = 128 + hp; out[land < 0.5] = 128
LON0,LON1,LAT0,LAT1 = -180,180,-85,85
merc = lambda lat: np.log(np.tan(np.pi/4 + np.radians(lat)/2))
ox = int(round((LON1-LON0)*PXDEG)); oy = int(round(ox * (merc(LAT1)-merc(LAT0)) / np.radians(LON1-LON0)))
ys = merc(LAT1) - (np.arange(oy)+0.5)/oy * (merc(LAT1)-merc(LAT0))
lat_out = np.degrees(2*np.arctan(np.exp(ys)) - np.pi/2)
rows = ((90 - lat_out)/180*H - 0.5)
lon_out = LON0 + (np.arange(ox)+0.5)/ox*(LON1-LON0)
cols = ((lon_out+180)/360*W - 0.5)
RR, CC = np.meshgrid(rows, cols, indexing='ij')
o = map_coordinates(out, [RR, CC], order=1, mode='wrap')
inbox = (lat_out[:,None] < 60) & (lat_out[:,None] > -36.5) & (lon_out[None,:] > -30) & (lon_out[None,:] < 104)
o[inbox] = 128
np.save(out_path + '.npy', o.astype(np.float32))
print(o.shape)
