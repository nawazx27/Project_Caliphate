import json,pickle,shapely,sys,subprocess
import pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape,LineString,Point,Polygon,box,MultiPolygon
from shapely.ops import substring
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
S=sys.argv[1]; R=S+'/riv/'
F={f:json.load(open(R+f+'.geojson'))['features'] for f in ['ne_10m_rivers_lake_centerlines','ne_10m_rivers_europe']}
def pieces(f,name,x0=None):
    out=[]
    for x in F[f]:
        if (x['properties'].get('name') or '')!=name: continue
        g=shape(x['geometry'])
        if x0 is not None and not (x0[0]<=g.bounds[0]<=x0[1]): continue
        out+=list(getattr(g,'geoms',[g]))
    return out
def chain(ls):
    ls=[list(l.coords) for l in ls]; cur=ls.pop(0)
    while ls:
        best=None
        for i,l in enumerate(ls):
            for rev in (False,True):
                c=l[::-1] if rev else l
                for end in ('tail','head'):
                    d=Point(cur[-1]).distance(Point(c[0])) if end=='tail' else Point(cur[0]).distance(Point(c[-1]))
                    if best is None or d<best[0]: best=(d,i,c,end)
        d,i,c,end=best; ls.pop(i)
        cur=cur+c if end=='tail' else c+cur
    return LineString(cur)
def seg(line,p,q):
    a=line.project(Point(p)); b=line.project(Point(q)); s=substring(line,min(a,b),max(a,b)); c=list(s.coords)
    return c if a<=b else c[::-1]
L='ne_10m_rivers_lake_centerlines'; E='ne_10m_rivers_europe'
dau=chain(pieces(L,'Daugava')+pieces(E,'Daugava'))
dne=chain(pieces(L,'Dnepre')+pieces(E,'Dnepr'))
ugr=chain(pieces(E,'Oka',(33.4,33.6)))
oka=chain(pieces(L,'Oka'))
vol=chain(pieces(L,'Volga',(32.5,32.7)))
kam=chain(pieces(L,'Kama',(49.3,49.4)))
bel=chain(pieces(L,'Belaya')+pieces(E,'Belaya',(57.9,58.0)))
ura=chain(pieces(L,'Ural',(51.0,51.2)))
P=[]
P+=seg(dau,(27.45,55.8),(31.13,55.62))         # Daugava upstream to Velizh
P+=seg(dne,(33.91,55.87),(33.4,54.93))         # (Valdai divide) Dnieper from its source down to Dorogobuzh
P+=seg(ugr,(33.51,54.55),(36.1,54.5))          # Ugra down to Kaluga
P+=seg(oka,(36.26,54.52),(43.98,56.33))        # Oka to Nizhny Novgorod
P+=seg(vol,(43.98,56.33),(49.36,55.17))        # Volga to the Kama mouth
P+=seg(kam,(49.36,55.17),(53.6,55.9))          # Kama up to the Belaya mouth
P+=seg(bel,(53.6,55.9),(55.96,54.73))          # Belaya up to Ufa
P+=[(57.2,54.9),(58.6,54.85)]                    # Ufa-Belaya divide (the river's own basin taken whole)
P+=seg(ura,(59.45,54.7),(58.6,51.2))           # Ural crest, then the Ural river to Orsk and Kazakhstan
json.dump(P,open(S+'/crim/rivfront.json','w'))
south=Polygon([(22,55.85)]+P+[(58.6,46),(22,46)]).buffer(0)
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
G={f['id']:shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land=shapely.union_all([G['112'],G['643']]).difference(box(19,54,23,56)).intersection(box(22,46,61.5,58))
X=pickle.load(open(S+'/crim/v7n4.pkl','rb'))
NEWL=south.intersection(land)
line=LineString(P); towns=[]
for r in pq.read_table(S+'/crim/towns_n.parquet').to_pylist():
    g=wkb.loads(r['geometry'])
    if A(g)<=500 and g.intersects(line): towns.append(g.buffer(0))
print('frontier km',round(Geod(ellps='WGS84').geometry_length(line)/1000),'towns on it taken whole',len(towns))
Y=shapely.union_all([X,NEWL.buffer(0.003)]+[t.buffer(0.003) for t in towns]).buffer(0)
pickle.dump(Y,open(S+'/crim/v7riv1.pkl','wb')); print('V7 km2',round(A(Y)))
for n,(x,y) in {'Smolensk':(32.05,54.78),'Vitebsk':(30.2,55.19),'Kaluga':(36.26,54.51),'Ryazan':(39.74,54.63),'Nizhny Novgorod':(44.0,56.33),'Kazan':(49.12,55.79),'Ufa':(55.96,54.73),'Magnitogorsk':(58.98,53.41),'Moscow':(37.62,55.75),'Chelyabinsk':(61.4,55.16)}.items(): print(n,'IN' if Y.contains(Point(x,y)) else 'out')
