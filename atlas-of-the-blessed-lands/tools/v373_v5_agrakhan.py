"""Version 373 PREVIEW (redrawn after his second circle: "I meant only that" = only the Agrakhan spit and Chechen Island, not the mainland shore). (Nawaz, on a screenshot of V5 after Version 371, circled in red the coast north of Makhachkala: the Agrakhan peninsula,
the shore of the Agrakhan Bay and Chechen Island: "Fill"). The circle, georeferenced on the screenshot (Mercator fitted on Batumi and Baku,
checked on Tbilisi, Yerevan and Aktau to 0.04 deg), is tools/data/v373_agrakhan_circle.geojson. V5 (grm) and V6 (sup) take all Russian land
inside it. On the live V5 (the Version 372 Caspian-line preview is separate). DIR env = project dir (preview: a copy)."""
import json, os, subprocess, math, shapely, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, Point, mapping
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['id']: (f['properties']['n'], shape(f['geometry']).buffer(0)) for f in geo['features'] if f.get('geometry')}
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
MP = lambda pl: MultiPolygon([Polygon(r[0], r[1:]) for r in pl]).buffer(0)
def km2of(out):
    return int(subprocess.check_output(['node', '-e', """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""], cwd=P, input=json.dumps(out).encode()))
def polys(X, mn=0.05):
    X = shapely.set_precision(X, 0.001); out = []
    for q in getattr(X, 'geoms', [X]):
        if q.geom_type != 'Polygon' or A(q) < mn: continue
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    return out
CI = shape(json.load(open(os.path.join(HERE, 'tools/data/v373_agrakhan_circle.geojson')))['geometry'])
# only the spit and the island: cut off the mainland west of the Agrakhan Bay along the bay's middle (base-map water), then south to the Sulak mouth
CUT = [(47.2, 44.05), (47.42, 43.92), (47.497, 43.88), (47.475, 43.84), (47.519, 43.80), (47.498, 43.76), (47.47, 43.72), (47.476, 43.68), (47.444, 43.64),
       (47.422, 43.60), (47.422, 43.56), (47.428, 43.52), (47.44, 43.48), (47.462, 43.42), (47.48, 43.36), (47.49, 43.28), (47.2, 43.28)]
W = CI.intersection(G['643'][1]).difference(Polygon(CUT))
def add(key):
    V = MP(C[key]['polys']); a = W.difference(V); print('  +', key, round(A(a)), 'km2')
    for g in sorted(getattr(a, 'geoms', [a]), key=lambda g: -A(g))[:5]:
        if A(g) > 1: print('     piece', round(A(g)), 'km2 at', [round(c, 2) for c in g.representative_point().coords[0]])
    X = unary_union([V, W.buffer(0.002)]).buffer(0); o = polys(X, 0.02); Y = MP(o); rws = []
    for k, (n, g) in G.items():
        if g.area and g.intersects(Y):
            pct = round(100 * g.intersection(Y).area / g.area)
            if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
    old = C[key]['km2']; C[key] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print(key, old, '->', C[key]['km2']); return Y
Y5 = add('grm'); Y6 = add('sup')
for n_, p in {'Agrakhan peninsula': (47.62, 43.75), 'Chechen Island': (47.75, 43.97), 'Agrakhan spit middle': (47.52, 43.6), 'mainland west of the bay (out)': (47.33, 43.6), 'Kizlyar (out, west of the circle)': (46.71, 43.85), 'Makhachkala': (47.5, 42.98)}.items():
    print('  ', n_, Y5.contains(Point(p)), round(Y5.distance(Point(p)) * 111, 1), 'km')
print('grm outside sup', round(A(Y5.difference(Y6.buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
