"""Version 329 (Nawaz circled a speck off western Norway: "Is this a part of Roman Empire" -> no). It was Karmoy island (and an islet
north of it), ~195 km2, picked up by the Version 305 trace of the Roman-rule map (a mis-registered speck; Rome never held Norway).
V5 (grm) drops every piece in Norway (3-8 E, 57.5-61.5 N). Checked: every other small V5 piece in a country V5 barely holds comes
from V4 (Thai, Sumatran, Madagascan, Caspian, Lake Malawi islands)."""
import json, os, subprocess
from shapely.geometry import Polygon, MultiPolygon, box, shape
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
B = box(3, 57.5, 8, 61.5)
keep = [r for r in C['grm']['polys'] if not Polygon(r[0]).within(B)]
print('dropped', len(C['grm']['polys']) - len(keep), 'pieces:', round(sum(A(Polygon(r[0])) for r in C['grm']['polys'] if Polygon(r[0]).within(B)), 1), 'km2')
C['grm']['polys'] = keep
C['grm']['states'] = [s for s in C['grm']['states'] if s['n'] != 'Norway']
old = C['grm']['km2']; C['grm']['km2'] = km2of(keep); print('grm', old, '->', C['grm']['km2'])
Y = MultiPolygon([Polygon(r[0], r[1:]) for r in keep]).buffer(0)
S = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sas']['polys']]).buffer(0)
print('sas outside grm', round(A(S.difference(Y.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
