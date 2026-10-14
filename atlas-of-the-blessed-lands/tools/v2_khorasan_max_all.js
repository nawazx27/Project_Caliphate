/* Version 136 (2026-10-14, Nawaz: "Don't leave anything out… widest and max!!!"). Adds tools/data/khorasan_max.geojson
   (tools/khorasan_max.py) to V2 (CALIPH.x); V2-B then takes V2's Central Asia with tools/v2b_khorasan_from_v2.js.
   Run: node tools/v2_khorasan_max_all.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const NEW = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/khorasan_max.geojson'))).features[0];
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
for (const k of ['x']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const poly of R3mp(asMp(NEW.geometry))) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
