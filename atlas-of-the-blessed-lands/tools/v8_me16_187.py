"""Version 187 (Nawaz sent the Middle East reference map, "Another version"). A NEW V8 (CALIPH.me8, XV 'me8'): the sixteen states the map
shades, each whole (Türkiye, Syria, Lebanon, Israel, Palestine, Jordan, Iraq, Iran, Egypt, Saudi Arabia, Kuwait, Bahrain, Qatar, the UAE,
Oman, Yemen), plus the standing lands every outline holds (Version 175 rule): the whole island of Cyprus, Azerbaijan, Georgia, Armenia and
the whole of Lake Albert. Run: python3 tools/v8_me16_187.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
LAKE = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Albert'])
LDRC = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/lake_albert_drc.geojson')))['features']])
C = json.load(open(os.path.join(P, 'src/caliph.json')))
S16 = ['792', '760', '422', '376', '275', '400', '368', '364', '818', '682', '414', '048', '634', '784', '512', '887']
STAND = ['031', '268', '051']
CY = unary_union([G[i][1] for i in ('196', 'CYN', 'CNM', 'WSB', 'ESB')])
parts = [G[i][1] for i in S16 + STAND] + [CY, LAKE, LDRC]
extra = [shapely.make_valid(Polygon(r[0], r[1:])) for r in C['extraLand']['polys']] if 'extraLand' in C else []
X = shapely.union_all([g.buffer(0.003) for g in parts], grid_size=0.001)
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = [{'id': i, 'n': G[i][0], 'km2': round(A(G[i][1])), 'pct': 100} for i in S16 + STAND]
rows.append({'id': '196', 'n': 'Cyprus (the whole island)', 'km2': round(A(CY)), 'pct': 100})
rows.append({'id': '800_A', 'n': 'Lake Albert, the whole lake (Uganda and DR Congo; every outline holds it)', 'km2': round(A(LAKE.union(LDRC))), 'pct': None})
F_ = os.path.join(P, 'src/caliph.json'); C['me8'] = {'polys': out, 'km2': km2, 'states': rows}
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V8', km2, 'km2,', len(out), 'pieces,', len(rows), 'rows')
