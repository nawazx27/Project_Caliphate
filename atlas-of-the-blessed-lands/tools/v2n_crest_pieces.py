"""Version 95: compare V2N (src/caliph.json, CALIPH.xn) with the crest lines traced on real elevation data and write
the land on the inner side of the crests that V2N does not yet hold to tools/data/v2n_crest_pieces.geojson
(then node tools/v2n_crests.js adds it). Inner side = the Fergana valley inside its ring of ranges
(tools/data/fergana_crest_basin.geojson, tools/crest_basin.py) and the Syr Darya side of the Karatau
(tools/data/karatau_syr_side.geojson, tools/karatau_divide.py) from the range's north-west tip, across to the
Syr Darya (river line from rivers.geojson, Natural Earth), to where V2N already reaches. Pieces under 1 km² are
the grid's own step (cells about 0.4 km across) and are left to the province lines. My method.
Usage: python3 tools/v2n_crest_pieces.py"""
import json
from shapely.geometry import shape, Point, LineString, MultiPolygon, Polygon, box, mapping
from shapely.ops import split, unary_union, nearest_points
from shapely.validation import make_valid
from pyproj import Geod
G = Geod(ellps='WGS84'); km2 = lambda g: abs(G.geometry_area_perimeter(g)[0]) / 1e6 if not g.is_empty else 0
C = json.load(open('src/caliph.json'))
xn = make_valid(MultiPolygon([Polygon(p[0], p[1:]) for p in C['xn']['polys']])).intersection(box(60, 35, 80, 47)).buffer(0)
parts = lambda g: [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon']
out = []
# Fergana: inside the ring of crests
basin = shape(json.load(open('tools/data/fergana_crest_basin.geojson'))['geometry']).buffer(0)
for q in parts(basin.difference(xn)):
    if km2(q) >= 1: out.append(('Fergana valley, inside its crests', q))
# Karatau: the Syr Darya side of the divide
syr = shape(json.load(open('tools/data/karatau_syr_side.geojson'))['geometry']).buffer(0)
ridge = sorted((lo, la) for lo, la, e in json.load(open('tools/data/karatau_divide.json')) if e > 400 and 66.9 <= lo <= 71.0)
T = Point(ridge[0])                                     # north-west tip of the range (first ridge cell above 400 m)
R = [f for f in json.load(open('rivers.geojson'))['features'] if f['properties']['name'] == 'Syr  Darya' and f['properties']['featurecla'] == 'River'][0]
riv = LineString(max(R['geometry']['coordinates'], key=len)); R1 = nearest_points(T, riv)[1]
ne = [p for p in split(box(66.0, 42.5, 69.5, 45.2), riv).geoms if p.contains(Point(68.5, 44.5))][0]
cut = LineString([(T.x + (T.x - R1.x) * 3, T.y + (T.y - R1.y) * 3), (R1.x - (T.x - R1.x) * 0.3, R1.y - (T.y - R1.y) * 0.3)])
nw = [p for p in split(ne, cut).geoms if p.contains(Point(68.3, 43.6))][0]
for q in parts(syr.intersection(nw).difference(xn)):
    if km2(q) >= 1: out.append(('Karatau, Syr Darya side, north-west end', q))
for q in parts(syr.intersection(box(68.17, 41.6, 71.2, 45.4)).difference(xn)):   # east of 71.2 the box edge decides, not the range
    if km2(q) >= 1: out.append(('Karatau, Syr Darya side, south-east end', q))
fc = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'where': w, 'km2': round(km2(q), 1)}, 'geometry': mapping(q.simplify(0.001))} for w, q in out]}
json.dump(fc, open('tools/data/v2n_crest_pieces.geojson', 'w'))
tot = {}
for w, q in out: tot[w] = tot.get(w, 0) + km2(q)
print({k: round(v) for k, v in tot.items()}, 'tip', T, 'river', R1)
