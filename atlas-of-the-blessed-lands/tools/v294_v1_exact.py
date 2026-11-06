"""Version 294 (Nawaz: "Make v1 borders better" -> "borders exactly like this" (the page's Shām/Ḥijāz diagram) -> "Finish the job").
V1 (CALIPH.shj) = tools/data/v1_sham_hijaz294.geojson: the land inside the diagram's outer lines exactly (Shām's disputed edge,
SHAM_OUTER, and al-Ḥijāz's uncertain edge, HIJAZ_OUTER, in src/old_data.js), straight edges, no whole-district or town additions;
made by tools/v1_sham_hijaz291_build/exact294.py. It lies wholly inside V2 (checked: 0 km2 outside), so the larger versions are unchanged.
V1 is an exception to the every-outline rule (Cyprus, Lake Albert, Georgia, Armenia, Azerbaijan): the diagram does not hold them.
Run after tools/v293_no_crimea.py."""
import json, os, subprocess
from shapely.geometry import shape
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
from pyproj import Geod
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F = json.load(open(os.path.join(P, 'tools/data/v1_sham_hijaz294.geojson')))['features'][0]['geometry']
NEW = shape(F).buffer(0); out = F['coordinates']
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
rows = []
for k, (n, g) in G.items():
    if g.area and g.intersects(NEW):
        pct = round(100 * g.intersection(NEW).area / g.area)
        if pct >= 1: rows.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
old = C['shj']['km2']; C['shj'] = {'polys': out, 'km2': km2, 'states': sorted(rows, key=lambda r: -r['km2'] * r['pct'])}
print('shj', old, '->', km2, [r['n'] for r in rows])
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
