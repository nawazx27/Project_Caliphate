"""Version 341 PREVIEW, run on top of the Version 340 natural-borders preview (Nawaz sent a list of lands Rome invaded or meant to
annex but gave up, and a map of Germania Magna, "Preview with these"). V5 (grm) takes Germania Magna as that map shades it:
all of Germany, Denmark (Jutland and the islands), and Poland west of the Vistula and the San (Gdansk, Poznan, Lodz, Krakow,
Rzeszow; Warsaw's west bank), so the border runs Vistula - San - Carpathian crest. Czechia (Marcomannia) is already in from
Version 340; Caledonia, Mesopotamia and Assyria, Arabia Felix (Yemen, Asir, Jizan, Najran), the Iazyges' plain (Sarmatia) and
Moldova are already in V5. Base map countries (276, 208, 616); Vistula and San from Natural Earth 10m (tools/data/v341_vistula_san.geojson)."""
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
R = unary_union([shape(f['geometry']) for f in json.load(open(os.path.join(P, 'tools/data/v341_vistula_san.geojson')))['features']])
PL = G['616'][1]
band = R.buffer(0.01)
pieces = PL.difference(band)
WEST = unary_union([q for q in getattr(pieces, 'geoms', [pieces]) if Point(14.5, 52.0).distance(q) < 1e-9 or q.representative_point().x < 19.0 and A(q) > 100])
print('Poland pieces', [(round(A(q)), round(q.representative_point().x, 1)) for q in getattr(pieces, 'geoms', [pieces]) if A(q) > 100])
WEST = unary_union([WEST, PL.intersection(band).intersection(WEST.buffer(0.02))])
V5 = M('grm')
DE, DK = G['276'][1], G['208'][1]
for n, x in [('Germany', DE), ('Denmark', DK), ('Poland west of the Vistula and San', WEST)]: print(n, 'adds', round(A(x.difference(V5))), 'km2')
X = unary_union([V5, DE.buffer(0.003), DK.buffer(0.003), WEST.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, gg) in G.items():
    if gg.area and gg.intersects(Y):
        pct = round(100 * gg.intersection(Y).area / gg.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(gg)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Berlin': (13.4, 52.52), 'Copenhagen': (12.57, 55.68), 'Skagen': (10.58, 57.72), 'Szczecin': (14.55, 53.43), 'Poznan': (16.93, 52.41),
              'Gdansk': (18.65, 54.35), 'Lodz': (19.46, 51.76), 'Krakow': (19.94, 50.06), 'Rzeszow': (22.0, 50.04), 'Warsaw west bank': (20.98, 52.23),
              'Lublin (stays out)': (22.57, 51.25), 'Bialystok (stays out)': (23.16, 53.13), 'Malmo (stays out)': (13.0, 55.6)}.items():
    print('  ', n_, Y.contains(Point(p)))
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
