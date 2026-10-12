# Version 106: names the settlements (Overture Maps divisions). Run in the scan folder; see notes.md Version 106.
import json, time, shapely, numpy as np, pyarrow.parquet as pq
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
T0 = time.time()
import os
F = json.load(open(os.environ.get('IN','scan2_final.json')))
t = pq.read_table('ov_division.parquet', columns=['subtype', 'class', 'names', 'country', 'population', 'geometry'])
g = shapely.from_wkb(t.column('geometry').to_numpy(zero_copy_only=False))
boxes = []
for ss in F.values():
    for s in ss:
        b = shape(s['fp']).bounds
        boxes.append(shapely.box(b[0] - 0.06, b[1] - 0.06, b[2] + 0.06, b[3] + 0.06))
keep = np.unique(STRtree(g).query(boxes, predicate='intersects')[1])
t = t.take(keep); g = g[keep]
print('kept', len(keep), round(time.time() - T0), 's', flush=True)
sub = t.column('subtype').to_pylist(); nm = t.column('names').to_pylist()
popu = t.column('population').to_pylist(); cty = t.column('country').to_pylist(); cls = t.column('class').to_pylist()
CR = {'megacity': 0, 'city': 1, 'town': 2, 'village': 3, 'hamlet': 4, None: 5}
tree = STRtree(g)
RANK = {'locality': 0, 'localadmin': 1, 'macrohood': 2, 'neighborhood': 3, 'microhood': 4}

def label(n):
    n = n or {}; p = n.get('primary'); com = n.get('common'); en = None
    if isinstance(com, dict): en = com.get('en')
    elif com: en = dict(com).get('en')
    return p, en

out = []
for cell, ss in F.items():
    for s in ss:
        fp = shape(s['fp']); fo = shape(s['fout']) if s.get('fout') else None
        shapely.prepare(fp)
        if fo is not None: shapely.prepare(fo)
        b = fp.bounds
        idx = tree.query(shapely.box(b[0] - 0.003, b[1] - 0.003, b[2] + 0.003, b[3] + 0.003))
        if len(idx): idx = idx[shapely.dwithin(fp, g[idx], 0.003)]
        places = []
        for i in idx:
            if sub[i] not in RANK: continue
            p, en = label(nm[i])
            side = 'out' if (fo is not None and shapely.dwithin(fo, g[i], 0.0005)) else 'in'
            places.append({'name': p, 'en': en, 'sub': sub[i], 'cls': cls[i], 'pop': popu[i], 'cc': cty[i], 'side': side})
        places.sort(key=lambda q: (RANK[q['sub']], -(q['pop'] or 0)))
        main = sorted([q for q in places if q['sub'] in ('locality', 'localadmin')], key=lambda q: (CR.get(q['cls'], 5), -(q['pop'] or 0)))
        if not main:  # nearest locality within about 5 km
            c = Point(s['lon'], s['lat']); best = None
            for i in tree.query(shapely.box(c.x - 0.05, c.y - 0.05, c.x + 0.05, c.y + 0.05)):
                if sub[i] in ('locality', 'localadmin'):
                    d = c.distance(g[i])
                    if best is None or d < best[0]: best = (d, i)
            if best:
                p, en = label(nm[best[1]])
                main = [{'name': p, 'en': en, 'sub': sub[best[1]], 'pop': popu[best[1]], 'cc': cty[best[1]], 'side': 'near', 'km': round(best[0] * 100, 1)}]
        s2 = {k: v for k, v in s.items() if k not in ('fp', 'fout')}
        s2['places'] = places; s2['main'] = main[:1]
        out.append(s2)
json.dump(out, open(os.environ.get('OUT','splits_named.json'), 'w'), ensure_ascii=False)
print('named', len(out), round(time.time() - T0), 's')
for s in sorted([o for o in out if o['v'] == 'x' and o['kind'] == 'new'], key=lambda o: -(o['in'] + o['out']))[:25]:
    m = s['main'][0] if s['main'] else {}
    print(round(s['in']), round(s['out']), m.get('en') or m.get('name'), m.get('side', ''), '|',
          ', '.join(f"{(q['en'] or q['name'])}({q['side']})" for q in s['places'][:8]))
