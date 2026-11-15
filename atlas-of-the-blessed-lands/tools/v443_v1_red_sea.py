"""Version 443 (Nawaz: "Does the current V1 have the entire Red Sea?" -> its shores and islands, yes; the water no -> "preview").
V1 (shj) takes the water of the whole Red Sea with the Gulfs of Suez and Aqaba, to the IHO southern limit at the Bab el-Mandeb (the line from Husn Murad,
Yemen, 12 40 N 43 30 E, to Ras Siyyan, Djibouti, 12 29 N 43 20 E). The water is the sea part of that basin as the base map's coastline draws it.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union, split
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
BX = box(31.5, 11.5, 44.5, 30.5)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
LAND = unary_union([shape(f['geometry']).buffer(0).intersection(BX) for f in geo['features'] if f.get('geometry')]).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
V = MP(C['shj']['polys'])
# south of the IHO line is the Gulf of Aden: cut it off with a polygon south-east of the line Husn Murad - Ras Siyyan
HM, RS = (43.5, 12.6667), (43.3333, 12.4833)
d = np.array(HM) - np.array(RS); d /= np.hypot(*d); far = 3
SOUTH = Polygon([tuple(np.array(RS) - far * d), tuple(np.array(HM) + far * d), (46, 10), (40, 9)]).buffer(0)
water = BX.difference(LAND).difference(SOUTH)
water = max(getattr(water, 'geoms', [water]), key=lambda g: g.contains(Point(38.5, 20.0)) * 1e9 + g.area)
print('Red Sea water', round(A(water)), 'km2 (published figure about 438,000)')
X = unary_union([V, water.buffer(0.004)]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
old = C['shj']['km2']; C['shj']['polys'] = o; C['shj']['km2'] = km
Y = MP(o)
print('shj', old, '->', km, '| Red Sea water inside', round(100 * water.intersection(Y).area / water.area, 2), '%')
for n_, p in {'Red Sea middle': (38.5, 20.0), 'Gulf of Suez': (32.9, 29.0), 'Gulf of Aqaba': (34.75, 28.8), 'Bab el-Mandeb (inside)': (43.35, 12.75), 'Gulf of Aden (out)': (44.5, 12.3)}.items():
    print('  ', n_, Y.contains(Point(p)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
