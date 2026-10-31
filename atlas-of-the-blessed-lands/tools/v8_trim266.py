"""Version 266 (Nawaz: "Take the current V8, reduce the Balkans to Greece, use V[4] for Africa, use the two islands left of Italy and
preview", then "apply it"). V8 (CALIPH.v2, the Super Caliphate): every Balkan land but Greece out (Bulgaria, Albania, North Macedonia, Kosovo
and any other base-map unit of the peninsula; Greece and Turkiye kept whole); its Africa replaced by exactly V4's Africa (CALIPH.me9 within
the African countries); Corsica and Sardinia whole. Asia (South Asia, Kashmir, Greater Tibet, East Turkestan, Southeast Asia, PNG),
Iberia and Malta unchanged. Rerun after V4's Africa changes: python3 tools/v8_trim266.py"""
import os
import json,subprocess,sys,os,shapely
from shapely.geometry import shape,MultiPolygon,Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"],cwd=P))
G={f['id']:(f['properties'].get('n'),shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
land=unary_union([g for n,g in G.values()])
COR=unary_union([p for p in getattr(G['FRA'][1],'geoms',[G['FRA'][1]]) if 8.4<p.centroid.x<9.7 and 41.2<p.centroid.y<43.1])
SAR=unary_union([p for p in getattr(G['380'][1],'geoms',[G['380'][1]]) if 7.9<p.centroid.x<10.0 and 38.7<p.centroid.y<41.35])
F_=os.path.join(P,'src/caliph.json');C=json.load(open(F_))
M=lambda k: MultiPolygon([Polygon(q[0],q[1:]) for q in C[k]['polys']]).buffer(0)
V8,V4=M('v2'),M('me9')
# Africa: every country whose representative point lies in Africa (Sinai stays with Egypt), plus African islands
asia=Polygon([(32.6,31.6),(34.9,29.4),(43.4,12.6),(51.5,11.9),(60,22),(60,40),(32.6,40)])
afr_box=box(-30,-40,60,37.6).difference(asia)
AF=[i for i,(n,g) in G.items() if afr_box.contains(g.representative_point()) and i not in ('724','620','380','470','300','196','792','887','682','512')]
afr=unary_union([G[i][1] for i in AF])
print('African units',len(AF))
# Balkans except Greece
BK=[i for i,(n,g) in G.items() if box(13,39.6,30.5,48.5).contains(g.representative_point()) and i not in ('300','792','380','470')]
print('Balkan units removed',sorted(G[i][0] for i in BK))
bal=unary_union([G[i][1] for i in BK])
X=V8.difference(afr.buffer(0.002)).difference(bal.difference(G['300'][1]).difference(G['792'][1]).buffer(0.004))
X=shapely.union_all([X,V4.intersection(afr.buffer(0.02)),G['300'][1].buffer(0.003),COR.buffer(0.003),SAR.buffer(0.003),G['792'][1].intersection(V8).buffer(0.003)],grid_size=0.001)
print('V8 Africa before',round(A(V8.intersection(afr))),'after',round(A(X.intersection(afr))),'V4 Africa',round(A(V4.intersection(afr))))
out=[]
for q in getattr(X,'geoms',[X]):
  if q.geom_type!='Polygon' or A(q)<0.05: continue
  q=orient(Polygon(q.exterior,[h for h in q.interiors if A(Polygon(h))>=5000]),1.0)
  out.append([[[round(u,3),round(v,3)] for u,v in rr.coords] for rr in [q.exterior,*q.interiors]])
km2=int(subprocess.check_output(['node','-e',"""const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""],cwd=P,input=json.dumps(out).encode()))
Y=MultiPolygon([Polygon(r[0],r[1:]) for r in out]).buffer(0)
print('Corsica in %',round(100*A(COR.intersection(Y))/A(COR),1),'Sardinia in %',round(100*A(SAR.intersection(Y))/A(SAR),1))
for i in ['300','100','008','807','KOS','566','288','384','120','140','654','132']:
  if i in G: print(G[i][0],'in %',round(100*A(G[i][1].intersection(Y))/A(G[i][1]),1))
print('V8',C['v2']['km2'],'->',km2)
C['v2'].update(polys=out,km2=km2)
afr_ids=set(AF)|{'BET','SOL','BRT','MYT','CAN','CEU','MEL','MAD','PEL','REU','504_W','180_A','800_A','566_S','120_S','140_S'}
bk_ids=set(BK)|{'KOS','191_B','688_B','705_B','642_B','380_B'}
keep=[r for r in C['v2']['states'] if r['id'].split('_')[0] not in afr_ids and r['id'] not in afr_ids and r['id'] not in bk_ids]
v4af=[r for r in C['me9']['states'] if r['id'] in afr_ids or r['id'].split('_')[0] in afr_ids]
rows=keep+[dict(r,core=False) for r in v4af if r['id'] not in {k['id'] for k in keep}]
rows+=[{'id':'COR','n':'France: Corsica','km2':round(A(COR)),'pct':1.4,'core':False},{'id':'SAR','n':'Italy: Sardinia with its islands','km2':round(A(SAR)),'pct':8.0,'core':False}]
print('rows',len(C['v2']['states']),'->',len(rows),'removed',sorted(r['n'][:25] for r in C['v2']['states'] if r not in keep))
C['v2']['states']=rows
json.dump(C,open(F_+'.tmp','w'),separators=(',',':'),ensure_ascii=False); os.replace(F_+'.tmp',F_)
