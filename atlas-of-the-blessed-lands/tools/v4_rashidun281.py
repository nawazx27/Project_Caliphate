"""Version 281 (Nawaz: "ig we have all the Rashidun lands inside v4"; "Be very academically and technically accurate and check"; then previews
with red lines: Dagestan filled to his lines, "take in entire gujrat", "Just connect gujrat to thana"; "Apply").
Checked (Wikipedia: Rashidun Caliphate, Balanjar, Muslim conquests in the Indian subcontinent): every land the Rashidun held was already
in V4; outside were only raid targets: Thāna and Bharuch (naval raids c. 636/637, al-Baladhuri via Wikipedia) and Balanjar (failed
expedition of ʿAbd al-Raḥmān b. Rabīʿa, 652/653; site unknown: Buynaksk, ruins south of Makhachkala, or the lower Sulak).
tools/data/v4_rashidun281.geojson holds the added shapes per outline:
 me9 (V4): Dagestan districts filled to his lines (whole Overture 2026-10-21.0 districts incl. Makhachkala, Kaspiysk, Buynaksk and
   Buynaksky, Kumtorkalinsky, Karabudakhkent, Kayakent, Izberbash, Sergokala, Levashi, Gunib, Laksky, Kulinsky, Akusha, Dakhadaev,
   Kaitag, Charoda, Tlyarata, Shamil and the rest south-east of his line; the districts' detached northern pasture plots left out), all
   of Gujarat, Daman, Diu, Dadra and Nagar Haveli, Palghar, Thane, Mumbai City and Suburban; gap pockets (incl. ~1,500 km2 of Nandurbar,
   ~390 km2 by Alirajpur, Kutch-Sindh slivers, two Dagestan pockets west of his line by Georgia).
 v2 (V5, the Super Caliphate): the same Dagestan land and pockets (it already held India), so V4 stays inside V5.
Run AFTER tools/v4_derbent269.py (V4) and tools/v5_tibet_plateau277.py (V5)."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon
from shapely.geometry.polygon import orient
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
D = {f['properties']['key']: shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'tools/data/v4_rashidun281.geojson')))['features']}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
for key, W in D.items():
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[key]['polys']]).buffer(0)
    X = shapely.union_all([V, W.buffer(0.002)], grid_size=0.001)
    out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < 0.05: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
    rows = []
    ru = A(W.intersection(G['643']))
    if ru > 100: rows.append({'id': 'RU_DA', 'n': 'Russia: Dagestan from Derbent to Makhachkala, Buynaksk and the lower Sulak (the candidate sites of Balanjar), whole districts to the author’s line', 'km2': round(ru), 'pct': round(100 * ru / A(G['643']), 2)})
    ind = A(W.intersection(G['356']))
    if key == 'me9' and ind > 100: rows.append({'id': 'IN_GJ', 'n': 'India: Gujarat (with Bharuch), Daman, Diu, Dadra and Nagar Haveli, and the coast to Thāna (Palghar, Thane, Mumbai)', 'km2': round(ind), 'pct': round(100 * ind / A(G['356']), 1)})
    print(key, C[key]['km2'], '->', km2, rows)
    C[key].update(polys=out, km2=km2, states=[r for r in C[key]['states'] if r['id'] not in {x['id'] for x in rows}] + rows)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
