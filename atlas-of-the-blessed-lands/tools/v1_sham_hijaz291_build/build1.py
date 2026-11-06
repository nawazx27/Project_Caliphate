import json,subprocess,shapely,pickle,sys,collections
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,MultiPolygon,Polygon,box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]
T=shape(json.load(open(D+'/sham_trace.json'))).buffer(0)
rows=pq.read_table(D+'/divs.parquet').to_pylist()
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
G={f['id']:(f['properties']['n'],shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
land=shapely.union_all([g for n,g in G.values() if g.intersects(T)])
tl=T.intersection(land)
take=[];log=collections.defaultdict(list);skip=collections.defaultdict(list)
for r in rows:
    if r['country']=='SA' or r['subtype']!='county': continue
    g=wkb.loads(r['geometry']).buffer(0)
    if not g.intersects(T): continue
    f=g.intersection(T).area/g.area; n=(r['names'] or {}).get('primary')
    if n=='لواء القويرة': f=0.5
    (take if f>=0.5 else []).append(g)
    (log if f>=0.5 else skip)[r['country']].append((n,round(100*f)))
for c in log: print(c,'IN',len(log[c]),log[c] if c in ('TR','EG') else '')
for c in skip: print(c,'OUT',[s for s in skip[c] if s[1]>=10])
SH=shapely.union_all(take+[G['275'][1]])
HJ=shapely.union_all([wkb.loads(r['geometry']).buffer(0) for r in rows if r['country']=='SA' and (r['names'] or {}).get('primary') in ('منطقة تبوك','منطقة المدينة المنورة','منطقة مكة المكرمة','منطقة الباحة')])
print('trace land km2',round(A(tl)),'Sham districts km2',round(A(SH)),'Hijaz km2',round(A(HJ)))
print('trace land left out km2',round(A(tl.difference(SH.buffer(0.01)))),'districts beyond trace km2',round(A(SH.difference(T))))
pickle.dump((SH,HJ),open(D+'/v1parts.pkl','wb'))
