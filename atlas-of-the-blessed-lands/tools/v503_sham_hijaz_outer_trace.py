"""Version 503 preview (Nawaz, a screenshot of the page's own Sham/Hijaz diagram: "Trace this map with broader outlines exactly").
The diagram is drawn from SHAM_OUTER and HIJAZ_OUTER in src/old_data.js (the dashed 'Sham, disputed edge' and 'Hijaz, uncertain' lines), so the
trace uses those exact points: the land inside either ring, with every island inside the rings. -> tools/data/v503_sham_hijaz_outer.geojson."""
import json, os, re, subprocess
from shapely.geometry import shape, Polygon, mapping, box
from shapely.ops import unary_union
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
src = open(os.path.join(HERE, 'src/old_data.js')).read()
def ring(name):
    body = re.search(r'const ' + name + r' = \[(.*?)\n\];', src, re.S).group(1)
    pts = []
    for seg in re.findall(r'p:\[(.*?)\]\}', body):
        for x, y in re.findall(r'\[([-\d.]+),([-\d.]+)\]', seg):
            q = (float(x), float(y))
            if not pts or pts[-1] != q: pts.append(q)
    return Polygon(pts).buffer(0)
R = unary_union([ring('SHAM_OUTER'), ring('HIJAZ_OUTER')])
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
B = box(*R.bounds)
parts = {}
for f in geo['features']:
    if not f.get('geometry'): continue
    g = shape(f['geometry']).buffer(0)
    if not g.intersects(B): continue
    i = g.intersection(R)
    if not i.is_empty and A(i) > 0.5: parts[f['properties']['n']] = (i, A(i), 100 * A(i) / A(g))
T = unary_union([v[0] for v in parts.values()]).buffer(0)
print('traced land', round(A(T)), 'km2')
for n, (g, a, pc) in sorted(parts.items(), key=lambda x: -x[1][1]): print(f'  {n:25s}{a:10.0f} km2  {pc:5.1f}% of the country')
json.dump({'type': 'Feature', 'properties': {'name': 'Sham and Hijaz, broader outlines of the page diagram'}, 'geometry': mapping(T)},
          open(os.path.join(HERE, 'tools/data/v503_sham_hijaz_outer.geojson'), 'w'))
