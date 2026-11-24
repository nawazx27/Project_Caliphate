"""Version 498 (Nawaz, the Wikipedia Umayyad Caliphate article; V4 held 27 of 31 key Umayyad places, missing Septimania (Narbonne, Carcassonne, Nimes,
719-759) and Kashgar (Qutayba's raid, c. 715): "I want all those lands in v4"). Added to V4 (CALIPH.me9): Septimania traced from the Wikipedia Septimania map he sent
("Trace this map exactly"; tools/v498_septimania_trace.py -> tools/data/v498_septimania_traced.geojson; the 5-department version was replaced), and the Kashgar oasis
as China's Kashgar Prefecture with the Kizilsu Kyrgyz Prefecture between it and Kyrgyzstan (the Version 138 shape, tools/data/kashgar_and_shore.geojson,
its Chinese part). V5, V6 and V7 already hold Septimania (Gaul) and V6, V7 Kashgar; V5 gets Kashgar too so it still holds V4.
DIR env = project dir. Run v386_areas_ellipsoid.py after."""
import json, os, subprocess, shapely
from shapely.geometry import shape, MultiPolygon, Polygon, Point, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from pyproj import Geod
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); P = os.environ.get('DIR') or HERE
A = lambda g: abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
SEP = shape(json.load(open(os.path.join(HERE, 'tools/data/v498_septimania_traced.geojson')))['geometry']).buffer(0).intersection(G['France'].buffer(0.003))   # "Trace this map exactly": his Wikipedia Septimania map (tools/v498_septimania_trace.py)
# the land left between it and Spain/Andorra (if the sketch stops short of the border) is filled, so no gap is left between Septimania and al-Andalus
SEP = unary_union([SEP, unary_union([SEP, G['Spain'], G['Andorra']]).buffer(0.08).buffer(-0.08).intersection(G['France']).difference(SEP)]).buffer(0)
KG = shape(json.load(open(os.path.join(HERE, 'tools/data/kashgar_and_shore.geojson')))['features'][0]['geometry']).buffer(0).intersection(G['China'].buffer(0.01))
print('Septimania', round(A(SEP)), 'km2 | Kashgar + Kizilsu', round(A(KG)), 'km2')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
for key, add in [('me9', [SEP, KG]), ('grm', [KG])]:
    polys = [Polygon(r[0], r[1:]) for r in C[key]['polys']]
    for a in add:
        near = [i for i, p in enumerate(polys) if box(*p.exterior.bounds).intersects(box(*a.buffer(0.5).bounds))]
        V = unary_union([polys[i].buffer(0) for i in near]) if near else Polygon()
        X = unary_union([V, a.buffer(0.003)]).buffer(0)
        X = unary_union([X] + [Polygon(h) for q in getattr(X, 'geoms', [X]) for h in q.interiors if A(Polygon(h)) < 2000]).buffer(0)
        X = shapely.set_precision(X, 0.001)
        new = []
        for q in getattr(X, 'geoms', [X]):
            if q.geom_type != 'Polygon' or A(q) < 0.02: continue
            q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 100]), 1.0)
            new.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
        keep = [C[key]['polys'][i] for i in range(len(polys)) if i not in near]
        C[key]['polys'] = keep + new; polys = [Polygon(r[0], r[1:]) for r in C[key]['polys']]
        print(key, 'added', round(A(X.difference(V)) if not V.is_empty else A(X)), 'km2')
    T = shapely.STRtree(polys)
    for n, p in {'Narbonne': (3.0, 43.18), 'Carcassonne': (2.35, 43.21), 'Nimes': (4.36, 43.84), 'Kashgar': (75.99, 39.47), 'Yarkand': (77.24, 38.42)}.items():
        print('  ', key, n, any(polys[i].contains(Point(p)) for i in T.query(Point(p))))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
