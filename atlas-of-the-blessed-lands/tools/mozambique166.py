"""Version 166 (Nawaz, with a phone screenshot and a black line drawn along the lower Zambezi: "Take Mozambique until the river and the border
should be the river"). All of Mozambique north of the Zambezi except Tete province (Natural Earth river line, from where it enters Mozambique at Zumbo to its
mouth) is added to V2 and V2-B; the river is the new border (the south bank stays out). V7 is rebuilt from V2. Run: python3
tools/mozambique166.py, then tools/v7_build159.py, then the clean-up loop."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, LineString, mapping
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, linemerge
from pyproj import Geod
import numpy as np
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); D = os.path.join(P, 'tools/data')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}; land = unary_union(list(G.values()))
MZ = G['508']
rv = [shape(f['geometry']) for f in json.load(open(os.path.join(P, 'rivers.geojson')))['features'] if f['properties'].get('name') == 'Zambezi']
Z = linemerge(unary_union(rv))
pieces = [p for p in getattr(Z, 'geoms', [Z]) if p.length > 1.0 and p.bounds[0] >= 28.0]   # the river data comes in pieces (lakes Kariba and Cahora Bassa break it); join those east of 28 E, west to east
pieces.sort(key=lambda g: g.bounds[0]); co = []
for g in pieces:
    c = list(g.coords)
    if c[0][0] > c[-1][0]: c = c[::-1]
    co += c
co.sort(key=lambda c: c[0])
print('Zambezi pieces', [(round(g.length, 1), [round(v, 1) for v in g.bounds[:3:2]]) for g in pieces], 'points', len(co))
# keep from Zumbo (30.0 E) to the mouth, extended 3 degrees seaward and 1.5 degrees upstream so the cut crosses the whole country
sel = [c for c in co if c[0] >= 29.5]
a = np.array(sel[0]); b = np.array(sel[1]); up = a + (a - b) / np.linalg.norm(a - b) * 1.5
dn = np.array((40.0, sel[-1][1]))   # the delta's last points zigzag, so the cut leaves the river's mouth due east into the sea
line = [tuple(up)] + sel + [tuple(dn)]
north = Polygon(line + [(48.0, dn[1]), (48.0, 5.0), (up[0], 5.0)]).buffer(0)   # closed far to the east so the whole coast north of the mouth is kept
import pyarrow.parquet as pq
TETE = unary_union([shapely.from_wkb(r['geometry']) for r in pq.read_table('/tmp/claude-0/-home-user-Project-Caliphate/e227bf79-e0c6-5974-a79a-4f0672b36775/scratchpad/v155/mz_regions.parquet').to_pylist() if r['names']['primary'] == 'Tete']).buffer(0)
TETE = TETE.buffer(0.03)   # the province outline and the country outline differ a little; this keeps hairlines from staying along the cut
reg = MZ.intersection(north).difference(TETE).buffer(0)   # "This bit is not needed": Tete province's land north of the river (the finger west of Malawi) is left out
print('Mozambique', round(A(MZ)), 'km2; north of the river', round(A(reg)), 'km2')
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'role': 'add', 'v': 'Version 166 Mozambique north of the Zambezi'}, 'geometry': mapping(reg)}]}, open(os.path.join(D, 'mozambique166.geojson'), 'w'))
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {}, 'geometry': mapping(LineString(line))}]}, open(os.path.join(D, 'zambezi_line166.json'), 'w'))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
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
    X = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0).difference(MZ.buffer(0.03).intersection(TETE).intersection(north.buffer(0.03)).buffer(0))   # drop the finger put in before
    X = shapely.make_valid(X)
    X = unary_union([q for q in getattr(X, 'geoms', [X]) if not (q.intersects(MZ.buffer(0.1)) and not q.intersects(MZ.buffer(-0.5)) and A(q) < 300 and 29 < q.centroid.x < 37.5 and -19 < q.centroid.y < -9)])   # leftover hairlines from the finger
    add = reg.difference(X); print(k, 'adds', round(A(add)))
    X2 = shapely.union_all([shapely.make_valid(X), shapely.make_valid(add.buffer(0.003).intersection(land.buffer(0.003)))], grid_size=0.001)
    C[k]['polys'] = pack(X2); C[k]['km2'] = km2(C[k]['polys'])
    C[k]['states'] = [r for r in C[k]['states'] if r['id'] != '508_N']
    C[k]['states'].append({'id': '508_N', 'n': 'Mozambique: everything north of the Zambezi except Tete province, with the river as the border', 'km2': round(A(reg)), 'pct': round(A(reg) / A(MZ) * 100, 1)})
    print(k, C[k]['km2'])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
