"""Version 485 (Nawaz, the Wikipedia Nile article again). Check of the drawn Nile (src/four_rivers.json) against the article: every place on the course
lies on the line, but the furthest source was not reached: "the source of the Nile is a tributary of the Rukarara River, in Nyungwe National Park,
Rwanda, at 2 19 35 S 29 21 30 E", leading to the Mwogo, the Nyabarongo and the Kagera; the trace followed the Kagera only up its Burundi head (the
Ruvyironza), 124 km from that spring. Added from the same OpenStreetMap/Overture data (v430_rivers_nile.parquet): every piece named Akagera/Kagera,
Nyabarongo, Mwogo, Rukarara or Ruvyironza that joins the drawn river, then the unnamed head stream from the Rukarara up to the spring (the chain of
waterway pieces leading closest to 29.3583 E 2.3264 S). New pieces simplified to ~40 m. Usage: python3 tools/v485_nile_rukarara.py <v430_rivers_nile.parquet>."""
import json, os, sys, shapely, pyarrow.parquet as pq, networkx as nx
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
F_ = os.path.join(HERE, 'src/four_rivers.json'); R = json.load(open(F_)); N = [r for r in R['rivers'] if r['k'] == 'nile'][0]
SP = Point(29.3583, -2.3264)
rows = [r for r in pq.read_table(sys.argv[1], columns=['names', 'geometry']).to_pylist()]
nm = lambda r: ((r['names'].get('primary') if isinstance(r['names'], dict) else r['names']) or '') if r.get('names') else ''
geo = [(nm(r), shapely.from_wkb(r['geometry'])) for r in rows]
geo = [(n, g) for n, g in geo if g.geom_type == 'LineString' and g.intersects(box(28.8, -4.2, 31.9, -0.8))]
cur = unary_union([LineString(c) for c in N['parts']]); add = []
NAMES = ('akagera', 'kagera', 'nyabarongo', 'mwogo', 'rukarara', 'ruvyironza')
cand = [g for n, g in geo if any(k == n.lower().strip() or n.lower().startswith(k) for k in NAMES)]
while True:
    new = [g for g in cand if g.distance(cur) < 0.01 and g.difference(cur.buffer(0.003)).length > 0.3 * g.length]
    if not new: break
    for g in new: add.append(g); cur = cur.union(g); cand.remove(g)
print('named pieces added', len(add), '| distance to the spring now', round(cur.distance(SP) * 111, 1), 'km')
# the head stream: shortest chain of (any) waterway pieces from the drawn line to the piece nearest the spring
loc = [g for n, g in geo if g.distance(SP) < 0.3]
G = nx.Graph()
for i, g in enumerate(loc):
    G.add_node(i)
    for j in range(i):
        if g.distance(loc[j]) < 0.002: G.add_edge(i, j, w=g.length)
start = [i for i, g in enumerate(loc) if g.distance(cur) < 0.002]
goal = min(range(len(loc)), key=lambda i: loc[i].distance(SP))
best = None
for s in start:
    try:
        p = nx.shortest_path(G, s, goal, weight='w')
        if best is None or len(p) < len(best): best = p
    except nx.NetworkXNoPath: pass
if best:
    for i in best:
        if loc[i].difference(cur.buffer(0.003)).length > 0.2 * loc[i].length: add.append(loc[i]); cur = cur.union(loc[i])
print('head-stream pieces', len(best or []), '| distance to the spring now', round(cur.distance(SP) * 111, 2), 'km')
for g in add: N['parts'].append([[round(x, 4), round(y, 4)] for x, y in g.simplify(0.0004).coords])
json.dump(R, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
