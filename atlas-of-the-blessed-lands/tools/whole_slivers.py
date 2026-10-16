"""Version 145 (2026-10-14, Nawaz: "i said i want everything in!!!"). Outlines are stored on a 0.001° grid (about 110 m; build.js),
so an outline that follows a coast or border exactly leaves hairline slivers of the lands it holds outside it (about 390 km² in all
in V2 after Version 144). This takes, for V2 and V2-B, every land the version holds (each country listed whole, plus the partial lands'
own shapes: classical Khurāsān, the whole outline as it was in Version 144 (tools/data/outline144_<v>.geojson), Manqishlāq and the Ustyurt, the Ustyurt pocket, V5's Dagestan block, Lake Albert), finds what is still
outside, and widens each sliver by W degrees (default 0.001°, about 110 m) beyond the coast or border, so the rounded edge lies outside
the true one. Writes tools/data/whole_slivers_<v>.geojson. Run: python3 tools/whole_slivers.py <x|xb> [W]; then
python3 tools/whole_slivers_apply.py <x|xb>. My method; Nawaz's rule."""
import json, os, subprocess, sys
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
k = sys.argv[1]; W = float(sys.argv[2]) if len(sys.argv) > 2 else 0.001
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
F = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
C = json.load(open(os.path.join(P, 'src/caliph.json')))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
parts = [F[str(r['id'])] for r in C[k]['states'] if str(r['id']) in F]
for f in ['khorasan_classical', 'manqishlaq_ustyurt', 'ustyurt_pocket', 'caucasus_v5', 'lake_albert_drc', 'lake_albert_shore', 'africa_expand146', 'caucasus_expand146']:
    p = os.path.join(D, f + '.geojson')
    if os.path.exists(p): parts += [shape(g['geometry']).buffer(0) for g in json.load(open(p))['features'] if g['properties'].get('role', 'add') == 'add']
import glob   # the border towns taken whole (tools/whole_slivers_places.py) must be wholly inside too
for p in sorted(glob.glob(os.path.join(D, 'whole_slivers_places*_%s.geojson' % k)) + glob.glob(os.path.join(D, 'expand_towns146_*_%s.geojson' % k))): parts += [shape(g['geometry']).buffer(0) for g in json.load(open(p))['features']]
for p in [os.path.join(D, 'outline%s_%s.geojson' % (n, k)) for n in ('144', '145')]:   # all the version held in Versions 144 and 145 stays in
  if os.path.exists(p): parts += [shape(g['geometry']).buffer(0) for g in json.load(open(p))['features']]
T = unary_union(parts)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'v': k}, 'geometry': mapping(T)}]}, open(os.path.join(D, 'whole_slivers_held_%s.geojson' % k), 'w'))   # the held lands, for the town step
miss = T.difference(X)
print(k, 'held lands outside the outline', round(A(miss) * 1e6) if not miss.is_empty else 0, 'm2')
if os.environ.get('LIST'):
    for q in sorted(getattr(miss, 'geoms', [miss]), key=lambda q: -A(q))[:12]: print('  ', round(A(q), 4), [round(v, 3) for v in q.bounds])
piece = miss.buffer(W) if not miss.is_empty else miss   # not minus X: a sliver in a notch narrower than the grid must fill the notch
out = {'type': 'FeatureCollection', 'features': [] if piece.is_empty else [{'type': 'Feature', 'properties': {'v': k}, 'geometry': mapping(piece)}]}
json.dump(out, open(os.path.join(D, 'whole_slivers_%s.geojson' % k), 'w'))
if not piece.is_empty:
    sea = piece.difference(unary_union(list(F.values())))
    print(' widened piece', round(A(piece), 1), 'km2: at sea', round(A(sea), 1), '; on land outside the held lands', round(A(piece.difference(T).difference(sea)), 2))
