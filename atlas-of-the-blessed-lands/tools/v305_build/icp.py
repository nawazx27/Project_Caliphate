import json,sys,subprocess,numpy as np,shapely
from shapely.geometry import shape
from scipy import ndimage
from PIL import Image,ImageDraw
S=sys.argv[1]
im=np.array(Image.open('/root/.claude/uploads/e227bf79-e0c6-5974-a79a-4f0672b36775/e1e2f3fb-image.jpg').convert('RGB')).astype(int)
H,W=im.shape[:2]
blk=(im.max(2)<70)
# coastline also = boundary between light-blue water and non-water
r,g,b=im[...,0],im[...,1],im[...,2]
water=(b>200)&(g>190)&(r>150)&(r<205)&(b-r>25)
water=ndimage.binary_opening(water,iterations=1)
edge=water ^ ndimage.binary_erosion(water)
tgt=blk|edge
dt,ind=ndimage.distance_transform_edt(~tgt,return_indices=True)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
win=shapely.box(-12,12,55,58)
land=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(win)]).simplify(0.02)
pts=[]
for p in getattr(land,'geoms',[land]):
    if p.area<0.3: continue
    c=np.array(p.exterior.segmentize(0.15).coords); pts.append(c)
P=np.vstack(pts); P=P[(P[:,0]>-12)&(P[:,0]<55)&(P[:,1]>12)&(P[:,1]<58)]
print('coast pts',len(P))
def feat(lon,lat): return np.c_[np.ones_like(lon),lon,lat,lon*lon,lon*lat,lat*lat,lon**3,lon*lon*lat,lon*lat*lat,lat**3]
tf=json.load(open(S+'/rmap/tf.json'))
F6=feat(P[:,0],P[:,1])[:,:6]
x=F6@np.array(tf['cx']); y=F6@np.array(tf['cy'])
F=feat(P[:,0],P[:,1])
for it,thr in enumerate([25,20,15,12,10,8,6,5,5,4,4,4]):
    ok=(x>=0)&(x<W)&(y>=0)&(y<H)
    xi=np.clip(x.astype(int),0,W-1); yi=np.clip(y.astype(int),0,H-1)
    d=dt[yi,xi]; ny=ind[0][yi,xi]; nx=ind[1][yi,xi]
    sel=ok&(d<thr)
    cols=10 if it>3 else 6
    cx=np.linalg.lstsq(F[sel,:cols],nx[sel],rcond=None)[0]; cy=np.linalg.lstsq(F[sel,:cols],ny[sel],rcond=None)[0]
    x=F[:,:cols]@cx; y=F[:,:cols]@cy
    print(it,'used',sel.sum(),'median dist',round(float(np.median(d[ok])),2))
json.dump({'cx':list(cx),'cy':list(cy),'cols':cols},open(S+'/rmap/tf2.json','w'))
img=Image.open('/root/.claude/uploads/e227bf79-e0c6-5974-a79a-4f0672b36775/e1e2f3fb-image.jpg').convert('RGB'); dr=ImageDraw.Draw(img)
for c in pts:
    f=feat(c[:,0],c[:,1])[:,:cols]; dr.line(list(zip(f@cx,f@cy)),fill=(255,0,0),width=1)
img.resize((W*2,H*2)).save(S+'/rmap/overlay.png')
