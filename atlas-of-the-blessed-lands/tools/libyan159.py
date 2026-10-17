"""Version 159 (Nawaz: "Add the whole Libyan desert in v2 and v2b and make sure you fill that 1% Balkan which is left out of 99% in v2").
The whole Libyan Desert (Natural Earth physical region, on land) is added to V2 and V2-B (V7, built on V2, already had it): 322,875 km2 more,
in northern Chad and the Central African Republic's edge. The Balkan Peninsula's last 1% went into V2 in tools/v7_build159.py; this prints
the Balkan Peninsula's coverage as a check. Run: python3 tools/libyan159.py, then re-run tools/v7_build159.py to refresh V7 from V2."""
import json, os, subprocess, shapely, copy
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']])
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
reg = {f['properties']['NAME'].upper(): shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'regions.geojson')))['features']}
LD = [g for n, g in reg.items() if n.startswith('LIBYAN DESERT')][0].intersection(land).buffer(0)
BP = [g for n, g in reg.items() if n.startswith('BALKAN PEN')][0].intersection(land).buffer(0)
mk = lambda ps: MultiPolygon([Polygon(r[0], r[1:]) for r in ps]).buffer(0)
def pack(X):
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon': continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
def km2(out): return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
for k in ('x', 'xb'):
    X = mk(C[k]['polys']); add = LD.difference(X)
    print(k, 'Libyan Desert adds', round(A(add)), 'km2; before', round(A(LD.intersection(X)) / A(LD) * 100, 1), '%')
    X = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
    C[k]['polys'] = pack(X); C[k]['km2'] = km2(C[k]['polys'])
    rows = []
    for f in geo['features']:
        i = str(f['id']); a = add.intersection(shape(f['geometry']).buffer(0))
        if A(a) < 20 or any(r['id'] == 'LD_' + i for r in C[k]['states']): continue
        rows.append({'id': 'LD_' + i, 'n': {'148': 'Chad', '140': 'Central African Republic'}.get(i, i) + ': the rest of the Libyan Desert', 'km2': round(A(a)), 'pct': round(A(a) / A(shape(f['geometry']).buffer(0)) * 100, 1)})
    C[k]['states'] += rows
    print(k, C[k]['km2'], 'Libyan Desert now', round(A(LD.intersection(X)) / A(LD) * 100, 2), '%; Balkan Peninsula now', round(A(BP.intersection(X)) / A(BP) * 100, 2), '%')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
