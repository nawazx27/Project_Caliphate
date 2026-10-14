"""Version 140 (2026-10-14, Nawaz, on a screenshot of V2 showing a hole south of Issyk-Kul: "Why is there a gap here?"). A hole fully
enclosed by a version's land is a gap under the standing rule, but tools/fill_gaps.py only looks at pockets on the outer edge (and the
tools keep holes of 5,000 km² or more on purpose, for seas and lakes). So: every interior ring (hole) of V2 and V2-B that is mostly land
(geo2) is removed, i.e. filled. Found: the Naryn region of Kyrgyzstan (about 28,000 km²), left when Version 139 joined Farghāna, the Chu
valley with Issyk-Kul, and Kashgar. Run: python3 tools/fill_enclosed.py [x,xb]"""
import json, os, sys, subprocess, pyproj
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
H = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(H)
A = lambda g: abs(pyproj.Geod(ellps='WGS84').geometry_area_perimeter(g)[0]) / 1e6
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
land = [shape(f['geometry']).buffer(0) for f in geo['features']]
F = os.path.join(P, 'src', 'caliph.json'); C = json.load(open(F))
for k in (sys.argv[1] if len(sys.argv) > 1 else 'x,xb').split(','):
    V = C[k]; added = 0
    for p in V['polys']:
        keep = [p[0]]
        for r in p[1:]:
            h = Polygon(r); a = A(h)
            l = sum(A(g.intersection(h)) for g in land if g.intersects(h))
            if l > 0.5 * a: added += a; print(k, 'filled hole', round(a), 'km2 at', round(h.centroid.x, 2), round(h.centroid.y, 2)); continue
            keep.append(r)
        p[:] = keep
    V['km2'] = round(V['km2'] + added); print(k, '->', V['km2'])
json.dump(C, open(F, 'w'), separators=(',', ':'), ensure_ascii=False)
