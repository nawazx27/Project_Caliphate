import pickle,json,subprocess,shapely,sys
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,MultiPolygon,Polygon
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
SH,HJ=pickle.load(open(D+'/v1parts.pkl','rb'))
X=shapely.union_all([SH.buffer(0.003),HJ.buffer(0.003)]).buffer(0)
X=Polygon(max(X.geoms,key=lambda p:p.area).exterior) if X.geom_type=='MultiPolygon' and False else X
XB=X.buffer(0.05)
rows=pq.read_table(D+'/divs.parquet').to_pylist()
fill=[]
for r in rows:
    if r['subtype']!='county' and r['country']!='SA': continue
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(XB): continue
    rem=g.difference(X)
    if A(rem)<20: continue
    for q in getattr(rem,'geoms',[rem]):
        if A(q)<20: continue
        t=q.exterior.intersection(XB).length/q.exterior.length
        if t>=0.5: print((r['names'] or {}).get('primary'),r['country'],'%.0f%% enclosed'%(100*t),round(A(q)),'km2')
        if t>=0.8: fill.append(q)
X=shapely.union_all([X]+[q.buffer(0.003) for q in fill]).buffer(0)
pickle.dump(X,open(D+'/v1X.pkl','wb'))
print('pieces',len(getattr(X,'geoms',[X])),'km2',round(A(X)))
C=json.load(open('src/caliph.json'))
for k in ['me8','me2']:
    V=MultiPolygon([Polygon(r[0],r[1:]) for r in C[k]['polys']]).buffer(0)
    print(k,'new V1 outside it km2',round(A(X.difference(V.buffer(0.01)))),'| it outside new V1',round(A(V.difference(X.buffer(0.01)))))
