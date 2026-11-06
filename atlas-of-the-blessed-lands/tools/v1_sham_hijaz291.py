"""Version 291 (Nawaz: "Make New v1" with his maps of Bilad al-Sham and al-Hijaz; "Cover till the furthest dotted line";
"I meant using classical knowledge and sources"; "Stick to hijaz and sham"; northern Iraq and Badiyat al-Sham / al-Samawa added
at his request; "Across all definitions, Max and Widest" -> classical only, geographers' Hijaz; "New v1").
New V1 (CALIPH.shj) from tools/data/v1_sham_hijaz291.geojson (how it was made: tools/v1_sham_hijaz291_build/README.md).
Every other version moves up one number (V1 me8 -> V2 ... the Super Caliphate v2 -> V8). The new V1 is also unioned into
every larger version (me8, me2, ca, me9, sas, rom, v2), so each stays inside the next (about 450 km2 of coastal slivers).
Run after tools/v6_roman290.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
NEW = shape(json.load(open(os.path.join(P, 'tools/data/v1_sham_hijaz291.geojson')))['features'][0]['geometry']).buffer(0)
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
print('shj', C['shj']['km2'])
for key in ['me8', 'me2', 'ca', 'me9', 'sas', 'rom', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    extra = NEW.difference(V)
    if A(extra) < 1: continue
    X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
    o = polys(X); old = C[key]['km2']; C[key].update(polys=o, km2=km2of(o)); print(key, old, '->', C[key]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
