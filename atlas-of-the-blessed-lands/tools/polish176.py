"""Version 176 (part; Nawaz: "make the atlas more accurate and beautiful", he chose an accuracy audit and cleaner outline edges among
others). One pass over all six outlines (CALIPH keys me, me2, xb, x, x3, v2 = V1–V6), in this order:
 1. Junk: three-cornered specks of a few metres left in the sea by the 0.001° grid (no land under them) are dropped. Real islands
    are kept, also the traced Kastellorizo group (Megisti, Ro, Strongyli, Psomi), which the base map does not draw.
 2. Cleaner inland edges: a morphological close (radius RC = 0.015°) fills slits, hairline notches and stair-step corners narrower
    than about 3 km. Only pieces lying wholly on land more than INL (0.03°) from the base map's coast and under ADD_MAX km² are
    filled; a notch whose outside reaches the sea within about 30 km is taken for a bay or an inlet and kept as drawn (e.g. the
    Caspian arm on the Buzachi peninsula); nothing is added on the land of a country the outline does not list at all, nor on DR
    Congo's land beyond Lake Albert (the author's shore line). Spikes are NOT cut: a trial with a morphological open (RO) cut the
    necks of towns taken whole (e.g. by Gorizia), so RO = 0 (the code is kept, off). Nothing is ever cut from a land listed whole.
 3. Overshoot: where the outline runs along the border of a country it does not list at all, a hairline strip (narrower than about
    1 km) reaching further into that country than the 0.003° (~300 m) margin that Version 145 keeps past borders on purpose (so the
    0.001° grid leaves no sliver of held land outside) is cut back to that margin. Bumps wider than that are kept (towns taken whole
    under the Version 145 rule, Siachen, Baikonur), and a cut that would split a piece off is not made.
 4. A land listed whole (rows at 100%, by base-map unit) of which more than 0.1% lay outside, and any part of the standing lands
    (the whole of Lake Albert, the whole island of Cyprus, Azerbaijan, Georgia, Armenia) outside, is put back: the missing part,
    buffered 0.003° as in Version 145. Smaller coastal differences between the coarse base map and the finer outline coasts are left.
 5. Snapped to the 0.001° grid (shapely union_all grid_size=0.001). Snapping can shave a few metres off listed land along long
    straight edges, so whatever of a listed land was inside before and is not now is put back (buffered 0.0006°, up to four
    rounds). Loose specks under 0.05 km² left by the steps above are dropped; holes under 5,000 km² filled; km2 recounted
    (d3.geoArea × 6371.0088², as the other tools). Rows: Baikonur added to V6 (it held it whole without a row), Siachen's part to
    V3 and V4 (held, without a row).
Saves src/caliph.json compactly via tmp + os.replace. Prints every change with its place. Run from the original Version 175 data:
python3 tools/polish176.py (running it twice would smooth twice)."""
import json, os, subprocess, shapely, shapely.prepared
from shapely.geometry import shape, Polygon, MultiPolygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pyproj import Geod
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GD = Geod(ellps='WGS84')
A = lambda g: abs(GD.geometry_area_perimeter(g)[0]) / 1e6
RC, RO, INL, ADD_MAX, REM_MAX = 0.015, 0.0, 0.03, 50.0, 2.0
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {str(f['id']): shape(f['geometry']).buffer(0) for f in geo['features']}
NM = {str(f['id']): f['properties']['n'] for f in geo['features']}
LAND = unary_union(list(G.values()))
INLAND = LAND.buffer(-INL)
INP = shapely.prepared.prep(INLAND)
LANDP = shapely.prepared.prep(LAND.buffer(0.001))
LA = unary_union([shape(f['geometry']).buffer(0) for f in json.load(open(os.path.join(P, 'lakes.geojson')))['features'] if f['properties'].get('name') == 'Lake Albert'])
CYB = box(32.2, 34.5, 34.7, 35.75)
CY = unary_union([g.intersection(CYB) for g in G.values() if g.intersects(CYB)])
CY_IDS = {'196', 'CYN', 'CNM', 'ESB', 'WSB', 'CYP'}
KAST = box(29.45, 36.05, 29.7, 36.2)          # Kastellorizo, Ro, Strongyli, Psomi (traced; not on the base map)
DRC = G['180'].difference(LA)               # DR Congo beyond Lake Albert: only its lake half (or the author's shore line) is held
STANDING = {'Lake Albert': LA, 'Cyprus': CY, 'Azerbaijan': G['031'], 'Georgia': G['268'], 'Armenia': G['051']}
D3 = """const d3=require('./node_modules/d3'),fs=require('fs');const C=JSON.parse(fs.readFileSync(0));
const s=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)};
process.stdout.write(String(Math.round(C.reduce((t,p)=>t+s(p[0])-p.slice(1).reduce((h,r)=>h+s(r),0),0)*6371.0088**2)))"""
at = lambda g: '%.2f°E %.2f°N' % g.representative_point().coords[0]
polys = lambda g: [q for q in getattr(g, 'geoms', [g]) if q.geom_type == 'Polygon' and not q.is_empty]
def pieces(g, lo, hi=1e18):
    return [q for q in polys(g) if lo <= A(q) < hi]
