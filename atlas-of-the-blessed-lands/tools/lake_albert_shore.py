"""Version 144 (2026-10-14, Nawaz: "did you leave 0.03% of the lake?"). After Version 143 about 1.4 km² of Lake Albert (22 hairline
slivers, at most ~45 m wide, along the DR Congo shore) stayed outside, because outlines are stored to 0.001° (~110 m). This takes the
lake widened by 0.002° (~220 m) within DR Congo's land, minus V2, and adds whole every settlement the new edge would cut (Overture
buildings, release 2026-09-23.1, fetched to the scratchpad; blobs of buildings within ~45 m of each other), repeating until none is cut.
Writes tools/data/lake_albert_shore.geojson. Run: python3 tools/lake_albert_shore.py <buildings.parquet>"""
import json, os, subprocess, sys, shapely, numpy as np, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda x: abs(Geod(ellps='WGS84').geometry_area_perimeter(x)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
CD = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '180'][0]
lake = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Albert'][0]
X = MultiPolygon([Polygon(r[0], r[1:]) for r in json.load(open(os.path.join(P, 'src/caliph.json')))['x']['polys']]).buffer(0)
band = lake.buffer(0.002).intersection(unary_union([lake, CD])).difference(X)
b = shapely.from_wkb(pq.read_table(sys.argv[1]).column('geometry').to_numpy(zero_copy_only=False))
c = shapely.centroid(b)
zone = lake.buffer(0.05); keep = shapely.contains(zone, c); b, c = b[keep], c[keep]
land = CD.difference(lake); shapely.prepare(land)
for it in range(1, 11):
    N = unary_union([X, band]); shapely.prepare(N)
    edge = N.boundary.intersection(land.buffer(-0.0005))           # the new edge on DR Congo land
    near = shapely.dwithin(c, edge, 0.005)
    bb, cc = b[near], c[near]
    blobs = unary_union(shapely.buffer(bb, 0.0004)); blobs = list(getattr(blobs, 'geoms', [blobs]))
    ins = shapely.contains(N, cc); out = (~ins) & shapely.contains(land, cc)
    cut = [g for g in blobs if (shapely.contains(g, cc) & ins).any() and (shapely.contains(g, cc) & out).any()]
    print('pass', it, 'buildings near edge', len(bb), 'settlements cut', len(cut), flush=True)
    if not cut: break
    band = unary_union([band] + [g.buffer(0.0005).intersection(CD) for g in cut]).difference(X)
band = MultiPolygon([p for p in getattr(band, 'geoms', [band]) if p.area > 1e-7])
print('piece km2', round(A(band), 1), 'parts', len(band.geoms))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Lake Albert shore, DR Congo'}, 'geometry': mapping(band)}]},
          open(os.path.join(P, 'tools/data/lake_albert_shore.geojson'), 'w'))
