"""Version 405 PREVIEW (Nawaz, on a Wikipedia map of Kuwait with the hatched former Saudi-Kuwaiti Neutral Zone: "Extend Kuwait until here"). V1 (shj) gets the whole of
Kuwait (with Bubiyan, Warbah and Faylakah) and the southern (Saudi) half of the former Neutral Zone down to the hatch's southern edge, read off
tools/data/v405_kuwait_map.webp and fitted on Kuwait's own corners. DIR env = project dir (preview: a copy). Run v386_areas_ellipsoid.py after."""
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
# the map (tools/data/v405_kuwait_map.webp, displayed 1828 px wide; these pixel positions are in that display, x1.0503 = file pixels), fitted affinely on Kuwait's own corners
CP = [((80, 1148), (46.533, 29.096)), ((945, 1640), (47.721, 28.534)), ((1490, 1625), (48.433, 28.541)), ((1160, 920), (47.978, 29.375)), ((893, 937), (47.658, 29.337))]
P_ = np.array([p for p, _ in CP], float); L_ = np.array([l for _, l in CP], float); M = np.c_[np.ones(len(P_)), P_]
ax, *_ = np.linalg.lstsq(M, L_[:, 0], rcond=None); ay, *_ = np.linalg.lstsq(M, L_[:, 1], rcond=None)
print('fit error km', [round(float(np.hypot((M @ ax - L_[:, 0])[i] * 97, (M @ ay - L_[:, 1])[i] * 111)), 1) for i in range(len(P_))])
ll = lambda pts: [(ax[0] + ax[1] * x + ax[2] * y, ay[0] + ay[1] * x + ay[2] * y) for x, y in pts]
# the hatched former Saudi-Kuwaiti Neutral Zone south of Kuwait's border (its Saudi half), closed through the sea
NZ = Polygon(ll([(945, 1640), (960, 1700), (1010, 1760), (1060, 1830), (1100, 1890), (1640, 1890), (1900, 1890), (1900, 1600), (1490, 1600), (945, 1600)])).buffer(0)
cid = lambda n: [k for k, (nm, g) in G.items() if nm == n][0]
LAND = unary_union([g for n, g in G.values()]).buffer(0.005)
W = {'Kuwait (whole, with Bubiyan, Warbah and Faylakah)': G[cid('Kuwait')][1], 'the former Neutral Zone, its southern (Saudi) half': NZ.intersection(LAND)}
V = MP(C['shj']['polys']); run = V
for n, g in W.items(): print('   shj +', n, round(A(g.difference(run))), 'km2'); run = unary_union([run, g.buffer(0.003)])
X = run.buffer(0)
holes = [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) > 0.5]
for h in holes: print('     enclosed pocket closed:', round(A(h)), 'km2 at', [round(c, 1) for c in h.representative_point().coords[0]])
o = polys(unary_union([X] + holes).buffer(0).intersection(MP(C['me2']['polys']).buffer(0.002)), 0.02); Y = MP(o); rws = []
for k, (n, g) in G.items():
    if g.area and g.intersects(Y):
        pct = round(100 * g.intersection(Y).area / g.area)
        if pct >= 1: rws.append({'id': k, 'n': n, 'km2': round(A(g)), 'pct': pct})
old = C['shj']['km2']; C['shj'] = {'polys': o, 'km2': km2of(o), 'states': sorted(rws, key=lambda r: -r['km2'] * r['pct'])}; print('shj', old, '->', C['shj']['km2'])
for n_, p in {'Kuwait City': (47.98, 29.37), 'Bubiyan': (48.25, 29.8), 'Faylakah': (48.34, 29.43), 'Al-Wafrah': (47.93, 28.64), 'Nuwaiseeb': (48.40, 28.56), 'Khafji (Neutral Zone)': (48.49, 28.43), 'Hafar al-Batin (out)': (45.97, 28.43), 'Jubail (out)': (49.66, 27.01)}.items():
    print('  ', n_, Y.contains(Point(p)), round(Y.distance(Point(p)) * 105, 1), 'km')
print('shj outside me2', round(A(Y.difference(MP(C['me2']['polys']).buffer(0.01)))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
