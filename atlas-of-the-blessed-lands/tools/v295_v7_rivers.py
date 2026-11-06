"""Version 295 (Nawaz: red line north of the Black Sea and Caspian, "borders must be good and natural"; "Push it further north";
circle "Push this flat area into natural borders"; "Preview the full river version"; "Apply").
V7 (CALIPH.rom) = tools/data/v7_river_frontier295.geojson: Version 293's V7 + all of Ukraine (Crimea included) + Belarus and Russia
south of a river frontier: Daugava (Latvian border to Velizh), Valdai watershed to the Dnieper source, Dnieper to Dorogobuzh, Ugra
to Kaluga, Oka to Nizhny Novgorod, Volga to the Kama mouth, Kama to the Belaya mouth, Belaya to Ufa, the Ufa-Belaya divide to the
Ural crest, the Uy river east to Troitsk on the Kazakh border (Overture water lines; Troitsk, Kartaly, Magnitogorsk in); North Caucasus, Kalmykia, Astrakhan, Volgograd, Saratov etc. by whole districts;
544 towns on the rivers whole, Kazan whole; Kaliningrad out. Build scripts: tools/v295_build/ (Natural Earth 10m rivers, Overture
2026-10-21.0). V8 (CALIPH.v2) takes all of V7 too. Run after tools/v294_v1_exact.py."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F = json.load(open(os.path.join(P, 'tools/data/v7_river_frontier295.geojson')))['features'][0]['geometry']
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
old = C['rom']['km2']; C['rom'].update(polys=F['coordinates'], km2=km2of(F['coordinates']), states=rows(NEW, C['rom']['states'])); print('rom', old, '->', C['rom']['km2'])
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['v2']['polys']]).buffer(0)
X = shapely.set_precision(shapely.union_all([V, NEW.buffer(0.003)], grid_size=0.001).buffer(0), 0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.02: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
old = C['v2']['km2']; C['v2'].update(polys=out, km2=km2of(out), states=rows(Y, C['v2']['states'])); print('v2', old, '->', C['v2']['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
