import json,shapely,pickle,sys,subprocess
from shapely.geometry import shape,Point,Polygon,LineString
from shapely.ops import linemerge
from pyproj import Geod
import pyarrow.parquet as pq
from shapely import wkb
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
d=json.load(open('rivers.geojson'))
L=linemerge(shapely.union_all([shape(f['geometry']) for f in d['features'] if f['properties']['name'] in ('Euphrates','Al Furat')]))
G_=sorted(L.geoms,key=lambda g:-g.length)
c=list(G_[0].coords)+list(G_[2].coords)+list(G_[1].coords); print('ends',c[0],c[-1])
if c[0][1]<c[-1][1]: c=c[::-1]
c=[p for p in c if p[0]>40.6]
ring=c+[(47.47,30.4),(47.0,29.0),(38.0,29.0),(38.0,c[0][1]),c[0]]
W=Polygon(ring).buffer(0)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
IQ=[shape(f['geometry']).buffer(0) for f in geo['features'] if f['id']=='368'][0]
west=IQ.intersection(W)
print('Iraq west of Euphrates km2',round(A(west)),'contains Rutba',west.contains(Point(40.28,33.03)),'Karbala',west.contains(Point(44.02,32.61)))
deep=west.difference(LineString(c).buffer(0.30))
print('deep desert (>~30 km from river) km2',round(A(deep)))
X=pickle.load(open(D+'/v1J2.pkl','rb'))
edge=LineString(c).buffer(0.30).boundary.intersection(west.buffer(0.01))
towns=[]
for r in pq.read_table(D+'/towns.parquet').to_pylist():
    if r['country']!='IQ' or r['subtype']=='localadmin': continue
    g=wkb.loads(r['geometry']).buffer(0)
    if A(g)<500 and g.intersects(edge) and g.difference(X).area>1e-6: towns.append(g)
print('towns on the cut, whole:',len(towns))
X2=shapely.union_all([X,deep.buffer(0.003)]+[g.buffer(0.003) for g in towns]).buffer(0)
pickle.dump(X2,open(D+'/v1J3.pkl','wb')); print('V1 km2',round(A(X2)))
