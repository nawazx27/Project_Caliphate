import json,sys,subprocess,numpy as np,shapely
from shapely.geometry import shape,box,Polygon,MultiPolygon,Point
from shapely.geometry.polygon import orient
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]
R=shape(json.load(open(S+'/rmap/rome_map.json'))).buffer(0)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
G={f['id']:(f['properties']['n'],shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
win=box(-12,10,56,60)
land=shapely.union_all([g for n,g in G.values() if g.intersects(win)]).intersection(win)
coast=land.difference(land.buffer(-0.25))
RL=shapely.union_all([land.intersection(R), coast.intersection(R.buffer(0.25))]).buffer(0)
# small islands: any island polygon mostly within R.buffer
isl=[p for p in getattr(land,'geoms',[land]) if A(p)<30000 and p.intersection(R.buffer(0.1)).area/p.area>0.5]
RL=shapely.union_all([RL]+isl).buffer(0)
C=json.load(open('src/caliph.json'))
V4=MultiPolygon([Polygon(r[0],r[1:]) for r in C['sas']['polys']]).buffer(0)
X=shapely.union_all([V4,RL.buffer(0.003)]).buffer(0)
X=shapely.set_precision(X,0.001); out=[]
for q in getattr(X,'geoms',[X]):
    if q.geom_type!='Polygon' or A(q)<0.05: continue
    q=orient(Polygon(q.exterior,[h for h in q.interiors if A(Polygon(h))>=5000]),1.0)
    out.append([[[round(u,3),round(v,3)] for u,v in rr.coords] for rr in [q.exterior,*q.interiors]])
km2=int(subprocess.check_output(['node','-e',"""const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""],input=json.dumps(out).encode()))
print('V5 ->',km2)
Y=MultiPolygon([Polygon(r[0],r[1:]) for r in out]).buffer(0)
for n,(x,y) in {'Edinburgh':(-3.19,55.95),'Inverness':(-4.22,57.48),'Dublin':(-6.26,53.35),'Amsterdam':(4.9,52.37),'Groningen':(6.57,53.22),'Hamburg':(9.99,53.55),'Hanover':(9.73,52.37),'Berlin':(13.4,52.52),'Munich':(11.58,48.14),'Prague':(14.42,50.08),'Vienna':(16.37,48.21),'Budapest':(19.04,47.5),'Debrecen':(21.63,47.53),'Cluj':(23.6,46.77),'Iasi':(27.6,47.16),'Chisinau':(28.86,47.0),'Kyiv':(30.52,50.45),'Odesa':(30.73,46.48),'Simferopol':(34.1,44.95),'Taman':(36.72,45.21),'Krakow':(19.94,50.06),'Bratislava':(17.11,48.15)}.items(): print(' ',n,Y.contains(Point(x,y)))
json.dump([out,km2],open(S+'/rmap/v5.json','w'))
P=json.load(open(S+'/pv/src/caliph.json')); P['grm']['polys']=out; P['grm']['km2']=km2
json.dump(P,open(S+'/pv/src/caliph.json','w'),separators=(',',':'),ensure_ascii=False)
