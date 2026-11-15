"""Every HYDE 3.3 time step (10,000 BCE to 2023): share of the standard Middle East's cropland inside V1.
Usage: python3 measure_all.py <project dir> <caliph.json>"""
import json, sys, subprocess, os, numpy as np, netCDF4
from shapely.geometry import shape, MultiPolygon, Polygon, mapping
from shapely.ops import unary_union
from rasterio.features import rasterize
from rasterio.transform import from_origin
P, CJ = sys.argv[1], sys.argv[2]; HERE = os.path.dirname(os.path.abspath(__file__))
geo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs'),t=require('./node_modules/topojson-client');const g=JSON.parse(fs.readFileSync('geo2.json'));process.stdout.write(JSON.stringify(t.feature(g,g.objects.countries)))"], cwd=P))
G = {f['properties']['n']: shape(f['geometry']).buffer(0) for f in geo['features'] if f.get('geometry')}
V1 = MultiPolygon([Polygon(r[0], r[1:]) for r in json.load(open(CJ))['shj']['polys']]).buffer(0)
STD = ['Egypt', 'Türkiye', 'Iran', 'Iraq', 'Syria', 'Lebanon', 'Jordan', 'Israel', 'Palestine', 'Cyprus', 'N. Cyprus', 'Saudi Arabia', 'Yemen', 'Oman',
       'United Arab Emirates', 'Qatar', 'Bahrain', 'Kuwait']
d = netCDF4.Dataset(os.path.join(HERE, 'cropland.nc')); lat = d.variables['lat'][:]; lon = d.variables['lon'][:]
north_first = lat[0] > lat[-1]
# window 25 W - 80 E, 0 - 50 N
li = np.where((lat > 0) & (lat < 50))[0]; lj = np.where((lon > -25) & (lon < 80))[0]
la, lo = lat[li], lon[lj]; step = abs(float(lat[1] - lat[0]))
top = float(la.max()) + step / 2 if True else 0; left = float(lo.min()) - step / 2
tr = from_origin(left, top, step, step); shp = (len(la), len(lo))
def mask(g):
    m = rasterize([(mapping(g), 1)], out_shape=shp, transform=tr, fill=0, dtype='uint8').astype(bool)
    return m if north_first else m[::-1]
mV1 = mask(V1); mS = mask(unary_union([G[n] for n in STD if n in G]))
units = d.variables['time'].units; T = netCDF4.num2date(d.variables['time'][:], units, calendar=getattr(d.variables['time'], 'calendar', 'standard'), only_use_cftime_datetimes=True)
C = d.variables['cropland']; worst = (101, None); rows = []
for k in range(len(T)):
    a = np.ma.filled(C[k, li[0]:li[-1] + 1, lj[0]:lj[-1] + 1], 0).astype(np.float64); a[a < 0] = 0
    tot = a[mS].sum(); ins = a[mS & mV1].sum(); pct = 100 * ins / tot if tot else 100.0
    y = T[k].year; lab = f'{-y + 1} BCE' if y <= 0 else f'{y} CE'
    rows.append((lab, tot, ins, pct)); worst = min(worst, (pct, lab))
for lab, tot, ins, pct in rows: print(f'{lab:>10s}  ME cropland {tot:11.0f} km2  inside V1 {ins:11.0f} km2  {pct:6.2f}%')
print('time steps:', len(rows), '| lowest share:', worst)
