"""Version 260 (Nawaz: "Does v4 have the entire Sahara and Sahel", "Yes" to a preview, then "V4 only"). V4 (CALIPH.me9) gains Chad whole
and the whole local districts of Nigeria (23 LGAs of Borno and Yobe), Cameroon (6 far-north departments) and the Central African Republic
(Birao) that hold any of Natural Earth's SAHARA, LIBYAN DESERT or SAHEL (regions.geojson) V4 lacked (Overture 2026-10-21.0 counties,
tools/data/v4_sahel_districts260.geojson); pockets >= 80% in 9W-30E, 4-20N filled. Afterwards 100% of the Sahara and the Sahel are inside.
V5 not changed. Run AFTER tools/v4_sahara259.py."""
import json,subprocess,sys,os,shapely
from shapely import make_valid
from shapely.geometry import shape,MultiPolygon,Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"],cwd=P))
G={f['id']:shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land=unary_union(list(G.values()))
Rg=json.load(open(os.path.join(P,'regions.geojson')))
SS=unary_union([shape(f['geometry']).buffer(0) for f in Rg['features'] if (f['properties'].get('NAME') or '').upper() in ('SAHARA','LIBYAN DESERT','SAHEL')]).intersection(land)
F_=os.path.join(P,'src/caliph.json');C=json.load(open(F_))
V=MultiPolygon([Polygon(q[0],q[1:]) for q in C['me9']['polys']]).buffer(0)
CID={'NG':'566','CM':'120','CF':'140'}
take=[make_valid(shape(f['geometry'])).buffer(0).intersection(G[CID[f['properties']['cc']]].buffer(0.02)) for f in json.load(open(os.path.join(P,'tools/data/v4_sahel_districts260.geojson')))['features']]
cnt=unary_union(take)
print('districts',round(A(cnt)),'Chad',round(A(G['148'])))
X=shapely.union_all([V,G['148'].buffer(0.003),cnt.buffer(0.003)],grid_size=0.001)
m=X.intersection(box(-9,4,30,20));gap=m.buffer(0.5,quad_segs=4).buffer(-0.5,quad_segs=4).difference(m).intersection(land);mb=m.buffer(0.01);fill=[]
for g in getattr(gap,'geoms',[gap]):
  if g.geom_type!='Polygon' or A(g)<100: continue
  t=g.exterior.intersection(mb).length/g.exterior.length
  print('pocket',round(A(g)),round(t*100),round(g.centroid.x,2),round(g.centroid.y,2),'FILLED' if t>=0.8 else '')
  if t>=0.8: fill.append(g)
X=unary_union([X]+[g.buffer(0.003) for g in fill]).buffer(0)
out=[]
for q in getattr(X,'geoms',[X]):
  if q.geom_type!='Polygon' or A(q)<0.05: continue
  q=orient(Polygon(q.exterior,[h for h in q.interiors if A(Polygon(h))>=5000]),1.0)
  out.append([[[round(u,3),round(v,3)] for u,v in rr.coords] for rr in [q.exterior,*q.interiors]])
km2=int(subprocess.check_output(['node','-e',"""const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""],cwd=P,input=json.dumps(out).encode()))
Y=MultiPolygon([Polygon(r[0],r[1:]) for r in out]).buffer(0)
for nm in [('SAHARA','LIBYAN DESERT'),('SAHEL',)]:
  g=unary_union([shape(f['geometry']).buffer(0) for f in Rg['features'] if (f['properties'].get('NAME') or '').upper() in nm]).intersection(land)
  print(nm,'in new V4 %',round(100*A(g.intersection(Y))/A(g),3))
print('V4',C['me9']['km2'],'->',km2)
rows=[{'id':'148','n':'Chad','km2':round(A(G['148'])),'pct':100}]
for i,n in [('566','Nigeria: north-east Borno and Yobe, 23 local government areas (Lake Chad, Sahel)'),('120','Cameroon: the far north, 6 departments (Lake Chad, Sahel)'),('140','Central African Republic: Birao (Sahel)')]:
  rows.append({'id':i+'_S','n':n,'km2':round(A(G[i].intersection(Y))),'pct':round(100*A(G[i].intersection(Y))/A(G[i]),1)})
print(rows)
C['me9'].update(polys=out,km2=km2,states=[r for r in C['me9']['states'] if r['id'] not in ('BET','148','566_S','120_S','140_S')]+rows)
json.dump(C,open(F_+'.tmp','w'),separators=(',',':'),ensure_ascii=False);os.replace(F_+'.tmp',F_)
