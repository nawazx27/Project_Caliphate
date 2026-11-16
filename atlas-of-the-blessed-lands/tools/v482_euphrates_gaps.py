"""Version 482 (Nawaz: "Are the entire four best rivers drawn accurately end to end?"). Check of src/four_rivers.json: the Seyhan and Ceyhan are one
unbroken line each; the Nile's only breaks are where it runs through lakes drawn on the map (Victoria, Kyoga, Albert, Tana, the Roseires/GERD reservoir).
The Euphrates had one visible break of ~7 km beside Ramadi (43.38-43.45 E): that stretch of the river, present in the same OpenStreetMap/Overture data
(name al-Furat) but dropped by the Version 430 trace, is added; and the Murat branch's sub-kilometre breaks (0.1-0.8 km, where the trace's pieces did
not quite meet) are closed by joining the nearest ends. Usage: python3 tools/v482_euphrates_gaps.py <v430_rivers_euphrates.parquet>."""
import json, os, sys, shapely, pyarrow.parquet as pq
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
F_ = os.path.join(HERE, 'src/four_rivers.json'); R = json.load(open(F_))
E = [r for r in R['rivers'] if r['k'] == 'euphrates'][0]
cur = unary_union([LineString(c) for c in E['parts']])
added = 0
for r in pq.read_table(sys.argv[1]).to_pylist():
    g = shapely.from_wkb(r['geometry'])
    if g.geom_type != 'LineString' or not g.intersects(box(43.36, 33.40, 43.47, 33.50)): continue
    if g.difference(cur.buffer(0.003)).length > 0.5 * g.length:
        E['parts'].append([[round(x, 4), round(y, 4)] for x, y in g.coords]); added += 1; cur = cur.union(g)
print('Ramadi stretch pieces added:', added)
# close the small breaks between separate pieces only: while the line is in more than one piece, join the closest pair of pieces (< 1 km apart)
from shapely.ops import nearest_points
LK = unary_union([shapely.geometry.shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'lakes.geojson')))['features']])
skip = set(); joins = 0
while True:
    comps = list(getattr(unary_union([LineString(c) for c in E['parts']]).buffer(0.004), 'geoms', [None]))
    lines = unary_union([LineString(c) for c in E['parts']])
    if len(comps) < 2 or comps[0] is None: break
    best = None
    for a in range(len(comps)):
        for b in range(a + 1, len(comps)):
            d = comps[a].distance(comps[b])
            if best is None or d < best[0]: best = (d, a, b)
    if best[0] > 0.015: break
    la = lines.intersection(comps[best[1]]); lb = lines.intersection(comps[best[2]])
    p, q = nearest_points(la, lb)
    if LineString([p, q]).intersects(LK): print('   (across a lake, left as is)', round(p.x, 2), round(p.y, 2)); skip.add((best[1], best[2])); break
    E['parts'].append([[round(p.x, 4), round(p.y, 4)], [round(q.x, 4), round(q.y, 4)]]); joins += 1
print('small breaks joined:', joins)
comp = unary_union([LineString(c).buffer(0.004) for c in E['parts']]); print('Euphrates now in', len(getattr(comp, 'geoms', [comp])), 'piece(s) (lakes apart)')
json.dump(R, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
