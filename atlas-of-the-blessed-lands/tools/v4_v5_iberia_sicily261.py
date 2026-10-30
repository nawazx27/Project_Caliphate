"""Version 261 (Nawaz: "add Sicily and all the islands associated with it, and make sure the entire Iberian Peninsula is in v4 and v5").
V4 (me9) and V5 (sah) both gain Sicily with its islands and Malta (as tools/v5_sicily250.py drew them) and the thin strips of
OpenStreetMap's "Iberia" peninsula (tools/data/iberia_osm.geojson, Overture base/land, class peninsula) that lie in France along the
Pyrenees (~300 km2; no recognized town is cut). Run AFTER tools/v4_sahel260.py. (Only these: Nawaz did not want the Russia and Indian subcontinent preview applied.)"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
land = unary_union(list(G.values()))
SIC = unary_union([p for p in getattr(G['380'], 'geoms', [G['380']]) if 11 < p.centroid.x < 16 and 35 < p.centroid.y < 39.2 and p.area < 10])
IB = shape(json.load(open(os.path.join(P, 'tools/data/iberia_osm.geojson')))['geometry']).buffer(0).intersection(land)
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for k in ['me9', 'sah']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    add = [IB, SIC, G['470']]
    X = shapely.union_all([V] + [g.buffer(0.003) for g in add], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    print(k, C[k]['km2'], '->', km2, 'Iberia in %', round(100 * A(IB.intersection(Y)) / A(IB), 3), 'Sicily in %', round(100 * A(SIC.intersection(Y)) / A(SIC), 2), 'Malta in %', round(100 * A(G['470'].intersection(Y)) / A(G['470']), 2))
    rows = [{'id': 'FRA_IB', 'n': 'France: the strips of the Iberian Peninsula along the Pyrenees (OpenStreetMap outline)', 'km2': round(A(IB.intersection(G['FRA']))), 'pct': 0.1}]
    rows += [{'id': 'SIC', 'n': 'Italy: Sicily with its islands (Aegadian, Aeolian, Ustica, Pantelleria, Pelagie)', 'km2': round(A(SIC)), 'pct': round(A(SIC) / A(G['380']) * 100, 1)}, {'id': '470', 'n': 'Malta', 'km2': round(A(G['470'])), 'pct': 100}]
    C[k].update(polys=out, km2=km2, states=[r for r in C[k]['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
