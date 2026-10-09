import numpy as np, os
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, binary_opening
im = Image.open('dem/shadedrelief.jpg').convert('RGB'); W,H = im.size
LON0,LON1,LAT0,LAT1 = -30,104,-36.5,60
PXDEG = 20
a = np.asarray(im).astype(np.float32)
x0=int((LON0+180)/360*W)-8; x1=int((LON1+180)/360*W)+8
y0=int((90-LAT1)/180*H)-8; y1=int((90-LAT0)/180*H)+8
src = a[y0:y1, x0:x1]
R,G,B = src[...,0],src[...,1],src[...,2]
L = 0.30*R+0.59*G+0.11*B
sea = (B > R + 18) & (B > G + 4)
sea = binary_opening(sea, iterations=1)
land = (~sea).astype(np.float32)
# two-scale band-pass of the luminance, blurred over land only so coasts leave no halo:
# fine ridges plus mid-scale slopes; the hypsometric colour tint lives mostly at larger scales and drops out
nb = lambda x, r: gaussian_filter(x*land, r) / (gaussian_filter(land, r) + 1e-4)
b1, b2 = nb(L, 7), nb(L, 42)
sh = ((L - b1) * 1.15 + (b1 - b2) * 0.55) * land
s = np.std(sh[land > 0.5]); hp = np.tanh(sh/(1.25*s)) * 112
out = 128 + hp; out[land < 0.5] = 128
merc = lambda lat: np.log(np.tan(np.pi/4 + np.radians(lat)/2))
ox = int(round((LON1-LON0)*PXDEG)); oy = int(round(ox * (merc(LAT1)-merc(LAT0)) / np.radians(LON1-LON0)))
ys = merc(LAT1) - (np.arange(oy)+0.5)/oy * (merc(LAT1)-merc(LAT0))
lat_out = np.degrees(2*np.arctan(np.exp(ys)) - np.pi/2)
rows = ((90 - lat_out)/180*H - 0.5) - y0
lon_out = LON0 + (np.arange(ox)+0.5)/ox*(LON1-LON0)
cols = ((lon_out+180)/360*W - 0.5) - x0
RR, CC = np.meshgrid(rows, cols, indexing='ij')
o = map_coordinates(out, [RR, CC], order=1, mode='nearest')
img = Image.fromarray(np.clip(o,0,255).astype(np.uint8))
img.save('atlas/relief_full.webp', quality=66, method=6)
print(img.size, os.path.getsize('atlas/relief_full.webp'))
img.resize((img.size[0]//2, img.size[1]//2)).save('dem/preview.png')
