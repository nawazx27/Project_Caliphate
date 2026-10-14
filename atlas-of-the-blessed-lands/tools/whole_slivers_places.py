"""Version 145 (Nawaz: "Why not consider the nearest cities along the border as a whole for now"): instead of building footprints, the
named towns and villages (Overture Maps 2026-09-23.1 division_area, subtype locality (towns and villages, not administrative districts), from OpenStreetMap; the local
copy in the scratchpad) whose outline is cut by the new edge of V2 / V2-B (where tools/whole_slivers.py pushed it past a border onto
land the version did not hold) are taken whole. Only places on land the version did not hold (most of their outside part off the held lands) on land, and town-sized (100 km² or less) are taken; larger rural communes and districts are not. Writes <out.geojson> for
python3 tools/whole_slivers_apply.py <v> <out.geojson> and lists the places. Run until none is cut:
python3 tools/whole_slivers_places.py <x|xb> <division_area.parquet> <spill.geojson> <out.geojson>. My method; Nawaz's town rule."""
import json, os, subprocess, sys, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pyproj import Geod
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
k, DP, SP, OUT = sys.argv[1:5]
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
T = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/whole_slivers_held_%s.geojson' % k)))['features']])
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']])
N = MultiPolygon([Polygon(r[0], r[1:]) for r in json.load(open(os.path.join(P, 'src/caliph.json')))[k]['polys']]).buffer(0)
spill = unary_union([shape(f['geometry']) for f in json.load(open(SP))['features']]).buffer(0.003)
edge = N.boundary.intersection(spill).intersection(land)
parts = [g for g in getattr(edge, 'geoms', [edge]) if not g.is_empty]
t = pq.read_table(DP, columns=['subtype', 'names', 'country', 'geometry'])
keep = [i for i, s in enumerate(t.column('subtype').to_pylist()) if s == 'locality']
t = t.take(keep); G = shapely.from_wkb(t.column('geometry').to_numpy(zero_copy_only=False))
names = t.column('names').to_pylist(); cc = t.column('country').to_pylist()
hit = sorted(set(STRtree(G).query(parts, predicate='intersects')[1].tolist()))
take, rows = [], []
for i in hit:
    g = G[i] if G[i].is_valid else G[i].buffer(0)
    a = A(g)
    if a <= 0 or a > 100: continue
    f = A(g.intersection(N)) / a
    if 0.001 < f < 0.999 and A(g.difference(N).difference(T).intersection(land)) > 0.5 * A(g.difference(N)):
        take.append(g); rows.append((a, (names[i] or {}).get('primary'), cc[i]))
print(k, 'places cut by the new edge', len(take))
for a, n, c in sorted(rows, reverse=True)[:25]: print('  ', n, c, round(a, 1), 'km2')
piece = unary_union(take) if take else None
json.dump({'type': 'FeatureCollection', 'features': [] if piece is None else [{'type': 'Feature', 'properties': {'v': k, 'places': [r[1] for r in rows]}, 'geometry': mapping(piece)}]}, open(OUT, 'w'))
