import pickle,json,subprocess,shapely,sys
from shapely.geometry import shape,box
from pyproj import Geod
A=lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6
D=sys.argv[1]; X=pickle.load(open(D+'/'+sys.argv[2],'rb'))
geo=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"]))
win=box(30,14,52,41)
land=shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(win)]).intersection(win)
rest=land.difference(X)
# only consider land within 400 km window of X: cut by X's hull to find pockets
hull=X.convex_hull
r=rest.intersection(hull)
XB=X.buffer(0.05)
for q in sorted(getattr(r,'geoms',[r]),key=lambda p:-p.area):
    if A(q)<200: continue
    full=[p for p in getattr(rest,'geoms',[rest]) if p.intersects(q)]
    t=q.exterior.intersection(XB).length/q.exterior.length
    print('pocket inside hull: %d km2, edge on outline %.0f%%, centre %s'%(A(q),100*t,tuple(round(v,1) for v in q.representative_point().coords[0])))
fill=[q for q in getattr(r,'geoms',[r]) if A(q)>=1 and q.exterior.intersection(XB).length/q.exterior.length>=0.8]
print('filling',len(fill),'pockets',round(sum(A(q) for q in fill)),'km2')
X=shapely.union_all([X]+[q.buffer(0.003) for q in fill]).buffer(0)
pickle.dump(X,open(D+'/'+sys.argv[3],'wb'))
