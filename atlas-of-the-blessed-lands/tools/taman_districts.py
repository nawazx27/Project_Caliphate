"""Version 126 (2026-10-14). Nawaz circled on a screenshot of V2 the land west of the North Caucasus line: the Taman peninsula, Anapa and
the land up to the lower Kuban ("It should cover this land"). As in Version 125, whole districts (Overture Maps 2026-09-23.1, division_area
subtype county): his loop was placed on the map from the outline's corners (Anapa tip 37.237 E, 44.99 N; Abinsky's north-west corner
38.217 E, 45.189 N); each district with any real share inside it comes in whole, by the "include what seems doubtful and tell him" rule:
Anapa 100%, Krymsky 100%, Temryuksky (Taman) 100%, Slavyansky 56%, Krasnoarmeysky 28%. Krasnodar city (6%, the loop's end touching it)
is left out as the drawing's edge. Crimea (Kerch) is not in the loop. Writes tools/data/taman_districts.geojson (clipped to geo2's Russia).
Needs scratchpad ru_div_areas.parquet (Overture RU counties) as argument. Run: python3 tools/taman_districts.py <ru_div_areas.parquet>"""
import json, os, sys, subprocess, pyproj, shapely, pyarrow.parquet as pq
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
NAMES = {'муниципальный округ Анапа': 'Anapa', 'Крымский район': 'Krymsky', 'Темрюкский район': 'Temryuksky (Taman)',
         'Славянский район': 'Slavyansky', 'Красноармейский район': 'Krasnoarmeysky'}
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0].intersection(box(35.5, 44, 40, 46.5))
gs, rows, others = [], [], []
for r in pq.read_table(sys.argv[1]).to_pylist():
    n = (r['names'] or {}).get('primary')
    if r['subtype'] != 'county': continue
    g = shapely.from_wkb(r['geometry']).buffer(0)
    if n in NAMES: gs.append(g); rows.append(NAMES[n])
    elif g.intersects(box(35.5, 44, 40, 46.5)): others.append(g)
assert len(gs) == 5, rows
D = unary_union(gs)
S = RU.intersection(D.buffer(0.02)).difference(unary_union(others))   # coast slivers of geo2 just outside the districts come too; never into a neighbour
S = unary_union([q for q in getattr(S, 'geoms', [S]) if q.geom_type == 'Polygon' and A(q) >= 0.5])
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'id': 'RU-TAMAN', 'km2': round(A(S)), 'districts': rows}, 'geometry': mapping(S)}]}, open(os.path.join(H, 'data', 'taman_districts.geojson'), 'w'), ensure_ascii=False)
print('area', round(A(S)), 'km2', rows)
