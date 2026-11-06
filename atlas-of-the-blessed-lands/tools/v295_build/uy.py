import json,pickle,shapely,sys,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,Polygon,MultiPolygon,LineString,Point,box
from shapely.ops import linemerge
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
uy=[wkb.loads(r['geometry']) for r in pq.read_table(S+'/riv/uy_area.parquet').to_pylist() if (r['names'] or {}).get('primary')=='Уй']
pts=[]
for g in uy:
    for part in getattr(g,'geoms',[g]):
        pts+=list(part.exterior.coords if part.geom_type=='Polygon' else part.coords)
pts=sorted(pts)          # west->east by longitude
# thin to a monotone-ish line: take for each 0.02 deg of longitude the mean latitude
import collections
bins=collections.defaultdict(list)
for x,y in pts: bins[round(x/0.02)].append(y)
line=[(k*0.02,sum(v)/len(v)) for k,v in sorted(bins.items())]
print('Uy from',[round(v,2) for v in line[0]],'to',[round(v,2) for v in line[-1]],len(line))
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
RU=[shape(f['geometry']).buffer(0) for f in geo['features'] if f['id']=='643'][0]
south=Polygon([(58.6,54.85),line[0]]+line+[(62.5,line[-1][1]),(62.5,50),(58.6,50)]).buffer(0)
add=south.intersection(RU).intersection(box(58.6,50,62.5,55))
C=json.load(open('src/caliph.json'))
X=MultiPolygon([Polygon(r[0],r[1:]) for r in C['rom']['polys']]).buffer(0)
print('new land km2',round(A(add.difference(X))))
L=LineString(line); towns=[]
for r in pq.read_table(S+'/crim/towns_n.parquet').to_pylist():
    g=wkb.loads(r['geometry'])
    if A(g)<=500 and g.intersects(L): towns.append(g.buffer(0))
print('towns on the Uy whole',len(towns), 'Troitsk' , any(t.contains(Point(61.56,54.08)) for t in towns))
Y=shapely.union_all([X,add.buffer(0.003)]+[t.buffer(0.003) for t in towns]).buffer(0)
json.dump(line,open(S+'/crim/uy_line.json','w'))
pickle.dump(Y,open(S+'/crim/v7uy.pkl','wb'))
for n,(x,y) in {'Kartaly':(60.65,53.05),'Troitsk':(61.56,54.08),'Chelyabinsk':(61.4,55.16),'Magnitogorsk':(58.98,53.41)}.items(): print(n,'IN' if Y.contains(Point(x,y)) else 'out')
