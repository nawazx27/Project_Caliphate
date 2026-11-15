"""Version 430 (Nawaz: "trace all four rivers end to end correctly and accurately into the atlas"). Builds each of the four rivers of Ṣaḥīḥ Muslim 2839 from
OpenStreetMap river lines (fetched by tools/v430_fetch_rivers.py; RIV env = their folder) and writes src/four_rivers.json:
  Sayḥān = the Seyhan with its longest headstream, the Zamantı, from its source to the Mediterranean;
  Jayḥān = the Ceyhan from its source at Elbistan to the Gulf of İskenderun;
  the Euphrates from both headstreams, the Karasu (Erzurum) and the Murat (Aladağ, north of Lake Van), past the Keban confluence, through Syria and Iraq
    to al-Qurna, and on as the Shatt al-ʿArab to the Gulf;
  the Nile from its farthest source, the Ruvyironza in Burundi, by the Ruvubu and the Kagera to Lake Victoria, the Victoria Nile through Lake Kyoga to
    Lake Albert, the Albert Nile, the Baḥr al-Jabal and the White Nile to Khartoum, with the Blue Nile from the Gilgel Abay through Lake Ṭānā,
    and the main Nile to Cairo and both Delta branches (Rosetta, Damietta) to the sea.
Method: the named segments become a graph (ends within 300 m joined; gaps up to 6 km bridged at a cost; gaps through lakes bridged and not drawn); the
shortest path from a source point to the mouth is taken. Simplified to ~150 m."""
import pyarrow.parquet as pq, shapely, json, os, re, heapq, math, numpy as np
from shapely.geometry import LineString, MultiLineString, Point, shape
from shapely.ops import unary_union, linemerge
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RIV = os.environ['RIV']; GD = Geod(ellps='WGS84')
km = lambda a, b: GD.inv(a[0], a[1], b[0], b[1])[2] / 1000
LAKES = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(HERE, 'lakes.geojson')))['features']]).buffer(0.05)
def load(box, pat, bad=None, unnamed_km=15):
    """named segments matching pat (cost x1), plus nameless river lines within unnamed_km of them (cost x2, to cross reservoirs and gaps)"""
    named, nameless = [], []
    for r in pq.read_table(os.path.join(RIV, 'v430_rivers_%s.parquet' % box)).to_pylist():
        nm = ((r['names'] or {}).get('primary') or ''); en = dict((r['names'] or {}).get('common') or []).get('en', '')
        s = (nm + ' | ' + en); g = shapely.from_wkb(r['geometry'])
        if re.search(pat, s, re.I) and not (bad and re.search(bad, s, re.I)):
            named += [(s, list(l.coords), 1.0) for l in getattr(g, 'geoms', [g])]
        elif not nm.strip() and not en.strip():
            nameless += [('', list(l.coords), 2.0) for l in getattr(g, 'geoms', [g])]
    zone = unary_union([LineString(c) for n, c, f in named]).buffer(unnamed_km / 111)
    tree = shapely.STRtree([LineString(c) for n, c, f in nameless])
    near = [nameless[i] for i in tree.query(zone, predicate='intersects')]
    segs = named + near
    # node T-junctions: split a segment where another segment's end touches its interior (within 300 m)
    lines = [LineString(c) for n, c, f in segs]; tree = shapely.STRtree(lines); cuts = {}
    for i, l in enumerate(lines):
        for e in (Point(l.coords[0]), Point(l.coords[-1])):
            for j in tree.query(e.buffer(0.003)):
                if j == i: continue
                m = lines[j]; d = m.project(e)
                if 0.003 < d < m.length - 0.003 and m.distance(e) < 0.003: cuts.setdefault(int(j), []).append(d)
    out = []
    from shapely.ops import substring
    for i, (n, c, f) in enumerate(segs):
        ds_ = sorted(set([0.0] + cuts.get(i, []) + [lines[i].length]))
        for x0, x1 in zip(ds_[:-1], ds_[1:]):
            if x1 - x0 > 1e-6: out.append((n, list(substring(lines[i], x0, x1).coords), f))
    print('      %d named + %d nameless segments, %d after noding' % (len(named), len(near), len(out)))
    return out
def hav(p, Q):   # km from point p to every row of Q
    p = np.radians(p); Q = np.radians(Q)
    h = np.sin((Q[:, 1] - p[1]) / 2) ** 2 + np.cos(p[1]) * np.cos(Q[:, 1]) * np.sin((Q[:, 0] - p[0]) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))
_cache = {}
def build(segs, maxbridge=6.0, lakebridge=350.0):
    if id(segs) in _cache: return _cache[id(segs)]
    ends = []
    for i, (n, c, f) in enumerate(segs): ends += [c[0], c[-1]]
    pts = np.array(ends); N = len(pts); node = list(range(N))
    def find(a):
        while node[a] != a: node[a] = node[node[a]]; a = node[a]
        return a
    for a in range(N):
        for b in np.nonzero(hav(pts[a], pts) < 0.3)[0]: node[find(a)] = find(int(b))
    adj = {}
    def add(u, v, w, kind, data):
        adj.setdefault(u, []).append((v, w, kind, data)); adj.setdefault(v, []).append((u, w, kind, data))
    for i, (n, c, f) in enumerate(segs):
        L = GD.line_length([x for x, y in c], [y for x, y in c]) / 1000; add(find(2 * i), find(2 * i + 1), L * f, 'seg', i)
    reps = sorted(set(find(a) for a in range(N))); RP = pts[reps]
    nearlake = [i for i, r in enumerate(reps) if LAKES.distance(Point(RP[i])) < 0.03]
    for i in range(len(reps)):
        d = hav(RP[i], RP)
        for j in np.nonzero((d < maxbridge) & (np.arange(len(reps)) > i))[0]: add(reps[i], reps[j], 3 * d[j], 'bridge', (tuple(RP[i]), tuple(RP[j])))
    for ii, i in enumerate(nearlake):
        for j in nearlake[ii + 1:]:
            d = hav(RP[i], RP[j:j + 1])[0]
            if maxbridge <= d < lakebridge:
                ln = LineString([RP[i], RP[j]])
                if ln.intersection(LAKES).length > 0.85 * ln.length: add(reps[i], reps[j], 1.5 * d, 'lake', (tuple(RP[i]), tuple(RP[j])))
    _cache[id(segs)] = (adj, reps, RP); return _cache[id(segs)]
