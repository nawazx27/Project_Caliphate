/* Version 117 (2026-10-13, Nawaz: "Fill these gaps... don't keep such gaps in between lands, from now").
   Adds the pieces marked fill in tools/data/gaps_<v>.geojson (made by tools/fill_gaps.py) to each version, piece by piece.
   Run: node tools/v2_fill_gaps.js [versions, default x,xb,xn]; then node tools/v2_ca_frontiers.js rows to recount the rows. */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
for (const k of (process.argv[2] || 'x,xb,xn').split(',')) {
  const V = C[k], before = V.km2;
  const ADD = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', `gaps_${k}.geojson`))).features.filter(f => f.properties.fill);
  let X = R3mp(V.polys), n = 0, fail = 0;
  for (const f of ADD) for (const poly of R3mp(asMp(f.geometry))) { try { X = R3mp(pc.union(X, [poly])); n++; } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') pieces', n, 'failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
