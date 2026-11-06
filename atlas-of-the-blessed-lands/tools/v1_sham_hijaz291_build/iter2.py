import pickle,pyarrow.parquet as pq,shapely,sys
from shapely import wkb
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]; X=pickle.load(open(D+'/'+sys.argv[2],'rb'))
rows=[(r,wkb.loads(r['geometry']).buffer(0)) for r in [r for r in pq.read_table(D+'/divs.parquet').to_pylist() if r['subtype']=='county']+pq.read_table(D+'/divs2.parquet').to_pylist()]
towns=[(r,wkb.loads(r['geometry']).buffer(0)) for r in pq.read_table(D+'/towns.parquet').to_pylist() if r['subtype']!='localadmin']
towns=[(r,g) for r,g in towns if A(g)<=500]
WH=[]; WHn=set()
for rnd in range(8):
    new=[]
    for r,g in rows:
        k=r['id']
        if k in WHn or not g.intersects(X): continue
        ins=g.intersection(X); i=A(ins); o=A(g)-i
        if i<=5: continue
        core=ins.buffer(-0.02)
        if not (core.is_empty or A(core)<0.05*i):
            WHn.add(k); WH.append(g)
            if o>5: new.append(g); print(' whole:',(r['names'] or {}).get('primary'),round(100*i/A(g)),'%')
    if not new: break
    X=shapely.union_all([X]+[g.buffer(0.003) for g in new]).buffer(0)
WU=shapely.union_all(WH).buffer(0.003) if WH else None
# slivers of other districts and towns: trim only outside the whole districts
trim=[]
for r,g in rows:
    if r['id'] in WHn or not g.intersects(X): continue
    ins=g.intersection(X); i=A(ins); o=A(g)-i
    if i>0.5 and o>5: trim.append(ins)
ta=[];tt=[]
for r,g in towns:
    if not g.intersects(X): continue
    i=A(g.intersection(X)); o=A(g)-i
    if i>0.3 and o>0.3: (ta if i>=o else tt).append(g)
T=shapely.union_all([t.buffer(0.001) for t in trim+tt]) if trim+tt else None
if T is not None:
    if WU is not None: T=T.difference(WU)
    X=X.difference(T).buffer(0)
if ta: X=shapely.union_all([X]+[g.buffer(0.003) for g in ta]).buffer(0)
print('whole districts',len(WH),'slivers trimmed',len(trim),'towns whole',len(ta),'town slivers trimmed',len(tt),'km2',round(A(X)))
pickle.dump(X,open(D+'/'+sys.argv[3],'wb'))
c=[]
for r,g in rows:
    if not g.intersects(X): continue
    i=A(g.intersection(X)); o=A(g)-i
    if i>20 and o>20: c.append(((r['names'] or {}).get('primary'),round(i),round(o)))
print('still split (>20 km2 each side):',c)
