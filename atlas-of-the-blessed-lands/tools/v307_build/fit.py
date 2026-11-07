import json,sys,subprocess,numpy as np,shapely
from shapely.geometry import shape,box
from PIL import Image,ImageDraw
S=sys.argv[1]; IMG='/home/user/Project_Caliphate/atlas-of-the-blessed-lands/reference/v306_ottoman_1683_map.jpg'
cp=[((43,105),(16.37,48.21)),((89,124),(19.04,47.50)),((104,177),(20.46,44.79)),((152,227),(23.32,42.70)),((229,255),(28.98,41.01)),
((145,313),(23.73,37.98)),((563,271),(49.87,40.41)),((433,242),(41.60,41.60)),((352,184),(36.60,45.30)),((413,143),(39.20,47.20)),((327,237),(35.15,42.02))]
ll=np.array([c[1] for c in cp]); px=np.array([c[0] for c in cp],float)
def feat(lon,lat,k): return np.c_[np.ones_like(lon),lon,lat,lon*lon,lon*lat,lat*lat][:,:k]
k=int(sys.argv[2]) if len(sys.argv)>2 else 6
F=feat(ll[:,0],ll[:,1],k)
cx=np.linalg.lstsq(F,px[:,0],rcond=None)[0]; cy=np.linalg.lstsq(F,px[:,1],rcond=None)[0]
res=np.c_[F@cx,F@cy]-px
for c,r in zip(cp,res): print(c[1],np.round(r,1))
json.dump({'cx':list(cx),'cy':list(cy),'k':k},open(S+'/omap2/tf.json','w'))
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"],cwd='/home/user/Project_Caliphate/atlas-of-the-blessed-lands'))
land=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(box(8,30,58,55))])
img=Image.open(IMG).convert('RGB'); W,H=img.size; z=2; img=img.resize((W*z,H*z)); dr=ImageDraw.Draw(img)
for p in getattr(land,'geoms',[land]):
    if p.area<0.3: continue
    for ring in [p.exterior,*p.interiors]:
        c=np.array(ring.coords); f=feat(c[:,0],c[:,1],k); dr.line([(a*z,b*z) for a,b in zip(f@cx,f@cy)],fill=(255,0,0),width=1)
img.save(S+'/omap2/overlay.png')
