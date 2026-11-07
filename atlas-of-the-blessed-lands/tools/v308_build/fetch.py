import json,pyarrow.dataset as ds,pyarrow.fs as pfs,shapely,pyarrow as pa,pyarrow.parquet as pq,sys
fs=pfs.S3FileSystem(anonymous=True,region='us-west-2')
d=ds.dataset('overturemaps-us-west-2/release/2026-10-21.0/theme=divisions/type=division_area/',filesystem=fs,format='parquet')
O=__import__('sys').argv[1] if len(__import__('sys').argv)>1 else './'
rows=[]
def get(c,sub,keep):
    t=d.to_table(filter=(ds.field('country')==c)&(ds.field('subtype')==sub),columns=['country','region','subtype','names','is_land','geometry']).to_pylist()
    n=0
    for r in t:
        nm=(r['names'] or {}).get('primary')
        if keep(r,nm): r['name']=nm; del r['names']; rows.append(r); n+=1
    print(c,sub,n,flush=True)
get('RU','region',lambda r,n: r['region'] in {'RU-STA','RU-KB','RU-CE','RU-DA','RU-KC','RU-SE','RU-IN'})
get('UA','region',lambda r,n: r['region'] in {'UA-61','UA-68','UA-71','UA-35','UA-21','UA-05'})
get('UA','county',lambda r,n: r['region']=='UA-71')
get('SK','region',lambda r,n: True)
get('AT','region',lambda r,n: r['region']=='AT-9')
get('AT','county',lambda r,n: r['region']=='AT-3')
get('DE','county',lambda r,n: r['region']=='DE-BY')
get('GB','county',lambda r,n: r['region']=='GB-SCT')
get('SA','county',lambda r,n: True)
pq.write_table(pa.Table.from_pylist(rows),O+'regions.parquet')
