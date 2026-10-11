/* Version 82 (2026-10-11, Nawaz: "Include the Caspian water in Khorasan too").
   The Greater Khorasan outline traced from reference/transoxiana_khwarazm_khorasan.webp (tools/data/transoxiana_trace.json, 'khorasan')
   runs out over the south-east Caspian (Gorgan Bay and the Turkmen shore, about 4,700 km² of water). The outlines were land only, so
   that water was outside. It is now added to every version that holds all of Khorasan's land: V2 (x), V5 (x3), V6 (v2) and V7 (g).
   The version areas now count that water. Run: node tools/khorasan_caspian.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KH = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/transoxiana_trace.json'))).khorasan;
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const T = R3mp([[KH]]);
for (const k of ['x', 'x3', 'v2', 'g']) {
  const V = C[k], before = V.km2, water = area(R3mp(pc.difference(T, R3mp(V.polys))));
  let X = R3mp(pc.union(R3mp(V.polys), T));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => s.id !== 'CAS_K');
  V.states.push({id:'CAS_K', n:'Caspian Sea: the Khorasan shore (Gorgan Bay and the Turkmen coast), as the author’s Khorasan map draws it (water)', km2:water, pct:null});
  V.states.sort((a, b) => b.km2 - a.km2);
  V.khorasanCaspian = 'Version 82: the Caspian water inside the traced Khorasan outline (Nawaz)';
  console.log(k, before, '->', V.km2, '| water', water, '| still outside', area(R3mp(pc.difference(T, X))));
}
fs.writeFileSync(F, JSON.stringify(C));
