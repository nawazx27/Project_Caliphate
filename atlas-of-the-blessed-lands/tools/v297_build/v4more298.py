import json,pickle,shapely,sys,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,MultiPolygon,Polygon,box,Point,LineString
from shapely.ops import linemerge
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
C=json.load(open('src/caliph.json'))
V=MultiPolygon([Polygon(r[0],r[1:]) for r in C['sas']['polys']]).buffer(0)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
G={f['id']:(f['properties']['n'],shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
# 1 southern Scotland to the Antonine Wall
SC=['South Ayrshire','Inverclyde','East Renfrewshire','West Dunbartonshire','Renfrewshire','North Ayrshire','West Lothian','Falkirk','East Dunbartonshire','Glasgow City','North Lanarkshire','South Lanarkshire','East Ayrshire','Dumfries and Galloway','Scottish Borders','Midlothian','City of Edinburgh','East Lothian']
sc=[wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(S+'/rome/rohugb.parquet').to_pylist() if r['country']=='GB' and r['subtype']=='county' and (r['names'] or {}).get('primary') in SC]
# 2 Germany between the Rhine and the Elbe, with the Frisian Netherlands
d=json.load(open(S+'/riv/lc.geojson'))
parts_=[]
for f in d['features']:
    if (f['properties'].get('name') or '')=='Elbe':
        g=shape(f['geometry']); parts_+=[list(l.coords) for l in getattr(g,'geoms',[g]) if l.length>0.001]
cur=[(8.70,53.88),(9.83,53.55)]
while parts_:
    best=min(((min(Point(cur[-1]).distance(Point(q[0])),Point(cur[-1]).distance(Point(q[-1]))),i) for i,q in enumerate(parts_)))
    q=parts_.pop(best[1]); q=q if Point(cur[-1]).distance(Point(q[0]))<=Point(cur[-1]).distance(Point(q[-1])) else q[::-1]
    cur+=q
c=[]
for p_ in cur:
    if p_[0]>14.25 and p_[1]<50.9: break
    c.append(p_)
c.append((14.25,50.87))
print('Elbe from',c[0],'to',c[-1],len(c))
west=Polygon([(5,c[0][1]+0.6),(c[0][0],c[0][1]+0.6)]+c+[(c[-1][0],47.0),(5,47.0)]).buffer(0)
rows=pq.read_table(S+'/rome/de_nl_districts.parquet').to_pylist()
de=[];n=0
for r in rows:
    g=wkb.loads(r['geometry']).buffer(0)
    if r['country']=='NL' or g.intersection(west).area/g.area>=0.5: de.append(g); n+=1
print('German/Dutch districts between Rhine and Elbe (whole):',n)
# Elbe cities whole (Hamburg, Magdeburg, Dresden...): districts the river crosses with >=25% west
for r in rows:
    g=wkb.loads(r['geometry']).buffer(0)
    if g.intersects(LineString(c)) and g.intersection(west).area/g.area<0.5 and (g.intersection(west).area/g.area>=0.25 or A(g)<1000): de.append(g); print(' on the Elbe:',(r['names'] or {}).get('primary'))
# 3 Crimea and Taman
cr=[wkb.loads(g).buffer(0) for cc,nm,g in pickle.load(open(S+'/rome/crimea.pkl','rb'))]
tam=[wkb.loads(r['geometry']).buffer(0) for r in pq.read_table(S+'/crim/divs.parquet').to_pylist() if (r['names'] or {}).get('primary')=='Темрюкский район']
parts={'Scotland':shapely.union_all(sc),'Germany':shapely.union_all(de),'Crimea+Taman':shapely.union_all(cr+tam)}
for k,g in parts.items(): print(k,'new km2',round(A(g.difference(V))))
X=shapely.union_all([V]+[g.buffer(0.003) for g in parts.values()]).buffer(0)
pickle.dump(X,open(S+'/rome/v4m1.pkl','wb')); print('V4 km2',round(A(V)),'->',round(A(X)))
for nm,(x,y) in {'Hamburg':(9.99,53.55),'Magdeburg':(11.63,52.13),'Dresden':(13.74,51.05),'Hanover':(9.73,52.37),'Berlin':(13.4,52.52),'Leipzig':(12.37,51.34),'Edinburgh':(-3.19,55.95),'Glasgow':(-4.25,55.86),'Kerch':(36.47,45.36),'Taman':(36.72,45.21)}.items(): print(nm,'IN' if X.contains(Point(x,y)) else 'out')
