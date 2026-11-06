import json,pickle,shapely,sys,collections
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import Polygon,MultiPolygon,LineString
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
L=json.load(open(S+'/crim/redline2.json'))
# extend the line a little at both ends onto the V7 outline, then close south
L=[(L[0][0]-0.6,L[0][1]-0.05)]+L+[(L[-1][0]+0.6,L[-1][1]+0.05)]
south=Polygon(L+[(L[-1][0],40),(L[0][0],40)]).buffer(0)
C=json.load(open('src/caliph.json'))
V=MultiPolygon([Polygon(r[0],r[1:]) for r in C['rom']['polys']]).buffer(0)
add=[];log=collections.defaultdict(list)
for r in pq.read_table(S+'/crim/counties.parquet').to_pylist():
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(south) or g.difference(V).area/g.area<0.02: continue
    f=g.intersection(south).area/g.area
    if f>=0.5: add.append(g); log[r['country']].append((r['names'] or {}).get('primary'))
cr=[wkb.loads(g).buffer(0) for c,n,g in pickle.load(open(S+'/rome/crimea.pkl','rb'))]
print('UA',len(log['UA']),'RU',len(log['RU']))
X=shapely.union_all([V]+[g.buffer(0.003) for g in add+cr]).buffer(0)
pickle.dump((X,south),open(S+'/crim/v7n1.pkl','wb')); print('km2',round(A(V)),'->',round(A(X)))
json.dump(log,open(S+'/crim/v7n_log.json','w'),ensure_ascii=False)
