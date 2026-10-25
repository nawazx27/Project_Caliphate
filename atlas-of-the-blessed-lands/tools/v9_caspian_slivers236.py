"""Version 236 (Nawaz, circling V9's Caucasus on his phone: "Just give me normal Georgia and Azerbaijan borders with the stray line fixed").
V9 (CALIPH.v2) kept small leftover slivers of Russian land along the Caspian and Caucasus (from older Dagestan coast strips); zoomed out
the outline is drawn round each, a stray gold line down the Dagestan coast. Every V9 piece lying mostly in Russia is removed; V9 keeps to
the modern borders of Georgia and Azerbaijan. Run: python3 tools/v9_caspian_slivers236.py"""
import json, os, subprocess, shapely
from shapely.geometry import shape, Polygon
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
RU = shapely.union_all([shape(f['geometry']).buffer(0) for f in geo['features'] if f['id'] == '643' and f.get('geometry')])
RUb = RU.buffer(0.02)   # Russian land and its shore water
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
keep, gone = [], 0
for p in C['v2']['polys']:
    g = Polygon(p[0], p[1:]).buffer(0)
    if g.area and g.intersection(RUb).area / g.area > 0.5: gone += A(g); continue
    keep.append(p)
print('pieces', len(C['v2']['polys']), '->', len(keep), 'removed km2', round(gone, 1))
km2 = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(keep).encode()))
print('V9', C['v2']['km2'], '->', km2)
C['v2'].update(polys=keep, km2=km2)
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
