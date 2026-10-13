"""Version 117 (2026-10-13, Nawaz, with screenshots of the Talas valley and of Khwarazm and the Aral: "Fill these gaps... don't keep
such gaps in between lands, from now"). Finds land left outside a version in pockets and narrow bays between parts of it: the
version closed by R degrees (about 50 km), minus the version, on land (geo2) and not in lakes (lakes.geojson). A piece is filled when
  - it lies in Central Asia (55-80 E, 35-48 N) and at least 70% of its edge touches the version (the Talas valley, the pockets west of
    the Amu Darya round Khiva, the dry Aral bed, the wedges between the Syr Darya and the Karatau, the Tashkurgan pocket), or
  - it is a sliver of at most 20 km2 with at least 95% of its edge on the version (anywhere).
Other bends (rivers, borders elsewhere) are listed for Nawaz, not filled. My method; Nawaz's rule.
Run: python3 tools/fill_gaps.py [versions, default x,xb,xn] → tools/data/gaps_<v>.geojson; then node tools/v2_fill_gaps.js"""
import json, os, subprocess, sys, pyproj
from shapely.geometry import shape, MultiPolygon, Polygon, box, mapping
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
G = pyproj.Geod(ellps='WGS84'); A = lambda g: abs(G.geometry_area_perimeter(g)[0]) / 1e6
R = 0.5; CA = box(55, 35, 80, 48)
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = unary_union([shape(f['geometry']).buffer(0) for f in geo['features']])
lakes = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features']])
C = json.load(open(os.path.join(P, 'src/caliph.json')))
for k in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['x', 'xb', 'xn']):
    m = MultiPolygon([Polygon(p[0], p[1:]) for p in C[k]['polys']]).buffer(0)
    gap = m.buffer(R, quad_segs=4).buffer(-R, quad_segs=4).difference(m).intersection(land).difference(lakes)
    mb = m.buffer(0.005); fill, other = [], []
    for g in getattr(gap, 'geoms', [gap]):
        if g.geom_type != 'Polygon': continue
        a = A(g)
        if a < 1: continue
        t = g.boundary.intersection(mb).length / g.boundary.length
        if (CA.contains(g.representative_point()) and t >= 0.7) or (a <= 20 and t >= 0.95): fill.append((a, t, g))
        else: other.append((a, t, g))
    feats = [{'type': 'Feature', 'properties': {'v': k, 'km2': round(a, 1), 'touch': round(t, 2), 'fill': True}, 'geometry': mapping(g)} for a, t, g in fill]
    feats += [{'type': 'Feature', 'properties': {'v': k, 'km2': round(a, 1), 'touch': round(t, 2), 'fill': False}, 'geometry': mapping(g)} for a, t, g in other if a >= 50 and t >= 0.6]
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(H, 'data', f'gaps_{k}.geojson'), 'w'))
    print(k, 'filled', len(fill), round(sum(a for a, _, _ in fill)), 'km2; listed, not filled', sum(1 for f in feats if not f['properties']['fill']), round(sum(f['properties']['km2'] for f in feats if not f['properties']['fill'])), 'km2', flush=True)
