import pickle,shapely,sys,collections,json
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
X=pickle.load(open(S+'/crim/v7n2.pkl','rb'))
UA=[wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(S+'/crim/divs.parquet').to_pylist() if r['country']=='UA' and r['subtype']=='region']
print('UA regions',len(UA))
south=box(33,40,61.4,52.0)
add=[];names=[]
for r in pq.read_table(S+'/crim/ru52.parquet').to_pylist():
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(south) or g.difference(X).area/g.area<0.02: continue
    if g.intersection(south).area/g.area>=0.5: add.append(g); names.append((r['names'] or {}).get('primary'))
print('RU districts',len(add))
X=shapely.union_all([X]+[g.buffer(0.003) for g in UA+add]).buffer(0)
pickle.dump(X,open(S+'/crim/v7n3.pkl','wb')); print('km2',round(A(X)))
