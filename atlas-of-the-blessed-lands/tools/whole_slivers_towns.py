"""Version 145: settlements cut by the new edge where tools/whole_slivers.py pushed V2 / V2-B about 110 m past a coast or border onto
land the version did not hold. Buildings (Overture 2026-09-23.1, fetched along the new strips to the scratchpad) within ~45 m of each
other form one settlement; a settlement with buildings both inside and outside the outline is taken whole (its footprint widened
~55 m). Writes <out.geojson> for python3 tools/whole_slivers_apply.py <v> <out.geojson>; prints the count. Run until it finds none:
python3 tools/whole_slivers_towns.py <x|xb> <buildings.parquet> <spill.geojson> <out.geojson>. My method; Nawaz's town rule."""
import json, os, subprocess, sys, shapely, numpy as np, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
k, BP, SP, OUT = sys.argv[1:5]
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']]); shapely.prepare(land)
N = MultiPolygon([Polygon(r[0], r[1:]) for r in json.load(open(os.path.join(P, 'src/caliph.json')))[k]['polys']]).buffer(0)
spill = unary_union([shape(f['geometry']) for f in json.load(open(SP))['features']]).buffer(0.003)
edge = N.boundary.intersection(spill).intersection(land)
parts = [g for g in getattr(edge, 'geoms', [edge]) if not g.is_empty]
b = shapely.from_wkb(pq.read_table(BP).column('geometry').to_numpy(zero_copy_only=False)); c = shapely.centroid(b)
near = np.unique(STRtree(c).query(parts, predicate='dwithin', distance=0.005)[1])
bb, cc = b[near], c[near]
print(k, 'buildings near the new edge', len(bb), flush=True)
blobs = unary_union(shapely.buffer(bb, 0.0004)); blobs = list(getattr(blobs, 'geoms', [blobs]))
ins = shapely.contains(N, cc); out = (~ins) & shapely.contains(land, cc)
tree = STRtree(cc); cut = []
for g in blobs:
    idx = tree.query(g, predicate='contains')
    if ins[idx].any() and out[idx].any(): cut.append(g)
print(k, 'settlements cut', len(cut), 'buildings outside', int(sum(out[tree.query(g, predicate='contains')].sum() for g in cut)))
piece = unary_union([g.buffer(0.0005) for g in cut]).intersection(land) if cut else None
json.dump({'type': 'FeatureCollection', 'features': [] if piece is None or piece.is_empty else
           [{'type': 'Feature', 'properties': {'v': k}, 'geometry': mapping(piece)}]}, open(OUT, 'w'))
