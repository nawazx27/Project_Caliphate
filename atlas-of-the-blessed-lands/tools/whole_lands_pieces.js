/* Version 99 (2026-10-12, Nawaz asked whether every shaded land of his Greater Turkey maps is in V2). Puts back into every version
   the bits of a land it lists whole that its outline had lost along a coast or border: country by country and piece by piece,
   since one big union makes polygon-clipping fail (tools/whole_lands_complete.js does it in one go and now fails on V2). The row
   "Cyprus (the whole island)" (id CYP) stands for Cyprus, Northern Cyprus, the UN buffer zone and the British bases together.
   Run: node tools/whole_lands_pieces.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM;
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const G = {}; geo.objects.countries.geometries.forEach(g => { G[String(g.id)] = g; });
const shape = id => { const f = topojson.feature(geo, G[id]); return f.geometry ? R3mp(asMp(f.geometry)) : []; };
const ALIAS = {CYP: ['196', 'CYN', 'CNM', 'ESB', 'WSB']};
for (const k of ['me', 'x', 'xn', 'xw', 'me2', 'x3', 'v2', 'g']) {
  const V = C[k]; if (!V || !V.polys) continue;
  let X = R3mp(V.polys), fixed = 0; const failed = new Set();
  for (const s of V.states.filter(s => s.pct >= 99.5 && (G[s.id] || ALIAS[s.id]))) {
    for (const id of ALIAS[s.id] || [s.id]) for (const poly of shape(id)) {
      let miss; try { miss = R3mp(pc.difference([poly], X)); } catch (e) { failed.add(id); continue; }
      const a = area(miss); if (a < 0.05) continue;
      try { X = R3mp(pc.union(X, miss)); fixed += a; } catch (e) {
        for (const m of miss) { try { X = R3mp(pc.union(X, [m])); fixed += area([m]); } catch (e2) { failed.add(id); } } }
    }
  }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  const before = V.km2; V.polys = X; V.km2 = Math.round(area(X));
  console.log(k, 'put back', fixed.toFixed(1), 'km²', before, '->', V.km2, failed.size ? 'could not check: ' + [...failed].join(',') : '');
}
fs.writeFileSync(F, JSON.stringify(C));
