/* Version 130 (2026-10-14). On a phone screenshot of V2 Nawaz drew a black line across Kazakhstan from the Caspian's bay north of the
   Buzachi peninsula to the outline east of the Aral; asked what it meant, he chose "Make it the new border": everything north of the line
   goes out of V2 and V2-B, everything south stays. The line (tools/data/kz_border_line130.json) was placed from the screenshot's
   graticule (45 N at y 1160, 50 N at y 545, 55 E at x 252; 83.2 px per degree): 53.11 E 45.61 N - 55.10 E 46.51 N - 57.98 E 47.17 N -
   60.39 E 47.25 N - 63.03 E 47.18 N. Taken out: the land north of it, a polygon from just west of the line's start (52.6 E 45.45 N,
   which keeps the Buzachi peninsula in) north to 52 N. Row 398_K is recounted by: node tools/v2_ca_frontiers.js rows.
   Run: node tools/v2_kz_border_line.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const LINE = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/kz_border_line130.json')));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const ring = [[52.6, 45.45], ...LINE, [LINE[LINE.length-1][0], 52], [46, 52], [46, 45.45], [52.6, 45.45]];
const NORTH = d3.geoArea({type:'Polygon', coordinates:[ring]}) > 2*Math.PI ? [[ring.slice().reverse()]] : [[ring]];
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(pc.difference(R3mp(V.polys), R3mp(NORTH)));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
  V.polys = X; V.km2 = area(X);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ')');
}
fs.writeFileSync(F, JSON.stringify(C));
