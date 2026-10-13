# Version 107: the settlement scan, with the Balkan countries that are only partly inside judged against the OpenStreetMap outline (balkan_north.geojson) plus the towns taken in. See notes.md Versions 106-107.
# and in the partly included countries (Uzbekistan, Kyrgyzstan, Kazakhstan, China; India in V2N) the drawn line decides.
# Population: Meta High Resolution Settlement Layer (~30 m). Real borders: Overture Maps country areas (from OpenStreetMap).
import json, sys, os, time, numpy as np, shapely, pyarrow.parquet as pq
from concurrent.futures import ThreadPoolExecutor
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import rasterize, shapes
from scipy import ndimage
from shapely.geometry import Polygon, MultiPolygon, box, shape, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree
from affine import Affine
OUT=sys.argv[1]; CELLS=[tuple(c) for c in json.load(open(sys.argv[2]))]
VRT='/vsicurl/https://dataforgood-fb-data.s3.amazonaws.com/hrsl-cogs/hrsl_general/hrsl_general-latest.vrt'
V=json.load(open('v2.json')); MEM=json.load(open('members.json'))
GE={k:[g for g in MultiPolygon([Polygon(p[0],p[1:]) for p in V[k]+V['extra']]).buffer(0).geoms] for k in ['x','xn']}
TV={k:STRtree(GE[k]) for k in GE}
t=pq.read_table('ov_country.parquet',columns=['country','is_land','geometry'])
parts=[]; pcc=[]
for c,land,wkb in zip(t.column('country').to_pylist(),t.column('is_land').to_pylist(),t.column('geometry').to_pylist()):
    if not land: continue
    g=shapely.from_wkb(wkb)
    for p in getattr(g,'geoms',[g]): parts.append(p); pcc.append(c)
TC=STRtree(parts)
# Balkan countries only partly inside (Version 107): their homes count as inside unless they lie in the part north of the
# Sava-Danube-Kupa line (or, for Italy, outside the Trieste piece), from the OpenStreetMap outline itself
BN=json.load(open('balkan_north.geojson'))['features'] if os.path.exists('balkan_north.geojson') else []
BNC={f['properties']['cc'] for f in BN}
BNG=[g for f in BN for g in getattr(shape(f['geometry']),'geoms',[shape(f['geometry'])])]
TBN=STRtree(BNG) if BNG else None
import glob
ADDG={'x':[],'xn':[]}
for fn in sorted(glob.glob('/home/user/Project_Caliphate/atlas-of-the-blessed-lands/tools/data/balkan_settlements*.geojson')):
    for f in json.load(open(fn))['features']:
        g=shape(f['geometry']); ADDG[f['properties']['v']].extend(getattr(g,'geoms',[g]))
ADDT={k:STRtree(v) for k,v in ADDG.items() if v}
M=0.04; DIL=3
def ras(geoms,bounds,tr,shp):
    b=box(*bounds); gs=[]
    for g in geoms:
        h=g.intersection(b)
        if not h.is_empty: gs.append(h)
    if not gs: return np.zeros(shp,bool)
    return rasterize([(g,1) for g in gs],out_shape=shp,transform=tr,fill=0,dtype='uint8').astype(bool)
