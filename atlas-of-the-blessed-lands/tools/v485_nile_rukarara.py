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
import numpy as np
T = pq.read_table(sys.argv[1], columns=['names', 'geometry'])
GA = shapely.from_wkb(np.array(T.column('geometry').to_pylist(), dtype=object))
keep = np.where(shapely.intersects(GA, box(28.8, -4.2, 31.9, -0.8)) & (shapely.get_type_id(GA) == 1))[0]
NM = T.column('names').to_pylist()
nm = lambda r: ((r.get('primary') if isinstance(r, dict) else r) or '') if r else ''
geo = [(nm(NM[k]), GA[k]) for k in keep]; print('waterway pieces in the area', len(geo))
cur = unary_union([LineString(c) for c in N['parts']]).intersection(box(28.6, -4.4, 32.1, -0.6)); add = []   # the drawn river near the Kagera only (fast)
NAMES = ('akagera', 'kagera', 'nyabarongo', 'mwogo', 'rukarara', 'ruvyironza')
cand = [g for n, g in geo if any(n.lower().strip().startswith(k) for k in NAMES)]
while True:
    cb = cur.buffer(0.003)
    new = [g for g in cand if g.distance(cur) < 0.02 and g.difference(cb).length > 0.3 * g.length]
    if not new: break
    for g in new: add.append(g); cand.remove(g)
    cur = unary_union([cur] + new)
print('named pieces added', len(add), '| distance to the spring now', round(cur.distance(SP) * 111, 1), 'km')
# the head stream: the data's pieces between the drawn river and the spring do not all touch (the spring is on the Nyirabugoyi, which meets the
# Rukarara ~5 km from the nearest Rukarara piece in the data); so the chain is the shortest path through waterway pieces near the spring where a small
# gap (up to ~6 km) between two pieces costs ten times its length and is bridged by a short joining segment
from shapely.ops import nearest_points
loc = np.array([g for n, g in geo if g.distance(SP) < 0.45], dtype=object); print('pieces near the spring', len(loc))
tree = shapely.STRtree(loc); a, b = tree.query(loc, predicate='dwithin', distance=0.055)
G = nx.Graph(); G.add_nodes_from(range(len(loc)))
for x, y in zip(a, b):
    if x < y:
        gap = loc[x].distance(loc[y]); G.add_edge(int(x), int(y), w=(loc[x].length + loc[y].length) / 2 + 10 * gap, gap=gap)
start = [i for i, g in enumerate(loc) if g.distance(cur) < 0.004]
goal = min(range(len(loc)), key=lambda i: loc[i].distance(SP)); print('nearest piece to the spring is', round(loc[goal].distance(SP) * 111, 2), 'km away')
G.add_node('S')
for s_ in start: G.add_edge('S', s_, w=0, gap=0)
best = nx.shortest_path(G, 'S', goal, weight='w')[1:]
joins = []
for x, y in zip(best[:-1], best[1:]):
    if G[x][y]['gap'] > 0.001:
        p_, q_ = nearest_points(loc[x], loc[y]); joins.append(LineString([p_, q_]))
for i in best:
    if loc[i].difference(cur.buffer(0.003)).length > 0.2 * loc[i].length: add.append(loc[i])
add += joins
cur = unary_union([cur] + [loc[i] for i in best] + joins)
print('gaps bridged', len(joins), [round(j.length * 111, 1) for j in joins], 'km')
print('head-stream pieces', len(best or []), '| distance to the spring now', round(cur.distance(SP) * 111, 2), 'km')
for g in add: N['parts'].append([[round(x, 4), round(y, 4)] for x, y in g.simplify(0.0004).coords])
json.dump(R, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
