"""Version 290 (Nawaz: "build upon V5 and add in this the entire Mediterranean basin" -> bordering countries, a new version;
"Add Moldova, Romania, Kosovo, Serbia, Hungary, Slovakia, Austria, Switzerland, Luxembourg, Belgium, United Kingdom and Ireland";
"Add the Roman Rhineland ... add Roman Empire at its peak and all the lands that they held"; "Add Crimea and the Georgian coast ...
and add what's left out"; "Remove crimea and apply").
New V6 (CALIPH.rom) = V5 (CALIPH.sas) + tools/data/v6_mediterranean_rome290.geojson. That file holds, every land whole (base map):
Italy, San Marino, the Vatican, France (mainland and Corsica), Monaco, Slovenia, Croatia, Bosnia, Montenegro, Andorra; Moldova,
Romania, Kosovo, Serbia, Hungary, Slovakia, Austria, Switzerland, Liechtenstein, Luxembourg, Belgium, the United Kingdom, Ireland,
Man, Jersey, Guernsey; and the Roman Empire of 117 CE (provinces of the Digital Atlas of the Roman Empire, Lund University, via
github.com/klokantech/roman-empire data/provinces.geojson) in whole Overture 2026-10-21.0 districts: German Kreise and Dutch
gemeenten more than half Roman or with 150 km2+ of Roman land, then any with 5 km2+ left, and the Reni, Safiany, Kiliia and
Vylkove hromadas on the Danube delta; the last ~860 km2 of Roman land (edge slivers) added as is. Crimea was previewed and removed.
The Georgian coast was already in V5. The same lands go into the Super Caliphate (CALIPH.v2, now V7) so V6 stays inside V7; V7 also takes all of V6 (Sicily, Malta and other V5 lands it lacked).
Run after tools/v2_kashmir286.py (src as of Version 289)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
ADD = shape(json.load(open(os.path.join(P, 'tools/data/v6_mediterranean_rome290.geojson')))['features'][0]['geometry']).buffer(0)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def build(base, more=None):
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[base]['polys']]).buffer(0)
    X = shapely.set_precision(shapely.union_all([V, ADD.buffer(0.003)] + ([more.buffer(0.003)] if more is not None else []), grid_size=0.001).buffer(0), 0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    rows = {r['id']: r for r in C[base]['states']}
    for k, (n, g) in G.items():
        if g.area == 0 or not g.intersects(ADD): continue
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rows[k] = {'id': k, 'n': rows.get(k, {}).get('n', n), 'km2': round(A(g)), 'pct': pct}
    return {'polys': out, 'km2': km2, 'states': sorted(rows.values(), key=lambda r: -(r.get('km2') or 0) * (r.get('pct') or 100))}
C['rom'] = build('sas'); print('rom', C['sas']['km2'], '->', C['rom']['km2'])
old = C['v2']['km2']; C['v2'].update(build('v2', MultiPolygon([Polygon(r[0], r[1:]) for r in C['rom']['polys']]).buffer(0))); print('v2', old, '->', C['v2']['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
