"""Version 223 (Nawaz: "In V3, do you have every official border at 100%?", then "Go ahead" with: close the hairline gaps and take
out the land of countries V3 does not list). V3 (key me2) is cut to its countries' official borders on the base map:
- every bit of an unlisted country goes: the Tashkurgan pocket (China) and the pocket next to Turkmenistan (Uzbekistan), both from
  gap filling, and the ~300 m strips the outline ran past its borders into neighbours (Algeria, Russia, Romania, Serbia, India...);
- kept by Nawaz's standing rules: the whole island of Cyprus (Northern Cyprus, the UN buffer zone, Akrotiri, Dhekelia) and Lake
  Albert's DR Congo half with his shore strip (V3's land in DR Congo by the lake, 29.9-31.6 E, 0.8-2.6 N);
- every listed country made whole on the base map and on Natural Earth 10 m (its small islets and reclaimed land, e.g. Bahrain's),
  never past an unlisted country; on coasts the line sits ~150 m offshore so the page's 0.001 deg rounding never cuts the land; on
  borders with unlisted countries it follows the border to that rounding (about 50-100 m).
Standing rule (Nawaz, 2026-10-23): in V3 gap filling never adds land of a country V3 does not list. So no fill_gaps run after this.
Run: python3 tools/v3_official223.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, box, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['me2']['polys']]).buffer(0)
listed = {r['id'] for r in C['me2']['states'] if r['id'] in G}
keep = {'CYN', 'CNM', 'ESB', 'WSB'}                       # the whole island of Cyprus
ALBERT = box(29.9, 0.8, 31.6, 2.6)                          # Lake Albert's DR Congo side and the shore strip
other = unary_union([g for i, g in G.items() if i not in listed and i not in keep and i != '180'] + [G['180'].difference(ALBERT)])
NE = {}
for f in json.load(open(os.path.join(P, 'ne_10m_admin_0_countries.geojson')))['features']:
    NE.setdefault(f['properties']['ISO_N3'], []).append(shape(f['geometry']).buffer(0))
mine = unary_union([G[i] for i in listed] + [g for i in listed for g in NE.get(i, [])])
cut = V.intersection(other)
X = shapely.union_all([V.difference(other), mine.buffer(0.0015).difference(other)], grid_size=0.001)   # 0.0015 deg: the coast line sits just offshore so the 0.001 deg rounding never cuts the land
out = []
for q in getattr(X, 'geoms', [X]):
    if q.geom_type != 'Polygon' or A(q) < 0.05: continue
    q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
    out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
print('cut from unlisted countries:', round(A(cut)), 'km2 | added (hairlines and islets):', round(A(Y.difference(V))), 'km2')
worst = sorted(((A(G[i].intersection(Y)) / A(G[i]) * 100, i) for i in listed))[:5]
print('lowest base-map coverage:', [(i, round(p, 4)) for p, i in worst])
print('left in unlisted countries:', round(A(Y.intersection(other)), 1), 'km2 | V3', C['me2']['km2'], '->', km2)
C['me2'].update(polys=out, km2=km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
