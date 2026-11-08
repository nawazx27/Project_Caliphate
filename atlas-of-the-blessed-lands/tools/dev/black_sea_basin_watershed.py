import json, subprocess, math, heapq, numpy as np, sys
from PIL import Image, ImageDraw
from shapely.geometry import shape
d=np.load(sys.argv[1]); h=d['h'].astype(np.float32); Z=int(d['z']); x0=int(d['x0']); y0=int(d['y0']); TS=int(d['ts']); n=2**Z
H,W=h.shape
def px(lon,lat):
    x=((lon+180)/360*n-x0)*TS
    y=((1-math.log(math.tan(math.radians(lat))+1/math.cos(math.radians(lat)))/math.pi)/2*n-y0)*TS
    return x,y
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
for f in geo['features']:
    if not f.get('geometry'): continue
    g=shape(f['geometry'])
    if g.bounds[2]<0 or g.bounds[0]>60 or g.bounds[3]<30: continue
    for p in getattr(g,'geoms',[g]):
        dr.polygon([px(*c) for c in p.exterior.coords],fill=1)
        for r in p.interiors: dr.polygon([px(*c) for c in r.coords],fill=0)
land=np.array(im).astype(bool)
# block the Bosphorus and Dardanelles so the Black Sea is a separate water body
for (a,b,c,e) in [(28.85,40.95,29.25,41.3),(26.1,39.9,26.8,40.5)]:
    xa,ya=px(a,e); xb,yb=px(c,b); land[int(ya):int(yb)+1,int(xa):int(xb)+1]=True
sea=~land
# label Black Sea water by flood from (34E,43N)
from scipy import ndimage
lab,nl=ndimage.label(sea)
bx,by=px(34,43.5); bs=lab[int(by),int(bx)]; az=lab[int(px(36.5,46)[1]),int(px(36.5,46)[0])]
print('black sea label',bs,'azov label',az)
yy,xx=np.mgrid[0:H,0:W]
lonA=(xx/TS+x0)/n*360-180
latA=np.degrees(np.arctan(np.sinh(math.pi*(1-2*(yy/TS+y0)/n))))
black=sea&(lonA>27.3)&(lonA<42.0)&(latA>40.8)&(latA<47.6)&~((lonA<29.3)&(latA<41.3))   # every water body of the Black Sea and Azov basin box (limans, lagoons), not the Marmara
label=np.zeros((H,W),np.int8)   # 0 unvisited, 1 black sea basin, 2 other
filled=h.copy()
heap=[]
seed=sea.copy(); seed[0,:]=seed[-1,:]=seed[:,0]=seed[:,-1]=True
ys,xs=np.nonzero(seed)
for y,x in zip(ys,xs):
    L=1 if black[y,x] else 2
    label[y,x]=L; e=-500.0 if sea[y,x] else float(h[y,x])
    filled[y,x]=e; heapq.heappush(heap,(e,int(y),int(x)))
nb=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
cnt=0
while heap:
    e,y,x=heapq.heappop(heap); L=label[y,x]
    for dy,dx in nb:
        yy=y+dy; xx=x+dx
        if 0<=yy<H and 0<=xx<W and label[yy,xx]==0:
            label[yy,xx]=L; ne=max(float(h[yy,xx]),e); filled[yy,xx]=ne; heapq.heappush(heap,(ne,yy,xx))
    cnt+=1
basin=(label==1)&land
print('basin pixels',basin.sum())
np.savez_compressed(sys.argv[2],basin=basin,z=Z,x0=x0,y0=y0,ts=TS)
Image.fromarray((basin*255).astype('uint8')).resize((W//4,H//4)).save(sys.argv[2]+'.png')
