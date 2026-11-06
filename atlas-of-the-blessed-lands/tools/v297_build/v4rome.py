import json,pickle,shapely,sys,subprocess,collections
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,MultiPolygon,Polygon,box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
R=pickle.load(open(S+'/romeR.pkl','rb'))
C=json.load(open('src/caliph.json'))
V=MultiPolygon([Polygon(r[0],r[1:]) for r in C['sas']['polys']]).buffer(0)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
G={f['id']:(f['properties']['n'],shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
WHOLE=['442','056','KOS','040','380','756','688','191','705','499','070','674','492','438','020']
add=[G[k][1] for k in WHOLE if k in G]+[G['FRA'][1].intersection(box(-6,41,10,52))]
print('whole:',[G[k][0] for k in WHOLE if k in G]+['France (mainland, Corsica)'])
rows=[r for r in pq.read_table(S+'/rome/de_nl_districts.parquet').to_pylist()]+[r for r in pq.read_table(S+'/rome/rohugb.parquet').to_pylist() if r['subtype']=='county']
cnt=collections.Counter()
for r in rows:
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(R): continue
    ra=A(g.intersection(R)); f=ra/A(g)
    if f>=0.5 or ra>=150: add.append(g); cnt[r['country']]+=1
print('partial-country districts taken whole:',dict(cnt))
X=shapely.union_all([V]+[a.buffer(0.003) for a in add]).buffer(0)
land=shapely.union_all([g for n,g in G.values() if g.intersects(R)])
rest=R.intersection(land).difference(X)
print('leftover Roman land added as is km2',round(A(rest)))
X=shapely.union_all([X,rest.buffer(0.003)]).buffer(0)
print('Roman land outside now km2',round(A(R.intersection(land).difference(X))))
pickle.dump(X,open(S+'/rome/v4r1.pkl','wb')); print('V4 km2',round(A(V)),'->',round(A(X)))
