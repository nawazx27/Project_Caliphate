"""Version 229 (Nawaz: "Apply it as V8 and make sure that the entire African continent is included"). A NEW V8 (key CALIPH.af, XV 'af'):
V3 (me2) with all of Central Asia (Kazakhstan with Baikonur, Uzbekistan, Kyrgyzstan, Tajikistan; Turkmenistan is in V3) and the whole
African continent: every African state whole, Ceuta and Melilla, and the islands on Africa's shelf or counted in the UN's African regions
(the Canaries, Madeira, Cabo Verde, Saint Helena with Ascension and Tristan da Cunha, São Tomé and Príncipe, Madagascar, the Comoros,
Mayotte, Réunion, Mauritius, the Seychelles, the Chagos, the French Southern Territories, and Italy's Pelagie Islands and Pantelleria).
Run: python3 tools/v8_africa229.py   (reads me2, writes af; the atlas keeps V3 as it is)"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
G['MYT'] = G['FRA'].intersection(box(44.9, -13.1, 45.4, -12.5)); G['REU'] = G['FRA'].intersection(box(55.1, -21.5, 55.9, -20.8))
G['CAN'] = G['724'].intersection(box(-18.5, 27.4, -13.2, 29.6)); G['MAD'] = G['620'].intersection(box(-17.5, 29.9, -15.8, 33.3))
G['CEU'] = G['724'].intersection(box(-5.45, 35.85, -5.25, 35.95)); G['MEL'] = G['724'].intersection(box(-3.0, 35.25, -2.9, 35.33))
G['PEL'] = G['380'].intersection(box(11.8, 35.3, 13.0, 36.95))   # Lampedusa, Lampione, Linosa (if drawn) and Pantelleria
ADD = {'398': 'Kazakhstan', 'KAB': 'Baikonur (Kazakhstan, leased to Russia)', '860': 'Uzbekistan', '417': 'Kyrgyzstan', '762': 'Tajikistan',
  '504': 'Morocco', '012': 'Algeria', '478': 'Mauritania', '732': 'Western Sahara', 'CEU': 'Ceuta (Spain)', 'MEL': 'Melilla (Spain)',
  '466': 'Mali', '562': 'Niger', '148': 'Chad', '686': 'Senegal', '270': 'Gambia', '624': 'Guinea-Bissau', '324': 'Guinea', '694': 'Sierra Leone',
  '430': 'Liberia', '384': 'Côte d’Ivoire', '854': 'Burkina Faso', '288': 'Ghana', '768': 'Togo', '204': 'Benin', '566': 'Nigeria', '120': 'Cameroon',
  '140': 'Central African Republic', '226': 'Equatorial Guinea', '266': 'Gabon', '178': 'Republic of the Congo', '180': 'DR Congo', '024': 'Angola',
  '894': 'Zambia', '454': 'Malawi', '508': 'Mozambique', '716': 'Zimbabwe', '072': 'Botswana', '516': 'Namibia', '710': 'South Africa', '426': 'Lesotho',
  '748': 'Eswatini', '450': 'Madagascar', '174': 'Comoros', '480': 'Mauritius', '690': 'Seychelles', '132': 'Cabo Verde', '678': 'São Tomé and Príncipe',
  '654': 'Saint Helena, Ascension and Tristan da Cunha (UK)', '086': 'British Indian Ocean Territory (Chagos; UK)', '260': 'French Southern Territories (France)',
  'MYT': 'Mayotte (France)', 'REU': 'Réunion (France)', 'CAN': 'Canary Islands (Spain)', 'MAD': 'Madeira (Portugal)',
  'PEL': 'Italy: the Pelagie Islands and Pantelleria (on Africa’s shelf off Tunisia)'}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me2']['polys']]).buffer(0)
X = shapely.union_all([V] + [G[i].buffer(0.003) for i in ADD], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
for i, n in ADD.items():
    p = A(G[i].intersection(Y)) / A(G[i]) * 100
    if p < 99.99: print('NOT WHOLE', n, round(p, 3))
rows = [r for r in C['me2']['states'] if r['id'] not in ('180_A',)] + [{'id': i, 'n': n, 'km2': round(A(G[i])), 'pct': 100} for i, n in ADD.items()]
C['af'] = {'polys': out, 'km2': km2, 'states': rows}
print('V8 (af)', km2, 'km2,', len(out), 'pieces,', len(rows), 'rows')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
