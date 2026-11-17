"""Version 484 (Nawaz, the Wikipedia Seyhan River article: 560 km, "headwaters in the Tahtali Mountains (in Sivas and Kayseri provinces) in the
Anti-Taurus", left tributary the Zamanti (308 km, from near Pinarbasi, Kayseri); and the Ceyhan article: source "Sogutlu Dere" at Pinarbasi on the
Nurhak Mountains south-east of Elbistan, 509 km). The Version 430 trace (src/four_rivers.json) stopped short of these headwaters. Added from the same
OpenStreetMap/Overture data (v430_rivers_turkey_south.parquet): every piece named Zamanti, Goksu (the Seyhan's other head branch) or Seyhan not yet
drawn, and for the Ceyhan every piece named Ceyhan or Sogutlu Cayi, each only if it joins the drawn river (directly or through another added piece,
within ~1 km). The Seyhan and Ceyhan lines are then simplified to ~40 m (the new OSM pieces had a point every ~14 m). Usage: python3 tools/v484_seyhan_ceyhan_heads.py <v430_rivers_turkey_south.parquet>."""
import json, os, sys, shapely, pyarrow.parquet as pq, networkx as nx, numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
from scipy.spatial import cKDTree
from pyproj import Geod
gd = Geod(ellps='WGS84')
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
F_ = os.path.join(HERE, 'src/four_rivers.json'); R = json.load(open(F_))
rows = pq.read_table(sys.argv[1]).to_pylist()
def nm(r):
    n = r.get('names'); return (n.get('primary') if isinstance(n, dict) else n) or ''
def course(parts, mouth):
    G = nx.Graph(); key = lambda p: (round(p[0], 3), round(p[1], 3))
    for c in parts:
        for a, b in zip(c[:-1], c[1:]):
            ka, kb = key(a), key(b)
            if ka != kb: G.add_edge(ka, kb, w=gd.inv(a[0], a[1], b[0], b[1])[2] / 1000)
    nodes = list(G.nodes); T = cKDTree(np.array(nodes))
    for i, j in T.query_pairs(0.02):
        a, b = nodes[i], nodes[j]
        if not G.has_edge(a, b): G.add_edge(a, b, w=gd.inv(a[0], a[1], b[0], b[1])[2] / 1000)
    m = min(nodes, key=lambda n: (n[0] - mouth[0]) ** 2 + (n[1] - mouth[1]) ** 2)
    d = nx.single_source_dijkstra_path_length(G, m, weight='w'); far = max(d, key=d.get); return round(d[far]), far
for k, names, mouth in [('seyhan', ('Zamantı', 'Göksu', 'Seyhan', 'Seyhan Nehri'), (34.91, 36.73)), ('ceyhan', ('Ceyhan', 'Söğütlü Çayı'), (35.56, 36.57))]:
    r = [x for x in R['rivers'] if x['k'] == k][0]
    before = course(r['parts'], mouth)
    cand = [shapely.from_wkb(x['geometry']) for x in rows if nm(x) in names]
    cand = [g for g in cand if g.geom_type == 'LineString']
    cur = unary_union([LineString(c) for c in r['parts']]); added = 0
    while True:
        new = [g for g in cand if g.distance(cur) < 0.01 and g.difference(cur.buffer(0.003)).length > 0.3 * g.length]
        if not new: break
        for g in new:
            r['parts'].append([[round(x, 4), round(y, 4)] for x, y in g.coords]); cur = cur.union(g); added += 1
            cand.remove(g)
    after = course(r['parts'], mouth)
    print(r['n'], '| pieces added', added, '| longest course from the mouth', before[0], '->', after[0], 'km, source end at', after[1])
for r in R['rivers']:
    if r['k'] in ('seyhan', 'ceyhan'): r['parts'] = [[[round(x, 4), round(y, 4)] for x, y in LineString(c).simplify(0.0004).coords] for c in r['parts']]
json.dump(R, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
