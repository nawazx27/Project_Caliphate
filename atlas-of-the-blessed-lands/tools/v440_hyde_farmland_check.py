"""How much of the Middle East's historic cropland (HYDE 3.3, km2 of cropland per 5-arc-minute cell) lies inside V1 (CALIPH.shj)?
Usage: python3 measure.py <project dir> <caliph.json> ; reads cropland*.asc in this folder."""
import json, sys, subprocess, os, numpy as np
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from rasterio.features import rasterize
from rasterio.transform import from_origin
P, CJ = sys.argv[1], sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
C = json.load(open(CJ)); V1 = MultiPolygon([Polygon(r[0], r[1:]) for r in C['shj']['polys']]).buffer(0)
STD = ['Egypt', 'Türkiye', 'Iran', 'Iraq', 'Syria', 'Lebanon', 'Jordan', 'Israel', 'Palestine', 'Cyprus', 'N. Cyprus', 'Saudi Arabia', 'Yemen', 'Oman',
       'United Arab Emirates', 'Qatar', 'Bahrain', 'Kuwait']
WIDE = {'Libya': ['Libya'], 'Sudan': ['Sudan'], 'South Caucasus': ['Armenia', 'Azerbaijan', 'Georgia'], 'Afghanistan': ['Afghanistan'], 'Pakistan': ['Pakistan']}
CLASSIC = {'Tunisia (Ifriqiya)': ['Tunisia'], 'Algeria + Morocco': ['Algeria', 'Morocco'], 'Uzbekistan (Transoxiana)': ['Uzbekistan'], 'Turkmenistan (Merv)': ['Turkmenistan']}
missing = [n for n in STD + sum(WIDE.values(), []) + sum(CLASSIC.values(), []) if n not in G]
if missing: print('not in base map:', missing)
tr = from_origin(-180, 90, 1 / 12, 1 / 12); W, H = 4320, 2160
# work in a window round the region (25 W - 80 E, 0 - 50 N) to keep memory small
c0, c1, r0, r1 = int((-25 + 180) * 12), int((80 + 180) * 12), int((90 - 50) * 12), int((90 - 0) * 12)
wtr = from_origin(-25, 50, 1 / 12, 1 / 12); shp = (r1 - r0, c1 - c0)
def mask(g): return rasterize([(mapping(g), 1)], out_shape=shp, transform=wtr, fill=0, dtype='uint8', all_touched=False).astype(bool)
mV1 = mask(V1)
groups = {'Standard Middle East (17 countries)': STD}
groups.update({k: v for k, v in WIDE.items()}); groups.update(CLASSIC)
gm = {k: mask(unary_union([G[n] for n in v if n in G])) for k, v in groups.items()}
cm = {n: mask(G[n]) for n in STD if n in G}
out = {}
for yr in ['1000BC', '0AD', '1000AD', '1700AD']:
    a = np.loadtxt(os.path.join(HERE, f'cropland{yr}.asc'), skiprows=6, dtype=np.float32)[r0:r1, c0:c1]
    a[a < 0] = 0
    print(f'\n=== {yr} ===')
    for k, m in gm.items():
        tot = a[m].sum(); ins = a[m & mV1].sum()
        print(f'  {k:38s} cropland {tot:10.0f} km2 | inside V1 {ins:10.0f} km2 = {100 * ins / tot if tot else 0:5.1f}%')
    std = gm['Standard Middle East (17 countries)']; outside = a * (std & ~mV1)
    print(f'  standard-ME cropland outside V1: {outside.sum():.0f} km2 (border cells of the 5-minute grid)')
    for n, m in cm.items():
        t = a[m].sum(); o = a[m & ~mV1].sum()
        if t and o / t > 0.01: print(f'     {n}: {o:.0f} of {t:.0f} km2 outside ({100 * o / t:.1f}%)')
    out[yr] = a
np.save(os.path.join(HERE, 'mV1.npy'), mV1); np.save(os.path.join(HERE, 'std.npy'), gm['Standard Middle East (17 countries)'])
np.save(os.path.join(HERE, 'crop1000AD.npy'), out['1000AD'])