def do(cell, margin=M):
    cx,cy=cell; x0,y0=cx/10,cy/10; core=(x0,y0,x0+0.1,y0+0.1)
    bounds=(x0-margin,y0-margin,x0+0.1+margin,y0+0.1+margin)
    for attempt in range(4):
        try:
            with rasterio.open(VRT) as r:
                w=from_bounds(*bounds,r.transform).round_offsets().round_lengths()
                a=r.read(1,window=w,boundless=True,fill_value=np.nan); tr=r.window_transform(w)
            break
        except Exception as e:
            if attempt==3: return {'cell':cell,'error':str(e)}
            time.sleep(2+3*attempt)
    pop=np.where(np.isfinite(a)&(a>0),a,0.0)
    if pop.sum()==0: return {'cell':cell,'pop':0,'splits':[]}
    shp=a.shape; wb=(tr.c,tr.f+tr.e*shp[0],tr.c+tr.a*shp[1],tr.f)
    b=box(*wb); idx=TC.query(b)
    # country code per pixel (first hit), plus member/non-member/partial flags
    code=np.full(shp,'',dtype=object)
    flags={}
    for k in ['x','xn']:
        whole=set(MEM[k]['whole']); part=set(MEM[k]['part'])
        m_w=ras([parts[i] for i in idx if pcc[i] in whole],wb,tr,shp)
        m_p=ras([parts[i] for i in idx if pcc[i] in part],wb,tr,shp)
        m_n=ras([parts[i] for i in idx if pcc[i] not in whole and pcc[i] not in part],wb,tr,shp)
        vin=ras([GE[k][i] for i in TV[k].query(b)],wb,tr,shp)
        intended=np.where(m_w&~m_n&~m_p,True,np.where(m_n&~m_w&~m_p,False,vin))
        if TBN is not None:
            m_pb=ras([parts[i] for i in idx if pcc[i] in BNC],wb,tr,shp)
            if m_pb.any():
                north=ras([BNG[i] for i in TBN.query(b)],wb,tr,shp)
                added=ras([ADDG[k][i] for i in ADDT[k].query(b)],wb,tr,shp) if ADDG[k] else np.zeros(shp,bool)
                intended=np.where(m_pb&~m_w,(~north)|added,intended)   # towns taken in whole on the Balkan line count too
        valid=m_w|m_n|m_p
        flags[k]=(intended,valid,m_p)
    cc_list=sorted(set(pcc[i] for i in idx))
    ccode=np.zeros(shp,np.int16)-1
    for j,c in enumerate(cc_list):
        m=ras([parts[i] for i in idx if pcc[i]==c],wb,tr,shp); ccode[m&(ccode<0)]=j
    occ=pop>0
    lab,n=ndimage.label(ndimage.binary_dilation(occ,iterations=DIL)); lab=np.where(occ,lab,0)
    res=[]
    for k in ['x','xn']:
        ins,valid,mp_=flags[k]
        pi=np.bincount(lab[ins&valid].ravel(),weights=pop[ins&valid].ravel(),minlength=n+1)
        po=np.bincount(lab[~ins&valid].ravel(),weights=pop[~ins&valid].ravel(),minlength=n+1)
        edge=(ndimage.binary_dilation(ins)&~ins)|(ins&ndimage.binary_dilation(~ins))
        for L in np.where((pi>0)&(po>0))[0]:
            if L==0: continue
            sub=lab==L; rr,cc=np.where(sub)
            er,ec=np.where(sub&edge)
            if len(er)==0: er,ec=rr,cc
            lon=tr.c+tr.a*(ec.mean()+0.5); lat=tr.f+tr.e*(er.mean()+0.5)
            if not (core[0]<=lon<core[2] and core[1]<=lat<core[3]): continue
            touches= rr.min()==0 or cc.min()==0 or rr.max()==shp[0]-1 or cc.max()==shp[1]-1
            # countries of the people on each side
            def bycc(m):
                d={}
                for j in np.unique(ccode[m]):
                    v=float(pop[m&(ccode==j)].sum())
                    if v>0: d[cc_list[j] if j>=0 else '?']=round(v,1)
                return d
            cin=bycc(sub&ins&valid); cout=bycc(sub&~ins&valid)
            kind='new' if (set(cin)&set(cout)) else 'border'
            r0,r1,c0,c1=rr.min(),rr.max()+1,cc.min(),cc.max()+1
            st=ndimage.binary_dilation(sub[r0:r1,c0:c1],iterations=1)
            fp=unary_union([shape(g) for g,v in shapes(st.astype('uint8'),mask=st,transform=tr*Affine.translation(c0,r0))])
            # people of this settlement on the outer side, as an outline (what would have to be added to keep it whole)
            so=(sub&~ins&valid)[r0:r1,c0:c1]; so=ndimage.binary_dilation(so,iterations=1)
            fo=unary_union([shape(g) for g,v in shapes(so.astype('uint8'),mask=so,transform=tr*Affine.translation(c0,r0))]) if so.any() else None
            res.append({'v':k,'lon':round(lon,5),'lat':round(lat,5),'in':round(float(pi[L]),1),'out':round(float(po[L]),1),'kind':kind,
                        'cin':cin,'cout':cout,'bbox':[round(wb[0]+tr.a*c0,5),round(wb[3]+tr.e*r1,5),round(wb[0]+tr.a*c1,5),round(wb[3]+tr.e*r0,5)],
                        'trunc':bool(touches),'fp':mapping(fp.simplify(0.0002)),'fout':mapping(fo.simplify(0.0001)) if fo is not None else None})
    return {'cell':cell,'pop':round(float(pop.sum())),'splits':res}
if __name__=='__main__':
    done=set()
    if os.path.exists(OUT):
        for line in open(OUT):
            d=json.loads(line)
            if 'error' not in d: done.add(tuple(d['cell']))
    todo=[c for c in CELLS if c not in done]
    print('cells to do',len(todo),flush=True); t0=time.time(); n=0
    with open(OUT,'a') as f, ThreadPoolExecutor(int(os.environ.get('NT','12'))) as ex:
        for d in ex.map(do,todo):
            f.write(json.dumps(d)+'\n'); f.flush(); n+=1
            if n%200==0: print(n,'cells',round(time.time()-t0),'s',flush=True)
    print('finished',n,round(time.time()-t0),'s')
