"""Trace the red 'Boundary of the Nile Basin' line of Nawaz's Wikimedia Nile-basin map (1920x3575) into lon/lat, placed by the 12 labelled yellow
dots of the same base map (affine fit in lon and Mercator y). Writes nile_basin.geojson."""
import numpy as np, json, sys
from PIL import Image
from scipy import ndimage as nd
from shapely.geometry import Polygon, mapping, Point
from shapely.ops import unary_union
U = '/root/.claude/uploads/e227bf79-e0c6-5974-a79a-4f0672b36775/'
K = 1.7877
P = [((544,174),(31.24,30.05)),((630,471),(32.88,23.97)),((499,758),(30.48,19.17)),((701,865),(33.98,17.70)),((616,986),(32.51,15.62)),
     ((783,995),(35.90,14.93)),((705,1168),(34.39,11.80)),((545,1287),(31.66,9.53)),((566,1521),(31.77,5.20)),((580,1656),(31.68,2.28)),((636,1751),(33.19,0.43))]
merc = lambda la: np.degrees(np.log(np.tan(np.pi/4 + np.radians(la)/2)))
px = np.array([p[0] for p in P], float); ll = np.array([p[1] for p in P], float)
M = np.c_[np.ones(len(P)), px[:,0], px[:,1]]
cl, *_ = np.linalg.lstsq(M, ll[:,0], rcond=None); cm, *_ = np.linalg.lstsq(M, merc(ll[:,1]), rcond=None)
def tolonlat(x, y):
    lon = cl[0] + cl[1]*x + cl[2]*y; my = cm[0] + cm[1]*x + cm[2]*y
    lat = np.degrees(2*np.arctan(np.exp(np.radians(my))) - np.pi/2); return lon, lat
lon, lat = tolonlat(px[:,0], px[:,1]); res = np.hypot((lon-ll[:,0])*np.cos(np.radians(ll[:,1])), lat-ll[:,1])*111
print('control-point errors km:', np.round(res).astype(int), 'mean', round(res.mean()))
a = np.array(Image.open(U+'cbc5b55e-image.webp').convert('RGB')).astype(int)
red = (a[...,0] > 190) & (a[...,1] < 80) & (a[...,2] < 80)
for it in (4, 8, 14, 22):
    rr = nd.binary_dilation(red, iterations=it); rr[170:186, 755:1070] = True     # close the Mediterranean mouth
    inside = nd.binary_fill_holes(rr) & ~rr
    lab, n = nd.label(inside); kx, ky = int(616*K), int(986*K)
    if lab[ky, kx] and (lab == lab[ky, kx]).sum() > 1e6: print('bridged with dilation', it); break
reg0 = nd.binary_dilation(lab == lab[ky, kx], iterations=it)   # back out to the middle of the line
inside = reg0
reg = inside
reg = nd.binary_opening(reg, iterations=2)
import skimage.measure as sm
c = max(sm.find_contours(reg.astype(float), 0.5), key=len)
xd, yd = c[:,1]/K, c[:,0]/K; lo, la_ = tolonlat(xd, yd)
poly = Polygon(np.c_[lo, la_]).buffer(0).simplify(0.01)
print('basin polygon area deg2', round(poly.area,1), 'bounds', [round(v,2) for v in poly.bounds])
json.dump({'type':'Feature','properties':{'n':'Nile basin (traced from the Wikimedia map Nawaz sent)'},'geometry':mapping(poly)}, open('nile_basin.geojson','w'))
