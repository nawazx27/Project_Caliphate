"""Version 259 (Nawaz: "Give v5 Africa to v4", preview shown, then "Apply"). V4 (CALIPH.me9) gains every piece of V5 (CALIPH.sah) in Africa
(box 30W-43E, 40S-30N) it lacks: Niger and Burkina Faso, each whole, and northern Chad (Borkou, Ennedi, Tibesti), 2,019,515 km2, with
V5's state rows for them. Run AFTER tools/v7_sahara239.py (V5's Africa). Usage: python3 tools/v4_sahara259.py ."""
import json,subprocess,sys,os,shapely
from shapely.geometry import MultiPolygon,Polygon,box
from shapely.geometry.polygon import orient
from pyproj import Geod
P=sys.argv[1]
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
F_=os.path.join(P,'src/caliph.json');C=json.load(open(F_))
M=lambda k: MultiPolygon([Polygon(q[0],q[1:]) for q in C[k]['polys']]).buffer(0)
v4,v5=M('me9'),M('sah')
af=v5.intersection(box(-30,-40,43,30)).difference(v4)
print('Africa add',round(A(af)))
X=shapely.union_all([v4,af.buffer(0.003)],grid_size=0.001)
out=[]
for q in getattr(X,'geoms',[X]):
  if q.geom_type!='Polygon' or A(q)<0.05: continue
  q=orient(Polygon(q.exterior,[h for h in q.interiors if A(Polygon(h))>=5000]),1.0)
  out.append([[[round(u,3),round(v,3)] for u,v in rr.coords] for rr in [q.exterior,*q.interiors]])
km2=int(subprocess.check_output(['node','-e',"""const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""],cwd=P,input=json.dumps(out).encode()))
Y=MultiPolygon([Polygon(r[0],r[1:]) for r in out]).buffer(0)
print('left over V5 Africa not in new V4',round(A(v5.intersection(box(-30,-40,43,30)).difference(Y.buffer(0.001)))))
add=[r for r in C['sah']['states'] if r['id'] in ('562','854','BET')]
print([r['n'] for r in add])
print('V4',C['me9']['km2'],'->',km2)
C['me9'].update(polys=out,km2=km2,states=[r for r in C['me9']['states'] if r['id'] not in {x['id'] for x in add}]+add)
json.dump(C,open(F_+'.tmp','w'),separators=(',',':'),ensure_ascii=False);os.replace(F_+'.tmp',F_)
