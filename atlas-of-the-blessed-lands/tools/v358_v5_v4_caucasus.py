"""Version 358 (Nawaz: "Keep this Gelendzhik and ... use the crown used in v4 which has the modern Georgia and [Derbent] inside").
V5 (grm) takes V4's (sas) Caucasus: inside the box 39.0-49.5E, 41.0-44.6N, everything V5 holds beyond V4 is removed (the Russian crown:
Sochi-Adler coast, Krasnaya Polyana, the north-slope strips), so the Caucasus is modern Georgia (with Abkhazia) and Azerbaijan plus
Derbent and southern Dagestan, exactly as in V4. The Bosporan block (Taman, Anapa, Novorossiysk, the Gelendzhik district) lies west of
the box and is kept. Run on Version 357."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
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
V4, V5 = M('sas'), M('grm')
BOX = box(39.0, 41.0, 49.5, 44.6)
CUT = V5.difference(V4).intersection(BOX)
print('removes', round(A(CUT)), 'km2')
X = V5.difference(CUT.buffer(0.0005)).union(V4.intersection(BOX)).buffer(0)
o = polys(X, 0.02); Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['grm']['km2']; C['grm'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('grm', old, '->', C['grm']['km2'])
for n_, p in {'Pitsunda (Pityus)': (40.34, 43.16), 'Sukhum (Sebastopolis)': (41.02, 43.0), 'Poti (Phasis)': (41.67, 42.15), 'Gonio (Apsaros)': (41.57, 41.57), 'Mtskheta': (44.72, 41.84),
              'Gobustan': (49.38, 40.10), 'Derbent': (48.29, 42.06), 'Rutul': (47.42, 41.54), 'Sochi (out)': (39.72, 43.59), 'Gelendzhik': (38.06, 44.56), 'Arkhipo-Osipovka tower': (38.55, 44.39),
              'Anapa': (37.32, 44.89), 'Taman': (36.72, 45.21)}.items():
    print('  ', n_, Y.buffer(0.003).contains(Point(p)))
print('sas outside grm', round(A(V4.difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
