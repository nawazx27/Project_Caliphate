import re,json,pickle,sys,shapely,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import Polygon,shape,box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
src=open('src/old_data.js').read()
def ring(name):
    blk=src[src.index('const '+name+' = ['):]; blk=blk[:blk.index('];')]
    pts=[]
    for seg in re.findall(r'p:(\[\[.*?\]\])\}',blk): pts+=json.loads(seg)
    return Polygon(pts).buffer(0)
geod=Geod(ellps='WGS84')
ENV=shapely.union_all([ring('SHAM_OUTER'),ring('HIJAZ_OUTER')])
X=pickle.load(open(D+'/v1Y3.pkl','rb'))
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
land=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(ENV)])
add=ENV.intersection(land).difference(X)
edge=ENV.boundary
towns=[];names=[]
for r in pq.read_table(D+'/towns.parquet').to_pylist():
    if r['subtype']=='localadmin': continue
    g=wkb.loads(r['geometry']).buffer(0)
    if g.is_empty or not g.intersects(edge): continue
    if A(g)>500: continue
    if g.difference(X).area<1e-6: continue
    towns.append(g); names.append((r['country'],(r['names'] or {}).get('primary'),round(A(g))))
print('land up to the line added km2',round(A(add)))
print(len(towns),'towns cut by the line, taken whole, km2',round(A(shapely.union_all(towns))) if towns else 0)
print([n for n in names if n[2]>=3][:80])
X=shapely.union_all([X,add.buffer(0.003)]+[g.buffer(0.003) for g in towns]).buffer(0)
pickle.dump(X,open(D+'/v1Y4.pkl','wb'))
