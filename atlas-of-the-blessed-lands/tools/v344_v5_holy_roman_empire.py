"""Version 344 PREVIEW (Nawaz: "Is the German Empire of 800-1806 Roman?" -> "Preview German empire"). V5 (grm) takes the lands of the
Holy Roman Empire (800/962-1806) that it lacked, i.e. those east of the Elbe and in Bohemia: all of Germany (Brandenburg,
Mecklenburg, Pomerania, Saxony east of the Elbe, Holstein to the Eider; not Schleswig, a Danish fief, nor Fehmarn), all of Czechia (Bohemia), and in Poland the old imperial lands of
Silesia, Lusatia, the Neumark and Pomerania: Lower Silesian, Opole, Lubusz and West Pomeranian voivodeships whole, the Silesian
(Upper Silesia and Teschen) counties of Silesian voivodeship, and Slupsk (Stolp). Lands already in V5 (the Low Countries, western
Germany, Austria, Switzerland, Slovenia, northern Italy, Burgundy) are unchanged. Not added: Ducal Prussia and Livonia (outside the
Empire), Lauenburg-Butow and the Polish strip round Walcz (approximate edge). Base map countries 276, 203; Overture 2026-10-21.0
(tools/data/v344_hre_poland.parquet)."""
import json, os, subprocess, shapely
import pyarrow.parquet as pq
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
SILESIA = {'Bielsko-Biała', 'Powiat Bielski', 'Bytom', 'Chorzów', 'Gliwice', 'Powiat Gliwicki', 'Jastrzębie-Zdrój', 'Katowice', 'Mysłowice',
           'Piekary Śląskie', 'Powiat Bieruńsko-lędziński', 'Powiat Cieszyński', 'Powiat Lubliniecki', 'Powiat Mikołowski', 'Powiat Pszczyński',
           'Powiat Raciborski', 'Powiat Rybnicki', 'Rybnik', 'Powiat Tarnogórski', 'Powiat Wodzisławski', 'Ruda Śląska', 'Siemianowice Śląskie',
           'Świętochłowice', 'Tychy', 'Zabrze', 'Żory'}
rows = pq.read_table(os.path.join(P, 'tools/data/v344_hre_poland.parquet')).to_pylist()
g = lambda r: shapely.from_wkb(r['geometry']).buffer(0)
PL = unary_union([g(r) for r in rows if r['subtype'] == 'region'] + [g(r) for r in rows if r['region'] == 'PL-24' and r['name'] in SILESIA]
                 + [g(r) for r in rows if r['region'] == 'PL-22' and r['name'] in ('Słupsk', 'Powiat Słupski')])
SCHLESWIG = Polygon([(7.5, 54.32), (8.95, 54.32), (9.66, 54.30), (10.15, 54.36), (10.70, 54.395), (11.5, 54.395), (11.5, 55.2), (7.5, 55.2)])   # north of the Eider: the Duchy of Schleswig, outside the Empire
DE, CZ = G['276'][1].difference(SCHLESWIG), G['203'][1]
V5 = M('grm')
for n, x in [('Germany east of the Elbe (Holstein to the Eider)', DE), ('Czechia (Bohemia)', CZ), ('Silesia, Lusatia, Neumark, Pomerania (Poland)', PL)]:
    print(n, 'adds', round(A(x.difference(V5))), 'km2')
X = unary_union([V5, DE.buffer(0.003), CZ.buffer(0.003), PL.buffer(0.003)]).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, gg) in G.items():
    if gg.area and gg.intersects(Y):
        pct = round(100 * gg.intersection(Y).area / gg.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(gg)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Berlin': (13.40, 52.52), 'Hamburg': (10.0, 53.55), 'Kiel (Holstein)': (10.13, 54.32), 'Prague': (14.42, 50.08), 'Wroclaw (Breslau)': (17.03, 51.11),
              'Szczecin (Stettin)': (14.55, 53.43), 'Slupsk (Stolp)': (17.03, 54.46), 'Katowice': (19.02, 50.26), 'Opole': (17.93, 50.67),
              'Gdansk (Polish, stays out)': (18.65, 54.35), 'Krakow (Polish, stays out)': (19.94, 50.06), 'Kaliningrad (Prussia, stays out)': (20.51, 54.71),
              'Flensburg (Schleswig, stays out)': (9.43, 54.79)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('sas outside grm', round(A(M('sas').difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
