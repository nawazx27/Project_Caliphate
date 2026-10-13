/* Version 114 (2026-10-13, Nawaz: the whole Greater Caucasus in V2; his final choice: down to the northern foot of the mountains, so the line looks like Georgia's and Azerbaijan's border further up;
   V2, V2-B and V2N). Adds the pieces of tools/data/greater_caucasus.geojson (made by tools/greater_caucasus.py) piece by piece.
   Row 643_GC (the range down to the foot of its mountains, Nawaz's final choice). Run: node tools/v2_greater_caucasus.js
   Also adds Dagestan's Caspian coast (his next request, row 643_DC): node tools/v2_greater_caucasus.js tools/data/dagestan_coast.geojson */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = JSON.parse(fs.readFileSync(process.argv[2] ? path.resolve(process.argv[2]) : path.join(__dirname, 'data/greater_caucasus.geojson')));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
for (const k of ['x', 'xb', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const f of ADD.features) {
    const g = f.geometry.type === 'GeometryCollection' ? null : f.geometry; if (!g) continue;
    for (const poly of R3mp(asMp(g))) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  for (const f of ADD.features) {
    const id = '643_' + f.properties.id.slice(3);
    V.states = V.states.filter(s => s.id !== id);
    V.states.push(f.properties.kind === 'republic'
      ? {id, n: 'Russia: ' + f.properties.n + ' (the whole republic, for the Greater Caucasus)', km2: f.properties.km2, pct: null}
      : {id, n: 'Russia: ' + f.properties.n, km2: f.properties.km2, pct: null});
  }
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
