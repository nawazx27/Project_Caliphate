import json,pickle,shapely,sys,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]; X=pickle.load(open(S+'/crim/'+sys.argv[2],'rb'))
XB=X.buffer(0.05)
# pockets by district: a district outside X whose edge is >=80% on X, or groups of them (repeat)
rows=[(r,wkb.loads(r['geometry']).buffer(0)) for r in pq.read_table(S+'/crim/counties.parquet').to_pylist()]
for rnd in range(4):
    rest=shapely.union_all([g.difference(X) for r,g in rows if g.difference(X).area/g.area>0.5])
    fill=[]
    for q in getattr(rest,'geoms',[rest]):
        if A(q)<5: continue
        t=q.exterior.intersection(XB).length/q.exterior.length
        if t>=0.5: print(' pocket %d km2 %.0f%% enclosed at %s'%(A(q),100*t,tuple(round(v,1) for v in q.representative_point().coords[0])))
        if t>=0.8: fill.append(q)
    if not fill: break
    X=shapely.union_all([X]+[q.buffer(0.003) for q in fill]).buffer(0); XB=X.buffer(0.05)
    print('round',rnd,'filled',len(fill),round(sum(A(q) for q in fill)))
pickle.dump(X,open(S+'/crim/'+sys.argv[3],'wb')); print('km2',round(A(X)))
