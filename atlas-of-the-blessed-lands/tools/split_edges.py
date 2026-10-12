# Version 106: sorts every piece of V2 / V2N edge into coast, existing border or new line. See notes.md Version 106.
# Classify every piece of V2 / V2N's edge: coast (sea on one side), border (different countries on the two sides) or new line (same country both sides).
import json, sys, math
import numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, LineString
from shapely.strtree import STRtree
from shapely import points as spoints, contains_xy
S=sys.argv[1]
V=json.load(open(S+'/v2.json')); G=json.load(open(S+'/countries.geojson'))
cg=[shape(f['geometry']).buffer(0) for f in G['features']]; cid=[str(f['id']) for f in G['features']]; cn=[f['properties']['n'] for f in G['features']]
tree=STRtree(cg)
def country_at(x,y):
    idx=tree.query(Point(x,y))
    for i in idx:
        if cg[i].contains(Point(x,y)): return i
    return -1
OFF=0.008   # ~800 m
STEP=0.004  # ~400 m segments
res={}
for k in ['x','xn']:
    polys=[Polygon(p[0],p[1:]) for p in V[k]]+[Polygon(p[0],p[1:]) for p in V['extra']]
    mp=MultiPolygon(polys).buffer(0)
    segs=[]
    for poly in getattr(mp,'geoms',[mp]):
        for ring in [poly.exterior,*poly.interiors]:
            c=np.asarray(ring.coords)
            for a,b in zip(c[:-1],c[1:]):
                L=math.hypot(*(b-a)); n=max(1,int(L/STEP))
                for t in range(n):
                    p=a+(b-a)*(t+0.5)/n; d=(b-a)/L if L>0 else np.array([1,0])
                    nx,ny=-d[1],d[0]
                    segs.append((p[0],p[1],nx,ny,L/n))
    segs=np.array(segs)
    # sample both sides
    lx=segs[:,0]+segs[:,2]*OFF; ly=segs[:,1]+segs[:,3]*OFF
    rx=segs[:,0]-segs[:,2]*OFF; ry=segs[:,1]-segs[:,3]*OFF
    def classify(xs,ys):
        out=np.full(len(xs),-1)
        pts=spoints(xs,ys)
        ii,jj=tree.query(pts,predicate='intersects')
        out[ii]=jj
        return out
    L=classify(lx,ly); R=classify(rx,ry)
    kind=np.where((L<0)|(R<0),'coast',np.where(L==R,'new','border'))
    km=segs[:,4]*111*np.cos(np.radians(segs[:,1]))  # rough
    for kd in ['coast','border','new']: print(k,kd,'~km',int(km[kind==kd].sum()))
    # countries for new line
    from collections import Counter
    c=Counter(); 
    for i in np.where(kind=='new')[0]: c[cn[L[i]]]+=km[i]
    print('  new line by country:', {a:int(b) for a,b in c.most_common()})
    cb=Counter()
    for i in np.where(kind=='border')[0]: cb[tuple(sorted((cn[L[i]],cn[R[i]])))]+=km[i]
    print('  borders:', len(cb), 'pairs; longest', [(a,int(b)) for a,b in cb.most_common(8)])
    keep=kind!='coast'
    res[k]={'pts':segs[keep][:,:2].round(5).tolist(),'kind':kind[keep].tolist(),'L':[cid[i] for i in L[keep]],'R':[cid[i] for i in R[keep]]}
json.dump(res,open(S+'/landedges.json','w'))
