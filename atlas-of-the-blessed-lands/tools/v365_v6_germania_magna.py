"""Version 365 (Nawaz, with a map of Germania Magna / Greater Germania (orange; the Rhine-Elbe land hatched "Temporarily Roman 7 BCE - 9 CE"):
"Add this to v6"). V6 (CALIPH.sup) takes every land the map shades:
  - Germany, Denmark (with Bornholm and Jutland beyond the map's top edge) and Czechia, each whole;
  - Poland west of the Vistula as far up as the San mouth, with the south-east edge on the map's straight diagonal from there to the Danube knee
    (Krakow, Katowice, Lodz, Poznan, Gdansk in; Warsaw's west bank in; Lublin, Rzeszow, Bialystok out);
  - southern Sweden (Scania, Blekinge, southern Smaland and the tip of Oland) as far as the map's top edge (about 56.5 N).
The shading was traced from the image (tools/data/v365_germania_magna_traced.geojson; georeferenced as Mercator on Bornholm and Cape Tarkhankut,
checked on Den Helder, the Danube knee and Perekop, error about 0.1-0.3 deg); on the Vistula the river itself (Natural Earth, tools/data/v341_vistula_san.geojson)
is the edge. The rest (the Low Countries, Austria and Slovakia north of the Danube) is already in V6. DIR env = project dir (default this repo)."""
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
TR = shape(json.load(open(os.path.join(HERE, 'tools/data/v365_germania_magna_traced.geojson')))['geometry'])
# only the Germania shading: the big piece and the small pieces in the western Baltic (other specks are look-alike colours elsewhere on the image)
TR = unary_union([g for g in getattr(TR, 'geoms', [TR]) if A(g) > 100000 or (8 < g.representative_point().x < 20 and 53.5 < g.representative_point().y < 57)])
V6 = MP(C['sup']['polys'])
DE, DK, CZ, PL, SE = (G[k][1] for k in ['276', '208', '203', '616', '752'])
riv = unary_union([shape(f['geometry']) for f in json.load(open(os.path.join(HERE, 'tools/data/v341_vistula_san.geojson')))['features']])
cut = PL.difference(riv.buffer(0.01))
west = unary_union([q for q in getattr(cut, 'geoms', [cut]) if q.representative_point().x < 19.0 and A(q) > 100 or Point(14.5, 52.0).distance(q) < 1e-9])
west = unary_union([west, PL.intersection(riv.buffer(0.01)).intersection(west.buffer(0.02))])
PLW = west.intersection(TR.buffer(0.15))      # the river where the map follows the Vistula; the traced diagonal in the south-east
SEs = SE.intersection(TR)
parts = {'Germany': DE, 'Denmark': DK, 'Czechia': CZ, 'Poland (west of the Vistula, to the diagonal)': PLW, 'southern Sweden (to the map edge)': SEs}
for n, g in parts.items(): print('  +', n, round(A(g.difference(V6))), 'km2')
other = unary_union([g for k, (n, g) in G.items() if k not in ('276', '208', '203', '616', '752')]).intersection(TR).difference(V6)
print('  shaded land of other countries not yet in V6:', round(A(other)), 'km2 (left out if only edge specks)')
X = unary_union([V6] + [g.buffer(0.003) for g in parts.values()]).buffer(0)
o = polys(X, 0.02); Y = MP(o)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Berlin': (13.4, 52.52), 'Hamburg': (9.99, 53.55), 'Copenhagen': (12.57, 55.68), 'Skagen': (10.59, 57.72), 'Bornholm': (14.92, 55.13), 'Prague': (14.42, 50.08),
              'Gdansk': (18.65, 54.35), 'Poznan': (16.93, 52.41), 'Wroclaw': (17.03, 51.11), 'Lodz': (19.46, 51.76), 'Krakow': (19.94, 50.06), 'Katowice': (19.02, 50.26),
              'Warsaw west bank': (20.98, 52.23), 'Warsaw east bank (out)': (21.06, 52.25), 'Tarnow': (20.99, 50.01), 'Sandomierz': (21.75, 50.68), 'Lublin (out)': (22.57, 51.25),
              'Rzeszow (out)': (22.0, 50.04), 'Malmo': (13.0, 55.6), 'Kalmar': (16.36, 56.66), 'Vaxjo': (14.8, 56.88), 'Stockholm (out)': (18.07, 59.33)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(MP(C['grm']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
