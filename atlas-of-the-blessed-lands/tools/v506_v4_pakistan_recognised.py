"""Version 506 preview (Nawaz: "Preview Pakistan in V4 with official borders", then he chose "Recognised borders only"). V4 (me9) loses the
Indian-administered part of Jammu and Kashmir that the Version 264 Pakistan-official-map addition put in (the Kashmir Valley, Jammu, Ladakh) and
the Siachen Glacier, i.e. all land of India and 'Siachen Glacier' on the base map inside V4; Pakistan as the base map draws it (with Azad Kashmir
and Gilgit-Baltistan) stays whole. Any China-administered land in Kashmir inside V4 goes too. DIR env = project dir. Run v386 after."""
import json, os, subprocess
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
KASH = box(72.5, 32.0, 80.5, 37.2)
CUT = unary_union([G['India'], G['Siachen Glacier'], G['China'].intersection(KASH)])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
polys = C['me9']['polys']; W = box(60, 20, 82, 38)
near = [i for i, r in enumerate(polys) if box(*Polygon(r[0]).bounds).intersects(W)]
V = unary_union([Polygon(polys[i][0], polys[i][1:]).buffer(0) for i in near])
cut = V.intersection(CUT)
print('removed', round(A(cut)), 'km2:', ', '.join(f"{n} {round(A(V.intersection(G[n] if n != 'China' else G[n].intersection(KASH))))}" for n in ['India', 'Siachen Glacier', 'China']))
N = V.difference(CUT).buffer(0)
N = unary_union([q for q in getattr(N, 'geoms', [N]) if A(q) > 0.5])   # no hairline leftovers
import shapely
N = shapely.set_precision(N, 0.001)   # snapped to the 0.001-degree grid the file is stored on, so the stored outline stays valid
new = []
for q in getattr(N, 'geoms', [N]):
    q = orient(q, 1.0)
    new.append([[[round(a, 3), round(b, 3)] for a, b in q.exterior.coords]] + [[[round(a, 3), round(b, 3)] for a, b in h.coords] for h in q.interiors])
C['me9']['polys'] = [r for i, r in enumerate(polys) if i not in near] + new
print('Pakistan inside V4 after:', round(100 * A(G['Pakistan'].intersection(N)) / A(G['Pakistan']), 2), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
