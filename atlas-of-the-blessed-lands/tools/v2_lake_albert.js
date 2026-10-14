/* Version 143 (2026-10-14, Nawaz: "sure"). Lake Albert's DR Congo half (tools/data/lake_albert_drc.geojson, from
   tools/lake_albert.py) added to V2 and V2-B, so the whole lake the Nile passes through is inside; row 180_A after Uganda.
   Run: node tools/v2_lake_albert.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const NEW = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/lake_albert_drc.geojson'))).features[0];
const KM = 6371.0088**2, DRC_KM2 = 2344858;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const poly of R3mp(asMp(NEW.geometry))) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  const add = V.km2 - before;
  V.states = V.states.filter(r => r.id !== '180_A');
  const i = V.states.findIndex(r => String(r.id) === '800');
  V.states.splice(i + 1, 0, {id: '180_A', n: 'DR Congo: the western half of Lake Albert (water the Nile passes through)', km2: add,
                             pct: Math.round(add / DRC_KM2 * 1000) / 10});
  console.log(k, before, '->', V.km2, '(+', add, ') failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
