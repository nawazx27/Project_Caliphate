"""Version 116 (2026-10-13, Nawaz, with a screenshot of V2 in Central Asia, Khurasan and the Punjab: "make sure that there borders are
politically strong"; asked, he chose defensible frontiers, for that area, in V2, V2-B and V2N; then "Stronger for all three", the
rivers (Amu Darya, Aral, Syr Darya) and "Push out to the Chu river"). Nawaz's specification; my construction; not from the sources.
Writes tools/data/central_asia_frontiers.geojson, three pieces added to V2, V2-B and V2N (land only added):
  'v2n'    V2N's frontiers of Versions 92-95 (the Punjab to the Beas and Sutlej, Fergana to its crests, the Turkistan region to the
           Karatau) that V2 and V2-B lacked: V2N minus V2.
  'rivers' the land between the Amu Darya, the old shore of the Aral Sea and the Syr Darya beyond V2N's line (the Kyzylkum, Nukus,
           the south bank of the Syr in the Qyzylorda region): rivers.geojson (Natural Earth), tools/data/ne_10m_lakes_historic_aral.geojson;
           river ends near the Aral are joined to its old shore.
  'chu'    the land of Kazakhstan between V2N's line, the Chu (tools/data/chu_river.geojson) and Kyrgyzstan (the Zhambyl region south
           of the Chu, with Taraz and the Moyynkum sands); the Chu's end in the sands is joined to V2N's line.
Run: python3 tools/ca_frontiers.py, then node tools/v2_ca_frontiers.js"""
import json, os, subprocess, pyproj
from shapely.geometry import shape, MultiPolygon, Polygon, box, Point, mapping, LineString
from shapely.ops import unary_union, nearest_points
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
G = pyproj.Geod(ellps='WGS84'); A = lambda g: round(abs(G.geometry_area_perimeter(g)[0]) / 1e6)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
cty = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
C = json.load(open(os.path.join(P, 'src/caliph.json')))
mp = lambda k: MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
x, xn = mp('x'), mp('xn')
polys = lambda g: unary_union([q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and q.area > 1e-4])
def face(B, barriers, seed):
    free = B.difference(unary_union(barriers))
    return [q for q in getattr(free, 'geoms', [free]) if q.contains(Point(*seed))][0]
# 1. V2N's frontiers
v2n = polys(xn.difference(x).intersection(box(44, 20, 82, 50)))
# 2. between the Amu Darya, the Aral and the Syr Darya
B = box(57, 40, 71, 47.5)
land = unary_union([g for g in cty.values() if g.intersects(B)]).intersection(B)
riv = unary_union([shape(f['geometry']) for f in json.load(open(os.path.join(P, 'rivers.geojson')))['features']
                   if (f['properties'].get('name') or '').replace('  ', ' ') in ('Syr Darya', 'Amu Darya')]).intersection(B)
aral = unary_union([shape(f['geometry']) for f in json.load(open(os.path.join(H, 'data', 'ne_10m_lakes_historic_aral.geojson')))['features']]).buffer(0)
links = [LineString([c, nearest_points(Point(c), aral)[1].coords[0]]) for ln in getattr(riv, 'geoms', [riv]) for c in (ln.coords[0], ln.coords[-1]) if 0 < aral.distance(Point(c)) < 0.6]
f = face(B, [riv.buffer(0.01)] + [l.buffer(0.01) for l in links] + [aral.buffer(0.01), xn.buffer(0.002)], (63.5, 43.8))
rivers = polys(f.buffer(0.012).intersection(land).difference(xn).difference(aral))
# 3. between V2N's line, the Chu and Kyrgyzstan
B = box(66, 41.5, 77, 47.5)
chu = shape(json.load(open(os.path.join(H, 'data', 'chu_river.geojson')))['features'][0]['geometry'])
end = min([c for l in getattr(chu, 'geoms', [chu]) if l.geom_type == 'LineString' for c in (l.coords[0], l.coords[-1])], key=lambda c: c[0])
link = LineString([end, nearest_points(Point(end), xn)[1].coords[0]])
f = face(B, [chu.buffer(0.02), link.buffer(0.02), xn.buffer(0.002), cty['417'].buffer(0.002)], (72.0, 44.2))
chur = polys(f.buffer(0.022).intersection(cty['398'].intersection(B)).difference(xn))
feats = [{'type': 'Feature', 'properties': {'role': r, 'km2': A(g)}, 'geometry': mapping(g)} for r, g in [('v2n', v2n), ('rivers', rivers), ('chu', chur)]]
json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', 'central_asia_frontiers.geojson'), 'w'))
print({ft['properties']['role']: ft['properties']['km2'] for ft in feats})
