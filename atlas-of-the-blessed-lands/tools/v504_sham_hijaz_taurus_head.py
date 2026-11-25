"""Version 504 preview (Nawaz, with four maps of Greater/Natural Syria (the Empire of Greater Syria map, the SSNP 'natural borders' map, the Arabic
general map of Natural Syria, the Wikipedia Bilad al-Sham ajnad/thughur map): "The head... near turkey region must look like the one in these images").
The head of the v503 Sham/Hijaz trace (tools/data/v503_sham_hijaz_outer.geojson) is replaced, west of the Euphrates, by the Taurus head of the
Arabic Natural Syria map as traced in Version 400 (tools/data/v400_natural_syria.geojson): all of Cilicia (Mersin, Tarsus, Adana, al-Massisa,
'Ayn Zarba), Hatay, Mar'ash, 'Aintab, Kilis, Adiyaman to the Taurus crest, its east edge on the Euphrates itself (~38.2-38.4 N). East of the Euphrates (Urfa, Diyarbakir, Mardin and
the Jazira) is NOT added. -> tools/data/v504_sham_hijaz_taurus.geojson (land only)."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
ld = lambda f: (lambda d: shape(d['geometry'] if 'geometry' in d else d['features'][0]['geometry']).buffer(0))(json.load(open(os.path.join(HERE, f))))
T = ld('tools/data/v503_sham_hijaz_outer.geojson'); NS = ld('tools/data/v400_natural_syria.geojson')
# west of the Euphrates itself (src/four_rivers.json, Jarabulus up to Keban), north of 36.6 N (35.5 N west of 36.3 E, so all of the Cilician coast)
from shapely.geometry import LineString
from shapely.ops import linemerge
EU = [x for x in json.load(open(os.path.join(HERE, 'src/four_rivers.json')))['rivers'] if x['k'] == 'euphrates'][0]
L = linemerge(unary_union([LineString(q) for q in EU['parts'] if len(q) > 1]).intersection(box(37.5, 36.6, 39.8, 38.75)))
segs = sorted(getattr(L, 'geoms', [L]), key=lambda g: -g.length)
def seg(a, b):   # the merged piece that starts near a and ends near b
    for g in segs:
        c = list(g.coords)
        for cc in (c, c[::-1]):
            if abs(cc[0][0] - a[0]) + abs(cc[0][1] - a[1]) < 0.05 and abs(cc[-1][0] - b[0]) + abs(cc[-1][1] - b[1]) < 0.05: return cc
    raise SystemExit('river piece not found %s %s' % (a, b))
RIV = seg((38.47, 38.7), (39.14, 38.23)) + seg((39.13, 38.23), (38.9, 37.79)) + seg((38.87, 37.7), (38.03, 36.87)) + seg((38.03, 36.83), (38.23, 36.6))
ZONE = Polygon([(30, 35.5), (36.3, 35.5), (36.3, 36.6)] + RIV[::-1] + [(38.47, 40.5), (30, 40.5)]).buffer(0)   # down to the sea in Cilicia
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
LAND = unary_union([shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry') and shape(f['geometry']).intersects(ZONE)])
head_new = NS.intersection(ZONE).intersection(LAND)
head_old = T.intersection(ZONE)
print('old head', round(A(head_old)), 'km2 | new head', round(A(head_new)), 'km2 | old head outside the new', round(A(head_old.difference(head_new)), 1), 'km2')
N = unary_union([T, head_new]).buffer(0.003, join_style=2).buffer(-0.003, join_style=2)   # no seam where they meet
N = unary_union([q for q in getattr(N, 'geoms', [N]) if A(q) > 0.05])
print('new shape', round(A(N)), 'km2 (was', round(A(T)), ')')
for n in ['Türkiye', 'Syria', 'Cyprus']:
    g = [shape(f['geometry']).buffer(0) for f in geo['features'] if f['properties']['n'] == n][0]
    print(' ', n, round(A(N.intersection(g))), 'km2')
json.dump({'type': 'Feature', 'properties': {'name': 'Sham and Hijaz, broader outlines, Taurus head'}, 'geometry': mapping(N)},
          open(os.path.join(HERE, 'tools/data/v504_sham_hijaz_taurus.geojson'), 'w'))
