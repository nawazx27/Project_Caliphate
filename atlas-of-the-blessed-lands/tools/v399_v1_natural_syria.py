"""Version 399 PREVIEW (Nawaz, for the new V1: three maps of Natural Syria / the Fertile Crescent (an "Empire of Greater Syria" map, the Arabic general map of
Natural Syria, and the SSNP natural-borders map). A NEW V1 (key shj, replaced) built from whole modern units matching what the three maps share:
Syria, Lebanon, Israel, Palestine, Jordan, Iraq, Kuwait, the whole island of Cyprus, the Sinai (North and South Sinai), Turkey south of the Taurus
(Mersin, Adana, Osmaniye, Hatay, Kahramanmaras, Gaziantep, Kilis, Adiyaman, Sanliurfa, Diyarbakir, Mardin, Batman, Siirt, Sirnak, Hakkari), Iran west of
the Zagros (Khuzestan, Ilam) and the Saudi north (Al-Jawf, Northern Borders). MODE=natural_hejaz also joins the Hejaz (Version 398).
DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
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
import pyarrow.parquet as pq
MODE = os.environ.get('MODE', 'natural')
def rg(f, keep): return [shapely.from_wkb(r['geometry']).buffer(0) for r in pq.read_table(os.path.join(HERE, f)).to_pylist() if r['region'] in keep and r['class'] == 'land' and r['is_land'] is not False]
cid = lambda n: [k for k, (nm, g) in G.items() if nm == n][0]
SA = cid('Saudi Arabia'); TRK = cid('Türkiye')
CY = [cid(n) for n in ['Cyprus', 'N. Cyprus', 'Cyprus U.N. Buffer Zone', 'Akrotiri', 'Dhekelia']]
EGc = cid('Egypt'); IRc = cid('Iran')
parts = {}
for n in ['Syria', 'Lebanon', 'Israel', 'Palestine', 'Jordan', 'Iraq', 'Kuwait']: parts[n] = G[cid(n)][1]
parts['Cyprus (whole island)'] = unary_union([G[k][1] for k in CY])
parts['Sinai (North and South Sinai)'] = unary_union(rg('tools/data/v399_regions.parquet', {'EG-SIN', 'EG-JS'})).intersection(G[EGc][1].buffer(0.02))
parts['Turkey south of the Taurus (Mersin, Adana, Osmaniye, Hatay, Kahramanmaras, Gaziantep, Kilis, Adiyaman, Sanliurfa, Diyarbakir, Mardin, Batman, Siirt, Sirnak, Hakkari)'] = unary_union(
    rg('tools/data/v399_regions.parquet', {'TR-33', 'TR-01', 'TR-80', 'TR-46', 'TR-30'}) + rg('tools/data/v396_tr_southeast.parquet', {'TR-31', 'TR-27', 'TR-79', 'TR-02', 'TR-63', 'TR-21', 'TR-47', 'TR-72', 'TR-56', 'TR-73'})).intersection(G[TRK][1].buffer(0.02))
parts['Iran west of the Zagros (Khuzestan, Ilam)'] = unary_union(rg('tools/data/v399_regions.parquet', {'IR-06', 'IR-16'})).intersection(G[IRc][1].buffer(0.02))
parts['Saudi north (Al-Jawf, Northern Borders)'] = unary_union(rg('tools/data/v398_sa_regions.parquet', {'SA-12', 'SA-08'})).intersection(G[SA][1].buffer(0.02))
if MODE == 'natural_hejaz':
    parts['Hejaz (Tabuk, Medina, Mecca, Al-Bahah)'] = unary_union(rg('tools/data/v398_sa_regions.parquet', {'SA-07', 'SA-03', 'SA-02', 'SA-11'})).intersection(G[SA][1].buffer(0.02))
for n, g in parts.items(): print('  ', n, round(A(g)), 'km2')
X = unary_union([g.buffer(0.003) for g in parts.values()]).buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) > 0.5]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
o = polys(unary_union([X] + holes).buffer(0).intersection(MP(C['me2']['polys']).buffer(0.002)), 0.02); Y = MP(o); rws = []  # V1 stays inside V2 (drops the Bardawil lagoon and Khuzestan tidal flats that V2 treats as water)
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', MODE, old, '->', C['shj']['km2'])
for n_, p in {'Mecca': (39.83, 21.42), 'Medina': (39.61, 24.47), 'Jeddah': (39.17, 21.54), 'Taif': (40.41, 21.27), 'Yanbu': (38.06, 24.09), 'Tabuk': (36.57, 28.38), 'Al-Ula': (37.92, 26.62), 'Khaybar': (39.29, 25.70),
              'Tayma (Tabuk)': (38.55, 27.63), 'Al-Bahah': (41.47, 20.01), 'Badr': (38.79, 23.73), 'Riyadh (Najd, out)': (46.72, 24.69), 'Abha (Asir, out)': (42.5, 18.22), 'Jerusalem': (35.23, 31.78), 'Damascus': (36.29, 33.51), 'Baghdad': (44.36, 33.31), 'Basra': (47.78, 30.51), 'Kuwait City': (47.98, 29.37), 'Mosul': (43.13, 36.34), 'Erbil': (44.01, 36.19), 'Nicosia': (33.36, 35.17), 'El-Tor (Sinai)': (33.62, 28.24), 'Al-Arish': (33.8, 31.13), 'Mersin': (34.64, 36.81), 'Adana': (35.32, 37.0), 'Ahvaz': (48.67, 31.32), 'Ilam': (46.42, 33.64), 'Sakakah': (40.2, 29.97), 'Arar': (41.04, 30.98), 'Kermanshah (out)': (47.07, 34.31), 'Bushehr (out)': (50.84, 28.97), 'Van (out)': (43.38, 38.5), 'Malatya (out)': (38.31, 38.35), 'Port Said (out)': (32.3, 31.26)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('shj outside me2', round(A(Y.difference(MP(C['me2']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