def path(segs, src, dst):
    adj, reps, RP = build(segs)
    s = reps[int(np.argmin(hav(src, RP)))]; t = reps[int(np.argmin(hav(dst, RP)))]
    print('      source snapped %.1f km, mouth snapped %.1f km' % (hav(src, RP).min(), hav(dst, RP).min()))
    dist = {s: 0}; prev = {}; q = [(0, s)]
    while q:
        d, u = heapq.heappop(q)
        if u == t: break
        if d > dist.get(u, 1e18): continue
        for v, w, kind, data in adj.get(u, []):
            if d + w < dist.get(v, 1e18): dist[v] = d + w; prev[v] = (u, kind, data); heapq.heappush(q, (d + w, v))
    if t not in prev: raise SystemExit('no path')
    lines = []; u = t; bridges = []; lakes = []; used_nameless = []
    while u != s:
        p, kind, data = prev[u]
        if kind == 'seg': lines.append(LineString(segs[data][1])); used_nameless.append(segs[data][2] > 1)
        elif kind == 'bridge': lines.append(LineString(data)); bridges.append(km(*data))
        else: lakes.append(km(*data))
        u = p
    g = linemerge(unary_union(lines))
    print('      nameless segments used: %d' % sum(used_nameless)); print('      %.0f km drawn; small gaps bridged: %d (max %.1f km); lake crossings: %s km' % (sum(GD.geometry_length(x) for x in getattr(g, 'geoms', [g])) / 1000, len(bridges), max(bridges or [0]), [round(x) for x in lakes]))
    return g
R = {}
print('Sayhan (Seyhan)')
R['seyhan'] = path(load('turkey_south', r'^(Seyhan|Zamantı)\b'), (36.45, 38.95), (34.88, 36.72))
print('Jayhan (Ceyhan)')
R['ceyhan'] = path(load('turkey_south', r'^Ceyhan\b'), (37.2, 38.25), (35.55, 36.62))
EU = r'^(Fırat|Euphrates|الفرات|نهر الفرات|شط العرب|Karasu\b|Karasu Irmağı|Karasu Çayı|Murat Nehri|Murat River|Le Murat|نهر مراد)'
EUS = load('euphrates', EU)
print('Euphrates via the Karasu'); a = path(EUS, (41.27, 40.05), (48.53, 29.92))
print('Euphrates via the Murat'); b = path(EUS, (43.45, 39.35), (38.8, 38.75))
R['euphrates'] = linemerge(unary_union([a, b]))
NI = r'(Ruvyironza|Ruvubu|Akagera|Kagera|Victoria Nile|Albert Nile|Bahr al Jabal|White Nile|النيل الأبيض|نهر النيل|^النيل|\| Nile|فرع دمياط|فرع رشيد|Rosetta)'
BL = r'(Gilgel Abay|ዓባይ|Abay|النيل الأزرق|ጥቁር ዓባይ|Blue Nile)'
segs = load('nile', NI + '|' + BL, r'Tana River|Gibe|وادي|Wadi|Atbar|عطبرة|Wadyan|Widyan')
print('Nile: Ruvyironza to the Rosetta mouth'); a = path(segs, (29.85, -3.85), (30.36, 31.46))
print('Nile: Ruvyironza to the Damietta mouth'); b = path(segs, (29.85, -3.85), (31.84, 31.51))
print('Blue Nile: Gilgel Abay to Khartoum'); c = path(segs, (37.03, 10.95), (32.51, 15.62))
R['nile'] = linemerge(unary_union([a, b, c]))
out = {'n': 'The four rivers of Sahih Muslim 2839, traced end to end from OpenStreetMap (Overture Maps 2026-10-21.0) by tools/v430_trace_rivers.py', 'rivers': []}
NAMES = {'seyhan': 'Sayḥān · Seyhan', 'ceyhan': 'Jayḥān · Ceyhan', 'euphrates': 'al-Furāt · Euphrates', 'nile': 'al-Nīl · Nile'}
for k, g in R.items():
    g = g.simplify(0.0015)
    parts = [[[round(x, 3), round(y, 3)] for x, y in l.coords] for l in getattr(g, "geoms", [g])]   # 0.001 deg (~100 m), so build.js can pack them
    out['rivers'].append({'k': k, 'n': NAMES[k], 'parts': parts})
    print(k, 'parts', len(parts), 'points', sum(len(p) for p in parts), 'bounds', [round(v, 2) for v in g.bounds])
json.dump(out, open(os.path.join(HERE, 'src/four_rivers.json'), 'w'), separators=(',', ':'), ensure_ascii=False)
