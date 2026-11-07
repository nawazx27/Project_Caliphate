"""Version 330 (Nawaz circled specks off Madagascar and in the northern Caspian on V5: "Are these specs part of the Roman Empire?" -> no,
and not part of any land he asked for: leftovers inherited from V4 -> "Sure"). Removed from V4 (sas) and V5 (grm): Nosy Be
(Madagascar, ~300 km2) and the Russian islands off the Volga delta and Chechen Island (~100 km2 each). Kazakh islands stay (all of
Kazakhstan is in V3-V5)."""
import json, os, subprocess
from shapely.geometry import Polygon, MultiPolygon, box
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
DROP = [box(47.5, -14, 49.5, -12), box(47.4, 45.2, 48.4, 45.9), box(47.4, 43.7, 48.1, 44.2)]   # Nosy Be; Volga-delta islands; Chechen Island
for k in ['sas', 'grm']:
    ps = C[k]['polys']; keep = [r for r in ps if not any(Polygon(r[0]).within(b) for b in DROP)]
    gone = [r for r in ps if r not in keep]
    print(k, 'dropped', len(gone), 'pieces', round(sum(A(Polygon(r[0])) for r in gone), 1), 'km2')
    old = C[k]['km2']; C[k]['polys'] = keep; C[k]['km2'] = km2of(keep)
    if k == 'sas' or k == 'grm':
        C[k]['states'] = [s for s in C[k]['states'] if s['n'] != 'Madagascar']
    print('  ', old, '->', C[k]['km2'])
M = lambda k: MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
print('me9 outside sas', round(A(M('me9').difference(M('sas').buffer(0.01)))), '| sas outside grm', round(A(M('sas').difference(M('grm').buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
