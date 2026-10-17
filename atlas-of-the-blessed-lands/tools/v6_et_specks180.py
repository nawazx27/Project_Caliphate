"""Version 180b (Nawaz, screenshot: "What are these dots?"): three crumbs of the old hand-traced East Turkestan left outside China after
tools/v6_et180.py (it replaced only the part inside the base map's China): two in Aksai Chin (79.8E 34.6N, 80.3E 35.2N, which the ETGE
definition leaves out) and one on the Mongolian border (89.9E 47.9N). Removes every V6 piece under 2,000 km2 between 70-100E, 32-50N."""
import json, os, subprocess
from shapely.geometry import Polygon, box
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_)); R = box(70, 32, 100, 50)
keep = [p for p in C['v2']['polys'] if not (R.intersects(Polygon(p[0])) and A(Polygon(p[0], p[1:])) < 2000)]
print('removed', len(C['v2']['polys']) - len(keep)); C['v2']['polys'] = keep
C['v2']['km2'] = int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(keep).encode()))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_); print('V6', C['v2']['km2'])
