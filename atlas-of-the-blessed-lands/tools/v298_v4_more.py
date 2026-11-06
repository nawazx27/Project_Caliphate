"""Version 298 (Nawaz: "Is this Roman Empire at its peak ... all the lands" -> "Preview adding all three to V4" (Antonine Scotland, Rhine-Elbe Germany, Crimea+Taman) -> "Add Moldova, Austria, Hungary, Switzerland, Slovakia, Serbia" -> "Remove Crimea and add uk and Ireland and push").
V4 (CALIPH.sas, the Grand Caliphate) = tools/data/v4_rome298.geojson: V4 + the Roman Empire of 117 CE (DARE provinces,
tools/data/roman_provinces_117_dare.geojson): Italy, mainland France with Corsica, Belgium, Luxembourg, Switzerland, Austria,
Slovenia, Croatia, Bosnia, Montenegro, Serbia, Kosovo, Monaco, San Marino, Liechtenstein, Andorra whole; Britain to Hadrian's Wall,
the Rhineland and limes lands, the Netherlands south of the Rhine, Pannonia and Dacia by whole Overture districts (>=50% Roman or
>=150 km2 Roman); the last ~5,000 km2 of Roman land as is; small pockets filled. Build script: tools/v297_build/v4rome.py.
V5 (rom) and V6 (v2) are unioned with the new V4 so each version stays inside the next. Run after tools/v295_v7_rivers.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F = json.load(open(os.path.join(P, 'tools/data/v4_rome298.geojson')))['features'][0]['geometry']
NEW = shape(F).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def rows(Y, base):
    r = {x['id']: x for x in base}
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: r[k] = {'id': k, 'n': r.get(k, {}).get('n', n), 'km2': round(A(g)), 'pct': pct}
    return sorted(r.values(), key=lambda x: -(x.get('km2') or 0) * (x.get('pct') or 100))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
old = C['sas']['km2']; C['sas'].update(polys=F['coordinates'], km2=km2of(F['coordinates']), states=rows(NEW, C['sas']['states'])); print('sas', old, '->', C['sas']['km2'])
for key in ['rom', 'v2']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    ex = A(NEW.difference(V)); print(key, 'V4 land outside it km2', round(ex))
    if ex < 1: continue
    X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.02: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    old = C[key]['km2']; C[key].update(polys=out, km2=km2of(out)); print(key, old, '->', C[key]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
