import json,sys,subprocess,numpy as np,shapely
from shapely.geometry import shape,box,Polygon,MultiPolygon
from scipy import ndimage
from PIL import Image
from rasterio import features
from rasterio.transform import Affine
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
im=np.array(Image.open('/root/.claude/uploads/e227bf79-e0c6-5974-a79a-4f0672b36775/e1e2f3fb-image.jpg').convert('RGB')).astype(int)
H,W=im.shape[:2]; r,g,b=im[...,0],im[...,1],im[...,2]
purple=((r-g>40)&(b-g>40))|((r<90)&(g<40)&(b<90)&(r>15))
water=(b>200)&(g>190)&(r>150)&(r<205)&(b-r>25)
m=ndimage.binary_closing(purple,iterations=2)
m=ndimage.binary_fill_holes(m)
lab,n=ndimage.label(m); sizes=ndimage.sum(m,lab,range(1,n+1))
m=np.isin(lab,1+np.nonzero(sizes>=8)[0])
tf=json.load(open(S+'/rmap/tf2.json')); cx=np.array(tf['cx']); cy=np.array(tf['cy']); cols=tf['cols']
def feat(lon,lat): return np.c_[np.ones_like(lon),lon,lat,lon*lon,lon*lat,lat*lat,lon**3,lon*lon*lat,lon*lat*lat,lat**3][:,:cols]
step=0.04; lons=np.arange(-12,56,step); lats=np.arange(10,60,step)
LO,LA=np.meshgrid(lons,lats); F=feat(LO.ravel(),LA.ravel())
x=(F@cx).round().astype(int); y=(F@cy).round().astype(int)
ok=(x>=0)&(x<W)&(y>=0)&(y<H)
grid=np.zeros(LO.size,bool); grid[ok]=m[y[ok],x[ok]]; grid=grid.reshape(LO.shape)
T=Affine(step,0,lons[0]-step/2,0,step,lats[0]-step/2)
shp=[shape(s) for s,v in features.shapes(grid.astype(np.uint8),transform=T) if v==1]
R=shapely.union_all(shp).buffer(0.02).buffer(-0.02)
print('Roman map shape km2 (incl. sea where coloured)',round(A(R)))
pickle_path=S+'/rmap/rome_map.json'
json.dump(shapely.geometry.mapping(R),open(pickle_path,'w'))
