import pickle,pyarrow.parquet as pq,shapely,sys
from shapely import wkb
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]; X=pickle.load(open(D+'/'+sys.argv[2],'rb'))
rows=[r for r in pq.read_table(D+'/divs.parquet').to_pylist() if r['subtype']=='county']+pq.read_table(D+'/divs2.parquet').to_pylist()
add=[];trim=[];la=[];lt=[]
for r in rows:
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(X): continue
    ins=g.intersection(X); i=A(ins); o=A(g)-i
    if i<=5 or o<=5: continue
    core=ins.buffer(-0.02)   # ~2 km in from every edge
    n=(r['country'],(r['names'] or {}).get('primary'),round(100*i/A(g)))
    if core.is_empty or A(core)<0.05*i: trim.append(ins); lt.append(n)
    else: add.append(g); la.append(n)
print('taken whole',len(la)); print(la)
print('slivers trimmed',len(lt)); print(lt)
X=shapely.union_all([X]+[g.buffer(0.003) for g in add]).buffer(0)
if trim: X=X.difference(shapely.union_all([t.buffer(0.001) for t in trim])).buffer(0)
pickle.dump(X,open(D+'/'+sys.argv[3],'wb')); print('km2',round(A(X)))
