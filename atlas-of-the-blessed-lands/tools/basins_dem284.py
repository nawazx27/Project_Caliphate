# Version 284: drainage basins of the Indus and the Ganges-Brahmaputra from the Mapzen terrain tiles (tools/dem_fetch.py 60 15 106 42 5 sa_z5.npz) with Natural Earth 10m rivers burned in; run: python3 tools/basins_dem284.py 30 40 3000 (expects sa_z5.npz and ne/rivers10.geojson in the working directory)
import numpy as np, heapq, sys
from scipy import ndimage
d=np.load('sa_z5.npz'); h=d['h'].astype(np.float32); Z=int(d['z']); x0=int(d['x0']); y0=int(d['y0']); TS=int(d['ts'])
f=2; h=h[:h.shape[0]//f*f,:h.shape[1]//f*f].reshape(h.shape[0]//f,f,h.shape[1]//f,f).min((1,3))
H,W=h.shape; n=2**Z*TS
R,Cc=np.mgrid[0:H,0:W]; X=x0*TS+(Cc+.5)*f; Y=y0*TS+(R+.5)*f; LO=X/n*360-180; LA=np.degrees(np.arctan(np.sinh(np.pi*(1-2*Y/n))))
sea=h<=0; lab,_=ndimage.label(sea); keep=np.unique(lab[-1,:]); keep=keep[keep>0]; sea=np.isin(lab,keep)
import json, rasterio.features as rf
from shapely.geometry import shape, LineString, MultiLineString
from shapely.ops import transform
def topix(x,y,z=None):
  x=np.asarray(x); y=np.asarray(y)
  X=(x+180)/360*n; Y=(1-np.log(np.tan(np.radians(y))+1/np.cos(np.radians(y)))/np.pi)/2*n
  return (X-x0*TS)/f, (Y-y0*TS)/f
lines=[]
for ft in json.load(open('ne/rivers10.geojson'))['features']:
  g=shape(ft['geometry']); b=g.bounds
  if b[2]<60 or b[0]>106 or b[3]<15 or b[1]>42: continue
  lines.append(transform(topix,g))
burn=rf.rasterize([(l,1) for l in lines],out_shape=h.shape,all_touched=True).astype(bool)&~sea
BURN=float(sys.argv[3]) if len(sys.argv)>3 else 400
h=np.where(burn,np.maximum(h-BURN,1.0),h).astype(np.float32)
print('burned cells',int(burn.sum()))
filled=h.copy(); seen=np.zeros(h.shape,bool); out=-np.ones(h.shape,np.int64); par=-np.ones(h.size,np.int64); order=[]
pq=[]
for r,c in zip(*np.where(sea)): seen[r,c]=True; out[r,c]=r*W+c; heapq.heappush(pq,(float(h[r,c]),r,c))
for r in range(H):
  for c in (0,W-1):
    if not seen[r,c]: seen[r,c]=True; out[r,c]=-2; heapq.heappush(pq,(float(h[r,c]),r,c))
for c in range(W):
  if not seen[0,c]: seen[0,c]=True; out[0,c]=-2; heapq.heappush(pq,(float(h[0,c]),0,c))
nb=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
while pq:
  e,r,c=heapq.heappop(pq); order.append(r*W+c)
  for dr,dc in nb:
    rr,cc=r+dr,c+dc
    if 0<=rr<H and 0<=cc<W and not seen[rr,cc]:
      seen[rr,cc]=True; fe=max(float(h[rr,cc]),e+1e-3); filled[rr,cc]=fe; out[rr,cc]=out[r,c]; par[rr*W+cc]=r*W+c
      heapq.heappush(pq,(fe,rr,cc))
depth=filled-h
A=int(sys.argv[1]) if len(sys.argv)>1 else 40; T=float(sys.argv[2]) if len(sys.argv)>2 else 60
lab2,nl=ndimage.label(depth>15)
sz=ndimage.sum(np.ones_like(depth),lab2,range(1,nl+1)); mx=ndimage.maximum(depth,lab2,range(1,nl+1))
mh=ndimage.mean(h,lab2,range(1,nl+1))
lakeid=1+np.where(((sz>=A)&(mx>=T)&(mh>2500))|(sz>=2000))[0]; lake=np.isin(lab2,lakeid)&~sea
print('lake basins',len(lakeid))
fl=lake.ravel().copy()
for i in order:
  p=par[i]
  if p>=0 and fl[p]: fl[i]=True
deep=fl.reshape(h.shape)
valid=out>=0; oc=np.clip(out,0,None)
olo=np.where(valid,LO.ravel()[oc.ravel()].reshape(h.shape),np.nan); ola=np.where(valid,LA.ravel()[oc.ravel()].reshape(h.shape),np.nan)
indus=valid&(olo>65.5)&(olo<69.5)&(ola>22.5)&(ola<26)&~deep&~sea
gb=valid&(olo>86)&(olo<92.6)&(ola>20)&(ola<24)&~deep&~sea
np.save('depth.npy',depth); np.save('lake.npy',lake); np.savez_compressed('basin_mask.npz',indus=indus,gb=gb,deep=deep,LO=LO.astype(np.float32),LA=LA.astype(np.float32),h=h)
print('indus',int(indus.sum()),'gb',int(gb.sum()),'deep',int(deep.sum()))
from PIL import Image
img=np.zeros((H,W,3),np.uint8); img[...,:]=np.clip((h/6000*200),0,200)[...,None].astype(np.uint8); img[sea]=(40,60,120)
img[indus]=(220,80,60); img[gb]=(60,170,80); img[deep&~sea]=(150,150,220)
for lon in range(60,107,5):
  c=np.argmin(abs(LO[0]-lon)); img[:,c]=(255,255,0)
for lat in range(15,43,5):
  r=np.argmin(abs(LA[:,0]-lat)); img[r,:]=(255,255,0)
Image.fromarray(img).resize((W//2,H//2)).save('basins.png')
