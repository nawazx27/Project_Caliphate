"""Version 430 helper (Nawaz: "trace all four rivers end to end correctly and accurately into the atlas"). Fetches OpenStreetMap river lines (Overture Maps
base/water, release 2026-10-21.0, class river) in three boxes (southern Türkiye for the Seyhan and Ceyhan, the Euphrates basin, the Nile basin) and saves them
to tools/data/v430_rivers_<box>.parquet. Only line geometries are kept."""
import pyarrow.fs as pfs, pyarrow.dataset as ds, pyarrow.parquet as pq, pyarrow as pa, os, time, shapely
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
fs = pfs.S3FileSystem(anonymous=True, region='us-west-2')
d = ds.dataset('overturemaps-us-west-2/release/2026-10-21.0/theme=base/type=water/', filesystem=fs, format='parquet')
F = lambda a: ds.field(('bbox', a))
BOXES = {'turkey_south': (33.5, 36.3, 37.8, 39.6), 'euphrates': (37.0, 29.3, 49.0, 40.6), 'nile': (28.0, -4.6, 40.5, 31.8)}
for k, (x0, y0, x1, y1) in BOXES.items():
    t0 = time.time()
    f = (F('xmax') > x0) & (F('xmin') < x1) & (F('ymax') > y0) & (F('ymin') < y1) & (ds.field('class') == 'river')
    t = d.to_table(filter=f, columns=['id', 'names', 'wikidata', 'geometry'])
    keep = [i for i, g in enumerate(t.column('geometry').to_pylist()) if shapely.from_wkb(g).geom_type in ('LineString', 'MultiLineString')]
    t = t.take(pa.array(keep, type=pa.int64()))
    pq.write_table(t, os.path.join(OUT, 'v430_rivers_%s.parquet' % k)); print(k, t.num_rows, 'lines', round(time.time() - t0), 's')
