import json, sys, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_fill_holes, binary_closing, label, binary_dilation
from rasterio.features import shapes
from rasterio.transform import Affine
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
S, OUT = sys.argv[1], sys.argv[2]
im=np.array(Image.open(S+'/waz.png').convert('RGB')).astype(int)
gray=(abs(im[...,0]-227)<6)&(abs(im[...,1]-232)<6)&(abs(im[...,2]-232)<6)
red=(im[...,0]>100)&(im[...,0]<200)&(im[...,1]<70)&(im[...,2]<70)
blk=im.sum(-1)<330
reg=gray|red|(blk&binary_dilation(gray,iterations=6))
reg=binary_closing(reg,iterations=3); reg=binary_fill_holes(reg)
lab,n=label(reg); sizes=np.bincount(lab.ravel()); sizes[0]=0; keep=lab==sizes.argmax()
Mx=np.load(S+'/waz_M.npy'); Ai=np.linalg.inv(Mx[:2].T); b=Mx[2]
inv_m=lambda y: np.degrees(2*np.arctan(np.exp(np.radians(y)))-np.pi/2)
def px2ll(x,y):
  v=Ai@(np.array([x,y])-b); return (v[0], inv_m(v[1]))
polys=[]
for g,v in shapes(keep.astype(np.uint8), mask=keep, transform=Affine.identity()):
  rings=[[px2ll(x,y) for x,y in r] for r in g['coordinates']]; polys.append(Polygon(rings[0], rings[1:]))
P=unary_union(polys).buffer(0)
P=unary_union([Polygon(q.exterior) for q in getattr(P,'geoms',[P])]).simplify(0.008)
print('pieces',len(getattr(P,'geoms',[P])),'| traced area km2', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(P)[0])/1e6), [round(v,2) for v in P.bounds])
json.dump({'type':'Feature','properties':{'n':'Whole Azerbaijan, traced from his map IMG_5482 (the shaded area inside the red line)'},'geometry':mapping(P)},open(OUT,'w'))
d=Image.open(S+'/waz.png').convert('RGB'); dr=ImageDraw.Draw(d)
lat2y=lambda la: np.degrees(np.log(np.tan(np.pi/4+np.radians(la)/2)))
for q in getattr(P,'geoms',[P]):
  c=np.array(q.exterior.coords); X=np.c_[c[:,0],lat2y(c[:,1]),np.ones(len(c))]@Mx
  dr.line(list(map(tuple,X)),fill=(0,170,0),width=4)
d.save(S+'/waz_chk.png')
