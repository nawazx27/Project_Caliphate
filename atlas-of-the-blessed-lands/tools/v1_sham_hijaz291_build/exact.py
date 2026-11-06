import re,json,pickle,sys,shapely,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import Polygon,LineString,shape,Point
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
src=open('src/old_data.js').read()
def segs(name):
    blk=src[src.index('const '+name+' = ['):]; blk=blk[:blk.index('];')]
    return [(c,json.loads(p)) for c,p in re.findall(r'\{c:"(\w+)", p:(\[\[.*?\]\])\}',blk)]
E=[];SEA=[]
for nm in ['SHAM_OUTER','HIJAZ_OUTER']:
    ss=segs(nm); pts=[]
    for c,p in ss:
        pts+=p
        if c=='sea': SEA.append(LineString(p))
    E.append(Polygon(pts).buffer(0))
E=shapely.union_all(E)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
land=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(E.buffer(0.5))])
coastal=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and f['id'] not in ('818','196','CYN','CNM','ESB','WSB') and shape(f['geometry']).intersects(E.buffer(0.5))])
seaband=shapely.union_all([l.buffer(0.3) for l in SEA])
X=shapely.union_all([land.intersection(E), coastal.intersection(seaband)]).buffer(0)
# whole towns the land edge of the lines touches
edge=E.boundary.difference(seaband)
towns=[]
for r in pq.read_table(D+'/towns.parquet').to_pylist():
    if r['subtype']=='localadmin': continue
    g=wkb.loads(r['geometry']).buffer(0)
    if A(g)<500 and g.intersects(edge): towns.append(g)
for r in pq.read_table(D+'/towns.parquet').to_pylist():
    if r['country']=='SY' and r['subtype']!='localadmin':
        g=wkb.loads(r['geometry'])
        if g.distance(Point(39.01,35.95))<0.08 or g.distance(Point(40.14,35.335))<0.03: towns.append(g.buffer(0))
X=shapely.union_all([X]+[t.buffer(0.003) for t in towns]).buffer(0)
print('towns',len(towns),'km2',round(A(X)))
pickle.dump(X,open(D+'/v1E1.pkl','wb'))
