"""Version 219: the no-gaps rule for the Super Caliphate (V9, key 'v2') after tools/v9_super219.py and tools/fill_gaps.py v2.
Drops from tools/data/gaps_v2.geojson every pocket inside East Turkestan (tools/data/v9_east_turkestan_v218.geojson, less Qinghai,
which is Greater Tibet), as Nawaz took East Turkestan out (Tashkurgan would otherwise be filled again), then runs
tools/silhouette_gaps204.py for V9 only (V8, 'x3', is left as it is).
Run: python3 tools/v9_super_gaps219.py <dir with cn_tibet.parquet>"""
import json, os, sys, shapely, pyarrow.parquet as pq
from shapely import wkb
from shapely.geometry import shape
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = sys.argv[1]
ET = shape(json.load(open(os.path.join(P, 'tools/data/v9_east_turkestan_v218.geojson')))['features'][0]['geometry'])
QH = [shapely.make_valid(wkb.loads(r['geometry'])) for r in pq.read_table(os.path.join(D, 'cn_tibet.parquet')).to_pylist() if r['subtype'] == 'region' and r['region'] == 'CN-QH'][0]
ETo = ET.difference(QH)
F = os.path.join(P, 'tools/data/gaps_v2.geojson'); d = json.load(open(F))
keep = [f for f in d['features'] if not shape(f['geometry']).representative_point().within(ETo)]
print('pockets inside East Turkestan left unfilled:', len(d['features']) - len(keep))
d['features'] = keep; json.dump(d, open(F, 'w'))
src = open(os.path.join(P, 'tools/silhouette_gaps204.py')).read()
assert src.count("for k in ['x3', 'v2']:") == 1
exec(compile(src.replace("for k in ['x3', 'v2']:", "for k in ['v2']:").replace("os.path.dirname(os.path.abspath(__file__))", repr(os.path.join(P, 'tools'))), 'silhouette_gaps204', 'exec'))
