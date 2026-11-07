"""Version 331 (Nawaz, on V5 over the Andaman Sea: "Are there any stray specs here.. if so are they part of the Roman Empire?" -> yes:
Thai islands (Phuket, Ko Lanta, Ko Yao, Ko Samui, Ko Pha Ngan, Ko Tao, Ko Chang, Ko Kut) and Sumatra's Weh and Breueh, leftovers
inherited by V4 from the old Super Caliphate's Southeast Asia; never Roman -> "Sure"). Removed from V4 (sas) and V5 (grm): every
piece lying in Thailand or Indonesia (base map). Myanmar (Mergui), India (Andaman & Nicobar) and Bangladesh pieces stay."""
import json, os, subprocess
from shapely.geometry import Polygon, MultiPolygon, box, shape
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
BAD = [shape(f['geometry']).buffer(0.02) for f in geo['features'] if f.get('geometry') and f['properties']['n'] in ('Thailand', 'Indonesia')]
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
B = box(90, -6, 108, 22)
for k in ['sas', 'grm']:
    ps = C[k]['polys']
    gone = [r for r in ps if Polygon(r[0]).within(B) and any(Polygon(r[0]).within(b) for b in BAD)]
    C[k]['polys'] = [r for r in ps if r not in gone]
    C[k]['states'] = [s for s in C[k]['states'] if s['n'] not in ('Thailand', 'Indonesia')]
    old = C[k]['km2']; C[k]['km2'] = km2of(C[k]['polys'])
    print(k, 'dropped', len(gone), 'pieces', round(sum(A(Polygon(r[0])) for r in gone)), 'km2;', old, '->', C[k]['km2'])
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
print('sas outside grm', round(A(M('sas').difference(M('grm').buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
