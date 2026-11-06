import pickle,json,subprocess,shapely,sys
from shapely.geometry.polygon import orient
from shapely.geometry import Polygon,MultiPolygon
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
X=shapely.set_precision(pickle.load(open(S+'/v1new/'+sys.argv[2],'rb')),0.001)
out=[]
for q in getattr(X,'geoms',[X]):
    if q.geom_type!='Polygon' or A(q)<0.05: continue
    q=orient(Polygon(q.exterior,[h for h in q.interiors if A(Polygon(h))>=5000]),1.0)
    out.append([[[round(u,3),round(v,3)] for u,v in rr.coords] for rr in [q.exterior,*q.interiors]])
km2=int(subprocess.check_output(['node','-e',"""const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""],input=json.dumps(out).encode()))
print(len(out),'pieces',km2,'km2')
C=json.load(open('src/caliph.json'))
Y=MultiPolygon([Polygon(r[0],r[1:]) for r in out]).buffer(0)
for k in ['me8','me2']:
    V=MultiPolygon([Polygon(r[0],r[1:]) for r in C[k]['polys']]).buffer(0)
    print(k,'new V1 outside it km2',round(A(Y.difference(V.buffer(0.01)))))
json.dump(out,open(S+'/v1new/v1_polys.json','w'))
P=json.load(open(S+'/pv/src/caliph.json')); P['me8']['polys']=out; P['me8']['km2']=km2
json.dump(P,open(S+'/pv/src/caliph.json','w'),separators=(',',':'),ensure_ascii=False)
