"""Version 366 (Nawaz, after Wikipedia's Germania article ("...the known parts of southern Scandinavia" / "including Scandinavia") sent the Scandza
article twice). Scandza, Jordanes's "great island" (Getica, AD 551), "usually identified with Scandinavia"; the tribes he names run from Scania and
Gotland to Rogaland, Hordaland, Romsdalen and Halogaland (the Adogit, midnight sun) and the Sami. V6 (sup) takes the Scandinavian peninsula:
all of Sweden (with Oland and Gotland) and mainland Norway with its coastal islands (Lofoten, Vesteralen). Svalbard and Jan Mayen (not part of
the peninsula, unknown to Jordanes), Finland and Aland are NOT added. Run after tools/v365_v6_germania_magna.py. DIR env = project dir."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
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
V6 = MP(C['sup']['polys'])
SE = G['752'][1]; NO = G['NOR'][1]
NOm = unary_union([q for q in getattr(NO, 'geoms', [NO]) if q.representative_point().y < 72 and q.representative_point().x > 3])   # mainland Norway with its coastal islands, NOT Svalbard or Jan Mayen
for n, g in [('Sweden (with Oland and Gotland)', SE), ('Norway (mainland and coastal islands)', NOm)]: print('  +', n, round(A(g.difference(V6))), 'km2')
X = unary_union([V6, SE.buffer(0.003), NOm.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Stockholm': (18.07, 59.33), 'Uppsala': (17.64, 59.86), 'Kiruna': (20.23, 67.86), 'Visby (Gotland)': (18.29, 57.64), 'Oslo': (10.75, 59.91), 'Bergen': (5.32, 60.39),
              'Stavanger (Rogaland)': (5.73, 58.97), 'Trondheim': (10.4, 63.43), 'Tromso': (18.96, 69.65), 'Andoya': (16.0, 69.1), 'North Cape': (25.78, 71.17),
              'Svalbard (out)': (15.6, 78.2), 'Helsinki (out)': (24.94, 60.17), 'Aland (out)': (19.94, 60.1)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
