"""Version 427 (Nawaz's Apple Maps screenshot of the Kharg Islands): Kharku (Khargu), the small island north-east of Kharg, is missing from Natural Earth and the
base map. Drawn from his screenshot (scaled on Kharg Island's known extent): a thin island ~5 km long from ~50.333 E 29.301 N to ~50.360 E 29.343 N.
Added to CALIPH.extraLand (so it is drawn as land) and to every outline that holds Iran (V2-V6) and to V1. Run after tools/v427_v1_bahrain_kharg.py."""
import json, os, subprocess, numpy as np
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
P = os.environ.get('DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
a = np.array([50.333, 29.301]); b = np.array([50.360, 29.343]); ax = (b - a) / np.linalg.norm(b - a); nx = np.array([-ax[1], ax[0]])
t = np.linspace(0, 1, 24); w = 0.0032 * np.sqrt(np.clip(np.sin(np.pi * t), 0, 1)) + 0.0004
pts = [tuple(a + (b - a) * ti + nx * wi) for ti, wi in zip(t, w)] + [tuple(a + (b - a) * ti - nx * wi) for ti, wi in zip(t[::-1], w[::-1])]
KU = orient(Polygon(pts).buffer(0), 1.0)
ring = [[round(x, 4), round(y, 4)] for x, y in KU.exterior.coords]
C['extraLand']['polys'].append([ring])
if 'Kharku' not in C['extraLand']['n']: C['extraLand']['n'] += '; Kharku (Khargu) island drawn from Apple Maps (Version 427)'
def km2of(o):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(o).encode()))
for k in ['shj', 'me2', 'me9', 'grm', 'tib', 'sup']:
    V = MultiPolygon([Polygon(r[0], r[1:]) for r in C[k]['polys']]).buffer(0)
    if V.contains(KU.buffer(-0.0002)): print(k, 'already'); continue
    C[k]['polys'].append([ring]); C[k]['km2'] = km2of(C[k]['polys']); print(k, 'Kharku added')
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
