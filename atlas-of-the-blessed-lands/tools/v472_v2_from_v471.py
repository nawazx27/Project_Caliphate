"""Version 472 (Nawaz, on the Version 471 preview (V1's African piece enlarged in its own shape until the whole Nile is inside, from the Kagera sources
to the Delta): "Fill the tip near the Horn of Africa and replace the current V2 with this."). The Version 471 outline, with all of Somalia and Somaliland
(the north-eastern tip of the Horn, Puntland to Cape Guardafui, was left outside by the enlargement), becomes the NEW V2 (CALIPH.arb). V1 is not changed.
The old V2 (V1 + the Nile basin, East Africa, all of Libya) is replaced: western Libya (Tripolitania, the Fezzan), most of Tanzania, the Kenyan coast
round Mombasa and southern Burundi are no longer in V2; the Central African Republic's east, more of DR Congo and eastern Chad come in.
Usage: DIR=<project> python3 tools/v472_v2_from_v471.py <caliph.json holding the Version 471 V1>. Run v386_areas_ellipsoid.py after."""
import json, os, sys, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
N = MP(json.load(open(sys.argv[1]))['shj']['polys'])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V1 = MP(C['shj']['polys'])
X = unary_union([N, V1, G['Somalia'].buffer(0.003), G['Somaliland'].buffer(0.003)]).buffer(0)
X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 5000]).buffer(0)
X = shapely.set_precision(X, 0.001); o = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
    o.append([[[round(a, 3), round(b, 3)] for a, b in rr.coords] for rr in [q.exterior, *q.interiors]])
km = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
Y = MP(o); print('V2 (arb)', C['arb']['km2'], '->', km, '| V1 inside V2:', round(A(V1.difference(Y.buffer(0.002))), 1), 'km2 outside')
print('shares:', {n: round(100 * A(G[n].intersection(Y)) / A(G[n]), 1) for n in ['Somalia', 'Somaliland', 'Ethiopia', 'Kenya', 'Uganda', 'Rwanda', 'Burundi', 'Tanzania', 'DR Congo', 'Central African Rep.', 'Chad', 'Libya']})
C['arb'] = {'polys': o, 'km2': km, 'states': C['arb'].get('states', [])}
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
# ---- page text: V2 is described as it is now
def sub(path, a, b):
    s = open(path).read(); n = s.count(a); assert n >= 1, (path, a[:60]); open(path, 'w').write(s.replace(a, b)); return n
T_OLD = 'V2: V1 with the whole Nile and its basin to Lake Victoria and the Kagera sources, the Horn of Africa and East Africa (Ethiopia, Somalia, Somaliland, Uganda, Rwanda, Burundi, Kenya and Tanzania, whole) and all of Libya (the author’s specification)'
T_NEW = 'V2: V1 with its African piece enlarged in its own shape until the whole Nile is inside, end to end, from the Kagera sources and Lake Victoria to the Delta; with Ethiopia, Somalia, Somaliland, Uganda, Rwanda, most of Kenya, Burundi and DR Congo’s north-east (the author’s specification)'
print('titles', sub(os.path.join(P, 'src/body.html'), T_OLD, T_NEW))
B_OLD = '<b>V2</b> is V1 with the whole Nile and its basin to Lake Victoria and the Kagera sources, and with all of Libya, Ethiopia, Somalia, Somaliland, Kenya, Uganda, Rwanda, Burundi and Tanzania (about 15.0 million km²).'
B_NEW = ('<b>V2</b> is V1 with its African piece enlarged in its own shape until the whole Nile is inside, end to end, from the Kagera sources and Lake Victoria to '
         'the Delta, so with Ethiopia, Somalia and Somaliland, Uganda, Rwanda, most of Kenya and Burundi, north-western Tanzania, the east of the Central African Republic '
         'and the north-east of DR Congo (about ' + f'{km / 1e6:.1f}' + ' million km²).')
sub(os.path.join(P, 'src/body.html'), B_OLD, B_NEW)
ep = os.path.join(P, 'src/eng_e.js'); e = open(ep).read(); i = e.index('CX_LEAD.arb = `'); j = e.index('`;', i) + 2
e = e[:i] + ("CX_LEAD.arb = `<p>${CX_SPEC} <b>V2</b> is V1 with its African piece, the land south of Egypt, <b>enlarged as one piece in its own shape</b> until "
             "<b>the whole Nile</b> lies inside, end to end: from its farthest sources on the Kagera in Burundi and Rwanda, through Lake Victoria, the Victoria Nile, "
             "Lake Kyoga, Murchison Falls and Lake Albert, the Albert and Mountain Nile, the Sudd and the White Nile, and the Blue Nile from Lake Tana, to Khartoum, "
             "the cataracts, Aswan and the Delta. The enlarged piece keeps the straight Sudan border on 24 E and its curves elsewhere, so it also holds Ethiopia, "
             "Somalia and Somaliland (the whole Horn), Uganda, Rwanda, most of Kenya with Nairobi and Burundi, north-western Tanzania with Mwanza, the east of the "
             "Central African Republic, the north-east of DR Congo with Kisangani, and eastern Chad. The outlines are the author’s specification, not a ruling. "
             "About ${(CALIPH.arb.km2/1e6).toFixed(1)} million km².</p>`;") + e[j:]
a = "const ARB_B = [[8.5,-12.5],[64.5,43.0]];   /* Version 455: V2 (arb), Libya to Iran, the Black Sea to southern Tanzania */"
assert e.count(a) == 1; e = e.replace(a, "const ARB_B = [[14.0,-8.0],[64.5,43.0]];   /* Version 472: V2 (arb), eastern Chad to Iran, the Black Sea to the Kagera sources */")
open(ep, 'w').write(e); print('text done')
