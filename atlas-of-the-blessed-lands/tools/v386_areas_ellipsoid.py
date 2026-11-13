"""Version 386 (Nawaz: "Let's do everything in fixing the accuracy..."). The km2 of the seven outlines on the page are re-measured on the WGS84
ellipsoid (pyproj Geod, exact geodesic areas) instead of d3's sphere of radius 6371.0088 km, which reads about 0.15% high at these latitudes.
RERUN THIS AFTER ANY OUTLINE TOOL: the tools' own km2of() still writes the sphere figure for the outline they change."""
import json, os
from shapely.geometry import Polygon
from pyproj import Geod
P = os.environ.get('DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
G = Geod(ellps='WGS84'); A = lambda ring: abs(G.geometry_area_perimeter(Polygon(ring))[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ['shj', 'me2', 'me9', 'sas', 'grm', 'tib', 'sup']:
    new = round(sum(A(p[0]) - sum(A(h) for h in p[1:]) for p in C[k]['polys']))
    print(k, C[k]['km2'], '->', new, '(%+.2f%%)' % (100 * (new - C[k]['km2']) / C[k]['km2'])); C[k]['km2'] = new
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
