"""Version 283 (Nawaz, with Britannica's "Topography of South Asia" map (reference/v283_south_asia_topography_britannica.jpg):
"Build another version which is upon v4, and add the entire Indian subcontinent ... not stopping near Himalayas but going beyond
Himalayas as shown in the image ... trace the entire image of Indian subcontinent end to end"; then: all of the princely state of Jammu
and Kashmir; all of India, Pakistan, Afghanistan, Bangladesh, Nepal, Bhutan, Myanmar, Sri Lanka, Andaman and Nicobar, Pakistan- and
China-administered Kashmir, the Maldives and the Chagos Archipelago; then "Add all islands and push/apply").
The map's coloured landmass was traced end to end (land/sea mask), georeferenced by fitting an equal-area projection to the real borders
(IoU 0.963) and unprojected; real coastlines were used where it meets the sea. Saved in tools/data/v5_subcontinent283.geojson:
 'sas'  (the NEW V5 = V4 + this): the traced subcontinent with its strip beyond the Himalayas (~224,000 km2 of Tibet incl. part of
        Aksai Chin), all of India, Nepal, Bhutan, Bangladesh, Sri Lanka, the Maldives, Myanmar, the Chagos Archipelago, all of Aksai Chin
        and the Shaksgam valley (Natural Earth), one Tibet pocket; and the islands: Cabo Verde, Lakshadweep, St Martin's Island, Arwad,
        the Caspian's Chechen and Tyuleniy islands, Thailand's Andaman-Sea and Gulf islands, Weh and Breueh off Aceh, the Tuscan islands
        and Ischia, Porquerolles, Nosy Be, Likoma and Chizumulu.
 'v2'   (the Super Caliphate, now V6): the same islands, so the new V5 lies inside V6.
 'extraLand': Lakshadweep (Overture IN-LD), St Martin's Island and Arwad (Overture), which the base map does not draw.
CALIPH.sas held the old V5 (South Asia + northern wings); that shape is saved in tools/data/v5_shape_v276.json. Run after
tools/v4_derbent269.py and tools/v5_tibet_plateau277.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
D = {f['properties']['key']: shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/v5_subcontinent283.geojson')))['features']}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
def rings(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
NAMES = {'356': 'India, with the Andaman, Nicobar and Lakshadweep islands', '524': 'Nepal', '064': 'Bhutan', '050': 'Bangladesh', '144': 'Sri Lanka',
         '462': 'Maldives', '104': 'Myanmar', '086': 'the Chagos Archipelago (British Indian Ocean Territory, claimed by Mauritius)', '132': 'Cabo Verde',
         '156': 'China: Aksai Chin and the Shaksgam valley (all of the princely state of Jammu and Kashmir) and the strip of Tibet beyond the Himalayas that Britannica’s South Asia map draws',
         '764': 'Thailand: its Andaman Sea and Gulf islands (Phuket, Ko Samui, Ko Chang and others)', '360': 'Indonesia: Weh and Breueh off Aceh',
         '380': 'Italy: the Tuscan islands (Elba, Giglio, Pianosa, Capraia) and Ischia', 'FRA': 'France: Porquerolles', '450': 'Madagascar: Nosy Be',
         '454': 'Malawi: Likoma and Chizumulu in Lake Malawi', '643': 'Russia: Chechen and Tyuleniy islands in the Caspian'}
V4, V6 = M('me9'), M('v2')
X5 = shapely.union_all([V4, D['sas'].buffer(0.001)], grid_size=0.001); o5 = rings(X5); k5 = km2(o5)
Y5 = MultiPolygon([Polygon(r[0], r[1:]) for r in o5]).buffer(0)
rows = []
for k, n in NAMES.items():
    a = A(G[k].intersection(Y5.difference(V4)))
    if a > 1 or k in ('132',): rows.append({'id': k if k not in ('156', '764', '360', '380', 'FRA', '450', '454', '643') else k + '_S', 'n': n, 'km2': round(a), 'pct': None if k in ('764', '360', '380', 'FRA', '450', '454', '643') else round(100 * A(G[k].intersection(Y5)) / A(G[k]), 1)})
rows.append({'id': 'XL_S', 'n': 'Islands the base map does not draw: Lakshadweep, St Martin’s Island (Bangladesh), Arwad (Syria)', 'km2': round(A(D['extraLand'])), 'pct': None})
old = C.get('sas', {})
C['sas'] = {'polys': o5, 'km2': k5, 'states': [dict(r) for r in C['me9']['states']] + rows}
print('new V5 (sas)', k5, [(r['id'], r['km2'], r['pct']) for r in rows])
X6 = shapely.union_all([V6, D['v2'].buffer(0.001)], grid_size=0.001); o6 = rings(X6); k6 = km2(o6)
r6 = [{'id': '132', 'n': 'Cabo Verde', 'km2': round(A(G['132'])), 'pct': 100},
      {'id': 'ISL_S', 'n': 'Islands near its lands: Lakshadweep, St Martin’s Island, Arwad, the Caspian’s Chechen and Tyuleniy islands, the Tuscan islands and Ischia, Porquerolles, Nosy Be, Likoma and Chizumulu', 'km2': round(A(D['v2'].difference(V6))), 'pct': None}]
print('V6 (v2)', C['v2']['km2'], '->', k6, 'V5 outside V6: %.1f km2' % A(Y5.difference(MultiPolygon([Polygon(r[0], r[1:]) for r in o6]).buffer(0))))
C['v2'].update(polys=o6, km2=k6, states=[r for r in C['v2']['states'] if r['id'] not in ('132', 'ISL_S')] + r6)
ex = C['extraLand']; E0 = MultiPolygon([Polygon(r[0], r[1:]) for r in ex['polys']]).buffer(0)
Ex = unary_union([E0, D['extraLand']]); ex['polys'] = rings(Ex); ex['km2'] = round(A(Ex), 2)
ex['n'] = 'Kastellorizo (Megisti), Ro, Strongyli and Psomi, traced (tools/kastellorizo.py); Lakshadweep, St Martin’s Island and Arwad (Overture, Version 283)'
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
