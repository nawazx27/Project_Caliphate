"""Version 143 (2026-10-14, Nawaz: "sure", to adding all of Lake Albert after checking the Nile end to end). The Nile, Blue Nile and
White Nile were already inside V2 and V2-B from source to sea; only Lake Albert's western (DR Congo) half was out. This writes
tools/data/lake_albert_drc.geojson = Lake Albert (lakes.geojson) minus V2. Run: python3 tools/lake_albert.py"""
import json, os
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
lake = [shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']
        if f['properties'].get('name') == 'Lake Albert'][0]
c = json.load(open(os.path.join(P, 'src/caliph.json')))
X = MultiPolygon([Polygon(r[0], r[1:]) for r in c['x']['polys']]).buffer(0)
piece = lake.difference(X)
piece = MultiPolygon([p for p in getattr(piece, 'geoms', [piece]) if p.area > 1e-5])
print('Lake Albert outside V2:', round(abs(Geod(ellps='WGS84').geometry_area_perimeter(piece)[0]) / 1e6), 'km2 in', len(piece.geoms), 'part(s)')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Lake Albert, DR Congo part'},
           'geometry': mapping(piece)}]}, open(os.path.join(P, 'tools/data/lake_albert_drc.geojson'), 'w'))