def ncomp(g):
    return len(polys(g))

F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
NEW_ROWS = {'v2': [{'id': 'KAB', 'n': 'Baikonur (Kazakh land leased to Russia)', 'km2': round(A(G['KAB'])), 'pct': 100, 'core': True}]}
for k, n in (('me', 'V1'), ('me2', 'V2'), ('xb', 'V3'), ('x', 'V4'), ('x3', 'V5'), ('v2', 'V6')):
    rows = C[k]['states'] + NEW_ROWS.get(k, [])
    km_before = C[k]['km2']
    parts = [shapely.make_valid(Polygon(r[0], r[1:])) for r in C[k]['polys']]
    print('==', n, k, km_before, 'km2,', len(parts), 'pieces')
    # 1. junk specks
    keep = []
    for p in parts:
        a = A(p)
        if len(p.exterior.coords) <= 4 and a < 0.1 and not p.intersects(KAST) and A(p.intersection(LAND)) < 0.3 * a:
            print('   junk speck removed at', at(p), round(a, 3), 'km2'); continue
        keep.append(p)
    X = unary_union(keep)
    ids = {s for r in rows for s in r['id'].split('_')} | CY_IDS
    if any(r['id'] == '398' or r['id'].startswith('398') for r in rows): ids.add('KAB')
    if k in ('xb', 'x'): ids.add('KAS')       # Siachen: held in part, a row is added below
    X0 = X
    whole = {}
    for r in rows:
        if r.get('pct') != 100: continue
        if r['id'] in G: whole[r['n']] = G[r['id']]
        elif r['id'] == 'CYP': whole[r['n']] = CY
    WH = unary_union(list(whole.values()) + list(STANDING.values()))
    miss0 = {nm: A(g.difference(X0)) for nm, g in list(whole.items()) + list(STANDING.items())}
    env = X.envelope.buffer(1)
    U = unary_union([g for i, g in G.items() if i not in ids and g.intersects(env)])
    LISTED = unary_union([G[i] for i in ids if i in G])
    # 2. smoothing, inland only
    Xc = X.buffer(RC, 4).buffer(-RC, 4)
    add = Xc.difference(X).difference(U).difference(DRC)
    add = [q for q in polys(add) if q.area > 4e-7 and INP.contains(q.buffer(-1e-6))]   # a notch that reaches a coast is a bay or an inlet: kept
    def opens_on_sea(q):              # the outside land next to a notch reaches the sea within ~30 km: an inlet, not a notch
        bx = q.envelope.buffer(0.3)
        out_ = [c for c in polys(bx.difference(X)) if c.distance(q) < 1e-6]
        return any(not LANDP.contains(c) for c in out_)
    addp = [q for q in add if 0.005 <= A(q) < ADD_MAX and (A(q) < 1 or not opens_on_sea(q))]
    big = [q for q in add if A(q) >= ADD_MAX]
    for q in big: print('   not filled (wider than a notch):', at(q), round(A(q)), 'km2')
    remp = []
    if RO > 0:
        Xo = X.buffer(-RO, 4).buffer(RO, 4)
        rem = [q for q in polys(X.difference(Xo).difference(WH).difference(DRC).difference(U)) if q.area > 4e-7 and INP.contains(q.buffer(-1e-6))]
        remp = pieces(unary_union(rem), 0.005, REM_MAX) if rem else []
    sa, sr = sum(map(A, addp)), sum(map(A, remp))
    print('   smoothing: %d notches/slits filled, %.1f km2; %d spikes cut, %.1f km2' % (len(addp), sa, len(remp), sr))
    for q in sorted(addp, key=A)[-6:]: print('      filled %.1f km2 at %s' % (A(q), at(q)))
    for q in sorted(remp, key=A)[-4:]: print('      cut %.2f km2 at %s' % (A(q), at(q)))
    Xn = shapely.union_all([X.difference(unary_union(remp)), *addp])
    # a cut must not split a piece off (e.g. a town joined by a thin neck): put back the cuts next to any piece split off
    orig = polys(X); tree = shapely.STRtree(orig); best = {}; comps = polys(Xn)
    for c in comps:
        o = max(tree.query(c), key=lambda i: orig[i].intersection(c).area, default=None)
        if o is not None and (o not in best or c.area > best[o].area): best[o] = c
    keepers = {id(c) for c in best.values()}
    loose = [c for c in comps if id(c) not in keepers]
    if loose and remp:
        rt = shapely.STRtree(remp); back = set()
        for c in loose:
            for i in rt.query(c.buffer(1e-6)): back.add(int(i))
        if back:
            print('   %d cuts undone so no piece is split off' % len(back))
            remp = [r for i, r in enumerate(remp) if i not in back]
            Xn = shapely.union_all([X.difference(unary_union(remp)), *addp]) if remp else shapely.union_all([X, *addp])
    # a filled pocket that does not join the outline (it met it only at a corner) is not kept
    lone = [c for c in polys(Xn) if all(orig[i].intersection(c).area < 1e-9 for i in tree.query(c))]
    if lone:
        print('   %d filled pockets that met the outline only at a corner left out (%.2f km2)' % (len(lone), sum(map(A, lone))))
        Xn = Xn.difference(unary_union([q.buffer(1e-7) for q in lone]))
    X = Xn
    # 3. hairline overshoot into countries not listed at all
    O = X.intersection(U)
    thin = O.difference(O.buffer(-0.005, 4).buffer(0.005, 4)).intersection(LISTED.buffer(0.012)).difference(LISTED.buffer(0.0035, 4))
    cut, tot = [], 0.0
    for t in pieces(thin, 0.01):
        L = GD.geometry_area_perimeter(t)[1] / 2e3
        if L < 1: continue
        loc = t.envelope.buffer(0.05)
        if ncomp(X.intersection(loc).difference(t)) > ncomp(X.intersection(loc)): continue
        cut.append(t); tot += A(t)
    if cut:
        X = X.difference(unary_union(cut))
        byc = {}
        for t in cut:
            c = max((i for i in G if i not in ids and G[i].intersects(t)), key=lambda i: G[i].intersection(t).area, default='?')
            byc.setdefault(NM.get(c, c), []).append(A(t))
        print('   overshoot cut back to the border: %.1f km2 in %d strips:' % (tot, len(cut)), '; '.join('%s %.1f' % (c, sum(v)) for c, v in sorted(byc.items(), key=lambda kv: -sum(kv[1]))))
    # 4. lands listed whole that are not >= 99.9% inside, and the standing lands, put back whole
    fill = []
    for nm, g in {**whole, **STANDING}.items():
        miss = g.difference(X); m = A(miss)
        if m > 0.01 and (nm in STANDING or m / A(g) > 0.001):
            fill.append(shapely.set_precision(miss.buffer(0.003, 4), 0.001))
            print('   put back %s: %.2f km2 (was %.3f%% inside)' % (nm, m, 100 - m / A(g) * 100))
    X = shapely.union_all([shapely.make_valid(X), *fill], grid_size=0.001)
    # snapping to the grid may shave a few metres off listed land along long edges: put back what was inside before
    for it in range(4):
        back = []
        for nm, g in list(whole.items()) + list(STANDING.items()):
            lost = [q for q in polys(g.intersection(X0).difference(X)) if A(q) > 0.0005]
            if lost: back.append(shapely.set_precision(unary_union(lost).buffer(0.0006, 2), 0.001))
        if not back: break
        X = shapely.union_all([X, *back], grid_size=0.001)
    specks = [q for q in polys(X) if A(q) < 0.05 and not q.intersects(KAST) and A(q.intersection(WH)) < 0.001 and not any(A(q.intersection(p0)) > 0.5 * A(q) for p0 in polys(X0) if A(p0) < 1)]
    if specks:
        print('   %d specks of under 0.05 km2 left loose by the steps above dropped (%.3f km2)' % (len(specks), sum(map(A, specks))))
        X = MultiPolygon([q for q in polys(X) if q not in specks])
    out = []
    for q in polys(X):
        q = orient(Polygon(q.exterior, [h for h in q.interiors if A(Polygon(h)) >= 5000]), 1.0)
        out.append([[[round(u, 3), round(v, 3)] for u, v in rr.coords] for rr in [q.exterior, *q.interiors]])
    C[k]['polys'] = out
    C[k]['km2'] = int(subprocess.check_output(['node', '-e', D3], cwd=P, input=json.dumps(out).encode()))
    XF = MultiPolygon([Polygon(r[0], r[1:]) for r in out]).buffer(0)
    for nm, g in list(whole.items()) + list(STANDING.items()):
        m = A(g.difference(XF)); pct = 100 - m / A(g) * 100
        if m > miss0[nm] + 0.05 or pct < 99.9 or (nm in STANDING and pct < 99.99): print('   CHECK', nm, 'outside %.2f km2 (before %.2f), %.3f%% inside' % (m, miss0[nm], pct))
    # rows
    for r in NEW_ROWS.get(k, []):
        if not any(s['id'] == r['id'] for s in C[k]['states']): C[k]['states'].append(r); print('   row added:', r['n'], r['km2'], 'km2')
    if k in ('xb', 'x') and not any(s['id'] == 'KAS' for s in C[k]['states']):
        s = A(G['KAS'].intersection(XF))
        if s > 1:
            C[k]['states'].append({'id': 'KAS', 'n': 'Siachen Glacier (held by India, claimed by Pakistan): the part inside the outline', 'km2': round(s), 'pct': round(s / A(G['KAS']) * 100, 1)})
            print('   row added: Siachen Glacier', round(s), 'km2')
    print('   %s: %d -> %d km2 (%+d), %d pieces' % (n, km_before, C[k]['km2'], C[k]['km2'] - km_before, len(out)))
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
