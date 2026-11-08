"""Version 345 PREVIEW (Nawaz sent three maps of the Ottoman north c.1672-1683 -> "Preview"). V5 (grm) takes the Podolia Eyalet as
drawn (dark red) on the Wikimedia map "The Ottoman Empire in 1683" (Ottoman_empire.svg derivative), the only one of the three with a
coordinate grid: traced from the image and placed on its 5-degree graticule (lon 25-30, lat 45-50 cell; error ~2-5 km)
(tools/data/v345_podolia_wiki1683.geojson). That map's eyalet reaches the Strypa in the west, ~49.9N in the north and, after the
Treaty of Zurawno (1676), south-east past Bratslav along the Dniester to ~29.7E. The hand-read outline of the schematic map
(tools/data/v345_podolia_wiki1683.geojson) is kept for reference but not used."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
POD = shape(json.load(open(os.path.join(P, 'tools/data/v345_podolia_wiki1683.geojson')))['features'][0]['geometry']).intersection(G['804'][1])
V5 = M('grm'); print('Podolia (as on the map) adds', round(A(POD.difference(V5))), 'km2')
X = unary_union([V5, POD.buffer(0.002)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Kamianets-Podilskyi': (26.58, 48.68), 'Medzhybizh': (27.41, 49.44), 'Khmilnyk': (27.96, 49.56), 'Proskuriv (Khmelnytskyi)': (26.99, 49.42),
              'Horodok': (26.57, 49.17), 'Satanov': (26.26, 49.25), 'Chortkiv': (25.80, 49.02), 'Yazlovets': (25.47, 48.96), 'Buchach': (25.39, 49.06),
              'Starokostiantyniv': (27.21, 49.76), 'Kalynivka (NE corner)': (28.52, 49.45), 'Bratslav': (28.94, 48.82), 'Yampil': (28.28, 48.24), 'Rybnytsia': (29.01, 47.77), 'Ternopil': (25.59, 49.55), 'Uman (vassal, stays out)': (30.22, 48.75)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
