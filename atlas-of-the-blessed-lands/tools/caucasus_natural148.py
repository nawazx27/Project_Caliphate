"""Version 148 (2026-10-16, Nawaz: "Make newly drawn border look nice. And implement natural border rule since changes we started
making since lake Albert"; asked how, he chose "Closest natural features"). The Caucasus line of Versions 146-147 (traced from his
orange sketch) runs between two rivers: the Kuban in the west and the Kuma in the east. The new line follows the main channel of the
Kuban from its mouth at Temryuk upstream to where it comes nearest the Kuma's upper course (near Cherkessk), a short straight link
there, then the Kuma down to its end in the Caspian lowland and on to the shore. Rivers: OpenStreetMap via Overture Maps 2026-09-23.1
(tools/data/river_kuban.geojson, river_kuma.geojson). All of Russia south of it is the Caucasus land (Crimea out); the main channel is
found as the shortest path through the river's pieces. Writes tools/data/caucasus_natural148.geojson (region) and
caucasus_natural148_line.json. My method; Nawaz's choice."""
import json, os, heapq, subprocess
from shapely.geometry import shape, LineString, Polygon, Point, MultiPolygon, mapping, box
from shapely.ops import nearest_points, unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
def segs(name):
    g = shape(json.load(open(os.path.join(D, name)))['features'][0]['geometry'])
    return [list(l.coords) for l in getattr(g, 'geoms', [g])]
def path(lines, a, b):   # shortest path along the river pieces between the vertices nearest a and b
    adj = {}; R = lambda p: (round(p[0], 5), round(p[1], 5))
    for l in lines:
        for p, q in zip(l, l[1:]):
            p, q = R(p), R(q); w = Point(p).distance(Point(q))
            adj.setdefault(p, []).append((q, w)); adj.setdefault(q, []).append((p, w))
    # bridge breaks between the map's pieces of the river: each piece's ends join the nearest vertex of any other piece (up to ~8 km)
    from shapely.strtree import STRtree
    pts = list(adj); tree = STRtree([Point(p) for p in pts])
    comp = {}
    for i, l in enumerate(lines):
        for p in l: comp[R(p)] = i
    for i, l in enumerate(lines):
        for e in (R(l[0]), R(l[-1])):
            cand = [pts[j] for j in tree.query(Point(e).buffer(0.08)) if comp.get(pts[j]) != i]
            if cand:
                q = min(cand, key=lambda q: Point(e).distance(Point(q))); w = Point(e).distance(Point(q))
                adj.setdefault(e, []).append((q, w)); adj.setdefault(q, []).append((e, w))
    nodes = list(adj); near = lambda t: min(nodes, key=lambda n: (n[0]-t[0])**2 + (n[1]-t[1])**2)
    s, e = near(a), near(b); dist = {s: 0}; prev = {}; h = [(0, s)]
    while h:
        d, u = heapq.heappop(h)
        if u == e: break
        if d > dist[u]: continue
        for v, w in adj[u]:
            if d + w < dist.get(v, 1e9): dist[v] = d + w; prev[v] = u; heapq.heappush(h, (d + w, v))
    out = [e]
    while out[-1] != s: out.append(prev[out[-1]])
    return out[::-1]
kuban, kuma = segs('river_kuban.geojson'), segs('river_kuma.geojson')
KU, KM = unary_union([LineString(l) for l in kuban]), unary_union([LineString(l) for l in kuma])
# the link: nearest points of the Kuban (upstream of Nevinnomyssk) and the upper Kuma
pa, pb = nearest_points(KU.intersection(box(41.5, 43.6, 42.6, 44.7)), KM.intersection(box(41.9, 43.6, 43.2, 44.4)))
kuban_mouth = (37.36, 45.33)   # Temryuk
k1 = path(kuban, kuban_mouth, (pa.x, pa.y))
kuma_end = max((c for l in kuma for c in l), key=lambda c: c[0])
k2 = path(kuma, (pb.x, pb.y), kuma_end)
line = k1 + k2
print('link', (round(pa.x, 3), round(pa.y, 3)), '->', (round(pb.x, 3), round(pb.y, 3)), 'Kuma ends', [round(v, 3) for v in kuma_end])
L = LineString(line)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'note': 'Kuban (mouth to near Cherkessk) + link + Kuma'}, 'geometry': mapping(L)}]}, open(os.path.join(D, 'caucasus_natural148_line.json'), 'w'))
R = Polygon([(36.3, line[0][1])] + line + [(48.6, line[-1][1]), (48.6, 41.0), (36.3, 41.0)]).buffer(0)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = [shape(f['geometry']).buffer(0) for f in geo['features'] if str(f['id']) == '643'][0]
cr = shape(json.load(open(os.path.join(D, 'crimea_out.geojson')))['features'][0]['geometry'])
reg = R.intersection(RU).difference(cr)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 148 Caucasus (natural)'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'caucasus_natural148.geojson'), 'w'))
old = shape(json.load(open(os.path.join(D, 'caucasus_expand147.geojson')))['features'][0]['geometry'])
print('Russia south of the Kuban-Kuma line', round(A(reg)), 'km2; vs Version 147 Caucasus: gained', round(A(reg.difference(old))), 'lost', round(A(old.difference(reg))))
