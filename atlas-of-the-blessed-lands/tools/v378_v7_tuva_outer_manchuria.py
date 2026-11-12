"""Version 378 PREVIEW, on top of the Version 377 Greater China preview (Nawaz sent six maps of the Greater China concept: the Yuan dynasty, the
Qing dynasty, Tuva (Tyva), Outer Manchuria, Madrid Maps' "Concept of a Greater China" and Arab Atlas' "actual greater China / to China until 1867" map,
and said "Preview"). Their lands: the PRC and Taiwan, Mongolia, Tuva, Outer Manchuria, parts of Kazakhstan and Kyrgyzstan, Nepal, Bhutan and Arunachal Pradesh.
Already in V7: Kazakhstan, Kyrgyzstan, Nepal, Bhutan, India (Arunachal). New here, whole Russian federal subjects (Overture 2026-10-21.0 regions,
tools/data/v378_ru_far_east.parquet): the Tuva Republic, and Outer Manchuria = Primorsky Krai, Khabarovsk Krai (to the Okhotsk coast), Amur Oblast and the
Jewish Autonomous Oblast. Sakhalin is NOT added (the Outer Manchuria map does not shade it). The two dynasty maps are blank outlines with
fuzzy northern borders, so they were not traced. DIR env = project dir (preview: a copy; needs the 377 preview applied first)."""
import pyarrow.parquet as pq
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
V = MP(C['sup']['polys']); parts = {}
for r in pq.read_table(os.path.join(HERE, 'tools/data/v378_ru_far_east.parquet')).to_pylist():
    if r['class'] != 'land' or r['is_land'] is False: continue
    g = shapely.from_wkb(r['geometry']).buffer(0); parts[r['region']] = g
    print('  +', dict(r['names']['common']).get('en'), round(A(g.difference(V))), 'km2 of', round(A(g)))
X = unary_union([V] + [g.buffer(0.003) for g in parts.values()]).buffer(0)
o = polys(X, 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['sup']['km2']; C['sup'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}
print('sup', old, '->', C['sup']['km2'])
for n_, p in {'Kyzyl (Tuva)': (94.45, 51.72), 'Blagoveshchensk (Amur)': (127.53, 50.27), 'Khabarovsk': (135.08, 48.48), 'Vladivostok': (131.9, 43.12), 'Birobidzhan': (132.92, 48.79), 'Okhotsk coast (Ayan)': (138.15, 56.45),
              'Nikolayevsk-on-Amur': (140.7, 53.14), 'Sakhalin (out)': (142.75, 46.96), 'Irkutsk (out)': (104.3, 52.29), 'Ulan-Ude (out)': (107.6, 51.83), 'Chita (out)': (113.5, 52.03), 'Yakutsk (out)': (129.7, 62.03)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 111, 1), 'km')
print('tib outside sup', round(A(MP(C['tib']['polys']).difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
