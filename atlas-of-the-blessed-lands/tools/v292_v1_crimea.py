"""Version 292 (Nawaz: "It should look like this" (the page's Sham/Hijaz diagram), "Add these too" (Hejaz map, Britannica Levant, Abbasid Sham map),
"Take every district whole and preview", then "apply and add Crimea to V6 and find a way to connect Crimea from Georgia through Ukraine. Moldova."
-> he chose V7 (rom, the Roman one, which was V6 when made) and the coastal link).
1. V1 (CALIPH.shj) replaced from tools/data/v1_sham_hijaz292.geojson (how: tools/v1_sham_hijaz291_build/README.md), unioned into every larger version.
2. V7 (CALIPH.rom) and V8 (CALIPH.v2) get tools/data/v7_crimea_link292.geojson: Crimea and Sevastopol; Kherson, Mykolaiv and Odesa
   oblasts (joining Crimea to Moldova); Temryuk (Taman), Anapa, Novorossiysk, Gelendzhik, Tuapse, Sochi and Sirius (the coast from
   the Kerch Strait to Abkhazia in Georgia). Whole Overture 2026-10-21.0 units.
Run after tools/v1_sham_hijaz291.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
NEW = shape(json.load(open(os.path.join(P, 'tools/data/v1_sham_hijaz292.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, minkm=0.02):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < minkm: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def rows_for(Y, base=None):
    rows = {r['id']: r for r in (base or [])}
    for k, (n, g) in G.items():
        if g.area == 0 or not g.intersects(Y): continue
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1 and (base is None or k not in rows): rows[k] = {'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct}
    return sorted(rows.values(), key=lambda r: -(r.get('km2') or 0) * (r.get('pct') or 100))
out = polys(NEW, 0.05)
C['shj'] = {'polys': out, 'km2': km2of(out), 'states': rows_for(NEW)}
LINK = shape(json.load(open(os.path.join(P, 'tools/data/v7_crimea_link292.geojson')))['features'][0]['geometry']).buffer(0)
for key in ['rom', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    X = shapely.set_precision(shapely.union_all([V, LINK.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
    o = polys(X); old = C[key]['km2']; Y = MultiPolygon([Polygon(r[0], r[1:]) for r in o]).buffer(0)
    C[key].update(polys=o, km2=km2of(o), states=rows_for(Y, [r for r in C[key]['states'] if r['id'] not in ('804', '643')]) )
    print(key, 'Crimea link', old, '->', C[key]['km2'])
print('shj', C['shj']['km2'])
for key in ['me8', 'me2', 'ca', 'me9', 'sas', 'rom', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    extra = NEW.difference(V)
    if A(extra) < 1: continue
    X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
    o = polys(X); old = C[key]['km2']; C[key].update(polys=o, km2=km2of(o)); print(key, old, '->', C[key]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
