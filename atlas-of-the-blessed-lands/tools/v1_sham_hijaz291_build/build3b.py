import re,json,pickle,sys,shapely,collections
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import Polygon,LineString,Point
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
src=open('src/old_data.js').read()
def ring(name):
    blk=src[src.index('const '+name+' = ['):]; blk=blk[:blk.index('];')]
    pts=[]
    for seg in re.findall(r'p:(\[\[.*?\]\])\}',blk): pts+=json.loads(seg)
    return Polygon(pts).buffer(0)
SO,HO=ring('SHAM_OUTER'),ring('HIJAZ_OUTER')
geod=Geod(ellps='WGS84')
yam=Polygon([geod.fwd(46.85,24.45,az,95000)[:2] for az in range(0,360,5)])
line=LineString([(39.61,24.47),(46.85,24.45)])
ENV=shapely.union_all([SO,HO])
SH,HJ=pickle.load(open(D+'/v1parts.pkl','rb'))
rows=[r for r in pq.read_table(D+'/divs.parquet').to_pylist() if r['subtype']=='county']+pq.read_table(D+'/divs2.parquet').to_pylist()
take=[];log=collections.defaultdict(list)
for r in rows:
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(ENV): continue
    f=g.intersection(ENV).area/g.area; n=(r['names'] or {}).get('primary')
    on=False
    if f>=0.5 or on: take.append(g); log[r['country']].append((n,round(100*f),'line' if on and f<0.5 else ''))
for c in log: print(c,len(log[c]),[x for x in log[c] if c in ('SA','IQ','TR')])
X=shapely.union_all([SH.buffer(0.003),HJ.buffer(0.003)]+[g.buffer(0.003) for g in take]).buffer(0)
print('km2',round(A(X)),'envelope land not covered km2 (approx)', round(A(ENV.intersection(shapely.union_all([wkb.loads(r['geometry']) for r in rows])).difference(X))))
pickle.dump(X,open(D+'/v1Y2.pkl','wb'))
