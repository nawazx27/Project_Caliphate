"""Version 146 (Nawaz: "Make sure take cities that which are recognized on Google Maps and Apple Maps… because finding every single
little settlement will take a lot of time"). Along the two new lines (Africa, Caucasus), every CITY or TOWN (Overture Maps 2026-09-23.1
divisions, subtype locality, class city or town; not villages or hamlets) that the new edge of V2 / V2-B cuts is taken whole: by its
outline (division_area, any size) where it has one, else the city district (county or localadmin, up to 300 km²) holding its point
(e.g. Nevinnomyssk's городской округ), else a circle of about 1.5 km round its point. Cut = at least 1% of it on each
side, its outside part on land. Writes <out.geojson> for python3 tools/whole_slivers_apply.py <v> <out.geojson> and lists the places.
Run until none is cut: python3 tools/expand_towns146.py <x|xb> <division.parquet> <division_area.parquet> <spill.geojson> <out.geojson> [<counties.parquet>]"""
import json, os, subprocess, sys, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from pyproj import Geod
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
k, DP, AP, SP, OUT = sys.argv[1:6]
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']])
N = MultiPolygon([Polygon(r[0], r[1:]) for r in json.load(open(os.path.join(P, 'src/caliph.json')))[k]['polys']]).buffer(0)
spill = unary_union([shape(f['geometry']) for f in json.load(open(SP))['features']]).buffer(0.003)
edge = N.boundary.intersection(spill).intersection(land)
d = pq.read_table(DP, columns=['id', 'class', 'names', 'country', 'geometry']).to_pylist()
towns = {r['id']: r for r in d if r['class'] in ('city', 'town')}
areas = {}
for r in pq.read_table(AP, columns=['division_id', 'geometry']).to_pylist():
    if r['division_id'] in towns: areas[r['division_id']] = shapely.from_wkb(r['geometry'])
from shapely.strtree import STRtree
cg = []
if len(sys.argv) > 6:
    cg = [g for g in shapely.from_wkb(pq.read_table(sys.argv[6], columns=['geometry']).column('geometry').to_numpy(zero_copy_only=False))]
    cg = [g if g.is_valid else g.buffer(0) for g in cg]; cg = [g for g in cg if A(g) <= 300]
ct = STRtree(cg) if cg else None
def district(pt):
    if ct is None: return None
    h = [cg[j] for j in ct.query(pt, predicate='within')]
    return min(h, key=lambda g: g.area) if h else None
take, rows = [], []
near = edge.buffer(0.3)
for i, r in towns.items():
    pt = shapely.from_wkb(r['geometry'])
    if not near.contains(pt): continue
    g = areas.get(i)
    src = 'outline' if g is not None else None
    if g is None:
        g = district(pt); src = 'city district' if g is not None else 'circle'
    if g is None: g = pt.buffer(0.0135)
    elif not g.is_valid: g = g.buffer(0)
    if not g.intersects(edge): continue
    a = A(g); f = A(g.intersection(N)) / a
    if 0.01 < f < 0.99 and not g.difference(N).intersection(land).is_empty:
        take.append(g); rows.append((r['class'], (r['names'] or {}).get('primary'), r['country'], round(a, 1), src))
print(k, 'cities and towns cut by the new edge', len(take))
for c, n, cc, a, o in sorted(rows, key=lambda x: -x[3]): print('  ', c, n, cc, a, 'km2', '(' + o + ')')
json.dump({'type': 'FeatureCollection', 'features': [] if not take else [{'type': 'Feature', 'properties': {'v': k, 'places': [r[1] for r in rows]}, 'geometry': mapping(unary_union(take))}]}, open(OUT, 'w'))
